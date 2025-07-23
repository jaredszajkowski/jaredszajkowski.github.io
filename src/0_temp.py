import time

from coinbase.websocket import WSClient
from load_api_keys import load_api_keys

# Load API keys from the environment
api_keys = load_api_keys()

api_key=api_keys["COINBASE_KEY"]

# api_key = "organizations/{org_id}/apiKeys/{key_id}"

api_secret = api_keys["COINBASE_SECRET"]
# api_secret = "-----BEGIN EC PRIVATE KEY-----\nYOUR PRIVATE KEY\n-----END EC PRIVATE KEY-----\n"

def on_message(msg):
    print(msg)

client = WSClient(api_key=api_key, api_secret=api_secret, on_message=on_message)

# open the connection and subscribe to the ticker and heartbeat channels for BTC-USD and ETH-USD
client.open()
# client.subscribe(product_ids=["BTC-USD", "ETH-USD"], channels=["ticker", "heartbeats"])
client.subscribe(product_ids=["BTC-USD"], channels=["candles"])

# wait 10 seconds
time.sleep(10)

# unsubscribe from the ticker channel and heartbeat channels for BTC-USD and ETH-USD, and close the connection
# client.unsubscribe(product_ids=["BTC-USD", "ETH-USD"], channels=["ticker", "heartbeats"])
# client.close()