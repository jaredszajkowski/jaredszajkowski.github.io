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
# Over the past 15 years (or so), leveraged ETFs have become frequently used for trading equity indices, sectors, and other asset classes by the investor that is seeking to use leverage for excess exposure to those asset classes. The question remains, however, what happens to the returns of leveraged ETFs over an extended time horizon and is there an optimal leverage ratio for the long-term buy-and-hold investor that allows them to take advantage of leverage to increase the up-side returns, while avoiding catastrophic losses on the down-side? In this investigation, we will delve into these ideas and see what the data shows.

# %% [markdown]
#  ## Python Imports

# %%
# Standard Library
import os
import sys
import warnings

from pathlib import Path

# Data Handling
import pandas as pd

# Suppress warnings
warnings.filterwarnings("ignore")

# %%
# Add the source subdirectory to the system path to allow import config from settings.py
current_directory = Path(os.getcwd())
website_base_directory = current_directory.parent.parent.parent
src_directory = website_base_directory / "src"
sys.path.append(str(src_directory)) if str(src_directory) not in sys.path else None

# Import settings.py
from settings import config

# Add configured directories from config to path
SOURCE_DIR = config("SOURCE_DIR")
sys.path.append(str(Path(SOURCE_DIR))) if str(Path(SOURCE_DIR)) not in sys.path else None

# Add other configured directories
BASE_DIR = config("BASE_DIR")
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
# * [run_regression](/posts/reusable-extensible-python-functions-financial-data-analysis/#run_regression): Run a linear regression using statsmodels OLS and return the results.
# * [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.
# * [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.

# %%
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_histogram import plot_histogram
from plot_scatter import plot_scatter
from plot_time_series import plot_time_series
from run_regression import run_regression
from summary_stats import summary_stats
from yf_pull_data import yf_pull_data

# %% [markdown]
# ## Data Overview
#
# For this exercise, we will investigate the long-term return relationships between the following:
#
# * QQQ (Invesco QQQ Trust, Series 1) and TQQQ (ProShares  UltraPro QQQ)
# * SPY (SPDR S&P 500 ETF Trust) and UPRO (ProShares UltraPro S&P 500)
#
# Just to clarify, any time we are referring to "close prices" in this analysis, we are referring to the partially-adjusted close prices that account for splits, but not dividends. Because we are dealing with leveraged ETFs, we want to focus on the pure returns due to change in price, but exclude the dividends, which are not leveraged in the same way as the price changes.
#
# ## QQQ & TQQQ
#
# ### Acquire & Plot Data (QQQ)
#
# First, let's get the data for QQQ. If we already have the desired data, we can load it from a local pickle file. Otherwise, we can download it from Yahoo Finance using the `yf_pull_data` function.

# %%
pandas_set_decimal_places(2)

yf_pull_data(
    base_directory=DATA_DIR,
    ticker="QQQ",
    adjusted=False,
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

qqq = load_data(
    base_directory=DATA_DIR,
    ticker="QQQ",
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "QQQ_Close", etc.
qqq = qqq.rename(columns={
    "Adj Close": "QQQ_Adj_Close",
    "Close": "QQQ_Close",
    "High": "QQQ_High",
    "Low": "QQQ_Low",
    "Open": "QQQ_Open",
    "Volume": "QQQ_Volume"
})

display(qqq)

# %% [markdown]
# And the plot of the time series of partially adjusted close prices:

# %%
plot_time_series(
    df=qqq,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Adj_Close"],
    title="QQQ Adjusted Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# ### Acquire & Plot Data (TQQQ)
#
# Next, TQQQ:

# %%
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="TQQQ",
    adjusted=False,
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

tqqq = load_data(
    base_directory=DATA_DIR,
    ticker="TQQQ",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "TQQQ_Close", etc.
tqqq = tqqq.rename(columns={
    "Adj Close": "TQQQ_Adj_Close",
    "Close": "TQQQ_Close", 
    "High": "TQQQ_High", 
    "Low": "TQQQ_Low", 
    "Open": "TQQQ_Open", 
    "Volume": "TQQQ_Volume"
})

display(tqqq)

# %% [markdown]
# And the plot of the time series of partially adjusted close prices:

# %%
plot_time_series(
    df=tqqq,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_Adj_Close"],
    title="TQQQ Adjusted Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# Looking at the close prices doesn't give us a true picture of the magnitude of the difference in returns due to the leverage. In order to see that, we need to look at the cumulative returns and the drawdowns.
#
#  ### Calculate & Plot Cumulative Returns, Rolling Returns, and Drawdowns (QQQ & TQQQ)
#
#  Next, we will calculate the cumulative returns, rolling returns, and drawdowns. This involves aligning the data to start with the inception of TQQQ. For this excercise, we will not extrapolate the data for QQQ back to 1999, but rather just align the data from the inception of TQQQ in 2010.

# %%
etfs = ["QQQ", "TQQQ"]

# Merge dataframes and drop rows with missing values
qqq_tqqq_aligned = tqqq.merge(qqq, left_index=True, right_index=True, how='left')
qqq_tqqq_aligned = qqq_tqqq_aligned.dropna()

# Calculate cumulative returns
for etf in etfs:
    qqq_tqqq_aligned[f"{etf}_Return"] = qqq_tqqq_aligned[f"{etf}_Close"].pct_change()
    qqq_tqqq_aligned[f"{etf}_Cumulative_Return"] = (1 + qqq_tqqq_aligned[f"{etf}_Return"]).cumprod() - 1
    qqq_tqqq_aligned[f"{etf}_Cumulative_Return_Plus_One"] = 1 + qqq_tqqq_aligned[f"{etf}_Cumulative_Return"]
    qqq_tqqq_aligned[f"{etf}_Rolling_Max"] = qqq_tqqq_aligned[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    qqq_tqqq_aligned[f"{etf}_Drawdown"] = qqq_tqqq_aligned[f"{etf}_Cumulative_Return_Plus_One"] / qqq_tqqq_aligned[f"{etf}_Rolling_Max"] - 1
    qqq_tqqq_aligned.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)

# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        qqq_tqqq_aligned[f"{etf}_Rolling_Return_{period_name}"] = (
            qqq_tqqq_aligned[f"{etf}_Close"].pct_change(periods=window)
        )
        
display(qqq_tqqq_aligned)

# %% [markdown]
# And now the plot for the cumulative returns:

# %%
plot_time_series(
    df=qqq_tqqq_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Cumulative_Return", "TQQQ_Cumulative_Return"],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# And the drawdown plot:

# %%
plot_time_series(
    df=qqq_tqqq_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Drawdown", "TQQQ_Drawdown"],
    title="Drawdowns",
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
)

# %% [markdown]
# Here is where we truly see the volatility of TQQQ relative to QQQ. In the past 5 years, TQQQ has had drawdowns of 50%, 60%, 70%, and 80%. While it has recovered to make new highs (with the exception of the current ~25% drawdown as of mid-March 2026), very few investors can endure those drawdowns and continue to hold their position. At the same time, we can see from the plot that a ~35% drawdown in QQQ equated to a ~80% drawdown in TQQQ, which is not in fact, 3x. So this tells us (which we already knew) that there is dispersion in the long-term returns relative to the short-term returns between the non-leveraged QQQ and 3x leveraged TQQQ. This idea is well documented in the financial literature as "volatility decay" or "volatility drag". But, and this is the question we are trying to answer, how significant is this effect over various time horizons?
#
# ### Summary Statistics (QQQ & TQQQ)
#
# Looking at the summary statistics further confirms our intuitions about the volatility and drawdowns.

# %%
qqq_sum_stats = summary_stats(
    fund_list=["QQQ"],
    df=qqq_tqqq_aligned[["QQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

tqqq_sum_stats = summary_stats(
    fund_list=["TQQQ"],
    df=qqq_tqqq_aligned[["TQQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([qqq_sum_stats, tqqq_sum_stats])

display(sum_stats)

# %% [markdown]
# Note that these statistics are being run on the partially-adjusted close prices, which are not the true returns (due to not accounting for dividends), but they do give us a picture of the relative volatility and drawdowns of the two ETFs. The mean return for TQQQ is much higher than that of QQQ, but the volatility is also much higher, which is consistent with the idea of leverage amplifying both the up-side and down-side. The maximum drawdown for TQQQ is also much higher than that of QQQ, which again confirms our observations from the drawdown plot.
#
# Also note that the daily maximum return for both funds occured during "Liberation Day" and the daily minimum return for both funds occured early on during the COVID-19 pandemic.
#
# ### Plot Returns & Verify Beta (QQQ & TQQQ)
#
# Before we look at the rolling returns, let us first verify that the daily returns for TQQQ are in fact ~3x those of QQQ. We can do that by plotting the daily returns for both funds against each other and running a linear regression to see if the beta is indeed ~3.

# %%
plot_scatter(
    df=qqq_tqqq_aligned,
    x_plot_column="QQQ_Return",
    y_plot_columns=["TQQQ_Return"],
    title="QQQ & TQQQ Returns",
    x_label="QQQ Return",
    x_format="Decimal",
    x_format_decimal_places=2,
    x_tick_spacing="Auto",
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="TQQQ Return",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=True,
    OLS_column="TQQQ_Return",
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=True,
    RidgeCV_column="TQQQ_Return",
    regression_constant=True,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
model = run_regression(
    df=qqq_tqqq_aligned,
    x_plot_column="QQQ_Return",
    y_plot_column="TQQQ_Return",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)

print(model.summary())

# %% [markdown]
# Visually, this plot makes sense and we can see that there is a strong clustering of points, but we double check with the regression, regressing the TQQQ daily return (y) on the QQQ daily return (X).
#
# Given the above result, with a coefficient of 2.96 and an R^2 of 0.997 (based on the statsmodels OLS regression), we can say that TQQQ does in fact return ~3x QQQ. We would also intuitively expect the coefficient to be 0, and it is nearly 0.
#
# Interestingly, the coefficient varies between OLS and Ridge cross-validation, and both are less than 3.
#
# ### Extrapolate Data (QQQ & TQQQ)
#
# With the above coefficient, we will now extrapolate the returns of QQQ to backfill the data from the inception of QQQ in 1999 to the inception of TQQQ in 2010 to expand our dataset of returns. For this, we'll use the coefficient of 2.96 that we found in the regression results above.

# %%
# Set leverage multiplier based on regression coefficient
LEVERAGE_MULTIPLIER = model.params.iloc[1]

# Merge dataframes and extrapolate return values for QQQ back to 1999 using the leverage multiplier
qqq_tqqq_extrap = qqq[["QQQ_Close"]].merge(tqqq[["TQQQ_Close"]], left_index=True, right_index=True, how='left')

etfs = ["QQQ", "TQQQ"]

# Calculate cumulative returns
for etf in etfs:
    qqq_tqqq_extrap[f"{etf}_Return"] = qqq_tqqq_extrap[f"{etf}_Close"].pct_change()

# Extrapolate TQQQ returns for missing values
qqq_tqqq_extrap["TQQQ_Return"] = qqq_tqqq_extrap["TQQQ_Return"].fillna(LEVERAGE_MULTIPLIER * qqq_tqqq_extrap["QQQ_Return"])

# Find the first valid TQQQ_Close index and value
first_valid_idx = qqq_tqqq_extrap['TQQQ_Close'].first_valid_index()
print(first_valid_idx)
first_valid_price = qqq_tqqq_extrap.loc[first_valid_idx, 'TQQQ_Close']
print(first_valid_price)

# %% [markdown]
# Before we extrapolate, let's first look at the data we have for QQQ and TQQQ around the inception of TQQQ in 2010:

# %%
# Check values around the first valid index
pandas_set_decimal_places(4)
display(qqq_tqqq_extrap.loc["2010-02-08":"2010-02-13"])

# %% [markdown]
# Now, backfill the data for the TQQQ close price:

# %%
# Iterate through the dataframe backwards
for i in range(qqq_tqqq_extrap.index.get_loc(first_valid_idx) - 1, -1, -1):
    
    # The return that led to the price the next day
    current_return = qqq_tqqq_extrap.iloc[i + 1]['TQQQ_Return']

    # Get the next day's price
    next_price = qqq_tqqq_extrap.iloc[i + 1]['TQQQ_Close']
    
    # Price_{t} = Price_{t+1} / (1 + Return_{t})
    qqq_tqqq_extrap.loc[qqq_tqqq_extrap.index[i], 'TQQQ_Close'] = next_price / (1 + current_return)

# %% [markdown]
# Finally, confirm the values are correct:

# %%
# Confirm values around the first valid index after extrapolation
display(qqq_tqqq_extrap.loc["2010-02-08":"2010-02-13"])

# %% [markdown]
# And the complete DataFrame with the extrapolated values:

# %%
pandas_set_decimal_places(2)
display(qqq_tqqq_extrap)

# %% [markdown]
# After the extrapolation, we now have the following plots for the prices, cumulative returns, and drawdowns:

# %%
etfs = ["QQQ", "TQQQ"]

# Calculate cumulative returns
for etf in etfs:
    qqq_tqqq_extrap[f"{etf}_Return"] = qqq_tqqq_extrap[f"{etf}_Close"].pct_change()
    qqq_tqqq_extrap[f"{etf}_Cumulative_Return"] = (1 + qqq_tqqq_extrap[f"{etf}_Return"]).cumprod() - 1
    qqq_tqqq_extrap[f"{etf}_Cumulative_Return_Plus_One"] = 1 + qqq_tqqq_extrap[f"{etf}_Cumulative_Return"]
    qqq_tqqq_extrap[f"{etf}_Rolling_Max"] = qqq_tqqq_extrap[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    qqq_tqqq_extrap[f"{etf}_Drawdown"] = qqq_tqqq_extrap[f"{etf}_Cumulative_Return_Plus_One"] / qqq_tqqq_extrap[f"{etf}_Rolling_Max"] - 1
    qqq_tqqq_extrap.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)

# %%
plot_time_series(
    df=qqq_tqqq_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Close"],
    title="QQQ Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_time_series(
    df=qqq_tqqq_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_Close"],
    title="TQQQ Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_time_series(
    df=qqq_tqqq_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Cumulative_Return", "TQQQ_Cumulative_Return"],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_time_series(
    df=qqq_tqqq_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Drawdown", "TQQQ_Drawdown"],
    title="Drawdowns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
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
)

# %%
qqq_extrap_sum_stats = summary_stats(
    fund_list=["QQQ"],
    df=qqq_tqqq_extrap[["QQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

tqqq_extrap_sum_stats = summary_stats(
    fund_list=["TQQQ"],
    df=qqq_tqqq_extrap[["TQQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([qqq_sum_stats, tqqq_sum_stats, qqq_extrap_sum_stats, tqqq_extrap_sum_stats])
sum_stats.index = ["QQQ (2010 - Present)", "TQQQ (2010 - Present)", "QQQ (1999 - Present)", "TQQQ Extrapolated (1999 - Present)"]

display(sum_stats)

# %% [markdown]
# A few quick comments before we look at rolling returns:
#
# * The cumulative return for TQQQ is *less* than that of QQQ - which is starkly different from the plot beginning in 2010 at the inception of TQQQ. So the return path really matters here.
# * The drawdown for TQQQ is nearly 100%... which also represents nearly a total loss of capital for any allocation to the extrap-TQQQ. Furthermore, as we walk forward through time (2002, 2003, ... etc.), there is really no reason to believe that the returns would ever recover (even partially). So while we can look at the rolling returns and see how they compare to the 3x return of QQQ, we should keep in mind that the drawdown post-1999 is so severe that it would be very difficult for any investor to hold through it.
# * The recovery time for QQQ was more than 5,000 days, or ~14 years. Note that this is calendar days, not trading days. While returns have been great for QQQ since 2016, the 14 year dry spell is a reminder of just how large the tech bubble was.
# * The extrapolated TQQQ data remains in a drawdown and has never recovered to make new highs (as of March 2026).
#
# ### Plot Rolling Returns (QQQ & TQQQ)
#
# Next, we will consider the following:
#
# * Histogram and scatter plots of the rolling returns of QQQ and TQQQ
# * Regressions to establish a "leverage factor" for the rolling returns
# * The deviation from a 3x return for each time period
#
# For this set of regressions, we will also allow the constant. First, we need the rolling returns for various time periods:
#

# %%
# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        qqq_tqqq_extrap[f"{etf}_Rolling_Return_{period_name}"] = (
            qqq_tqqq_extrap[f"{etf}_Close"].pct_change(periods=window)
        )

# %% [markdown]
# This gives us the following series of histograms, scatter plots, and regression model results:

# %%
# Create a dataframe to hold rolling returns stats
rolling_returns_stats = pd.DataFrame()

for period_name, window in rolling_windows.items():
    plot_histogram(
        df=qqq_tqqq_extrap,
        plot_columns=[f"QQQ_Rolling_Return_{period_name}", f"TQQQ_Rolling_Return_{period_name}"],
        title=f"QQQ & TQQQ {period_name} Rolling Returns",
        x_label="Rolling Return",
        x_tick_spacing="Auto",
        x_tick_rotation=30,
        y_label="# Of Datapoints",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    plot_scatter(
        df=qqq_tqqq_extrap,
        x_plot_column=f"QQQ_Rolling_Return_{period_name}",
        y_plot_columns=[f"TQQQ_Rolling_Return_{period_name}"],
        title=f"QQQ & TQQQ {period_name} Rolling Returns",
        x_label="QQQ Rolling Return",
        x_format="Decimal",
        x_format_decimal_places=2,
        x_tick_spacing="Auto",
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="TQQQ Rolling Return",
        y_format="Decimal",
        y_format_decimal_places=2,
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        plot_OLS_regression_line=True,
        OLS_column=f"TQQQ_Rolling_Return_{period_name}",
        plot_Ridge_regression_line=False,
        Ridge_column=None,
        plot_RidgeCV_regression_line=True,
        RidgeCV_column=f"TQQQ_Rolling_Return_{period_name}",
        regression_constant=True,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    # Run OLS regression with statsmodels
    model = run_regression(
        df=qqq_tqqq_extrap,
        x_plot_column=f"QQQ_Rolling_Return_{period_name}",
        y_plot_column=f"TQQQ_Rolling_Return_{period_name}",
        regression_model="OLS-statsmodels",
        regression_constant=True,
    )
    print(model.summary())

    # Add the regression results to the rolling returns stats dataframe
    intercept = model.params.iloc[0]
    intercept_pvalue = model.pvalues.iloc[0]   # p-value for Intercept
    slope = model.params.iloc[1]
    slope_pvalue = model.pvalues.iloc[1]       # p-value for QQQ_Return
    r_squared = model.rsquared

    # Calc skew
    return_ratio = qqq_tqqq_extrap[f'TQQQ_Rolling_Return_{period_name}'] / qqq_tqqq_extrap[f'QQQ_Rolling_Return_{period_name}']
    skew = return_ratio.skew()

    # Calc conditional symmetry
    up_markets = qqq_tqqq_extrap[qqq_tqqq_extrap[f'QQQ_Rolling_Return_{period_name}'] > 0]
    down_markets = qqq_tqqq_extrap[qqq_tqqq_extrap[f'QQQ_Rolling_Return_{period_name}'] <= 0]

    avg_beta_up = (up_markets[f'TQQQ_Rolling_Return_{period_name}'] / up_markets[f'QQQ_Rolling_Return_{period_name}']).mean()
    avg_beta_down = (down_markets[f'TQQQ_Rolling_Return_{period_name}'] / down_markets[f'QQQ_Rolling_Return_{period_name}']).mean()

    asymmetry = avg_beta_up - avg_beta_down

    rolling_returns_slope_int = pd.DataFrame({
        "Period": period_name,
        "Intercept": [intercept],
        # "Intercept_PValue": [intercept_pvalue],
        "Slope": [slope],
        # "Slope_PValue": [slope_pvalue],
        "R_Squared": [r_squared],
        "Return Skew": [skew],
        "Average Upside Beta": [avg_beta_up],
        "Average Downside Beta": [avg_beta_down],
        "Asymmetry": [asymmetry]
    })

    rolling_returns_stats = pd.concat([rolling_returns_stats, rolling_returns_slope_int])

# %% [markdown]
# You're welcome to digest each plot, but here's my observations on the above results:
#
# * 1d: TQQQ tracks QQQ as expected (it's a 3x daily return leveraged ETF after all), with a regression coefficient of 2.96 and an R^2 of 0.997, and we extrapolated half the data with the same coefficient.
# * 1w: Essentially the same as above. A few outliers, but the regression coefficient is still 2.95 with an R^2 of 0.994. We see a slight skew toward the positive in the rolling returns.
# * 1m: The skew toward the positive is more pronounced, and we see more outliers. The regression coefficient has decreased to 2.93 and the R^2 has dropped to 0.98, which is still very high, but we are starting to see some dispersion in the returns.
# * 3m: The skew toward the positive is even more pronounced, and we see even more outliers. The regression coefficient has *increased*, to 2.98 and the R^2 has dropped to 0.96.
# * 6m: The skew toward the positive is very pronounced, and we see a significant number of outliers with pronounced curvanture in the plot. The regression coefficient has increased again, to 3.4 and the R^2 has dropped to 0.92.
# * 1y: At this point, based on the plot and the regression results, we can start to see that the returns of TQQQ are no longer tracking 3x the returns of QQQ as closely as they did in the shorter time periods. The regression coefficient has is now 2.84 and the R^2 has dropped to 0.88.
# * 4y and 5y: We can see that there are periods where the rolling returns of TQQQ are significantly higher *and* lower than 3x the returns of QQQ, which is consistent with the idea of volatility decay.
#
# For 4y, based on the regression results, we see that if the rolling return of QQQ was 0, then we would expect a return of -0.30 for TQQQ.
#
# $$
# r_{TQQQ} = -0.30 + 3.93 \times r_{QQQ} = -0.30 + 3.93 \times 0 = -0.30
# $$
#
# On the other end of the spectrum, if the rolling return of QQQ was 1, then we would expect a return of:
#
# $$
# r_{TQQQ} = -0.30 + 3.93 \times r_{QQQ} = -0.30 + 3.93 \times 1 = 3.63
# $$
#
# In general, the positive skew of the rolling returns of TQQQ relative to QQQ is related to the general postive return performance of QQQ. With sustained positive returns, the leverage effect of TQQQ will amplify those returns, leading to a positive skew. However, during periods of negative returns for QQQ, the leverage effect will also amplify those losses, leading to a negative skew, and to the limit of a cumulative return of -1, or a 100% loss. The overall skewness of the rolling returns will depend on the balance of these positive and negative periods.
#
# ### Rolling Returns Deviation (QQQ & TQQQ)
#
# Next, we will the rolling returns deviation from the expected 3x return for each time period. This will give us a better picture of the volatility decay effect and how it changes over different time horizons.

# %%
rolling_returns_stats["Return_Deviation_From_3x"] = rolling_returns_stats["Slope"] - 3.0
pandas_set_decimal_places(3)
display(rolling_returns_stats.set_index("Period"))

# %%
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Return_Deviation_From_3x"],
    title="TQQQ Deviation from Perfect 3x Leverage by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Deviation from 3x Leverage",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Slope"],
    title="TQQQ Slope by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Slope",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Intercept"],
    title="Intercept by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Intercept",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
display(rolling_returns_stats.set_index("Period"))

# %% [markdown]
# This is very interesting. Up to 1 year, there is minimal difference between the mean TQQQ 1 year rolling return and the hypothetical 3x leverage, with an R^2 of greater than 0.9.
#
# However, as we extend the time period, we see that
#
# * The "leverage factor" increases significantly, resulting in a deviation from the perfect 3x leverage.
# * The intercept also begins to deviate significantly from 0.
#
# The above highlight the impact of volatility magnification over longer time horizons. This phenomenon is happening likely due to the positive returns that QQQ has achieved since 2010 - resulting in TQQQ compounding at a much higher rate than 3x - but it may and likely is not exhibited by other 3x leveraged ETFs that have not had the same positive return profile as QQQ.
#
# With the above results, the next logical question is, when is the opportune time to buy a 3x leveraged ETF like TQQQ? To answer this, we will look a the drawdown levels of TQQQ and the subsequent returns over various time horizons.
#
# ### Rolling Returns Following Drawdowns (QQQ & TQQQ)
#
# We will identify the drawdown levels of TQQQ and then look at the subsequent rolling returns over various time horizons.

# %%
# Copy DataFrame
qqq_tqqq_extrap_future = qqq_tqqq_extrap.copy()

# Create a list of drawdown levels to analyze
drawdown_levels = [-0.10, -0.20, -0.30, -0.40, -0.50, -0.60, -0.70, -0.80, -0.90]

# Shift the rolling return columns by the number of days in the rolling window to get the returns following the drawdown
for etf in etfs:
    for period_name, window in rolling_windows.items():
        qqq_tqqq_extrap_future[f"{etf}_Rolling_Future_Return_{period_name}"] = qqq_tqqq_extrap_future[f"{etf}_Rolling_Return_{period_name}"].shift(-window)

# %% [markdown]
# Now, we can analyze the future rolling returns following specific drawdown levels:

# %%
# Create a dataframe to hold rolling returns stats
rolling_returns_drawdown_stats = pd.DataFrame()

for drawdown in drawdown_levels:

    for period_name, window in rolling_windows.items():

        try:
            plot_histogram(
                df=qqq_tqqq_extrap_future[qqq_tqqq_extrap_future["TQQQ_Drawdown"] <= drawdown],
                plot_columns=[f"QQQ_Rolling_Future_Return_{period_name}", f"TQQQ_Rolling_Future_Return_{period_name}"],
                title=f"QQQ & TQQQ {period_name} Rolling Future Returns Post {drawdown} TQQQ Drawdown",
                x_label="Rolling Return",
                x_tick_spacing="Auto",
                x_tick_rotation=30,
                y_label="# Of Datapoints",
                y_tick_spacing="Auto",
                y_tick_rotation=0,
                grid=True,
                legend=True,
                export_plot=False,
                plot_file_name=None,
            )

            plot_scatter(
                df=qqq_tqqq_extrap_future[qqq_tqqq_extrap_future["TQQQ_Drawdown"] <= drawdown],
                x_plot_column=f"QQQ_Rolling_Future_Return_{period_name}",
                y_plot_columns=[f"TQQQ_Rolling_Future_Return_{period_name}"],
                title=f"QQQ & TQQQ {period_name} Rolling Future Returns Post {drawdown} TQQQ Drawdown",
                x_label="QQQ Rolling Return",
                x_format="Decimal",
                x_format_decimal_places=2,
                x_tick_spacing="Auto",
                x_tick_start=None,
                x_tick_rotation=30,
                y_label="TQQQ Rolling Return",
                y_format="Decimal",
                y_format_decimal_places=2,
                y_tick_spacing="Auto",
                y_tick_rotation=0,
                plot_OLS_regression_line=True,
                OLS_column=f"TQQQ_Rolling_Future_Return_{period_name}",
                plot_Ridge_regression_line=False,
                Ridge_column=None,
                plot_RidgeCV_regression_line=True,
                RidgeCV_column=f"TQQQ_Rolling_Future_Return_{period_name}",
                regression_constant=True,
                grid=True,
                legend=True,
                export_plot=False,
                plot_file_name=None,
            )

            # Run OLS regression with statsmodels
            model = run_regression(
                df=qqq_tqqq_extrap_future[qqq_tqqq_extrap_future["TQQQ_Drawdown"] <= drawdown],
                x_plot_column=f"QQQ_Rolling_Future_Return_{period_name}",
                y_plot_column=f"TQQQ_Rolling_Future_Return_{period_name}",
                regression_model="OLS-statsmodels",
                regression_constant=True,
            )
            print(model.summary())

            # Filter by drawdown
            drawdown_filter = qqq_tqqq_extrap_future[qqq_tqqq_extrap_future["TQQQ_Drawdown"] <= drawdown]

            # Filter by period, drop rows with missing values
            future_filter = drawdown_filter[[f"TQQQ_Rolling_Future_Return_{period_name}"]].dropna()

            # Find length of future dataframe
            future_length = len(future_filter)

            # Find length of future dataframe where return is positive
            positive_future_length = len(future_filter[future_filter[f"TQQQ_Rolling_Future_Return_{period_name}"] > 0])

            # Calculate percentage of future returns that are positive
            positive_future_percentage = (positive_future_length / future_length) if future_length > 0 else 0

            # Add the regression results to the rolling returns stats dataframe
            intercept = model.params.iloc[0]
            # intercept_pvalue = model.pvalues.iloc[0]   # p-value for Intercept
            slope = model.params.iloc[1]
            # slope_pvalue = model.pvalues.iloc[1]       # p-value for Slope
            r_squared = model.rsquared

            rolling_returns_slope_int = pd.DataFrame({
                "Drawdown": drawdown,
                "Period": period_name,
                "Intercept": [intercept],
                # "Intercept_PValue": [intercept_pvalue],
                "Slope": [slope],
                # "Slope_PValue": [slope_pvalue],
                "R_Squared": [r_squared],
                "Positive_Future_Percentage": [positive_future_percentage],
            })
            
            rolling_returns_drawdown_stats = pd.concat([rolling_returns_drawdown_stats, rolling_returns_slope_int])

        except:
            print(f"Not enough data points for drawdown level {drawdown} and period {period_name} to run regression.")

# %% [markdown]
# ### Rolling Returns Following Drawdowns Deviation (QQQ & TQQQ)

# %%
rolling_returns_positive_future_returns = pd.DataFrame(index=rolling_windows.keys(), data=rolling_windows.values())
rolling_returns_positive_future_returns.reset_index(inplace=True)
rolling_returns_positive_future_returns.rename(columns={"index":"Period", 0:"Days"}, inplace=True)

for drawdown in drawdown_levels:
    temp = rolling_returns_drawdown_stats.loc[rolling_returns_drawdown_stats["Drawdown"] == drawdown]
    temp = temp[["Period", "Positive_Future_Percentage"]]
    temp.rename(columns={"Positive_Future_Percentage" : f"Positive_Future_Percentage_Post_{drawdown}_Drawdown"}, inplace=True)
    rolling_returns_positive_future_returns = pd.merge(rolling_returns_positive_future_returns, temp, left_on="Period", right_on="Period", how="outer")
    rolling_returns_positive_future_returns.sort_values(by="Days", ascending=True, inplace=True)

rolling_returns_positive_future_returns.drop(columns={"Days"}, inplace=True)
rolling_returns_positive_future_returns.reset_index(drop=True, inplace=True)
pandas_set_decimal_places(2)
display(rolling_returns_positive_future_returns.set_index("Period"))

# %%
plot_scatter(
    df=rolling_returns_positive_future_returns,
    x_plot_column="Period",
    y_plot_columns=[col for col in rolling_returns_positive_future_returns.columns if col != "Period"],
    title="TQQQ Future Return by Time Period Post Drawdown",
    x_label="Rolling Return Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Positive Future Return Percentage",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# This plot summarizes the future rolling returns well. For rolling returns up to ~3 months *following* all drawdown levels, we see the rolling returns of TQQQ are positive ~65% of the time.
#
# As we extend the time horizon, the percentage of positive rolling returns increases, which is consistent with the idea that the longer you hold through and post drawdown, the more likely you are to recover and achieve positive returns.
#
# From a timing standpoint, this analysis suggests that the optimal time to buy TQQQ would be following a drawdown of 70% or more, and holding for at least 3 years. The data tells us that having a positive rolling return over time is ~75%.
#
# One might consider the idea of allocating to TQQQ via a ladder, starting at a drawdown of 50%, and continuing to add to the position as the drawdown deepens, with the idea that the more severe the drawdown, the higher the expected future returns. However, this strategy could require enduring significant volatility, as one would be adding to the position during periods of paper losses.
#
# ## SPY & UPRO
#
# Next, we will repeat the same analysis for SPY and UPRO, and see how the results compare to those of QQQ and TQQQ.
#
# ### Acquire & Plot Data (SPY)
#
# First, let's get the data for SPY. If we already have the desired data, we can load it from a local pickle file. Otherwise, we can download it from Yahoo Finance using the `yf_pull_data` function.

# %%
pandas_set_decimal_places(2)

yf_pull_data(
    base_directory=DATA_DIR,
    ticker="SPY",
    adjusted=False,
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

spy = load_data(
    base_directory=DATA_DIR,
    ticker="SPY",
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "SPY_Close", etc.
spy = spy.rename(columns={
    "Adj Close": "SPY_Adj_Close",
    "Close": "SPY_Close",
    "High": "SPY_High",
    "Low": "SPY_Low",
    "Open": "SPY_Open",
    "Volume": "SPY_Volume"
})

display(spy)

# %% [markdown]
# And the plot of the time series of partially adjusted close prices:

# %%
plot_time_series(
    df=spy,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Adj_Close"],
    title="SPY Adjusted Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# ### Acquire & Plot Data (UPRO)
#
# Next, UPRO:

# %%
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="UPRO",
    adjusted=False,
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)
    
upro = load_data(
    base_directory=DATA_DIR,
    ticker="UPRO",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "UPRO_Close", etc.
upro = upro.rename(columns={
    "Adj Close": "UPRO_Adj_Close",
    "Close": "UPRO_Close", 
    "High": "UPRO_High", 
    "Low": "UPRO_Low", 
    "Open": "UPRO_Open", 
    "Volume": "UPRO_Volume"
})

display(upro)

# %% [markdown]
# And the plot of the time series of partially adjusted close prices:

# %%
plot_time_series(
    df=upro,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["UPRO_Adj_Close"],
    title="UPRO Adjusted Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# Looking at the close prices doesn't give us a true picture of the magnitude of the difference in returns due to the leverage. In order to see that, we need to look at the cumulative returns and the drawdowns.
#
#  ### Calculate & Plot Cumulative Returns, Rolling Returns, and Drawdowns (SPY & UPRO)
#
#  Next, we will calculate the cumulative returns, rolling returns, and drawdowns. This involves aligning the data to start with the inception of UPRO. For this excercise, we will not extrapolate the data for SPY back to 1993, but rather just align the data from the inception of UPRO in 2009.

# %%
etfs = ["SPY", "UPRO"]

# Merge dataframes and drop rows with missing values
spy_upro_aligned = upro.merge(spy, left_index=True, right_index=True, how='left')
spy_upro_aligned = spy_upro_aligned.dropna()

# Calculate cumulative returns
for etf in etfs:
    spy_upro_aligned[f"{etf}_Return"] = spy_upro_aligned[f"{etf}_Close"].pct_change()
    spy_upro_aligned[f"{etf}_Cumulative_Return"] = (1 + spy_upro_aligned[f"{etf}_Return"]).cumprod() - 1
    spy_upro_aligned[f"{etf}_Cumulative_Return_Plus_One"] = 1 + spy_upro_aligned[f"{etf}_Cumulative_Return"]
    spy_upro_aligned[f"{etf}_Rolling_Max"] = spy_upro_aligned[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    spy_upro_aligned[f"{etf}_Drawdown"] = spy_upro_aligned[f"{etf}_Cumulative_Return_Plus_One"] / spy_upro_aligned[f"{etf}_Rolling_Max"] - 1
    spy_upro_aligned.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)

# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        spy_upro_aligned[f"{etf}_Rolling_Return_{period_name}"] = (
            spy_upro_aligned[f"{etf}_Close"].pct_change(periods=window)
        )
        
display(spy_upro_aligned)

# %% [markdown]
# And now the plot for the cumulative returns:

# %%
plot_time_series(
    df=spy_upro_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Cumulative_Return", "UPRO_Cumulative_Return"],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# And the drawdown plot:

# %%
plot_time_series(
    df=spy_upro_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Drawdown", "UPRO_Drawdown"],
    title="Drawdowns",
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
)

# %% [markdown]
# ### Summary Statistics (SPY & UPRO)
#
# Looking at the summary statistics further confirms our intuitions about the volatility and drawdowns.

# %%
spy_sum_stats = summary_stats(
    fund_list=["SPY"],
    df=spy_upro_aligned[["SPY_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

upro_sum_stats = summary_stats(
    fund_list=["UPRO"],
    df=spy_upro_aligned[["UPRO_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([spy_sum_stats, upro_sum_stats])

display(sum_stats)

# %% [markdown]
# ### Plot Returns & Verify Beta (SPY & UPRO)
#
# Before we look at the rolling returns, let us first verify that the daily returns for UPRO are in fact ~3x those of SPY.

# %%
plot_scatter(
    df=spy_upro_aligned,
    x_plot_column="SPY_Return",
    y_plot_columns=["UPRO_Return"],
    title="SPY & UPRO Returns",
    x_label="SPY Return",
    x_format="Decimal",
    x_format_decimal_places=2,
    x_tick_spacing="Auto",
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="UPRO Return",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=True,
    OLS_column="UPRO_Return",
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=True,
    RidgeCV_column="UPRO_Return",
    regression_constant=True,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
model = run_regression(
    df=spy_upro_aligned,
    x_plot_column="SPY_Return",
    y_plot_column="UPRO_Return",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)

print(model.summary())

# %% [markdown]
# Similar to QQQ/TQQQ, this plot makes sense and we can see that there is a strong clustering of points, but we double check with the regression, regressing the UPRO daily return (y) on the SPY daily return (X).
#
# ### Extrapolate Data (SPY & UPRO)
#
# We will now extrapolate the returns of SPY to backfill the data from the inception of SPY in 1993 to the inception of UPRO in 2009. For this, we'll use the coefficient of 2.98 that we found in the regression results above.

# %%
# Set leverage multiplier based on regression coefficient
LEVERAGE_MULTIPLIER = model.params.iloc[1]

# Merge dataframes and extrapolate return values for SPY back to 1993 using the leverage multiplier
spy_upro_extrap = spy[["SPY_Close"]].merge(upro[["UPRO_Close"]], left_index=True, right_index=True, how='left')

etfs = ["SPY", "UPRO"]

# Calculate cumulative returns
for etf in etfs:
    spy_upro_extrap[f"{etf}_Return"] = spy_upro_extrap[f"{etf}_Close"].pct_change()

# Extrapolate UPRO returns for missing values
spy_upro_extrap["UPRO_Return"] = spy_upro_extrap["UPRO_Return"].fillna(LEVERAGE_MULTIPLIER * spy_upro_extrap["SPY_Return"])

# Find the first valid UPRO_Close index and value
first_valid_idx = spy_upro_extrap['UPRO_Close'].first_valid_index()
print(first_valid_idx)
first_valid_price = spy_upro_extrap.loc[first_valid_idx, 'UPRO_Close']
print(first_valid_price)

# %% [markdown]
# Before we extrapolate, let's first look at the data we have for SPY and UPRO around the inception of UPRO in 2009:

# %%
# Check values around the first valid index
pandas_set_decimal_places(4)
display(spy_upro_extrap.loc["2009-06-20":"2009-06-30"])

# %% [markdown]
# Now, backfill the data for the UPRO close price:

# %%
# Iterate through the dataframe backwards
for i in range(spy_upro_extrap.index.get_loc(first_valid_idx) - 1, -1, -1):
    
    # The return that led to the price the next day
    current_return = spy_upro_extrap.iloc[i + 1]['UPRO_Return']

    # Get the next day's price
    next_price = spy_upro_extrap.iloc[i + 1]['UPRO_Close']
    
    # Price_{t} = Price_{t+1} / (1 + Return_{t})
    spy_upro_extrap.loc[spy_upro_extrap.index[i], 'UPRO_Close'] = next_price / (1 + current_return)

# %% [markdown]
# Finally, confirm the values are correct:

# %%
# Confirm values around the first valid index after extrapolation
display(spy_upro_extrap.loc["2009-06-20":"2009-06-30"])

# %% [markdown]
# And the complete DataFrame with the extrapolated values:

# %%
pandas_set_decimal_places(2)
display(spy_upro_extrap)

# %% [markdown]
# After the extrapolation, we now have the following plots for the prices, cumulative returns, and drawdowns:

# %%
etfs = ["SPY", "UPRO"]

# Calculate cumulative returns
for etf in etfs:
    spy_upro_extrap[f"{etf}_Return"] = spy_upro_extrap[f"{etf}_Close"].pct_change()
    spy_upro_extrap[f"{etf}_Cumulative_Return"] = (1 + spy_upro_extrap[f"{etf}_Return"]).cumprod() - 1
    spy_upro_extrap[f"{etf}_Cumulative_Return_Plus_One"] = 1 + spy_upro_extrap[f"{etf}_Cumulative_Return"]
    spy_upro_extrap[f"{etf}_Rolling_Max"] = spy_upro_extrap[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    spy_upro_extrap[f"{etf}_Drawdown"] = spy_upro_extrap[f"{etf}_Cumulative_Return_Plus_One"] / spy_upro_extrap[f"{etf}_Rolling_Max"] - 1
    spy_upro_extrap.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)

# %%
plot_time_series(
    df=spy_upro_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Close"],
    title="SPY Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_time_series(
    df=spy_upro_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["UPRO_Close"],
    title="UPRO Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_time_series(
    df=spy_upro_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Cumulative_Return", "UPRO_Cumulative_Return"],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_time_series(
    df=spy_upro_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Drawdown", "UPRO_Drawdown"],
    title="Drawdowns",
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
)

# %%
spy_extrap_sum_stats = summary_stats(
    fund_list=["SPY"],
    df=spy_upro_extrap[["SPY_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

upro_extrap_sum_stats = summary_stats(
    fund_list=["UPRO"],
    df=spy_upro_extrap[["UPRO_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([spy_sum_stats, upro_sum_stats, spy_extrap_sum_stats, upro_extrap_sum_stats])
sum_stats.index = ["SPY (2009 - Present)", "UPRO (2009 - Present)", "SPY (1993 - Present)", "UPRO Extrapolated (1993 - Present)"]

display(sum_stats)

# %% [markdown]
# Interestingly, the maximum drawdown for UPRO is not as severe as that of TQQQ, which may be due to that SPY has not had the same extreme return profile as QQQ. This highlights the importance of the underlying asset's return profile on the performance of leveraged ETFs.
#
# ### Plot Rolling Returns (SPY & UPRO)
#
# Next, we will consider the following:
#
# * Histogram and scatter plots of the rolling returns of SPY and UPRO
# * Regressions to establish a "leverage factor" for the rolling returns
# * The deviation from a 3x return for each time period
#
# For this set of regressions, we will also allow the constant. First, we need the rolling returns for various time periods:
#

# %%
# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        spy_upro_extrap[f"{etf}_Rolling_Return_{period_name}"] = (
            spy_upro_extrap[f"{etf}_Close"].pct_change(periods=window)
        )

# %% [markdown]
# This gives us the following series of histograms, scatter plots, and regression model results:

# %%
# Create a dataframe to hold rolling returns stats
rolling_returns_stats = pd.DataFrame()

for period_name, window in rolling_windows.items():
    plot_histogram(
        df=spy_upro_extrap,
        plot_columns=[f"SPY_Rolling_Return_{period_name}", f"UPRO_Rolling_Return_{period_name}"],
        title=f"SPY & UPRO {period_name} Rolling Returns",
        x_label="Rolling Return",
        x_tick_spacing="Auto",
        x_tick_rotation=30,
        y_label="# Of Datapoints",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    plot_scatter(
        df=spy_upro_extrap,
        x_plot_column=f"SPY_Rolling_Return_{period_name}",
        y_plot_columns=[f"UPRO_Rolling_Return_{period_name}"],
        title=f"SPY & UPRO {period_name} Rolling Returns",
        x_label="SPY Rolling Return",
        x_format="Decimal",
        x_format_decimal_places=2,
        x_tick_spacing="Auto",
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="UPRO Rolling Return",
        y_format="Decimal",
        y_format_decimal_places=2,
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        plot_OLS_regression_line=True,
        OLS_column=f"UPRO_Rolling_Return_{period_name}",
        plot_Ridge_regression_line=False,
        Ridge_column=None,
        plot_RidgeCV_regression_line=True,
        RidgeCV_column=f"UPRO_Rolling_Return_{period_name}",
        regression_constant=True,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    # Run OLS regression with statsmodels
    model = run_regression(
        df=spy_upro_extrap,
        x_plot_column=f"SPY_Rolling_Return_{period_name}",
        y_plot_column=f"UPRO_Rolling_Return_{period_name}",
        regression_model="OLS-statsmodels",
        regression_constant=True,
    )
    print(model.summary())

    # Add the regression results to the rolling returns stats dataframe
    intercept = model.params.iloc[0]
    intercept_pvalue = model.pvalues.iloc[0]   # p-value for Intercept
    slope = model.params.iloc[1]
    slope_pvalue = model.pvalues.iloc[1]       # p-value for SPY_Return
    r_squared = model.rsquared

    # Calc skew
    return_ratio = spy_upro_extrap[f'UPRO_Rolling_Return_{period_name}'] / spy_upro_extrap[f'SPY_Rolling_Return_{period_name}']
    skew = return_ratio.skew()

    # Calc conditional symmetry
    up_markets = spy_upro_extrap[spy_upro_extrap[f'SPY_Rolling_Return_{period_name}'] > 0]
    down_markets = spy_upro_extrap[spy_upro_extrap[f'SPY_Rolling_Return_{period_name}'] <= 0]

    avg_beta_up = (up_markets[f'UPRO_Rolling_Return_{period_name}'] / up_markets[f'SPY_Rolling_Return_{period_name}']).mean()
    avg_beta_down = (down_markets[f'UPRO_Rolling_Return_{period_name}'] / down_markets[f'SPY_Rolling_Return_{period_name}']).mean()

    asymmetry = avg_beta_up - avg_beta_down

    rolling_returns_slope_int = pd.DataFrame({
        "Period": period_name,
        "Intercept": [intercept],
        # "Intercept_PValue": [intercept_pvalue],
        "Slope": [slope],
        # "Slope_PValue": [slope_pvalue],
        "R_Squared": [r_squared],
        "Skew": [skew],
        "Average Upside Beta": [avg_beta_up],
        "Average Downside Beta": [avg_beta_down],
        "Asymmetry": [asymmetry]
    })

    rolling_returns_stats = pd.concat([rolling_returns_stats, rolling_returns_slope_int])

# %% [markdown]
# ### Rolling Returns Deviation (SPY & UPRO)
#
# Next, we will the rolling returns deviation from the expected 3x return for each time period. This will give us a better picture of the volatility decay effect and how it changes over different time horizons.

# %%
rolling_returns_stats["Return_Deviation_From_3x"] = rolling_returns_stats["Slope"] - 3.0
pandas_set_decimal_places(3)
display(rolling_returns_stats.set_index("Period"))

# %%
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Return_Deviation_From_3x"],
    title="UPRO Deviation from Perfect 3x Leverage by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Deviation from 3x Leverage",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Slope"],
    title="UPRO Slope by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Slope",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Intercept"],
    title="Intercept by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Intercept",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %%
display(rolling_returns_stats.set_index("Period"))

# %% [markdown]
# Similar as to QQQ/TQQQ, up to 1 year, there is minimal difference between the mean UPRO 1 year rolling return and the hypothetical 3x leverage, with an R^2 of greater than 0.9.
#
# However, as we extend the time period, we see that
#
# * The "leverage factor" increases significantly, resulting in a deviation from the perfect 3x leverage.
# * The intercept also begins to deviate significantly from 0.
#
# ### Rolling Returns Following Drawdowns (SPY & UPRO)
#
# We will identify the drawdown levels of UPRO and then look at the subsequent rolling returns over various time horizons.

# %%
# Copy DataFrame
spy_upro_extrap_future = spy_upro_extrap.copy()

# Create a list of drawdown levels to analyze
drawdown_levels = [-0.10, -0.20, -0.30, -0.40, -0.50, -0.60, -0.70, -0.80, -0.90]

# Shift the rolling return columns by the number of days in the rolling window to get the returns following the drawdown
for etf in etfs:
    for period_name, window in rolling_windows.items():
        spy_upro_extrap_future[f"{etf}_Rolling_Future_Return_{period_name}"] = spy_upro_extrap_future[f"{etf}_Rolling_Return_{period_name}"].shift(-window)

# %% [markdown]
# Now, we can analyze the future rolling returns following specific drawdown levels:

# %%
# Create a dataframe to hold rolling returns stats
rolling_returns_drawdown_stats = pd.DataFrame()

for drawdown in drawdown_levels:

    for period_name, window in rolling_windows.items():

        try:
            plot_histogram(
                df=spy_upro_extrap_future[spy_upro_extrap_future["UPRO_Drawdown"] <= drawdown],
                plot_columns=[f"SPY_Rolling_Future_Return_{period_name}", f"UPRO_Rolling_Future_Return_{period_name}"],
                title=f"SPY & UPRO {period_name} Rolling Future Returns Post {drawdown} UPRO Drawdown",
                x_label="Rolling Return",
                x_tick_spacing="Auto",
                x_tick_rotation=30,
                y_label="# Of Datapoints",
                y_tick_spacing="Auto",
                y_tick_rotation=0,
                grid=True,
                legend=True,
                export_plot=False,
                plot_file_name=None,
            )

            plot_scatter(
                df=spy_upro_extrap_future[spy_upro_extrap_future["UPRO_Drawdown"] <= drawdown],
                x_plot_column=f"SPY_Rolling_Future_Return_{period_name}",
                y_plot_columns=[f"UPRO_Rolling_Future_Return_{period_name}"],
                title=f"SPY & UPRO {period_name} Rolling Future Returns Post {drawdown} UPRO Drawdown",
                x_label="SPY Rolling Return",
                x_format="Decimal",
                x_format_decimal_places=2,
                x_tick_spacing="Auto",
                x_tick_start=None,
                x_tick_rotation=30,
                y_label="UPRO Rolling Return",
                y_format="Decimal",
                y_format_decimal_places=2,
                y_tick_spacing="Auto",
                y_tick_rotation=0,
                plot_OLS_regression_line=True,
                OLS_column=f"UPRO_Rolling_Future_Return_{period_name}",
                plot_Ridge_regression_line=False,
                Ridge_column=None,
                plot_RidgeCV_regression_line=True,
                RidgeCV_column=f"UPRO_Rolling_Future_Return_{period_name}",
                regression_constant=True,
                grid=True,
                legend=True,
                export_plot=False,
                plot_file_name=None,
            )

            # Run OLS regression with statsmodels
            model = run_regression(
                df=spy_upro_extrap_future[spy_upro_extrap_future["UPRO_Drawdown"] <= drawdown],
                x_plot_column=f"SPY_Rolling_Future_Return_{period_name}",
                y_plot_column=f"UPRO_Rolling_Future_Return_{period_name}",
                regression_model="OLS-statsmodels",
                regression_constant=True,
            )
            print(model.summary())

            # Filter by drawdown
            drawdown_filter = spy_upro_extrap_future[spy_upro_extrap_future["UPRO_Drawdown"] <= drawdown]

            # Filter by period, drop rows with missing values
            future_filter = drawdown_filter[[f"UPRO_Rolling_Future_Return_{period_name}"]].dropna()

            # Find length of future dataframe
            future_length = len(future_filter)

            # Find length of future dataframe where return is positive
            positive_future_length = len(future_filter[future_filter[f"UPRO_Rolling_Future_Return_{period_name}"] > 0])

            # Calculate percentage of future returns that are positive
            positive_future_percentage = (positive_future_length / future_length) if future_length > 0 else 0

            # Add the regression results to the rolling returns stats dataframe
            intercept = model.params.iloc[0]
            # intercept_pvalue = model.pvalues.iloc[0]   # p-value for Intercept
            slope = model.params.iloc[1]
            # slope_pvalue = model.pvalues.iloc[1]       # p-value for Slope
            r_squared = model.rsquared

            rolling_returns_slope_int = pd.DataFrame({
                "Drawdown": drawdown,
                "Period": period_name,
                "Intercept": [intercept],
                # "Intercept_PValue": [intercept_pvalue],
                "Slope": [slope],
                # "Slope_PValue": [slope_pvalue],
                "R_Squared": [r_squared],
                "Positive_Future_Percentage": [positive_future_percentage],
            })
            
            rolling_returns_drawdown_stats = pd.concat([rolling_returns_drawdown_stats, rolling_returns_slope_int])

        except:
            print(f"Not enough data points for drawdown level {drawdown} and period {period_name} to run regression.")

# %% [markdown]
# ### Rolling Returns Following Drawdowns Deviation (SPY & UPRO)

# %%
rolling_returns_positive_future_returns = pd.DataFrame(index=rolling_windows.keys(), data=rolling_windows.values())
rolling_returns_positive_future_returns.reset_index(inplace=True)
rolling_returns_positive_future_returns.rename(columns={"index":"Period", 0:"Days"}, inplace=True)

for drawdown in drawdown_levels:
    temp = rolling_returns_drawdown_stats.loc[rolling_returns_drawdown_stats["Drawdown"] == drawdown]
    temp = temp[["Period", "Positive_Future_Percentage"]]
    temp.rename(columns={"Positive_Future_Percentage" : f"Positive_Future_Percentage_Post_{drawdown}_Drawdown"}, inplace=True)
    rolling_returns_positive_future_returns = pd.merge(rolling_returns_positive_future_returns, temp, left_on="Period", right_on="Period", how="outer")
    rolling_returns_positive_future_returns.sort_values(by="Days", ascending=True, inplace=True)

rolling_returns_positive_future_returns.drop(columns={"Days"}, inplace=True)
rolling_returns_positive_future_returns.reset_index(drop=True, inplace=True)
pandas_set_decimal_places(2)
display(rolling_returns_positive_future_returns.set_index("Period"))

# %%
plot_scatter(
    df=rolling_returns_positive_future_returns,
    x_plot_column="Period",
    y_plot_columns=[col for col in rolling_returns_positive_future_returns.columns if col != "Period"],
    title="UPRO Future Return by Time Period Post Drawdown",
    x_label="Rolling Return Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Positive Future Return Percentage",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# This plot summarizes the future rolling returns well. Similar as to QQQ/TQQQ, for rolling returns up to ~3 months *following* all drawdown levels, we see the rolling returns of UPRO are positive ~65% of the time.
#
# As we extend the time horizon, out to the 2y, 3y, 4y, and 5y mark, the percentage of positive rolling returns following an 80% drawdown increases significantly, and is greater than *95%*. This suggests that while the volatility decay effect is present for UPRO, it may not be as severe as that of TQQQ, which could be due to the less extreme return profile of SPY compared to QQQ.
#
# As an investor, this suggests that the optimal time to buy UPRO would be following a drawdown of 50% or more, and holding for at least 2 years. One could dollar cost average into UPRO following a drawdown of 50% or more, and continue to add to the position with a consistent contribution schedule until all capital has been allocated.
#
# ## Future Investigation
#
# There are a couple of ideas for future investigation that would be interesting to explore:
#
# * Expand the analysis of SPY/UPRO to SPX/UPRO (using Bloomberg data for SPX), and extrapolate UPRO return data back to January of 1975.
# * Implement and backtest a strategy that DCA's into UPRO on a consistent schdule (monthly, quarterly, etc.)

# %% [markdown]
#
