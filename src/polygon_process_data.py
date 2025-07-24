"""
This script uses existing functions to download daily price data from 
Polygon, then:

* Resample to month end data
* Resample to quarter end data
"""

from datetime import datetime
from pathlib import Path
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
    # Pull minute data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Polygon",
        asset_class="Equities",
        start_date=datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day),
        timespan="minute",
        multiplier=1,
        adjusted=True,
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Pull hourly data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Polygon",
        asset_class="Equities",
        start_date=datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day),
        timespan="hour",
        multiplier=1,
        adjusted=True,
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Pull daily data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Polygon",
        asset_class="Equities",
        start_date=datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day),
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
    # Pull minute data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Polygon",
        asset_class="Exchange_Traded_Funds",
        start_date=datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day),
        timespan="minute",
        multiplier=1,
        adjusted=True,
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Pull hourly data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Polygon",
        asset_class="Exchange_Traded_Funds",
        start_date=datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day),
        timespan="hour",
        multiplier=1,
        adjusted=True,
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Pull daily data
    polygon_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Polygon",
        asset_class="Exchange_Traded_Funds",
        start_date=datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day),
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
    #     ticker=stock,
    #     source="Nasdaq_Data_Link",
    #     asset_class="Equities",
    #     excel_export=True,
    #     pickle_export=True,
    #     output_confirmation=True,
    # )

# Mutual Fund Data
# None