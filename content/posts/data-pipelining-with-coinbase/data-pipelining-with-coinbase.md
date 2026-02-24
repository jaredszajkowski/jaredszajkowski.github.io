## Introduction

This is a quick post to illustrate how I collect and store crypto asset data from Coinbase. Essentially, the scripts below pull minute, hour, and daily data for the specified assets and if there is an existing data record, then the existing record is updated to include the most recent data. If there is not an existing data record, then the complete historical record from coinbase is pulled and stored.

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

## Add Directories To Path


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

Here are the functions needed for this project:

* [coinbase_fetch_available_products](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_available_products): Fetch available products from Coinbase Exchange API.
* [coinbase_fetch_full_history](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_full_history): Fetch full historical data for a given product from Coinbase Exchange API.
* [coinbase_fetch_historical_candles](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_historical_candles): Fetch historical candle data for a given product from Coinbase Exchange API.
* [coinbase_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#coinbase_pull_data): Update existing record or pull full historical data for a given product from Coinbase Exchange API.


```python
from coinbase_fetch_available_products import coinbase_fetch_available_products
from coinbase_fetch_full_history import coinbase_fetch_full_history
from coinbase_fetch_historical_candles import coinbase_fetch_historical_candles
from coinbase_pull_data import coinbase_pull_data
```

## Function Usage

### Coinbase Fetch Available Products

This script pulls the list of available assets based on the inputs for base and quote currency. Here's an example:


```python
df = coinbase_fetch_available_products(
    base_currency=None,
    quote_currency="USD",
    status="online",
)
```

In this example, the `quote_currency` is provided as "USD". This script checks all available assets that are priced against USD and returns a dataframe listing all available assets:


```python
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
      <th>id</th>
      <th>base_currency</th>
      <th>quote_currency</th>
      <th>quote_increment</th>
      <th>base_increment</th>
      <th>display_name</th>
      <th>min_market_funds</th>
      <th>margin_enabled</th>
      <th>post_only</th>
      <th>limit_only</th>
      <th>cancel_only</th>
      <th>status</th>
      <th>status_message</th>
      <th>trading_disabled</th>
      <th>fx_stablecoin</th>
      <th>max_slippage_percentage</th>
      <th>auction_mode</th>
      <th>high_bid_limit_percentage</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>24</th>
      <td>00-USD</td>
      <td>00</td>
      <td>USD</td>
      <td>0.0001</td>
      <td>0.01</td>
      <td>00-USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
    </tr>
    <tr>
      <th>342</th>
      <td>1INCH-USD</td>
      <td>1INCH</td>
      <td>USD</td>
      <td>0.001</td>
      <td>0.01</td>
      <td>1INCH-USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
    </tr>
    <tr>
      <th>534</th>
      <td>2Z-USD</td>
      <td>2Z</td>
      <td>USD</td>
      <td>0.00001</td>
      <td>0.01</td>
      <td>2Z/USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
    </tr>
    <tr>
      <th>713</th>
      <td>A8-USD</td>
      <td>A8</td>
      <td>USD</td>
      <td>0.0001</td>
      <td>0.01</td>
      <td>A8/USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
    </tr>
    <tr>
      <th>115</th>
      <td>AAVE-USD</td>
      <td>AAVE</td>
      <td>USD</td>
      <td>0.01</td>
      <td>0.001</td>
      <td>AAVE-USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
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
    </tr>
    <tr>
      <th>442</th>
      <td>ZKC-USD</td>
      <td>ZKC</td>
      <td>USD</td>
      <td>0.0001</td>
      <td>0.01</td>
      <td>ZKC/USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
    </tr>
    <tr>
      <th>352</th>
      <td>ZKP-USD</td>
      <td>ZKP</td>
      <td>USD</td>
      <td>0.00001</td>
      <td>0.1</td>
      <td>ZKP/USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
    </tr>
    <tr>
      <th>88</th>
      <td>ZORA-USD</td>
      <td>ZORA</td>
      <td>USD</td>
      <td>0.00001</td>
      <td>1</td>
      <td>ZORA/USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
    </tr>
    <tr>
      <th>467</th>
      <td>ZRO-USD</td>
      <td>ZRO</td>
      <td>USD</td>
      <td>0.001</td>
      <td>0.01</td>
      <td>ZRO/USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
    </tr>
    <tr>
      <th>610</th>
      <td>ZRX-USD</td>
      <td>ZRX</td>
      <td>USD</td>
      <td>0.000001</td>
      <td>0.00001</td>
      <td>ZRX-USD</td>
      <td>1</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>online</td>
      <td></td>
      <td>False</td>
      <td>False</td>
      <td>0.03000000</td>
      <td>False</td>
      <td></td>
    </tr>
  </tbody>
</table>
<p>375 rows × 18 columns</p>
</div>


### Coinbase Fetch Historical Candles

This script pulls the historical candles:


```python
df = coinbase_fetch_historical_candles(
    product_id="BTC-USD",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 1, 1),
    granularity=86_400,
)
```

Specifically, the date/time, open, high, low, close, and volume levels:


```python
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
  </tbody>
</table>
</div>


### Coinbase Fetch Full History

This script pulls the full history for a specified asset:


```python
df = coinbase_fetch_full_history(
    product_id="BTC-USD",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 1, 31),
    granularity=86_400,
)
```

The example above pulls the daily data for 1 month, but can handle data ranges of years because it uses the `coinbase_fetch_historical_candles` to pull 300 candles at a time to ensure that the API is not overloaded and drops data. Here's the results for the above:


```python
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

This script combines the above functions to perform the following:

1. Attempt to read an existing pickle data file
2. If a data file exists, then pull updated data
3. Otherwise, pull all historical data available for that asset on Coinbase
4. Store pickle and/or excel files of the data in the specified directories

Through the `base_directory`, `source`, and `asset_class` variables the script knows where in the local filesystem to look for an existing pickle file and the store the resulting updated pickle and/or excel files:

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
    start_date=datetime(current_year, current_month - 1, 1), # default start date
    end_date=datetime.now() - timedelta(days=1), # updates data through 1 day ago due to lag in data availability
)
```

By passing `None` as the `base_currency` and/or the `quote_currency`, the script will use the `coinbase_fetch_available_products` function to pull the list of all the available products, and then pulls data for all assets in that list. This functionality is incredibly useful, and makes acquiring data very straightforward, especially for a set of products for a specific `base_currency` or `quote_currency`.

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

## References

1. https://www.coinbase.com/
