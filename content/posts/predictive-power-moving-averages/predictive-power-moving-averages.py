# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
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

# %% [markdown]
# The idea of time series momentum (AKA, trend following) heavily relies on the idea that, for an asset experiencing upward momentum, if the price at time t is higher than the price at time t-x, then the price at time t+y is likely to be higher than the price at time t.
#
# In this post, we will investigate the idea of moving averages, and whether if the price at time t is higher or lower than the moving average up until time t (for several different lookback periods) has any predictive power for forward returns (for several different horizons). 

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

# %% [markdown]
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

# %% [markdown]
# For this exercise, we will investigate the predictive power of moving averages for the following ETFs:
#
# * IVV - iShares Core S&P 500 ETF
# * EFA - iShares MSCI EAFE ETF
# * EEM - iShares MSCI Emerging Markets ETF
# * GSG - iShares S&P GSCI Commodity-Indexed Trust
# * IAU - iShares Gold Trust
# * IEF - iShares 7-10 Year Treasury Bond ETF
# * TLT - iShares 20+ Year Treasury Bond ETF
#
# We'll use the adjusted close prices for each of these ETFs.

# %% [markdown]
# ## Acquire Data

# %% [markdown]
# First, let's get the data for these ETFs. If we already have the desired data, we can load it from a local pickle file. Otherwise, we can download it from Yahoo Finance using the `yf_pull_data` function.

# %%
pandas_set_decimal_places(2)

# Create a list of the ETF tickers
fund_list = ["IVV", "EFA", "EEM", "GSG", "IAU", "IEF", "TLT"]

# %%
# Pull data for each ETF and cache it locally
for fund in fund_list:
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        adjusted=False,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=False,
    )

# %% [markdown]
# ## Create Data Dictionary

# %% [markdown]
# Then, create a dictionary to hold the data for each ETF, and plot the adjusted close price for each ETF over time.

# %%
# Create an empty dictionary to hold the data for each ETF
fund_data = {}

# Load the data for each ETF, rename the columns to include the ticker, store it in the fund_data dictionary
for fund in fund_list:
    data = load_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        timeframe="Daily",
        file_format="pickle",
    )

    data = data.rename(columns={
        "Adj Close": f"{fund}_Adj_Close",
        "Close": f"{fund}_Close",
        "High": f"{fund}_High",
        "Low": f"{fund}_Low",
        "Open": f"{fund}_Open",
        "Volume": f"{fund}_Volume"
    })
    
    fund_data[fund] = data

# %% [markdown]
# ## Plot Data

# %% [markdown]
# Next, we will:
#
# * Check the date ranges
# * Plot the adjusted close prices
# * Plot the cumulative returns
# * Plot the drawdowns

# %%
for fund, data in fund_data.items():    
    display(data)

    plot_time_series(
        df=data,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[f"{fund}_Adj_Close"],
        title=f"{fund} Adjusted Close Price",
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
# Create empty DF
data_merged = pd.DataFrame()

# Merge all data, calc cumulative returns, drawdowns
for fund, data in fund_data.items():
    data_merged = data_merged.merge(data[[f"{fund}_Adj_Close"]], left_index=True, right_index=True, how='outer') if not data_merged.empty else data[[f"{fund}_Adj_Close"]]
    data_merged[f"{fund}_Return"] = data_merged[f"{fund}_Adj_Close"].pct_change()
    data_merged[f"{fund}_Cumulative_Return"] = (1 + data_merged[f"{fund}_Return"]).cumprod() - 1
    data_merged[f"{fund}_Cumulative_Return_Plus_One"] = 1 + data_merged[f"{fund}_Cumulative_Return"]
    data_merged[f"{fund}_Rolling_Max"] = data_merged[f"{fund}_Cumulative_Return_Plus_One"].cummax()
    data_merged[f"{fund}_Drawdown"] = data_merged[f"{fund}_Cumulative_Return_Plus_One"] / data_merged[f"{fund}_Rolling_Max"] - 1
    data_merged.drop(columns=[f"{fund}_Cumulative_Return_Plus_One", f"{fund}_Rolling_Max"], inplace=True)
        
display(data_merged)

# %% [markdown]
# And now the plots for the cumulative returns and drawdowns:

# %%
plot_time_series(
    df=data_merged,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[col for col in data_merged.columns if "Cumulative_Return" in col],
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

plot_time_series(
    df=data_merged,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[col for col in data_merged.columns if "Drawdown" in col],
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
# This time we'll drop the empty rows to give a more accurate comparison, but this will reduce our data set to the inception of GSG in 2006:

# %%
# Create empty DF
data_merged_aligned = pd.DataFrame()

# Merge all data, calc cumulative returns, drawdowns
for fund, data in fund_data.items():
    data_merged_aligned = data_merged_aligned.merge(data[[f"{fund}_Adj_Close"]], left_index=True, right_index=True, how='outer') if not data_merged_aligned.empty else data[[f"{fund}_Adj_Close"]]
    data_merged_aligned = data_merged_aligned.dropna()

for fund in fund_data.keys():
    data_merged_aligned[f"{fund}_Return"] = data_merged_aligned[f"{fund}_Adj_Close"].pct_change()
    data_merged_aligned[f"{fund}_Cumulative_Return"] = (1 + data_merged_aligned[f"{fund}_Return"]).cumprod() - 1
    data_merged_aligned[f"{fund}_Cumulative_Return_Plus_One"] = 1 + data_merged_aligned[f"{fund}_Cumulative_Return"]
    data_merged_aligned[f"{fund}_Rolling_Max"] = data_merged_aligned[f"{fund}_Cumulative_Return_Plus_One"].cummax()
    data_merged_aligned[f"{fund}_Drawdown"] = data_merged_aligned[f"{fund}_Cumulative_Return_Plus_One"] / data_merged_aligned[f"{fund}_Rolling_Max"] - 1
    data_merged_aligned.drop(columns=[f"{fund}_Cumulative_Return_Plus_One", f"{fund}_Rolling_Max"], inplace=True)
        
display(data_merged_aligned)

# %%
plot_time_series(
    df=data_merged_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[col for col in data_merged_aligned.columns if "Cumulative_Return" in col],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

plot_time_series(
    df=data_merged_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[col for col in data_merged_aligned.columns if "Drawdown" in col],
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
# Several things to note here:
#
# * Gold wins! Almost...
# * You lose most of your money investing in commodies...
# * Gold diversified well during the financial crisis
# * The equity funds all had similar drawdowns

# %% [markdown]
# ## Summary Statistics
#
# Let's look at the summary statistics. Keep in mind that we are not aligning the dates here, so the number of observations is different for each ETF.

# %%
sum_stats = pd.DataFrame()

for fund in fund_data.keys():
    data_stats = summary_stats(
        fund_list=[f"{fund}"],
        df=data_merged[[f"{fund}_Return"]].dropna(),
        period="Daily",
        use_calendar_days=False,
        excel_export=False,
        pickle_export=False,
        output_confirmation=False,
    )

    sum_stats = pd.concat([sum_stats, data_stats])

display(sum_stats)

# %% [markdown]
# ## Calculate Moving Averages

# %% [markdown]
# Now, let's calculate the various different moving averages for each ETF. We will calculate the 3, 4, 5, 6, 7, 8, 9, 10, 11, and 12 month moving averages, using the equivalent number of trading days for each time period (63, 84, 105, 126, 147, 168, 189, 210, 231, and 252 trading days).

# %%
# Define moving average windows in trading days
ma_windows = {
    '3m': 63,     # 3 months (~63 trading days)
    '4m': 84,     # 4 months (~84 trading days)
    '5m': 105,    # 5 months (~105 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '7m': 147,    # 7 months (~147 trading days)
    '8m': 168,    # 8 months (~168 trading days)
    '9m': 189,    # 9 months (~189 trading days)
    '10m': 210,   # 10 months (~210 trading days)
    '11m': 231,   # 11 months (~231 trading days)
    '12m': 252    # 12 months (~252 trading days)
}

# %%
for fund, data in fund_data.items():
    for window, days in ma_windows.items():
        data[f"{fund}_MA_{window}"] = data[f"{fund}_Adj_Close"].rolling(window=days).mean()

# %% [markdown]
# ## Calculate Forward Return Windows

# %% [markdown]
# Next, we will calculate the forward return for each ETF for the same time periods as the moving averages. For example, we will calculate the 3 month forward return, which is the return from the current date to 3 months in the future, and so on for each of the other time periods.

# %%
# Define forward return windows in trading days
forward_return_windows = {
    '3m': 63,     # 3 months (~63 trading days)
    '4m': 84,     # 4 months (~84 trading days)
    '5m': 105,    # 5 months (~105 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '7m': 147,    # 7 months (~147 trading days)
    '8m': 168,    # 8 months (~168 trading days)
    '9m': 189,    # 9 months (~189 trading days)
    '10m': 210,   # 10 months (~210 trading days)
    '11m': 231,   # 11 months (~231 trading days)
    '12m': 252    # 12 months (~252 trading days)
}

# %%
for fund, data in fund_data.items():
    for window, days in forward_return_windows.items():
        data[f"{fund}_Forward_Return_{window}"] = data[f"{fund}_Adj_Close"].shift(-days) / data[f"{fund}_Adj_Close"] - 1

# %% [markdown]
# ## Calculate Moving Average Predictions

# %% [markdown]
# Now, we will calculate the moving average predictions, as follows:
#
# * If the price is above the moving average, the prediction is 1 (i.e. the price will be above the moving average in the future).
# * If the price is below the moving average, the prediction is -1 (i.e. the price will be below the moving average in the future).
# * Calculate the accuracy of the predictions by comparing them to the actual forward returns (i.e. if the forward return is positive, the actual outcome is 1, and if the forward return is negative, the actual outcome is -1).
# * Calculate the difference between the price and moving average (percentage), z-score (standardize) both that difference and the forward returns, and run a standardized OLS regression of forward return on the price-MA difference. Standardizing both sides puts every fund, moving average, and forward return window on the same scale, so the regression slope (a standardized beta, equal to the Pearson correlation) is directly comparable across them.

# %%
ma_prediction_results = pd.DataFrame(columns=[
    "Fund",
    "MA_Window",
    "Forward_Return_Window",
    "Overall_Accuracy",
    "Positive_Accuracy",
    "Negative_Accuracy",
    "Std_Beta",
    "Std_Beta_PValue",
    "R_Squared",
])

for fund, data in fund_data.items():
    for ma_label, ma_window in ma_windows.items():
        # Prediction and the price-vs-MA gap depend only on the MA window, so compute them
        # once per MA on the full frame (these columns persist for the plots further down).
        data[f"{fund}_MA_Prediction_{ma_label}"] = 0
        data.loc[data[f"{fund}_Adj_Close"] > data[f"{fund}_MA_{ma_label}"], f"{fund}_MA_Prediction_{ma_label}"] = 1
        data.loc[data[f"{fund}_Adj_Close"] < data[f"{fund}_MA_{ma_label}"], f"{fund}_MA_Prediction_{ma_label}"] = -1

        # Calculate the percentage difference between price and moving average
        data[f"{fund}_Price_MA_Diff_Percent_{ma_label}"] = (data[f"{fund}_Adj_Close"] - data[f"{fund}_MA_{ma_label}"]) / data[f"{fund}_MA_{ma_label}"]

        for fr_label, fr_window in forward_return_windows.items():
            data[f"{fund}_Actual_{fr_label}"] = 0
            data.loc[data[f"{fund}_Forward_Return_{fr_label}"] > 0, f"{fund}_Actual_{fr_label}"] = 1
            data.loc[data[f"{fund}_Forward_Return_{fr_label}"] < 0, f"{fund}_Actual_{fr_label}"] = -1

            pred_col = f"{fund}_MA_Prediction_{ma_label}"
            actual_col = f"{fund}_Actual_{fr_label}"
            diff_col = f"{fund}_Price_MA_Diff_Percent_{ma_label}"
            fr_col = f"{fund}_Forward_Return_{fr_label}"

            # Restrict to rows where THIS MA and THIS forward return are both defined, so each
            # window pair is evaluated on its own full sample rather than the intersection of all
            # 12 windows. (Dropping NaN on every column collapsed every pair onto the 12m-MA /
            # 12m-forward overlap, discarding most of the data for the shorter windows.)
            pair_data = data.dropna(subset=[f"{fund}_MA_{ma_label}", fr_col])
            # pair_data = pair_data.resample("W").last()

            overall_accuracy = (pair_data[pred_col] == pair_data[actual_col]).mean()
            pos_accuracy = ((pair_data[pred_col] == 1) & (pair_data[actual_col] == 1)).sum() / (pair_data[pred_col] == 1).sum()
            neg_accuracy = ((pair_data[pred_col] == -1) & (pair_data[actual_col] == -1)).sum() / (pair_data[pred_col] == -1).sum()

            # Calculate the mean forward return (and +/- 2 std bands) for the cases where the MA predicted a positive return and where it predicted a negative return
            positive_returns = pair_data.loc[pair_data[pred_col] == 1, fr_col]
            positive_mean_return = positive_returns.mean()
            positive_mean_plus_two_std = positive_mean_return + positive_returns.std() * 2
            positive_mean_minus_two_std = positive_mean_return - positive_returns.std() * 2
            negative_returns = pair_data.loc[pair_data[pred_col] == -1, fr_col]
            negative_mean_return = negative_returns.mean()
            negative_mean_plus_two_std = negative_mean_return + negative_returns.std() * 2
            negative_mean_minus_two_std = negative_mean_return - negative_returns.std() * 2

            # Z-score (standardize) the predictor and the forward return so the regression
            # slope is a standardized beta, comparable across funds, MAs, and forward windows.
            # With both sides standardized the slope equals the Pearson correlation.
            diff_z_col = f"{diff_col}_Z"
            fr_z_col = f"{fr_col}_Z"
            pair_data = pair_data.assign(**{
                diff_z_col: (pair_data[diff_col] - pair_data[diff_col].mean()) / pair_data[diff_col].std(),
                fr_z_col: (pair_data[fr_col] - pair_data[fr_col].mean()) / pair_data[fr_col].std(),
            })

            # Run a standardized OLS regression of forward return on the price-MA difference
            model = run_regression(
                df=pair_data,
                x_plot_column=diff_z_col,
                y_plot_column=fr_z_col,
                regression_model="OLS-statsmodels",
                regression_constant=True,
            )
            std_beta = model.params.iloc[1]          # standardized slope (== Pearson correlation)
            std_beta_pvalue = model.pvalues.iloc[1]  # p-value for the slope
            r_squared = model.rsquared               # R-squared of the regression

            results = pd.DataFrame([{
                    "Fund": fund,
                    "MA_Window": ma_label,
                    "Forward_Return_Window": fr_label,
                    "Overall_Accuracy": overall_accuracy,
                    "Positive_Accuracy": pos_accuracy,
                    "Negative_Accuracy": neg_accuracy,
                    "Positive_Mean_Return": positive_mean_return,
                    "Positive_Mean_Plus_Two_Std": positive_mean_plus_two_std,
                    "Positive_Mean_Minus_Two_Std": positive_mean_minus_two_std,
                    "Negative_Mean_Return": negative_mean_return,
                    "Negative_Mean_Plus_Two_Std": negative_mean_plus_two_std,
                    "Negative_Mean_Minus_Two_Std": negative_mean_minus_two_std,
                    "Std_Beta": std_beta,
                    "Std_Beta_PValue": std_beta_pvalue,
                    "R_Squared": r_squared,
            }])
            
            ma_prediction_results = pd.concat([ma_prediction_results, results], ignore_index=True)

# %%
display(ma_prediction_results)

# %% [markdown]
# ## Plot Moving Average Predictions
#
# The following plots show the relationship between the price-MA difference and the forward returns for each ETF, moving average, and forward return window. Simply comment out the MA and forward return windows you don't want to plot. we'll use the 3 month MA for a brief look at the results.

# %%
# Define moving average windows in trading days
ma_windows = {
    '3m': 63,     # 3 months (~63 trading days)
    # '4m': 84,     # 4 months (~84 trading days)
    # '5m': 105,    # 5 months (~105 trading days)
    # '6m': 126,    # 6 months (~126 trading days)
    # '7m': 147,    # 7 months (~147 trading days)
    # '8m': 168,    # 8 months (~168 trading days)
    # '9m': 189,    # 9 months (~189 trading days)
    # '10m': 210,   # 10 months (~210 trading days)
    # '11m': 231,   # 11 months (~231 trading days)
    # '12m': 252    # 12 months (~252 trading days)
}

# Define forward return windows in trading days
forward_return_windows = {
    '3m': 63,     # 3 months (~63 trading days)
    '4m': 84,     # 4 months (~84 trading days)
    '5m': 105,    # 5 months (~105 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '7m': 147,    # 7 months (~147 trading days)
    '8m': 168,    # 8 months (~168 trading days)
    '9m': 189,    # 9 months (~189 trading days)
    '10m': 210,   # 10 months (~210 trading days)
    '11m': 231,   # 11 months (~231 trading days)
    '12m': 252    # 12 months (~252 trading days)
}

# %% [markdown]
# ### IVV, EFA, and EEM

# %%
for fund, data in fund_data.items():
    if fund not in ["IVV", "EFA", "EEM"]:
        continue
    for ma_label, ma_window in ma_windows.items():
        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Overall_Accuracy", "Positive_Accuracy", "Negative_Accuracy"],
            title=f"{fund} MA ({ma_label}) Prediction Accuracy vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Accuracy",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Positive_Mean_Return", "Positive_Mean_Plus_Two_Std", "Positive_Mean_Minus_Two_Std", "Negative_Mean_Return", "Negative_Mean_Plus_Two_Std", "Negative_Mean_Minus_Two_Std"],
            title=f"{fund} MA ({ma_label}) Forward Mean, +/- 2 Std Return vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Return",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        for fr_label, fr_window in forward_return_windows.items():
            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == 1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Positive Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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

            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == -1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Negative Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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

# %% [markdown]
# ### GSG and IAU

# %%
for fund, data in fund_data.items():
    if fund not in ["GSG", "IAU"]:
        continue
    for ma_label, ma_window in ma_windows.items():
        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Overall_Accuracy", "Positive_Accuracy", "Negative_Accuracy"],
            title=f"{fund} MA ({ma_label}) Prediction Accuracy vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Accuracy",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Positive_Mean_Return", "Positive_Mean_Plus_Two_Std", "Positive_Mean_Minus_Two_Std", "Negative_Mean_Return", "Negative_Mean_Plus_Two_Std", "Negative_Mean_Minus_Two_Std"],
            title=f"{fund} MA ({ma_label}) Forward Mean, +/- 2 Std Return vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Return",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        for fr_label, fr_window in forward_return_windows.items():
            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == 1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Positive Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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

            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == -1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Negative Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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

# %% [markdown]
# ### IEF and TLT

# %%
for fund, data in fund_data.items():
    if fund not in ["IEF", "TLT"]:
        continue
    for ma_label, ma_window in ma_windows.items():
        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Overall_Accuracy", "Positive_Accuracy", "Negative_Accuracy"],
            title=f"{fund} MA ({ma_label}) Prediction Accuracy vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Accuracy",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Positive_Mean_Return", "Positive_Mean_Plus_Two_Std", "Positive_Mean_Minus_Two_Std", "Negative_Mean_Return", "Negative_Mean_Plus_Two_Std", "Negative_Mean_Minus_Two_Std"],
            title=f"{fund} MA ({ma_label}) Forward Mean, +/- 2 Std Return vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Return",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        for fr_label, fr_window in forward_return_windows.items():
            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == 1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Positive Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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

            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == -1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Negative Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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

# %%
# for fund, data in fund_data.items():
    # for ma_label, ma_window in ma_windows.items():
        # for fr_label, fr_window in forward_return_windows.items():
            # plot_scatter(
            #     df=data,
            #     x_plot_column=f"{fund}_Price_MA_Diff_Percent_{ma_label}",
            #     y_plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
            #     title=f"{fund} MA Diff (Percent) ({ma_label}) vs Forward Return ({fr_label})",
            #     x_label="MA Diff (Percent)",
            #     x_format="Decimal",
            #     x_format_decimal_places=2,
            #     x_tick_spacing="Auto",
            #     x_tick_start=None,
            #     x_tick_rotation=30,
            #     y_label="Forward Return",
            #     y_format="Decimal",
            #     y_format_decimal_places=2,
            #     y_tick_spacing="Auto",
            #     y_tick_rotation=0,
            #     plot_OLS_regression_line=True,
            #     OLS_column=f"{fund}_Forward_Return_{fr_label}",
            #     plot_Ridge_regression_line=True,
            #     Ridge_column=f"{fund}_Forward_Return_{fr_label}",
            #     plot_RidgeCV_regression_line=True,
            #     RidgeCV_column=f"{fund}_Forward_Return_{fr_label}",
            #     regression_constant=True,
            #     grid=True,
            #     legend=True,
            #     export_plot=False,
            #     plot_file_name=None,
            # )

# %% [markdown]
# ## Analysis Of Results

# %% [markdown]
# ### 1. Positive, Negative, and Overall Accuracy

# %% [markdown]
# From the above plots, we can see that some ETFs (which we are - kind of - using as a proxy for asset classes), appear to have a stronger relationship between the price-MA difference and the forward returns than others. This "relationship" takes the form of the overall accuracy of the predictions, which tells us how well the price-MA difference predicts the direction of the future returns.

# %% [markdown]
# #### 1.1. Mean Overall Accuracy by Fund and MA Window

# %% [markdown]
# Here we plot the overall mean prediction accuracy for each ETF and MA window combination.

# %%
# Calc overall mean accuracy for each fund across all MA windows
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Overall_Accuracy"].mean().reset_index()

# Create a new DataFrame with unique MA_Window values and merge the mean accuracy for each fund
accuracy = pd.DataFrame({"MA_Window": temp["MA_Window"].unique()})

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Overall_Accuracy"]].rename(
        columns={"Overall_Accuracy": f"{fund}_Overall_Accuracy"}
    )
    accuracy = pd.merge(accuracy, fund_temp, on="MA_Window", how="outer")
    
plot_scatter(
    df=accuracy,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Overall_Accuracy", 
                    "EFA_Overall_Accuracy", 
                    "EEM_Overall_Accuracy", 
                    "GSG_Overall_Accuracy", 
                    "IAU_Overall_Accuracy", 
                    "IEF_Overall_Accuracy", 
                    "TLT_Overall_Accuracy"],
    title="Mean Overall Accuracy by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Accuracy",
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
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)


# %% [markdown]
# The stock funds (IVV, EFA, and EEM) have the highest mean overall accuracy, which tells us that the price-MA difference is a better predictor of the direction of future returns for these funds than for the other funds. The commodity fund (GSG) has the lowest mean overall accuracy, followed by long-term bonds (TLT), which both rank below the 50% threshold. If the mean overall accuracy does not exceed the 50% mark, then essentially the price-MA difference is not any better than a coin flip at predicting the direction of future returns.

# %% [markdown]
# #### 1.2. Mean Positive Accuracy by Fund and MA Window

# %% [markdown]
# The overall accuracy statistic includes the predicted accuracy of both the positive (are future returns positive when the price-MA is positive) and the negative (are future returns negative when the price-MA is negative) directions. The overall accuracy is useful from a long-short standpoint, but from a long-only perspective, we care only about the positive direction, which we plot next.

# %%
# Calc overall mean accuracy for each fund across all MA windows
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Positive_Accuracy"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Positive_Accuracy"]].rename(
        columns={"Positive_Accuracy": f"{fund}_Positive_Accuracy"}
    )
    accuracy = pd.merge(accuracy, fund_temp, on="MA_Window", how="outer")
    
plot_scatter(
    df=accuracy,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Positive_Accuracy",
                    "EFA_Positive_Accuracy",
                    "EEM_Positive_Accuracy",
                    "GSG_Positive_Accuracy",
                    "IAU_Positive_Accuracy",
                    "IEF_Positive_Accuracy",
                    "TLT_Positive_Accuracy"],
    title="Mean Positive Accuracy by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Accuracy",
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
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# What we see is a nearly uniform shift up in the mean positive accuracy for all of the funds, relative to the overall accuracy. And not just by a little bit - it's significant, as we will see below.

# %% [markdown]
# #### 1.3. Difference Between Positive and Overall Accuracy by Fund and MA Window

# %% [markdown]
# Here's the plot of the difference betweent he mean and positive accuracy.

# %%
for fund in fund_list:
    accuracy[f"{fund}_Positive_Overall_Mean_Diff"] = accuracy[f"{fund}_Positive_Accuracy"] - accuracy[f"{fund}_Overall_Accuracy"]

plot_scatter(
    df=accuracy,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Positive_Overall_Mean_Diff", 
                    "EFA_Positive_Overall_Mean_Diff", 
                    "EEM_Positive_Overall_Mean_Diff", 
                    "GSG_Positive_Overall_Mean_Diff", 
                    "IAU_Positive_Overall_Mean_Diff", 
                    "IEF_Positive_Overall_Mean_Diff", 
                    "TLT_Positive_Overall_Mean_Diff"],
    title="Difference Between Positive and Overall Accuracy by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Accuracy Difference",
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
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# IVV shows a 10 - 14% difference, while GSG show only a 2 or 3% improvement. The other funds show a 9 - 12%. If we were interested in using the price-MA difference to predict the direction of future returns, we would be better off using only the positive predictions.

# %% [markdown]
# ### 2. Distribution of Future Returns Based on Price-MA Difference

# %% [markdown]
# Next, we can consider the shape of the distribution of the future returns, split on whether the the price-MA difference is positive or negative.

# %% [markdown]
# #### 2.1. Mean Future Return When Price-MA Difference is Positive by Fund and MA Window

# %% [markdown]
# First, the distribution of future returns when the price-MA difference is positive.

# %%
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Positive_Mean_Return"].mean().reset_index()

distribution = pd.DataFrame({"MA_Window": temp["MA_Window"].unique()})

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Positive_Mean_Return"]].rename(
        columns={"Positive_Mean_Return": f"{fund}_Positive_Mean_Return"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Positive_Mean_Return",
                    "EFA_Positive_Mean_Return",
                    "EEM_Positive_Mean_Return",
                    "GSG_Positive_Mean_Return",
                    "IAU_Positive_Mean_Return",
                    "IEF_Positive_Mean_Return",
                    "TLT_Positive_Mean_Return"],
    title="Mean Future Return When Price-MA Difference is Positive by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Return",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)



# %% [markdown]
# In a perfect world, we want to see similar numbers across all MA windows, and all of those numbers would be relatively high. If every window gives us roughly the same distribution of future returns, that would indicate a consistent predictive relationship across all windows. But, what we often see is that the distributions vary quite a bit depending on the window, which suggests that it's useful to consider a combination of windows to form a more robust signal.
#
# Note that gold (IAU) has a smaller variation and much higher values (mean return is ~1.5% greater than IVV) across MA windows compared to the other funds.

# %% [markdown]
# #### 2.2. Mean Future Return When Price-MA Difference is Negative by Fund and MA Window

# %% [markdown]
# On to the distribution of future returns when the price-MA difference is negative.

# %%
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Negative_Mean_Return"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Negative_Mean_Return"]].rename(
        columns={"Negative_Mean_Return": f"{fund}_Negative_Mean_Return"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Negative_Mean_Return",
                    "EFA_Negative_Mean_Return",
                    "EEM_Negative_Mean_Return",
                    "GSG_Negative_Mean_Return",
                    "IAU_Negative_Mean_Return",
                    "IEF_Negative_Mean_Return",
                    "TLT_Negative_Mean_Return"],
    title="Mean Future Return When Price-MA Difference is Negative by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Return",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# Interesting, the mean returns are mostly still positive. That suggests that even when the price-MA difference is negative, future returns tend to be positive on average, though perhaps smaller than when the difference is positive.

# %% [markdown]
# #### 2.3. Difference Between Predicted Positive and Negative Mean Returns by Fund and MA Window

# %% [markdown]
# Next, we can look at the *difference* in mean future returns between when the price-MA difference is positive and when it is negative.

# %%
for fund in fund_list:
    distribution[f"{fund}_Mean_Return_Diff"] = distribution[f"{fund}_Positive_Mean_Return"] - distribution[f"{fund}_Negative_Mean_Return"]

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Mean_Return_Diff", 
                    "EFA_Mean_Return_Diff", 
                    "EEM_Mean_Return_Diff", 
                    "GSG_Mean_Return_Diff", 
                    "IAU_Mean_Return_Diff", 
                    "IEF_Mean_Return_Diff", 
                    "TLT_Mean_Return_Diff"],
    title="Difference Between Predicted Positive and Negative Mean Returns by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Return Difference",
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
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
#  In general, the mean of the future positive predicted returns is higher than the mean of the future negative predicted returns, which is what we would expect if the price-MA difference has any predictive power. However, the distributions are not normal, and there are some outliers that skew the distributions. These outliers show up as the long tails in the distributions, and the number and magnitude of the outliers can be seen in the mean +/- 2 standard deviations.
#
#  Note again, gold has the highest difference in mean return between when the price-MA difference is positive and when it is negative.

# %% [markdown]
# #### 2.4. Difference Between Positive Mean +2 Std and Positive Mean -2 Std Returns by Fund and MA Window

# %% [markdown]
# As mentioned above, we think that there are outliers that skew the distributions of the forward returns. But by how much? And how can we quantify their impact? One way is to look at the standard deviations. Here's the plots for the difference between  2 standard deviations above and below the mean for the forward returns.

# %%
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Positive_Mean_Plus_Two_Std"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Positive_Mean_Plus_Two_Std"]].rename(
        columns={"Positive_Mean_Plus_Two_Std": f"{fund}_Positive_Mean_Plus_Two_Std"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Positive_Mean_Minus_Two_Std"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Positive_Mean_Minus_Two_Std"]].rename(
        columns={"Positive_Mean_Minus_Two_Std": f"{fund}_Positive_Mean_Minus_Two_Std"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

for fund in fund_list:
    distribution[f"{fund}_Positive_Mean_Plus_Minus_2Std_Diff"] = distribution[f"{fund}_Positive_Mean_Plus_Two_Std"] - distribution[f"{fund}_Positive_Mean_Minus_Two_Std"]

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Positive_Mean_Plus_Minus_2Std_Diff",
                    "EFA_Positive_Mean_Plus_Minus_2Std_Diff",
                    "EEM_Positive_Mean_Plus_Minus_2Std_Diff",
                    "GSG_Positive_Mean_Plus_Minus_2Std_Diff",
                    "IAU_Positive_Mean_Plus_Minus_2Std_Diff",
                    "IEF_Positive_Mean_Plus_Minus_2Std_Diff",
                    "TLT_Positive_Mean_Plus_Minus_2Std_Diff"],
    title="Difference Between Positive Mean +2 Std and Positive Mean -2 Std Returns by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Mean Return 2 Std Difference",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# GSG is a mess... the commodity fund has a lot of noise and outliers. We'd like to see a tight distribution, that might give us confidence that the forward returns are within a reasonable range and not being dominated by extreme values. Here, the 7-10 year bond ETF is the leader, with a much tighter distribution and fewer extreme values skewing the results.

# %% [markdown]
# #### 2.5. Difference Between Negative Mean +2 Std and Negative Mean -2 Std Returns by Fund and MA Window

# %% [markdown]
# Now for the e difference between 2 standard deviations above and below the mean for the forward returns when price-MA is negative.

# %%
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Negative_Mean_Plus_Two_Std"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Negative_Mean_Plus_Two_Std"]].rename(
        columns={"Negative_Mean_Plus_Two_Std": f"{fund}_Negative_Mean_Plus_Two_Std"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Negative_Mean_Minus_Two_Std"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Negative_Mean_Minus_Two_Std"]].rename(
        columns={"Negative_Mean_Minus_Two_Std": f"{fund}_Negative_Mean_Minus_Two_Std"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

for fund in fund_list:
    distribution[f"{fund}_Negative_Mean_Plus_Minus_2Std_Diff"] = distribution[f"{fund}_Negative_Mean_Plus_Two_Std"] - distribution[f"{fund}_Negative_Mean_Minus_Two_Std"]

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Negative_Mean_Plus_Minus_2Std_Diff",
                    "EFA_Negative_Mean_Plus_Minus_2Std_Diff",
                    "EEM_Negative_Mean_Plus_Minus_2Std_Diff",
                    "GSG_Negative_Mean_Plus_Minus_2Std_Diff",
                    "IAU_Negative_Mean_Plus_Minus_2Std_Diff",
                    "IEF_Negative_Mean_Plus_Minus_2Std_Diff",
                    "TLT_Negative_Mean_Plus_Minus_2Std_Diff"],
    title="Difference Between Negative Mean +2 Std and Negative Mean -2 Std Returns by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Mean Return 2 Std Difference",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# This might not be as relevant to us (from a long-only perspective), but it's still worth looking at to understand how the asset classes rank. Emerging markets tend to have more volatility and outliers, so this plot makes sense intuitively.

# %% [markdown]
# #### 2.6. Difference Between Positive and Negative +/-2 Std Return Spreads by Fund and MA Window

# %% [markdown]
# Finally, we have the difference between the 2 standard deviation spreads.

# %%
for fund in fund_list:
    distribution[f"{fund}_2Std_Spread_Diff"] = distribution[f"{fund}_Positive_Mean_Plus_Minus_2Std_Diff"] - distribution[f"{fund}_Negative_Mean_Plus_Minus_2Std_Diff"]

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_2Std_Spread_Diff",
                    "EFA_2Std_Spread_Diff",
                    "EEM_2Std_Spread_Diff",
                    "GSG_2Std_Spread_Diff",
                    "IAU_2Std_Spread_Diff",
                    "IEF_2Std_Spread_Diff",
                    "TLT_2Std_Spread_Diff"],
    title="Difference Between Positive and Negative +/-2 Std Return Spreads by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Mean Return 2 Std Difference (Positive - Negative)",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)

# %% [markdown]
# This plot really compares the kurtosis of the forward return distributions by looking at the difference between the 2 standard deviation spreads for positive and negative price-MA conditions. If these values are positive, it means that the forward return distributions have fatter tails for positive price-MA conditions relative to negative price-MA conditions, and the opposite is true if the values are negative.
#
# So anything <=0 is good here, which brings us back to gold, which is positive. Pulling up one of the earlier plots:

# %%
for fund, data in fund_data.items():
    if fund not in ["IAU"]:
        continue
    for ma_label, ma_window in ma_windows.items():
        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Positive_Mean_Return", "Positive_Mean_Plus_Two_Std", "Positive_Mean_Minus_Two_Std", "Negative_Mean_Return", "Negative_Mean_Plus_Two_Std", "Negative_Mean_Minus_Two_Std"],
            title=f"{fund} MA ({ma_label}) Forward Mean, +/- 2 Std Return vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Return",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

# %% [markdown]
# We can see that the mean +2 std return line is for the positive price-MA condition is actually above the mean +2 std return line for the negative price-MA condition, whichi is different than any of the other funds. The explanation? The forward positive return tail is fatter, which is actually a more desirable condition. While we'd like a tight distribution, we also will accept a fatter positive tail, as that means that the forward returns are more likely to be positive and larger than they would be otherwise.

# %% [markdown]
# ## Conclusion

# %% [markdown]
# This analysis shows that the predictive power of moving averages varies across different asset classes. While some ETFs, particularly those representing equities, demonstrate a stronger relationship between price-MA differences and future returns, others, like commodities and long-term bonds, show less predictive power. The findings suggest that investors may benefit from using the price-MA relationship when developing trend following investment strategies.

# %% [markdown]
#


