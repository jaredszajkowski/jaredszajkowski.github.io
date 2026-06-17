"""
This script uses existing functions to download OHLCV data from DataBento, then:

* Resample to month end data
* Resample to quarter end data

DataBento dataset reference (US equities):
  DBEQ.BASIC  - Consolidated US equities (good general-purpose default)
  XNAS.ITCH   - Nasdaq equities only
  XNYS.PILLAR - NYSE equities only
  ARCX.PILLAR - NYSE Arca (ETFs)
"""

import pandas as pd

from datetime import datetime
from databento_pull_data import databento_pull_data
from databento_month_end import databento_month_end
from databento_quarter_end import databento_quarter_end
from settings import config

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Get current year, month, day
current_year = datetime.now().year
current_month = datetime.now().month
current_day = datetime.now().day

# Set global variables
GLOBAL_VERBOSE = False
GLOBAL_PULL_MINUTE = True
GLOBAL_PARQUET_EXPORT = False

###############
# Stock data
###############

# Read existing data from csv file into equities dictionary
# CSV must have columns: Symbol (index), Name, Dataset
equities_df = pd.read_csv(f"{DATA_DIR}/DataBento/equities.csv", index_col=0)
equities = equities_df.to_dict(orient="index")

for stock, meta in equities.items():
    dataset = meta["Dataset"]

    if GLOBAL_PULL_MINUTE:
        databento_pull_data(
            base_directory=DATA_DIR,
            symbol=stock,
            dataset=dataset,
            source="DataBento",
            asset_class="Equities",
            start_date=datetime(current_year - 2, current_month, current_day),
            schema="ohlcv-1m",
            force_existing_check=False,
            verbose=GLOBAL_VERBOSE,
            excel_export=False,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )

    databento_pull_data(
        base_directory=DATA_DIR,
        symbol=stock,
        dataset=dataset,
        source="DataBento",
        asset_class="Equities",
        start_date=datetime(current_year - 2, current_month, current_day),
        schema="ohlcv-1h",
        force_existing_check=False,
        verbose=GLOBAL_VERBOSE,
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    databento_pull_data(
        base_directory=DATA_DIR,
        symbol=stock,
        dataset=dataset,
        source="DataBento",
        asset_class="Equities",
        start_date=datetime(current_year - 2, current_month, current_day),
        schema="ohlcv-1d",
        force_existing_check=False,
        verbose=GLOBAL_VERBOSE,
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    databento_month_end(
        base_directory=DATA_DIR,
        symbol=stock,
        source="DataBento",
        asset_class="Equities",
        schema="ohlcv-1d",
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    databento_quarter_end(
        base_directory=DATA_DIR,
        symbol=stock,
        source="DataBento",
        asset_class="Equities",
        schema="ohlcv-1d",
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

###############
# ETF data
###############

# Read existing data from csv file into etfs dictionary
# CSV must have columns: Symbol (index), Name, Dataset
etfs_df = pd.read_csv(f"{DATA_DIR}/DataBento/etfs.csv", index_col=0)
etfs = etfs_df.to_dict(orient="index")

for fund, meta in etfs.items():
    dataset = meta["Dataset"]

    if GLOBAL_PULL_MINUTE:
        databento_pull_data(
            base_directory=DATA_DIR,
            symbol=fund,
            dataset=dataset,
            source="DataBento",
            asset_class="Exchange_Traded_Funds",
            start_date=datetime(current_year - 2, current_month, current_day),
            schema="ohlcv-1m",
            force_existing_check=False,
            verbose=GLOBAL_VERBOSE,
            excel_export=False,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )

    databento_pull_data(
        base_directory=DATA_DIR,
        symbol=fund,
        dataset=dataset,
        source="DataBento",
        asset_class="Exchange_Traded_Funds",
        start_date=datetime(current_year - 2, current_month, current_day),
        schema="ohlcv-1h",
        force_existing_check=False,
        verbose=GLOBAL_VERBOSE,
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    databento_pull_data(
        base_directory=DATA_DIR,
        symbol=fund,
        dataset=dataset,
        source="DataBento",
        asset_class="Exchange_Traded_Funds",
        start_date=datetime(current_year - 2, current_month, current_day),
        schema="ohlcv-1d",
        force_existing_check=False,
        verbose=GLOBAL_VERBOSE,
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    databento_month_end(
        base_directory=DATA_DIR,
        symbol=fund,
        source="DataBento",
        asset_class="Exchange_Traded_Funds",
        schema="ohlcv-1d",
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    databento_quarter_end(
        base_directory=DATA_DIR,
        symbol=fund,
        source="DataBento",
        asset_class="Exchange_Traded_Funds",
        schema="ohlcv-1d",
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )
