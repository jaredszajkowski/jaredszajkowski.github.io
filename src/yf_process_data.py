"""
This script uses existing functions to download daily price data from Yahoo Finance, then resample to month end data, then resample to month end total return data, then resample to quarter end data, and finally resample to quarter end total return data.
"""

import pandas as pd

from settings import config
from yf_pull_data import yf_pull_data
from yf_month_end import yf_month_end
from yf_month_end_total_return import yf_month_end_total_return
from yf_quarter_end import yf_quarter_end
from yf_quarter_end_total_return import yf_quarter_end_total_return

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Set global variables
GLOBAL_ADJUSTED = False

# Crypto Data
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

# Iterate through each cryptocurrency
for currency in cryptocurrencies:
    # Fetch raw data
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=currency,
        adjusted=GLOBAL_ADJUSTED,
        source="Yahoo_Finance",
        asset_class="Cryptocurrencies",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end data
    # yf_month_end(
    #     base_directory=DATA_DIR,
    #     ticker=currency,
    #     source="Yahoo_Finance",
    #     asset_class="Cryptocurrencies",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to month-end total return data
    yf_month_end_total_return(
        base_directory=DATA_DIR,
        ticker=currency,
        source="Yahoo_Finance",
        asset_class="Cryptocurrencies",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to quarter-end data
    # yf_quarter_end(
    #     base_directory=DATA_DIR,
    #     ticker=currency,
    #     source="Yahoo_Finance",
    #     asset_class="Cryptocurrencies",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to quarter-end total return data
    yf_quarter_end_total_return(
        base_directory=DATA_DIR,
        ticker=currency,
        source="Yahoo_Finance",
        asset_class="Cryptocurrencies",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

###############
# Stock data
###############

# Read existing data from csv file into equities dictionary
equities_df = pd.read_csv(f"{DATA_DIR}/Polygon/equities.csv", index_col=0)
equities = equities_df.to_dict()["Name"]

# Iterate through each stock
for stock in equities.keys():
    # Fetch raw data
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=stock,
        adjusted=GLOBAL_ADJUSTED,
        source="Yahoo_Finance",
        asset_class="Equities",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end data
    # yf_month_end(
    #     base_directory=DATA_DIR,
    #     ticker=stock,
    #     source="Yahoo_Finance",
    #     asset_class="Equities",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to month-end total return data
    yf_month_end_total_return(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Yahoo_Finance",
        asset_class="Equities",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to quarter-end data
    # yf_quarter_end(
    #     base_directory=DATA_DIR,
    #     ticker=stock,
    #     source="Yahoo_Finance",
    #     asset_class="Equities",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to quarter-end total return data
    yf_quarter_end_total_return(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Yahoo_Finance",
        asset_class="Equities",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

# Index Data
indices = ["^GSPC", "^VIX", "^VVIX"]

# Iterate through each index
for index in indices:
    # Fetch raw data
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=index,
        adjusted=GLOBAL_ADJUSTED,
        source="Yahoo_Finance",
        asset_class="Indices",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end data
    # yf_month_end(
    #     base_directory=DATA_DIR,
    #     ticker=index,
    #     source="Yahoo_Finance",
    #     asset_class="Indices",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to month-end total return data
    yf_month_end_total_return(
        base_directory=DATA_DIR,
        ticker=index,
        source="Yahoo_Finance",
        asset_class="Indices",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to quarter-end data
    # yf_quarter_end(
    #     base_directory=DATA_DIR,
    #     ticker=index,
    #     source="Yahoo_Finance",
    #     asset_class="Indices",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to quarter-end total return data
    yf_quarter_end_total_return(
        base_directory=DATA_DIR,
        ticker=index,
        source="Yahoo_Finance",
        asset_class="Indices",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

###############
# ETF data
###############

# Read existing data from csv file into etfs dictionary
etfs_df = pd.read_csv(f"{DATA_DIR}/Polygon/etfs.csv", index_col=0)
etfs = etfs_df.to_dict()["Name"]

# Iterate through each ETF
for fund in etfs.keys():
    # Fetch raw data
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        adjusted=GLOBAL_ADJUSTED,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end data
    # yf_month_end(
    #     base_directory=DATA_DIR,
    #     ticker=fund,
    #     source="Yahoo_Finance",
    #     asset_class="Exchange_Traded_Funds",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to month-end total return data
    yf_month_end_total_return(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to quarter-end data
    # yf_quarter_end(
    #     base_directory=DATA_DIR,
    #     ticker=fund,
    #     source="Yahoo_Finance",
    #     asset_class="Exchange_Traded_Funds",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to quarter-end total return data
    yf_quarter_end_total_return(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

# Mutual Fund Data
mutual_funds = ["VFIAX", "FXAIX", "TCIEX", "OGGYX", "VSMAX", "VBTLX", "VMVAX", "GIBIX"]

# Iterate through each mutual fund
for fund in mutual_funds:
    # Fetch raw data
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        adjusted=GLOBAL_ADJUSTED,
        source="Yahoo_Finance",
        asset_class="Mutual_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end data
    # yf_month_end(
    #     base_directory=DATA_DIR,
    #     ticker=fund,
    #     source="Yahoo_Finance",
    #     asset_class="Mutual_Funds",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to month-end total return data
    yf_month_end_total_return(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Yahoo_Finance",
        asset_class="Mutual_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to quarter-end data
    # yf_quarter_end(
    #     base_directory=DATA_DIR,
    #     ticker=fund,
    #     source="Yahoo_Finance",
    #     asset_class="Mutual_Funds",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Resample to quarter-end total return data
    yf_quarter_end_total_return(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Yahoo_Finance",
        asset_class="Mutual_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )
