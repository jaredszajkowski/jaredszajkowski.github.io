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
#     display_name: general-venv-p313 (3.13.11)
#     language: python
#     name: python3
# ---
# %% [markdown]
# ## Introduction

# %% [markdown]
# This post intends to provide the code for all of the python functions that I use in my analysis. The goal here is that when writing another post I will simply be able to link to the functions below as opposed to providing the function code in each post.

# %% [markdown]
# ## Python Imports

# %%
# Standard Library
import os
import re
import sys
import warnings

from pathlib import Path

# Python Modules
from IPython.display import Markdown, display

# Suppress warnings
warnings.filterwarnings("ignore")

# %% [markdown]
# ## Add Directories To Path

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

# %% [markdown]
# ## Function Index

# %% [markdown]
# * [backtest_target_weight_portfolio](/posts/reusable-extensible-python-functions-financial-data-analysis/#backtest_target_weight_portfolio): Backtest a portfolio that periodically rebalances toward a set of target weights.
# * [bb_clean_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#bb_clean_data): Takes an Excel export from Bloomberg, removes the miscellaneous headings/rows, and returns a DataFrame.
# * [build_index](/posts/reusable-extensible-python-functions-financial-data-analysis/#build_index): Reads the `index_temp.md` markdown file, inserts the markdown dependencies where indicated, and then saves the file as `index.md`.
# * [calc_fed_cycle_asset_performance](/posts/reusable-extensible-python-functions-financial-data-analysis/#calc_fed_cycle_asset_performance): Calculates metrics for an asset based on a specified Fed tightening/easing cycle.
# * [calc_vix_trade_pnl](/posts/reusable-extensible-python-functions-financial-data-analysis/#calc_vix_trade_pnl): Calculates the profit/loss from VIX options trades.
# * [coinbase_fetch_available_products](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_available_products): Fetch available products from Coinbase Exchange API.
# * [coinbase_fetch_full_history](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_full_history): Fetch full historical data for a given product from Coinbase Exchange API.
# * [coinbase_fetch_historical_candles](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_historical_candles): Fetch historical candle data for a given product from Coinbase Exchange API.
# * [coinbase_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_pull_data): Update existing record or pull full historical data for a given product from Coinbase Exchange API.
# * [create_ma_trend_signals](/posts/reusable-extensible-python-functions-financial-data-analysis/#create_ma_trend_signals): Generate multi-asset trend following target weights from a grid of moving averages.
# * [df_info](/posts/reusable-extensible-python-functions-financial-data-analysis/#df_info): A simple function to display the information about a DataFrame and the first five rows and last five rows.
# * [df_info_markdown](/posts/reusable-extensible-python-functions-financial-data-analysis/#df_info_markdown): Similar to the `df_info` function above, except that it coverts the output to markdown.
# * [export_track_md_deps](/posts/reusable-extensible-python-functions-financial-data-analysis/#export_track_md_deps): Exports various text outputs to markdown files, which are included in the `index.md` file created when building the site with Hugo.
# * [load_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.
# * [pandas_set_decimal_places](/posts/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.
# * [plot_bar_returns_ffr_change](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_bar_returns_ffr_change): Plot the bar chart of the cumulative or annualized returns for the asset class along with the change in the Fed Funds Rate.
# * [plot_histogram](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_histogram): Plot the histogram of a data set from a DataFrame.
# * [plot_scatter](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter): Plot the data from a DataFrame for a specified date range and columns.
# * [plot_scatter_regression_ffr_vs_returns](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter_regression_ffr_vs_returns): Plot a scatter plot of annualized returns vs annualized change in Fed Funds Rate, with a regression line and annotations for each policy cycle.
# * [plot_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_stats): Generate a scatter plot for the mean OHLC prices.
# * [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the time series data from a DataFrame for a specified date range and columns.
# * [plot_vix_with_trades](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_vix_with_trades): Plot the VIX daily high and low prices, along with the VIX spikes, and trades.
# * [polygon_fetch_full_history](/posts/reusable-extensible-python-functions-financial-data-analysis/#polygon_fetch_full_history): Fetch full historical data for a given product from Polygon API.
# * [polygon_fetch_ticker_details](/posts/reusable-extensible-python-functions-financial-data-analysis/#polygon_fetch_ticker_details): Fetch detailed information for a given product from Polygon API.
# * [polygon_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#polygon_pull_data): Read existing data file, download price data from Polygon, and export data.
# * [run_regression](/posts/reusable-extensible-python-functions-financial-data-analysis/#run_regression): Run a regression using a variety of different methods and return the results.
# * [strategy_harry_brown_perm_port](/posts/reusable-extensible-python-functions-financial-data-analysis/#strategy_harry_brown_perm_port): Execute the strategy for the Harry Brown permanent portfolio.
# * [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.
# * [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.

# %% [markdown]
# ## Python Functions

# %% tags=["remove_input"]
def display_source(module_name: str) -> None:
    """Render the full contents of src/<module_name>.py as a python code block."""
    code = (Path(SOURCE_DIR) / f"{module_name}.py").read_text().strip()
    # Use a fence longer than any backtick run inside the source
    longest = max((len(run) for run in re.findall(r"`+", code)), default=0)
    fence = "`" * max(3, longest + 1)
    display(Markdown(f"{fence}python\n{code}\n{fence}"))

# %% [markdown]
# ### backtest_target_weight_portfolio

# %% tags=["remove_input"]
display_source("backtest_target_weight_portfolio")

# %% [markdown]
# ### bb_clean_data

# %% tags=["remove_input"]
display_source("bb_clean_data")

# %% [markdown]
# ### build_index

# %% tags=["remove_input"]
display_source("build_index")

# %% [markdown]
# ### calc_fed_cycle_asset_performance

# %% tags=["remove_input"]
display_source("calc_fed_cycle_asset_performance")

# %% [markdown]
# ### calc_vix_trade_pnl

# %% tags=["remove_input"]
display_source("calc_vix_trade_pnl")

# %% [markdown]
# ### coinbase_fetch_available_products

# %% tags=["remove_input"]
display_source("coinbase_fetch_available_products")

# %% [markdown]
# ### coinbase_fetch_full_history

# %% tags=["remove_input"]
display_source("coinbase_fetch_full_history")

# %% [markdown]
# ### coinbase_fetch_historical_candles

# %% tags=["remove_input"]
display_source("coinbase_fetch_historical_candles")

# %% [markdown]
# ### coinbase_pull_data

# %% tags=["remove_input"]
display_source("coinbase_pull_data")

# %% [markdown]
# ### create_ma_trend_signals

# %% tags=["remove_input"]
display_source("create_ma_trend_signals")

# %% [markdown]
# ### df_info

# %% tags=["remove_input"]
display_source("df_info")

# %% [markdown]
# ### df_info_markdown

# %% tags=["remove_input"]
display_source("df_info_markdown")

# %% [markdown]
# ### export_track_md_deps

# %% tags=["remove_input"]
display_source("export_track_md_deps")

# %% [markdown]
# ### load_data

# %% tags=["remove_input"]
display_source("load_data")

# %% [markdown]
# ### pandas_set_decimal_places

# %% tags=["remove_input"]
display_source("pandas_set_decimal_places")

# %% [markdown]
# ### plot_bar_returns_ffr_change

# %% tags=["remove_input"]
display_source("plot_bar_returns_ffr_change")

# %% [markdown]
# ### plot_histogram

# %% tags=["remove_input"]
display_source("plot_histogram")

# %% [markdown]
# ### plot_scatter

# %% tags=["remove_input"]
display_source("plot_scatter")

# %% [markdown]
# ### plot_scatter_regression_ffr_vs_returns

# %% tags=["remove_input"]
display_source("plot_scatter_regression_ffr_vs_returns")

# %% [markdown]
# ### plot_stats

# %% tags=["remove_input"]
display_source("plot_stats")

# %% [markdown]
# ### plot_time_series

# %% tags=["remove_input"]
display_source("plot_time_series")

# %% [markdown]
# ### plot_vix_with_trades

# %% tags=["remove_input"]
display_source("plot_vix_with_trades")

# %% [markdown]
# ### polygon_fetch_full_history

# %% tags=["remove_input"]
display_source("polygon_fetch_full_history")

# %% [markdown]
# ### polygon_fetch_ticker_details

# %% tags=["remove_input"]
display_source("polygon_fetch_ticker_details")

# %% [markdown]
# ### polygon_pull_data

# %% tags=["remove_input"]
display_source("polygon_pull_data")

# %% [markdown]
# ### run_regression

# %% tags=["remove_input"]
display_source("run_regression")

# %% [markdown]
# ### strategy_harry_brown_perm_port

# %% tags=["remove_input"]
display_source("strategy_harry_brown_perm_port")

# %% [markdown]
# ### summary_stats

# %% tags=["remove_input"]
display_source("summary_stats")

# %% [markdown]
# ### yf_pull_data

# %% tags=["remove_input"]
display_source("yf_pull_data")

# %% [markdown]
# ## References

# %% [markdown]
# None
