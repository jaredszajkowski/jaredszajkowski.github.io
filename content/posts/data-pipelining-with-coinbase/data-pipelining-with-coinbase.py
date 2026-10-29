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
#     display_name: general-venv-p313 (3.13.11.final.0)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Post Updates

# %% [markdown]
# Update 8/8/2026: Reworked `coinbase_pull_data` so that a new record is built from 2010 forward and an existing record resumes from its last stored candle, rather than the initial pull starting at a fixed year and updates re-fetching a caller-supplied range. Revised the walkthrough of that function to match.
#
# Update 8/6/2026: Clarified how the initial pull differs from an incremental update, documented the asset filtering performed by `coinbase_pull_data`, reordered the function list to build from the lowest-level function upward, and replaced the historical candles example with an hourly range that returns more than a single row.

# %% [markdown]
# ## Introduction

# %% [markdown]
# This post covers how I collect and store minute, hour, and daily crypto asset data from Coinbase. Since I first published it I have expanded the walkthrough to cover how the initial pull differs from an incremental update, and the filtering that gets applied to the asset list along the way.
#
# The work is split across four functions that build on one another. `coinbase_fetch_historical_candles` wraps a single request to the Coinbase Exchange candles endpoint. `coinbase_fetch_full_history` pages that endpoint to cover an arbitrary date range. `coinbase_fetch_available_products` lists the tradeable pairs. And `coinbase_pull_data` combines all three to maintain a directory of pickle files on disk, resuming an existing data file from its last stored candle, or building a new record from scratch where none exists.
#
# The first three functions are executed below. `coinbase_pull_data` is shown but not run, since it writes to the filesystem and can run for a long time against a full asset list.

# %% [markdown]
# ## Python Imports

# %%
# Standard Library
import datetime
import os
import sys
import warnings

from datetime import datetime
from pathlib import Path

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
# * [coinbase_fetch_available_products](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_available_products): Fetch available products from Coinbase Exchange API.
# * [coinbase_fetch_historical_candles](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_historical_candles): Fetch historical candle data for a given product from Coinbase Exchange API.
# * [coinbase_fetch_full_history](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_full_history): Fetch full historical data for a given product from Coinbase Exchange API.
# * [coinbase_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_pull_data): Update existing record or pull full historical data for a given product from Coinbase Exchange API.

# %%
from coinbase_fetch_available_products import coinbase_fetch_available_products
from coinbase_fetch_historical_candles import coinbase_fetch_historical_candles
from coinbase_fetch_full_history import coinbase_fetch_full_history
from coinbase_pull_data import coinbase_pull_data

# %% [markdown]
# ## Function Usage

# %% [markdown]
# ### Coinbase Fetch Available Products

# %% [markdown]
# This function pulls the list of available assets based on the inputs for base and quote currency. In the example below the `quote_currency` is provided as "USD", so the function returns every asset priced against USD:

# %%
df = coinbase_fetch_available_products(
    base_currency=None,
    quote_currency="USD",
    status="online",
)

display(df[["id", "base_currency", "quote_currency", "status"]])

# %% [markdown]
# The API returns eighteen columns per product, but the four shown above are the ones that matter downstream, and are the same four that `coinbase_pull_data` prints when it builds its working list.

# %% [markdown]
# ### Coinbase Fetch Historical Candles

# %% [markdown]
# This is the lowest-level of the four functions, and maps to a single request against the Coinbase Exchange candles endpoint. It returns the date/time, open, high, low, close, and volume for each period in the requested range. The example below pulls hourly candles from the start of 2025:

# %%
df = coinbase_fetch_historical_candles(
    product_id="BTC-USD",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 1, 1, 6),
    granularity=3_600,
)

display(df)

# %% [markdown]
# Two details are worth noting here. The endpoint returns at most 300 candles per request no matter how wide a range is asked for, which is the constraint that the next function exists to work around. And the response arrives in reverse chronological order, so the function reverses it before building the dataframe. Rate limiting (HTTP 429) is retried up to five times with an exponential backoff.

# %% [markdown]
# ### Coinbase Fetch Full History

# %% [markdown]
# This function pulls an arbitrary date range for a specified asset by paging the function above. Because a single request is capped at 300 candles, it walks the range in windows of `granularity * 300` seconds, advancing from the timestamp of the last candle it received and pausing 0.2 seconds between requests to stay within the rate limits. The individual responses are concatenated into one dataframe, so a range of years is handled exactly the same way as the single month below:

# %%
df = coinbase_fetch_full_history(
    product_id="BTC-USD",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 1, 31),
    granularity=86_400,
)

display(df)

# %% [markdown]
# ### Coinbase Pull Data

# %% [markdown]
# This function combines the three above to perform the following:
#
# 1. Resolve the list of products to update from the `base_currency` and `quote_currency` arguments.
# 2. Attempt to read an existing pickle data file for each product.
# 3. If a data file exists, resume from its last stored candle and pull forward to the present.
# 4. Otherwise, pull the available historical data for that asset and create a new record.
# 5. Store pickle and/or excel files of the data in the specified directories.
# 6. Prune the resulting product list down to the assets worth carrying forward.
#
# Through the `base_directory`, `source`, and `asset_class` variables the function knows where in the local filesystem to look for an existing pickle file and where to store the resulting updated pickle and/or excel files:
#
# ```python
# df = coinbase_pull_data(
#     base_directory=DATA_DIR,
#     source="Coinbase",
#     asset_class="Cryptocurrencies",
#     excel_export=False,
#     pickle_export=True,
#     output_confirmation=True,
#     base_currency="BTC",
#     quote_currency="USD",
#     granularity=60, # 60=minute, 3600=hourly, 86400=daily
#     status='online', # default status is 'online'
# )
# ```
#
# Note that no dates are passed. `start_date` defaults to 1/1/2010 and only applies when there is no existing record, and `end_date` defaults to one day ago to account for the lag in data availability, so a single call per product and granularity is enough to either create a record or bring one current.
#
# By passing `None` as the `base_currency` and/or the `quote_currency`, the function uses `coinbase_fetch_available_products` to build the product list, so a single call can pull every USD-quoted pair on Coinbase.

# %% [markdown]
# On an update, the existing record is read back and the fetch resumes from the last date it contains. That final candle is deliberately re-fetched, since the period may still have been in progress when it was written; where a date appears in both the stored and the newly fetched data, the new row wins, so a partial candle is replaced by its completed version rather than left stale. The same range can therefore be pulled repeatedly without duplicating or corrupting anything.
#
# The initial pull works differently. With no pickle file to resume from, there is no last date to start at, so the function falls back to `start_date` and works forward a year at a time until the API returns something. Coinbase has nothing for any of these pairs in 2010, so the first several attempts come back empty and are skipped; for BTC-USD the data begins on 7/20/2015, which is where the record actually starts.
#
# The function also prunes the product list it returns. Assets with no data available, assets whose closing price never exceeds the price threshold, stablecoins (USDT, USDC, PAX, DAI, PYUSD, GUSD), and wrapped coins (WAXL, WBTC) are all removed. What remains is the set of assets actually useful for analysis, which matters when the starting product list runs to several hundred entries.

# %% [markdown]
# The example above pulls the data for BTC-USD, and stores it in the following system directory:
#
# **DATA_DIR/Coinbase/Cryptocurrencies/Minute**
#
# And here is the filesystem tree output for the `Coinbase` directory:
#
# ```bash
# $ tree Coinbase/
# Coinbase/
# └── Cryptocurrencies
#     ├── Daily
#     │   ├── BTC-USD.pkl
#     │   ├── BTC-USD.xlsx
#     │   ├── ETH-USD.pkl
#     │   ├── ETH-USD.xlsx
#     │   ├── SOL-USD.pkl
#     │   ├── SOL-USD.xlsx
#     │   ├── XRP-USD.pkl
#     │   └── XRP-USD.xlsx
#     ├── Hourly
#     │   ├── BTC-USD.pkl
#     │   ├── BTC-USD.xlsx
#     │   ├── ETH-USD.pkl
#     │   ├── ETH-USD.xlsx
#     │   ├── SOL-USD.pkl
#     │   ├── SOL-USD.xlsx
#     │   ├── XRP-USD.pkl
#     │   └── XRP-USD.xlsx
#     └── Minute
#         ├── BTC-USD.pkl
#         ├── ETH-USD.pkl
#         ├── SOL-USD.pkl
#         └── XRP-USD.pkl
#
# 5 directories, 20 files
# ```
#
# Note that the `Minute` directory holds only pickle files. Minute data runs to hundreds of thousands of rows per asset, which makes the excel export slow and unwieldy, so `excel_export` is left as `False` at that granularity.

# %% [markdown]
# ## References

# %% [markdown]
# 1. [Coinbase](https://www.coinbase.com/)
# 2. Coinbase Exchange API, products endpoint: `https://api.exchange.coinbase.com/products`
# 3. Coinbase Exchange API, candles endpoint: `https://api.exchange.coinbase.com/products/{product_id}/candles`
# 4. [Reusable & Extensible Python Functions For Financial Data Analysis](/posts/reusable-extensible-python-functions-financial-data-analysis/)
