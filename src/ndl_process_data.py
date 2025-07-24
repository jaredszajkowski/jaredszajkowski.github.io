"""
This script uses existing functions to download daily price data from 
Nasdaq Data Link, then:

* Resample to month end data
* Resample to month end total return data
* Resample to quarter end data
* Resample to quarter end total return data
"""

from ndl_pull_data import ndl_pull_data
from ndl_month_end import ndl_month_end
from ndl_month_end_total_return import ndl_month_end_total_return
from ndl_quarter_end import ndl_quarter_end
from ndl_quarter_end_total_return import ndl_quarter_end_total_return
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
    ndl_pull_data(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Nasdaq_Data_Link",
        asset_class="Equities",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end data
    ndl_month_end(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Nasdaq_Data_Link",
        asset_class="Equities",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end total return data
    ndl_month_end_total_return(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Nasdaq_Data_Link",
        asset_class="Equities",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to quarter-end data
    ndl_quarter_end(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Nasdaq_Data_Link",
        asset_class="Equities",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to quarter-end total return data
    ndl_quarter_end_total_return(
        base_directory=DATA_DIR,
        ticker=stock,
        source="Nasdaq_Data_Link",
        asset_class="Equities",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

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
    'UPRO', 'TMF'
]

# Iterate through each ETF
for fund in etfs:
    # Fetch raw data
    ndl_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Nasdaq_Data_Link",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end data
    ndl_month_end(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Nasdaq_Data_Link",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to month-end total return data
    ndl_month_end_total_return(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Nasdaq_Data_Link",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to quarter-end data
    ndl_quarter_end(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Nasdaq_Data_Link",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

    # Resample to quarter-end total return data
    ndl_quarter_end_total_return(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Nasdaq_Data_Link",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )

# Mutual Fund Data
# None