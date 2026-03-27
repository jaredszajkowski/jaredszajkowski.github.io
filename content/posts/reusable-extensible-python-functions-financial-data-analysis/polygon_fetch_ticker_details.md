```python
import pandas as pd
import time

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
    Fetch detailed information for a given product from Polygon API.

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

    ###############
    # Stock data
    ###############

    new_equity_tickers = [
        # Put new tickers here that you want to pull details for
    ]

    # Create empty dictionary
    new_equity = {}

    # Read existing data from csv file into equities dictionary
    equities_df = pd.read_csv(f"{DATA_DIR}/Polygon/equities.csv", index_col=0)
    equities = equities_df.to_dict()["Name"]

    for ticker in new_equity_tickers:
        ticker_details = polygon_fetch_ticker_details(ticker)
        new_equity[ticker] = ticker_details.name  # access name field
        equities.update(new_equity)
        equities = dict(sorted(equities.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(equities)

    # Export equities dictionary to csv file
    equities_df = pd.DataFrame.from_dict(equities, orient="index", columns=["Name"])
    equities_df.to_csv(f"{DATA_DIR}/Polygon/equities.csv")

    time.sleep(12)

    ###############
    # ETF data
    ###############

    new_etf_tickers = [
        # Put new tickers here that you want to pull details for
    ]

    # Create empty dictionary
    new_etf = {}

    # Read existing data from csv file into etfs dictionary
    etfs_df = pd.read_csv(f"{DATA_DIR}/Polygon/etfs.csv", index_col=0)
    etfs = etfs_df.to_dict()["Name"]

    for ticker in new_etf_tickers:
        ticker_details = polygon_fetch_ticker_details(ticker)
        new_etf[ticker] = ticker_details.name  # access name field
        etfs.update(new_etf)
        etfs = dict(sorted(etfs.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(etfs)

    # Export etfs dictionary to csv file
    etfs_df = pd.DataFrame.from_dict(etfs, orient="index", columns=["Name"])
    etfs_df.to_csv(f"{DATA_DIR}/Polygon/etfs.csv")

```