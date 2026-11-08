"""
This script uses existing functions to download price data from Polygon
and save it under DATA_DIR/Polygon:

* Equities (tickers from equities.csv), indices (tickers from indexes.csv),
  and ETFs (tickers from etfs.csv):
    * Pull day, hour, and minute bars
    * Resample the daily data to month end and quarter end
* Options (underlying tickers from options.csv):
    * Fetch the list of expired and active contracts and export it
    * Pull day, hour, and minute bars
"""

import os
import pandas as pd
import time

from datetime import datetime, timedelta
from massive import RESTClient
from polygon_pull_equity_data import (
    polygon_pull_equity_data,
    polygon_resample_period_end,
)
from polygon_pull_index_data import (
    polygon_pull_index_data,
    polygon_resample_index_period_end,
)
from polygon_pull_options_data import (
    polygon_fetch_options_contracts,
    polygon_pull_options_data,
)
from settings import config

# Get the environment variable for where data is stored
POLYGON_KEY = config("POLYGON_KEY")
DATA_DIR = config("DATA_DIR")

# Set global variables
GLOBAL_FREE_TIER = False
GLOBAL_PARQUET_EXPORT = False
GLOBAL_FREE_START_DATE = datetime.now() - timedelta(days=2*365)
GLOBAL_PAID_START_DATE = datetime.now() - timedelta(days=5*365)
GLOBAL_VERBOSE = False

# Timespans
timespans = ["day", "hour", "minute"]


def pull_equities():
    """Pull and resample data for the tickers in equities.csv."""

    # Read existing data from csv file into equities dictionary
    equities_df = pd.read_csv(f"{DATA_DIR}/Polygon/equities.csv", index_col=0)
    equities = equities_df.to_dict()["Name"]

    # Iterate through each stock
    for stock in equities.keys():
        for span in timespans:
            polygon_pull_equity_data(
                base_directory=DATA_DIR,
                ticker=stock,
                source="Polygon",
                asset_class="Equities",
                start_date=GLOBAL_PAID_START_DATE,
                timespan=span,
                multiplier=1,
                adjusted=True,
                force_existing_check=False,
                verbose=GLOBAL_VERBOSE,
                free_tier=GLOBAL_FREE_TIER,
                excel_export=True,
                pickle_export=True,
                parquet_export=GLOBAL_PARQUET_EXPORT,
                output_confirmation=True,
            )

            if GLOBAL_FREE_TIER == True:
                time.sleep(12)

        # Resample to month-end data
        polygon_resample_period_end(
            base_directory=DATA_DIR,
            ticker=stock,
            source="Polygon",
            asset_class="Equities",
            timespan="day",
            period="month",
            excel_export=True,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )

        # Resample to quarter-end data
        polygon_resample_period_end(
            base_directory=DATA_DIR,
            ticker=stock,
            source="Polygon",
            asset_class="Equities",
            timespan="day",
            period="quarter",
            excel_export=True,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )


def pull_indices():
    """Pull and resample data for the tickers in indexes.csv."""

    # Read existing data from csv file into index dictionary
    index_df = pd.read_csv(f"{DATA_DIR}/Polygon/indexes.csv", index_col=0)
    indices = index_df.to_dict()["Name"]

    # Iterate through each index
    for index in indices:
        for timespan in timespans:
            polygon_pull_index_data(
                base_directory=DATA_DIR,
                ticker=index,
                source="Polygon",
                asset_class="Indices",
                start_date=GLOBAL_FREE_START_DATE,
                timespan=timespan,
                multiplier=1,
                force_existing_check=False,
                free_tier=True,
                verbose=GLOBAL_VERBOSE,
                excel_export=True,
                pickle_export=True,
                parquet_export=GLOBAL_PARQUET_EXPORT,
                output_confirmation=True,
            )

            if GLOBAL_FREE_TIER == True:
                time.sleep(12)

        # Resample to month-end data
        polygon_resample_index_period_end(
            base_directory=DATA_DIR,
            ticker=index,
            source="Polygon",
            asset_class="Indices",
            timespan="day",
            period="month",
            excel_export=True,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )

        # Resample to quarter-end data
        polygon_resample_index_period_end(
            base_directory=DATA_DIR,
            ticker=index,
            source="Polygon",
            asset_class="Indices",
            timespan="day",
            period="quarter",
            excel_export=True,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )


def pull_etfs():
    """Pull and resample data for the tickers in etfs.csv."""

    # Read existing data from csv file into etfs dictionary
    etfs_df = pd.read_csv(f"{DATA_DIR}/Polygon/etfs.csv", index_col=0)
    etfs = etfs_df.to_dict()["Name"]

    # Iterate through each ETF
    for fund in etfs.keys():
        for span in timespans:
            polygon_pull_equity_data(
                base_directory=DATA_DIR,
                ticker=fund,
                source="Polygon",
                asset_class="Exchange_Traded_Funds",
                start_date=GLOBAL_PAID_START_DATE,
                timespan=span,
                multiplier=1,
                adjusted=True,
                force_existing_check=False,
                verbose=GLOBAL_VERBOSE,
                free_tier=GLOBAL_FREE_TIER,
                excel_export=True,
                pickle_export=True,
                parquet_export=GLOBAL_PARQUET_EXPORT,
                output_confirmation=True,
            )

            if GLOBAL_FREE_TIER == True:
                time.sleep(12)

        # Resample to month-end data
        polygon_resample_period_end(
            base_directory=DATA_DIR,
            ticker=fund,
            source="Polygon",
            asset_class="Exchange_Traded_Funds",
            timespan="day",
            period="month",
            excel_export=True,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )

        # Resample to quarter-end data
        polygon_resample_period_end(
            base_directory=DATA_DIR,
            ticker=fund,
            source="Polygon",
            asset_class="Exchange_Traded_Funds",
            timespan="day",
            period="quarter",
            excel_export=True,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )


def pull_options(client):
    """Fetch contract lists and pull data for the underlyings in options.csv."""

    # Read existing data from csv file into options dictionary
    options_df = pd.read_csv(f"{DATA_DIR}/Polygon/options.csv", index_col=0)
    options = options_df.to_dict()["Name"]

    # Iterate through each underlying option ticker
    for underlying in options.keys():

        # Inactive (expired) contracts expiring within the last 2 years
        # Active (unexpired) contracts expiring within the next 5 years
        contracts_df = (
            pd.concat(
                [
                    polygon_fetch_options_contracts(
                        client=client,
                        underlying_ticker=underlying,
                        contract_type=None,
                        expiration_date_gte=datetime.now() - timedelta(days=2 * 365),
                        expiration_date_lte=datetime.now() + timedelta(days=5 * 365),
                        strike_price_gte=None,
                        strike_price_lte=None,
                        expired=is_expired,
                        as_of=None,
                        free_tier=True,
                        verbose=False,
                    )
                    for is_expired in (True, False)
                ],
                ignore_index=True,
            )
            .sort_values(by=["expiration_date", "contract_type", "strike_price"])
            .reset_index(drop=True)
        )

        # Export contract list for that underlying ticker
        contracts_directory = f"{DATA_DIR}/Polygon/Options/{underlying}"
        os.makedirs(contracts_directory, exist_ok=True)
        contracts_df.to_pickle(f"{contracts_directory}/{underlying}_contracts.pkl")
        contracts_df.to_excel(
            f"{contracts_directory}/{underlying}_contracts.xlsx", sheet_name="data"
        )

        # Iterate through the list of contracts
        for option_ticker in contracts_df["ticker"]:
            for timespan in timespans:
                polygon_pull_options_data(
                    base_directory=DATA_DIR,
                    ticker=option_ticker,
                    source="Polygon",
                    asset_class="Options",
                    start_date=GLOBAL_FREE_START_DATE,
                    timespan=timespan,
                    multiplier=1,
                    force_existing_check=False,
                    free_tier=True,
                    verbose=False,
                    excel_export=True,
                    pickle_export=True,
                    parquet_export=GLOBAL_PARQUET_EXPORT,
                    output_confirmation=True,
                )

                if GLOBAL_FREE_TIER == True:
                    time.sleep(12)


def main():
    client = RESTClient(api_key=POLYGON_KEY)

    # Crypto data: none
    pull_equities()
    pull_indices()
    pull_etfs()
    # Mutual fund data: none
    pull_options(client)


if __name__ == "__main__":
    main()
