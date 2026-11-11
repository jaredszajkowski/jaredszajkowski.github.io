## Post Updates

Update 11/1/2026: Moved the total correlation metric, decile analysis, and trading strategy here from the original post, which is now [part 1](/posts/asset-class-return-correlations-part-1/). Also added the 2x leveraged funds SSO, MVV, and SAA to the trading strategy, using the same signal as the original IVV, IJH, and IJR strategies.

## Introduction

In [part 1](/posts/asset-class-return-correlations-part-1/), we looked at historical return correlations between asset classes, and saw that the rolling correlations can abruptly increase or decrease in response to market shocks. In this post, we'll build a "total correlation" metric from those rolling correlations, look at future returns based on that metric, and develop a trading strategy that uses correlation as a market timing signal.

 ## Python Imports


```python
import os
import sys
import warnings

from itertools import combinations, count
from pathlib import Path

# Data Handling
import numpy as np
import pandas as pd

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
```

## Python Functions

Here are the functions needed for this project:

* [load_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.
* [pandas_set_decimal_places](/posts/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.
* [plot_histogram](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_histogram): Plot the histogram of a data set from a DataFrame.
* [plot_scatter](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter): Plot the data from a DataFrame for a specified date range and columns.
* [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the timeseries data from a DataFrame for a specified date range and columns.
* [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.
* [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.


```python
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_histogram import plot_histogram
from plot_scatter import plot_scatter
from plot_time_series import plot_time_series
from summary_stats import summary_stats
from yf_pull_data import yf_pull_data
```


```python
pandas_set_decimal_places(2)
figure_number = count(1)
table_number = count(1)
```

## Data Overview

The signal in this post comes from the rolling correlations between the following funds:

* Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
* Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
* Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)

We'll also use the following 2x leveraged ETFs, but only in the trading strategy. They do not feed into the signal:

* 2x Large Cap US Stocks / S&P 500 -- SSO (ProShares Ultra S&P500)
* 2x Mid Cap US Stocks / S&P MidCap 400 -- MVV (ProShares Ultra MidCap400)
* 2x Small Cap US Stocks / S&P SmallCap 600 -- SAA (ProShares Ultra SmallCap600)

We'll load the rest of the ETFs from [part 1](/posts/asset-class-return-correlations-part-1/) as well, in order to keep the same sample of days. That sample only includes the days where all of the ETFs have data, so it starts with the inception of GSG in July 2006. Using only IVV, IJH, and IJR would extend the sample back to 2000, and change the deciles and the resulting trades.

For all of these, we will use the adjusted closing price, which accounts for dividends and stock splits.

### Acquire & Load Data


```python
# Create list of tickers to pull data for
us_equity_tickers = ["IVV", "IJH", "IJR", "QQQ", "IWB", "IWD", "IWF", "IWM"]
intl_equity_tickers = ["EFA", "EEM", "IEV"]
equity_tickers = us_equity_tickers + intl_equity_tickers
bond_tickers = ["SHY", "IEF", "TLT", "AGG"]
commodity_tickers = ["GLD", "GSG"]
real_estate_tickers = ["IYR"]

# 2x leveraged funds, used only in the trading strategy. These are kept out of etf_tickers
# so that SAA's later inception date doesn't change the sample used for the correlations.
leveraged_tickers = ["SSO", "MVV", "SAA"]

etf_tickers = (
    us_equity_tickers
    + intl_equity_tickers
    + bond_tickers
    + commodity_tickers
    + real_estate_tickers
)
```


```python
for ticker in etf_tickers + leveraged_tickers:
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
```

    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)


    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:568: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      quotes.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:585: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:587: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      dividends.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:604: Pandas4Warning: The inplace keyword in DataFrame.set_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.set_index("date", inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/utils.py:606: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      splits.sort_index(inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:220: Pandas4Warning: The inplace keyword in DataFrame.rename is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.rename(columns=ctx.isins, inplace=True)
    /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/.venv/lib/python3.14/site-packages/yfinance/multi.py:224: Pandas4Warning: The inplace keyword in DataFrame.sort_index is deprecated and will be removed in a future version (PDEP-8).
    See https://pandas.pydata.org/docs/dev/whatsnew/v3.1.0.html#deprecation-inplace for more details.
      data.sort_index(level=0, axis=1, inplace=True)



```python
fund_data = pd.DataFrame()

for ticker in etf_tickers + leveraged_tickers:
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

display(Markdown(f"Table {next(table_number)}: Fund Data"))
display(fund_data)
```


Table 1: Fund Data



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>IVV_Adj_Close</th>
      <th>IVV_Daily_Return</th>
      <th>IJH_Adj_Close</th>
      <th>IJH_Daily_Return</th>
      <th>IJR_Adj_Close</th>
      <th>IJR_Daily_Return</th>
      <th>QQQ_Adj_Close</th>
      <th>QQQ_Daily_Return</th>
      <th>IWB_Adj_Close</th>
      <th>IWB_Daily_Return</th>
      <th>...</th>
      <th>GSG_Adj_Close</th>
      <th>GSG_Daily_Return</th>
      <th>IYR_Adj_Close</th>
      <th>IYR_Daily_Return</th>
      <th>SSO_Adj_Close</th>
      <th>SSO_Daily_Return</th>
      <th>MVV_Adj_Close</th>
      <th>MVV_Daily_Return</th>
      <th>SAA_Adj_Close</th>
      <th>SAA_Daily_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1999-03-10</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>42.98</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1999-03-11</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>43.19</td>
      <td>0.00</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1999-03-12</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>42.14</td>
      <td>-0.02</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1999-03-15</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>43.35</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1999-03-16</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>43.72</td>
      <td>0.01</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-11-04</th>
      <td>770.17</td>
      <td>0.02</td>
      <td>74.59</td>
      <td>0.01</td>
      <td>142.93</td>
      <td>0.01</td>
      <td>691.95</td>
      <td>0.01</td>
      <td>419.20</td>
      <td>0.02</td>
      <td>...</td>
      <td>34.20</td>
      <td>-0.04</td>
      <td>104.02</td>
      <td>0.03</td>
      <td>69.62</td>
      <td>0.03</td>
      <td>84.56</td>
      <td>0.01</td>
      <td>34.51</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>2026-11-05</th>
      <td>736.21</td>
      <td>-0.04</td>
      <td>71.68</td>
      <td>-0.04</td>
      <td>137.49</td>
      <td>-0.04</td>
      <td>647.05</td>
      <td>-0.06</td>
      <td>401.06</td>
      <td>-0.04</td>
      <td>...</td>
      <td>34.53</td>
      <td>0.01</td>
      <td>102.24</td>
      <td>-0.02</td>
      <td>63.51</td>
      <td>-0.09</td>
      <td>77.80</td>
      <td>-0.08</td>
      <td>31.93</td>
      <td>-0.07</td>
    </tr>
    <tr>
      <th>2026-11-06</th>
      <td>738.68</td>
      <td>0.00</td>
      <td>72.11</td>
      <td>0.01</td>
      <td>137.64</td>
      <td>0.00</td>
      <td>656.10</td>
      <td>0.01</td>
      <td>402.58</td>
      <td>0.00</td>
      <td>...</td>
      <td>34.46</td>
      <td>-0.00</td>
      <td>101.62</td>
      <td>-0.01</td>
      <td>63.85</td>
      <td>0.01</td>
      <td>78.77</td>
      <td>0.01</td>
      <td>31.85</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>2026-11-09</th>
      <td>756.05</td>
      <td>0.02</td>
      <td>74.39</td>
      <td>0.03</td>
      <td>141.72</td>
      <td>0.03</td>
      <td>679.35</td>
      <td>0.04</td>
      <td>412.33</td>
      <td>0.02</td>
      <td>...</td>
      <td>33.93</td>
      <td>-0.02</td>
      <td>103.18</td>
      <td>0.02</td>
      <td>66.85</td>
      <td>0.05</td>
      <td>83.81</td>
      <td>0.06</td>
      <td>33.75</td>
      <td>0.06</td>
    </tr>
    <tr>
      <th>2026-11-10</th>
      <td>753.37</td>
      <td>-0.00</td>
      <td>74.13</td>
      <td>-0.00</td>
      <td>141.19</td>
      <td>-0.00</td>
      <td>674.76</td>
      <td>-0.01</td>
      <td>410.85</td>
      <td>-0.00</td>
      <td>...</td>
      <td>33.67</td>
      <td>-0.01</td>
      <td>102.98</td>
      <td>-0.00</td>
      <td>66.37</td>
      <td>-0.01</td>
      <td>83.13</td>
      <td>-0.01</td>
      <td>33.62</td>
      <td>-0.00</td>
    </tr>
  </tbody>
</table>
<p>6962 rows × 42 columns</p>
</div>



```python
for ticker in etf_tickers + leveraged_tickers:
    print(f"First date for {ticker}: {fund_data[f'{ticker}_Daily_Return'].first_valid_index()}")
```

    First date for IVV: 2000-05-22 00:00:00
    First date for IJH: 2000-05-30 00:00:00
    First date for IJR: 2000-05-30 00:00:00
    First date for QQQ: 1999-03-11 00:00:00
    First date for IWB: 2000-05-22 00:00:00
    First date for IWD: 2000-05-30 00:00:00
    First date for IWF: 2000-05-30 00:00:00
    First date for IWM: 2000-05-30 00:00:00
    First date for EFA: 2001-08-28 00:00:00
    First date for EEM: 2003-04-15 00:00:00
    First date for IEV: 2000-07-31 00:00:00
    First date for SHY: 2002-07-31 00:00:00
    First date for IEF: 2002-07-31 00:00:00
    First date for TLT: 2002-07-31 00:00:00
    First date for AGG: 2003-09-30 00:00:00
    First date for GLD: 2004-11-19 00:00:00
    First date for GSG: 2006-07-24 00:00:00
    First date for IYR: 2000-06-20 00:00:00
    First date for SSO: 2006-06-22 00:00:00
    First date for MVV: 2006-06-22 00:00:00
    First date for SAA: 2007-01-26 00:00:00



```python
# Keep only the daily return columns for the ETFs used in the correlations
daily_return_columns = [f"{ticker}_Daily_Return" for ticker in etf_tickers]
fund_data_daily_returns_all = fund_data[daily_return_columns]

# Drop the rows with missing data, which sets the start of the sample
fund_data_daily_returns = fund_data_daily_returns_all.dropna()

print(f"Shape of fund_data_daily_returns_all: {fund_data_daily_returns_all.shape}")
print(f"Shape of fund_data_daily_returns: {fund_data_daily_returns.shape}")
print(f"First date in sample: {fund_data_daily_returns.index[0]}")
```

    Shape of fund_data_daily_returns_all: (6962, 18)
    Shape of fund_data_daily_returns: (5108, 18)
    First date in sample: 2006-07-24 00:00:00


## Calculate Rolling Correlations

Next, we will calculate the rolling correlations between IVV, IJH, and IJR for the same periods as in part 1.


```python
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
```


```python
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
        temp_df = fund_data_daily_returns[
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
```


Table 2: Rolling Correlations



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>IVV_IJH_3d</th>
      <th>IVV_IJH_1w</th>
      <th>IVV_IJH_2w</th>
      <th>IVV_IJH_1m</th>
      <th>IVV_IJH_3m</th>
      <th>IVV_IJH_6m</th>
      <th>IVV_IJH_1y</th>
      <th>IVV_IJH_5y</th>
      <th>IVV_IJH_10y</th>
      <th>IVV_IJR_3d</th>
      <th>...</th>
      <th>IVV_IJR_10y</th>
      <th>IJH_IJR_3d</th>
      <th>IJH_IJR_1w</th>
      <th>IJH_IJR_2w</th>
      <th>IJH_IJR_1m</th>
      <th>IJH_IJR_3m</th>
      <th>IJH_IJR_6m</th>
      <th>IJH_IJR_1y</th>
      <th>IJH_IJR_5y</th>
      <th>IJH_IJR_10y</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2006-07-24</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2006-07-25</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2006-07-26</th>
      <td>0.97</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.96</td>
      <td>...</td>
      <td>NaN</td>
      <td>1.00</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2006-07-27</th>
      <td>0.99</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.93</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.97</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2006-07-28</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.99</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.98</td>
      <td>0.99</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-11-04</th>
      <td>-0.23</td>
      <td>0.58</td>
      <td>0.67</td>
      <td>0.64</td>
      <td>0.70</td>
      <td>0.75</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.40</td>
      <td>...</td>
      <td>0.83</td>
      <td>0.80</td>
      <td>0.92</td>
      <td>0.76</td>
      <td>0.87</td>
      <td>0.89</td>
      <td>0.91</td>
      <td>0.93</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
    <tr>
      <th>2026-11-05</th>
      <td>0.99</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.88</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.81</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>0.83</td>
      <td>0.97</td>
      <td>0.97</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>0.93</td>
      <td>0.92</td>
      <td>0.94</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
    <tr>
      <th>2026-11-06</th>
      <td>0.98</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.81</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>1.00</td>
      <td>...</td>
      <td>0.83</td>
      <td>0.97</td>
      <td>0.97</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>0.92</td>
      <td>0.92</td>
      <td>0.94</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
    <tr>
      <th>2026-11-09</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.90</td>
      <td>0.83</td>
      <td>0.81</td>
      <td>0.82</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>0.83</td>
      <td>1.00</td>
      <td>0.98</td>
      <td>0.98</td>
      <td>0.95</td>
      <td>0.94</td>
      <td>0.93</td>
      <td>0.94</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
    <tr>
      <th>2026-11-10</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.91</td>
      <td>0.83</td>
      <td>0.81</td>
      <td>0.82</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>0.83</td>
      <td>0.99</td>
      <td>0.98</td>
      <td>0.98</td>
      <td>0.95</td>
      <td>0.94</td>
      <td>0.93</td>
      <td>0.94</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
  </tbody>
</table>
<p>5108 rows × 27 columns</p>
</div>


## Total Correlation Metric

As we saw in [part 1](/posts/asset-class-return-correlations-part-1/), there are periods of time when the correlations abruptly increase or decrease as a response to some kind of market shock or event.

As an attempt to find some kind of signal, let's simply add the correlations together to get a "total correlation" metric, and look at the distribution. Note that we normalize the correlations to account for the number of correlations being summed by dividing the total by the number of correlations, to keep the values between -1 and 1.


```python
# Calculate total rolling correlation for each window
for window, days in rolling_windows.items():
    rolling_corr_results_df[f"total_rolling_correlation_{window}"] = rolling_corr_results_df[[col for col in rolling_corr_results_df.columns if col.endswith(f"_{window}")]].sum(axis=1) / len([col for col in rolling_corr_results_df.columns if col.endswith(f"_{window}")])

# Reset any 0.00 values to NaN
rolling_corr_results_df.replace(0.00, np.nan, inplace=True)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>IVV_IJH_3d</th>
      <th>IVV_IJH_1w</th>
      <th>IVV_IJH_2w</th>
      <th>IVV_IJH_1m</th>
      <th>IVV_IJH_3m</th>
      <th>IVV_IJH_6m</th>
      <th>IVV_IJH_1y</th>
      <th>IVV_IJH_5y</th>
      <th>IVV_IJH_10y</th>
      <th>IVV_IJR_3d</th>
      <th>...</th>
      <th>IJH_IJR_10y</th>
      <th>total_rolling_correlation_3d</th>
      <th>total_rolling_correlation_1w</th>
      <th>total_rolling_correlation_2w</th>
      <th>total_rolling_correlation_1m</th>
      <th>total_rolling_correlation_3m</th>
      <th>total_rolling_correlation_6m</th>
      <th>total_rolling_correlation_1y</th>
      <th>total_rolling_correlation_5y</th>
      <th>total_rolling_correlation_10y</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2006-07-24</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2006-07-25</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2006-07-26</th>
      <td>0.97</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.96</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.98</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2006-07-27</th>
      <td>0.99</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.93</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.97</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2006-07-28</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.99</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.99</td>
      <td>0.97</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-11-04</th>
      <td>-0.23</td>
      <td>0.58</td>
      <td>0.67</td>
      <td>0.64</td>
      <td>0.70</td>
      <td>0.75</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.40</td>
      <td>...</td>
      <td>0.96</td>
      <td>0.32</td>
      <td>0.70</td>
      <td>0.64</td>
      <td>0.68</td>
      <td>0.73</td>
      <td>0.77</td>
      <td>0.82</td>
      <td>0.89</td>
      <td>0.90</td>
    </tr>
    <tr>
      <th>2026-11-05</th>
      <td>0.99</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.88</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.81</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>0.96</td>
      <td>0.98</td>
      <td>0.95</td>
      <td>0.92</td>
      <td>0.87</td>
      <td>0.82</td>
      <td>0.81</td>
      <td>0.83</td>
      <td>0.89</td>
      <td>0.90</td>
    </tr>
    <tr>
      <th>2026-11-06</th>
      <td>0.98</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.81</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>1.00</td>
      <td>...</td>
      <td>0.96</td>
      <td>0.98</td>
      <td>0.95</td>
      <td>0.91</td>
      <td>0.87</td>
      <td>0.82</td>
      <td>0.81</td>
      <td>0.83</td>
      <td>0.89</td>
      <td>0.90</td>
    </tr>
    <tr>
      <th>2026-11-09</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.90</td>
      <td>0.83</td>
      <td>0.81</td>
      <td>0.82</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>0.96</td>
      <td>1.00</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.85</td>
      <td>0.82</td>
      <td>0.84</td>
      <td>0.89</td>
      <td>0.90</td>
    </tr>
    <tr>
      <th>2026-11-10</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.91</td>
      <td>0.83</td>
      <td>0.81</td>
      <td>0.82</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>0.96</td>
      <td>0.99</td>
      <td>0.98</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.85</td>
      <td>0.82</td>
      <td>0.84</td>
      <td>0.89</td>
      <td>0.90</td>
    </tr>
  </tbody>
</table>
<p>5108 rows × 36 columns</p>
</div>




```python
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
```


    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_25_0.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_25_1.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_25_2.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_25_3.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_25_4.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_25_5.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_25_6.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_25_7.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_25_8.png)
    


Alright, so the distributions for 1w, 2w, and 1m look interesting. For each of those windows, let's look at the different deciles of the rolling correlations, and what that implies for future returns.

## Future Returns Based On Total Rolling Correlation

First, we need to define the forward return windows that we want to look at.


```python
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
```

Then, we'll merge in the returns and create the forward returns for each of the funds.


```python
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
```


Table 3: Total Rolling Correlations With Forward Returns



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>IVV_IJH_3d</th>
      <th>IVV_IJH_1w</th>
      <th>IVV_IJH_2w</th>
      <th>IVV_IJH_1m</th>
      <th>IVV_IJH_3m</th>
      <th>IVV_IJH_6m</th>
      <th>IVV_IJH_1y</th>
      <th>IVV_IJH_5y</th>
      <th>IVV_IJH_10y</th>
      <th>IVV_IJR_3d</th>
      <th>...</th>
      <th>IJH_Daily_Return_2m_CRR</th>
      <th>IJH_Daily_Return_fwd_2m_CRR</th>
      <th>IJR_Daily_Return_2m_CRR</th>
      <th>IJR_Daily_Return_fwd_2m_CRR</th>
      <th>IVV_Daily_Return_3m_CRR</th>
      <th>IVV_Daily_Return_fwd_3m_CRR</th>
      <th>IJH_Daily_Return_3m_CRR</th>
      <th>IJH_Daily_Return_fwd_3m_CRR</th>
      <th>IJR_Daily_Return_3m_CRR</th>
      <th>IJR_Daily_Return_fwd_3m_CRR</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2006-07-24</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.08</td>
    </tr>
    <tr>
      <th>2006-07-25</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.01</td>
      <td>NaN</td>
      <td>0.02</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.08</td>
    </tr>
    <tr>
      <th>2006-07-26</th>
      <td>0.97</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.96</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.02</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.09</td>
    </tr>
    <tr>
      <th>2006-07-27</th>
      <td>0.99</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.93</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>0.10</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.11</td>
    </tr>
    <tr>
      <th>2006-07-28</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.99</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>0.05</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.08</td>
      <td>NaN</td>
      <td>0.10</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-11-04</th>
      <td>-0.23</td>
      <td>0.58</td>
      <td>0.67</td>
      <td>0.64</td>
      <td>0.70</td>
      <td>0.75</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.40</td>
      <td>...</td>
      <td>-0.01</td>
      <td>NaN</td>
      <td>-0.01</td>
      <td>NaN</td>
      <td>0.00</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2026-11-05</th>
      <td>0.99</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.88</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.81</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>-0.08</td>
      <td>NaN</td>
      <td>-0.07</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2026-11-06</th>
      <td>0.98</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.81</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>1.00</td>
      <td>...</td>
      <td>-0.03</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>-0.07</td>
      <td>NaN</td>
      <td>-0.07</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2026-11-09</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.90</td>
      <td>0.83</td>
      <td>0.81</td>
      <td>0.82</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>0.01</td>
      <td>NaN</td>
      <td>0.01</td>
      <td>NaN</td>
      <td>-0.02</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2026-11-10</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.91</td>
      <td>0.83</td>
      <td>0.81</td>
      <td>0.82</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>-0.00</td>
      <td>NaN</td>
      <td>-0.00</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>5108 rows × 81 columns</p>
</div>


### Summary By Decile

Before looking at the individual plots, here is a summary of the forward returns for each decile of total rolling correlation compared with the baseline (all days). Values are in percent.


```python
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
```


```python
for window in analysis_windows:
    display(Markdown(f"Table {next(table_number)}: Percentage of Positive Future Returns by {window} Total Rolling Correlation Decile"))
    display(decile_summary[window]["pct_positive"])
    display(Markdown(f"Table {next(table_number)}: Mean Future Return (%) by {window} Total Rolling Correlation Decile"))
    display(decile_summary[window]["mean_return"])
```


Table 4: Percentage of Positive Future Returns by 1w Total Rolling Correlation Decile



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="3" halign="left">1d</th>
      <th colspan="3" halign="left">3d</th>
      <th colspan="3" halign="left">1w</th>
      <th colspan="3" halign="left">2w</th>
      <th colspan="3" halign="left">1m</th>
      <th colspan="3" halign="left">2m</th>
      <th colspan="3" halign="left">3m</th>
    </tr>
    <tr>
      <th></th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>...</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Baseline (all days)</th>
      <td>54.83</td>
      <td>53.69</td>
      <td>52.32</td>
      <td>58.71</td>
      <td>55.42</td>
      <td>53.99</td>
      <td>60.09</td>
      <td>56.93</td>
      <td>55.05</td>
      <td>63.78</td>
      <td>...</td>
      <td>57.36</td>
      <td>67.52</td>
      <td>62.35</td>
      <td>60.91</td>
      <td>71.59</td>
      <td>67.01</td>
      <td>65.57</td>
      <td>73.83</td>
      <td>69.37</td>
      <td>66.59</td>
    </tr>
    <tr>
      <th>D1 (-0.28 to 0.68)</th>
      <td>54.01</td>
      <td>48.14</td>
      <td>47.16</td>
      <td>57.34</td>
      <td>50.29</td>
      <td>47.36</td>
      <td>60.08</td>
      <td>54.40</td>
      <td>50.10</td>
      <td>66.93</td>
      <td>...</td>
      <td>56.50</td>
      <td>68.39</td>
      <td>56.86</td>
      <td>54.47</td>
      <td>73.65</td>
      <td>64.67</td>
      <td>62.08</td>
      <td>78.16</td>
      <td>68.74</td>
      <td>64.53</td>
    </tr>
    <tr>
      <th>D2 (0.68 to 0.81)</th>
      <td>56.08</td>
      <td>54.90</td>
      <td>51.57</td>
      <td>57.45</td>
      <td>54.90</td>
      <td>50.59</td>
      <td>57.37</td>
      <td>54.62</td>
      <td>50.69</td>
      <td>64.10</td>
      <td>...</td>
      <td>53.45</td>
      <td>67.19</td>
      <td>59.68</td>
      <td>57.91</td>
      <td>74.00</td>
      <td>67.80</td>
      <td>66.00</td>
      <td>76.83</td>
      <td>71.75</td>
      <td>68.29</td>
    </tr>
    <tr>
      <th>D3 (0.81 to 0.87)</th>
      <td>54.71</td>
      <td>49.41</td>
      <td>50.78</td>
      <td>57.45</td>
      <td>53.53</td>
      <td>52.75</td>
      <td>60.20</td>
      <td>54.90</td>
      <td>54.12</td>
      <td>64.71</td>
      <td>...</td>
      <td>56.08</td>
      <td>67.39</td>
      <td>60.71</td>
      <td>58.35</td>
      <td>71.94</td>
      <td>65.42</td>
      <td>62.25</td>
      <td>76.00</td>
      <td>70.80</td>
      <td>68.20</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.91)</th>
      <td>56.16</td>
      <td>59.30</td>
      <td>58.32</td>
      <td>62.43</td>
      <td>57.14</td>
      <td>56.75</td>
      <td>63.41</td>
      <td>60.67</td>
      <td>60.08</td>
      <td>59.49</td>
      <td>...</td>
      <td>55.19</td>
      <td>67.58</td>
      <td>60.90</td>
      <td>58.74</td>
      <td>69.09</td>
      <td>65.16</td>
      <td>66.14</td>
      <td>75.25</td>
      <td>68.32</td>
      <td>66.93</td>
    </tr>
    <tr>
      <th>D5 (0.91 to 0.93)</th>
      <td>59.22</td>
      <td>58.24</td>
      <td>55.69</td>
      <td>60.98</td>
      <td>57.65</td>
      <td>56.86</td>
      <td>60.39</td>
      <td>55.69</td>
      <td>53.33</td>
      <td>66.27</td>
      <td>...</td>
      <td>57.25</td>
      <td>66.60</td>
      <td>63.85</td>
      <td>62.08</td>
      <td>68.91</td>
      <td>64.36</td>
      <td>63.17</td>
      <td>70.63</td>
      <td>63.89</td>
      <td>62.90</td>
    </tr>
    <tr>
      <th>D6 (0.93 to 0.95)</th>
      <td>49.61</td>
      <td>49.80</td>
      <td>48.63</td>
      <td>54.42</td>
      <td>52.06</td>
      <td>51.47</td>
      <td>56.50</td>
      <td>54.72</td>
      <td>53.94</td>
      <td>57.48</td>
      <td>...</td>
      <td>55.31</td>
      <td>62.52</td>
      <td>61.34</td>
      <td>59.96</td>
      <td>66.60</td>
      <td>63.64</td>
      <td>63.04</td>
      <td>66.73</td>
      <td>63.56</td>
      <td>60.40</td>
    </tr>
    <tr>
      <th>D7 (0.95 to 0.96)</th>
      <td>54.21</td>
      <td>54.40</td>
      <td>53.42</td>
      <td>61.45</td>
      <td>60.27</td>
      <td>59.10</td>
      <td>63.60</td>
      <td>60.47</td>
      <td>58.12</td>
      <td>69.08</td>
      <td>...</td>
      <td>58.90</td>
      <td>69.28</td>
      <td>64.38</td>
      <td>63.41</td>
      <td>71.26</td>
      <td>67.91</td>
      <td>63.58</td>
      <td>72.44</td>
      <td>70.67</td>
      <td>67.91</td>
    </tr>
    <tr>
      <th>D8 (0.96 to 0.97)</th>
      <td>53.14</td>
      <td>52.75</td>
      <td>50.78</td>
      <td>58.55</td>
      <td>55.40</td>
      <td>53.63</td>
      <td>59.33</td>
      <td>58.74</td>
      <td>55.01</td>
      <td>62.08</td>
      <td>...</td>
      <td>57.96</td>
      <td>68.57</td>
      <td>65.42</td>
      <td>64.64</td>
      <td>73.28</td>
      <td>69.16</td>
      <td>68.57</td>
      <td>72.10</td>
      <td>71.71</td>
      <td>68.17</td>
    </tr>
    <tr>
      <th>D9 (0.97 to 0.98)</th>
      <td>55.99</td>
      <td>56.58</td>
      <td>54.22</td>
      <td>59.14</td>
      <td>57.17</td>
      <td>55.60</td>
      <td>59.33</td>
      <td>57.56</td>
      <td>56.78</td>
      <td>65.62</td>
      <td>...</td>
      <td>61.49</td>
      <td>67.19</td>
      <td>63.46</td>
      <td>64.24</td>
      <td>73.23</td>
      <td>69.69</td>
      <td>70.28</td>
      <td>72.64</td>
      <td>68.70</td>
      <td>66.54</td>
    </tr>
    <tr>
      <th>D10 (0.98 to 1.00)</th>
      <td>55.19</td>
      <td>53.42</td>
      <td>52.64</td>
      <td>57.93</td>
      <td>55.77</td>
      <td>55.77</td>
      <td>60.67</td>
      <td>57.53</td>
      <td>58.32</td>
      <td>62.04</td>
      <td>...</td>
      <td>61.45</td>
      <td>70.45</td>
      <td>66.73</td>
      <td>65.17</td>
      <td>73.97</td>
      <td>72.21</td>
      <td>70.45</td>
      <td>77.69</td>
      <td>75.54</td>
      <td>72.02</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 5: Mean Future Return (%) by 1w Total Rolling Correlation Decile



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="3" halign="left">1d</th>
      <th colspan="3" halign="left">3d</th>
      <th colspan="3" halign="left">1w</th>
      <th colspan="3" halign="left">2w</th>
      <th colspan="3" halign="left">1m</th>
      <th colspan="3" halign="left">2m</th>
      <th colspan="3" halign="left">3m</th>
    </tr>
    <tr>
      <th></th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>...</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Baseline (all days)</th>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.14</td>
      <td>0.14</td>
      <td>0.14</td>
      <td>0.24</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.48</td>
      <td>...</td>
      <td>0.45</td>
      <td>1.01</td>
      <td>0.95</td>
      <td>0.95</td>
      <td>2.01</td>
      <td>1.90</td>
      <td>1.88</td>
      <td>3.00</td>
      <td>2.84</td>
      <td>2.81</td>
    </tr>
    <tr>
      <th>D1 (-0.28 to 0.68)</th>
      <td>0.07</td>
      <td>0.05</td>
      <td>0.04</td>
      <td>0.12</td>
      <td>0.05</td>
      <td>0.04</td>
      <td>0.25</td>
      <td>0.24</td>
      <td>0.26</td>
      <td>0.53</td>
      <td>...</td>
      <td>0.70</td>
      <td>0.95</td>
      <td>0.70</td>
      <td>0.82</td>
      <td>1.90</td>
      <td>1.45</td>
      <td>1.39</td>
      <td>2.95</td>
      <td>1.94</td>
      <td>1.52</td>
    </tr>
    <tr>
      <th>D2 (0.68 to 0.81)</th>
      <td>0.05</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.11</td>
      <td>0.09</td>
      <td>0.05</td>
      <td>0.13</td>
      <td>0.03</td>
      <td>-0.03</td>
      <td>0.38</td>
      <td>...</td>
      <td>0.15</td>
      <td>0.85</td>
      <td>0.43</td>
      <td>0.35</td>
      <td>1.82</td>
      <td>1.40</td>
      <td>1.40</td>
      <td>2.93</td>
      <td>2.34</td>
      <td>2.37</td>
    </tr>
    <tr>
      <th>D3 (0.81 to 0.87)</th>
      <td>-0.00</td>
      <td>-0.03</td>
      <td>-0.02</td>
      <td>0.10</td>
      <td>0.03</td>
      <td>0.03</td>
      <td>0.14</td>
      <td>0.05</td>
      <td>0.06</td>
      <td>0.38</td>
      <td>...</td>
      <td>0.22</td>
      <td>0.85</td>
      <td>0.68</td>
      <td>0.66</td>
      <td>1.77</td>
      <td>1.36</td>
      <td>1.22</td>
      <td>3.13</td>
      <td>2.67</td>
      <td>2.68</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.91)</th>
      <td>0.12</td>
      <td>0.11</td>
      <td>0.09</td>
      <td>0.27</td>
      <td>0.26</td>
      <td>0.24</td>
      <td>0.33</td>
      <td>0.31</td>
      <td>0.31</td>
      <td>0.34</td>
      <td>...</td>
      <td>0.35</td>
      <td>0.68</td>
      <td>0.59</td>
      <td>0.63</td>
      <td>1.70</td>
      <td>1.53</td>
      <td>1.68</td>
      <td>2.63</td>
      <td>2.36</td>
      <td>2.47</td>
    </tr>
    <tr>
      <th>D5 (0.91 to 0.93)</th>
      <td>0.13</td>
      <td>0.16</td>
      <td>0.16</td>
      <td>0.24</td>
      <td>0.27</td>
      <td>0.25</td>
      <td>0.31</td>
      <td>0.34</td>
      <td>0.28</td>
      <td>0.62</td>
      <td>...</td>
      <td>0.54</td>
      <td>1.07</td>
      <td>1.07</td>
      <td>1.02</td>
      <td>1.70</td>
      <td>1.49</td>
      <td>1.36</td>
      <td>2.26</td>
      <td>2.03</td>
      <td>1.96</td>
    </tr>
    <tr>
      <th>D6 (0.93 to 0.95)</th>
      <td>-0.07</td>
      <td>-0.10</td>
      <td>-0.10</td>
      <td>-0.03</td>
      <td>-0.06</td>
      <td>-0.03</td>
      <td>0.08</td>
      <td>0.11</td>
      <td>0.13</td>
      <td>0.10</td>
      <td>...</td>
      <td>0.09</td>
      <td>0.55</td>
      <td>0.72</td>
      <td>0.71</td>
      <td>0.85</td>
      <td>0.78</td>
      <td>0.81</td>
      <td>1.69</td>
      <td>1.74</td>
      <td>1.81</td>
    </tr>
    <tr>
      <th>D7 (0.95 to 0.96)</th>
      <td>0.04</td>
      <td>0.06</td>
      <td>0.07</td>
      <td>0.35</td>
      <td>0.38</td>
      <td>0.38</td>
      <td>0.48</td>
      <td>0.48</td>
      <td>0.48</td>
      <td>0.87</td>
      <td>...</td>
      <td>0.79</td>
      <td>1.38</td>
      <td>1.42</td>
      <td>1.37</td>
      <td>2.11</td>
      <td>2.21</td>
      <td>2.14</td>
      <td>3.20</td>
      <td>3.41</td>
      <td>3.45</td>
    </tr>
    <tr>
      <th>D8 (0.96 to 0.97)</th>
      <td>0.08</td>
      <td>0.11</td>
      <td>0.12</td>
      <td>0.10</td>
      <td>0.17</td>
      <td>0.15</td>
      <td>0.15</td>
      <td>0.21</td>
      <td>0.22</td>
      <td>0.30</td>
      <td>...</td>
      <td>0.28</td>
      <td>0.92</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>2.33</td>
      <td>2.47</td>
      <td>2.45</td>
      <td>3.30</td>
      <td>3.38</td>
      <td>3.33</td>
    </tr>
    <tr>
      <th>D9 (0.97 to 0.98)</th>
      <td>0.04</td>
      <td>0.05</td>
      <td>0.06</td>
      <td>0.08</td>
      <td>0.09</td>
      <td>0.14</td>
      <td>0.28</td>
      <td>0.31</td>
      <td>0.34</td>
      <td>0.77</td>
      <td>...</td>
      <td>0.83</td>
      <td>1.22</td>
      <td>1.29</td>
      <td>1.30</td>
      <td>2.50</td>
      <td>2.60</td>
      <td>2.64</td>
      <td>3.36</td>
      <td>3.41</td>
      <td>3.36</td>
    </tr>
    <tr>
      <th>D10 (0.98 to 1.00)</th>
      <td>0.04</td>
      <td>0.04</td>
      <td>0.04</td>
      <td>0.12</td>
      <td>0.11</td>
      <td>0.12</td>
      <td>0.25</td>
      <td>0.20</td>
      <td>0.23</td>
      <td>0.50</td>
      <td>...</td>
      <td>0.57</td>
      <td>1.60</td>
      <td>1.68</td>
      <td>1.68</td>
      <td>3.43</td>
      <td>3.65</td>
      <td>3.67</td>
      <td>4.56</td>
      <td>5.07</td>
      <td>5.09</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 6: Percentage of Positive Future Returns by 2w Total Rolling Correlation Decile



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="3" halign="left">1d</th>
      <th colspan="3" halign="left">3d</th>
      <th colspan="3" halign="left">1w</th>
      <th colspan="3" halign="left">2w</th>
      <th colspan="3" halign="left">1m</th>
      <th colspan="3" halign="left">2m</th>
      <th colspan="3" halign="left">3m</th>
    </tr>
    <tr>
      <th></th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>...</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Baseline (all days)</th>
      <td>54.85</td>
      <td>53.71</td>
      <td>52.31</td>
      <td>58.71</td>
      <td>55.42</td>
      <td>53.98</td>
      <td>60.09</td>
      <td>56.97</td>
      <td>55.08</td>
      <td>63.78</td>
      <td>...</td>
      <td>57.36</td>
      <td>67.49</td>
      <td>62.31</td>
      <td>60.87</td>
      <td>71.56</td>
      <td>66.98</td>
      <td>65.53</td>
      <td>73.81</td>
      <td>69.34</td>
      <td>66.56</td>
    </tr>
    <tr>
      <th>D1 (-0.03 to 0.76)</th>
      <td>55.29</td>
      <td>48.43</td>
      <td>47.65</td>
      <td>60.20</td>
      <td>48.63</td>
      <td>47.84</td>
      <td>63.65</td>
      <td>53.63</td>
      <td>50.69</td>
      <td>68.85</td>
      <td>...</td>
      <td>55.36</td>
      <td>72.26</td>
      <td>59.08</td>
      <td>56.29</td>
      <td>75.50</td>
      <td>63.45</td>
      <td>63.65</td>
      <td>79.07</td>
      <td>67.20</td>
      <td>65.19</td>
    </tr>
    <tr>
      <th>D2 (0.76 to 0.83)</th>
      <td>54.71</td>
      <td>55.49</td>
      <td>54.71</td>
      <td>58.43</td>
      <td>57.25</td>
      <td>53.33</td>
      <td>60.39</td>
      <td>56.86</td>
      <td>53.92</td>
      <td>66.47</td>
      <td>...</td>
      <td>52.55</td>
      <td>70.72</td>
      <td>60.36</td>
      <td>58.37</td>
      <td>74.44</td>
      <td>66.13</td>
      <td>62.47</td>
      <td>78.42</td>
      <td>72.61</td>
      <td>65.77</td>
    </tr>
    <tr>
      <th>D3 (0.83 to 0.87)</th>
      <td>51.57</td>
      <td>53.14</td>
      <td>52.16</td>
      <td>54.51</td>
      <td>51.96</td>
      <td>50.98</td>
      <td>54.90</td>
      <td>53.14</td>
      <td>52.35</td>
      <td>57.06</td>
      <td>...</td>
      <td>50.98</td>
      <td>64.31</td>
      <td>59.41</td>
      <td>57.84</td>
      <td>71.49</td>
      <td>68.12</td>
      <td>65.94</td>
      <td>76.91</td>
      <td>72.29</td>
      <td>68.88</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.90)</th>
      <td>57.25</td>
      <td>55.88</td>
      <td>54.31</td>
      <td>57.65</td>
      <td>53.92</td>
      <td>52.16</td>
      <td>58.04</td>
      <td>55.88</td>
      <td>53.92</td>
      <td>63.92</td>
      <td>...</td>
      <td>57.06</td>
      <td>63.73</td>
      <td>58.04</td>
      <td>57.45</td>
      <td>68.24</td>
      <td>65.88</td>
      <td>61.74</td>
      <td>71.49</td>
      <td>64.55</td>
      <td>64.36</td>
    </tr>
    <tr>
      <th>D5 (0.90 to 0.92)</th>
      <td>54.71</td>
      <td>56.67</td>
      <td>52.35</td>
      <td>62.08</td>
      <td>60.71</td>
      <td>56.97</td>
      <td>62.40</td>
      <td>63.58</td>
      <td>56.89</td>
      <td>66.54</td>
      <td>...</td>
      <td>59.45</td>
      <td>70.87</td>
      <td>66.93</td>
      <td>64.76</td>
      <td>74.95</td>
      <td>69.43</td>
      <td>67.65</td>
      <td>74.95</td>
      <td>68.64</td>
      <td>66.07</td>
    </tr>
    <tr>
      <th>D6 (0.92 to 0.94)</th>
      <td>56.30</td>
      <td>53.74</td>
      <td>53.15</td>
      <td>58.19</td>
      <td>56.61</td>
      <td>54.04</td>
      <td>58.97</td>
      <td>55.62</td>
      <td>52.66</td>
      <td>61.54</td>
      <td>...</td>
      <td>56.02</td>
      <td>62.33</td>
      <td>60.36</td>
      <td>58.19</td>
      <td>67.65</td>
      <td>63.91</td>
      <td>63.91</td>
      <td>70.41</td>
      <td>65.88</td>
      <td>65.29</td>
    </tr>
    <tr>
      <th>D7 (0.94 to 0.95)</th>
      <td>56.08</td>
      <td>54.12</td>
      <td>49.80</td>
      <td>59.80</td>
      <td>55.88</td>
      <td>55.10</td>
      <td>57.25</td>
      <td>54.51</td>
      <td>55.69</td>
      <td>57.65</td>
      <td>...</td>
      <td>56.27</td>
      <td>62.35</td>
      <td>59.41</td>
      <td>58.43</td>
      <td>64.31</td>
      <td>59.02</td>
      <td>58.43</td>
      <td>63.33</td>
      <td>61.96</td>
      <td>59.61</td>
    </tr>
    <tr>
      <th>D8 (0.95 to 0.96)</th>
      <td>51.96</td>
      <td>48.82</td>
      <td>50.78</td>
      <td>57.25</td>
      <td>54.12</td>
      <td>55.10</td>
      <td>59.22</td>
      <td>55.88</td>
      <td>54.12</td>
      <td>63.14</td>
      <td>...</td>
      <td>58.24</td>
      <td>61.57</td>
      <td>61.96</td>
      <td>60.59</td>
      <td>66.47</td>
      <td>63.53</td>
      <td>61.76</td>
      <td>65.69</td>
      <td>65.29</td>
      <td>61.57</td>
    </tr>
    <tr>
      <th>D9 (0.96 to 0.97)</th>
      <td>56.27</td>
      <td>54.51</td>
      <td>53.14</td>
      <td>64.31</td>
      <td>60.39</td>
      <td>60.39</td>
      <td>66.47</td>
      <td>63.92</td>
      <td>63.14</td>
      <td>66.67</td>
      <td>...</td>
      <td>62.75</td>
      <td>72.35</td>
      <td>66.47</td>
      <td>64.12</td>
      <td>73.92</td>
      <td>71.18</td>
      <td>70.78</td>
      <td>75.69</td>
      <td>73.92</td>
      <td>69.41</td>
    </tr>
    <tr>
      <th>D10 (0.97 to 0.99)</th>
      <td>54.31</td>
      <td>56.27</td>
      <td>55.10</td>
      <td>54.71</td>
      <td>54.71</td>
      <td>53.92</td>
      <td>59.61</td>
      <td>56.67</td>
      <td>57.45</td>
      <td>66.08</td>
      <td>...</td>
      <td>64.90</td>
      <td>74.51</td>
      <td>70.98</td>
      <td>72.55</td>
      <td>78.82</td>
      <td>79.02</td>
      <td>78.82</td>
      <td>82.55</td>
      <td>81.18</td>
      <td>79.41</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 7: Mean Future Return (%) by 2w Total Rolling Correlation Decile



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="3" halign="left">1d</th>
      <th colspan="3" halign="left">3d</th>
      <th colspan="3" halign="left">1w</th>
      <th colspan="3" halign="left">2w</th>
      <th colspan="3" halign="left">1m</th>
      <th colspan="3" halign="left">2m</th>
      <th colspan="3" halign="left">3m</th>
    </tr>
    <tr>
      <th></th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>...</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Baseline (all days)</th>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.14</td>
      <td>0.14</td>
      <td>0.14</td>
      <td>0.24</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.48</td>
      <td>...</td>
      <td>0.45</td>
      <td>1.01</td>
      <td>0.95</td>
      <td>0.95</td>
      <td>2.01</td>
      <td>1.90</td>
      <td>1.88</td>
      <td>3.00</td>
      <td>2.84</td>
      <td>2.80</td>
    </tr>
    <tr>
      <th>D1 (-0.03 to 0.76)</th>
      <td>0.05</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>0.16</td>
      <td>0.06</td>
      <td>0.11</td>
      <td>0.28</td>
      <td>0.19</td>
      <td>0.29</td>
      <td>0.61</td>
      <td>...</td>
      <td>0.63</td>
      <td>1.07</td>
      <td>0.49</td>
      <td>0.66</td>
      <td>1.75</td>
      <td>0.88</td>
      <td>0.94</td>
      <td>2.95</td>
      <td>1.39</td>
      <td>0.94</td>
    </tr>
    <tr>
      <th>D2 (0.76 to 0.83)</th>
      <td>0.05</td>
      <td>0.06</td>
      <td>0.08</td>
      <td>0.17</td>
      <td>0.16</td>
      <td>0.16</td>
      <td>0.24</td>
      <td>0.19</td>
      <td>0.16</td>
      <td>0.54</td>
      <td>...</td>
      <td>0.26</td>
      <td>1.02</td>
      <td>0.65</td>
      <td>0.48</td>
      <td>1.75</td>
      <td>1.18</td>
      <td>1.01</td>
      <td>2.92</td>
      <td>2.03</td>
      <td>1.90</td>
    </tr>
    <tr>
      <th>D3 (0.83 to 0.87)</th>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.02</td>
      <td>0.04</td>
      <td>-0.03</td>
      <td>-0.02</td>
      <td>0.08</td>
      <td>-0.00</td>
      <td>0.02</td>
      <td>0.16</td>
      <td>...</td>
      <td>0.03</td>
      <td>0.64</td>
      <td>0.56</td>
      <td>0.63</td>
      <td>1.98</td>
      <td>1.70</td>
      <td>1.93</td>
      <td>3.02</td>
      <td>2.62</td>
      <td>3.07</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.90)</th>
      <td>0.09</td>
      <td>0.10</td>
      <td>0.09</td>
      <td>0.12</td>
      <td>0.17</td>
      <td>0.16</td>
      <td>0.18</td>
      <td>0.22</td>
      <td>0.18</td>
      <td>0.34</td>
      <td>...</td>
      <td>0.37</td>
      <td>0.73</td>
      <td>0.95</td>
      <td>0.98</td>
      <td>1.37</td>
      <td>1.40</td>
      <td>1.33</td>
      <td>2.18</td>
      <td>2.12</td>
      <td>2.22</td>
    </tr>
    <tr>
      <th>D5 (0.90 to 0.92)</th>
      <td>0.07</td>
      <td>0.12</td>
      <td>0.09</td>
      <td>0.21</td>
      <td>0.30</td>
      <td>0.24</td>
      <td>0.39</td>
      <td>0.47</td>
      <td>0.40</td>
      <td>0.57</td>
      <td>...</td>
      <td>0.62</td>
      <td>1.36</td>
      <td>1.44</td>
      <td>1.41</td>
      <td>2.07</td>
      <td>2.06</td>
      <td>1.99</td>
      <td>2.87</td>
      <td>2.87</td>
      <td>2.88</td>
    </tr>
    <tr>
      <th>D6 (0.92 to 0.94)</th>
      <td>0.03</td>
      <td>0.01</td>
      <td>0.04</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.15</td>
      <td>0.19</td>
      <td>0.21</td>
      <td>0.30</td>
      <td>...</td>
      <td>0.34</td>
      <td>0.61</td>
      <td>0.66</td>
      <td>0.64</td>
      <td>1.08</td>
      <td>0.91</td>
      <td>0.86</td>
      <td>2.00</td>
      <td>2.02</td>
      <td>1.98</td>
    </tr>
    <tr>
      <th>D7 (0.94 to 0.95)</th>
      <td>0.03</td>
      <td>0.02</td>
      <td>-0.02</td>
      <td>0.14</td>
      <td>0.11</td>
      <td>0.05</td>
      <td>0.06</td>
      <td>-0.01</td>
      <td>-0.08</td>
      <td>0.14</td>
      <td>...</td>
      <td>0.03</td>
      <td>0.49</td>
      <td>0.40</td>
      <td>0.36</td>
      <td>1.16</td>
      <td>1.08</td>
      <td>0.91</td>
      <td>1.64</td>
      <td>1.79</td>
      <td>1.59</td>
    </tr>
    <tr>
      <th>D8 (0.95 to 0.96)</th>
      <td>0.03</td>
      <td>0.01</td>
      <td>0.02</td>
      <td>0.05</td>
      <td>0.01</td>
      <td>0.04</td>
      <td>0.16</td>
      <td>0.15</td>
      <td>0.14</td>
      <td>0.43</td>
      <td>...</td>
      <td>0.41</td>
      <td>0.58</td>
      <td>0.58</td>
      <td>0.56</td>
      <td>1.35</td>
      <td>1.44</td>
      <td>1.46</td>
      <td>2.54</td>
      <td>2.74</td>
      <td>2.75</td>
    </tr>
    <tr>
      <th>D9 (0.96 to 0.97)</th>
      <td>0.12</td>
      <td>0.11</td>
      <td>0.12</td>
      <td>0.42</td>
      <td>0.43</td>
      <td>0.48</td>
      <td>0.60</td>
      <td>0.59</td>
      <td>0.64</td>
      <td>0.65</td>
      <td>...</td>
      <td>0.62</td>
      <td>1.19</td>
      <td>1.11</td>
      <td>1.03</td>
      <td>3.07</td>
      <td>3.28</td>
      <td>3.25</td>
      <td>3.98</td>
      <td>4.26</td>
      <td>4.19</td>
    </tr>
    <tr>
      <th>D10 (0.97 to 0.99)</th>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.04</td>
      <td>0.10</td>
      <td>0.13</td>
      <td>0.11</td>
      <td>0.27</td>
      <td>0.31</td>
      <td>0.33</td>
      <td>1.05</td>
      <td>...</td>
      <td>1.24</td>
      <td>2.38</td>
      <td>2.66</td>
      <td>2.72</td>
      <td>4.49</td>
      <td>4.96</td>
      <td>5.03</td>
      <td>5.86</td>
      <td>6.44</td>
      <td>6.42</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 8: Percentage of Positive Future Returns by 1m Total Rolling Correlation Decile



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="3" halign="left">1d</th>
      <th colspan="3" halign="left">3d</th>
      <th colspan="3" halign="left">1w</th>
      <th colspan="3" halign="left">2w</th>
      <th colspan="3" halign="left">1m</th>
      <th colspan="3" halign="left">2m</th>
      <th colspan="3" halign="left">3m</th>
    </tr>
    <tr>
      <th></th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>...</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Baseline (all days)</th>
      <td>54.85</td>
      <td>53.73</td>
      <td>52.33</td>
      <td>58.70</td>
      <td>55.46</td>
      <td>54.00</td>
      <td>60.10</td>
      <td>56.97</td>
      <td>55.09</td>
      <td>63.71</td>
      <td>...</td>
      <td>57.27</td>
      <td>67.42</td>
      <td>62.25</td>
      <td>60.79</td>
      <td>71.50</td>
      <td>66.90</td>
      <td>65.46</td>
      <td>73.75</td>
      <td>69.27</td>
      <td>66.49</td>
    </tr>
    <tr>
      <th>D1 (0.19 to 0.79)</th>
      <td>55.80</td>
      <td>51.87</td>
      <td>50.29</td>
      <td>58.35</td>
      <td>52.65</td>
      <td>49.12</td>
      <td>57.87</td>
      <td>52.36</td>
      <td>50.20</td>
      <td>62.43</td>
      <td>...</td>
      <td>54.47</td>
      <td>67.61</td>
      <td>59.11</td>
      <td>55.26</td>
      <td>73.93</td>
      <td>62.12</td>
      <td>59.47</td>
      <td>74.85</td>
      <td>60.12</td>
      <td>57.26</td>
    </tr>
    <tr>
      <th>D2 (0.79 to 0.84)</th>
      <td>55.01</td>
      <td>51.87</td>
      <td>51.28</td>
      <td>59.53</td>
      <td>50.88</td>
      <td>49.12</td>
      <td>60.90</td>
      <td>51.67</td>
      <td>50.29</td>
      <td>66.60</td>
      <td>...</td>
      <td>50.88</td>
      <td>64.69</td>
      <td>55.42</td>
      <td>54.24</td>
      <td>71.69</td>
      <td>65.17</td>
      <td>60.49</td>
      <td>80.86</td>
      <td>74.69</td>
      <td>70.37</td>
    </tr>
    <tr>
      <th>D3 (0.84 to 0.87)</th>
      <td>55.40</td>
      <td>55.21</td>
      <td>52.06</td>
      <td>58.86</td>
      <td>53.94</td>
      <td>50.59</td>
      <td>61.34</td>
      <td>56.21</td>
      <td>50.89</td>
      <td>65.29</td>
      <td>...</td>
      <td>51.28</td>
      <td>72.78</td>
      <td>61.14</td>
      <td>58.58</td>
      <td>78.22</td>
      <td>68.91</td>
      <td>62.97</td>
      <td>74.14</td>
      <td>67.07</td>
      <td>66.06</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.89)</th>
      <td>53.74</td>
      <td>54.33</td>
      <td>50.98</td>
      <td>58.27</td>
      <td>58.07</td>
      <td>53.54</td>
      <td>59.65</td>
      <td>61.02</td>
      <td>57.68</td>
      <td>60.63</td>
      <td>...</td>
      <td>56.69</td>
      <td>69.49</td>
      <td>62.20</td>
      <td>59.84</td>
      <td>72.64</td>
      <td>70.47</td>
      <td>69.29</td>
      <td>80.75</td>
      <td>71.63</td>
      <td>71.63</td>
    </tr>
    <tr>
      <th>D5 (0.89 to 0.92)</th>
      <td>56.30</td>
      <td>55.51</td>
      <td>55.12</td>
      <td>60.55</td>
      <td>57.99</td>
      <td>58.38</td>
      <td>59.17</td>
      <td>57.79</td>
      <td>56.80</td>
      <td>64.69</td>
      <td>...</td>
      <td>57.40</td>
      <td>68.05</td>
      <td>64.10</td>
      <td>60.75</td>
      <td>70.81</td>
      <td>64.50</td>
      <td>64.30</td>
      <td>71.99</td>
      <td>68.44</td>
      <td>66.07</td>
    </tr>
    <tr>
      <th>D6 (0.92 to 0.93)</th>
      <td>53.24</td>
      <td>52.06</td>
      <td>51.28</td>
      <td>58.55</td>
      <td>57.56</td>
      <td>55.60</td>
      <td>60.12</td>
      <td>60.12</td>
      <td>59.33</td>
      <td>56.97</td>
      <td>...</td>
      <td>57.37</td>
      <td>60.90</td>
      <td>60.12</td>
      <td>61.30</td>
      <td>58.94</td>
      <td>54.03</td>
      <td>52.46</td>
      <td>58.94</td>
      <td>54.81</td>
      <td>51.47</td>
    </tr>
    <tr>
      <th>D7 (0.93 to 0.94)</th>
      <td>55.51</td>
      <td>53.74</td>
      <td>52.36</td>
      <td>54.33</td>
      <td>50.79</td>
      <td>50.79</td>
      <td>55.51</td>
      <td>52.17</td>
      <td>52.56</td>
      <td>59.25</td>
      <td>...</td>
      <td>55.71</td>
      <td>64.17</td>
      <td>59.65</td>
      <td>58.66</td>
      <td>62.80</td>
      <td>62.01</td>
      <td>62.01</td>
      <td>64.96</td>
      <td>65.16</td>
      <td>57.87</td>
    </tr>
    <tr>
      <th>D8 (0.94 to 0.95)</th>
      <td>55.99</td>
      <td>53.83</td>
      <td>52.06</td>
      <td>58.94</td>
      <td>56.39</td>
      <td>58.74</td>
      <td>64.83</td>
      <td>60.12</td>
      <td>57.37</td>
      <td>64.05</td>
      <td>...</td>
      <td>60.12</td>
      <td>64.64</td>
      <td>64.24</td>
      <td>63.26</td>
      <td>71.32</td>
      <td>70.14</td>
      <td>71.91</td>
      <td>74.07</td>
      <td>73.48</td>
      <td>71.12</td>
    </tr>
    <tr>
      <th>D9 (0.95 to 0.97)</th>
      <td>54.03</td>
      <td>55.60</td>
      <td>54.42</td>
      <td>62.48</td>
      <td>59.14</td>
      <td>56.19</td>
      <td>60.51</td>
      <td>58.35</td>
      <td>56.39</td>
      <td>69.74</td>
      <td>...</td>
      <td>62.67</td>
      <td>68.96</td>
      <td>66.80</td>
      <td>65.62</td>
      <td>74.66</td>
      <td>73.48</td>
      <td>72.89</td>
      <td>73.67</td>
      <td>76.42</td>
      <td>72.89</td>
    </tr>
    <tr>
      <th>D10 (0.97 to 0.99)</th>
      <td>53.44</td>
      <td>53.24</td>
      <td>53.44</td>
      <td>57.17</td>
      <td>57.17</td>
      <td>57.96</td>
      <td>61.10</td>
      <td>59.92</td>
      <td>59.33</td>
      <td>67.39</td>
      <td>...</td>
      <td>66.01</td>
      <td>72.89</td>
      <td>69.55</td>
      <td>70.14</td>
      <td>80.16</td>
      <td>78.00</td>
      <td>78.39</td>
      <td>83.69</td>
      <td>80.75</td>
      <td>79.96</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 9: Mean Future Return (%) by 1m Total Rolling Correlation Decile



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="3" halign="left">1d</th>
      <th colspan="3" halign="left">3d</th>
      <th colspan="3" halign="left">1w</th>
      <th colspan="3" halign="left">2w</th>
      <th colspan="3" halign="left">1m</th>
      <th colspan="3" halign="left">2m</th>
      <th colspan="3" halign="left">3m</th>
    </tr>
    <tr>
      <th></th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>...</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
      <th>IVV</th>
      <th>IJH</th>
      <th>IJR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Baseline (all days)</th>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.14</td>
      <td>0.14</td>
      <td>0.14</td>
      <td>0.24</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.48</td>
      <td>...</td>
      <td>0.45</td>
      <td>1.00</td>
      <td>0.95</td>
      <td>0.94</td>
      <td>2.00</td>
      <td>1.89</td>
      <td>1.87</td>
      <td>2.99</td>
      <td>2.83</td>
      <td>2.79</td>
    </tr>
    <tr>
      <th>D1 (0.19 to 0.79)</th>
      <td>0.02</td>
      <td>-0.01</td>
      <td>0.00</td>
      <td>0.07</td>
      <td>0.04</td>
      <td>0.08</td>
      <td>0.13</td>
      <td>0.08</td>
      <td>0.15</td>
      <td>0.35</td>
      <td>...</td>
      <td>0.37</td>
      <td>0.80</td>
      <td>0.50</td>
      <td>0.60</td>
      <td>1.24</td>
      <td>0.16</td>
      <td>-0.07</td>
      <td>2.48</td>
      <td>0.57</td>
      <td>-0.16</td>
    </tr>
    <tr>
      <th>D2 (0.79 to 0.84)</th>
      <td>0.06</td>
      <td>0.04</td>
      <td>0.05</td>
      <td>0.15</td>
      <td>0.04</td>
      <td>0.04</td>
      <td>0.28</td>
      <td>0.12</td>
      <td>0.10</td>
      <td>0.53</td>
      <td>...</td>
      <td>0.27</td>
      <td>0.64</td>
      <td>0.33</td>
      <td>0.36</td>
      <td>1.79</td>
      <td>1.10</td>
      <td>1.09</td>
      <td>3.39</td>
      <td>2.58</td>
      <td>2.73</td>
    </tr>
    <tr>
      <th>D3 (0.84 to 0.87)</th>
      <td>0.07</td>
      <td>0.06</td>
      <td>0.04</td>
      <td>0.19</td>
      <td>0.16</td>
      <td>0.09</td>
      <td>0.30</td>
      <td>0.18</td>
      <td>0.09</td>
      <td>0.60</td>
      <td>...</td>
      <td>0.19</td>
      <td>1.30</td>
      <td>0.96</td>
      <td>0.77</td>
      <td>2.38</td>
      <td>1.82</td>
      <td>1.79</td>
      <td>2.90</td>
      <td>2.08</td>
      <td>2.35</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.89)</th>
      <td>0.02</td>
      <td>0.05</td>
      <td>0.04</td>
      <td>0.16</td>
      <td>0.22</td>
      <td>0.20</td>
      <td>0.25</td>
      <td>0.34</td>
      <td>0.34</td>
      <td>0.35</td>
      <td>...</td>
      <td>0.49</td>
      <td>1.22</td>
      <td>1.20</td>
      <td>1.26</td>
      <td>2.44</td>
      <td>2.30</td>
      <td>2.49</td>
      <td>3.41</td>
      <td>3.53</td>
      <td>4.05</td>
    </tr>
    <tr>
      <th>D5 (0.89 to 0.92)</th>
      <td>0.10</td>
      <td>0.12</td>
      <td>0.13</td>
      <td>0.18</td>
      <td>0.22</td>
      <td>0.27</td>
      <td>0.24</td>
      <td>0.31</td>
      <td>0.40</td>
      <td>0.54</td>
      <td>...</td>
      <td>0.74</td>
      <td>1.08</td>
      <td>1.12</td>
      <td>1.23</td>
      <td>1.62</td>
      <td>1.51</td>
      <td>1.69</td>
      <td>2.34</td>
      <td>2.37</td>
      <td>2.75</td>
    </tr>
    <tr>
      <th>D6 (0.92 to 0.93)</th>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.11</td>
      <td>0.16</td>
      <td>0.16</td>
      <td>0.13</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.15</td>
      <td>...</td>
      <td>0.35</td>
      <td>0.15</td>
      <td>0.34</td>
      <td>0.33</td>
      <td>-0.46</td>
      <td>-0.39</td>
      <td>-0.58</td>
      <td>0.13</td>
      <td>0.23</td>
      <td>-0.10</td>
    </tr>
    <tr>
      <th>D7 (0.93 to 0.94)</th>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>-0.17</td>
      <td>-0.20</td>
      <td>-0.18</td>
      <td>-0.05</td>
      <td>-0.11</td>
      <td>-0.11</td>
      <td>0.12</td>
      <td>...</td>
      <td>0.04</td>
      <td>0.47</td>
      <td>0.28</td>
      <td>0.38</td>
      <td>0.77</td>
      <td>0.84</td>
      <td>0.75</td>
      <td>1.28</td>
      <td>1.49</td>
      <td>1.30</td>
    </tr>
    <tr>
      <th>D8 (0.94 to 0.95)</th>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.18</td>
      <td>0.19</td>
      <td>0.19</td>
      <td>0.28</td>
      <td>0.29</td>
      <td>0.28</td>
      <td>0.35</td>
      <td>...</td>
      <td>0.39</td>
      <td>0.56</td>
      <td>0.64</td>
      <td>0.59</td>
      <td>2.23</td>
      <td>2.60</td>
      <td>2.69</td>
      <td>3.28</td>
      <td>3.75</td>
      <td>3.71</td>
    </tr>
    <tr>
      <th>D9 (0.95 to 0.97)</th>
      <td>0.12</td>
      <td>0.10</td>
      <td>0.10</td>
      <td>0.26</td>
      <td>0.22</td>
      <td>0.18</td>
      <td>0.25</td>
      <td>0.19</td>
      <td>0.13</td>
      <td>0.65</td>
      <td>...</td>
      <td>0.45</td>
      <td>1.21</td>
      <td>1.30</td>
      <td>1.20</td>
      <td>2.79</td>
      <td>3.21</td>
      <td>3.22</td>
      <td>3.78</td>
      <td>4.25</td>
      <td>4.21</td>
    </tr>
    <tr>
      <th>D10 (0.97 to 0.99)</th>
      <td>0.05</td>
      <td>0.07</td>
      <td>0.07</td>
      <td>0.29</td>
      <td>0.34</td>
      <td>0.35</td>
      <td>0.58</td>
      <td>0.66</td>
      <td>0.67</td>
      <td>1.12</td>
      <td>...</td>
      <td>1.23</td>
      <td>2.60</td>
      <td>2.82</td>
      <td>2.71</td>
      <td>5.18</td>
      <td>5.65</td>
      <td>5.49</td>
      <td>6.87</td>
      <td>7.32</td>
      <td>6.95</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>


### Plots By Decile

Now the plots to illustrate the tables above:


```python
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
```


    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_38_0.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_38_1.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_38_2.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_38_3.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_38_4.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_38_5.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_38_6.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_38_7.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_38_8.png)
    


It's interesting what the baseline (all days) columns reveal about future returns. For *every* plot, the positive future return percentage increases as time increases. We see a similar, but slightly less pronounced, trend for the total rolling correlation deciles, and this suggests that, on average, the likelihood of positive future returns grows over longer time horizons, regardless of the rolling correlation decile. There is certainly a "belly" present in some of the plots, particularly at the 6th and 7th deciles.

The 10th decile consistently shows the highest positive future return percentages across all time horizons, indicating that assets in this decile tend to perform better in the future compared to those in lower deciles, so let's cherry pick the 2 week total rolling correlation for IVV, IJH, and IJR, at the 10th decile, and the 3 month forward return to examine more closely.

## 2w Total Rolling Correlation, 10th Decile, 3m Forward Return for IVV, IJH, and IJR

As mentioned above, we will take a closer look at the 2 week total rolling correlation for IVV, IJH, and IJR, at the 10th decile, and the 3 month forward return.


```python
# Assign each day to a correlation decile and record each decile's range
bucket = pd.qcut(total_rolling_corr_with_returns.dropna(subset=["total_rolling_correlation_2w"])["total_rolling_correlation_2w"], 10, labels=decile_labels)

# Merge the decile bucket back into the original DataFrame
total_rolling_corr_with_returns = total_rolling_corr_with_returns.dropna(subset=["total_rolling_correlation_2w"])
total_rolling_corr_with_returns["total_rolling_correlation_2w_decile"] = bucket

display(Markdown(f"Table {next(table_number)}: Total Rolling Correlations With 2w Decile Assignments"))
display(total_rolling_corr_with_returns)
```


Table 10: Total Rolling Correlations With 2w Decile Assignments



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>IVV_IJH_3d</th>
      <th>IVV_IJH_1w</th>
      <th>IVV_IJH_2w</th>
      <th>IVV_IJH_1m</th>
      <th>IVV_IJH_3m</th>
      <th>IVV_IJH_6m</th>
      <th>IVV_IJH_1y</th>
      <th>IVV_IJH_5y</th>
      <th>IVV_IJH_10y</th>
      <th>IVV_IJR_3d</th>
      <th>...</th>
      <th>IJH_Daily_Return_fwd_2m_CRR</th>
      <th>IJR_Daily_Return_2m_CRR</th>
      <th>IJR_Daily_Return_fwd_2m_CRR</th>
      <th>IVV_Daily_Return_3m_CRR</th>
      <th>IVV_Daily_Return_fwd_3m_CRR</th>
      <th>IJH_Daily_Return_3m_CRR</th>
      <th>IJH_Daily_Return_fwd_3m_CRR</th>
      <th>IJR_Daily_Return_3m_CRR</th>
      <th>IJR_Daily_Return_fwd_3m_CRR</th>
      <th>total_rolling_correlation_2w_decile</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2006-08-04</th>
      <td>0.98</td>
      <td>0.98</td>
      <td>0.96</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.69</td>
      <td>...</td>
      <td>0.02</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.05</td>
      <td>D7</td>
    </tr>
    <tr>
      <th>2006-08-07</th>
      <td>0.79</td>
      <td>0.89</td>
      <td>0.91</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.97</td>
      <td>...</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.05</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.05</td>
      <td>NaN</td>
      <td>0.06</td>
      <td>D4</td>
    </tr>
    <tr>
      <th>2006-08-08</th>
      <td>0.32</td>
      <td>0.93</td>
      <td>0.92</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1.00</td>
      <td>...</td>
      <td>0.05</td>
      <td>NaN</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>D5</td>
    </tr>
    <tr>
      <th>2006-08-09</th>
      <td>-0.01</td>
      <td>0.80</td>
      <td>0.93</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.74</td>
      <td>...</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.10</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.10</td>
      <td>D6</td>
    </tr>
    <tr>
      <th>2006-08-10</th>
      <td>0.99</td>
      <td>0.89</td>
      <td>0.95</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.96</td>
      <td>...</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.10</td>
      <td>D6</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-11-04</th>
      <td>-0.23</td>
      <td>0.58</td>
      <td>0.67</td>
      <td>0.64</td>
      <td>0.70</td>
      <td>0.75</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.40</td>
      <td>...</td>
      <td>NaN</td>
      <td>-0.01</td>
      <td>NaN</td>
      <td>0.00</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
      <td>D1</td>
    </tr>
    <tr>
      <th>2026-11-05</th>
      <td>0.99</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.88</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.81</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>-0.08</td>
      <td>NaN</td>
      <td>-0.07</td>
      <td>NaN</td>
      <td>D5</td>
    </tr>
    <tr>
      <th>2026-11-06</th>
      <td>0.98</td>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.81</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>1.00</td>
      <td>...</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>-0.07</td>
      <td>NaN</td>
      <td>-0.07</td>
      <td>NaN</td>
      <td>D5</td>
    </tr>
    <tr>
      <th>2026-11-09</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.90</td>
      <td>0.83</td>
      <td>0.81</td>
      <td>0.82</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.01</td>
      <td>NaN</td>
      <td>-0.02</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>D6</td>
    </tr>
    <tr>
      <th>2026-11-10</th>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.91</td>
      <td>0.83</td>
      <td>0.81</td>
      <td>0.82</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>NaN</td>
      <td>-0.00</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>D6</td>
    </tr>
  </tbody>
</table>
<p>5099 rows × 82 columns</p>
</div>



```python
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
```


    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_43_0.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_43_1.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_43_2.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_43_3.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_43_4.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_43_5.png)
    


With all three of these, we have a mean forward return of 3%, with the -1 standard deviation being around -2/-3%, and the +1 standard deviation being around 13-16%. This shows that while the average expected return is modestly positive, there is a range of potential outcomes.

## Trading Strategy

Next, let's develop a simple trading strategy. When the total rolling correlation hits the 10th decile, we will open a long position in the fund, hold the position for exactly 3 months, and then close it. We'll run the strategy separately for each of six funds: IVV, IJH, and IJR, along with their 2x leveraged counterparts SSO, MVV, and SAA. Here's the complete details:

* Use the 10th decile of the total rolling correlation as the signal for entering a trade.
* Position sizing: we always go fully long on the fund when a signal occurs, and we do not scale in or out.
* Entry: when the 2w total correlation decile is D10 on day i, buy the fund at that day's close.
* Exit: hold for exactly 63 trading days (return_windows["3m"]), then sell at that day's close.
* Overlapping signals: a D10 day that comes while a position is open is ignored. If the exit day is itself a D10 day, the strategy buys again, so the position just continues.
* Shared signal: the signal comes from the total correlation across IVV, IJH, and IJR, so the entry and exit dates are the same for all six funds. Only the returns differ. The leveraged funds are only traded, and do not feed into the signal.
* Inception dates: SAA's return history starts on January 26, 2007, after the first trade closes, so its statistics start from that date and cover 43 trades instead of 44.
* Settings: strategy_tickers, signal_decile and hold_days are variables at the top, so we can easily modify them to try other combinations.

We'll start with the strategy, and the complete list of trades.


```python
# Strategy parameters
strategy_tickers = tickers + leveraged_tickers
signal_column = "total_rolling_correlation_2w_decile"
signal_decile = "D10"
hold_days = return_windows["3m"]  # 63 trading days

# Returns stay NaN before a fund's inception date (SAA starts after the first signals), so that those
# days and trades are left out of that fund's statistics rather than being counted as flat.
strategy_df = total_rolling_corr_with_returns[["total_rolling_correlation_2w", signal_column]].join(
    fund_data[[f"{ticker}_Daily_Return" for ticker in strategy_tickers]]
)
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
```


Table 11: Days in D10 With an Open Position



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>total_rolling_correlation_2w</th>
      <th>total_rolling_correlation_2w_decile</th>
      <th>IVV_Daily_Return</th>
      <th>IJH_Daily_Return</th>
      <th>IJR_Daily_Return</th>
      <th>SSO_Daily_Return</th>
      <th>MVV_Daily_Return</th>
      <th>SAA_Daily_Return</th>
      <th>Signal</th>
      <th>Position</th>
      <th>IVV_Strategy_Return</th>
      <th>IJH_Strategy_Return</th>
      <th>IJR_Strategy_Return</th>
      <th>SSO_Strategy_Return</th>
      <th>MVV_Strategy_Return</th>
      <th>SAA_Strategy_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2006-08-21</th>
      <td>0.98</td>
      <td>D10</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>-0.00</td>
      <td>-0.02</td>
      <td>NaN</td>
      <td>True</td>
      <td>1.00</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>-0.00</td>
      <td>-0.02</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2007-02-28</th>
      <td>0.98</td>
      <td>D10</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.02</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.02</td>
      <td>0.01</td>
      <td>0.01</td>
    </tr>
    <tr>
      <th>2007-03-01</th>
      <td>0.98</td>
      <td>D10</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>-0.00</td>
      <td>True</td>
      <td>1.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>2007-03-02</th>
      <td>0.97</td>
      <td>D10</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>-0.03</td>
      <td>-0.03</td>
      <td>-0.04</td>
      <td>True</td>
      <td>1.00</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>-0.03</td>
      <td>-0.03</td>
      <td>-0.04</td>
    </tr>
    <tr>
      <th>2007-03-06</th>
      <td>0.97</td>
      <td>D10</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.04</td>
      <td>0.05</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.04</td>
      <td>0.05</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2025-04-22</th>
      <td>0.99</td>
      <td>D10</td>
      <td>0.03</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.03</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.05</td>
    </tr>
    <tr>
      <th>2025-04-23</th>
      <td>0.99</td>
      <td>D10</td>
      <td>0.02</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.02</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>2026-04-09</th>
      <td>0.99</td>
      <td>D10</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.02</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.02</td>
    </tr>
    <tr>
      <th>2026-04-10</th>
      <td>0.99</td>
      <td>D10</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>True</td>
      <td>1.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>-0.02</td>
    </tr>
    <tr>
      <th>2026-04-13</th>
      <td>0.98</td>
      <td>D10</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.02</td>
    </tr>
  </tbody>
</table>
<p>473 rows × 16 columns</p>
</div>



Table 12: Strategy Trades



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Entry Date</th>
      <th>Exit Date</th>
      <th>Entry Correlation</th>
      <th>Days Held</th>
      <th>Open</th>
      <th>IVV Return</th>
      <th>IJH Return</th>
      <th>IJR Return</th>
      <th>SSO Return</th>
      <th>MVV Return</th>
      <th>SAA Return</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2006-08-17</td>
      <td>2006-11-15</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.08</td>
      <td>0.08</td>
      <td>0.10</td>
      <td>0.15</td>
      <td>0.15</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2007-02-27</td>
      <td>2007-05-29</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.10</td>
      <td>0.09</td>
      <td>0.08</td>
      <td>0.18</td>
      <td>0.15</td>
      <td>0.15</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2007-06-14</td>
      <td>2007-09-13</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>-0.02</td>
      <td>-0.05</td>
      <td>-0.05</td>
      <td>-0.07</td>
      <td>-0.12</td>
      <td>-0.12</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2007-09-27</td>
      <td>2007-12-27</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>-0.03</td>
      <td>-0.03</td>
      <td>-0.07</td>
      <td>-0.08</td>
      <td>-0.07</td>
      <td>-0.15</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2008-03-07</td>
      <td>2008-06-06</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.06</td>
      <td>0.15</td>
      <td>0.11</td>
      <td>0.09</td>
      <td>0.30</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2008-06-06</td>
      <td>2008-09-05</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>-0.08</td>
      <td>-0.10</td>
      <td>-0.03</td>
      <td>-0.17</td>
      <td>-0.21</td>
      <td>-0.08</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2008-11-14</td>
      <td>2009-02-18</td>
      <td>0.97</td>
      <td>63</td>
      <td>False</td>
      <td>-0.09</td>
      <td>-0.03</td>
      <td>-0.08</td>
      <td>-0.22</td>
      <td>-0.14</td>
      <td>-0.23</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2009-02-24</td>
      <td>2009-05-26</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.19</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.36</td>
      <td>0.43</td>
      <td>0.43</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2009-05-27</td>
      <td>2009-08-25</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.16</td>
      <td>0.18</td>
      <td>0.19</td>
      <td>0.32</td>
      <td>0.37</td>
      <td>0.39</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2009-08-25</td>
      <td>2009-11-23</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>0.08</td>
      <td>0.05</td>
      <td>0.03</td>
      <td>0.16</td>
      <td>0.10</td>
      <td>0.04</td>
    </tr>
    <tr>
      <th>10</th>
      <td>2009-11-23</td>
      <td>2010-02-25</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.00</td>
      <td>0.07</td>
      <td>0.07</td>
      <td>-0.00</td>
      <td>0.13</td>
      <td>0.13</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2010-05-10</td>
      <td>2010-08-09</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>-0.05</td>
      <td>-0.06</td>
      <td>-0.06</td>
      <td>-0.11</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2010-09-03</td>
      <td>2010-12-03</td>
      <td>0.97</td>
      <td>63</td>
      <td>False</td>
      <td>0.11</td>
      <td>0.16</td>
      <td>0.17</td>
      <td>0.23</td>
      <td>0.34</td>
      <td>0.36</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2011-02-09</td>
      <td>2011-05-11</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>0.02</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.04</td>
      <td>0.09</td>
      <td>0.09</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2011-06-01</td>
      <td>2011-08-30</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>-0.07</td>
      <td>-0.10</td>
      <td>-0.10</td>
      <td>-0.16</td>
      <td>-0.23</td>
      <td>-0.21</td>
    </tr>
    <tr>
      <th>15</th>
      <td>2011-08-30</td>
      <td>2011-11-29</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>-0.01</td>
      <td>-0.03</td>
      <td>-0.02</td>
      <td>-0.04</td>
      <td>-0.09</td>
      <td>-0.08</td>
    </tr>
    <tr>
      <th>16</th>
      <td>2011-11-30</td>
      <td>2012-03-02</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>0.11</td>
      <td>0.11</td>
      <td>0.09</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>0.18</td>
    </tr>
    <tr>
      <th>17</th>
      <td>2012-04-18</td>
      <td>2012-07-18</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>-0.00</td>
      <td>-0.03</td>
      <td>0.00</td>
      <td>-0.02</td>
      <td>-0.06</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>18</th>
      <td>2012-11-19</td>
      <td>2013-02-21</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>0.09</td>
      <td>0.13</td>
      <td>0.14</td>
      <td>0.18</td>
      <td>0.27</td>
      <td>0.29</td>
    </tr>
    <tr>
      <th>19</th>
      <td>2013-02-21</td>
      <td>2013-05-22</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.11</td>
      <td>0.10</td>
      <td>0.09</td>
      <td>0.22</td>
      <td>0.18</td>
      <td>0.18</td>
    </tr>
    <tr>
      <th>20</th>
      <td>2013-06-20</td>
      <td>2013-09-19</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.09</td>
      <td>0.10</td>
      <td>0.12</td>
      <td>0.18</td>
      <td>0.21</td>
      <td>0.25</td>
    </tr>
    <tr>
      <th>21</th>
      <td>2013-10-14</td>
      <td>2014-01-14</td>
      <td>0.97</td>
      <td>63</td>
      <td>False</td>
      <td>0.08</td>
      <td>0.07</td>
      <td>0.07</td>
      <td>0.16</td>
      <td>0.13</td>
      <td>0.14</td>
    </tr>
    <tr>
      <th>22</th>
      <td>2014-01-24</td>
      <td>2014-04-25</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>0.05</td>
      <td>0.03</td>
      <td>0.01</td>
      <td>0.09</td>
      <td>0.04</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>23</th>
      <td>2015-07-13</td>
      <td>2015-10-09</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>-0.04</td>
      <td>-0.04</td>
      <td>-0.05</td>
      <td>-0.08</td>
      <td>-0.10</td>
      <td>-0.10</td>
    </tr>
    <tr>
      <th>24</th>
      <td>2015-10-16</td>
      <td>2016-01-19</td>
      <td>0.97</td>
      <td>63</td>
      <td>False</td>
      <td>-0.07</td>
      <td>-0.12</td>
      <td>-0.12</td>
      <td>-0.14</td>
      <td>-0.23</td>
      <td>-0.24</td>
    </tr>
    <tr>
      <th>25</th>
      <td>2016-02-03</td>
      <td>2016-05-04</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.07</td>
      <td>0.12</td>
      <td>0.12</td>
      <td>0.15</td>
      <td>0.24</td>
      <td>0.32</td>
    </tr>
    <tr>
      <th>26</th>
      <td>2016-06-13</td>
      <td>2016-09-12</td>
      <td>0.97</td>
      <td>63</td>
      <td>False</td>
      <td>0.04</td>
      <td>0.05</td>
      <td>0.06</td>
      <td>0.08</td>
      <td>0.09</td>
      <td>0.09</td>
    </tr>
    <tr>
      <th>27</th>
      <td>2016-09-21</td>
      <td>2016-12-20</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.06</td>
      <td>0.10</td>
      <td>0.14</td>
      <td>0.11</td>
      <td>0.19</td>
      <td>0.31</td>
    </tr>
    <tr>
      <th>28</th>
      <td>2017-08-30</td>
      <td>2017-11-29</td>
      <td>0.97</td>
      <td>63</td>
      <td>False</td>
      <td>0.07</td>
      <td>0.10</td>
      <td>0.14</td>
      <td>0.14</td>
      <td>0.21</td>
      <td>0.24</td>
    </tr>
    <tr>
      <th>29</th>
      <td>2017-12-29</td>
      <td>2018-04-03</td>
      <td>0.97</td>
      <td>63</td>
      <td>False</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>-0.00</td>
      <td>-0.06</td>
      <td>-0.05</td>
      <td>-0.06</td>
    </tr>
    <tr>
      <th>30</th>
      <td>2018-04-03</td>
      <td>2018-07-02</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.11</td>
      <td>0.09</td>
      <td>0.10</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>31</th>
      <td>2018-12-12</td>
      <td>2019-03-15</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.07</td>
      <td>0.07</td>
      <td>0.05</td>
      <td>0.12</td>
      <td>0.13</td>
      <td>0.07</td>
    </tr>
    <tr>
      <th>32</th>
      <td>2019-03-22</td>
      <td>2019-06-21</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.06</td>
      <td>0.04</td>
      <td>0.02</td>
      <td>0.11</td>
      <td>0.08</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>33</th>
      <td>2019-08-13</td>
      <td>2019-11-11</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.06</td>
      <td>0.06</td>
      <td>0.06</td>
      <td>0.11</td>
      <td>0.10</td>
      <td>0.11</td>
    </tr>
    <tr>
      <th>34</th>
      <td>2020-03-04</td>
      <td>2020-06-03</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.00</td>
      <td>-0.02</td>
      <td>-0.07</td>
      <td>-0.09</td>
      <td>-0.17</td>
      <td>-0.26</td>
    </tr>
    <tr>
      <th>35</th>
      <td>2020-06-24</td>
      <td>2020-09-23</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>0.07</td>
      <td>0.04</td>
      <td>0.03</td>
      <td>0.12</td>
      <td>0.06</td>
      <td>0.05</td>
    </tr>
    <tr>
      <th>36</th>
      <td>2022-02-28</td>
      <td>2022-05-27</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>-0.05</td>
      <td>-0.04</td>
      <td>-0.05</td>
      <td>-0.11</td>
      <td>-0.11</td>
      <td>-0.12</td>
    </tr>
    <tr>
      <th>37</th>
      <td>2022-06-09</td>
      <td>2022-09-09</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>-0.02</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>-0.06</td>
    </tr>
    <tr>
      <th>38</th>
      <td>2022-09-20</td>
      <td>2022-12-19</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>-0.01</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>-0.04</td>
      <td>-0.01</td>
      <td>-0.02</td>
    </tr>
    <tr>
      <th>39</th>
      <td>2022-12-19</td>
      <td>2023-03-22</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.04</td>
      <td>0.01</td>
      <td>-0.00</td>
      <td>0.05</td>
      <td>-0.01</td>
      <td>-0.04</td>
    </tr>
    <tr>
      <th>40</th>
      <td>2024-08-14</td>
      <td>2024-11-12</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.10</td>
      <td>0.12</td>
      <td>0.13</td>
      <td>0.19</td>
      <td>0.22</td>
      <td>0.24</td>
    </tr>
    <tr>
      <th>41</th>
      <td>2024-12-23</td>
      <td>2025-03-27</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>-0.04</td>
      <td>-0.05</td>
      <td>-0.08</td>
      <td>-0.11</td>
      <td>-0.12</td>
      <td>-0.17</td>
    </tr>
    <tr>
      <th>42</th>
      <td>2025-04-03</td>
      <td>2025-07-07</td>
      <td>0.98</td>
      <td>63</td>
      <td>False</td>
      <td>0.16</td>
      <td>0.14</td>
      <td>0.13</td>
      <td>0.29</td>
      <td>0.25</td>
      <td>0.22</td>
    </tr>
    <tr>
      <th>43</th>
      <td>2026-04-08</td>
      <td>2026-07-09</td>
      <td>0.99</td>
      <td>63</td>
      <td>False</td>
      <td>0.12</td>
      <td>0.08</td>
      <td>0.12</td>
      <td>0.22</td>
      <td>0.14</td>
      <td>0.24</td>
    </tr>
  </tbody>
</table>
</div>


Next, here's the statistics for win rate, average return, max gain, and max loss.


```python
# Trade summary
closed_trades = trades_df[~trades_df["Open"]]

print(f"Total trades: {len(trades_df)} ({len(closed_trades)} closed)")
print(f"Time in market: {strategy_df['Position'].mean() * 100:.2f}%")

for ticker in strategy_tickers:
    trade_returns = closed_trades[f"{ticker} Return"].dropna()
    print(f"\n{ticker}:")
    print(f"  Closed trades: {len(trade_returns)}")
    print(f"  Win rate (closed trades): {(trade_returns > 0).mean() * 100:.2f}%")
    print(f"  Average return per closed trade: {trade_returns.mean() * 100:.2f}%")
    print(f"  Max trade gain: {trade_returns.max() * 100:.2f}%")
    print(f"  Max trade loss: {trade_returns.min() * 100:.2f}%")
```

    Total trades: 44 (44 closed)
    Time in market: 54.36%
    
    IVV:
      Closed trades: 44
      Win rate (closed trades): 68.18%
      Average return per closed trade: 3.96%
      Max trade gain: 18.70%
      Max trade loss: -9.01%
    
    IJH:
      Closed trades: 44
      Win rate (closed trades): 68.18%
      Average return per closed trade: 4.37%
      Max trade gain: 23.09%
      Max trade loss: -11.54%
    
    IJR:
      Closed trades: 44
      Win rate (closed trades): 65.91%
      Average return per closed trade: 4.32%
      Max trade gain: 23.17%
      Max trade loss: -11.87%
    
    SSO:
      Closed trades: 44
      Win rate (closed trades): 63.64%
      Average return per closed trade: 6.60%
      Max trade gain: 35.67%
      Max trade loss: -21.76%
    
    MVV:
      Closed trades: 44
      Win rate (closed trades): 63.64%
      Average return per closed trade: 7.14%
      Max trade gain: 43.41%
      Max trade loss: -22.68%
    
    SAA:
      Closed trades: 43
      Win rate (closed trades): 60.47%
      Average return per closed trade: 6.75%
      Max trade gain: 43.02%
      Max trade loss: -25.61%


Now we can compare the summary stats for the different funds and see how the strategy performed across all six funds.


```python
# Compare each strategy against buy and hold for the same period
strategy_stats = pd.concat(
    [
        summary_stats(
            fund_list=[ticker],
            df=strategy_df[[return_column]].dropna(),
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
```


Table 13: Strategy vs Buy and Hold Summary Statistics



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Number of Observations</th>
      <th>Data Start Date</th>
      <th>Data End Date</th>
      <th>Annual Mean Return (Arithmetic)</th>
      <th>Annualized Volatility</th>
      <th>Annualized Sharpe Ratio</th>
      <th>CAGR (Geometric)</th>
      <th>Daily Max Return</th>
      <th>Daily Max Return (Date)</th>
      <th>Daily Min Return</th>
      <th>Daily Min Return (Date)</th>
      <th>Max Drawdown</th>
      <th>Peak</th>
      <th>Trough</th>
      <th>Recovery Date</th>
      <th>Calendar Days to Recovery</th>
      <th>MAR Ratio</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>IVV_Strategy_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.09</td>
      <td>0.15</td>
      <td>0.59</td>
      <td>0.08</td>
      <td>0.10</td>
      <td>2025-04-09</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.30</td>
      <td>2008-05-19</td>
      <td>2009-03-09</td>
      <td>2009-06-01</td>
      <td>84.00</td>
      <td>0.28</td>
    </tr>
    <tr>
      <th>IVV_Daily_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.12</td>
      <td>0.19</td>
      <td>0.65</td>
      <td>0.11</td>
      <td>0.11</td>
      <td>2008-10-28</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.55</td>
      <td>2007-10-09</td>
      <td>2009-03-09</td>
      <td>2012-08-16</td>
      <td>1256.00</td>
      <td>0.20</td>
    </tr>
    <tr>
      <th>IJH_Strategy_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.10</td>
      <td>0.18</td>
      <td>0.58</td>
      <td>0.09</td>
      <td>0.11</td>
      <td>2020-03-24</td>
      <td>-0.14</td>
      <td>2020-03-16</td>
      <td>-0.36</td>
      <td>2019-11-08</td>
      <td>2020-03-23</td>
      <td>2020-06-30</td>
      <td>99.00</td>
      <td>0.25</td>
    </tr>
    <tr>
      <th>IJH_Daily_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.12</td>
      <td>0.22</td>
      <td>0.54</td>
      <td>0.10</td>
      <td>0.11</td>
      <td>2020-03-24</td>
      <td>-0.14</td>
      <td>2020-03-16</td>
      <td>-0.55</td>
      <td>2007-06-04</td>
      <td>2009-03-09</td>
      <td>2010-12-02</td>
      <td>633.00</td>
      <td>0.18</td>
    </tr>
    <tr>
      <th>IJR_Strategy_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.10</td>
      <td>0.19</td>
      <td>0.54</td>
      <td>0.09</td>
      <td>0.09</td>
      <td>2025-04-09</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.35</td>
      <td>2019-11-05</td>
      <td>2020-03-23</td>
      <td>2020-07-21</td>
      <td>120.00</td>
      <td>0.25</td>
    </tr>
    <tr>
      <th>IJR_Daily_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.12</td>
      <td>0.24</td>
      <td>0.50</td>
      <td>0.09</td>
      <td>0.09</td>
      <td>2025-04-09</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.58</td>
      <td>2007-07-19</td>
      <td>2009-03-09</td>
      <td>2011-02-07</td>
      <td>700.00</td>
      <td>0.16</td>
    </tr>
    <tr>
      <th>SSO_Strategy_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.17</td>
      <td>0.31</td>
      <td>0.54</td>
      <td>0.13</td>
      <td>0.19</td>
      <td>2020-03-24</td>
      <td>-0.23</td>
      <td>2020-03-16</td>
      <td>-0.55</td>
      <td>2007-07-13</td>
      <td>2009-03-09</td>
      <td>2009-08-07</td>
      <td>151.00</td>
      <td>0.23</td>
    </tr>
    <tr>
      <th>SSO_Daily_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.21</td>
      <td>0.38</td>
      <td>0.56</td>
      <td>0.15</td>
      <td>0.22</td>
      <td>2008-10-13</td>
      <td>-0.23</td>
      <td>2020-03-16</td>
      <td>-0.85</td>
      <td>2007-10-09</td>
      <td>2009-03-09</td>
      <td>2013-10-22</td>
      <td>1688.00</td>
      <td>0.18</td>
    </tr>
    <tr>
      <th>MVV_Strategy_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.19</td>
      <td>0.36</td>
      <td>0.53</td>
      <td>0.13</td>
      <td>0.20</td>
      <td>2025-04-09</td>
      <td>-0.29</td>
      <td>2020-03-16</td>
      <td>-0.62</td>
      <td>2019-11-05</td>
      <td>2020-03-23</td>
      <td>2020-08-05</td>
      <td>135.00</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>MVV_Daily_Return</th>
      <td>5099</td>
      <td>2006-08-04</td>
      <td>2026-11-10</td>
      <td>0.20</td>
      <td>0.44</td>
      <td>0.46</td>
      <td>0.11</td>
      <td>0.25</td>
      <td>2008-10-13</td>
      <td>-0.29</td>
      <td>2020-03-16</td>
      <td>-0.86</td>
      <td>2007-06-04</td>
      <td>2009-03-09</td>
      <td>2013-04-30</td>
      <td>1513.00</td>
      <td>0.13</td>
    </tr>
    <tr>
      <th>SAA_Strategy_Return</th>
      <td>4980</td>
      <td>2007-01-26</td>
      <td>2026-11-10</td>
      <td>0.18</td>
      <td>0.38</td>
      <td>0.48</td>
      <td>0.12</td>
      <td>0.18</td>
      <td>2025-04-09</td>
      <td>-0.25</td>
      <td>2020-03-16</td>
      <td>-0.61</td>
      <td>2019-11-05</td>
      <td>2020-03-23</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>0.19</td>
    </tr>
    <tr>
      <th>SAA_Daily_Return</th>
      <td>4980</td>
      <td>2007-01-26</td>
      <td>2026-11-10</td>
      <td>0.20</td>
      <td>0.48</td>
      <td>0.42</td>
      <td>0.09</td>
      <td>0.18</td>
      <td>2025-04-09</td>
      <td>-0.25</td>
      <td>2020-03-16</td>
      <td>-0.87</td>
      <td>2007-06-04</td>
      <td>2009-03-09</td>
      <td>2013-07-09</td>
      <td>1583.00</td>
      <td>0.10</td>
    </tr>
  </tbody>
</table>
</div>


And finally, the plots for the cumulative returns and drawdowns.


```python
# Cumulative returns for each strategy and buy and hold
for ticker in strategy_tickers:
    strategy_df[f"{ticker}_Strategy_Cumulative_Return"] = (1 + strategy_df[f"{ticker}_Strategy_Return"]).cumprod() - 1
    strategy_df[f"{ticker}_Buy_Hold_Cumulative_Return"] = (1 + strategy_df[f"{ticker}_Daily_Return"]).cumprod() - 1

for fund_group, group_tickers in {"Unleveraged": tickers, "2x Leveraged": leveraged_tickers}.items():
    plot_time_series(
        df=strategy_df,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[f"{ticker}_Strategy_Cumulative_Return" for ticker in group_tickers]
        + [f"{ticker}_Buy_Hold_Cumulative_Return" for ticker in group_tickers],
        title=f"Figure {next(figure_number)}: Total Rolling Correlation {signal_decile} Strategies vs Buy and Hold ({fund_group} Funds)",
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
```


    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_53_0.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_53_1.png)
    



```python
# Drawdowns for each strategy and buy and hold, measured from the running peak of each equity curve
for ticker in strategy_tickers:
    strategy_equity = (1 + strategy_df[f"{ticker}_Strategy_Return"]).cumprod()
    buy_hold_equity = (1 + strategy_df[f"{ticker}_Daily_Return"]).cumprod()

    strategy_df[f"{ticker}_Strategy_Drawdown"] = strategy_equity / strategy_equity.cummax() - 1
    strategy_df[f"{ticker}_Buy_Hold_Drawdown"] = buy_hold_equity / buy_hold_equity.cummax() - 1

for fund_group, group_tickers in {"Unleveraged": tickers, "2x Leveraged": leveraged_tickers}.items():
    plot_time_series(
        df=strategy_df,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[f"{ticker}_Strategy_Drawdown" for ticker in group_tickers]
        + [f"{ticker}_Buy_Hold_Drawdown" for ticker in group_tickers],
        title=f"Figure {next(figure_number)}: Total Rolling Correlation {signal_decile} Strategies vs Buy and Hold Drawdowns ({fund_group} Funds)",
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
```


    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_54_0.png)
    



    
![png](asset-class-return-correlations-part-2_files/asset-class-return-correlations-part-2_54_1.png)
    


Starting with the unleveraged funds, we end up with 44 trades over the 20 year period, with a win rate of 68% for IVV and IJH, and 66% for IJR, not bad overall. Since the signal is shared, all three strategies spend just under 55% of their time in the market, which really gives us an opportunity to use our capital the other 45% of the time, either in a risk free asset or another strategy altogether.

For IVV, with a CAGR of 8%, we underperform the buy-and-hold strategy over the same period, but we also experience lower volatility (15% vs 19%), and much lower max drawdowns (30% vs 55%). Our strategy gives us a MAR ratio of 0.28, vs 0.20 for the buy-and-hold strategy.

IJH and IJR tell a similar story, but the gap in CAGR is much smaller:

* IJH: a CAGR of 9.1% vs 9.8% for buy-and-hold, with lower volatility (18% vs 22%), lower max drawdowns (36% vs 55%), and a MAR ratio of 0.25 vs 0.18.
* IJR: a CAGR of 8.9% vs 9.4% for buy-and-hold, with lower volatility (19% vs 24%), lower max drawdowns (35% vs 58%), and a MAR ratio of 0.25 vs 0.16.

For IJH and IJR, we give up less than 1% of CAGR per year in exchange for the reduced risk, and both strategies also have a higher Sharpe ratio than their buy-and-hold counterparts, which is not the case for IVV.

The difference in CAGR does add up over the long term, the effect of which we can see in the cumulative return plot, particularly for IVV.

The drawdown plot further illustrates the reduced risk of the strategies compared to the buy-and-hold approach, highlighting the lower maximum drawdowns experienced over the same period. During the GFC, the IVV strategy experienced its max drawdown of 30%, which was significantly lower than that of the buy-and-hold strategy at 55%. Interestingly, the max drawdowns for the IJH and IJR strategies came during the COVID crash in early 2020 rather than the GFC, while all three buy-and-hold strategies saw their max drawdowns during the GFC.

Moving on to the 2x leveraged funds, the win rates are lower (64% for SSO and MVV, and 60% for SAA over its 43 trades), but the results relative to buy-and-hold are more interesting:

* SSO: a CAGR of 12.8% vs 15.6% for buy-and-hold, with lower volatility (31% vs 38%), lower max drawdowns (55% vs 85%), and a MAR ratio of 0.23 vs 0.18.
* MVV: a CAGR of 13.2% vs 11.0% for buy-and-hold, with lower volatility (36% vs 44%), lower max drawdowns (62% vs 86%), and a MAR ratio of 0.21 vs 0.13.
* SAA: a CAGR of 11.6% vs 8.9% for buy-and-hold, with lower volatility (38% vs 48%), lower max drawdowns (61% vs 87%), and a MAR ratio of 0.19 vs 0.10.

For MVV and SAA, the strategy beats buy-and-hold on CAGR, despite being out of the market about 45% of the time. As with IVV, SSO gives up CAGR and has a slightly lower Sharpe ratio than buy-and-hold, while MVV and SAA have higher Sharpe ratios. Even with the strategy, the leveraged funds still see max drawdowns of more than 50%, so the reduced risk is relative. The max drawdown for the SSO strategy came during the GFC, and for the MVV and SAA strategies it came during the COVID crash, matching the pattern we see with the unleveraged funds.

## Conclusion

Overall, we delved into the different deciles of a "total correlation" metric, assembled from the rolling correlations of 3 well known US equity ETFs. This analysis, including comparison to a baseline, gave us insight into where the total correlations could be used to improve our ability to time market entries and exits. Finally, we built a simple trading strategy using a single total correlation window and decile and a single future return window, as a proof of concept for how these insights could be applied in practice. This strategy, while underperforming buy-and-hold over the long-term for IVV, IJH, IJR, and SSO, did have lower volatility and drawdowns for all six funds, and outperformed buy-and-hold for MVV and SAA, demonstrating the potential risk management benefits of incorporating total correlation information into trading decisions.

## Future Investigation

None

## References

None
