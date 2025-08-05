import logging
import numpy as np
import pandas as pd
import time
import threading

from coinbase.rest import RESTClient
from coinbase.websocket import WSClient
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import time

from coinbase.websocket import WSClient
from load_api_keys import load_api_keys

# Load API keys from the environment
api_keys = load_api_keys()

API_KEY = api_keys["COINBASE_KEY"]
API_SECRET = api_keys["COINBASE_SECRET"]

PRODUCT_ID = "BTC-USD"  # Trading pair
RSI_PERIOD = 14  # RSI calculation period
RSI_OVERSOLD = 30  # RSI threshold for buy
STOP_LOSS_PERCENT = 0.02  # 2% stop loss
LIMIT_ORDER_SIZE = "0.001"  # BTC amount per order (as string for API)
SANDBOX = True  # Set to False for production

# Initialize Coinbase REST client
api_url = "https://api-public.sandbox.cdp.coinbase.com" if SANDBOX else "https://api.coinbase.com"
client = RESTClient(api_key=API_KEY, api_secret=API_SECRET, base_url=api_url)

# Data storage
price_data = []
orders = []

def calculate_rsi(prices, period=RSI_PERIOD):
    """Calculate RSI for the given price series."""
    if len(prices) < period + 1:
        return None
    df = pd.DataFrame(prices, columns=['close'])
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def place_buy_limit_order(price, size):
    """Place a buy limit order."""
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
    """Place a stop limit sell order."""
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

def handle_candle_event(event):
    """Handle incoming WebSocket candle events."""
    try:
        if event['event'] == 'update' and 'candles' in event:
            candle = event['candles'][0]
            price = float(candle['close'])
            timestamp = datetime.fromisoformat(candle['start'][:-1])  # Remove 'Z'

            # Store price data
            price_data.append({'time': timestamp, 'close': price})

            # Keep only the last 100 data points
            if len(price_data) > 100:
                price_data.pop(0)

            # Calculate RSI
            prices = [p['close'] for p in price_data]
            rsi = calculate_rsi(prices)

            if rsi is not None:
                logger.info(f"RSI: {rsi:.2f}, Price: {price}")

                # Check for buy condition
                if rsi < RSI_OVERSOLD:
                    logger.info(f"RSI below {RSI_OVERSOLD}. Placing buy order.")
                    buy_order = place_buy_limit_order(price, LIMIT_ORDER_SIZE)
                    if buy_order and 'order_id' in buy_order:
                        orders.append({
                            'order_id': buy_order['order_id'],
                            'type': 'buy',
                            'price': price,
                            'size': LIMIT_ORDER_SIZE,
                            'timestamp': timestamp
                        })
                        # Place stop loss order
                        sell_order = place_stop_limit_sell_order(price, LIMIT_ORDER_SIZE)
                        if sell_order and 'order_id' in sell_order:
                            orders.append({
                                'order_id': sell_order['order_id'],
                                'type': 'sell',
                                'price': stop_price,
                                'size': LIMIT_ORDER_SIZE,
                                'timestamp': timestamp
                            })

            # Log market data
            logger.info(f"Market Data - Time: {timestamp}, Price: {price}")
            logger.info(f"Active Orders: {len(orders)}")
    except Exception as e:
        logger.error(f"Error processing candle event: {e}")

def on_error(ws, error):
    """Handle WebSocket errors."""
    logger.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    """Handle WebSocket closure."""
    logger.info("WebSocket closed")

def on_open(ws):
    """Subscribe to candles channel on WebSocket open."""
    logger.info("WebSocket opened")
    ws.subscribe([PRODUCT_ID], "candles")

def run_websocket():
    """Run WebSocket client."""
    ws_url = "wss://ws-direct.sandbox.cdp.coinbase.com" if SANDBOX else "wss://ws-direct.cdp.coinbase.com"
    ws = WSClient(
        api_key=API_KEY,
        api_secret=API_SECRET,
        callback=handle_candle_event,
        ws_url=ws_url
    )
    
    # Subscribe to the candles channel AFTER connection
    ws.subscribe([PRODUCT_ID], channel="candles", granularity="ONE_MINUTE")  # adjust as needed

    ws.run_forever()

def monitor_orders():
    """Periodically check and log order status."""
    while True:
        try:
            for order in orders[:]:  # Copy to avoid modifying while iterating
                order_status = client.get_order(order['order_id'])
                logger.info(f"Order {order['order_id']} status: {order_status['status']}")
                if order_status['status'] in ['FILLED', 'CANCELLED']:
                    orders.remove(order)
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error monitoring orders: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Start WebSocket in a separate thread
    ws_thread = threading.Thread(target=run_websocket)
    ws_thread.daemon = True
    ws_thread.start()

    # Start order monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_orders)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")