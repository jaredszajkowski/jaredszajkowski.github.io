import pandas as pd
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

def polygon_fetch_ticker_details(
    ticker: str,
) -> any:
    
    """
    Pull detailed data about a ticker.

    Parameters:
    -----------
    ticker : str
        Ticker symbol to download.

    Returns:
    --------
    details : dict
        Dictionary containing detailed information about the ticker.
    """
    
    details = client.get_ticker_details(ticker)

    return details

if __name__ == "__main__":

    equities = [
        # Put tickers here
    ]

    # Create empty dictionary
    new_equity = {}

    # Copy existing dictionary so that it updates
    new_equities = {}

    for ticker in equities:
        ticker_details = polygon_fetch_ticker_details(ticker)
        new_equity[ticker] = ticker_details.name  # access name field
        new_equities.update(new_equity)
        new_equities = dict(sorted(new_equities.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(new_equities)

    time.sleep(12)

    etfs = [
        # Put tickers here
    ]

    # Create empty dictionary
    new_etf = {}

    # Copy existing dictionary so that it updates
    new_etfs = {}

    for ticker in etfs:
        ticker_details = polygon_fetch_ticker_details(ticker)
        new_etf[ticker] = ticker_details.name  # access name field
        new_etfs.update(new_etf)
        new_etfs = dict(sorted(new_etfs.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(new_etfs)

