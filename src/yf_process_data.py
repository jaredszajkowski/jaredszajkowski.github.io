"""
This script uses existing functions to download daily price data from Yahoo Finance, then resample to month end data, then resample to month end total return data, then resample to quarter end data, and finally resample to quarter end total return data.
"""

from settings import config
from yf_pull_data import yf_pull_data
from yf_month_end import yf_month_end
from yf_month_end_total_return import yf_month_end_total_return
from yf_quarter_end import yf_quarter_end
from yf_quarter_end_total_return import yf_quarter_end_total_return

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

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

# Stock Data
equities = {
    'AAPL': 'Apple Inc.', 
    'AMZN': 'Amazon.Com Inc',
}

# Iterate through each stock
for stock in equities.keys():

# Stock Data
# equities = ["AMZN", "AAPL"]

# Iterate through each stock
# for stock in equities:
    # Fetch raw data
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=stock,
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

# Exchange Traded Fund Data
# etfs = ["GLD", "SPY", "TLT"]

# Exchange Traded Fund Data
etfs = {
    'AGG': 'iShares Core U.S. Aggregate Bond ETF', 
    'BND': 'Vanguard Total Bond Market', 
    'DHY': 'Credit Suisse High Yield Bond Fund', 
    'DIG': 'ProShares Ultra Energy', 
    'EBND': 'SPDR Bloomberg Emerging Markets Local Bond ETF', 
    'EDC': 'Direxion Daily Emerging Markets Bull 3X Shares, Shares of beneficial interest, no par value', 
    'EEM': 'iShares MSCI Emerging Markets ETF', 
    'EET': 'ProShares Ultra MSCI Emerging Markets', 
    'EFA': 'iShares MSCI EAFE ETF', 
    'EFO': 'ProShares Ultra MSCI EAFE',
    'GLD': 'SPDR Gold Trust, SPDR Gold Shares', 
    'GSG': 'iShares S&P  GSCI Commodity-Indexed Trust', 
    'IAU': 'iShares Gold Trust', 
    'IDU': 'iShares U.S. Utilities ETF', 
    'IEF': 'iShares 7-10 Year Treasury Bond ETF', 
    'IEI': 'iShares 3-7 Year Treasury Bond ETF', 
    'IVV': 'iShares Core S&P 500 ETF', 
    'IWM': 'iShares Russell 2000 ETF', 
    'IYC': 'iShares U.S. Consumer Discretionary ETF', 
    'IYE': 'iShares U.S. Energy ETF', 
    'IYF': 'iShares U.S. Financials ETF', 
    'IYH': 'iShares U.S. Healthcare ETF', 
    'IYJ': 'iShares U.S. Industrials ETF', 
    'IYK': 'iShares U.S. Consumer Staples ETF', 
    'IYM': 'iShares U.S. Basic Materials ETF', 
    'IYR': 'iShares U.S. Real Estate ETF', 
    'IYW': 'iShares U.S. Technology ETF', 
    'IYZ': 'iShares U.S. Telecommunications ETF', 
    'LTL': 'ProShares Ultra Communication Services', 
    'MVV': 'ProShares Ultra MidCap400', 
    'ROM': 'ProShares Ultra Technology', 
    'RXL': 'ProShares Ultra Health Care', 
    'SCHZ': 'Schwab US Aggregate Bond ETF', 
    'SGOV': 'iShares 0-3 Month Treasury Bond ETF',
    'SPY': 'SPDR S&P 500 ETF Trust', 
    'SSO': 'ProShares Ultra S&P500', 
    'TLT': 'iShares 20+ Year Treasury Bond ETF', 
    'TMF': 'Direxion Daily 20+ Year Treasury Bull 3X Shares (based on the NYSE 20 Year Plus Treasury Bond Index; symbol AXTWEN)', 
    'TQQQ': 'ProShares  UltraPro QQQ', 
    'UBT': 'ProShares Ultra 20+ Year Treasury', 
    'UCC': 'ProShares Ultra Consumer Discretionary', 
    'UGE': 'ProShares Ultra Consumer Staples', 
    'UGL': 'ProShares Ultra Gold', 
    'UPRO': 'ProShares UltraPro S&P 500', 
    'UPW': 'ProShares Ultra Utilities', 
    'URE': 'ProShares Ultra Real Estate', 
    'URTY': 'ProShares UltraPro Russell2000', 
    'UST': 'ProShares Ultra 7-10 Year Treasury', 
    'UXI': 'ProShares Ultra Industrials', 
    'UYG': 'ProShares Ultra Financials', 
    'UYM': 'ProShares Ultra Materials', 
    'VB': 'Vanguard Small-Cap ETF', 
    'VIOO': 'Vanguard S&P Small-Cap 600 ETF', 
    'XLB': 'Materials Select Sector SPDR Fund', 
    'XLC': 'The Communication Services Select Sector SPDR Fund', 
    'XLE': 'Energy Select Sector SPDR Fund', 
    'XLF': 'Financial Select Sector SPDR Fund', 
    'XLI': 'Industrial Select Sector SPDR Fund', 
    'XLK': 'Technology Select Sector SPDR Fund', 
    'XLP': 'Consumers Staples Select Sector SPDR Fund', 
    'XLRE': 'Real Estate Select Sector SPDR Fund', 
    'XLU': 'Utilities Select Sector SPDR Fund', 
    'XLV': 'Health Care Select Sector SPDR Fund', 
    'XLY': 'Consumer Discretionary Select Sector SPDR Fund'
}

# Iterate through each ETF
for fund in etfs.keys():

# Iterate through each ETF
# for fund in etfs:
    # Fetch raw data
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
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
