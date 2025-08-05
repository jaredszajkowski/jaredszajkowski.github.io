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
WS_API_URL = "wss://advanced-trade-ws.coinbase.com"
CHANNEL = "level2"

# --- LOGGING ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# def on_message(message):
#     print(message)

# # ws_url = "wss://ws-direct.sandbox.cdp.coinbase.com" if SANDBOX else "wss://ws-direct.cdp.coinbase.com"

# ws = WSClient(
#     api_key=API_KEY,
#     api_secret=API_SECRET,
#     base_url=WS_API_URL,
#     on_message=on_message,
#     verbose=True,
# )

# # # open the connection and subscribe to the ticker and heartbeat channels for BTC-USD and ETH-USD
# ws.open()
# # # client.subscribe(product_ids=["BTC-USD", "ETH-USD"], channels=["ticker", "heartbeats"])
# ws.subscribe(product_ids=["BTC-USD"], channels=["candles"])

# # # wait 10 seconds
# ws.run_forever_with_exception_check()

def run_websocket():
    def on_message(message):
        print(message)

    ws = WSClient(
        api_key=API_KEY,
        api_secret=API_SECRET,
        base_url=WS_API_URL,
        on_message=on_message,
        verbose=True,
    )

    ws.open()

    ws.subscribe(product_ids=[PRODUCT_ID], channels=[CHANNEL])

    ws.run_forever_with_exception_check()


# unsubscribe from the ticker channel and heartbeat channels for BTC-USD and ETH-USD, and close the connection
# client.unsubscribe(product_ids=["BTC-USD", "ETH-USD"], channels=["ticker", "heartbeats"])
# client.close()

# def handle_ws_open(ws):
#     # logger.info("WebSocket opened")
#     print("Websocket opened")
#     ws.subscribe(product_ids=["BTC-USD"], channels=["candles"])

# def run_websocket():
#     ws_url = "wss://ws-direct.sandbox.cdp.coinbase.com" if SANDBOX else "wss://ws-direct.cdp.coinbase.com"
#     ws = WSClient(
#         api_key=API_KEY,
#         api_secret=API_SECRET,
#         base_url=ws_url,
#         # on_open = lambda: handle_ws_open(ws),
#         on_message = lambda message: on_message(message),
#     )

#     ws.run_forever_with_exception_check()

# def on_message(message):
#     print("MESSAGE:", message)

# def handle_open(ws):
#     print("WebSocket opened")
#     ws.subscribe(product_ids=[PRODUCT_ID], channels=[CHANNEL])

# def run_websocket():
#     # Create the WebSocket client
#     ws = WSClient(
#         api_key=API_KEY,
#         api_secret=API_SECRET,
#         base_url=WS_API_URL,
#         on_message=on_message,
#     )

#     # Attach on_open after `ws` is fully constructed
#     def handle_open():
#         print("WebSocket opened")
#         ws.subscribe(product_ids=[PRODUCT_ID], channels=[CHANNEL])

#     ws.on_open = handle_open
#     ws.run_forever_with_exception_check()

if __name__ == "__main__":
    ws_thread = threading.Thread(target=run_websocket)
    ws_thread.start()