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
#     display_name: general-venv-p313 (3.13.18)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Post Updates

# %% [markdown]
# Update 11/11/2026: Updated the methodology to ensure implementation lag is correctly applied based on FOMC announcements/rate changes and monthly returns The catch-all cycle label, previously "Modified Tightening", has been renamed `Extended Neutral` and is now documented that it covers 37% of the sample, including both zero-rate periods, and it is the single largest contributor to the strategy's return. The high yield regression chart was also plotting the Treasury series, and has been fixed. Commentary on the regressions has been revised to reflect that none of the four are statistically significant.

# %% [markdown]
# ## Introduction

# %% [markdown]
# In this post, we will look into the Fed Funds cycles and evaluate asset class performance during tightening and easing of monetary policy. We'll pull data for stocks, intermediate Treasuries, high yield credit, and gold, and analyze their returns during different phases of the Fed Funds cycle. We'll also establish a simple strategy that allocates capital to a specific asset based on the current phase of the cycle, and evaluate the performance of this strategy over time.

# %% [markdown]
# ## Python Imports

# %%
import os
import sys
import warnings

from itertools import combinations, count
from pathlib import Path

# Data Handling
import numpy as np
import pandas as pd

from scipy.stats import norm

# Display
from IPython.display import Markdown, display

# Suppress warnings
warnings.filterwarnings("ignore")

# Add src/ to the path so settings.py and the helper modules can be imported
src_directory = str(Path.cwd().parents[2] / "src")
if src_directory not in sys.path:
    sys.path.append(src_directory)

from settings import config

DATA_DIR = config("DATA_DIR")  # keep only the directories this post uses

# %% [markdown]
# ## Python Functions

# %% [markdown]
# Here are the functions needed for this project:
#
# * [bb_clean_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#bb_clean_data): Takes an Excel export from Bloomberg, removes the miscellaneous headings/rows, and returns a DataFrame.
# * [calc_fed_cycle_asset_performance](/posts/reusable-extensible-python-functions-financial-data-analysis/#calc_fed_cycle_asset_performance): Calculates metrics for an asset based on a specified Fed tightening/easing cycle.
# * [load_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.
# * [pandas_set_decimal_places](/posts/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.
# * [plot_bar_returns_ffr_change](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_bar_returns_ffr_change): Plot the bar chart of the cumulative or annualized returns for the asset class along with the change in the Fed Funds Rate.
# * [plot_scatter_regression_ffr_vs_returns](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter_regression_ffr_vs_returns): Plot the scatter plot and regression of the annualized return for the asset class along with the annualized change in the Fed Funds Rate.
# * [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the time series data from a DataFrame for a specified date range and columns.
# * [run_regression](/posts/reusable-extensible-python-functions-financial-data-analysis/#run_regression): Run a regression using a variety of different methods and return the results.
# * [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.

# %%
from bb_clean_data import bb_clean_data
from calc_fed_cycle_asset_performance import calc_fed_cycle_asset_performance
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_bar_returns_ffr_change import plot_bar_returns_ffr_change
from plot_scatter_regression_ffr_vs_returns import plot_scatter_regression_ffr_vs_returns
from plot_time_series import plot_time_series
from run_regression import run_regression
from summary_stats import summary_stats

# %%
pandas_set_decimal_places(2)
figure_number = count(1)
table_number = count(1)


# %% [markdown]
# ## Data Overview

# %% [markdown]
# ### Acquire & Plot Fed Funds Data

# %% [markdown]
# First, let's get the data for the Fed Funds target rate (FFR). This data is found in 3 different datasets from FRED, which we pull directly from the FRED CSV endpoint.

# %%
def pull_fred_series(series_id: str) -> pd.DataFrame:
    """Pull a single series from FRED as a date-indexed DataFrame."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    series = pd.read_csv(
        url,
        parse_dates=["observation_date"],
        index_col="observation_date",
    )
    # Normalize to nanosecond resolution so later merges against the
    # Bloomberg data line up on identical datetime dtypes
    series.index = series.index.astype("datetime64[ns]")
    series.index.name = "DATE"
    return pd.to_numeric(series[series_id], errors="coerce").to_frame()


# Pull Federal Funds Target Rate (DISCONTINUED) (DFEDTAR)
fedfunds_target_old = pull_fred_series("DFEDTAR")

# Pull Federal Funds Target Range - Upper Limit (DFEDTARU)
fedfunds_target_new_upper = pull_fred_series("DFEDTARU")

# Pull Federal Funds Target Range - Lower Limit (DFEDTARL)
fedfunds_target_new_lower = pull_fred_series("DFEDTARL")

# Merge the datasets together
fedfunds_combined = pd.concat([fedfunds_target_old, fedfunds_target_new_upper, fedfunds_target_new_lower], axis=1)

# Divide all values by 100 to get decimal rates
for col in fedfunds_combined.columns:
    fedfunds_combined[col] = fedfunds_combined[col] / 100

display(Markdown(f"Table {next(table_number)}: Fed Funds Target Rate Series, Daily"))
display(fedfunds_combined.iloc[45:60])

# %% [markdown]
# In the above plot we can see when the FFR adjustment actually took place, which was the middle of the month, post the FOMC meeting.

# %%
# Resample to month-end (as if we know the rate at the end of the month)
fedfunds_monthly = fedfunds_combined.resample("ME").last()

display(Markdown(f"Table {next(table_number)}: Fed Funds Target Rate Series, Month End"))
display(fedfunds_monthly)

# %% [markdown]
# The month end resampling helps us align monthly returns to FFR, but it is not perfect, as there is a roughly ~2 week lag between the rate adjustment and the end of the month. We'll discuss this more later.
#
# We can then generate several useful plots. First, the Fed Funds target rate:

# %%
plot_time_series(
    df=fedfunds_monthly,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["DFEDTAR", "DFEDTARU", "DFEDTARL"],
    title=f"Figure {next(figure_number)}: Fed Funds Target Rate",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Rate (%)",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing=0.01,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
    caption="Data Source: FRED, Analysis by the Author",
)

# %%
pandas_set_decimal_places(4)

# First drop the lower column and merge
fedfunds_monthly["fed_funds"] = fedfunds_monthly["DFEDTAR"].combine_first(fedfunds_monthly["DFEDTARU"])
fedfunds_monthly = fedfunds_monthly.drop(columns=["DFEDTARL", "DFEDTARU", "DFEDTAR"])

# Compute change in rate from either column
fedfunds_monthly["fed_funds_change"] = fedfunds_monthly["fed_funds"].diff()

display(Markdown(f"Table {next(table_number)}: Fed Funds Target Rate And Monthly Change"))
display(fedfunds_monthly)

# %% [markdown]
# And then the change in FFR from month-to-month:

# %%
plot_time_series(
    df=fedfunds_monthly,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["fed_funds_change"],
    title=f"Figure {next(figure_number)}: Fed Funds Change In Rate",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Rate Change (%)",
    y_format="Percentage",
    y_format_decimal_places=2,
    y_tick_spacing=0.0025,
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
    caption="Data Source: FRED, Analysis by the Author",
)

# %% [markdown]
# This plot, in particular, makes it easy to show the monthly increase and decrease in the FFR, as well as the magnitude of the change (i.e. slow, drawn-out increases or decreases or abrupt large increases or decreases).

# %% [markdown]
# ### Define Fed Policy Cycles

# %% [markdown]
# Next, we will define the Fed policy tightening and easing cycles:

# %%
# Set timeframe
START_DATE = "1989-12-15"
END_DATE = "2026-04-30"

# Copy DataFrame to avoid modifying original
fedfunds_cycles = fedfunds_monthly.copy()
fedfunds_cycles = fedfunds_cycles.loc[START_DATE:END_DATE]

# Reset index
fedfunds_cycles = fedfunds_cycles.reset_index()

# Drop the "fed_funds_change" column as we will use it to determine the cycle type later, but we don't need it in the final dataframe
fedfunds_cycles = fedfunds_cycles.drop(columns=["fed_funds_change"])

# Rename the date column to "Start Date", and the "fed_funds" column to "Fed Funds Start"
fedfunds_cycles = fedfunds_cycles.rename(columns={"DATE": "start_date", "fed_funds": "fed_funds_start"})

# Copy the "Start Date" column to a new column called "End Date" and shift it up by one row
fedfunds_cycles["end_date"] = fedfunds_cycles["start_date"].shift(-1)

# Copy the "Fed Funds Start" column to a new column called "Fed Funds End" and shift it up by one row
fedfunds_cycles["fed_funds_end"] = fedfunds_cycles["fed_funds_start"].shift(-1)

# Calculate the change in Fed Funds rate for each cycle
fedfunds_cycles["fed_funds_change"] = fedfunds_cycles["fed_funds_end"] - fedfunds_cycles["fed_funds_start"]

# Based on "Fed Funds Change" column, determine if the rate is increasing, decreasing, or unchanged
fedfunds_cycles["cycle"] = fedfunds_cycles["fed_funds_change"].apply(
    lambda x: "Tightening" if x > 0 else ("Easing" if x < 0 else "Neutral"))

display(Markdown(f"Table {next(table_number)}: Monthly Fed Funds Rate Changes And Cycle Labels"))
display(fedfunds_cycles)

# %% [markdown]
# Grouping the consecutive months of tightening and easing together, we can create a DataFrame that gives us the cumulative change in the FFR for each cycle, as well as the start and end dates for each cycle. This will be useful for evaluating asset class performance during these cycles.

# %%
fedfunds_grouped_cycles = fedfunds_cycles.copy()

# Create a group key that increments whenever the Cycle value changes
fedfunds_grouped_cycles['group'] = (fedfunds_grouped_cycles['cycle'] != fedfunds_grouped_cycles['cycle'].shift(1)).cumsum()

# Group by both the group key and Cycle label
cycle_ranges = (
    fedfunds_grouped_cycles.groupby(['group', 'cycle'], sort=False)
    .agg(
        start_date=('start_date', 'first'),
        end_date=('end_date', 'last'),
        fed_funds_start=('fed_funds_start', 'first'),
        fed_funds_end=('fed_funds_end', 'last')
    )
    .reset_index(drop=False)
    .drop(columns='group')
)

display(Markdown(f"Table {next(table_number)}: Fed Policy Cycles, Before Forward Filling Neutral Months"))
display(cycle_ranges)

# %% [markdown]
# We will also make the assumption that any "Neutral" months (i.e. months where the FFR did not change) are part of the preceding cycle, to a point. For example, if we have a tightening month followed by a neutral month, we will consider the neutral month to be part of the tightening cycle. This is a simplifying assumption, but it allows us to attempt to categorize months into either tightening or easing cycles that are in fact a continuation of those cycles.
# We will forward fill 6 months of neutral months as a starting point.
#
# That leaves a third bucket of monthly periods. Any month that is still unlabeled after the forward fill - either because the Fed has held the rate flat for more than 6 months, or because we are at the very start of the sample with no preceding cycle to inherit from - gets its own label, referred to as `Extended Neutral`. This includes most of the ZIRP era, such as the 2009-2015 and 2020-2021 zero-rate periods.

# %%
NEUTRAL_FILL_LIMIT = 6

fedfunds_grouped_cycles = fedfunds_cycles.copy()

# Forward fill cycle labels preceding "Neutral" cycles
fedfunds_grouped_cycles['cycle_filled'] = fedfunds_grouped_cycles['cycle'].replace('Neutral', pd.NA).ffill(limit=NEUTRAL_FILL_LIMIT)

# Label any remaining <NA> values as "Extended Neutral": either the Fed held the rate
# flat for longer than the 6 month fill limit, or we are at the start of the sample
# with no preceding cycle to inherit a label from
fedfunds_grouped_cycles['cycle_filled'] = fedfunds_grouped_cycles['cycle_filled'].fillna('Extended Neutral')

# Confirm how much of the sample lands in each bucket
display(Markdown(f"Table {next(table_number)}: Months By Cycle Label"))
display(fedfunds_grouped_cycles['cycle_filled'].value_counts())

# Create a group key that increments whenever the Cycle value changes
fedfunds_grouped_cycles['group'] = (fedfunds_grouped_cycles['cycle_filled'] != fedfunds_grouped_cycles['cycle_filled'].shift(1)).cumsum()

# Group by both the group key and Cycle label
cycle_ranges = (
    fedfunds_grouped_cycles.groupby(['group', 'cycle_filled'], sort=False)
    .agg(
        start_date=('start_date', 'first'),
        end_date=('end_date', 'last'),
        fed_funds_start=('fed_funds_start', 'first'),
        fed_funds_end=('fed_funds_end', 'last')
    )
    .reset_index(drop=False)
    .drop(columns='group')
)

# Calc change in Fed Funds rate for each cycle
cycle_ranges["fed_funds_change"] = cycle_ranges["fed_funds_end"] - cycle_ranges["fed_funds_start"]

# Add cycle labels
cycle_labels = [f"Cycle {i+1}" for i in range(len(cycle_ranges))]

# Combine labels with cycle_ranges
cycle_ranges['cycle_label'] = cycle_labels

display(Markdown(f"Table {next(table_number)}: Fed Policy Cycles"))
display(cycle_ranges)

# %% [markdown]
# ## Asset Class Performance By Fed Policy Cycle

# %% [markdown]
# Moving on, we will now look at the performance of four (4) different asset classes during each Fed cycle. We'll use the following Bloomberg indices:
#
# * SPXT_S&P 500 Total Return Index (Stocks)
# * SPBDU10T_S&P US Treasury Bond 7-10 Year Total Return Index (Bonds)
# * LF98TRUU_Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD (High Yield Bonds)
# * XAU_Gold USD Spot (Gold)

# %% [markdown]
# ### Stocks

# %% [markdown]
# First, we will clean and load the data for the S&P 500 Total Return Index (SPXT):

# %%
pandas_set_decimal_places(2)

bb_clean_data(
    base_directory=DATA_DIR,
    fund_ticker_name="SPXT_S&P 500 Total Return Index",
    source="Bloomberg",
    asset_class="Indices",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

spxt = load_data(
    base_directory=DATA_DIR,
    ticker="SPXT_S&P 500 Total Return Index_Clean",
    source="Bloomberg",
    asset_class="Indices",
    timeframe="Daily",
    file_format="pickle",
)

# The Bloomberg pickle stores the index as objects; convert to a nanosecond
# DatetimeIndex so it matches the FRED data in the merges further down
spxt.index = pd.to_datetime(spxt.index).astype("datetime64[ns]")

# Filter SPXT to date range
spxt = spxt[(spxt.index >= pd.to_datetime(START_DATE)) & (spxt.index <= pd.to_datetime(END_DATE))]

# Drop everything except the "close" column
spxt = spxt[["Close"]]

# Resample to monthly frequency
spxt_monthly = spxt.resample("ME").last()
spxt_monthly["Monthly_Return"] = spxt_monthly["Close"].pct_change()
spxt_monthly = spxt_monthly.dropna()

display(Markdown(f"Table {next(table_number)}: S&P 500 Total Return Index Monthly Close And Returns"))
display(spxt_monthly)

# %% [markdown]
# Next, we can plot the price history before calculating the cycle performance:

# %%
plot_time_series(
    df=spxt,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["Close"],
    title=f"Figure {next(figure_number)}: S&P 500 Total Return Index Daily Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=1000,
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
    caption="Data Source: Bloomberg, Analysis by the Author",
)

# %% [markdown]
# Next, we will calculate the performance for SPXT based on the pre-defined Fed cycles. To illustrate the methodology, we can take Cycle 1, which was 12/31/1989 to 6/30/1990, and which would also included rate decisions in the middle of December through the middle of June, and would therefore include monthly returns for January through June of 1990. So, hypothetically, from the rate decision in the middle of December, we could allocate a portfolio on January 1st, then after the rate decision in the middle of June, we could close any positions at the end of June (realizing June's return).

# %%
display(cycle_ranges.iloc[0])
print(f"Cycle 1 Cumulative Return: {(1+spxt_monthly.loc['1990-01-31':'1990-06-30']['Monthly_Return']).cumprod()-1}")

# %% [markdown]
# And a second example, from Cycle 2, which was July of 1990 through March of 1993. This would have included rate decisions in the middle of June (portfolio allocations 7/1), through the middle of March (closing positions 3/31), and would therefore include monthly returns for July 1990 through March 1993.

# %%
display(cycle_ranges.iloc[1])
print(f"Cycle 1 Cumulative Return: {(1+spxt_monthly.loc['1990-07-31':'1993-03-31']['Monthly_Return']).cumprod()-1}")

# %% [markdown]
# Based on the above, we can see that the `end_date` is value, but we need to bump the `start_date` to the beginning of the next month to correctly capture the monthly returns for the cycle. We'll call this column `adjusted_start_date`.

# %%
cycle_ranges['adjusted_start_date'] = cycle_ranges['start_date'] + pd.DateOffset(months=1)

display(Markdown(f"Table {next(table_number)}: Fed Policy Cycles, Adjusted Start Date"))
display(cycle_ranges)

# %%
spxt_cycles = calc_fed_cycle_asset_performance(
    start_date=cycle_ranges["adjusted_start_date"],
    end_date=cycle_ranges["end_date"],
    label=cycle_ranges["cycle_label"],
    fed_funds_change=cycle_ranges["fed_funds_change"],
    monthly_returns=spxt_monthly,
)

display(Markdown(f"Table {next(table_number)}: S&P 500 Total Return Index Performance By Fed Policy Cycle"))
display(spxt_cycles)

# %%
spxt_cycles = calc_fed_cycle_asset_performance(
    start_date=cycle_ranges["start_date"],
    end_date=cycle_ranges["end_date"],
    label=cycle_ranges["cycle_label"],
    fed_funds_change=cycle_ranges["fed_funds_change"],
    monthly_returns=spxt_monthly,
)

display(Markdown(f"Table {next(table_number)}: S&P 500 Total Return Index Performance By Fed Policy Cycle"))
display(spxt_cycles)

# %% [markdown]
# This gives us the following data points:
#
# * Cycle start date
# * Cycle end date
# * Number of months in the cycle
# * Cumulative return during the cycle (decimal and percent)
# * Average monthly return during the cycle (decimal and percent)
# * Annualized return during the cycle (decimal and percent)
# * Return volatility during the cycle
# * Cumulative change in FFR during the cycle (decimal and basis points)
# * Annualized change in FFR during the cycle (decimal and basis points)
#
# From the above DataFrame, we can then plot the cumulative and annualized returns for each cycle in a bar chart. First, the cumulative returns along with the cumulative change in FFR:

# %%
plot_bar_returns_ffr_change(
    cycle_df=spxt_cycles,
    asset_label="SPXT",
    annualized_or_cumulative="Cumulative",
    title=f"Figure {next(figure_number)}: S&P 500 Cumulative Return And Cumulative Change In FFR By Fed Policy Cycle",
    caption="Data Sources: Bloomberg & FRED, Analysis by the Author",
)

# %% [markdown]
# And then the annualized returns along with the annualized change in FFR:

# %%
plot_bar_returns_ffr_change(
    cycle_df=spxt_cycles,
    asset_label="SPXT",
    annualized_or_cumulative="Annualized",
    title=f"Figure {next(figure_number)}: S&P 500 Annualized Return And Annualized Change In FFR By Fed Policy Cycle",
    caption="Data Sources: Bloomberg & FRED, Analysis by the Author",
)

# %% [markdown]
# The cumulative returns plot is not particularly insightful, but there are some interesting observations from the annualized returns plot. During the past two (2) rate cutting cycles (cycles 11/12/13 and 18), stocks have exhibited negative returns during either a flat period or the rate cutting cycle. However, after the rate cutting cycle was complete, returns during the following cycle (when rates were usually flat) were quite strong and higher than the historical mean return for the S&P 500. The economic intuition for this behavior is valid; as the economy weakens, investors are concerned about the pricing of equities, the returns become negative, and the Fed responds with cutting rates. The exact timing of when the Fed begins cutting rates is one of the unknowns; the Fed could be ahead of the curve, cutting rates as economic data begins to prompt that action, or behind the curve, where the economy rolls over rapidly and even the Fed's actions are not enough to halt the economic contraction.
#
# Finally, we can run an OLS regression to check fit:

# %%
model = run_regression(
    df=spxt_cycles,
    x_plot_column="FFR_AnnualizedChange_bps",
    y_plot_column="AnnualizedReturnPct",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)

print(model.summary())

# Pull the fitted coefficients by name
intercept = model.params["const"]
slope = model.params["FFR_AnnualizedChange_bps"]
print(f"Intercept: {intercept}, Slope: {slope}")

# Calc X and Y values for the regression line across the observed FFR range
X_vals = np.linspace(
    spxt_cycles["FFR_AnnualizedChange_bps"].min(),
    spxt_cycles["FFR_AnnualizedChange_bps"].max(),
    100,
)
Y_vals = intercept + slope * X_vals

# %% [markdown]
# And then plot the regression line along with the values:

# %%
plot_scatter_regression_ffr_vs_returns(
    cycle_df=spxt_cycles,
    asset_label="SPXT",
    x_vals=X_vals,
    y_vals=Y_vals,
    intercept=intercept,
    slope=slope,
    title=f"Figure {next(figure_number)}: S&P 500 Annualized Return vs Annualized Change In FFR By Fed Policy Cycle",
    caption="Data Source: Bloomberg, FRED, Analysis by the Author",
)

# %% [markdown]
# Here we can see the data points for cycles 11, 12, 13, 14 and 18 as mentioned above. Interestingly, cycles 28/29/30 (which is the current rate cutting cycle) appears to be an outlier. Of course, the book is not yet finished for cycles 28/29/30, and we could certainly see a bear market in stocks over the next several years.

# %% [markdown]
# ### Bonds

# %% [markdown]
# Next, we'll run a similar process for medium term bonds using SPBDU10T_S&P US Treasury Bond 7-10 Year Total Return Index.
#
# First, we pull data with the following:

# %%
bb_clean_data(
    base_directory=DATA_DIR,
    fund_ticker_name="SPBDU10T_S&P US Treasury Bond 7-10 Year Total Return Index",
    source="Bloomberg",
    asset_class="Indices",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

treas_10y = load_data(
    base_directory=DATA_DIR,
    ticker="SPBDU10T_S&P US Treasury Bond 7-10 Year Total Return Index_Clean",
    source="Bloomberg",
    asset_class="Indices",
    timeframe="Daily",
    file_format="pickle",
)

# The Bloomberg pickle stores the index as objects; convert to a nanosecond
# DatetimeIndex so it matches the FRED data in the merges further down
treas_10y.index = pd.to_datetime(treas_10y.index).astype("datetime64[ns]")

# Filter TREAS_10Y to date range
treas_10y = treas_10y[(treas_10y.index >= pd.to_datetime(START_DATE)) & (treas_10y.index <= pd.to_datetime(END_DATE))]

# Drop everything except the "close" column
treas_10y = treas_10y[["Close"]]

# Resample to monthly frequency
treas_10y_monthly = treas_10y.resample("ME").last()
treas_10y_monthly["Monthly_Return"] = treas_10y_monthly["Close"].pct_change()
treas_10y_monthly = treas_10y_monthly.dropna()

display(Markdown(f"Table {next(table_number)}: S&P US Treasury Bond 7-10 Year Total Return Index Monthly Close And Returns"))
display(treas_10y_monthly)

# %% [markdown]
# Next, we can plot the price history before calculating the cycle performance:

# %%
plot_time_series(
    df=treas_10y,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["Close"],
    title=f"Figure {next(figure_number)}: S&P US Treasury Bond 7-10 Year Total Return Index Daily Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=50,
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
    caption="Data Source: Bloomberg, Analysis by the Author",
)

# %% [markdown]
# Next, we will calculate the performance for the Treasury index based on the pre-defined Fed cycles:

# %%
treas_10y_cycles = calc_fed_cycle_asset_performance(
    start_date=cycle_ranges["adjusted_start_date"],
    end_date=cycle_ranges["end_date"],
    label=cycle_ranges["cycle_label"],
    fed_funds_change=cycle_ranges["fed_funds_change"],
    monthly_returns=treas_10y_monthly,
)

display(Markdown(f"Table {next(table_number)}: S&P US Treasury Bond 7-10 Year Total Return Index Performance By Fed Policy Cycle"))
display(treas_10y_cycles)

# %% [markdown]
# As with the S&P 500 above, this gives us the per-cycle dates, month count, cumulative and annualized returns, volatility, and the cumulative and annualized change in the FFR.
#
# From the above DataFrame, we can then plot the cumulative and annualized returns for each cycle in a bar chart. First, the cumulative returns along with the cumulative change in FFR:

# %%
plot_bar_returns_ffr_change(
    cycle_df=treas_10y_cycles,
    asset_label="TREAS_10Y",
    annualized_or_cumulative="Cumulative",
    title=f"Figure {next(figure_number)}: 7-10 Year Treasuries Cumulative Return And Cumulative Change In FFR By Fed Policy Cycle",
    caption="Data Sources: Bloomberg & FRED, Analysis by the Author",
)

# %% [markdown]
# And then the annualized returns along with the annualized change in FFR:

# %%
plot_bar_returns_ffr_change(
    cycle_df=treas_10y_cycles,
    asset_label="TREAS_10Y",
    annualized_or_cumulative="Annualized",
    title=f"Figure {next(figure_number)}: 7-10 Year Treasuries Annualized Return And Annualized Change In FFR By Fed Policy Cycle",
    caption="Data Sources: Bloomberg & FRED, Analysis by the Author",
)

# %% [markdown]
# For this dataset, we have cycles 11/12/13 exhibiting strong returns, which is consistent with the economic intuition that bonds should perform well during periods of economic weakness and rate cuts. We also see this outcome with cycle 18. It becomes a little more interesting during cycles 25 and 26, where the correlations of stocks and bond returns turned positive (historically they have been negative), so we see negative bond returns there. Finally, cycles 28/29/30 also exhibit positive bond returns, which is consistent with our thesis that bonds should perform well during periods of economic weakness and rate cuts.
#
# Finally, we can run an OLS regression to check fit:

# %%
model = run_regression(
    df=treas_10y_cycles,
    x_plot_column="FFR_AnnualizedChange_bps",
    y_plot_column="AnnualizedReturnPct",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)

print(model.summary())

# Pull the fitted coefficients by name
intercept = model.params["const"]
slope = model.params["FFR_AnnualizedChange_bps"]
print(f"Intercept: {intercept}, Slope: {slope}")

# Calc X and Y values for the regression line across the observed FFR range
X_vals = np.linspace(
    treas_10y_cycles["FFR_AnnualizedChange_bps"].min(),
    treas_10y_cycles["FFR_AnnualizedChange_bps"].max(),
    100,
)
Y_vals = intercept + slope * X_vals

# %% [markdown]
# And then plot the regression line along with the values:

# %%
plot_scatter_regression_ffr_vs_returns(
    cycle_df=treas_10y_cycles,
    asset_label="TREAS_10Y",
    x_vals=X_vals,
    y_vals=Y_vals,
    intercept=intercept,
    slope=slope,
    title=f"Figure {next(figure_number)}: 7-10 Year Treasuries Annualized Return vs Annualized Change In FFR By Fed Policy Cycle",
    caption="Data Source: Bloomberg, FRED, Analysis by the Author",
)

# %% [markdown]
# The slope here is negative, which is the sign we would expect: cycles where the FFR fell are associated with stronger Treasury returns. It is worth being honest about the strength of that relationship, though. With only 30 cycle observations the R-squared is about 0.05 and the slope is not statistically significant at any conventional threshold, so the regression is directionally consistent with the economic intuition rather than evidence for it. The bar charts above, where the sign of the return lines up with the sign of the rate change in most cycles, are the more convincing exhibit.

# %% [markdown]
# ### High Yield Bonds

# %% [markdown]
# Next, we'll run a similar process for high yield bonds using LF98TRUU_Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD.
#
# First, we pull data with the following:

# %%
bb_clean_data(
    base_directory=DATA_DIR,
    fund_ticker_name="LF98TRUU_Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD",
    source="Bloomberg",
    asset_class="Indices",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

hy_bonds = load_data(
    base_directory=DATA_DIR,
    ticker="LF98TRUU_Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD_Clean",
    source="Bloomberg",
    asset_class="Indices",
    timeframe="Daily",
    file_format="pickle",
)

# The Bloomberg pickle stores the index as objects; convert to a nanosecond
# DatetimeIndex so it matches the FRED data in the merges further down
hy_bonds.index = pd.to_datetime(hy_bonds.index).astype("datetime64[ns]")

# Filter HY_BONDS to date range
hy_bonds = hy_bonds[(hy_bonds.index >= pd.to_datetime(START_DATE)) & (hy_bonds.index <= pd.to_datetime(END_DATE))]

# Drop everything except the "close" column
hy_bonds = hy_bonds[["Close"]]

# Resample to monthly frequency
hy_bonds_monthly = hy_bonds.resample("ME").last()
hy_bonds_monthly["Monthly_Return"] = hy_bonds_monthly["Close"].pct_change()
hy_bonds_monthly = hy_bonds_monthly.dropna()

display(Markdown(f"Table {next(table_number)}: Bloomberg US Corporate High Yield Total Return Index Monthly Close And Returns"))
display(hy_bonds_monthly)

# %% [markdown]
# Next, we can plot the price history before calculating the cycle performance:

# %%
plot_time_series(
    df=hy_bonds,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["Close"],
    title=f"Figure {next(figure_number)}: Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD Daily Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=200,
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
    caption="Data Source: Bloomberg, Analysis by the Author",
)

# %% [markdown]
# Next, we will calculate the performance of high yield bonds based on the pre-defined Fed cycles:

# %%
hy_bonds_cycles = calc_fed_cycle_asset_performance(
    start_date=cycle_ranges["adjusted_start_date"],
    end_date=cycle_ranges["end_date"],
    label=cycle_ranges["cycle_label"],
    fed_funds_change=cycle_ranges["fed_funds_change"],
    monthly_returns=hy_bonds_monthly,
)

display(Markdown(f"Table {next(table_number)}: Bloomberg US Corporate High Yield Total Return Index Performance By Fed Policy Cycle"))
display(hy_bonds_cycles)

# %% [markdown]
# As with the previous data sets, this gives us the per-cycle dates, month count, cumulative and annualized returns, volatility, and the cumulative and annualized change in the FFR.
#
# From the above DataFrame, we can then plot the cumulative and annualized returns for each cycle in a bar chart. First, the cumulative returns along with the cumulative change in FFR:

# %%
plot_bar_returns_ffr_change(
    cycle_df=hy_bonds_cycles,
    asset_label="HY_BONDS",
    annualized_or_cumulative="Cumulative",
    title=f"Figure {next(figure_number)}: High Yield Bonds Cumulative Return And Cumulative Change In FFR By Fed Policy Cycle",
    caption="Data Sources: Bloomberg & FRED, Analysis by the Author",
)

# %% [markdown]
# And then the annualized returns along with the annualized change in FFR:

# %%
plot_bar_returns_ffr_change(
    cycle_df=hy_bonds_cycles,
    asset_label="HY_BONDS",
    annualized_or_cumulative="Annualized",
    title=f"Figure {next(figure_number)}: High Yield Bonds Annualized Return And Annualized Change In FFR By Fed Policy Cycle",
    caption="Data Sources: Bloomberg & FRED, Analysis by the Author",
)

# %% [markdown]
# High yield behaves like a hybrid of the two asset classes above, which is what we would expect given that it carries both duration and credit risk. The largest drawdowns line up with credit events rather than with the FFR itself. Cycle 13 (mid-to-late 2002, the WorldCom/Enron aftermath) is the worst cycle in the sample at roughly -24% annualized despite no change in the FFR at all, and cycle 11 (late 2000) is similar, but also shorter in length. The strongest cycles, 14 (late 2002 through 2003) and 2 (1990-1993), are both recoveries which do coincide with easing.
#
# Finally, we can run an OLS regression to check fit:

# %%
model = run_regression(
    df=hy_bonds_cycles,
    x_plot_column="FFR_AnnualizedChange_bps",
    y_plot_column="AnnualizedReturnPct",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)

print(model.summary())

# Pull the fitted coefficients by name
intercept = model.params["const"]
slope = model.params["FFR_AnnualizedChange_bps"]
print(f"Intercept: {intercept}, Slope: {slope}")

# Calc X and Y values for the regression line across the observed FFR range
X_vals = np.linspace(
    hy_bonds_cycles["FFR_AnnualizedChange_bps"].min(),
    hy_bonds_cycles["FFR_AnnualizedChange_bps"].max(),
    100,
)
Y_vals = intercept + slope * X_vals

# %% [markdown]
# And then plot the regression line along with the values:

# %%
plot_scatter_regression_ffr_vs_returns(
    cycle_df=hy_bonds_cycles,
    asset_label="HY_BONDS",
    x_vals=X_vals,
    y_vals=Y_vals,
    intercept=intercept,
    slope=slope,
    title=f"Figure {next(figure_number)}: High Yield Bonds Annualized Return vs Annualized Change In FFR By Fed Policy Cycle",
    caption="Data Source: Bloomberg, FRED, Analysis by the Author",
)

# %% [markdown]
# This is the weakest relationship of the four assets. The slope is slightly negative but the R-squared is effectively zero, so the annualized change in the FFR explains essentially none of the variation in high yield returns across cycles. Credit spreads, not the policy rate, are what drive this asset class.

# %% [markdown]
# ### Gold

# %% [markdown]
# Finally, we'll run a similar process for gold using XAU_Gold USD Spot.

# %%
bb_clean_data(
    base_directory=DATA_DIR,
    fund_ticker_name="XAU_Gold USD Spot",
    source="Bloomberg",
    asset_class="Commodities",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

gold = load_data(
    base_directory=DATA_DIR,
    ticker="XAU_Gold USD Spot_Clean",
    source="Bloomberg",
    asset_class="Commodities",
    timeframe="Daily",
    file_format="pickle",
)

# The Bloomberg pickle stores the index as objects; convert to a nanosecond
# DatetimeIndex so it matches the FRED data in the merges further down
gold.index = pd.to_datetime(gold.index).astype("datetime64[ns]")

# Filter GOLD to date range
gold = gold[(gold.index >= pd.to_datetime(START_DATE)) & (gold.index <= pd.to_datetime(END_DATE))]

# Drop everything except the "close" column
gold = gold[["Close"]]

# Resample to monthly frequency
gold_monthly = gold.resample("ME").last()
gold_monthly["Monthly_Return"] = gold_monthly["Close"].pct_change()
gold_monthly = gold_monthly.dropna()

display(Markdown(f"Table {next(table_number)}: Gold Spot Price Monthly Close And Returns"))
display(gold_monthly)

# %% [markdown]
# Next, we can plot the price history before calculating the cycle performance:

# %%
plot_time_series(
    df=gold,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["Close"],
    title=f"Figure {next(figure_number)}: XAU Gold USD Spot Daily Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=400,
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
    caption="Data Source: Bloomberg, Analysis by the Author",
)

# %% [markdown]
# Finally, we will calculate the performance of gold based on the pre-defined Fed cycles:

# %%
gold_cycles = calc_fed_cycle_asset_performance(
    start_date=cycle_ranges["adjusted_start_date"],
    end_date=cycle_ranges["end_date"],
    label=cycle_ranges["cycle_label"],
    fed_funds_change=cycle_ranges["fed_funds_change"],
    monthly_returns=gold_monthly,
)

display(Markdown(f"Table {next(table_number)}: Gold Spot Price Performance By Fed Policy Cycle"))
display(gold_cycles)

# %% [markdown]
# As with the previous asset classes, this gives us the per-cycle dates, month count, cumulative and annualized returns, volatility, and the cumulative and annualized change in the FFR.
#
# From the above DataFrame, we can then plot the cumulative and annualized returns for each cycle in a bar chart. First, the cumulative returns along with the cumulative change in FFR:

# %%
plot_bar_returns_ffr_change(
    cycle_df=gold_cycles,
    asset_label="GOLD",
    annualized_or_cumulative="Cumulative",
    title=f"Figure {next(figure_number)}: Gold Cumulative Return And Cumulative Change In FFR By Fed Policy Cycle",
    caption="Data Sources: Bloomberg & FRED, Analysis by the Author",
)

# %% [markdown]
# And then the annualized returns along with the annualized change in FFR:

# %%
plot_bar_returns_ffr_change(
    cycle_df=gold_cycles,
    asset_label="GOLD",
    annualized_or_cumulative="Annualized",
    title=f"Figure {next(figure_number)}: Gold Annualized Return And Annualized Change In FFR By Fed Policy Cycle",
    caption="Data Sources: Bloomberg & FRED, Analysis by the Author",
)

# %% [markdown]
# We see strong returns for gold across several different Fed cycles, so it is difficult to draw any kind of initial conclusion based on the bar charts. We see rate cuts in cycle 2, without a corresponding strong performance in gold, but cycles 14, 18, and 24 all have strong gold performance coinciding with easing.
#
# Finally, we can run an OLS regression to check fit:

# %%
model = run_regression(
    df=gold_cycles,
    x_plot_column="FFR_AnnualizedChange_bps",
    y_plot_column="AnnualizedReturnPct",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)

print(model.summary())

# Pull the fitted coefficients by name
intercept = model.params["const"]
slope = model.params["FFR_AnnualizedChange_bps"]
print(f"Intercept: {intercept}, Slope: {slope}")

# Calc X and Y values for the regression line across the observed FFR range
X_vals = np.linspace(
    gold_cycles["FFR_AnnualizedChange_bps"].min(),
    gold_cycles["FFR_AnnualizedChange_bps"].max(),
    100,
)
Y_vals = intercept + slope * X_vals

# %% [markdown]
# And then plot the regression line along with the values:

# %%
plot_scatter_regression_ffr_vs_returns(
    cycle_df=gold_cycles,
    asset_label="GOLD",
    x_vals=X_vals,
    y_vals=Y_vals,
    intercept=intercept,
    slope=slope,
    title=f"Figure {next(figure_number)}: Gold Annualized Return vs Annualized Change In FFR By Fed Policy Cycle",
    caption="Data Source: Bloomberg, FRED, Analysis by the Author",
)

# %% [markdown]
# It's difficult to draw any strong conclusions with the above plot. Gold has traditionally been considered a hedge for inflation, and while one of the Fed's mandates is to manage inflation, there may not be a conclusion to draw in relationship to the historical returns that gold has exhibited.

# %% [markdown]
# ## Asset Allocation

# %% [markdown]
# With the above analysis complete, let's look at how a portfolio would have allocated based on the data, and at the hypothetical historical results.
#
# We will restrict the strategy to stocks and Treasuries. High yield showed essentially no relationship to the FFR (its R-squared was near zero, and its worst cycles were credit events that happened during flat-rate periods), and gold's relationship was weak enough that any rule built on it would be curve-fitting rather than economics.
#
# We also have to be careful with our criteria for when to hold stocks versus bonds, as hindsight bias is certainly possible. So, without overanalyzing the results:
#
# > **Let's assume that we hold stocks as the default position during tightening cycles, hold bonds during easing cycles when the Fed starts cutting rates, and resume holding stocks when the Fed stops cutting rates.**
#
# Let's consider the `Extended Neutral` bucket. Assigning those months to stocks is not a neutral decision, because it covers 37% of the sample, and because it covers 2009-2015 and 2020-2021 it gives the strategy the two strongest equity runs in the record. As we will see below, that single bucket is the largest contributor to the strategy's total return.
#
# We also have to be careful about *when* we are allowed to act on the signal. This is a similar discussion to matching the timing of economic data releases with the cycle labels, but we found that we could act on the 1st of the month following an FOMC decision, so we could use that following month's return.

# %%
fedfunds_grouped_cycles['cycle_invested'] = fedfunds_grouped_cycles['cycle_filled']

display(Markdown(f"Table {next(table_number)}: Monthly Cycle Labels With Implementation"))
display(fedfunds_grouped_cycles.head(50))

# %% [markdown]
# Now, we can merge the monthly returns for each asset class with the group, based on cycle invested.

# %%
# Reset index to merge on date
stocks_merged = pd.merge_asof(
    spxt_monthly.reset_index(),
    fedfunds_grouped_cycles[['start_date', 'end_date', 'cycle_invested', 'group']].dropna(),
    left_on='Date',
    right_on='end_date',
    direction='backward'
)

# Drop rows where the date falls outside the cycle's end_date
stocks_merged = stocks_merged[stocks_merged['Date'] <= stocks_merged['end_date']]
stocks_merged = stocks_merged[["Date", "Monthly_Return", "cycle_invested", "group"]]

display(Markdown(f"Table {next(table_number)}: SPXT Monthly Returns Merged With Cycle Labels"))
display(stocks_merged.head(15))

# %%
# Reset index to merge on date
bonds_merged = pd.merge_asof(
    treas_10y_monthly.reset_index(),
    fedfunds_grouped_cycles[['start_date', 'end_date', 'cycle_invested', 'group']].dropna(),
    left_on='Date',
    right_on='end_date',
    direction='backward'
)

# Drop rows where the date falls outside the cycle's end_date
bonds_merged = bonds_merged[bonds_merged['Date'] <= bonds_merged['end_date']]
bonds_merged = bonds_merged[["Date", "Monthly_Return", "cycle_invested", "group"]]

display(Markdown(f"Table {next(table_number)}: 10Y Treasury Monthly Returns Merged With Cycle Labels"))
display(bonds_merged.head(15))

# %% [markdown]
# And then compress the monthly returns for each cycle together to calculate the cumulative return.

# %%
# Select the appropriate return based on cycle
stocks_merged['strategy_return'] = stocks_merged.apply(
    lambda row: row['Monthly_Return'] if row['cycle_invested'] in ['Tightening', 'Extended Neutral'] else None,
    axis=1
)

bonds_merged['strategy_return'] = bonds_merged.apply(
    lambda row: row['Monthly_Return'] if row['cycle_invested'] == 'Easing' else None,
    axis=1
)

# Combine
strategy = pd.concat([stocks_merged, bonds_merged]).dropna(subset=['strategy_return'])
strategy = strategy.sort_values('Date')

display(Markdown(f"Table {next(table_number)}: Strategy Monthly Returns, First 20 Months"))
display(strategy.head(20))

# %%
# Calculate cumulative returns and drawdown for spxt
spxt_monthly['Cumulative_Return'] = (1 + spxt_monthly['Monthly_Return']).cumprod() - 1
spxt_monthly['Cumulative_Return_Plus_One'] = 1 + spxt_monthly['Cumulative_Return']
spxt_monthly['Rolling_Max'] = spxt_monthly['Cumulative_Return_Plus_One'].cummax()
spxt_monthly['Drawdown'] = spxt_monthly['Cumulative_Return_Plus_One'] / spxt_monthly['Rolling_Max'] - 1
spxt_monthly.drop(columns=['Cumulative_Return_Plus_One', 'Rolling_Max'], inplace=True)

# Calculate cumulative returns and drawdown for treas_10y
treas_10y_monthly['Cumulative_Return'] = (1 + treas_10y_monthly['Monthly_Return']).cumprod() - 1
treas_10y_monthly['Cumulative_Return_Plus_One'] = 1 + treas_10y_monthly['Cumulative_Return']
treas_10y_monthly['Rolling_Max'] = treas_10y_monthly['Cumulative_Return_Plus_One'].cummax()
treas_10y_monthly['Drawdown'] = treas_10y_monthly['Cumulative_Return_Plus_One'] / treas_10y_monthly['Rolling_Max'] - 1
treas_10y_monthly.drop(columns=['Cumulative_Return_Plus_One', 'Rolling_Max'], inplace=True)

# Convert to DataFrame
portfolio_monthly = strategy[['Date', 'strategy_return']].copy().set_index('Date')
portfolio_monthly = portfolio_monthly.rename(columns={'strategy_return': 'Portfolio_Monthly_Return'})

# Calculate cumulative returns and drawdown for the portfolio
portfolio_monthly['Portfolio_Cumulative_Return'] = (1 + portfolio_monthly['Portfolio_Monthly_Return']).cumprod() - 1
portfolio_monthly['Portfolio_Cumulative_Return_Plus_One'] = 1 + portfolio_monthly['Portfolio_Cumulative_Return']
portfolio_monthly['Portfolio_Rolling_Max'] = portfolio_monthly['Portfolio_Cumulative_Return_Plus_One'].cummax()
portfolio_monthly['Portfolio_Drawdown'] = portfolio_monthly['Portfolio_Cumulative_Return_Plus_One'] / portfolio_monthly['Portfolio_Rolling_Max'] - 1
portfolio_monthly.drop(columns=['Portfolio_Cumulative_Return_Plus_One', 'Portfolio_Rolling_Max'], inplace=True)

# Merge "spxt_monthly" and "treas_10y_monthly" into "portfolio_monthly" to compare cumulative returns
portfolio_monthly = portfolio_monthly.join(
    spxt_monthly['Monthly_Return'].rename('SPXT_Monthly_Return'),
    how='left'
).join(
    spxt_monthly['Cumulative_Return'].rename('SPXT_Cumulative_Return'),
    how='left'
).join(
    spxt_monthly['Drawdown'].rename('SPXT_Drawdown'),
    how='left'
).join(
    treas_10y_monthly['Monthly_Return'].rename('10Y_Monthly_Return'),
    how='left'
).join(
    treas_10y_monthly['Cumulative_Return'].rename('10Y_Cumulative_Return'),
    how='left'
).join(
    treas_10y_monthly['Drawdown'].rename('10Y_Drawdown'),
    how='left'
)

display(Markdown(f"Table {next(table_number)}: Portfolio, SPXT, And 10Y Monthly Returns, Cumulative Returns, And Drawdowns"))
display(portfolio_monthly)

# %% [markdown]
# Next, we'll look at performance for the assets and portfolio.

# %% [markdown]
# ## Performance Statistics

# %% [markdown]
# We can then plot the monthly returns:

# %%
plot_time_series(
    df=portfolio_monthly,
    plot_start_date=START_DATE,
    plot_end_date=END_DATE,
    plot_columns=["Portfolio_Monthly_Return", "SPXT_Monthly_Return", "10Y_Monthly_Return"],
    title=f"Figure {next(figure_number)}: Portfolio, SPXT, and 10Y Monthly Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Return",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing=0.02,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
    caption="Data Source: Bloomberg, Analysis by the Author",
)

# %% [markdown]
# And cumulative returns:

# %%
plot_time_series(
    df=portfolio_monthly,
    plot_start_date=START_DATE,
    plot_end_date=END_DATE,
    plot_columns=["Portfolio_Cumulative_Return", "SPXT_Cumulative_Return", "10Y_Cumulative_Return"],
    title=f"Figure {next(figure_number)}: Portfolio, SPXT, and 10Y Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=3,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
    caption="Data Source: Bloomberg, Analysis by the Author",
)

# %% [markdown]
# And drawdowns:

# %%
plot_time_series(
    df=portfolio_monthly,
    plot_start_date=START_DATE,
    plot_end_date=END_DATE,
    plot_columns=["Portfolio_Drawdown", "SPXT_Drawdown", "10Y_Drawdown"],
    title=f"Figure {next(figure_number)}: Portfolio, SPXT, and 10Y Drawdowns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Drawdown (%)",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing=0.05,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
    caption="Data Source: Bloomberg, Analysis by the Author",
)

# %% [markdown]
# Finally, we can run the summary statistics on the strategy portfolio, SPXT, and the 7-10 year Treasury index with the following code:

# %%
port_sum_stats = summary_stats(
    fund_list=["Portfolio"],
    df=portfolio_monthly[["Portfolio_Monthly_Return"]],
    period="Monthly",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

spxt_sum_stats = summary_stats(
    fund_list=["SPXT"],
    df=portfolio_monthly[["SPXT_Monthly_Return"]],
    period="Monthly",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

t10y_sum_stats = summary_stats(
    fund_list=["10Y"],
    df=portfolio_monthly[["10Y_Monthly_Return"]],
    period="Monthly",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([port_sum_stats, spxt_sum_stats, t10y_sum_stats])
display(Markdown(f"Table {next(table_number)}: Summary Statistics, Portfolio, SPXT, And 10Y"))
display(sum_stats)

# %% [markdown]
# Based on the above, the strategy portfolio earns a higher annualized return than either stocks or bonds on their own, and it cuts the worst equity drawdown roughly in half by being in Treasuries through the 2008 and 2020 declines.

# %% [markdown]
# ## Conclusion

# %% [markdown]
# This was an interesting exercise to evaluate the performance of different asset classes during Fed tightening and easing cycles. The bar charts line up with the economic intuition reasonably well. Stocks tend to do better through tightening cycles (economic strength) and Treasuries through easing cycles (economic weakness).
#
# The regressions tell a different story, however. Across all four assets, the annualized change in the FFR explains almost none of the cross-cycle variation in returns. R-squared values run from roughly 0.004 for high yield to 0.06 for gold, and not one of the four slopes is statistically significant with 30 cycle observations. The scatter plots look suggestive, but while they are not evidence that the FFR drives returns, it does appear that that policy direction is *associated* with which asset does better.

# %%
for cycle in ["Extended Neutral", "Tightening", "Easing"]:
    cum_return = (1 + strategy[strategy["cycle_invested"] == cycle]["Monthly_Return"]).cumprod() - 1
    print(f"Cumulative return for {cycle}: {cum_return.iloc[-1]:.2%} ")

# %% [markdown]
# On paper the backtest looks successful, but the caveats matter significantly. The largest caveat (as mentioned above) is the 37% of the sample that falls into the `Extended Neutral` bucket, and the choice to hold equities through those months. This contributes more to the strategy's total return than either the tightening or easing bucket. The strategy is effectively a long-equity position, with a Treasury hedge during cutting cycles. The signal carries a one-month implementation lag so it uses only completed rate changes, but it still assumes we correctly classify cycles as they happen in real time.
#
# The strategy has done well post-GFC, but the period from 2008 to the present has been marked by historically low interest rates and a strong bull market in stocks, which may not be representative of future market conditions given current valuations (present time August 2026). Additionally, the current rate cutting cycle (cycles 28/29/30) is still ongoing, and it remains to be seen how the strategy will perform during this cycle and the ones that follow.

# %% [markdown]
# ## Future Investigation

# %% [markdown]
# A couple of ideas sound intriguing for future investigation:
#
# * Does a commodity index (such as GSCI) exhibit differing behavior than gold?
# * How does leverage affect the returns that are observed for the strategy portfolio, stocks, and bonds?
# * Do other Fed tightening/easing cycles exhibit the same behavior for returns?
# * How sensitive is the strategy to the 6 month forward fill limit and to the choice to hold equities during `Extended Neutral` months? Sweeping both would show how much of the result is the policy signal and how much is the default long-equity stance.

# %% [markdown]
# ## References

# %% [markdown]
# 1. https://fred.stlouisfed.org/series/DFEDTARU
# 2. https://fred.stlouisfed.org/series/DFEDTARL
# 3. https://fred.stlouisfed.org/series/DFEDTAR

