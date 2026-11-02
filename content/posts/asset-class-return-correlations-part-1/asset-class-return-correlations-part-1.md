## Post Updates

Update 11/1/2026: Split this post into two parts. This post now covers the correlations and rolling correlations, and the total correlation metric, decile analysis, and trading strategy have moved to [part 2](/posts/asset-class-return-correlations-part-2/).

## Introduction

In this post, we'll take a look at historical return correlations between asset classes, including rolling correlations and how those correlations have changed over time. Since first publishing this post, we've split it into two parts, and [part 2](/posts/asset-class-return-correlations-part-2/) uses these correlations to build a market timing signal and a trading strategy.

 ## Python Imports


```python
# Standard Library
import os
import sys
import warnings

from IPython.display import display, Markdown
from itertools import combinations, count
from pathlib import Path

# Data Handling
import pandas as pd

# Suppress warnings
warnings.filterwarnings("ignore")

# Pandas display options
pd.set_option("display.float_format", lambda x: f"%.2f" % x)
```


```python
# Add the source subdirectory to the system path to allow import config from settings.py
current_directory = Path(os.getcwd())
BASE_DIR = current_directory.parent.parent.parent
src_directory = BASE_DIR / "src"
sys.path.append(str(src_directory)) if str(src_directory) not in sys.path else None

# Import settings.py
from settings import config

# Add other configured directories
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

* [load_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.
* [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the timeseries data from a DataFrame for a specified date range and columns.
* [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.


```python
from load_data import load_data
from plot_heatmap import plot_heatmap
from plot_time_series import plot_time_series
from yf_pull_data import yf_pull_data
```

## Data Overview

For this exercise, we will (mostly) use ETFs as a proxy for asset classes and will use the following:

* Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
* Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
* Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
* US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
* Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
* Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
* US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
* US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
* International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
* Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
* European Stocks -- IEV (iShares S&P Europe 350 ETF)
* Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
* Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
* Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
* Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
* Gold -- GLD (SPDR Gold Shares)
* Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
* Real Estate -- IYR (iShares U.S. Real Estate ETF)
* Bitcoin -- BTC-USD (Bitcoin USD)
* Ethereum -- ETH-USD (Ethereum USD)

For all of these, we will use the adjusted closing price, which accounts for dividends and stock splits.

### Acquire & Plot Data

We'll now pull the data for all the ETFs and cryptocurrencies listed above.


```python
figure_number = count(1)
table_number = count(1)

# Create list of tickers to pull data for
us_equity_tickers = ["IVV", "IJH", "IJR", "QQQ", "IWB", "IWD", "IWF", "IWM"]
intl_equity_tickers = ["EFA", "EEM", "IEV"]
equity_tickers = us_equity_tickers + intl_equity_tickers
bond_tickers = ["SHY", "IEF", "TLT", "AGG"]
commodity_tickers = ["GLD", "GSG"]
real_estate_tickers = ["IYR"]
cryptoasset_tickers = ["BTC-USD", "ETH-USD"]

etf_tickers = (
    us_equity_tickers
    + intl_equity_tickers
    + bond_tickers
    + commodity_tickers
    + real_estate_tickers
)

tickers_dict = {
    "IVV": "Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)",
    "IJH": "Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)",
    "IJR": "Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)",
    "QQQ": "US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)",
    "IWB": "Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)",
    "IWM": "Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)",
    "IWD": "Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)",
    "IWF": "Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)",
    "EFA": "International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)",
    "EEM": "Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)",
    "IEV": "European Stocks -- IEV (iShares S&P Europe 350 ETF)",
    "SHY": "Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)",
    "IEF": "Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)",
    "TLT": "Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)",
    "AGG": "Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)",
    "GLD": "Gold -- GLD (SPDR Gold Shares)",
    "GSG": "Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)",
    "IYR": "Real Estate -- IYR (iShares U.S. Real Estate ETF)",
    "BTC-USD": "Bitcoin -- BTC-USD (Bitcoin USD)",
    "ETH-USD": "Ethereum -- ETH-USD (Ethereum USD)",
}
```


```python
for ticker in etf_tickers:
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

for ticker in cryptoasset_tickers:
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=ticker,
        adjusted=False,
        source="Yahoo_Finance",
        asset_class="Cryptocurrencies",
        excel_export=True,
        pickle_export=True,
        output_confirmation=False,
    )
```

### Load & Filter Data

We'll then peform the following:
* Load data
* Rename columns to include the ticker (e.g. "QQQ_Close", "QQQ_Adj_Close", etc.)
* Drop all columns except for "Adj Close"
* Calculate the daily returns
* Combine the data into a single DataFrame
* Check the inception date for each of thge funds


```python
fund_data = pd.DataFrame()

for ticker in etf_tickers:
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

for ticker in cryptoasset_tickers:
    data = load_data(
        base_directory=DATA_DIR,
        ticker=ticker,
        source="Yahoo_Finance",
        asset_class="Cryptocurrencies",
        timeframe="Daily",
        file_format="pickle",
    )

    # Rename columns to "BTC-USD_Close", etc.
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
      <th>GLD_Adj_Close</th>
      <th>GLD_Daily_Return</th>
      <th>GSG_Adj_Close</th>
      <th>GSG_Daily_Return</th>
      <th>IYR_Adj_Close</th>
      <th>IYR_Daily_Return</th>
      <th>BTC-USD_Adj_Close</th>
      <th>BTC-USD_Daily_Return</th>
      <th>ETH-USD_Adj_Close</th>
      <th>ETH-USD_Daily_Return</th>
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
      <th>2026-10-27</th>
      <td>773.25</td>
      <td>0.01</td>
      <td>73.22</td>
      <td>0.00</td>
      <td>139.68</td>
      <td>0.01</td>
      <td>721.25</td>
      <td>0.01</td>
      <td>420.41</td>
      <td>0.01</td>
      <td>...</td>
      <td>372.28</td>
      <td>0.01</td>
      <td>36.99</td>
      <td>-0.01</td>
      <td>97.97</td>
      <td>-0.01</td>
      <td>80805.08</td>
      <td>0.01</td>
      <td>2347.73</td>
      <td>0.01</td>
    </tr>
    <tr>
      <th>2026-10-28</th>
      <td>775.65</td>
      <td>0.00</td>
      <td>73.35</td>
      <td>0.00</td>
      <td>139.76</td>
      <td>0.00</td>
      <td>725.61</td>
      <td>0.01</td>
      <td>421.72</td>
      <td>0.00</td>
      <td>...</td>
      <td>373.51</td>
      <td>0.00</td>
      <td>37.15</td>
      <td>0.00</td>
      <td>97.29</td>
      <td>-0.01</td>
      <td>81267.59</td>
      <td>0.01</td>
      <td>2357.62</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>2026-10-29</th>
      <td>772.97</td>
      <td>-0.00</td>
      <td>74.20</td>
      <td>0.01</td>
      <td>142.01</td>
      <td>0.02</td>
      <td>715.34</td>
      <td>-0.01</td>
      <td>420.52</td>
      <td>-0.00</td>
      <td>...</td>
      <td>368.57</td>
      <td>-0.01</td>
      <td>37.11</td>
      <td>-0.00</td>
      <td>99.47</td>
      <td>0.02</td>
      <td>77775.11</td>
      <td>-0.04</td>
      <td>2249.50</td>
      <td>-0.05</td>
    </tr>
    <tr>
      <th>2026-10-30</th>
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
      <td>77198.21</td>
      <td>-0.01</td>
      <td>2241.05</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>2026-10-31</th>
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
      <td>77434.75</td>
      <td>0.00</td>
      <td>2252.75</td>
      <td>0.01</td>
    </tr>
  </tbody>
</table>
<p>8334 rows × 40 columns</p>
</div>



```python
for ticker in tickers_dict.keys():
    print(f"First date for {ticker}: {fund_data[f'{ticker}_Daily_Return'].first_valid_index()}")
```

    First date for IVV: 2000-05-22 00:00:00
    First date for IJH: 2000-05-30 00:00:00
    First date for IJR: 2000-05-30 00:00:00
    First date for QQQ: 1999-03-11 00:00:00
    First date for IWB: 2000-05-22 00:00:00
    First date for IWM: 2000-05-30 00:00:00
    First date for IWD: 2000-05-30 00:00:00
    First date for IWF: 2000-05-30 00:00:00
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
    First date for BTC-USD: 2014-09-18 00:00:00
    First date for ETH-USD: 2017-11-10 00:00:00


### Plot Data

We'll then plot the time series of the adjusted close prices for each of the assets.


```python
# Combine the etf_tickers and cryptoasset_tickers lists into a single list of all tickers
all_tickers = etf_tickers + cryptoasset_tickers

for ticker in tickers_dict.keys():
    plot_time_series(
        df=fund_data,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[f"{ticker}_Adj_Close"],
        title=f"Figure {next(figure_number)}: {tickers_dict[ticker]} Adjusted Close Price",
        x_label="Date",
        x_format="Year",
        x_tick_spacing=1,
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="Price ($)",
        y_format="Decimal",
        y_format_decimal_places="Auto",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        caption=f"Data Source: Yahoo Finance, Analysis by the Author",
    )
```


    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_0.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_1.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_2.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_3.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_4.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_5.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_6.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_7.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_8.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_9.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_10.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_11.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_12.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_13.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_14.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_15.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_16.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_17.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_18.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_22_19.png)
    


## Calculate Correlations

Next, we'll calculate the correlation matrix of the daily returns for all of the assets and plot it as a heatmap. We'll do this first without the BTC and ETH data (due to the limited history), and then with the BTC and ETH data.


```python
# Drop the adjusted close price columns, leaving only the daily return columns
daily_return_columns = [f"{ticker}_Daily_Return" for ticker in tickers_dict.keys()]
fund_data_daily_returns_all = fund_data[daily_return_columns]

# Drop the BTC and ETH daily return columns due to the limited history
fund_data_daily_returns_no_crypto = fund_data_daily_returns_all.drop(columns=["BTC-USD_Daily_Return", "ETH-USD_Daily_Return"])

# Print the shape of the fund_data_daily_returns_no_crypto DataFrame to confirm that the rows with missing data have been dropped
print(f"Shape of fund_data_daily_returns_no_crypto: {fund_data_daily_returns_no_crypto.shape}")
print(f"Rows to drop due to missing data: {fund_data_daily_returns_no_crypto.dropna().shape}")

# Drop the NaN values
fund_data_daily_returns_no_crypto = fund_data_daily_returns_no_crypto.dropna()

# Calculate the correlation matrix of the daily returns
correlation_matrix_no_crypto = fund_data_daily_returns_no_crypto.corr()

display(Markdown(f"Table {next(table_number)}: Correlation Matrix of Daily Returns (Excluding BTC and ETH)"))
display(correlation_matrix_no_crypto)
```

    Shape of fund_data_daily_returns_no_crypto: (8334, 18)
    Rows to drop due to missing data: (5100, 18)



Table 2: Correlation Matrix of Daily Returns (Excluding BTC and ETH)



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
      <th>IVV_Daily_Return</th>
      <th>IJH_Daily_Return</th>
      <th>IJR_Daily_Return</th>
      <th>QQQ_Daily_Return</th>
      <th>IWB_Daily_Return</th>
      <th>IWM_Daily_Return</th>
      <th>IWD_Daily_Return</th>
      <th>IWF_Daily_Return</th>
      <th>EFA_Daily_Return</th>
      <th>EEM_Daily_Return</th>
      <th>IEV_Daily_Return</th>
      <th>SHY_Daily_Return</th>
      <th>IEF_Daily_Return</th>
      <th>TLT_Daily_Return</th>
      <th>AGG_Daily_Return</th>
      <th>GLD_Daily_Return</th>
      <th>GSG_Daily_Return</th>
      <th>IYR_Daily_Return</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>IVV_Daily_Return</th>
      <td>1.00</td>
      <td>0.93</td>
      <td>0.88</td>
      <td>0.92</td>
      <td>1.00</td>
      <td>0.90</td>
      <td>0.96</td>
      <td>0.96</td>
      <td>0.88</td>
      <td>0.82</td>
      <td>0.86</td>
      <td>-0.23</td>
      <td>-0.30</td>
      <td>-0.31</td>
      <td>-0.01</td>
      <td>0.07</td>
      <td>0.37</td>
      <td>0.76</td>
    </tr>
    <tr>
      <th>IJH_Daily_Return</th>
      <td>0.93</td>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.83</td>
      <td>0.94</td>
      <td>0.96</td>
      <td>0.94</td>
      <td>0.87</td>
      <td>0.85</td>
      <td>0.78</td>
      <td>0.83</td>
      <td>-0.20</td>
      <td>-0.28</td>
      <td>-0.30</td>
      <td>-0.00</td>
      <td>0.07</td>
      <td>0.38</td>
      <td>0.78</td>
    </tr>
    <tr>
      <th>IJR_Daily_Return</th>
      <td>0.88</td>
      <td>0.96</td>
      <td>1.00</td>
      <td>0.78</td>
      <td>0.89</td>
      <td>0.98</td>
      <td>0.90</td>
      <td>0.82</td>
      <td>0.80</td>
      <td>0.73</td>
      <td>0.78</td>
      <td>-0.19</td>
      <td>-0.27</td>
      <td>-0.29</td>
      <td>-0.03</td>
      <td>0.05</td>
      <td>0.35</td>
      <td>0.76</td>
    </tr>
    <tr>
      <th>QQQ_Daily_Return</th>
      <td>0.92</td>
      <td>0.83</td>
      <td>0.78</td>
      <td>1.00</td>
      <td>0.93</td>
      <td>0.82</td>
      <td>0.81</td>
      <td>0.97</td>
      <td>0.79</td>
      <td>0.76</td>
      <td>0.76</td>
      <td>-0.19</td>
      <td>-0.24</td>
      <td>-0.25</td>
      <td>0.01</td>
      <td>0.06</td>
      <td>0.29</td>
      <td>0.63</td>
    </tr>
    <tr>
      <th>IWB_Daily_Return</th>
      <td>1.00</td>
      <td>0.94</td>
      <td>0.89</td>
      <td>0.93</td>
      <td>1.00</td>
      <td>0.91</td>
      <td>0.96</td>
      <td>0.96</td>
      <td>0.88</td>
      <td>0.82</td>
      <td>0.86</td>
      <td>-0.22</td>
      <td>-0.29</td>
      <td>-0.31</td>
      <td>-0.01</td>
      <td>0.07</td>
      <td>0.37</td>
      <td>0.76</td>
    </tr>
    <tr>
      <th>IWM_Daily_Return</th>
      <td>0.90</td>
      <td>0.96</td>
      <td>0.98</td>
      <td>0.82</td>
      <td>0.91</td>
      <td>1.00</td>
      <td>0.90</td>
      <td>0.85</td>
      <td>0.81</td>
      <td>0.76</td>
      <td>0.80</td>
      <td>-0.19</td>
      <td>-0.27</td>
      <td>-0.28</td>
      <td>-0.02</td>
      <td>0.06</td>
      <td>0.35</td>
      <td>0.76</td>
    </tr>
    <tr>
      <th>IWD_Daily_Return</th>
      <td>0.96</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.81</td>
      <td>0.96</td>
      <td>0.90</td>
      <td>1.00</td>
      <td>0.86</td>
      <td>0.88</td>
      <td>0.80</td>
      <td>0.86</td>
      <td>-0.24</td>
      <td>-0.31</td>
      <td>-0.33</td>
      <td>-0.01</td>
      <td>0.06</td>
      <td>0.39</td>
      <td>0.80</td>
    </tr>
    <tr>
      <th>IWF_Daily_Return</th>
      <td>0.96</td>
      <td>0.87</td>
      <td>0.82</td>
      <td>0.97</td>
      <td>0.96</td>
      <td>0.85</td>
      <td>0.86</td>
      <td>1.00</td>
      <td>0.82</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>-0.19</td>
      <td>-0.25</td>
      <td>-0.26</td>
      <td>0.02</td>
      <td>0.08</td>
      <td>0.33</td>
      <td>0.67</td>
    </tr>
    <tr>
      <th>EFA_Daily_Return</th>
      <td>0.88</td>
      <td>0.85</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.88</td>
      <td>0.81</td>
      <td>0.88</td>
      <td>0.82</td>
      <td>1.00</td>
      <td>0.87</td>
      <td>0.98</td>
      <td>-0.18</td>
      <td>-0.26</td>
      <td>-0.28</td>
      <td>0.04</td>
      <td>0.17</td>
      <td>0.40</td>
      <td>0.70</td>
    </tr>
    <tr>
      <th>EEM_Daily_Return</th>
      <td>0.82</td>
      <td>0.78</td>
      <td>0.73</td>
      <td>0.76</td>
      <td>0.82</td>
      <td>0.76</td>
      <td>0.80</td>
      <td>0.78</td>
      <td>0.87</td>
      <td>1.00</td>
      <td>0.84</td>
      <td>-0.21</td>
      <td>-0.26</td>
      <td>-0.26</td>
      <td>-0.01</td>
      <td>0.19</td>
      <td>0.40</td>
      <td>0.66</td>
    </tr>
    <tr>
      <th>IEV_Daily_Return</th>
      <td>0.86</td>
      <td>0.83</td>
      <td>0.78</td>
      <td>0.76</td>
      <td>0.86</td>
      <td>0.80</td>
      <td>0.86</td>
      <td>0.80</td>
      <td>0.98</td>
      <td>0.84</td>
      <td>1.00</td>
      <td>-0.18</td>
      <td>-0.26</td>
      <td>-0.29</td>
      <td>0.03</td>
      <td>0.16</td>
      <td>0.40</td>
      <td>0.69</td>
    </tr>
    <tr>
      <th>SHY_Daily_Return</th>
      <td>-0.23</td>
      <td>-0.20</td>
      <td>-0.19</td>
      <td>-0.19</td>
      <td>-0.22</td>
      <td>-0.19</td>
      <td>-0.24</td>
      <td>-0.19</td>
      <td>-0.18</td>
      <td>-0.21</td>
      <td>-0.18</td>
      <td>1.00</td>
      <td>0.76</td>
      <td>0.57</td>
      <td>0.60</td>
      <td>0.22</td>
      <td>-0.14</td>
      <td>-0.12</td>
    </tr>
    <tr>
      <th>IEF_Daily_Return</th>
      <td>-0.30</td>
      <td>-0.28</td>
      <td>-0.27</td>
      <td>-0.24</td>
      <td>-0.29</td>
      <td>-0.27</td>
      <td>-0.31</td>
      <td>-0.25</td>
      <td>-0.26</td>
      <td>-0.26</td>
      <td>-0.26</td>
      <td>0.76</td>
      <td>1.00</td>
      <td>0.91</td>
      <td>0.77</td>
      <td>0.22</td>
      <td>-0.22</td>
      <td>-0.14</td>
    </tr>
    <tr>
      <th>TLT_Daily_Return</th>
      <td>-0.31</td>
      <td>-0.30</td>
      <td>-0.29</td>
      <td>-0.25</td>
      <td>-0.31</td>
      <td>-0.28</td>
      <td>-0.33</td>
      <td>-0.26</td>
      <td>-0.28</td>
      <td>-0.26</td>
      <td>-0.29</td>
      <td>0.57</td>
      <td>0.91</td>
      <td>1.00</td>
      <td>0.71</td>
      <td>0.16</td>
      <td>-0.24</td>
      <td>-0.15</td>
    </tr>
    <tr>
      <th>AGG_Daily_Return</th>
      <td>-0.01</td>
      <td>-0.00</td>
      <td>-0.03</td>
      <td>0.01</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.01</td>
      <td>0.02</td>
      <td>0.04</td>
      <td>-0.01</td>
      <td>0.03</td>
      <td>0.60</td>
      <td>0.77</td>
      <td>0.71</td>
      <td>1.00</td>
      <td>0.22</td>
      <td>-0.06</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>GLD_Daily_Return</th>
      <td>0.07</td>
      <td>0.07</td>
      <td>0.05</td>
      <td>0.06</td>
      <td>0.07</td>
      <td>0.06</td>
      <td>0.06</td>
      <td>0.08</td>
      <td>0.17</td>
      <td>0.19</td>
      <td>0.16</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>0.16</td>
      <td>0.22</td>
      <td>1.00</td>
      <td>0.25</td>
      <td>0.07</td>
    </tr>
    <tr>
      <th>GSG_Daily_Return</th>
      <td>0.37</td>
      <td>0.38</td>
      <td>0.35</td>
      <td>0.29</td>
      <td>0.37</td>
      <td>0.35</td>
      <td>0.39</td>
      <td>0.33</td>
      <td>0.40</td>
      <td>0.40</td>
      <td>0.40</td>
      <td>-0.14</td>
      <td>-0.22</td>
      <td>-0.24</td>
      <td>-0.06</td>
      <td>0.25</td>
      <td>1.00</td>
      <td>0.25</td>
    </tr>
    <tr>
      <th>IYR_Daily_Return</th>
      <td>0.76</td>
      <td>0.78</td>
      <td>0.76</td>
      <td>0.63</td>
      <td>0.76</td>
      <td>0.76</td>
      <td>0.80</td>
      <td>0.67</td>
      <td>0.70</td>
      <td>0.66</td>
      <td>0.69</td>
      <td>-0.12</td>
      <td>-0.14</td>
      <td>-0.15</td>
      <td>0.03</td>
      <td>0.07</td>
      <td>0.25</td>
      <td>1.00</td>
    </tr>
  </tbody>
</table>
</div>


And then the heatmap:


```python
plot_heatmap(
    df=correlation_matrix_no_crypto,
    title=f"Figure {next(figure_number)}: Correlation Matrix of Daily Returns (Excluding BTC and ETH)",
    caption=f"Data Source: Yahoo Finance, Analysis by the Author",
)
```


    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_27_0.png)
    


We'll now include the BTC and ETH data and recalculate the correlation matrix and heatmap. Keep in mind that the BTC and ETH data only goes back to 2014 and 2017 respectively, so the correlation matrix will be calculated using a shorter time period than the other assets.


```python
# Print the shape of the fund_data_daily_returns DataFrame to confirm that the rows with missing data have been dropped
print(f"Shape of fund_data_daily_returns: {fund_data_daily_returns_all.shape}")
print(f"Rows to drop due to missing data: {fund_data_daily_returns_all.dropna().shape}")

# Drop the NaN values
fund_data_daily_returns = fund_data_daily_returns_all.dropna()

# Calculate the correlation matrix of the daily returns
correlation_matrix = fund_data_daily_returns.corr()

display(Markdown(f"Table {next(table_number)}: Correlation Matrix of Daily Returns (Including BTC and ETH)"))
display(correlation_matrix)
```

    Shape of fund_data_daily_returns: (8334, 20)
    Rows to drop due to missing data: (2253, 20)



Table 3: Correlation Matrix of Daily Returns (Including BTC and ETH)



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
      <th>IVV_Daily_Return</th>
      <th>IJH_Daily_Return</th>
      <th>IJR_Daily_Return</th>
      <th>QQQ_Daily_Return</th>
      <th>IWB_Daily_Return</th>
      <th>IWM_Daily_Return</th>
      <th>IWD_Daily_Return</th>
      <th>IWF_Daily_Return</th>
      <th>EFA_Daily_Return</th>
      <th>EEM_Daily_Return</th>
      <th>IEV_Daily_Return</th>
      <th>SHY_Daily_Return</th>
      <th>IEF_Daily_Return</th>
      <th>TLT_Daily_Return</th>
      <th>AGG_Daily_Return</th>
      <th>GLD_Daily_Return</th>
      <th>GSG_Daily_Return</th>
      <th>IYR_Daily_Return</th>
      <th>BTC-USD_Daily_Return</th>
      <th>ETH-USD_Daily_Return</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>IVV_Daily_Return</th>
      <td>1.00</td>
      <td>0.90</td>
      <td>0.84</td>
      <td>0.93</td>
      <td>1.00</td>
      <td>0.86</td>
      <td>0.92</td>
      <td>0.96</td>
      <td>0.85</td>
      <td>0.75</td>
      <td>0.82</td>
      <td>-0.04</td>
      <td>-0.11</td>
      <td>-0.14</td>
      <td>0.14</td>
      <td>0.12</td>
      <td>0.29</td>
      <td>0.73</td>
      <td>0.30</td>
      <td>0.33</td>
    </tr>
    <tr>
      <th>IJH_Daily_Return</th>
      <td>0.90</td>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.77</td>
      <td>0.91</td>
      <td>0.96</td>
      <td>0.94</td>
      <td>0.80</td>
      <td>0.83</td>
      <td>0.71</td>
      <td>0.81</td>
      <td>-0.04</td>
      <td>-0.10</td>
      <td>-0.13</td>
      <td>0.16</td>
      <td>0.11</td>
      <td>0.29</td>
      <td>0.77</td>
      <td>0.28</td>
      <td>0.30</td>
    </tr>
    <tr>
      <th>IJR_Daily_Return</th>
      <td>0.84</td>
      <td>0.96</td>
      <td>1.00</td>
      <td>0.70</td>
      <td>0.85</td>
      <td>0.98</td>
      <td>0.90</td>
      <td>0.73</td>
      <td>0.78</td>
      <td>0.65</td>
      <td>0.76</td>
      <td>-0.02</td>
      <td>-0.09</td>
      <td>-0.12</td>
      <td>0.16</td>
      <td>0.09</td>
      <td>0.28</td>
      <td>0.73</td>
      <td>0.28</td>
      <td>0.30</td>
    </tr>
    <tr>
      <th>QQQ_Daily_Return</th>
      <td>0.93</td>
      <td>0.77</td>
      <td>0.70</td>
      <td>1.00</td>
      <td>0.93</td>
      <td>0.77</td>
      <td>0.75</td>
      <td>0.98</td>
      <td>0.76</td>
      <td>0.74</td>
      <td>0.72</td>
      <td>-0.02</td>
      <td>-0.06</td>
      <td>-0.09</td>
      <td>0.14</td>
      <td>0.14</td>
      <td>0.22</td>
      <td>0.57</td>
      <td>0.31</td>
      <td>0.34</td>
    </tr>
    <tr>
      <th>IWB_Daily_Return</th>
      <td>1.00</td>
      <td>0.91</td>
      <td>0.85</td>
      <td>0.93</td>
      <td>1.00</td>
      <td>0.88</td>
      <td>0.93</td>
      <td>0.96</td>
      <td>0.85</td>
      <td>0.75</td>
      <td>0.82</td>
      <td>-0.04</td>
      <td>-0.10</td>
      <td>-0.13</td>
      <td>0.15</td>
      <td>0.12</td>
      <td>0.28</td>
      <td>0.73</td>
      <td>0.30</td>
      <td>0.33</td>
    </tr>
    <tr>
      <th>IWM_Daily_Return</th>
      <td>0.86</td>
      <td>0.96</td>
      <td>0.98</td>
      <td>0.77</td>
      <td>0.88</td>
      <td>1.00</td>
      <td>0.89</td>
      <td>0.79</td>
      <td>0.80</td>
      <td>0.70</td>
      <td>0.77</td>
      <td>-0.01</td>
      <td>-0.07</td>
      <td>-0.10</td>
      <td>0.17</td>
      <td>0.13</td>
      <td>0.28</td>
      <td>0.72</td>
      <td>0.31</td>
      <td>0.33</td>
    </tr>
    <tr>
      <th>IWD_Daily_Return</th>
      <td>0.92</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.75</td>
      <td>0.93</td>
      <td>0.89</td>
      <td>1.00</td>
      <td>0.78</td>
      <td>0.85</td>
      <td>0.69</td>
      <td>0.83</td>
      <td>-0.05</td>
      <td>-0.13</td>
      <td>-0.17</td>
      <td>0.13</td>
      <td>0.11</td>
      <td>0.32</td>
      <td>0.80</td>
      <td>0.26</td>
      <td>0.28</td>
    </tr>
    <tr>
      <th>IWF_Daily_Return</th>
      <td>0.96</td>
      <td>0.80</td>
      <td>0.73</td>
      <td>0.98</td>
      <td>0.96</td>
      <td>0.79</td>
      <td>0.78</td>
      <td>1.00</td>
      <td>0.77</td>
      <td>0.73</td>
      <td>0.74</td>
      <td>-0.02</td>
      <td>-0.07</td>
      <td>-0.09</td>
      <td>0.15</td>
      <td>0.13</td>
      <td>0.22</td>
      <td>0.61</td>
      <td>0.31</td>
      <td>0.34</td>
    </tr>
    <tr>
      <th>EFA_Daily_Return</th>
      <td>0.85</td>
      <td>0.83</td>
      <td>0.78</td>
      <td>0.76</td>
      <td>0.85</td>
      <td>0.80</td>
      <td>0.85</td>
      <td>0.77</td>
      <td>1.00</td>
      <td>0.82</td>
      <td>0.98</td>
      <td>0.03</td>
      <td>-0.03</td>
      <td>-0.08</td>
      <td>0.22</td>
      <td>0.25</td>
      <td>0.27</td>
      <td>0.68</td>
      <td>0.29</td>
      <td>0.32</td>
    </tr>
    <tr>
      <th>EEM_Daily_Return</th>
      <td>0.75</td>
      <td>0.71</td>
      <td>0.65</td>
      <td>0.74</td>
      <td>0.75</td>
      <td>0.70</td>
      <td>0.69</td>
      <td>0.73</td>
      <td>0.82</td>
      <td>1.00</td>
      <td>0.79</td>
      <td>0.01</td>
      <td>-0.05</td>
      <td>-0.08</td>
      <td>0.16</td>
      <td>0.27</td>
      <td>0.26</td>
      <td>0.51</td>
      <td>0.26</td>
      <td>0.30</td>
    </tr>
    <tr>
      <th>IEV_Daily_Return</th>
      <td>0.82</td>
      <td>0.81</td>
      <td>0.76</td>
      <td>0.72</td>
      <td>0.82</td>
      <td>0.77</td>
      <td>0.83</td>
      <td>0.74</td>
      <td>0.98</td>
      <td>0.79</td>
      <td>1.00</td>
      <td>0.03</td>
      <td>-0.04</td>
      <td>-0.09</td>
      <td>0.21</td>
      <td>0.24</td>
      <td>0.26</td>
      <td>0.67</td>
      <td>0.29</td>
      <td>0.31</td>
    </tr>
    <tr>
      <th>SHY_Daily_Return</th>
      <td>-0.04</td>
      <td>-0.04</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>-0.04</td>
      <td>-0.01</td>
      <td>-0.05</td>
      <td>-0.02</td>
      <td>0.03</td>
      <td>0.01</td>
      <td>0.03</td>
      <td>1.00</td>
      <td>0.82</td>
      <td>0.60</td>
      <td>0.74</td>
      <td>0.32</td>
      <td>-0.13</td>
      <td>0.14</td>
      <td>0.03</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>IEF_Daily_Return</th>
      <td>-0.11</td>
      <td>-0.10</td>
      <td>-0.09</td>
      <td>-0.06</td>
      <td>-0.10</td>
      <td>-0.07</td>
      <td>-0.13</td>
      <td>-0.07</td>
      <td>-0.03</td>
      <td>-0.05</td>
      <td>-0.04</td>
      <td>0.82</td>
      <td>1.00</td>
      <td>0.91</td>
      <td>0.89</td>
      <td>0.30</td>
      <td>-0.16</td>
      <td>0.10</td>
      <td>-0.00</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>TLT_Daily_Return</th>
      <td>-0.14</td>
      <td>-0.13</td>
      <td>-0.12</td>
      <td>-0.09</td>
      <td>-0.13</td>
      <td>-0.10</td>
      <td>-0.17</td>
      <td>-0.09</td>
      <td>-0.08</td>
      <td>-0.08</td>
      <td>-0.09</td>
      <td>0.60</td>
      <td>0.91</td>
      <td>1.00</td>
      <td>0.84</td>
      <td>0.22</td>
      <td>-0.18</td>
      <td>0.05</td>
      <td>-0.01</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <th>AGG_Daily_Return</th>
      <td>0.14</td>
      <td>0.16</td>
      <td>0.16</td>
      <td>0.14</td>
      <td>0.15</td>
      <td>0.17</td>
      <td>0.13</td>
      <td>0.15</td>
      <td>0.22</td>
      <td>0.16</td>
      <td>0.21</td>
      <td>0.74</td>
      <td>0.89</td>
      <td>0.84</td>
      <td>1.00</td>
      <td>0.30</td>
      <td>-0.04</td>
      <td>0.30</td>
      <td>0.12</td>
      <td>0.11</td>
    </tr>
    <tr>
      <th>GLD_Daily_Return</th>
      <td>0.12</td>
      <td>0.11</td>
      <td>0.09</td>
      <td>0.14</td>
      <td>0.12</td>
      <td>0.13</td>
      <td>0.11</td>
      <td>0.13</td>
      <td>0.25</td>
      <td>0.27</td>
      <td>0.24</td>
      <td>0.32</td>
      <td>0.30</td>
      <td>0.22</td>
      <td>0.30</td>
      <td>1.00</td>
      <td>0.17</td>
      <td>0.14</td>
      <td>0.13</td>
      <td>0.13</td>
    </tr>
    <tr>
      <th>GSG_Daily_Return</th>
      <td>0.29</td>
      <td>0.29</td>
      <td>0.28</td>
      <td>0.22</td>
      <td>0.28</td>
      <td>0.28</td>
      <td>0.32</td>
      <td>0.22</td>
      <td>0.27</td>
      <td>0.26</td>
      <td>0.26</td>
      <td>-0.13</td>
      <td>-0.16</td>
      <td>-0.18</td>
      <td>-0.04</td>
      <td>0.17</td>
      <td>1.00</td>
      <td>0.19</td>
      <td>0.09</td>
      <td>0.10</td>
    </tr>
    <tr>
      <th>IYR_Daily_Return</th>
      <td>0.73</td>
      <td>0.77</td>
      <td>0.73</td>
      <td>0.57</td>
      <td>0.73</td>
      <td>0.72</td>
      <td>0.80</td>
      <td>0.61</td>
      <td>0.68</td>
      <td>0.51</td>
      <td>0.67</td>
      <td>0.14</td>
      <td>0.10</td>
      <td>0.05</td>
      <td>0.30</td>
      <td>0.14</td>
      <td>0.19</td>
      <td>1.00</td>
      <td>0.19</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>BTC-USD_Daily_Return</th>
      <td>0.30</td>
      <td>0.28</td>
      <td>0.28</td>
      <td>0.31</td>
      <td>0.30</td>
      <td>0.31</td>
      <td>0.26</td>
      <td>0.31</td>
      <td>0.29</td>
      <td>0.26</td>
      <td>0.29</td>
      <td>0.03</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>0.12</td>
      <td>0.13</td>
      <td>0.09</td>
      <td>0.19</td>
      <td>1.00</td>
      <td>0.80</td>
    </tr>
    <tr>
      <th>ETH-USD_Daily_Return</th>
      <td>0.33</td>
      <td>0.30</td>
      <td>0.30</td>
      <td>0.34</td>
      <td>0.33</td>
      <td>0.33</td>
      <td>0.28</td>
      <td>0.34</td>
      <td>0.32</td>
      <td>0.30</td>
      <td>0.31</td>
      <td>0.03</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>0.11</td>
      <td>0.13</td>
      <td>0.10</td>
      <td>0.21</td>
      <td>0.80</td>
      <td>1.00</td>
    </tr>
  </tbody>
</table>
</div>


And then the heatmap:


```python
plot_heatmap(
    df=correlation_matrix,
    title=f"Figure {next(figure_number)}: Correlation Matrix of Daily Returns (Including BTC and ETH)",
    caption=f"Data Source: Yahoo Finance, Analysis by the Author",
)
```


    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_31_0.png)
    


These are interesting results, but expected. The stock funds tend to have low correlations with the bond funds, the commodities don't really correlate with anything, etc. But we know that the correlations between these asset classes have changed over time, so let's take a look at how the correlations have evolved over time by calculating rolling correlations.

## Calculate Rolling Correlations

Next, we will calculate the rolling correlations for several different periods:

* 3 days
* 1 week
* 2 weeks
* 1 month
* 3 month
* 6 month
* 1 year
* 5 years
* 10 years


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

We'll pair down the list of funds to only include the high correlation US equity funds that make up the S&P 1500 index (IVV, IJH, IJR).


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
        temp_df = fund_data_daily_returns_no_crypto[
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

            # print(tickers_dict[f"{ticker1}"])
            # print(tickers_dict[f"{ticker2}"])

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


Table 4: Rolling Correlations



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
      <th>2026-10-23</th>
      <td>0.98</td>
      <td>0.83</td>
      <td>0.86</td>
      <td>0.76</td>
      <td>0.80</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>-0.45</td>
      <td>...</td>
      <td>0.83</td>
      <td>-0.25</td>
      <td>0.53</td>
      <td>0.84</td>
      <td>0.86</td>
      <td>0.90</td>
      <td>0.90</td>
      <td>0.93</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
    <tr>
      <th>2026-10-26</th>
      <td>0.98</td>
      <td>0.91</td>
      <td>0.89</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.07</td>
      <td>...</td>
      <td>0.83</td>
      <td>0.28</td>
      <td>0.54</td>
      <td>0.83</td>
      <td>0.86</td>
      <td>0.91</td>
      <td>0.90</td>
      <td>0.93</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
    <tr>
      <th>2026-10-27</th>
      <td>0.99</td>
      <td>0.98</td>
      <td>0.89</td>
      <td>0.76</td>
      <td>0.78</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.99</td>
      <td>...</td>
      <td>0.83</td>
      <td>0.97</td>
      <td>0.25</td>
      <td>0.84</td>
      <td>0.86</td>
      <td>0.90</td>
      <td>0.90</td>
      <td>0.93</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
    <tr>
      <th>2026-10-28</th>
      <td>0.95</td>
      <td>0.98</td>
      <td>0.85</td>
      <td>0.76</td>
      <td>0.79</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>0.94</td>
      <td>...</td>
      <td>0.83</td>
      <td>0.80</td>
      <td>0.29</td>
      <td>0.75</td>
      <td>0.86</td>
      <td>0.90</td>
      <td>0.90</td>
      <td>0.93</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
    <tr>
      <th>2026-10-29</th>
      <td>-0.86</td>
      <td>0.32</td>
      <td>0.71</td>
      <td>0.68</td>
      <td>0.76</td>
      <td>0.77</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>-0.82</td>
      <td>...</td>
      <td>0.83</td>
      <td>1.00</td>
      <td>0.92</td>
      <td>0.77</td>
      <td>0.86</td>
      <td>0.91</td>
      <td>0.90</td>
      <td>0.93</td>
      <td>0.97</td>
      <td>0.96</td>
    </tr>
  </tbody>
</table>
<p>5100 rows × 27 columns</p>
</div>



```python
for window in rolling_windows.keys():
    plot_time_series(
        df=rolling_corr_results_df,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[col for col in rolling_corr_results_df.columns if f"{window}" in col],
        title=f"Figure {next(figure_number)}: Rolling {window} Correlation",
        x_label="Date",
        x_format="Year",
        x_tick_spacing=1,
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="Correlation",
        y_format="Decimal",
        y_format_decimal_places="Auto",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
        caption=f"Data Source: Yahoo Finance, Analysis by the Author",
    )
```


    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_38_0.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_38_1.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_38_2.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_38_3.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_38_4.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_38_5.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_38_6.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_38_7.png)
    



    
![png](asset-class-return-correlations-part-1_files/asset-class-return-correlations-part-1_38_8.png)
    


With the above plots, we can see that there are periods of time when the correlations abruptly increase or decrease, such as:

* Early-mid 2007 (the start of the financial crisis)
* Mid 2011 (the European debt crisis)
* Late 2015 into 2016
* Late 2018 (rate hikes?)
* Early 2020 (COVID-19 pandemic)
* Late 2022 into early 2023 (rate hikes, recession fears, COVID tech bubble, etc.)
* Mid 2024 (banking crisis, rate hikes)
* Early 2025 (Liberation day)

We're not necessarily looking to explain away each of these time periods or delve into the macro factors that may have been at play or driving the correlations, but we are more interested in the change in correlation over time as a response to some kind of market shock or event.

## Conclusion

Overall, this was a brief but interesting study that dove into the historical correlations amongst a wide range of asset classes. The full period correlation matrices gave us the expected picture, while the rolling correlations showed how much those relationships change over time, particularly in response to market shocks.

## Future Investigation

In [part 2](/posts/asset-class-return-correlations-part-2/), we'll investigate whether the rolling correlations can be used as a signal, by building a "total correlation" metric, looking at future returns based on that metric, and developing a trading strategy.

## References

None
