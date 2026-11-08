import pandas as pd
import time

from massive import RESTClient
from settings import config

# Load API key from the environment variables
POLYGON_KEY = config("POLYGON_KEY")

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Open client connection
client = RESTClient(api_key=POLYGON_KEY)


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
    try:
        equities_df = pd.read_csv(f"{DATA_DIR}/Polygon/equities.csv", index_col=0)
        equities = equities_df.to_dict()["Name"]
    except FileNotFoundError:
        equities = {}

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
    try:
        etfs_df = pd.read_csv(f"{DATA_DIR}/Polygon/etfs.csv", index_col=0)
        etfs = etfs_df.to_dict()["Name"]
    except FileNotFoundError:
        etfs = {}

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

    ###############
    # Options data
    ###############

    new_options_tickers = [
        # Put new tickers here that you want to pull details for
    ]

    # Create empty dictionary
    new_options = {}

    # Read existing data from csv file into options dictionary
    try:
        options_df = pd.read_csv(f"{DATA_DIR}/Polygon/options.csv", index_col=0)
        options = options_df.to_dict()["Name"]
    except FileNotFoundError:
        options = {}

    for ticker in new_options_tickers:
        ticker_details = polygon_fetch_ticker_details(ticker)
        new_options[ticker] = ticker_details.name  # access name field
        options.update(new_options)
        options = dict(sorted(options.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(options)

    # Export options dictionary to csv file
    options_df = pd.DataFrame.from_dict(options, orient="index", columns=["Name"])
    options_df.to_csv(f"{DATA_DIR}/Polygon/options.csv")

    ###############
    # Index data
    ###############

    new_index_tickers = [
        # Put new tickers here that you want to pull details for
        "I:SPX",
    ]

    # Create empty dictionary
    new_index = {}

    # Read existing data from csv file into index dictionary
    try:
        index_df = pd.read_csv(f"{DATA_DIR}/Polygon/indexes.csv", index_col=0)
        indices = index_df.to_dict()["Name"]
    except FileNotFoundError:
        indices = {}

    for ticker in new_index_tickers:
        ticker_details = polygon_fetch_ticker_details(ticker)
        new_index[ticker] = ticker_details.name  # access name field
        indices.update(new_index)
        indices = dict(sorted(indices.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(indices)

    # Export index dictionary to csv file
    index_df = pd.DataFrame.from_dict(indices, orient="index", columns=["Name"])
    index_df.to_csv(f"{DATA_DIR}/Polygon/indexes.csv")
