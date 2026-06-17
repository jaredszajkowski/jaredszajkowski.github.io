"""
This script uses existing functions to download daily price data from
Polygon, then:

* Resample to month end data
* Resample to quarter end data
"""

import pandas as pd
import time

from datetime import datetime
from polygon_pull_data import polygon_pull_data
from polygon_month_end import polygon_month_end
from polygon_quarter_end import polygon_quarter_end
from settings import config

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Get current year, month, day
current_year = datetime.now().year
current_month = datetime.now().month
current_day = datetime.now().day

# Set global variables
GLOBAL_VERBOSE = False
GLOBAL_FREE_TIER = False
GLOBAL_PULL_MINUTE = True
GLOBAL_PARQUET_EXPORT = False

# Crypto Data
# None

###############
# Stock data
###############

# Read existing data from csv file into equities dictionary
equities_df = pd.read_csv(f"{DATA_DIR}/Polygon/equities.csv", index_col=0)
equities = equities_df.to_dict()["Name"]

# Iterate through each stock
for stock in equities.keys():
    if GLOBAL_PULL_MINUTE == True:
        # Pull minute data
        polygon_pull_data(
            base_directory=DATA_DIR,
            ticker=stock,
            source="Polygon",
            asset_class="Equities",
            start_date=datetime(current_year - 2, current_month, current_day),
            timespan="minute",
            multiplier=1,
            adjusted=True,
            force_existing_check=False,
            verbose=GLOBAL_VERBOSE,
            free_tier=GLOBAL_FREE_TIER,
            excel_export=False,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )

        if GLOBAL_FREE_TIER == True:
            time.sleep(12)
        else:
            pass
    else:
        pass

    # Pull hourly data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Polygon",
        asset_class="Equities",
        start_date=datetime(current_year - 2, current_month, current_day),
        timespan="hour",
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
    else:
        pass

    # Pull daily data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Polygon",
        asset_class="Equities",
        start_date=datetime(current_year - 2, current_month, current_day),
        timespan="day",
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
    else:
        pass

    # Resample to month-end data
    polygon_month_end(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Polygon",
        asset_class="Equities",
        timespan="day",
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    # # Resample to month-end total return data
    # ndl_month_end_total_return(
    #     base_directory=DATA_DIR,
    #     ticker=stock,
    #     source="Nasdaq_Data_Link",
    #     asset_class="Equities",
    #     excel_export=True,
    #     pickle_export=False,
    #     output_confirmation=True,
    # )

    # Resample to quarter-end data
    polygon_quarter_end(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Polygon",
        asset_class="Equities",
        timespan="day",
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    # # Resample to quarter-end total return data
    # ndl_quarter_end_total_return(
    #     base_directory=DATA_DIR,
    #     ticker=stock,
    #     source="Nasdaq_Data_Link",
    #     asset_class="Equities",
    #     excel_export=True,
    #     pickle_export=False,
    #     output_confirmation=True,
    # )

# # Index Data
# indices = ["I:SPX"]

# # Iterate through each index
# for index in indices:
#     # Pull minute data
#     polygon_pull_data(
#         base_directory=DATA_DIR,
#         ticker=index,
#         source="Polygon",
#         asset_class="Indices",
#         start_date=datetime(current_year - 2, current_month, current_day),
#         timespan="minute",
#         multiplier=1,
#         adjusted=True,
#         force_existing_check=True,
#         excel_export=True,
#         pickle_export=True,
#         output_confirmation=True,
#     )

#     # Pull hourly data
#     polygon_pull_data(
#         base_directory=DATA_DIR,
#         ticker=index,
#         source="Polygon",
#         asset_class="Indices",
#         start_date=datetime(current_year - 2, current_month, current_day),
#         timespan="hour",
#         multiplier=1,
#         adjusted=True,
#         force_existing_check=True,
#         excel_export=True,
#         pickle_export=True,
#         output_confirmation=True,
#     )

#     # Pull daily data
#     polygon_pull_data(
#         base_directory=DATA_DIR,
#         ticker=index,
#         source="Polygon",
#         asset_class="Indices",
#         start_date=datetime(current_year - 2, current_month, current_day),
#         timespan="day",
#         multiplier=1,
#         adjusted=True,
#         force_existing_check=True,
#         excel_export=True,
#         pickle_export=True,
#         output_confirmation=True,
#     )

#     # Resample to month-end data
#     polygon_month_end(
#         base_directory=DATA_DIR,
#         ticker=index,
#         source="Polygon",
#         asset_class="Indices",
#         timespan="day",
#         excel_export=True,
#         pickle_export=False,
#         parquet_export=GLOBAL_PARQUET_EXPORT,
#         output_confirmation=True,
#     )

#     # # Resample to month-end total return data
#     # ndl_month_end_total_return(
#     #     base_directory=DATA_DIR,
#     #     ticker=stock,
#     #     source="Nasdaq_Data_Link",
#     #     asset_class="Equities",
#     #     excel_export=True,
#     #     pickle_export=False,
#     #     output_confirmation=True,
#     # )

#     # Resample to quarter-end data
#     polygon_quarter_end(
#         base_directory=DATA_DIR,
#         ticker=index,
#         source="Polygon",
#         asset_class="Indices",
#         timespan="day",
#         excel_export=True,
#         pickle_export=False,
#         parquet_export=GLOBAL_PARQUET_EXPORT,
#         output_confirmation=True,
#     )

#     # # Resample to quarter-end total return data
#     # ndl_quarter_end_total_return(
#     #     base_directory=DATA_DIR,
#     #     ticker=stock,
#     #     source="Nasdaq_Data_Link",
#     #     asset_class="Equities",
#     #     excel_export=True,
#     #     pickle_export=False,
#     #     output_confirmation=True,
#     # )

###############
# ETF data
###############

# Read existing data from csv file into etfs dictionary
etfs_df = pd.read_csv(f"{DATA_DIR}/Polygon/etfs.csv", index_col=0)
etfs = etfs_df.to_dict()["Name"]

# Iterate through each ETF
for fund in etfs.keys():
    if GLOBAL_PULL_MINUTE == True:
        # Pull minute data
        polygon_pull_data(
            base_directory=DATA_DIR,
            ticker=fund,
            source="Polygon",
            asset_class="Exchange_Traded_Funds",
            start_date=datetime(current_year - 2, current_month, current_day),
            timespan="minute",
            multiplier=1,
            adjusted=True,
            force_existing_check=False,
            verbose=GLOBAL_VERBOSE,
            free_tier=GLOBAL_FREE_TIER,
            excel_export=False,
            pickle_export=True,
            parquet_export=GLOBAL_PARQUET_EXPORT,
            output_confirmation=True,
        )

        if GLOBAL_FREE_TIER == True:
            time.sleep(12)
        else:
            pass
    else:
        pass

    # Pull hourly data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Polygon",
        asset_class="Exchange_Traded_Funds",
        start_date=datetime(current_year - 2, current_month, current_day),
        timespan="hour",
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
    else:
        pass

    # Pull daily data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Polygon",
        asset_class="Exchange_Traded_Funds",
        start_date=datetime(current_year - 2, current_month, current_day),
        timespan="day",
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
    else:
        pass

    # Resample to month-end data
    polygon_month_end(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Polygon",
        asset_class="Exchange_Traded_Funds",
        timespan="day",
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    # # Resample to month-end total return data
    # ndl_month_end_total_return(
    #     base_directory=DATA_DIR,
    #     ticker=stock,
    #     source="Nasdaq_Data_Link",
    #     asset_class="Equities",
    #     excel_export=True,
    #     pickle_export=False,
    #     output_confirmation=True,
    # )

    # Resample to quarter-end data
    polygon_quarter_end(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Polygon",
        asset_class="Exchange_Traded_Funds",
        timespan="day",
        excel_export=True,
        pickle_export=True,
        parquet_export=GLOBAL_PARQUET_EXPORT,
        output_confirmation=True,
    )

    # # Resample to quarter-end total return data
    # ndl_quarter_end_total_return(
    #     base_directory=DATA_DIR,
    #     ticker=stock,
    #     source="Nasdaq_Data_Link",
    #     asset_class="Equities",
    #     excel_export=True,
    #     pickle_export=False,
    #     output_confirmation=True,
    # )

# Mutual Fund Data
# None
