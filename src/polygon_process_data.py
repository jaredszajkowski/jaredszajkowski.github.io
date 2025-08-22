"""
This script uses existing functions to download daily price data from 
Polygon, then:

* Resample to month end data
* Resample to quarter end data
"""

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

# Crypto Data
# None

# # Stock Data
# equities = ["AMZN", "AAPL"]

# # Iterate through each stock
# for stock in equities:
#     # Pull minute data
#     polygon_pull_data(
#         base_directory=DATA_DIR,
#         ticker=stock,
#         source="Polygon",
#         asset_class="Equities",
#         start_date=datetime(current_year - 2, current_month, current_day),
#         timespan="minute",
#         multiplier=1,
#         adjusted=True,
#         force_existing_check=True,
#         verbose=False,
#         free_tier=True,
#         excel_export=True,
#         pickle_export=True,
#         output_confirmation=True,
#     )

#     # Pull hourly data
#     polygon_pull_data(
#         base_directory=DATA_DIR,
#         ticker=stock,
#         source="Polygon",
#         asset_class="Equities",
#         start_date=datetime(current_year - 2, current_month, current_day),
#         timespan="hour",
#         multiplier=1,
#         adjusted=True,
#         force_existing_check=True,
#         verbose=False,
#         free_tier=True,
#         excel_export=True,
#         pickle_export=True,
#         output_confirmation=True,
#     )

#     # Pull daily data
#     polygon_pull_data(
#         base_directory=DATA_DIR,
#         ticker=stock,
#         source="Polygon",
#         asset_class="Equities",
#         start_date=datetime(current_year - 2, current_month, current_day),
#         timespan="day",
#         multiplier=1,
#         adjusted=True,
#         force_existing_check=True,
#         verbose=False,
#         free_tier=True,
#         excel_export=True,
#         pickle_export=True,
#         output_confirmation=True,
#     )

#     # Resample to month-end data
#     polygon_month_end(
#         base_directory=DATA_DIR,
#         ticker=stock,
#         source="Polygon",
#         asset_class="Equities",
#         timespan="day",
#         excel_export=True,
#         pickle_export=True,
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
#         ticker=stock,
#         source="Polygon",
#         asset_class="Equities",
#         timespan="day",
#         excel_export=True,
#         pickle_export=True,
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

# Exchange Traded Fund Data
etfs = [
    # 'DHY',
    # 'SPY',
    # 'TQQQ', 'AGG',
    # 'EDC', 'EBND',
    # 'MVV', 'SCHZ',
    # 'VB', 'VIOO', 'BND',
    # 'UPRO', 'SGOV',
    # 'IDU', 'IYC', 'IYE', 'IYF', 'IYH', 'IYJ', 'IYK', 'IYM', 'IYR', 'IYW', 'IYZ',
    # 'DIG', 
    # 'LTL', # No data available
    # 'ROM', 'RXL', 'UCC', 'UGE', 'UPW', 'URE', 
    'UXI', 
    'UYG', 'UYM',
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
        start_date=datetime(current_year - 2, current_month, current_day),
        timespan="minute",
        multiplier=1,
        adjusted=True,
        force_existing_check=True,
        verbose=False,
        free_tier=True,
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
        start_date=datetime(current_year - 2, current_month, current_day),
        timespan="hour",
        multiplier=1,
        adjusted=True,
        force_existing_check=True,
        verbose=False,
        free_tier=True,
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
        start_date=datetime(current_year - 2, current_month, current_day),
        timespan="day",
        multiplier=1,
        adjusted=True,
        force_existing_check=True,
        verbose=False,
        free_tier=True,
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