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
#     display_name: general-venv-p313 (3.13.17)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Post Updates

# %% [markdown]
# Update 8/6/2026: Brought the post back in line with the current source. Polygon.io has rebranded to Massive and the Python client is now imported as `massive`, `polygon_pull_data` gained a `parquet_export` parameter and returns the resulting DataFrame, and `polygon_fetch_full_history` renamed its `full_history_df` parameter to `existing_history_df`. Replaced the reproduced docstrings with prose descriptions, added the free tier constraints that shape the design, and documented the on-disk layout the data lands in.

# %% [markdown]
# ## Introduction

# %% [markdown]
# Where the [previous post on collecting crypto asset data from Coinbase](/posts/data-pipelining-with-coinbase/) covered digital assets, this one covers the equity side. The two functions below pull minute, hour, and daily bars for equities and ETFs from Polygon.io, since rebranded as [Massive](https://massive.com).
#
# Two constraints from the free tier drive most of the design. The first is a two year limit on historical data, which is why the examples below start from a date two years back rather than attempting to pull an asset's full history. The second is a rate limit of five API requests per minute, which is what the `free_tier` flag handles. When using the free tier, the fetch pauses for twelve seconds between requests. A single API call also returns at most 5,000 records, so any meaningful date range has to be walked through in chunks and reassembled.
#
# The work is split across two functions that build on one another. `polygon_fetch_full_history` walks a date range and returns it as a single dataframe. `polygon_pull_data` wraps that to maintain pickle, Excel, and Parquet files on disk, extending an existing record with the rows it is missing, or creating a new record where none exists.

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
# Here are the functions needed for this project, listed in the order they build on one another:
#
# * [polygon_fetch_full_history](/posts/reusable-extensible-python-functions-financial-data-analysis/#polygon_fetch_full_history): Fetch full historical data for a given product from Polygon API.
# * [polygon_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#polygon_pull_data): Read existing data file, download price data from Polygon, and export data.

# %%
from polygon_fetch_full_history import polygon_fetch_full_history
from polygon_pull_data import polygon_pull_data

# %% [markdown]
# One naming note before the code: Polygon.io has rebranded to Massive, and the official Python client followed. The package is now [`massive`](https://pypi.org/project/massive/) rather than `polygon-api-client`, so the import below reads `from massive import RESTClient`. The API surface is otherwise unchanged, and I've kept "Polygon" in the function names and directory layout since that's what the existing data is filed under.

# %% [markdown]
# ## Function Usage

# %% [markdown]
# Both examples below use daily bars, but switching to minute or hour data is a matter of changing the `timespan` and `multiplier` arguments, with everything else unchanged. Note that finer granularity burns through the free tier rate limit considerably faster, since each request covers a much shorter window. Massive actually aggregates minute data into hour bars, so the time to pull minute and hour data is actually the same. Both functions accept only `minute`, `hour`, or `day` for `timespan` and raise an exception otherwise, since the window sizing logic is only defined for those three.

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
    ticker="AMZN",
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
# ### Polygon Pull Data

# %% [markdown]
# This function wraps the one above and performs the following:
#
# 1. Attempt to read an existing pickle data file.
# 2. If a data file exists, then pull updated data starting from the last date on record.
# 3. Otherwise, pull all historical data available for that asset for the past 2 years (or chosen interval).
# 4. Store Pickle, Excel, and/or Parquet files of the data in the specified directories.
# 5. Return the resulting dataframe.
#
# Setting `force_existing_check` re-pulls the entire range rather than starting from the last date on record, which is how gaps in an existing file get filled.

# %% [markdown]
# The `base_directory`, `source`, `asset_class`, and `timespan` arguments together tell the function where in the local filesystem to look for an existing pickle file, and where to store the updated exports. They assemble into a path of the form `{base_directory}/{source}/{asset_class}/{timespan}/{ticker}`, so the example below reads and writes:
#
# ```text
# Data/Polygon/Equities/day/AMZN.pkl
# Data/Polygon/Equities/day/AMZN.xlsx
# Data/Polygon/Equities/day/AMZN.parquet
# ```
#
# Keeping the timespan in the path means minute, hour, and daily records for the same ticker sit side by side without overwriting one another.

# %%
current_year = datetime.now().year
current_month = datetime.now().month
current_day = datetime.now().day

# Example usage - daily
df = polygon_pull_data(
    base_directory=DATA_DIR,
    ticker="AMZN",
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
# ## Future Investigation

# %% [markdown]
# 1. Calculate adjusted open/high/low/close prices using the dividend adjustment factor.

# %% [markdown]
# ## References

# %% [markdown]
# 1. [Massive (formerly Polygon.io)](https://massive.com)
# 2. [Massive REST API quickstart](https://massive.com/docs/rest/quickstart)
# 3. [massive on PyPI](https://pypi.org/project/massive/)
# 4. [massive-com/client-python on GitHub](https://github.com/massive-com/client-python)
# 5. [Reusable & Extensible Python Functions For Financial Data Analysis](/posts/reusable-extensible-python-functions-financial-data-analysis/)
