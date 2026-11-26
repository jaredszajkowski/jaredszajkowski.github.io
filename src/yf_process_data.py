"""
This script uses existing functions to download daily price data from Yahoo
Finance and save it under DATA_DIR/Yahoo_Finance. Each data type has its own
section, run in this order by main():

* pull_cryptocurrencies: tickers from the cryptocurrencies list (e.g. BTC-USD)
* pull_equities: tickers from Polygon/equities.csv
* pull_etfs: tickers from Polygon/etfs.csv
* pull_indices: tickers from the indices list (e.g. ^GSPC)
* pull_mutual_funds: tickers from the mutual_funds list

Every section does the same thing for each ticker:
    * Pull the full daily history
    * Resample the daily data to month end and quarter end

With GLOBAL_ADJUSTED = False, Yahoo returns unadjusted OHLC plus an
"Adj Close" column, so the month-end and quarter-end files carry both the
close and the dividend-adjusted (total return) close.
"""

import pandas as pd

from resample_period_end import resample_period_end
from settings import config
from yf_pull_data import yf_pull_data

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Set global variables
GLOBAL_ADJUSTED = False

# Ticker lists (equities and ETFs are read from the Polygon csv files)
cryptocurrencies = [
    "ADA-USD",
    "AVAX-USD",
    "BCH-USD",
    "BTC-USD",
    "DOGE-USD",
    "DOT-USD",
    "ETH-USD",
    "LINK-USD",
    "LTC-USD",
    "SOL-USD",
    "XRP-USD",
]

indices = ["^GSPC", "^VIX", "^VIX3M", "^VVIX"]

mutual_funds = ["VFIAX", "FXAIX", "TCIEX", "OGGYX", "VSMAX", "VBTLX", "VMVAX", "GIBIX"]


def pull_and_resample(ticker: str, asset_class: str) -> None:
    """Pull daily data for one ticker, then resample to month and quarter end."""

    # Fetch raw daily data
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=ticker,
        adjusted=GLOBAL_ADJUSTED,
        source="Yahoo_Finance",
        asset_class=asset_class,
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end and quarter-end data
    for period in ["month", "quarter"]:
        resample_period_end(
            base_directory=DATA_DIR,
            ticker=ticker,
            source="Yahoo_Finance",
            asset_class=asset_class,
            timespan="day",
            period=period,
            excel_export=True,
            pickle_export=True,
            parquet_export=False,
            output_confirmation=True,
        )


def pull_cryptocurrencies():
    """Pull and resample data for the tickers in the cryptocurrencies list."""

    # Iterate through each cryptocurrency
    for currency in cryptocurrencies:
        pull_and_resample(ticker=currency, asset_class="Cryptocurrencies")


def pull_equities():
    """Pull and resample data for the tickers in equities.csv."""

    # Read existing data from csv file into equities dictionary
    equities_df = pd.read_csv(f"{DATA_DIR}/Polygon/equities.csv", index_col=0)
    equities = equities_df.to_dict()["Name"]

    # Iterate through each stock
    for stock in equities.keys():
        pull_and_resample(ticker=stock, asset_class="Equities")


def pull_etfs():
    """Pull and resample data for the tickers in etfs.csv."""

    # Read existing data from csv file into etfs dictionary
    etfs_df = pd.read_csv(f"{DATA_DIR}/Polygon/etfs.csv", index_col=0)
    etfs = etfs_df.to_dict()["Name"]

    # Iterate through each ETF
    for fund in etfs.keys():
        pull_and_resample(ticker=fund, asset_class="Exchange_Traded_Funds")


def pull_indices():
    """Pull and resample data for the tickers in the indices list."""

    # Iterate through each index
    for index in indices:
        pull_and_resample(ticker=index, asset_class="Indices")


def pull_mutual_funds():
    """Pull and resample data for the tickers in the mutual_funds list."""

    # Iterate through each mutual fund
    for fund in mutual_funds:
        pull_and_resample(ticker=fund, asset_class="Mutual_Funds")


def main():
    pulls = [
        pull_cryptocurrencies,
        pull_equities,
        pull_etfs,
        pull_indices,
        pull_mutual_funds,
    ]

    for pull in pulls:
        pull()


if __name__ == "__main__":
    main()
