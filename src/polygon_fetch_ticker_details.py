import pandas as pd
import time

from datetime import datetime, timedelta
from load_api_keys import load_api_keys
from massive import RESTClient
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

    equity_tickers = [
        # Put tickers here
    ]

    # Create empty dictionary
    new_equity = {}

    # Copy existing dictionary so that it updates
    equities = {
        'AAPL': 'Apple Inc.', 
        'AMZN': 'Amazon.Com Inc',
    }

    for ticker in equity_tickers:
        ticker_details = polygon_fetch_ticker_details(ticker)
        new_equity[ticker] = ticker_details.name  # access name field
        equities.update(new_equity)
        equities = dict(sorted(equities.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(equities)

    time.sleep(12)

    etf_tickers = [
        # Put tickers here
        "QQQ",
    ]

    # Create empty dictionary
    new_etf = {}

    # Copy existing dictionary so that it updates
    etfs = {}

    for ticker in etf_tickers:
        ticker_details = polygon_fetch_ticker_details(ticker)
        new_etf[ticker] = ticker_details.name  # access name field
        etfs.update(new_etf)
        etfs = dict(sorted(etfs.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(etfs)

