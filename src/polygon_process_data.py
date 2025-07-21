"""
This script uses existing functions to download daily price data from 
Polygon, then:

* Resample to month end data
* Resample to quarter end data
"""

import time

from polygon_pull_data import polygon_pull_data
from polygon_month_end import polygon_month_end
from polygon_quarter_end import polygon_quarter_end
from settings import config

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Crypto Data
# None

# Stock Data
equities = ["AMZN", "AAPL"]

# Iterate through each stock
for stock in equities:
    # Fetch raw data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Polygon",
        asset_class="Equities",
        start_date="2025-01-01",
        end_date="2025-12-31",
        timespan="day",
        multiplier=1,
        adjusted=True,
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end data
    polygon_month_end(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Polygon",
        asset_class="Equities",
        timespan="day",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # # Resample to month-end total return data
    # ndl_month_end_total_return(
    #     base_directory=DATA_DIR,
    #     ticker=stock,
    #     source="Nasdaq_Data_Link",
    #     asset_class="Equities",
    #     excel_export=True,
    #     pickle_export=True,
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
        output_confirmation=True,
    )

    # # Resample to quarter-end total return data
    # ndl_quarter_end_total_return(
    #     base_directory=DATA_DIR,
    #     ticker=stock,
    #     source="Nasdaq_Data_Link",
    #     asset_class="Equities",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Pause for 15 seconds to avoid hitting API rate limits
    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
    time.sleep(15)

# Index Data
# None

# Exchange Traded Fund Data
etfs = [
    'SPY',
    'TQQQ', 'AGG', 
    'EDC', 'EBND',
    'MVV', 'SCHZ',
    'VB', 'VIOO', 'BND',
    'UPRO', 'SGOV',
    'DHY',
    'IDU', 'IYC', 'IYE', 'IYF', 'IYH', 'IYJ', 'IYK', 'IYM', 'IYR', 'IYW', 'IYZ',
    'DIG', 'LTL', 'ROM', 'RXL', 'UCC', 'UGE', 'UPW', 'URE', 'UXI', 'UYG', 'UYM',
    'XLB', 'XLC', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY',
    'IVV', 'EFA', 'EEM', 'IEF', 'IEI', 'TLT', 'GSG', 'IAU', 'IYR',
    'SSO', 'EFO', 'EET', 'UBT', 'UST', 'GSG', 'UGL', 'URE',
    'TMF',
    'IWM', 'URTY',
]

# Iterate through each ETF
for fund in etfs:
    # Fetch raw data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Polygon",
        asset_class="Exchange_Traded_Funds",
        start_date="2025-01-01",
        end_date="2025-12-31",
        timespan="day",
        multiplier=1,
        adjusted=True,
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end data
    polygon_month_end(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Polygon",
        asset_class="Exchange_Traded_Funds",
        timespan="day",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # # Resample to month-end total return data
    # ndl_month_end_total_return(
    #     base_directory=DATA_DIR,
    #     ticker=fund,
    #     source="Nasdaq_Data_Link",
    #     asset_class="Exchange_Traded_Funds",
    #     excel_export=True,
    #     pickle_export=True,
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
        output_confirmation=True,
    )

    # # Resample to quarter-end total return data
    # ndl_quarter_end_total_return(
    #     base_directory=DATA_DIR,
    #     ticker=fund,
    #     source="Nasdaq_Data_Link",
    #     asset_class="Exchange_Traded_Funds",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

    # Pause for 15 seconds to avoid hitting API rate limits
    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
    time.sleep(15)

# Mutual Fund Data
# None