import logging
import numpy as np
import pandas as pd
import time
import threading

from coinbase.rest import RESTClient
from coinbase.websocket import WSClient
from datetime import datetime
from load_api_keys import load_api_keys

# Load API keys from the environment
api_keys = load_api_keys()

# --- CONFIGURATION ---
API_KEY = api_keys["COINBASE_KEY"]
API_SECRET = api_keys["COINBASE_SECRET"]
PRODUCT_ID = "BTC-USD"  # Trading pair
RSI_PERIOD = 14  # RSI calculation period
RSI_OVERSOLD = 30  # RSI threshold for buy
STOP_LOSS_PERCENT = 0.02  # 2% stop loss
LIMIT_ORDER_SIZE = "0.001"  # BTC amount per order (as string for API)
SANDBOX = True  # Set to False for production

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- API CLIENT ---
api_url = "https://api-public.sandbox.cdp.coinbase.com" if SANDBOX else "https://api.coinbase.com"
client = RESTClient(api_key=API_KEY, api_secret=API_SECRET, base_url=api_url)

# --- STATE ---
price_data = []
orders = []

# --- INDICATOR CALCULATION ---
def calculate_rsi(prices, period=RSI_PERIOD):
    if len(prices) < period + 1:
        return None
    df = pd.DataFrame(prices, columns=['close'])
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# --- ORDER PLACEMENT ---
def place_buy_limit_order(price, size):
    try:
        order = client.limit_order_buy(
            client_order_id=f"buy_{int(time.time())}",
            product_id=PRODUCT_ID,
            price=str(round(price, 2)),
            size=size
        )
        logger.info(f"Placed buy limit order: {order}")
        return order
    except Exception as e:
        logger.error(f"Error placing buy order: {e}")
        return None

def place_stop_limit_sell_order(buy_price, size):
    stop_price = buy_price * (1 - STOP_LOSS_PERCENT)
    try:
        order = client.stop_limit_order_sell(
            client_order_id=f"sell_{int(time.time())}",
            product_id=PRODUCT_ID,
            base_size=size,
            limit_price=str(round(stop_price, 2)),
            stop_price=str(round(stop_price, 2))
        )
        logger.info(f"Placed stop limit sell order: {order}")
        return order
    except Exception as e:
        logger.error(f"Error placing stop sell order: {e}")
        return None

# --- WEBSOCKET CALLBACKS ---
def handle_ws_message(ws, message):
    try:
        if message.get("channel") == "candles" and message.get("events"):
            candle = message["events"][0]["candle"]
            price = float(candle["close"])
            timestamp = datetime.fromisoformat(candle["start"][:-1])  # remove 'Z'

            price_data.append({"time": timestamp, "close": price})
            if len(price_data) > 100:
                price_data.pop(0)

            prices = [p["close"] for p in price_data]
            rsi = calculate_rsi(prices)

            print(f"Price: {price}, Timestamp: {timestamp}")

            if rsi is not None and not np.isnan(rsi):
                logger.info(f"RSI: {rsi:.2f}, Price: {price}")

                if rsi < RSI_OVERSOLD:
                    logger.info(f"RSI below {RSI_OVERSOLD}. Placing buy order.")
                    buy_order = place_buy_limit_order(price, LIMIT_ORDER_SIZE)
                    if buy_order and "order_id" in buy_order:
                        orders.append({
                            "order_id": buy_order["order_id"],
                            "type": "buy",
                            "price": price,
                            "size": LIMIT_ORDER_SIZE,
                            "timestamp": timestamp,
                        })

                        stop_price = price * (1 - STOP_LOSS_PERCENT)
                        sell_order = place_stop_limit_sell_order(price, LIMIT_ORDER_SIZE)
                        if sell_order and "order_id" in sell_order:
                            orders.append({
                                "order_id": sell_order["order_id"],
                                "type": "sell",
                                "price": stop_price,
                                "size": LIMIT_ORDER_SIZE,
                                "timestamp": timestamp,
                            })

            logger.info(f"Market Data - Time: {timestamp}, Price: {price}")
            logger.info(f"Active Orders: {len(orders)}")

    except Exception as e:
        logger.error(f"Error in WebSocket message handler: {e}")

def handle_ws_error(ws, error):
    logger.error(f"WebSocket error: {error}")

def handle_ws_close(ws):
    logger.info("WebSocket closed")

def handle_ws_open(ws):
    logger.info("WebSocket opened")
    ws.subscribe([PRODUCT_ID], channel="candles", granularity="ONE_MINUTE")

# --- RUN WEBSOCKET ---
def run_websocket():
    ws_url = "wss://ws-direct.sandbox.cdp.coinbase.com" if SANDBOX else "wss://ws-direct.cdp.coinbase.com"

    ws = WSClient(
        api_key=API_KEY,
        api_secret=API_SECRET,
        base_url=ws_url,
        on_open = lambda: handle_ws_open(ws),
        on_message = lambda message: handle_ws_message(ws, message),
        on_close = lambda: handle_ws_close(ws),
    )

    ws.run_forever_with_exception_check()

# --- ORDER MONITORING LOOP ---
def monitor_orders():
    while True:
        try:
            for order in orders[:]:  # Copy to avoid modification while iterating
                order_status = client.get_order(order["order_id"])
                logger.info(f"Order {order['order_id']} status: {order_status['status']}")
                if order_status["status"] in ["FILLED", "CANCELLED"]:
                    orders.remove(order)
            time.sleep(60)
        except Exception as e:
            logger.error(f"Error monitoring orders: {e}")
            time.sleep(60)

# --- MAIN LOOP ---
if __name__ == "__main__":
    ws_thread = threading.Thread(target=run_websocket, daemon=True)
    monitor_thread = threading.Thread(target=monitor_orders, daemon=True)

    ws_thread.start()
    monitor_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
