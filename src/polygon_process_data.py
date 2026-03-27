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
GLOBAL_FREE_TIER = True
GLOBAL_PULL_MINUTE = True

# Crypto Data
# None

###############
# Stock data
###############

# equities = {
#     'AAPL': 'Apple Inc.',
#     'AMZN': 'Amazon.Com Inc',
#     'TSLA': 'Tesla, Inc. Common Stock'
# }

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

###############
# ETF data
###############

# Read existing data from csv file into etfs dictionary
etfs_df = pd.read_csv(f"{DATA_DIR}/Polygon/etfs.csv", index_col=0)
etfs = etfs_df.to_dict()["Name"]

# etfs = {
#     'AGG': 'iShares Core U.S. Aggregate Bond ETF',
#     'BITU': 'ProShares Ultra Bitcoin ETF',
#     'BND': 'Vanguard Total Bond Market',
#     'DHY': 'Credit Suisse High Yield Bond Fund',
#     'DIG': 'ProShares Ultra Energy',
#     'EBND': 'SPDR Bloomberg Emerging Markets Local Bond ETF',
#     'EDC': 'Direxion Daily Emerging Markets Bull 3X Shares, Shares of beneficial interest, no par value',
#     'EEM': 'iShares MSCI Emerging Markets ETF',
#     'EET': 'ProShares Ultra MSCI Emerging Markets',
#     'EFA': 'iShares MSCI EAFE ETF',
#     'EFO': 'ProShares Ultra MSCI EAFE',
#     'ETHA': 'iShares Ethereum Trust ETF',
#     'ETHT': 'ProShares Ultra Ether ETF',
#     'EURL': 'Direxion Daily FTSE Europe Bull 3x ETF',
#     'GLD': 'SPDR Gold Trust, SPDR Gold Shares',
#     'GSG': 'iShares S&P  GSCI Commodity-Indexed Trust',
#     'IAU': 'iShares Gold Trust',
#     'IBIT': 'iShares Bitcoin Trust ETF',
#     'IDU': 'iShares U.S. Utilities ETF',
#     'IEF': 'iShares 7-10 Year Treasury Bond ETF',
#     'IEI': 'iShares 3-7 Year Treasury Bond ETF',
#     'IVV': 'iShares Core S&P 500 ETF',
#     'IWM': 'iShares Russell 2000 ETF',
#     'IYC': 'iShares U.S. Consumer Discretionary ETF',
#     'IYE': 'iShares U.S. Energy ETF',
#     'IYF': 'iShares U.S. Financials ETF',
#     'IYH': 'iShares U.S. Healthcare ETF',
#     'IYJ': 'iShares U.S. Industrials ETF',
#     'IYK': 'iShares U.S. Consumer Staples ETF',
#     'IYM': 'iShares U.S. Basic Materials ETF',
#     'IYR': 'iShares U.S. Real Estate ETF',
#     'IYW': 'iShares U.S. Technology ETF',
#     'IYZ': 'iShares U.S. Telecommunications ETF',
#     'LTL': 'ProShares Ultra Communication Services',
#     'MVV': 'ProShares Ultra MidCap400',
#     'QQQ': 'Invesco QQQ Trust, Series 1',
#     'ROM': 'ProShares Ultra Technology',
#     'RXL': 'ProShares Ultra Health Care',
#     'SCHZ': 'Schwab US Aggregate Bond ETF',
#     'SGOV': 'iShares 0-3 Month Treasury Bond ETF',
#     'SPY': 'SPDR S&P 500 ETF Trust',
#     'SSO': 'ProShares Ultra S&P500',
#     'TLT': 'iShares 20+ Year Treasury Bond ETF',
#     'TMF': 'Direxion Daily 20+ Year Treasury Bull 3X Shares (based on the NYSE 20 Year Plus Treasury Bond Index; symbol AXTWEN)',
#     'TQQQ': 'ProShares  UltraPro QQQ',
#     'UBT': 'ProShares Ultra 20+ Year Treasury',
#     'UCC': 'ProShares Ultra Consumer Discretionary',
#     'UGE': 'ProShares Ultra Consumer Staples',
#     'UGL': 'ProShares Ultra Gold',
#     'UPRO': 'ProShares UltraPro S&P 500',
#     'UPW': 'ProShares Ultra Utilities',
#     'URE': 'ProShares Ultra Real Estate',
#     'URTY': 'ProShares UltraPro Russell2000',
#     'UST': 'ProShares Ultra 7-10 Year Treasury',
#     'UXI': 'ProShares Ultra Industrials',
#     'UYG': 'ProShares Ultra Financials',
#     'UYM': 'ProShares Ultra Materials',
#     'VB': 'Vanguard Small-Cap ETF',
#     'VGK': 'Vanguard FTSE Europe ETF',
#     'VIOO': 'Vanguard S&P Small-Cap 600 ETF',
#     'XLB': 'Materials Select Sector SPDR Fund',
#     'XLC': 'The Communication Services Select Sector SPDR Fund',
#     'XLE': 'Energy Select Sector SPDR Fund',
#     'XLF': 'Financial Select Sector SPDR Fund',
#     'XLI': 'Industrial Select Sector SPDR Fund',
#     'XLK': 'Technology Select Sector SPDR Fund',
#     'XLP': 'Consumers Staples Select Sector SPDR Fund',
#     'XLRE': 'Real Estate Select Sector SPDR Fund',
#     'XLU': 'Utilities Select Sector SPDR Fund',
#     'XLV': 'Health Care Select Sector SPDR Fund',
#     'XLY': 'Consumer Discretionary Select Sector SPDR Fund'
# }

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
