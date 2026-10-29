---
title: Data Pipelining With Coinbase
description: Acquiring and managing minute, hour, and daily crypto data from Coinbase.
summary: Acquiring and managing minute, hour, and daily crypto data from Coinbase.
slug: data-pipelining-with-coinbase
date: 2025-07-06 00:00:01+0000
lastmod: 2026-08-08 00:00:01+0000
feature: behnam-norouzi-RDXcFY5g5O4-unsplash.jpg
coverCaption: Photo by <a href="https://unsplash.com/@behy_studio?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Behnam Norouzi</a> on <a href="https://unsplash.com/photos/a-computer-screen-displaying-a-stock-market-chart-RDXcFY5g5O4?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
draft: false
topics: [
    "Coinbase", 
    "Pandas", 
    "Python", 
]
---

## Post Updates

Update 8/8/2026: Reworked `coinbase_pull_data` so that a new record is built from 2010 forward and an existing record resumes from its last stored candle, rather than the initial pull starting at a fixed year and updates re-fetching a caller-supplied range. Revised the walkthrough of that function to match.

Update 8/6/2026: Clarified how the initial pull differs from an incremental update, documented the asset filtering performed by `coinbase_pull_data`, reordered the function list to build from the lowest-level function upward, and replaced the historical candles example with an hourly range that returns more than a single row.

## Introduction

This post covers how I collect and store minute, hour, and daily crypto asset data from Coinbase. Since I first published it I have expanded the walkthrough to cover how the initial pull differs from an incremental update, and the filtering that gets applied to the asset list along the way.

The work is split across four functions that build on one another. `coinbase_fetch_historical_candles` wraps a single request to the Coinbase Exchange candles endpoint. `coinbase_fetch_full_history` pages that endpoint to cover an arbitrary date range. `coinbase_fetch_available_products` lists the tradeable pairs. And `coinbase_pull_data` combines all three to maintain a directory of pickle files on disk, resuming an existing data file from its last stored candle, or building a new record from scratch where none exists.

The first three functions are executed below. `coinbase_pull_data` is shown but not run, since it writes to the filesystem and can run for a long time against a full asset list.

## Python Imports


```python
# Standard Library
import datetime
import os
import sys
import warnings

from datetime import datetime
from pathlib import Path

# Suppress warnings
warnings.filterwarnings("ignore")
```


```python
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
```

## Python Functions

Here are the functions needed for this project, listed in the order they build on one another:

* [coinbase_fetch_available_products](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_available_products): Fetch available products from Coinbase Exchange API.
* [coinbase_fetch_historical_candles](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_historical_candles): Fetch historical candle data for a given product from Coinbase Exchange API.
* [coinbase_fetch_full_history](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_full_history): Fetch full historical data for a given product from Coinbase Exchange API.
* [coinbase_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_pull_data): Update existing record or pull full historical data for a given product from Coinbase Exchange API.


```python
from coinbase_fetch_available_products import coinbase_fetch_available_products
from coinbase_fetch_historical_candles import coinbase_fetch_historical_candles
from coinbase_fetch_full_history import coinbase_fetch_full_history
from coinbase_pull_data import coinbase_pull_data
```

## Function Usage

### Coinbase Fetch Available Products

This function pulls the list of available assets based on the inputs for base and quote currency. In the example below the `quote_currency` is provided as "USD", so the function returns every asset priced against USD:


```python
df = coinbase_fetch_available_products(
    base_currency=None,
    quote_currency="USD",
    status="online",
)

display(df[["id", "base_currency", "quote_currency", "status"]])
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
      <th>id</th>
      <th>base_currency</th>
      <th>quote_currency</th>
      <th>status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>655</th>
      <td>00-USD</td>
      <td>00</td>
      <td>USD</td>
      <td>online</td>
    </tr>
    <tr>
      <th>155</th>
      <td>1INCH-USD</td>
      <td>1INCH</td>
      <td>USD</td>
      <td>online</td>
    </tr>
    <tr>
      <th>497</th>
      <td>2Z-USD</td>
      <td>2Z</td>
      <td>USD</td>
      <td>online</td>
    </tr>
    <tr>
      <th>815</th>
      <td>A8-USD</td>
      <td>A8</td>
      <td>USD</td>
      <td>online</td>
    </tr>
    <tr>
      <th>563</th>
      <td>AAVE-USD</td>
      <td>AAVE</td>
      <td>USD</td>
      <td>online</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>608</th>
      <td>ZKC-USD</td>
      <td>ZKC</td>
      <td>USD</td>
      <td>online</td>
    </tr>
    <tr>
      <th>835</th>
      <td>ZKP-USD</td>
      <td>ZKP</td>
      <td>USD</td>
      <td>online</td>
    </tr>
    <tr>
      <th>778</th>
      <td>ZORA-USD</td>
      <td>ZORA</td>
      <td>USD</td>
      <td>online</td>
    </tr>
    <tr>
      <th>282</th>
      <td>ZRO-USD</td>
      <td>ZRO</td>
      <td>USD</td>
      <td>online</td>
    </tr>
    <tr>
      <th>20</th>
      <td>ZRX-USD</td>
      <td>ZRX</td>
      <td>USD</td>
      <td>online</td>
    </tr>
  </tbody>
</table>
<p>402 rows × 4 columns</p>
</div>


The API returns eighteen columns per product, but the four shown above are the ones that matter downstream, and are the same four that `coinbase_pull_data` prints when it builds its working list.

### Coinbase Fetch Historical Candles

This is the lowest-level of the four functions, and maps to a single request against the Coinbase Exchange candles endpoint. It returns the date/time, open, high, low, close, and volume for each period in the requested range. The example below pulls hourly candles from the start of 2025:


```python
df = coinbase_fetch_historical_candles(
    product_id="BTC-USD",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 1, 1, 6),
    granularity=3_600,
)

display(df)
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
      <th>time</th>
      <th>low</th>
      <th>high</th>
      <th>open</th>
      <th>close</th>
      <th>volume</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2025-01-01 00:00:00</td>
      <td>93281.63</td>
      <td>94321.25</td>
      <td>93347.59</td>
      <td>94209.02</td>
      <td>337.581664</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2025-01-01 01:00:00</td>
      <td>93393.06</td>
      <td>94224.30</td>
      <td>94207.31</td>
      <td>93423.47</td>
      <td>198.579180</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2025-01-01 02:00:00</td>
      <td>93400.00</td>
      <td>93894.04</td>
      <td>93423.48</td>
      <td>93882.09</td>
      <td>154.768788</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2025-01-01 03:00:00</td>
      <td>93524.35</td>
      <td>93885.00</td>
      <td>93885.00</td>
      <td>93635.54</td>
      <td>127.391075</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2025-01-01 04:00:00</td>
      <td>93305.54</td>
      <td>93637.33</td>
      <td>93635.54</td>
      <td>93358.58</td>
      <td>257.394980</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2025-01-01 05:00:00</td>
      <td>93323.88</td>
      <td>93708.79</td>
      <td>93358.33</td>
      <td>93572.80</td>
      <td>146.990291</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2025-01-01 06:00:00</td>
      <td>93354.99</td>
      <td>93575.73</td>
      <td>93575.72</td>
      <td>93551.21</td>
      <td>138.098835</td>
    </tr>
  </tbody>
</table>
</div>


Two details are worth noting here. The endpoint returns at most 300 candles per request no matter how wide a range is asked for, which is the constraint that the next function exists to work around. And the response arrives in reverse chronological order, so the function reverses it before building the dataframe. Rate limiting (HTTP 429) is retried up to five times with an exponential backoff.

### Coinbase Fetch Full History

This function pulls an arbitrary date range for a specified asset by paging the function above. Because a single request is capped at 300 candles, it walks the range in windows of `granularity * 300` seconds, advancing from the timestamp of the last candle it received and pausing 0.2 seconds between requests to stay within the rate limits. The individual responses are concatenated into one dataframe, so a range of years is handled exactly the same way as the single month below:


```python
df = coinbase_fetch_full_history(
    product_id="BTC-USD",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 1, 31),
    granularity=86_400,
)

display(df)
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
      <th>time</th>
      <th>low</th>
      <th>high</th>
      <th>open</th>
      <th>close</th>
      <th>volume</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2025-01-01</td>
      <td>92743.63</td>
      <td>94960.91</td>
      <td>93347.59</td>
      <td>94383.59</td>
      <td>6871.738482</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2025-01-02</td>
      <td>94177.00</td>
      <td>97776.99</td>
      <td>94383.59</td>
      <td>96903.19</td>
      <td>10912.473840</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2025-01-03</td>
      <td>96016.63</td>
      <td>98969.92</td>
      <td>96905.48</td>
      <td>98136.51</td>
      <td>9021.885382</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2025-01-04</td>
      <td>97516.65</td>
      <td>98761.02</td>
      <td>98139.85</td>
      <td>98209.85</td>
      <td>2742.089606</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2025-01-05</td>
      <td>97250.00</td>
      <td>98814.00</td>
      <td>98209.85</td>
      <td>98345.33</td>
      <td>2377.921759</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2025-01-06</td>
      <td>97900.00</td>
      <td>102500.00</td>
      <td>98347.65</td>
      <td>102279.41</td>
      <td>15173.556068</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2025-01-07</td>
      <td>96105.11</td>
      <td>102735.99</td>
      <td>102279.41</td>
      <td>96941.98</td>
      <td>16587.286922</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2025-01-08</td>
      <td>92500.00</td>
      <td>97254.35</td>
      <td>96941.98</td>
      <td>95036.63</td>
      <td>14182.297395</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2025-01-09</td>
      <td>91187.00</td>
      <td>95363.26</td>
      <td>95033.18</td>
      <td>92547.44</td>
      <td>9712.378532</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2025-01-10</td>
      <td>92209.25</td>
      <td>95862.92</td>
      <td>92547.44</td>
      <td>94701.18</td>
      <td>12634.034078</td>
    </tr>
    <tr>
      <th>10</th>
      <td>2025-01-11</td>
      <td>93804.05</td>
      <td>94983.65</td>
      <td>94701.48</td>
      <td>94565.02</td>
      <td>2638.699568</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2025-01-12</td>
      <td>93670.30</td>
      <td>95383.84</td>
      <td>94569.91</td>
      <td>94509.62</td>
      <td>2025.816130</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2025-01-13</td>
      <td>89028.64</td>
      <td>95900.00</td>
      <td>94507.24</td>
      <td>94506.45</td>
      <td>13094.863595</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2025-01-14</td>
      <td>94311.36</td>
      <td>97353.29</td>
      <td>94507.35</td>
      <td>96534.96</td>
      <td>11210.742267</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2025-01-15</td>
      <td>96400.00</td>
      <td>100716.45</td>
      <td>96534.97</td>
      <td>100510.23</td>
      <td>13610.747294</td>
    </tr>
    <tr>
      <th>15</th>
      <td>2025-01-16</td>
      <td>97277.58</td>
      <td>100880.00</td>
      <td>100504.27</td>
      <td>99981.78</td>
      <td>12312.373669</td>
    </tr>
    <tr>
      <th>16</th>
      <td>2025-01-17</td>
      <td>99937.81</td>
      <td>105970.00</td>
      <td>99981.46</td>
      <td>104107.00</td>
      <td>20518.309493</td>
    </tr>
    <tr>
      <th>17</th>
      <td>2025-01-18</td>
      <td>102233.45</td>
      <td>104933.15</td>
      <td>104107.00</td>
      <td>104435.00</td>
      <td>7835.299918</td>
    </tr>
    <tr>
      <th>18</th>
      <td>2025-01-19</td>
      <td>99518.00</td>
      <td>106314.44</td>
      <td>104435.01</td>
      <td>101211.13</td>
      <td>13312.636856</td>
    </tr>
    <tr>
      <th>19</th>
      <td>2025-01-20</td>
      <td>99416.27</td>
      <td>109358.01</td>
      <td>101217.78</td>
      <td>102145.43</td>
      <td>32342.183113</td>
    </tr>
    <tr>
      <th>20</th>
      <td>2025-01-21</td>
      <td>100051.00</td>
      <td>107291.10</td>
      <td>102145.42</td>
      <td>106159.26</td>
      <td>19411.234890</td>
    </tr>
    <tr>
      <th>21</th>
      <td>2025-01-22</td>
      <td>103100.00</td>
      <td>106431.34</td>
      <td>106159.27</td>
      <td>103667.11</td>
      <td>10730.018962</td>
    </tr>
    <tr>
      <th>22</th>
      <td>2025-01-23</td>
      <td>101200.01</td>
      <td>106870.87</td>
      <td>103659.60</td>
      <td>103926.36</td>
      <td>25064.864999</td>
    </tr>
    <tr>
      <th>23</th>
      <td>2025-01-24</td>
      <td>102751.92</td>
      <td>107200.00</td>
      <td>103926.36</td>
      <td>104850.27</td>
      <td>12921.993614</td>
    </tr>
    <tr>
      <th>24</th>
      <td>2025-01-25</td>
      <td>104104.00</td>
      <td>105294.00</td>
      <td>104866.13</td>
      <td>104733.56</td>
      <td>3404.853083</td>
    </tr>
    <tr>
      <th>25</th>
      <td>2025-01-26</td>
      <td>102452.24</td>
      <td>105478.80</td>
      <td>104729.92</td>
      <td>102563.00</td>
      <td>4575.366115</td>
    </tr>
    <tr>
      <th>26</th>
      <td>2025-01-27</td>
      <td>97715.03</td>
      <td>103228.46</td>
      <td>102565.28</td>
      <td>102062.42</td>
      <td>23647.141119</td>
    </tr>
    <tr>
      <th>27</th>
      <td>2025-01-28</td>
      <td>100213.80</td>
      <td>103770.85</td>
      <td>102063.92</td>
      <td>101290.00</td>
      <td>9488.534295</td>
    </tr>
    <tr>
      <th>28</th>
      <td>2025-01-29</td>
      <td>101275.60</td>
      <td>104829.64</td>
      <td>101290.01</td>
      <td>103747.25</td>
      <td>11403.202789</td>
    </tr>
    <tr>
      <th>29</th>
      <td>2025-01-30</td>
      <td>103289.74</td>
      <td>106484.77</td>
      <td>103747.25</td>
      <td>104742.64</td>
      <td>13061.348812</td>
    </tr>
    <tr>
      <th>30</th>
      <td>2025-01-31</td>
      <td>101506.00</td>
      <td>106090.00</td>
      <td>104742.63</td>
      <td>102411.26</td>
      <td>13313.681045</td>
    </tr>
  </tbody>
</table>
</div>


### Coinbase Pull Data

This function combines the three above to perform the following:

1. Resolve the list of products to update from the `base_currency` and `quote_currency` arguments.
2. Attempt to read an existing pickle data file for each product.
3. If a data file exists, resume from its last stored candle and pull forward to the present.
4. Otherwise, pull the available historical data for that asset and create a new record.
5. Store pickle and/or excel files of the data in the specified directories.
6. Prune the resulting product list down to the assets worth carrying forward.

Through the `base_directory`, `source`, and `asset_class` variables the function knows where in the local filesystem to look for an existing pickle file and where to store the resulting updated pickle and/or excel files:

```python
df = coinbase_pull_data(
    base_directory=DATA_DIR,
    source="Coinbase",
    asset_class="Cryptocurrencies",
    excel_export=False,
    pickle_export=True,
    output_confirmation=True,
    base_currency="BTC",
    quote_currency="USD",
    granularity=60, # 60=minute, 3600=hourly, 86400=daily
    status='online', # default status is 'online'
)
```

Note that no dates are passed. `start_date` defaults to 1/1/2010 and only applies when there is no existing record, and `end_date` defaults to one day ago to account for the lag in data availability, so a single call per product and granularity is enough to either create a record or bring one current.

By passing `None` as the `base_currency` and/or the `quote_currency`, the function uses `coinbase_fetch_available_products` to build the product list, so a single call can pull every USD-quoted pair on Coinbase.

On an update, the existing record is read back and the fetch resumes from the last date it contains. That final candle is deliberately re-fetched, since the period may still have been in progress when it was written; where a date appears in both the stored and the newly fetched data, the new row wins, so a partial candle is replaced by its completed version rather than left stale. The same range can therefore be pulled repeatedly without duplicating or corrupting anything.

The initial pull works differently. With no pickle file to resume from, there is no last date to start at, so the function falls back to `start_date` and works forward a year at a time until the API returns something. Coinbase has nothing for any of these pairs in 2010, so the first several attempts come back empty and are skipped; for BTC-USD the data begins on 7/20/2015, which is where the record actually starts.

The function also prunes the product list it returns. Assets with no data available, assets whose closing price never exceeds the price threshold, stablecoins (USDT, USDC, PAX, DAI, PYUSD, GUSD), and wrapped coins (WAXL, WBTC) are all removed. What remains is the set of assets actually useful for analysis, which matters when the starting product list runs to several hundred entries.

The example above pulls the data for BTC-USD, and stores it in the following system directory:

**DATA_DIR/Coinbase/Cryptocurrencies/Minute**

And here is the filesystem tree output for the `Coinbase` directory:

```bash
$ tree Coinbase/
Coinbase/
└── Cryptocurrencies
    ├── Daily
    │   ├── BTC-USD.pkl
    │   ├── BTC-USD.xlsx
    │   ├── ETH-USD.pkl
    │   ├── ETH-USD.xlsx
    │   ├── SOL-USD.pkl
    │   ├── SOL-USD.xlsx
    │   ├── XRP-USD.pkl
    │   └── XRP-USD.xlsx
    ├── Hourly
    │   ├── BTC-USD.pkl
    │   ├── BTC-USD.xlsx
    │   ├── ETH-USD.pkl
    │   ├── ETH-USD.xlsx
    │   ├── SOL-USD.pkl
    │   ├── SOL-USD.xlsx
    │   ├── XRP-USD.pkl
    │   └── XRP-USD.xlsx
    └── Minute
        ├── BTC-USD.pkl
        ├── ETH-USD.pkl
        ├── SOL-USD.pkl
        └── XRP-USD.pkl

5 directories, 20 files
```

Note that the `Minute` directory holds only pickle files. Minute data runs to hundreds of thousands of rows per asset, which makes the excel export slow and unwieldy, so `excel_export` is left as `False` at that granularity.

## References

1. [Coinbase](https://www.coinbase.com/)
2. Coinbase Exchange API, products endpoint: `https://api.exchange.coinbase.com/products`
3. Coinbase Exchange API, candles endpoint: `https://api.exchange.coinbase.com/products/{product_id}/candles`
4. [Reusable & Extensible Python Functions For Financial Data Analysis](/posts/reusable-extensible-python-functions-financial-data-analysis/)

## Code

{{< post-files >}}
