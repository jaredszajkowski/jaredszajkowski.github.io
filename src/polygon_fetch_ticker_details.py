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
        "IYC",  # iShares U.S. Consumer Discretionary ETF
        "IYK",  # iShares U.S. Consumer Staples ETF
        "IYE",  # iShares U.S. Energy ETF
        "IYF",  # iShares U.S. Financials ETF
        "IYH",  # iShares U.S. Healthcare ETF
        "IYJ",  # iShares U.S. Industrials ETF
        "IYM",  # iShares U.S. Basic Materials ETF
        "IYW",  # iShares U.S. Technology ETF
        "IYZ",  # iShares U.S. Telecommunications ETF
        "IDU",  # iShares U.S. Utilities ETF
        "IYR",  # iShares U.S. Real Estate ETF

        "UCC",  # ProShares Ultra Consumer Discretionary
        "UGE",  # ProShares Ultra Consumer Staples
        "DIG",  # ProShares Ultra Energy
        "UYG",  # ProShares Ultra Financials
        "RXL",  # ProShares Ultra Health Care
        "UXI",  # ProShares Ultra Industrials
        "UYM",  # ProShares Ultra Materials
        "ROM",  # ProShares Ultra Technology
        "LTL",  # Proshares Ultra Communication Services
        "UPW",  # ProShares Ultra Utilities
        "URE",  # ProShares Ultra Real Estate

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

    time.sleep(12)

    ###############
    # Index data
    # Tickers use the "I:" prefix (e.g., "I:SPX", "I:NDX", "I:DJI", "I:RUT", "I:VIX")
    # Note: get_ticker_details() may not return data for all index tickers; add names
    # manually below if needed.
    ###############

    new_index_tickers = [
        # Put new tickers here that you want to add (e.g., "I:SPX")
    ]

    # Create empty dictionary
    new_index = {}

    # Read existing data from csv file into indices dictionary (create file if needed)
    try:
        indices_df = pd.read_csv(f"{DATA_DIR}/Polygon/indices.csv", index_col=0)
        indices = indices_df.to_dict()["Name"]
    except FileNotFoundError:
        indices = {}

    for ticker in new_index_tickers:
        try:
            ticker_details = polygon_fetch_ticker_details(ticker)
            new_index[ticker] = ticker_details.name
        except Exception:
            # Some index tickers do not have details; supply the name manually
            new_index[ticker] = ticker
        indices.update(new_index)
        indices = dict(sorted(indices.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(indices)

    # Export indices dictionary to csv file
    indices_df = pd.DataFrame.from_dict(indices, orient="index", columns=["Name"])
    indices_df.to_csv(f"{DATA_DIR}/Polygon/indices.csv")

    time.sleep(12)

    ###############
    # Options data
    # Tickers use the "O:" prefix with OCC symbology:
    #   O:{underlying}{YYMMDD}{C|P}{8-digit strike * 1000}
    #   e.g., "O:SPY251219C00600000" = SPY Dec 19 2025 $600 Call
    # Add full option contract tickers directly; get_ticker_details() returns
    # contract metadata (expiration, strike, type, underlying).
    ###############

    new_option_tickers = [
        # Put new option contract tickers here (e.g., "O:SPY251219C00600000")
    ]

    # Create empty dictionary
    new_option = {}

    # Read existing data from csv file into options dictionary (create file if needed)
    try:
        options_df = pd.read_csv(f"{DATA_DIR}/Polygon/options.csv", index_col=0)
        options = options_df.to_dict()["Name"]
    except FileNotFoundError:
        options = {}

    for ticker in new_option_tickers:
        try:
            ticker_details = polygon_fetch_ticker_details(ticker)
            new_option[ticker] = ticker_details.name
        except Exception:
            new_option[ticker] = ticker
        options.update(new_option)
        options = dict(sorted(options.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(options)

    # Export options dictionary to csv file
    options_df = pd.DataFrame.from_dict(options, orient="index", columns=["Name"])
    options_df.to_csv(f"{DATA_DIR}/Polygon/options.csv")

    time.sleep(12)

    ###############
    # Futures data
    # Polygon uses "/" prefix for continuous front-month futures contracts
    # (e.g., "/ES" E-mini S&P 500, "/NQ" E-mini Nasdaq 100, "/CL" WTI Crude Oil,
    #  "/GC" Gold, "/SI" Silver, "/ZB" 30-Year Treasury Bond).
    # Specific dated contracts follow exchange symbology (e.g., "/ESH25").
    # Note: futures data requires a Polygon subscription that includes futures.
    ###############

    new_futures_tickers = [
        # Put new futures tickers here (e.g., "/ES")
    ]

    # Create empty dictionary
    new_future = {}

    # Read existing data from csv file into futures dictionary (create file if needed)
    try:
        futures_df = pd.read_csv(f"{DATA_DIR}/Polygon/futures.csv", index_col=0)
        futures = futures_df.to_dict()["Name"]
    except FileNotFoundError:
        futures = {}

    for ticker in new_futures_tickers:
        try:
            ticker_details = polygon_fetch_ticker_details(ticker)
            new_future[ticker] = ticker_details.name
        except Exception:
            new_future[ticker] = ticker
        futures.update(new_future)
        futures = dict(sorted(futures.items()))
        print(f"Updated {ticker}")
        time.sleep(12)

    print(futures)

    # Export futures dictionary to csv file
    futures_df = pd.DataFrame.from_dict(futures, orient="index", columns=["Name"])
    futures_df.to_csv(f"{DATA_DIR}/Polygon/futures.csv")
