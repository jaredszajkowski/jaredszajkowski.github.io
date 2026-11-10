"""
This script uses existing functions to download price data from Polygon
(Massive) and save it under DATA_DIR/Polygon. Each data type has its own
section, run in this order by main():

* pull_equities: tickers from equities.csv
    * Pull day, hour, and minute bars
    * Resample the daily data to month end and quarter end
* pull_indices: tickers from indices.csv (e.g. I:NDX)
    * Pull day, hour, and minute bars
    * Resample the daily data to month end and quarter end
* pull_etfs: tickers from etfs.csv
    * Pull day, hour, and minute bars
    * Resample the daily data to month end and quarter end
* pull_options: underlying tickers from options.csv
    * Fetch the list of expired and active contracts and export it
    * Pull day, hour, and minute bars for each contract
* pull_futures: contract tickers from futures.csv (e.g. ESZ6)
    * Pull day, hour, and minute bars (no resampling, since each ticker is a
      single dated contract)

Massive sells a separate subscription for each data type, so
GLOBAL_PAID_ACCESS sets paid or free tier per type. Free-tier types start
from GLOBAL_FREE_START_DATE and pause 12 seconds between API calls to stay
under 5 calls per minute; paid types start from GLOBAL_PAID_START_DATE and
run without the pause.

All bars are exported to Pickle (and Parquet if GLOBAL_PARQUET_EXPORT is
True). Excel exports cover only the timespans in excel_timespans (day and
hour), plus the month-end, quarter-end, and options contract list files.
"""

import os
import pandas as pd

from datetime import datetime, timedelta
from massive import RESTClient
from polygon_pull_equity_data import polygon_pull_equity_data
from polygon_pull_futures_data import polygon_pull_futures_data
from polygon_pull_index_data import (
    polygon_pull_index_data,
    polygon_resample_index_period_end,
)
from polygon_pull_options_data import (
    polygon_fetch_options_contracts,
    polygon_pull_options_data,
)
from polygon_resample_period_end import polygon_resample_period_end
from settings import config

# Get the environment variable for where data is stored
POLYGON_KEY = config("POLYGON_KEY")
DATA_DIR = config("DATA_DIR")

# Set global variables
GLOBAL_PARQUET_EXPORT = False
GLOBAL_FREE_START_DATE = datetime.now() - timedelta(days=2 * 365)
GLOBAL_PAID_START_DATE = datetime.now() - timedelta(days=5 * 365)
GLOBAL_VERBOSE = False

# Massive (Polygon) sells a separate subscription for each data type.
# True = paid plan, False = free tier.
GLOBAL_PAID_ACCESS = {
    "equities": True,
    "etfs": True,
    "indices": False,
    "options": False,
    "futures": False,
}


def tier_settings(data_type: str) -> dict:
    """
    Return the free_tier flag and start date for a data type.

    On the free tier the pull functions sleep 12 seconds around each API
    call, which keeps that data type under the 5 calls per minute limit.
    Paid data types run without the pause.
    """
    paid = GLOBAL_PAID_ACCESS[data_type]
    return {
        "free_tier": not paid,
        "start_date": GLOBAL_PAID_START_DATE if paid else GLOBAL_FREE_START_DATE,
    }


# Timespans
timespans = ["day", "hour", "minute"]

# Timespans to export to Excel (minute data is too large)
excel_timespans = ["day", "hour"]


def pull_equities():
    """Pull and resample data for the tickers in equities.csv."""

    # Read existing data from csv file into equities dictionary
    equities_df = pd.read_csv(f"{DATA_DIR}/Polygon/equities.csv", index_col=0)
    equities = equities_df.to_dict()["Name"]

    tier = tier_settings("equities")

    # Iterate through each stock
    for stock in equities.keys():
        for span in timespans:
            polygon_pull_equity_data(
                base_directory=DATA_DIR,
                ticker=stock,
                source="Polygon",
                asset_class="Equities",
                start_date=tier["start_date"],
                timespan=span,
                multiplier=1,
                adjusted=True,
                force_existing_check=False,
                verbose=GLOBAL_VERBOSE,
                free_tier=tier["free_tier"],
                excel_export=span in excel_timespans,
                pickle_export=True,
                parquet_export=GLOBAL_PARQUET_EXPORT,
                output_confirmation=True,
            )

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
    """Pull and resample data for the tickers in indices.csv."""

    # Read existing data from csv file into index dictionary
    index_df = pd.read_csv(f"{DATA_DIR}/Polygon/indices.csv", index_col=0)
    indices = index_df.to_dict()["Name"]

    tier = tier_settings("indices")

    # Iterate through each index
    for index in indices:
        for timespan in timespans:
            polygon_pull_index_data(
                base_directory=DATA_DIR,
                ticker=index,
                source="Polygon",
                asset_class="Indices",
                start_date=tier["start_date"],
                timespan=timespan,
                multiplier=1,
                force_existing_check=False,
                free_tier=tier["free_tier"],
                verbose=GLOBAL_VERBOSE,
                excel_export=timespan in excel_timespans,
                pickle_export=True,
                parquet_export=GLOBAL_PARQUET_EXPORT,
                output_confirmation=True,
            )

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

    tier = tier_settings("etfs")

    # Iterate through each ETF
    for fund in etfs.keys():
        for span in timespans:
            polygon_pull_equity_data(
                base_directory=DATA_DIR,
                ticker=fund,
                source="Polygon",
                asset_class="Exchange_Traded_Funds",
                start_date=tier["start_date"],
                timespan=span,
                multiplier=1,
                adjusted=True,
                force_existing_check=False,
                verbose=GLOBAL_VERBOSE,
                free_tier=tier["free_tier"],
                excel_export=span in excel_timespans,
                pickle_export=True,
                parquet_export=GLOBAL_PARQUET_EXPORT,
                output_confirmation=True,
            )

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

    tier = tier_settings("options")

    # Iterate through each underlying option ticker
    for underlying in options.keys():

        # Expired contracts that expired after the start date, plus active
        # (unexpired) contracts expiring within the next 5 years
        contracts_df = (
            pd.concat(
                [
                    polygon_fetch_options_contracts(
                        client=client,
                        underlying_ticker=underlying,
                        contract_type=None,
                        expiration_date_gte=tier["start_date"],
                        expiration_date_lte=datetime.now() + timedelta(days=5 * 365),
                        strike_price_gte=None,
                        strike_price_lte=None,
                        expired=is_expired,
                        as_of=None,
                        free_tier=tier["free_tier"],
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
                    start_date=tier["start_date"],
                    timespan=timespan,
                    multiplier=1,
                    force_existing_check=False,
                    free_tier=tier["free_tier"],
                    verbose=False,
                    excel_export=timespan in excel_timespans,
                    pickle_export=True,
                    parquet_export=GLOBAL_PARQUET_EXPORT,
                    output_confirmation=True,
                )


def pull_futures():
    """Pull data for the futures contracts in futures.csv."""

    # Read existing data from csv file into futures dictionary
    futures_df = pd.read_csv(f"{DATA_DIR}/Polygon/futures.csv", index_col=0)
    futures = futures_df.to_dict()["Name"]

    tier = tier_settings("futures")

    # Iterate through each futures contract
    for contract in futures.keys():
        for timespan in timespans:
            polygon_pull_futures_data(
                base_directory=DATA_DIR,
                ticker=contract,
                source="Polygon",
                asset_class="Futures",
                start_date=tier["start_date"],
                timespan=timespan,
                multiplier=1,
                force_existing_check=False,
                free_tier=tier["free_tier"],
                verbose=GLOBAL_VERBOSE,
                excel_export=timespan in excel_timespans,
                pickle_export=True,
                parquet_export=GLOBAL_PARQUET_EXPORT,
                output_confirmation=True,
            )


def main():
    client = RESTClient(api_key=POLYGON_KEY)

    # Crypto data: none
    pull_equities()
    pull_indices()
    pull_etfs()
    # Mutual fund data: none
    pull_options(client)
    pull_futures()


if __name__ == "__main__":
    main()
