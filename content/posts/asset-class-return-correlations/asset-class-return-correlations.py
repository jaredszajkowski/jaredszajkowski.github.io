# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: general-venv-p313 (3.13.11.final.0)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Introduction
#
# In this post, we'll take a look at historical return correlations between asset classes, including rolling returns, and how those correlations have changed over time.

# %% [markdown]
#  ## Python Imports

# %%
# Standard Library
import datetime
import io
import os
import random
import sys
import warnings

from datetime import datetime, timedelta
from pathlib import Path

# Data Handling
import numpy as np
import pandas as pd

# Data Visualization
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from matplotlib.ticker import FormatStrFormatter, FuncFormatter, MultipleLocator

# Statistical Analysis
import statsmodels.api as sm

# Machine Learning
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Suppress warnings
warnings.filterwarnings("ignore")

# %%
# Add the source subdirectory to the system path to allow import config from settings.py
current_directory = Path(os.getcwd())
BASE_DIR = current_directory.parent.parent.parent
src_directory = BASE_DIR / "src"
sys.path.append(str(src_directory)) if str(src_directory) not in sys.path else None

# Import settings.py
from settings import config

# Add other configured directories
CONTENT_DIR = config("CONTENT_DIR")
POSTS_DIR = config("POSTS_DIR")
PAGES_DIR = config("PAGES_DIR")
PUBLIC_DIR = config("PUBLIC_DIR")
SOURCE_DIR = config("SOURCE_DIR")
DATA_DIR = config("DATA_DIR")
DATA_MANUAL_DIR = config("DATA_MANUAL_DIR")

# %% [markdown]
# ## Python Functions
#
# Here are the functions needed for this project:
#
# * [load_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.
# * [pandas_set_decimal_places](/posts/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.
# * [plot_histogram](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_histogram): Plot the histogram of a data set from a DataFrame.
# * [plot_scatter](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter): Plot the data from a DataFrame for a specified date range and columns.
# * [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the timeseries data from a DataFrame for a specified date range and columns.
# * [run_linear_regression](/posts/reusable-extensible-python-functions-financial-data-analysis/#run_linear_regression): Run a linear regression using statsmodels OLS and return the results.
# * [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.
# * [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.

# %%
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_heatmap import plot_heatmap
from plot_histogram import plot_histogram
from plot_scatter import plot_scatter
from plot_time_series import plot_time_series
from run_regression import run_regression
from summary_stats import summary_stats
from yf_pull_data import yf_pull_data

# %% [markdown]
# ## Data Overview
#
# For this exercise, we will (mostly) use ETFs as a proxy for asset classes and will use the following:
#
# * Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
# * Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
# * Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
# * US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
# * US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
# * US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
# * International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
# * Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
# * European Stocks -- IEV (iShares S&P Europe 350 ETF)
# * Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
# * Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
# * Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
# * Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
# * Gold -- GLD (SPDR Gold Shares)
# * Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
# * Real Estate -- IYR (iShares U.S. Real Estate ETF)
# * Bitcoin -- BTC-USD (Bitcoin USD)
# * Ethereum -- ETH-USD (Ethereum USD)
#
# For all of these, we will use the adjusted closing price, which accounts for dividends and stock splits.
#
# ## Acquire & Plot Data
#
# We'll now pull the data for all the ETFs and cryptocurrencies listed above.

# %%
pandas_set_decimal_places(2)

# Create list of tickers to pull data for
us_equity_tickers = ["IVV", "IJH", "IJR", "QQQ", "IWB", "IWD", "IWF", "IWM"]
intl_equity_tickers = ["EFA", "EEM", "IEV"]
equity_tickers = us_equity_tickers + intl_equity_tickers
bond_tickers = ["SHY", "IEF", "TLT", "AGG"]
commodity_tickers = ["GLD", "GSG"]
real_estate_tickers = ["IYR"]
cryptoasset_tickers = ["BTC-USD", "ETH-USD"]
etf_tickers = (
    us_equity_tickers
    + intl_equity_tickers
    + bond_tickers
    + commodity_tickers
    + real_estate_tickers
)
tickers_dict = {
    "IVV": "Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)",
    "IJH": "Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)",
    "IJR": "Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)",
    "QQQ": "US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)",
    "IWB": "Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)",
    "IWM": "Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)",
    "IWD": "Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)",
    "IWF": "Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)",
    "EFA": "International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)",
    "EEM": "Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)",
    "IEV": "European Stocks -- IEV (iShares S&P Europe 350 ETF)",
    "SHY": "Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)",
    "IEF": "Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)",
    "TLT": "Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)",
    "AGG": "Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)",
    "GLD": "Gold -- GLD (SPDR Gold Shares)",
    "GSG": "Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)",
    "IYR": "Real Estate -- IYR (iShares U.S. Real Estate ETF)",
    "BTC-USD": "Bitcoin -- BTC-USD (Bitcoin USD)",
    "ETH-USD": "Ethereum -- ETH-USD (Ethereum USD)",
}

# %%
for ticker in etf_tickers:
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=ticker,
        adjusted=False,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=False,
    )

for ticker in cryptoasset_tickers:
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=ticker,
        adjusted=False,
        source="Yahoo_Finance",
        asset_class="Cryptocurrencies",
        excel_export=True,
        pickle_export=True,
        output_confirmation=False,
    )

# %% [markdown]
# We'll then peform the following:
# * Load data
# * Rename columns to include the ticker (e.g. "QQQ_Close", "QQQ_Adj_Close", etc.)
# * Drop all columns except for "Adj Close"
# * Calculate the daily returns
# * Combine the data into a single DataFrame

# %%
fund_data = pd.DataFrame()

for ticker in etf_tickers:
    data = load_data(
        base_directory=DATA_DIR,
        ticker=ticker,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        timeframe="Daily",
        file_format="pickle",
    )

    # Rename columns to "QQQ_Close", etc.
    data = data.rename(
        columns={
            "Adj Close": f"{ticker}_Adj_Close",
            "Close": f"{ticker}_Close",
            "High": f"{ticker}_High",
            "Low": f"{ticker}_Low",
            "Open": f"{ticker}_Open",
            "Volume": f"{ticker}_Volume",
        }
    )

    # Drop all columns except for the adjusted close price and date index
    data = data[[f"{ticker}_Adj_Close"]]

    # Calculate daily returns and add as new column
    data[f"{ticker}_Daily_Return"] = data[f"{ticker}_Adj_Close"].pct_change()

    # Concatenate the data for this ticker with the main fund_data DataFrame
    fund_data = pd.concat([fund_data, data], axis=1)

for ticker in cryptoasset_tickers:
    data = load_data(
        base_directory=DATA_DIR,
        ticker=ticker,
        source="Yahoo_Finance",
        asset_class="Cryptocurrencies",
        timeframe="Daily",
        file_format="pickle",
    )

    # Rename columns to "BTC-USD_Close", etc.
    data = data.rename(
        columns={
            "Adj Close": f"{ticker}_Adj_Close",
            "Close": f"{ticker}_Close",
            "High": f"{ticker}_High",
            "Low": f"{ticker}_Low",
            "Open": f"{ticker}_Open",
            "Volume": f"{ticker}_Volume",
        }
    )

    # Drop all columns except for the adjusted close price and date index
    data = data[[f"{ticker}_Adj_Close"]]

    # Calculate daily returns and add as new column
    data[f"{ticker}_Daily_Return"] = data[f"{ticker}_Adj_Close"].pct_change()

    # Concatenate the data for this ticker with the main fund_data DataFrame
    fund_data = pd.concat([fund_data, data], axis=1)

display(fund_data)

# %% [markdown]
# We'll then plot the time series of the adjusted close prices for each of the assets.

# %%
# Combine the etf_tickers and cryptoasset_tickers lists into a single list of all tickers
all_tickers = etf_tickers + cryptoasset_tickers

for ticker in tickers_dict.keys():
    plot_time_series(
        df=fund_data,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[f"{ticker}_Adj_Close"],
        title=f"{tickers_dict[ticker]} Adjusted Close Price",
        x_label="Date",
        x_format="Year",
        x_tick_spacing=1,
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="Price ($)",
        y_format="Decimal",
        y_format_decimal_places="Auto",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=False,
        export_plot=False,
        plot_file_name=None,
    )

# %% [markdown]
# ## Calculate Correlations
#
# Next, we'll calculate the correlation matrix of the daily returns for all of the assets and plot it as a heatmap. We'll do this first without the BTC and ETH data (due to the limited history), and then with the BTC and ETH data.

# %%
# Drop the adjusted close price columns, leaving only the daily return columns
daily_return_columns = [f"{ticker}_Daily_Return" for ticker in tickers_dict.keys()]
fund_data_daily_returns_all = fund_data[daily_return_columns]

# Drop the BTC and ETH daily return columns due to the limited history
fund_data_daily_returns_no_crypto = fund_data_daily_returns_all.drop(
    columns=["BTC-USD_Daily_Return", "ETH-USD_Daily_Return"]
)

# Print the shape of the fund_data_daily_returns_no_crypto DataFrame to confirm that the rows with missing data have been dropped
print(
    f"Shape of fund_data_daily_returns_no_crypto: {fund_data_daily_returns_no_crypto.shape}"
)
print(
    f"Rows to drop due to missing data: {fund_data_daily_returns_no_crypto.dropna().shape}"
)

# Drop the NaN values
fund_data_daily_returns_no_crypto = fund_data_daily_returns_no_crypto.dropna()

# Calculate the correlation matrix of the daily returns
correlation_matrix_no_crypto = fund_data_daily_returns_no_crypto.corr()

display(correlation_matrix_no_crypto)

# %% [markdown]
# And then the heatmap:

# %%
plot_heatmap(
    df=correlation_matrix_no_crypto,
    title="Correlation Matrix of Daily Returns (Excluding BTC and ETH)",
)

# %% [markdown]
# We'll now include the BTC and ETH data and recalculate the correlation matrix and heatmap. Keep in mind that the BTC and ETH data only goes back to 2015 and 2018 respectively, so the correlation matrix will be calculated using a shorter time period than the other assets.

# %%
# Print the shape of the fund_data_daily_returns DataFrame to confirm that the rows with missing data have been dropped
print(f"Shape of fund_data_daily_returns: {fund_data_daily_returns_all.shape}")
print(f"Rows to drop due to missing data: {fund_data_daily_returns_all.dropna().shape}")

# Drop the NaN values
fund_data_daily_returns = fund_data_daily_returns_all.dropna()

# Calculate the correlation matrix of the daily returns
correlation_matrix = fund_data_daily_returns.corr()

display(correlation_matrix)

# %% [markdown]
# And then the heatmap:

# %%
plot_heatmap(
    df=correlation_matrix,
    title="Correlation Matrix of Daily Returns (Including BTC and ETH)",
)

# %% [markdown]
# These are interesting results, but expected. The stock funds tend to have low correlations with the bond funds, the commodities don't really correlate with anything, etc. But we know that the correlations between these asset classes have changed over time, so let's take a look at how the correlations have evolved over time by calculating rolling correlations.

# %% [markdown]
#  ## Calculate Rolling Correlations
#
#  Next, we will calculate the rolling correlations for several different periods:
#  * 1 month
#  * 3 month
#  * 6 month
#  * 1 year
#  * 5 years
#  * 10 years

# %%
# Define rolling windows in trading days
rolling_windows = {
    "3d": 3,  # 3 days (~3 trading days)
    "1w": 5,  # 1 week (~5 trading days)
    "2w": 10,  # 2 weeks (~10 trading days)
    "1m": 21,  # 1 month (~21 trading days)
    "3m": 63,  # 3 months (~63 trading days)
    "6m": 126,  # 6 months (~126 trading days)
    "1y": 252,  # 1 year (~252 trading days)
    "5y": 1260,  # 5 years (~1260 trading days)
    "10y": 2520,  # 10 years (~2520 trading days)
}

# %% [markdown]
# Before we run all of these, let's take a quick look at each of the rolling windows.

# %%
temp_df = fund_data_daily_returns_all[["IVV_Daily_Return", "IJH_Daily_Return"]].dropna()

for window_name, window_size in rolling_windows.items():
    rolling_corr = (
        temp_df["IVV_Daily_Return"]
        .rolling(window=window_size)
        .corr(temp_df["IJH_Daily_Return"])
    )

    print(tickers_dict["IVV"])
    print(tickers_dict["IJH"])

    plot_time_series(
        df=rolling_corr.to_frame(name="IVV_IJH_Rolling_Correlation"),
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=["IVV_IJH_Rolling_Correlation"],
        title=f"IVV vs IJH Rolling Correlation ({window_name} window)",
        x_label="Date",
        x_format="Year",
        x_tick_spacing=1,
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="Correlation",
        y_format="Decimal",
        y_format_decimal_places="Auto",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=False,
        export_plot=False,
        plot_file_name=None,
    )

# %% [markdown]
# Need to update
#
# <!-- Some inital thoughts here:
# * The 1 month and 3 month rolling windows are very noisy... it's going to be difficult to capture any kinds of meaningful trends with these short rolling windows - and these short-term movements are not the point of our investigation here.
# * The 6 months and 1 year rolling windows look like they might be a bit better, but still pretty noisy. We'll keep both of those.
# * The 5 year also looks potentially useful, but the 10 year is too long - it doesn't capture any of the medium-term movements that we are interested in. We'll keep the 5 year and drop the 10 year.
#
# So that leaves us with:
# * 6 months
# * 1 year
# * 5 years
#
# We are essentially looking to capture market movements over the months-to-years time frame (from a macro perspective), so the 6 month, 1 year, and 5 year rolling windows are the most appropriate for this analysis. -->

# %%
# Define rolling windows in trading days
rolling_windows = {
    "3d": 3,  # 3 days (~3 trading days)
    "1w": 5,  # 1 week (~5 trading days)
    "2w": 10,  # 2 weeks (~10 trading days)
    "1m": 21,  # 1 month (~21 trading days)
    "3m": 63,  # 3 months (~63 trading days)
}

# %%
from itertools import combinations

# Create temp list for tickers
temp_tickers = list(tickers_dict.keys())
pairs = list(combinations(temp_tickers, 2))

# Create empty dictionary to store rolling correlation results
rolling_correlation_results_no_crypto_dict = {}
rolling_correlation_results_no_crypto_df = pd.DataFrame()

for ticker1, ticker2 in pairs:
    try:
        temp_df = fund_data_daily_returns_no_crypto[
            [f"{ticker1}_Daily_Return", f"{ticker2}_Daily_Return"]
        ].dropna()
    except Exception as e:
        print(f"Error creating temp_df for {ticker1} and {ticker2}: {e}")
        continue

    for window_name, window_size in rolling_windows.items():
        try:
            rolling_corr = (
                temp_df[f"{ticker1}_Daily_Return"]
                .rolling(window=window_size)
                .corr(temp_df[f"{ticker2}_Daily_Return"])
            )

            print(tickers_dict[f"{ticker1}"])
            print(tickers_dict[f"{ticker2}"])

            rolling_correlation_results_no_crypto_dict[
                f"{ticker1}_{ticker2}_{window_name}"
            ] = rolling_corr
            rolling_correlation_results_no_crypto_df = pd.concat(
                [
                    rolling_correlation_results_no_crypto_df,
                    rolling_corr.to_frame(name=f"{ticker1}_{ticker2}_{window_name}"),
                ],
                axis=1,
            )

        except Exception as e:
            print(
                f"Error calculating rolling correlation for {ticker1} and {ticker2} with window {window_name}: {e}"
            )

# %%
display(rolling_correlation_results_no_crypto_df)

# %%
for window in rolling_windows.keys():
    plot_time_series(
        df=rolling_correlation_results_no_crypto_df,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[
            col
            for col in rolling_correlation_results_no_crypto_df.columns
            if f"{window}" in col
        ],
        title=f"Rolling {window} Correlation, No Crypto",
        x_label="Date",
        x_format="Year",
        x_tick_spacing=1,
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="Correlation",
        y_format="Decimal",
        y_format_decimal_places="Auto",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=False,
        export_plot=False,
        plot_file_name=None,
    )

# %% [markdown]
# ## Rolling Correlations Amongst US Stocks
#
# We'll now look specifically at the rolling correlations between the US S&P index ETFs (IVV, IJH, and IJR). We'll isolate the data for the rolling correlations for these three assets and see how the correlations have changed over time.

# %%
corr_list = [f"IVV_IJH_{window}", f"IVV_IJR_{window}", f"IJH_IJR_{window}"]

for window in rolling_windows.keys():
    plot_time_series(
        df=rolling_correlation_results_no_crypto_df,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=corr_list,
        title=f"Rolling {window} Correlation - US Equity ETFs (S&P 500, 400, 600)",
        x_label="Date",
        x_format="Year",
        x_tick_spacing=1,
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="Correlation",
        y_format="Decimal",
        y_format_decimal_places="Auto",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

# %% [markdown]
# With the above plot, we can see that there are periods of time when the correlations abruptly increase, such as:
#
# * Early-mid 2007 (the start of the financial crisis)
# * Mid 2011 (the European debt crisis)
# * Late 2015 into 2016
# * Late 2018 (rate hikes?)
# * Early 2020 (COVID-19 pandemic)
# * Late 2022 into early 2023 (rate hikes, recession fears, COVID tech bubble, etc.)
# * Mid 2024 (banking crisis, rate hikes)
# * Early 2025 (Liberation day)
#
# We're not necessarily looking to explain away each of these time periods or delve into the macro factors that may have been at play or driving the correlations, but we are more interested in the change in correlation over time on response to some kind of market shock or event.
#
# As an attempt to find some kind of signal, let's simply add the three correlations together to get a "total correlation" metric, and then plot that total correlation metric over time to see if we can identify any trends or patterns.

# %%
# Define rolling windows in trading days
return_windows = {
    "1d": 1,  # 1 day (~1 trading day)
    "3d": 3,  # 3 days (~3 trading days)
    "1w": 5,  # 1 week (~5 trading days)
    "2w": 10,  # 2 weeks (~10 trading days)
    "1m": 21,  # 1 month (~21 trading days)
    "2m": 42,  # 2 months (~42 trading days)
    "3m": 63,  # 3 months (~63 trading days)
    # '4m': 84,     # 4 months (~84 trading days)
    # '6m': 126,    # 6 months (~126 trading days)
    # '8m': 168,    # 8 months (~168 trading days)
    # '10m': 210,   # 10 months (~210 trading days)
    # '1y': 252,    # 1 year (~252 trading days)
    # '1y2m': 294,  # 1 year + 2 months (~294 trading days)
    # '1y4m': 336,  # 1 year + 4 months (~336 trading days)
    # '1y6m': 378,  # 1 year + 6 months (~378 trading days)
    # '1y8m': 420,  # 1 year + 8 months (~420 trading days)
    # '1y10m': 462, # 1 year + 10 months (~462 trading days)
    # '2y': 504,    # 2 years (~504 trading days)
}

# %%
corr_list = [f"IVV_IJH_{window}", f"IVV_IJR_{window}", f"IJH_IJR_{window}"]
fund_tickers = ["IVV", "IJH", "IJR"]

for window in rolling_windows.keys():
    us_sp_etfs = rolling_correlation_results_no_crypto_df[corr_list].dropna()

    # Add the correlations together
    us_sp_etfs["total_correlation"] = us_sp_etfs.sum(axis=1)

    # Merge daily returns into us_sp_etfs for the three ETFs
    us_sp_etfs = us_sp_etfs.merge(
        fund_data_daily_returns_all[
            [f"{ft}_Daily_Return" for ft in fund_tickers]
        ].dropna(),
        left_index=True,
        right_index=True,
        how="left",
    )

    plot_time_series(
        df=us_sp_etfs.dropna(),
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=["total_correlation"],
        title=f"Rolling {window} Total Correlation - US Equity ETFs (S&P 500, 400, 600)",
        x_label="Date",
        x_format="Year",
        x_tick_spacing=1,
        x_tick_start=None,
        x_tick_rotation=30,
        y_label=f"Rolling {window} Total Correlation",
        y_format="Decimal",
        y_format_decimal_places="Auto",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    for rw in return_windows.keys():
        for ft in fund_tickers:
            us_sp_etfs[f"{ft}_Daily_Return_{rw}_CRR"] = (
                us_sp_etfs[f"{ft}_Daily_Return"]
                .rolling(window=return_windows[rw])
                .apply(lambda x: (1 + x).prod() - 1)
            )
            us_sp_etfs[f"{ft}_Daily_Return_fwd_{rw}_CRR"] = us_sp_etfs[
                f"{ft}_Daily_Return_{rw}_CRR"
            ].shift(-return_windows[rw])

        plot_scatter(
            df=us_sp_etfs,
            x_plot_column="total_correlation",
            y_plot_columns=[
                col for col in us_sp_etfs.columns if f"fwd_{rw}_CRR" in col
            ],
            title=f"Rolling {window} Total Correlation vs Future {rw} Cumulative Rolling Return - US Equity ETFs (S&P 500, 400, 600)",
            x_label=f"Rolling {window} Total Correlation",
            x_format="Decimal",
            x_format_decimal_places=2,
            x_tick_spacing="Auto",
            x_tick_start=None,
            x_tick_rotation=30,
            y_label=f"Future {rw} Cumulative Rolling Return",
            y_format="Decimal",
            y_format_decimal_places=2,
            y_tick_spacing="Auto",
            y_tick_rotation=0,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        plot_histogram(
            df=us_sp_etfs,
            plot_columns=[col for col in us_sp_etfs.columns if f"fwd_{rw}_CRR" in col],
            title=f"Rolling {window} Total Correlation, Distribution of Future {rw} Cumulative Rolling Returns - US Equity ETFs (S&P 500, 400, 600)",
            x_label=f"Rolling {window} Total Correlation",
            x_tick_spacing="Auto",
            x_tick_rotation=30,
            y_label="Frequency",
            y_tick_spacing="Auto",
            y_tick_rotation=0,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

# %% [markdown]
# Now we'll look at a few different moving averages of the total correlation metric, the difference between the total correlation and the moving averages, and the percentage difference.

# %%
us_sp_etfs

# %%
ma_windows = [5, 10, 15, 20, 25]

for window in ma_windows:
    us_sp_etfs[f"total_correlation_{window}d_ma"] = (
        us_sp_etfs["total_correlation"].rolling(window=window).mean()
    )
    us_sp_etfs[f"total_correlation_diff_{window}d"] = (
        us_sp_etfs["total_correlation"] - us_sp_etfs[f"total_correlation_{window}d_ma"]
    )

display(us_sp_etfs)

# %%
us_sp_etfs[(us_sp_etfs.index >= "2020-01-01") & (us_sp_etfs.index <= "2021-01-01")]

# %%
plot_time_series(
    df=us_sp_etfs[
        (us_sp_etfs.index >= "2020-01-01") & (us_sp_etfs.index <= "2021-01-01")
    ],
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        col
        for col in us_sp_etfs.columns
        if "total_correlation" in col and "diff" not in col
    ],
    title="Total Correlation - US Equity ETFs (S&P 500, 400, 600)",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Correlation",
    y_format="Decimal",
    y_format_decimal_places="Auto",
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
fund_data_daily_returns_all

# %%
for ticker in us_equity_tickers:
    if ticker not in ["QQQ", "IWD", "IWF"]:
        plot_time_series(
            df=fund_data[
                (fund_data.index >= "2020-01-01") & (fund_data.index <= "2021-01-01")
            ],
            plot_start_date=None,
            plot_end_date=None,
            plot_columns=[f"{ticker}_Adj_Close"],
            title=f"{tickers_dict[ticker]} Adjusted Close Price",
            x_label="Date",
            x_format="Year",
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=30,
            y_label="Price ($)",
            y_format="Decimal",
            y_format_decimal_places="Auto",
            y_tick_spacing="Auto",
            y_tick_rotation=0,
            grid=True,
            legend=False,
            export_plot=False,
            plot_file_name=None,
        )

# %% [markdown]
# ## Future Investigation
#
# None for now.

# %% [markdown]
# ## References
#
# None for now.
