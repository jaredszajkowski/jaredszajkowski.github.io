import pandas as pd
import sys
import time

from datetime import datetime, timedelta
from load_api_keys import load_api_keys
from polygon import RESTClient
from settings import config

# Load API keys from the environment
api_keys = load_api_keys()

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Open client connection
client = RESTClient(api_key=api_keys["POLYGON_KEY"])

# Get current year, month, day
current_year = datetime.now().year
current_month = datetime.now().month
current_day = datetime.now().day

start = datetime(current_year - 2, current_month, current_day)
print(start)
mid = start + timedelta(days=20)
print(mid)
end = mid + timedelta(days=20)
# end = datetime.now()
print(end)

# Pull new data
aggs = client.get_aggs(
    ticker="XLC",
    timespan="hour",
    multiplier=1,
    from_=mid,
    to=end,
    adjusted=True,
    sort="asc",
    limit=5000,
)

# Convert to DataFrame
new_data = pd.DataFrame([bar.__dict__ for bar in aggs])
new_data["timestamp"] = pd.to_datetime(new_data["timestamp"], unit="ms")
new_data = new_data.rename(columns = {'timestamp':'Date'})
new_data = new_data[['Date', 'open', 'high', 'low', 'close', 'volume', 'vwap', 'transactions', 'otc']]
new_data = new_data.sort_values(by='Date', ascending=True)
print("New data:")
print(new_data)