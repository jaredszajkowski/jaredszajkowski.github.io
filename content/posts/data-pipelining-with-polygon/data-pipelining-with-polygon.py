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
#     display_name: jaredszajkowski-github-io (3.14.10)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Post Updates

# %% [markdown]
# Update 11/6/2026: Merged `polygon_fetch_full_history` and `polygon_pull_data` into a single module, `polygon_pull_equity_data`, and renamed `polygon_pull_data` to `polygon_pull_equity_data`. The pull now also fetches Massive's dividend adjustment factors and applies them to the split-adjusted prices, adding `adj_open`, `adj_high`, `adj_low`, `adj_close`, and `adj_vwap` columns. That was the one item under Future Investigation, so that section is gone, and a new section below covers the dividend adjustment. Also folded `polygon_month_end` and `polygon_quarter_end` into the same module as a single function, `polygon_resample_period_end`, which takes a `period` argument of either `month` or `quarter`. Switched the examples from AMZN to AAPL, since AMZN doesn't pay a dividend and AAPL shows the adjustment at work.
#
# Update 8/6/2026: Brought the post back in line with the current source. Polygon.io has rebranded to Massive and the Python client is now imported as `massive`, `polygon_pull_data` gained a `parquet_export` parameter and returns the resulting DataFrame, and `polygon_fetch_full_history` renamed its `full_history_df` parameter to `existing_history_df`. Replaced the reproduced docstrings with prose descriptions, added the free tier constraints that shape the design, and documented the on-disk layout the data lands in.

# %% [markdown]
# ## Introduction

# %% [markdown]
# Where the [previous post on collecting crypto asset data from Coinbase](/posts/data-pipelining-with-coinbase/) covered digital assets, this one covers the equity side. The two functions below pull minute, hour, and daily bars for equities and ETFs from Polygon.io, since rebranded as [Massive](https://massive.com).
#
# Two constraints from the free tier drive most of the design. The first is a two year limit on historical data, which is why the examples below start from a date two years back rather than attempting to pull an asset's full history. The second is a rate limit of five API requests per minute, which is what the `free_tier` flag handles. When using the free tier, the fetch pauses for twelve seconds between requests. A single API call also returns at most 5,000 records, so any meaningful date range has to be walked through in chunks and reassembled.
#
# The work lives in a single module, `polygon_pull_equity_data`, and is split across functions that build on one another. `polygon_fetch_full_history` walks a date range and returns it as a single dataframe. `polygon_pull_equity_data` wraps that to maintain pickle, Excel, and Parquet files on disk, extending an existing record with the rows it is missing, or creating a new record where none exists. It also adds dividend-adjusted prices, using two helpers in the same module: `polygon_fetch_dividend_factors` and `apply_dividend_adjustment`.

# %% [markdown]
# ## Python Imports

# %%
# Standard Library
import os
import sys
import time
import warnings

from datetime import datetime
from pathlib import Path

# Data Handling
import pandas as pd

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
# Here are the modules needed for this project:
#
# * [polygon_pull_equity_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#polygon_pull_equity_data): Read existing data file, download price data from Polygon, apply dividend adjustment factors, and export data. The module also holds the helpers `polygon_fetch_full_history`, `polygon_fetch_dividend_factors`, and `apply_dividend_adjustment`.
# * [polygon_resample_period_end](/posts/reusable-extensible-python-functions-financial-data-analysis/#polygon_resample_period_end): Resample the daily data on disk to month-end or quarter-end closes.

# %%
from polygon_pull_equity_data import (
    polygon_fetch_full_history,
    polygon_pull_equity_data,
)
from polygon_resample_period_end import polygon_resample_period_end

# %% [markdown]
# One naming note before the code: Polygon.io has rebranded to Massive, and the official Python client followed. The package is now [`massive`](https://pypi.org/project/massive/) rather than `polygon-api-client`, so the import below reads `from massive import RESTClient`. The API surface is otherwise unchanged, and I've kept "Polygon" in the function names and directory layout since that's what the existing data is filed under.

# %% [markdown]
# ## Function Usage

# %% [markdown]
# Both examples below use daily bars, but switching to minute or hour data is a matter of changing the `timespan` and `multiplier` arguments, with everything else unchanged. Note that finer granularity burns through the free tier rate limit considerably faster, since each request covers a much shorter window. Massive aggregates minute data into hour bars, so the time to pull minute and hour data is actually the same. Both functions accept only `minute`, `hour`, or `day` for `timespan` and raise an exception otherwise, since the window sizing logic is only defined for those three.

# %% [markdown]
# ### Polygon Fetch Full History

# %% [markdown]
# This is the lower level of the two functions. Starting from `current_start`, it walks forward through the date range in fixed size windows - 180 days for daily data, 15 days for minute and hour data - requests each window from the API, and appends the results to the dataframe passed in as `existing_history_df`, stopping once it reaches the present. Because each request is capped at 5,000 records, ranges spanning years are handled the same way as the single window below: the individual responses are concatenated and returned as one dataframe.
#
# The API key is read through `config`, which merges everything in the `.env` file into the settings defaults, so `config("POLYGON_KEY")` resolves without any further setup:

# %%
from massive import RESTClient

# Load API key from the environment variables
POLYGON_KEY = config("POLYGON_KEY")

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Open client connection
client = RESTClient(api_key=POLYGON_KEY)

# Create an empty DataFrame
df = pd.DataFrame({
    'Date': pd.Series(dtype="datetime64[ns]"),
    'open': pd.Series(dtype="float64"),
    'high': pd.Series(dtype="float64"),
    'low': pd.Series(dtype="float64"),
    'close': pd.Series(dtype="float64"),
    'volume': pd.Series(dtype="float64"),
    'vwap': pd.Series(dtype="float64"),
    'transactions': pd.Series(dtype="int64"),
    'otc': pd.Series(dtype="object")
})

# Example usage - daily
df = polygon_fetch_full_history(
    client=client,
    ticker="AAPL",
    timespan="day",
    multiplier=1,
    adjusted=True,
    existing_history_df=df,
    current_start=datetime(2025, 1, 1),
    free_tier=True,
    verbose=False,
)

time.sleep(12)  # Sleep for 12 seconds to avoid hitting rate limits

# %% [markdown]
# The example above pulls daily data starting from 1/1/2025. Here are the first five rows:

# %%
display(df.head())

# %% [markdown]
# ### Polygon Pull Equity Data

# %% [markdown]
# This function wraps the one above and performs the following:
#
# 1. Attempt to read an existing pickle data file.
# 2. If a data file exists, then pull updated data starting from the last date on record.
# 3. Otherwise, pull all historical data available for that asset for the past 2 years (or chosen interval).
# 4. If `adjusted` is set, pull the dividend adjustment factors and add the `adj_open`, `adj_high`, `adj_low`, `adj_close`, and `adj_vwap` columns (covered in the next section).
# 5. Store Pickle, Excel, and/or Parquet files of the data in the specified directories.
# 6. Return the resulting dataframe.
#
# Setting `force_existing_check` re-pulls the entire range rather than starting from the last date on record, which is how gaps in an existing file get filled.

# %% [markdown]
# The `base_directory`, `source`, `asset_class`, and `timespan` arguments together tell the function where in the local filesystem to look for an existing pickle file, and where to store the updated exports. They assemble into a path of the form `{base_directory}/{source}/{asset_class}/{timespan}/{ticker}`, so the example below reads and writes:
#
# ```text
# Data/Polygon/Equities/day/AAPL.pkl
# Data/Polygon/Equities/day/AAPL.xlsx
# Data/Polygon/Equities/day/AAPL.parquet
# ```
#
# Keeping the timespan in the path means minute, hour, and daily records for the same ticker sit side by side without overwriting one another.

# %%
current_year = datetime.now().year
current_month = datetime.now().month
current_day = datetime.now().day

# Example usage - daily
df = polygon_pull_equity_data(
    base_directory=DATA_DIR,
    ticker="AAPL",
    source="Polygon",
    asset_class="Equities",
    start_date=datetime(current_year - 2, current_month, current_day),
    timespan="day",
    multiplier=1,
    adjusted=True,
    force_existing_check=True,
    free_tier=True,
    verbose=False,
    excel_export=True,
    pickle_export=True,
    parquet_export=True,
    output_confirmation=True,
)

time.sleep(12)  # Sleep for 12 seconds to avoid hitting rate limits

# %% [markdown]
# And here are the first five rows of the returned dataframe:

# %%
display(df.head())

# %% [markdown]
# Note that `Date` is returned as a regular column with a plain integer index rather than as the index itself. That is deliberate, and any downstream analysis can call `set_index("Date")` as needed.

# %% [markdown]
# ### Dividend Adjustment

# %% [markdown]
# Setting `adjusted=True` makes the API adjust the bars for splits, but not for dividends. To get total return prices, `polygon_pull_equity_data` makes one more request, to Massive's dividends endpoint (`client.list_stocks_dividends`). Each dividend record there carries a `historical_adjustment_factor`, and Massive documents how to use it: for a price on date D, find the first dividend whose ex-dividend date falls after D, and multiply the price by that dividend's factor. The factors are already cumulative, so no running product is needed, and bars on or after the most recent ex-dividend date get a factor of 1.
#
# `apply_dividend_adjustment` does this lookup with a forward `merge_asof` and multiplies the split-adjusted open, high, low, close, and VWAP by the result to create `adj_open`, `adj_high`, `adj_low`, `adj_close`, and `adj_vwap`. A few details are worth noting:
#
# * Every new dividend changes the factor for all of the history before it, so the adjusted columns are recomputed over the full record on every run rather than only for the newly appended rows.
# * Volume gets no dividend adjustment. A cash dividend doesn't change the number of shares outstanding or traded, so only the split adjustment the API already applies is needed.
# * The timestamps are in UTC, so each bar is first mapped to its trading date in US/Eastern time. Otherwise an after-hours minute or hour bar, which falls after midnight UTC, would be counted as part of the next session.
#
# If `adjusted=False`, the prices aren't split-adjusted, so applying the factors would be wrong across any split. In that case the function skips the adjusted columns and prints a note saying so.
#
# Here is the ratio of `adj_close` to `close` on the last bar before each recent ex-dividend date, which is where the factor steps up:

# %%
ratio = (df["adj_close"] / df["close"]).round(6)
display(df.loc[ratio.ne(ratio.shift(-1)), ["Date", "close", "adj_close"]].assign(factor=ratio).tail(8))

# %% [markdown]
# ### Polygon Resample Period End

# %% [markdown]
# Monthly and quarterly analysis doesn't need daily bars, so this function makes a lower-frequency copy of a record already on disk. It makes no API calls. It reads the existing pickle file, keeps `close` (plus `adj_close` when the file has it), and takes the last value in each month or quarter. The `period` argument chooses between the two: `month` resamples to month-end and `quarter` resamples to quarter-end. Any other value raises an exception.
#
# The other arguments work the same as above, with `timespan` naming the record to read. The results go in their own directories alongside the daily data, so the two examples below write:
#
# ```text
# Data/Polygon/Equities/Month_End/AAPL_ME.pkl
# Data/Polygon/Equities/Month_End/AAPL_ME.xlsx
# Data/Polygon/Equities/Month_End/AAPL_ME.parquet
# Data/Polygon/Equities/Quarter_End/AAPL_QE.pkl
# Data/Polygon/Equities/Quarter_End/AAPL_QE.xlsx
# Data/Polygon/Equities/Quarter_End/AAPL_QE.parquet
# ```

# %%
# Example usage - month end
df_month_end = polygon_resample_period_end(
    base_directory=DATA_DIR,
    ticker="AAPL",
    source="Polygon",
    asset_class="Equities",
    timespan="day",
    period="month",
    excel_export=True,
    pickle_export=True,
    parquet_export=True,
    output_confirmation=True,
)

# Example usage - quarter end
df_quarter_end = polygon_resample_period_end(
    base_directory=DATA_DIR,
    ticker="AAPL",
    source="Polygon",
    asset_class="Equities",
    timespan="day",
    period="quarter",
    excel_export=True,
    pickle_export=True,
    parquet_export=True,
    output_confirmation=True,
)

# %% [markdown]
# Unlike the daily data, the result is indexed by the period-end date. Here are the last five month-end rows:

# %%
display(df_month_end.tail())

# %% [markdown]
# And the last five quarter-end rows:

# %%
display(df_quarter_end.tail())

# %% [markdown]
# ## References

# %% [markdown]
# 1. [Massive (formerly Polygon.io)](https://massive.com)
# 2. [Massive REST API quickstart](https://massive.com/docs/rest/quickstart)
# 3. [massive on PyPI](https://pypi.org/project/massive/)
# 4. [massive-com/client-python on GitHub](https://github.com/massive-com/client-python)
# 5. [Reusable & Extensible Python Functions For Financial Data Analysis](/posts/reusable-extensible-python-functions-financial-data-analysis/)
