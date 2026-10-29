# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: jaredszajkowski-github-io (3.14.8)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Introduction
#
# In this post, we'll take a look at historical return correlations between asset classes, including rolling correlations and how those correlations have changed over time. We'll also build a "total correlation" metric, and a trading strategy that uses correlation as a market timing signal.

# %% [markdown]
#  ## Python Imports

# %%
# Standard Library
import os
import sys
import warnings

from IPython.display import display, Markdown
from itertools import combinations, count
from pathlib import Path

# Data Handling
import numpy as np
import pandas as pd

# Suppress warnings
warnings.filterwarnings("ignore")

# Pandas display options
pd.set_option("display.float_format", lambda x: f"%.2f" % x)

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
# * [plot_histogram](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_histogram): Plot the histogram of a data set from a DataFrame.
# * [plot_scatter](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter): Plot the data from a DataFrame for a specified date range and columns.
# * [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the timeseries data from a DataFrame for a specified date range and columns.
# * [run_linear_regression](/posts/reusable-extensible-python-functions-financial-data-analysis/#run_linear_regression): Run a linear regression using statsmodels OLS and return the results.
# * [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.
# * [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.

# %%
from load_data import load_data
from plot_heatmap import plot_heatmap
from plot_histogram import plot_histogram
from plot_scatter import plot_scatter
from plot_time_series import plot_time_series
from summary_stats import summary_stats
from yf_pull_data import yf_pull_data

# %% [markdown]
# ## Data Overview

# %% [markdown]
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

# %% [markdown]
# ### Acquire & Plot Data

# %% [markdown]
# We'll now pull the data for all the ETFs and cryptocurrencies listed above.

# %%
figure_number = count(1)
table_number = count(1)

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
# ### Load & Filter Data

# %% [markdown]
# We'll then peform the following:
# * Load data
# * Rename columns to include the ticker (e.g. "QQQ_Close", "QQQ_Adj_Close", etc.)
# * Drop all columns except for "Adj Close"
# * Calculate the daily returns
# * Combine the data into a single DataFrame
# * Check the inception date for each of thge funds

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

display(Markdown(f"Table {next(table_number)}: Fund Data"))
display(fund_data)

# %%
for ticker in tickers_dict.keys():
    print(f"First date for {ticker}: {fund_data[f'{ticker}_Daily_Return'].first_valid_index()}")

# %% [markdown]
# ### Plot Data

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
        title=f"Figure {next(figure_number)}: {tickers_dict[ticker]} Adjusted Close Price",
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
        caption=f"Data Source: Yahoo Finance, Analysis by the Author",
    )

# %% [markdown]
# ## Calculate Correlations

# %% [markdown]
# Next, we'll calculate the correlation matrix of the daily returns for all of the assets and plot it as a heatmap. We'll do this first without the BTC and ETH data (due to the limited history), and then with the BTC and ETH data.

# %%
# Drop the adjusted close price columns, leaving only the daily return columns
daily_return_columns = [f"{ticker}_Daily_Return" for ticker in tickers_dict.keys()]
fund_data_daily_returns_all = fund_data[daily_return_columns]

# Drop the BTC and ETH daily return columns due to the limited history
fund_data_daily_returns_no_crypto = fund_data_daily_returns_all.drop(columns=["BTC-USD_Daily_Return", "ETH-USD_Daily_Return"])

# Print the shape of the fund_data_daily_returns_no_crypto DataFrame to confirm that the rows with missing data have been dropped
print(f"Shape of fund_data_daily_returns_no_crypto: {fund_data_daily_returns_no_crypto.shape}")
print(f"Rows to drop due to missing data: {fund_data_daily_returns_no_crypto.dropna().shape}")

# Drop the NaN values
fund_data_daily_returns_no_crypto = fund_data_daily_returns_no_crypto.dropna()

# Calculate the correlation matrix of the daily returns
correlation_matrix_no_crypto = fund_data_daily_returns_no_crypto.corr()

display(Markdown(f"Table {next(table_number)}: Correlation Matrix of Daily Returns (Excluding BTC and ETH)"))
display(correlation_matrix_no_crypto)

# %% [markdown]
# And then the heatmap:

# %%
plot_heatmap(
    df=correlation_matrix_no_crypto,
    title=f"Figure {next(figure_number)}: Correlation Matrix of Daily Returns (Excluding BTC and ETH)",
    caption=f"Data Source: Yahoo Finance, Analysis by the Author",
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

display(Markdown(f"Table {next(table_number)}: Correlation Matrix of Daily Returns (Including BTC and ETH)"))
display(correlation_matrix)

# %% [markdown]
# And then the heatmap:

# %%
plot_heatmap(
    df=correlation_matrix,
    title=f"Figure {next(figure_number)}: Correlation Matrix of Daily Returns (Including BTC and ETH)",
    caption=f"Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# These are interesting results, but expected. The stock funds tend to have low correlations with the bond funds, the commodities don't really correlate with anything, etc. But we know that the correlations between these asset classes have changed over time, so let's take a look at how the correlations have evolved over time by calculating rolling correlations.

# %% [markdown]
# ## Calculate Rolling Correlations

# %% [markdown]
# Next, we will calculate the rolling correlations for several different periods:
#
# * 3 days
# * 1 week
# * 2 weeks
# * 1 month
# * 3 month
# * 6 month
# * 1 year
# * 5 years
# * 10 years

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
# We'll pair down the list of funds to only include the high correlation US equity funds that make up the S&P 1500 index (IVV, IJH, IJR).

# %%
# Create temp list for tickers
tickers = ["IVV", "IJH", "IJR"]
pairs = list(combinations(tickers, 2))

# Create empty dictionary to store rolling correlation results
rolling_corr_results = {}

# Create empty DataFrame to store rolling correlation results
rolling_corr_results_df = pd.DataFrame()

# Calculate rolling correlations for each pair of tickers and each rolling window
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

            # print(tickers_dict[f"{ticker1}"])
            # print(tickers_dict[f"{ticker2}"])

            rolling_corr_results[
                f"{ticker1}_{ticker2}_{window_name}"
            ] = rolling_corr
            rolling_corr_results_df = pd.concat(
                [
                    rolling_corr_results_df,
                    rolling_corr.to_frame(name=f"{ticker1}_{ticker2}_{window_name}"),
                ],
                axis=1,
            )

        except Exception as e:
            print(
                f"Error calculating rolling correlation for {ticker1} and {ticker2} with window {window_name}: {e}"
            )

display(Markdown(f"Table {next(table_number)}: Rolling Correlations"))
display(rolling_corr_results_df)

# %%
for window in rolling_windows.keys():
    plot_time_series(
        df=rolling_corr_results_df,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[col for col in rolling_corr_results_df.columns if f"{window}" in col],
        title=f"Figure {next(figure_number)}: Rolling {window} Correlation",
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
        caption=f"Data Source: Yahoo Finance, Analysis by the Author",
    )

# %% [markdown]
# ## Total Correlation Metric

# %% [markdown]
# With the above plots, we can see that there are periods of time when the correlations abruptly increase or decrease, such as:
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
# We're not necessarily looking to explain away each of these time periods or delve into the macro factors that may have been at play or driving the correlations, but we are more interested in the change in correlation over time as a response to some kind of market shock or event.
#
# As an attempt to find some kind of signal, let's simply add the correlations together to get a "total correlation" metric, and look at the distribution. Note that we normalize the correlations to account for the number of correlations being summed by dividing the total by the number of correlations, to keep the values between -1 and 1.

# %%
# Calculate total rolling correlation for each window
for window, days in rolling_windows.items():
    rolling_corr_results_df[f"total_rolling_correlation_{window}"] = rolling_corr_results_df[[col for col in rolling_corr_results_df.columns if col.endswith(f"_{window}")]].sum(axis=1) / len([col for col in rolling_corr_results_df.columns if col.endswith(f"_{window}")])

# Reset any 0.00 values to NaN
rolling_corr_results_df.replace(0.00, np.nan, inplace=True)

# %%
for window in rolling_windows.keys():
    plot_histogram(
        df=rolling_corr_results_df[[f"total_rolling_correlation_{window}"]].dropna(),
        plot_columns=[f"total_rolling_correlation_{window}"],
        title=f"Figure {next(figure_number)}: Total Rolling Correlation ({window})",
        x_label="Total Rolling Correlation",
        x_tick_spacing="Auto",
        x_tick_rotation=0,
        y_label="Frequency",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        caption=f"Data Source: Yahoo Finance, Analysis by the Author",
    )

# %% [markdown]
# Alright, so the distributions for 1w, 2w, and 1m look interesting. For each of those windows, let's look at the different deciles of the rolling correlations, and what that implies for future returns.

# %% [markdown]
# ## Future Returns Based On Total Rolling Correlation

# %% [markdown]
# First, we need to define the forward return windows that we want to look at.

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
}

# %% [markdown]
# Then, we'll merge in the returns and create the forward returns for each of the funds.

# %%
# Merge daily returns in for the ETFs
total_rolling_corr_with_returns = rolling_corr_results_df.merge(
    fund_data_daily_returns_all[
        [f"{ft}_Daily_Return" for ft in tickers]
    ].dropna(),
    left_index=True,
    right_index=True,
    how="left",
)

# Calculate compounded rolling returns (CRR), and then shift to create forward returns
for rw in return_windows.keys():
    for ft in tickers:
        total_rolling_corr_with_returns[f"{ft}_Daily_Return_{rw}_CRR"] = (
            total_rolling_corr_with_returns[f"{ft}_Daily_Return"]
            .rolling(window=return_windows[rw])
            .apply(lambda x: (1 + x).prod() - 1, raw=True)
        )
        total_rolling_corr_with_returns[f"{ft}_Daily_Return_fwd_{rw}_CRR"] = total_rolling_corr_with_returns[
            f"{ft}_Daily_Return_{rw}_CRR"
        ].shift(-return_windows[rw])

display(Markdown(f"Table {next(table_number)}: Total Rolling Correlations With Forward Returns"))
display(total_rolling_corr_with_returns)

# %% [markdown]
# ### Summary By Decile

# %% [markdown]
# Before looking at the individual plots, here is a summary of the forward returns for each decile of total rolling correlation compared with the baseline (all days). Values are in percent.

# %%
analysis_windows = ["1w", "2w", "1m"]
decile_labels = [f"D{i}" for i in range(1, 11)]

decile_summary = {}

for window in analysis_windows:
    col = f"total_rolling_correlation_{window}"
    df = total_rolling_corr_with_returns.dropna(subset=[col])

    # Assign each day to a correlation decile and record each decile's range
    bucket = pd.qcut(df[col], 10, labels=decile_labels)
    ranges = df[col].groupby(bucket, observed=True).agg(["min", "max"])
    row_labels = ["Baseline (all days)"] + [
        f"{d} ({ranges.loc[d, 'min']:.2f} to {ranges.loc[d, 'max']:.2f})" for d in decile_labels
    ]

    pct_positive = {}
    mean_return = {}
    for rw in return_windows.keys():
        for ft in tickers:
            fwd = df[f"{ft}_Daily_Return_fwd_{rw}_CRR"]
            valid = fwd.notna()
            fwd, b = fwd[valid], bucket[valid]
            pct_positive[(rw, ft)] = [(fwd > 0).mean() * 100] + list(fwd.gt(0).groupby(b, observed=True).mean() * 100)
            mean_return[(rw, ft)] = [fwd.mean() * 100] + list(fwd.groupby(b, observed=True).mean() * 100)

    decile_summary[window] = {
        "pct_positive": pd.DataFrame(pct_positive, index=row_labels),
        "mean_return": pd.DataFrame(mean_return, index=row_labels),
    }

# %%
for window in analysis_windows:
    display(Markdown(f"Table {next(table_number)}: Percentage of Positive Future Returns by {window} Total Rolling Correlation Decile"))
    display(decile_summary[window]["pct_positive"])
    display(Markdown(f"Table {next(table_number)}: Mean Future Return (%) by {window} Total Rolling Correlation Decile"))
    display(decile_summary[window]["mean_return"])

# %% [markdown]
# ### Plots By Decile

# %% [markdown]
# Now the plots to illustrate the tables above:

# %%
for window in analysis_windows:
    for ticker in tickers:
        # Select this fund's columns (one per return window) and move the decile labels into a column
        ticker_df = (
            decile_summary[window]["pct_positive"]
            .xs(ticker, axis=1, level=1)
            .reset_index(names="Decile")
        )

        plot_scatter(
            df=ticker_df,
            x_plot_column="Decile",
            y_plot_columns=list(return_windows.keys()),
            title=f"Figure {next(figure_number)}: {ticker} Percentage of Positive Future Returns By Rolling {window} Total Correlation Decile + Baseline",
            x_label=f"Rolling {window} Total Correlation Decile or Baseline",
            x_format="String",
            x_format_decimal_places="Auto",
            x_tick_spacing="Auto",
            x_tick_start=None,
            x_tick_rotation=30,
            y_label="Positive Future Returns (%)",
            y_format="Decimal",
            y_format_decimal_places=0,
            y_tick_spacing="Auto",
            y_tick_rotation=0,
            grid=True,
            legend=True,
            legend_location="upper left",
            legend_anchor=(1, 1),
            caption=f"Data Source: Yahoo Finance, Analysis by the Author",
        )

# %% [markdown]
# It's interesting what the baseline (all days) columns reveal about future returns. For *every* plot, the positive future return percentage increases as time increases. We see a similar, but slightly less pronounced, trend for the total rolling correlation deciles, and this suggests that, on average, the likelihood of positive future returns grows over longer time horizons, regardless of the rolling correlation decile. There is certainly a "belly" present in some of the plots, particularly at the 6th and 7th deciles.
#
# The 10th decile consistently shows the highest positive future return percentages across all time horizons, indicating that assets in this decile tend to perform better in the future compared to those in lower deciles, so let's cherry pick the 2 week total rolling correlation for IVV, IJH, and IJR, at the 10th decile, and the 3 month forward return to examine more closely.

# %% [markdown]
# ## 2w Total Rolling Correlation, 10th Decile, 3m Forward Return for IVV

# %%
# Assign each day to a correlation decile and record each decile's range
bucket = pd.qcut(total_rolling_corr_with_returns.dropna(subset=["total_rolling_correlation_2w"])["total_rolling_correlation_2w"], 10, labels=decile_labels)

# Merge the decile bucket back into the original DataFrame
total_rolling_corr_with_returns = total_rolling_corr_with_returns.dropna(subset=["total_rolling_correlation_2w"])
total_rolling_corr_with_returns["total_rolling_correlation_2w_decile"] = bucket

display(Markdown(f"Table {next(table_number)}: Total Rolling Correlations With 2w Decile Assignments"))
display(total_rolling_corr_with_returns)

# %%
for ticker in tickers:
    plot_scatter(
        df=total_rolling_corr_with_returns[total_rolling_corr_with_returns["total_rolling_correlation_2w_decile"] == "D10"],
        x_plot_column="total_rolling_correlation_2w",
        y_plot_columns=[f"{ticker}_Daily_Return_fwd_3m_CRR"],
        title=f"Figure {next(figure_number)}: {ticker} 3 Month Future Returns vs 2 Week Total Rolling Correlation in Decile 10",
        x_label="2 Week Total Rolling Correlation (Normalized)",
        x_format="Decimal",
        x_format_decimal_places="Auto",
        x_tick_spacing="Auto",
        x_tick_start=None,
        x_tick_rotation=30,
        y_label=f"Future 3 Month Cumulative Rolling Return for {ticker}",
        y_format="Decimal",
        y_format_decimal_places=2,
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
        caption=f"Data Source: Yahoo Finance, Analysis by the Author",
    )

    plot_histogram(
        df=total_rolling_corr_with_returns[total_rolling_corr_with_returns["total_rolling_correlation_2w_decile"] == "D10"],
        plot_columns=[f"{ticker}_Daily_Return_fwd_3m_CRR"],
        title=f"Figure {next(figure_number)}: {ticker} Distribution of Future 3 Month Cumulative Rolling Returns from 2 Week Total Rolling Correlation in Decile 10",
        x_label="Future 3 Month Cumulative Rolling Return",
        x_tick_spacing="Auto",
        x_tick_rotation=30,
        y_label="Frequency",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
        caption=f"Data Source: Yahoo Finance, Analysis by the Author",
    )

# %% [markdown]
# ## Trading Strategy

# %% [markdown]
# Next, let's develop a simple trading strategy. When the total rolling correlation hits the 10th decile, we will open a long position in the fund, hold the position for exactly 3 months, and then close it. We'll run the strategy separately for each of the three funds. Here's the complete details:
#
# * Use the 10th decile of the total rolling correlation as the signal for entering a trade.
# * Position sizing: we always go fully long on the fund when a signal occurs, and we do not scale in or out.
# * Entry: when the 2w total correlation decile is D10 on day i, buy the fund at that day's close.
# * Exit: hold for exactly 63 trading days (return_windows["3m"]), then sell at that day's close.
# * Overlapping signals: a D10 day that comes while a position is open is ignored. If the exit day is itself a D10 day, the strategy buys again, so the position just continues.
# * Shared signal: the signal comes from the total correlation across all three funds, so the entry and exit dates are the same for IVV, IJH, and IJR. Only the returns differ.
# * Settings: strategy_tickers, signal_decile and hold_days are variables at the top, so we can easily modify them to try other combinations.
#
# We'll start with the strategy, and the complete list of trades.

# %%
# Strategy parameters
strategy_tickers = ["IVV", "IJH", "IJR"]
signal_column = "total_rolling_correlation_2w_decile"
signal_decile = "D10"
hold_days = return_windows["3m"]  # 63 trading days

strategy_df = total_rolling_corr_with_returns[
    ["total_rolling_correlation_2w", signal_column] + [f"{ticker}_Daily_Return" for ticker in strategy_tickers]
].copy()
for ticker in strategy_tickers:
    strategy_df[f"{ticker}_Daily_Return"] = strategy_df[f"{ticker}_Daily_Return"].fillna(0)
strategy_df["Signal"] = strategy_df[signal_column] == signal_decile

# Walk forward through the days. A signal at the close of day i opens a position at that close,
# which earns the returns of days i+1 through i+hold_days and is then closed. Signals that occur
# while a position is already open are ignored. The signal comes from the total correlation alone,
# so the entry and exit dates are the same for every fund and only the returns differ.
signals = strategy_df["Signal"].to_numpy()
position = np.zeros(len(strategy_df))
trades = []

i = 0
while i < len(strategy_df) - 1:  # A signal on the last day has no following days to trade
    if not signals[i]:
        i += 1
        continue

    entry_idx = i
    exit_idx = min(i + hold_days, len(strategy_df) - 1)
    position[entry_idx + 1 : exit_idx + 1] = 1

    trade = {
        "Entry Date": strategy_df.index[entry_idx],
        "Exit Date": strategy_df.index[exit_idx],
        "Entry Correlation": strategy_df["total_rolling_correlation_2w"].iloc[entry_idx],
        "Days Held": exit_idx - entry_idx,
        "Open": exit_idx - entry_idx < hold_days,  # True if the data ends before the hold period does
    }
    for ticker in strategy_tickers:
        daily_returns = strategy_df[f"{ticker}_Daily_Return"].to_numpy()
        trade[f"{ticker} Return"] = np.prod(1 + daily_returns[entry_idx + 1 : exit_idx + 1]) - 1
    trades.append(trade)

    i = exit_idx

strategy_df["Position"] = position
for ticker in strategy_tickers:
    strategy_df[f"{ticker}_Strategy_Return"] = strategy_df["Position"] * strategy_df[f"{ticker}_Daily_Return"]

display(Markdown(f"Table {next(table_number)}: Days in D10 With an Open Position"))
display(strategy_df[
    (strategy_df["total_rolling_correlation_2w_decile"] == "D10") &
    (strategy_df["Position"] == 1)
])

trades_df = pd.DataFrame(trades)
display(Markdown(f"Table {next(table_number)}: Strategy Trades"))
display(trades_df)

# %% [markdown]
# Next, here's the statistics for win rate, average return, max gain, and max loss.

# %%
# Trade summary
closed_trades = trades_df[~trades_df["Open"]]

print(f"Total trades: {len(trades_df)} ({len(closed_trades)} closed)")
print(f"Time in market: {strategy_df['Position'].mean() * 100:.2f}%")

for ticker in strategy_tickers:
    trade_returns = closed_trades[f"{ticker} Return"]
    print(f"\n{ticker}:")
    print(f"  Win rate (closed trades): {(trade_returns > 0).mean() * 100:.2f}%")
    print(f"  Average return per closed trade: {trade_returns.mean() * 100:.2f}%")
    print(f"  Max trade gain: {trade_returns.max() * 100:.2f}%")
    print(f"  Max trade loss: {trade_returns.min() * 100:.2f}%")

# %% [markdown]
# Now we can compare the summary stats for the different funds and see how the strategy performed across IVV, IJH, and IJR.

# %%
# Compare each strategy against buy and hold for the same period
strategy_stats = pd.concat(
    [
        summary_stats(
            fund_list=[ticker],
            df=strategy_df[[return_column]],
            period="Daily",
            use_calendar_days=False,
            excel_export=False,
            pickle_export=False,
            output_confirmation=False,
        )
        for ticker in strategy_tickers
        for return_column in [f"{ticker}_Strategy_Return", f"{ticker}_Daily_Return"]
    ]
)

display(Markdown(f"Table {next(table_number)}: Strategy vs Buy and Hold Summary Statistics"))
display(strategy_stats)

# %% [markdown]
# And finally, the plots for the cumulative returns and drawdowns.

# %%
# Cumulative returns for each strategy and buy and hold
for ticker in strategy_tickers:
    strategy_df[f"{ticker}_Strategy_Cumulative_Return"] = (1 + strategy_df[f"{ticker}_Strategy_Return"]).cumprod() - 1
    strategy_df[f"{ticker}_Buy_Hold_Cumulative_Return"] = (1 + strategy_df[f"{ticker}_Daily_Return"]).cumprod() - 1

plot_time_series(
    df=strategy_df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{ticker}_Strategy_Cumulative_Return" for ticker in strategy_tickers]
    + [f"{ticker}_Buy_Hold_Cumulative_Return" for ticker in strategy_tickers],
    title=f"Figure {next(figure_number)}: Total Rolling Correlation {signal_decile} Strategies vs Buy and Hold",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
    caption=f"Data Source: Yahoo Finance, Analysis by the Author",
)

# %%
# Drawdowns for each strategy and buy and hold, measured from the running peak of each equity curve
for ticker in strategy_tickers:
    strategy_equity = (1 + strategy_df[f"{ticker}_Strategy_Return"]).cumprod()
    buy_hold_equity = (1 + strategy_df[f"{ticker}_Daily_Return"]).cumprod()

    strategy_df[f"{ticker}_Strategy_Drawdown"] = strategy_equity / strategy_equity.cummax() - 1
    strategy_df[f"{ticker}_Buy_Hold_Drawdown"] = buy_hold_equity / buy_hold_equity.cummax() - 1

plot_time_series(
    df=strategy_df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{ticker}_Strategy_Drawdown" for ticker in strategy_tickers]
    + [f"{ticker}_Buy_Hold_Drawdown" for ticker in strategy_tickers],
    title=f"Figure {next(figure_number)}: Total Rolling Correlation {signal_decile} Strategies vs Buy and Hold Drawdowns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
    caption=f"Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# We end up with 44 trades over the 20 year period, with a win rate of 68% for IVV and IJH, and 66% for IJR, not bad overall. Since the signal is shared, all three strategies spend just under 55% of their time in the market, which really gives us an opportunity to use our capital the other 45% of the time, either in a risk free asset or another strategy altogether.
#
# For IVV, with a CAGR of 8%, we underperform the buy-and-hold strategy over the same period, but we also experience lower volatility (16% vs 19%), and much lower max drawdowns (30% vs 55%). Our strategy gives us a MAR ratio of 0.28, vs 0.20 for the buy-and-hold strategy.
#
# IJH and IJR tell a similar story, but the gap in CAGR is much smaller:
#
# * IJH: a CAGR of 9.1% vs 9.7% for buy-and-hold, with lower volatility (18% vs 22%), lower max drawdowns (36% vs 55%), and a MAR ratio of 0.25 vs 0.18.
# * IJR: a CAGR of 8.9% vs 9.3% for buy-and-hold, with lower volatility (19% vs 24%), lower max drawdowns (35% vs 58%), and a MAR ratio of 0.25 vs 0.16.
#
# For IJH and IJR, we give up less than 1% of CAGR per year in exchange for the reduced risk, and both strategies also have a higher Sharpe ratio than their buy-and-hold counterparts, which is not the case for IVV.
#
# The difference in CAGR does add up over the long term, the effect of which we can see in the cumulative return plot, particularly for IVV.
#
# The drawdown plot further illustrates the reduced risk of the strategies compared to the buy-and-hold approach, highlighting the lower maximum drawdowns experienced over the same period. During the GFC, the IVV strategy experienced its max drawdown of 30%, which was significantly lower than that of the buy-and-hold strategy at 55%. Interestingly, the max drawdowns for the IJH and IJR strategies came during the COVID crash in early 2020 rather than the GFC, while all three buy-and-hold strategies saw their max drawdowns during the GFC.

# %% [markdown]
# ## Conclusion
#
# Overall, this was a brief but interesting study that dove into the historical correlations amongst a wide range of asset classes. We looked at a series of rolling correlations amongst the asset classes, and then delved into the different deciles of a "total correlation" metric, assembled from the rolling correlations of 3 well known US equity ETFs. This analysis, including comparison to a baseline, gave us insight into where the total correlations could be used to improve our ability to time market entries and exits. Finally, we built a simple trading strategy using a single total correlation window and decile and a single future return window, as a proof of concept for how these insights could be applied in practice. This strategy, while underperforming over the long-term, did have lower volatility and drawdowns, demonstrating the potential risk management benefits of incorporating total correlation information into trading decisions.

# %% [markdown]
# ## Future Investigation
#
# None

# %% [markdown]
# ## References
#
# None
