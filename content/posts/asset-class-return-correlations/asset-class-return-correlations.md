## Introduction

In this post, we'll take a look at historical return correlations between asset classes, including rolling correlations and how those correlations have changed over time. We'll also build a "total correlation" metric, and a trading strategy that uses correlation as a market timing signal.

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
import numpy as np
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
* [plot_histogram](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_histogram): Plot the histogram of a data set from a DataFrame.
* [plot_scatter](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter): Plot the data from a DataFrame for a specified date range and columns.
* [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the timeseries data from a DataFrame for a specified date range and columns.
* [run_linear_regression](/posts/reusable-extensible-python-functions-financial-data-analysis/#run_linear_regression): Run a linear regression using statsmodels OLS and return the results.
* [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.
* [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.


```python
from load_data import load_data
from plot_heatmap import plot_heatmap
from plot_histogram import plot_histogram
from plot_scatter import plot_scatter
from plot_time_series import plot_time_series
from summary_stats import summary_stats
from yf_pull_data import yf_pull_data
```

## Data Overview

For this exercise, we will (mostly) use ETFs as a proxy for asset classes and will use the following:

* Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
* Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
* Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
* US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
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
      <th>2026-10-24</th>
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
      <td>80790.84</td>
      <td>-0.00</td>
      <td>2355.95</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <th>2026-10-25</th>
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
      <td>80024.01</td>
      <td>-0.01</td>
      <td>2326.92</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <th>2026-10-26</th>
      <td>768.69</td>
      <td>0.01</td>
      <td>72.91</td>
      <td>0.01</td>
      <td>138.93</td>
      <td>0.01</td>
      <td>712.20</td>
      <td>0.01</td>
      <td>418.06</td>
      <td>0.01</td>
      <td>...</td>
      <td>367.82</td>
      <td>0.00</td>
      <td>37.31</td>
      <td>-0.01</td>
      <td>98.83</td>
      <td>0.00</td>
      <td>80006.66</td>
      <td>-0.00</td>
      <td>2320.28</td>
      <td>-0.00</td>
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
  </tbody>
</table>
<p>8331 rows × 40 columns</p>
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


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_4.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_5.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_6.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_7.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_8.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_9.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_10.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_11.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_12.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_13.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_14.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_15.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_16.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_17.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_18.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_18_19.png)
    


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

    Shape of fund_data_daily_returns_no_crypto: (8331, 18)
    Rows to drop due to missing data: (5099, 18)



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
      <td>-0.28</td>
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
      <td>0.64</td>
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
      <td>-0.28</td>
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
      <td>0.64</td>
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


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_23_0.png)
    


We'll now include the BTC and ETH data and recalculate the correlation matrix and heatmap. Keep in mind that the BTC and ETH data only goes back to 2015 and 2018 respectively, so the correlation matrix will be calculated using a shorter time period than the other assets.


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

    Shape of fund_data_daily_returns: (8331, 20)
    Rows to drop due to missing data: (2252, 20)



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
      <td>0.93</td>
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
      <td>0.81</td>
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
      <td>0.29</td>
      <td>0.30</td>
    </tr>
    <tr>
      <th>IJR_Daily_Return</th>
      <td>0.84</td>
      <td>0.96</td>
      <td>1.00</td>
      <td>0.71</td>
      <td>0.85</td>
      <td>0.98</td>
      <td>0.90</td>
      <td>0.73</td>
      <td>0.78</td>
      <td>0.66</td>
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
      <td>0.71</td>
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
      <td>0.93</td>
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
      <td>0.81</td>
      <td>0.73</td>
      <td>0.98</td>
      <td>0.96</td>
      <td>0.79</td>
      <td>0.78</td>
      <td>1.00</td>
      <td>0.78</td>
      <td>0.73</td>
      <td>0.74</td>
      <td>-0.02</td>
      <td>-0.07</td>
      <td>-0.09</td>
      <td>0.15</td>
      <td>0.12</td>
      <td>0.22</td>
      <td>0.62</td>
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
      <td>0.78</td>
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
      <td>0.66</td>
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
      <td>0.12</td>
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
      <td>0.62</td>
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
      <td>0.29</td>
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


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_27_0.png)
    


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
      <th>2026-10-22</th>
      <td>0.90</td>
      <td>0.87</td>
      <td>0.87</td>
      <td>0.75</td>
      <td>0.79</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>-0.05</td>
      <td>...</td>
      <td>0.83</td>
      <td>0.39</td>
      <td>0.65</td>
      <td>0.82</td>
      <td>0.86</td>
      <td>0.91</td>
      <td>0.90</td>
      <td>0.93</td>
      <td>0.97</td>
      <td>0.96</td>
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
  </tbody>
</table>
<p>5099 rows × 27 columns</p>
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


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_34_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_34_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_34_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_34_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_34_4.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_34_5.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_34_6.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_34_7.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_34_8.png)
    


## Total Correlation Metric

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
      <th>2026-10-22</th>
      <td>0.90</td>
      <td>0.87</td>
      <td>0.87</td>
      <td>0.75</td>
      <td>0.79</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>-0.05</td>
      <td>...</td>
      <td>0.96</td>
      <td>0.41</td>
      <td>0.61</td>
      <td>0.73</td>
      <td>0.72</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.83</td>
      <td>0.89</td>
      <td>0.90</td>
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
      <td>0.96</td>
      <td>0.09</td>
      <td>0.45</td>
      <td>0.75</td>
      <td>0.73</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.83</td>
      <td>0.89</td>
      <td>0.90</td>
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
      <td>0.96</td>
      <td>0.44</td>
      <td>0.54</td>
      <td>0.76</td>
      <td>0.73</td>
      <td>0.81</td>
      <td>0.79</td>
      <td>0.83</td>
      <td>0.89</td>
      <td>0.90</td>
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
      <td>0.96</td>
      <td>0.98</td>
      <td>0.44</td>
      <td>0.77</td>
      <td>0.72</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.82</td>
      <td>0.89</td>
      <td>0.90</td>
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
      <td>0.96</td>
      <td>0.90</td>
      <td>0.46</td>
      <td>0.67</td>
      <td>0.72</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.83</td>
      <td>0.89</td>
      <td>0.90</td>
    </tr>
  </tbody>
</table>
<p>5099 rows × 36 columns</p>
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


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_38_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_38_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_38_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_38_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_38_4.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_38_5.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_38_6.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_38_7.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_38_8.png)
    


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


Table 5: Total Rolling Correlations With Forward Returns



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
      <th>2026-10-22</th>
      <td>0.90</td>
      <td>0.87</td>
      <td>0.87</td>
      <td>0.75</td>
      <td>0.79</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>-0.05</td>
      <td>...</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
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
      <td>-0.05</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
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
      <td>-0.05</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
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
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>-0.02</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
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
      <td>-0.03</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>-0.02</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>5099 rows × 81 columns</p>
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


Table 6: Percentage of Positive Future Returns by 1w Total Rolling Correlation Decile



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
      <td>53.67</td>
      <td>52.32</td>
      <td>58.76</td>
      <td>55.40</td>
      <td>54.01</td>
      <td>60.16</td>
      <td>56.94</td>
      <td>55.01</td>
      <td>63.87</td>
      <td>...</td>
      <td>57.27</td>
      <td>67.64</td>
      <td>62.34</td>
      <td>60.84</td>
      <td>71.70</td>
      <td>67.11</td>
      <td>65.64</td>
      <td>73.91</td>
      <td>69.50</td>
      <td>66.71</td>
    </tr>
    <tr>
      <th>D1 (-0.28 to 0.68)</th>
      <td>54.03</td>
      <td>47.94</td>
      <td>46.95</td>
      <td>57.79</td>
      <td>50.10</td>
      <td>47.14</td>
      <td>60.59</td>
      <td>54.06</td>
      <td>49.31</td>
      <td>67.33</td>
      <td>...</td>
      <td>56.24</td>
      <td>68.92</td>
      <td>56.77</td>
      <td>54.38</td>
      <td>73.71</td>
      <td>64.54</td>
      <td>61.95</td>
      <td>78.20</td>
      <td>68.60</td>
      <td>64.40</td>
    </tr>
    <tr>
      <th>D2 (0.68 to 0.81)</th>
      <td>56.58</td>
      <td>54.81</td>
      <td>52.06</td>
      <td>57.96</td>
      <td>55.21</td>
      <td>51.08</td>
      <td>57.56</td>
      <td>54.81</td>
      <td>50.88</td>
      <td>64.37</td>
      <td>...</td>
      <td>53.54</td>
      <td>67.19</td>
      <td>59.49</td>
      <td>57.51</td>
      <td>74.30</td>
      <td>68.07</td>
      <td>66.27</td>
      <td>76.83</td>
      <td>71.95</td>
      <td>68.50</td>
    </tr>
    <tr>
      <th>D3 (0.81 to 0.87)</th>
      <td>54.51</td>
      <td>49.80</td>
      <td>50.59</td>
      <td>57.45</td>
      <td>53.53</td>
      <td>52.55</td>
      <td>60.39</td>
      <td>55.10</td>
      <td>54.31</td>
      <td>64.51</td>
      <td>...</td>
      <td>55.88</td>
      <td>68.18</td>
      <td>61.07</td>
      <td>58.30</td>
      <td>72.56</td>
      <td>66.20</td>
      <td>63.02</td>
      <td>76.40</td>
      <td>71.20</td>
      <td>68.60</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.91)</th>
      <td>55.99</td>
      <td>58.94</td>
      <td>58.15</td>
      <td>62.08</td>
      <td>57.17</td>
      <td>56.58</td>
      <td>63.06</td>
      <td>60.31</td>
      <td>59.72</td>
      <td>59.57</td>
      <td>...</td>
      <td>55.03</td>
      <td>67.26</td>
      <td>60.75</td>
      <td>58.58</td>
      <td>69.25</td>
      <td>65.28</td>
      <td>66.27</td>
      <td>75.15</td>
      <td>68.19</td>
      <td>66.80</td>
    </tr>
    <tr>
      <th>D5 (0.91 to 0.93)</th>
      <td>59.41</td>
      <td>58.43</td>
      <td>55.88</td>
      <td>61.18</td>
      <td>57.65</td>
      <td>57.06</td>
      <td>60.59</td>
      <td>55.88</td>
      <td>53.73</td>
      <td>66.40</td>
      <td>...</td>
      <td>57.17</td>
      <td>66.86</td>
      <td>63.91</td>
      <td>62.13</td>
      <td>68.91</td>
      <td>64.36</td>
      <td>63.17</td>
      <td>70.58</td>
      <td>64.02</td>
      <td>63.02</td>
    </tr>
    <tr>
      <th>D6 (0.93 to 0.95)</th>
      <td>49.31</td>
      <td>49.51</td>
      <td>48.33</td>
      <td>54.22</td>
      <td>51.87</td>
      <td>51.47</td>
      <td>56.58</td>
      <td>54.62</td>
      <td>53.83</td>
      <td>57.87</td>
      <td>...</td>
      <td>55.51</td>
      <td>62.40</td>
      <td>61.22</td>
      <td>59.84</td>
      <td>66.27</td>
      <td>63.31</td>
      <td>62.52</td>
      <td>66.67</td>
      <td>63.49</td>
      <td>60.32</td>
    </tr>
    <tr>
      <th>D7 (0.95 to 0.96)</th>
      <td>54.22</td>
      <td>54.42</td>
      <td>53.44</td>
      <td>61.30</td>
      <td>60.31</td>
      <td>58.94</td>
      <td>63.46</td>
      <td>60.51</td>
      <td>58.15</td>
      <td>68.96</td>
      <td>...</td>
      <td>58.74</td>
      <td>69.35</td>
      <td>64.44</td>
      <td>63.46</td>
      <td>71.54</td>
      <td>68.18</td>
      <td>63.83</td>
      <td>72.96</td>
      <td>71.37</td>
      <td>68.59</td>
    </tr>
    <tr>
      <th>D8 (0.96 to 0.97)</th>
      <td>53.33</td>
      <td>52.94</td>
      <td>50.98</td>
      <td>58.63</td>
      <td>55.29</td>
      <td>53.92</td>
      <td>59.41</td>
      <td>59.02</td>
      <td>55.10</td>
      <td>62.16</td>
      <td>...</td>
      <td>57.65</td>
      <td>68.63</td>
      <td>65.49</td>
      <td>64.71</td>
      <td>73.33</td>
      <td>69.22</td>
      <td>68.63</td>
      <td>72.10</td>
      <td>71.91</td>
      <td>68.37</td>
    </tr>
    <tr>
      <th>D9 (0.97 to 0.98)</th>
      <td>55.80</td>
      <td>56.39</td>
      <td>54.03</td>
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
      <td>55.29</td>
      <td>53.53</td>
      <td>52.75</td>
      <td>57.84</td>
      <td>55.69</td>
      <td>55.69</td>
      <td>60.59</td>
      <td>57.45</td>
      <td>58.24</td>
      <td>61.96</td>
      <td>...</td>
      <td>61.37</td>
      <td>70.39</td>
      <td>66.67</td>
      <td>65.10</td>
      <td>73.92</td>
      <td>72.16</td>
      <td>70.39</td>
      <td>77.65</td>
      <td>75.49</td>
      <td>71.96</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 7: Mean Future Return (%) by 1w Total Rolling Correlation Decile



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
      <td>0.15</td>
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
      <td>2.02</td>
      <td>1.90</td>
      <td>1.88</td>
      <td>3.01</td>
      <td>2.85</td>
      <td>2.82</td>
    </tr>
    <tr>
      <th>D1 (-0.28 to 0.68)</th>
      <td>0.07</td>
      <td>0.05</td>
      <td>0.03</td>
      <td>0.13</td>
      <td>0.05</td>
      <td>0.04</td>
      <td>0.27</td>
      <td>0.23</td>
      <td>0.25</td>
      <td>0.56</td>
      <td>...</td>
      <td>0.70</td>
      <td>0.97</td>
      <td>0.70</td>
      <td>0.81</td>
      <td>1.90</td>
      <td>1.44</td>
      <td>1.38</td>
      <td>2.95</td>
      <td>1.93</td>
      <td>1.51</td>
    </tr>
    <tr>
      <th>D2 (0.68 to 0.81)</th>
      <td>0.06</td>
      <td>0.04</td>
      <td>0.04</td>
      <td>0.13</td>
      <td>0.10</td>
      <td>0.07</td>
      <td>0.14</td>
      <td>0.04</td>
      <td>-0.01</td>
      <td>0.38</td>
      <td>...</td>
      <td>0.15</td>
      <td>0.85</td>
      <td>0.42</td>
      <td>0.34</td>
      <td>1.82</td>
      <td>1.42</td>
      <td>1.44</td>
      <td>2.93</td>
      <td>2.39</td>
      <td>2.42</td>
    </tr>
    <tr>
      <th>D3 (0.81 to 0.87)</th>
      <td>-0.00</td>
      <td>-0.03</td>
      <td>-0.03</td>
      <td>0.09</td>
      <td>0.03</td>
      <td>0.03</td>
      <td>0.14</td>
      <td>0.05</td>
      <td>0.06</td>
      <td>0.39</td>
      <td>...</td>
      <td>0.22</td>
      <td>0.89</td>
      <td>0.70</td>
      <td>0.66</td>
      <td>1.83</td>
      <td>1.40</td>
      <td>1.25</td>
      <td>3.17</td>
      <td>2.71</td>
      <td>2.71</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.91)</th>
      <td>0.11</td>
      <td>0.10</td>
      <td>0.08</td>
      <td>0.26</td>
      <td>0.25</td>
      <td>0.23</td>
      <td>0.32</td>
      <td>0.31</td>
      <td>0.29</td>
      <td>0.34</td>
      <td>...</td>
      <td>0.34</td>
      <td>0.66</td>
      <td>0.57</td>
      <td>0.61</td>
      <td>1.70</td>
      <td>1.52</td>
      <td>1.68</td>
      <td>2.60</td>
      <td>2.33</td>
      <td>2.45</td>
    </tr>
    <tr>
      <th>D5 (0.91 to 0.93)</th>
      <td>0.13</td>
      <td>0.17</td>
      <td>0.17</td>
      <td>0.25</td>
      <td>0.28</td>
      <td>0.26</td>
      <td>0.31</td>
      <td>0.34</td>
      <td>0.29</td>
      <td>0.63</td>
      <td>...</td>
      <td>0.54</td>
      <td>1.08</td>
      <td>1.08</td>
      <td>1.03</td>
      <td>1.71</td>
      <td>1.50</td>
      <td>1.37</td>
      <td>2.27</td>
      <td>2.04</td>
      <td>1.96</td>
    </tr>
    <tr>
      <th>D6 (0.93 to 0.95)</th>
      <td>-0.08</td>
      <td>-0.11</td>
      <td>-0.11</td>
      <td>-0.04</td>
      <td>-0.07</td>
      <td>-0.04</td>
      <td>0.09</td>
      <td>0.11</td>
      <td>0.13</td>
      <td>0.11</td>
      <td>...</td>
      <td>0.09</td>
      <td>0.55</td>
      <td>0.71</td>
      <td>0.70</td>
      <td>0.82</td>
      <td>0.74</td>
      <td>0.77</td>
      <td>1.68</td>
      <td>1.73</td>
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
      <td>0.47</td>
      <td>0.87</td>
      <td>...</td>
      <td>0.79</td>
      <td>1.38</td>
      <td>1.41</td>
      <td>1.36</td>
      <td>2.13</td>
      <td>2.24</td>
      <td>2.15</td>
      <td>3.27</td>
      <td>3.48</td>
      <td>3.52</td>
    </tr>
    <tr>
      <th>D8 (0.96 to 0.97)</th>
      <td>0.08</td>
      <td>0.11</td>
      <td>0.13</td>
      <td>0.10</td>
      <td>0.17</td>
      <td>0.15</td>
      <td>0.16</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>0.30</td>
      <td>...</td>
      <td>0.29</td>
      <td>0.93</td>
      <td>0.98</td>
      <td>0.94</td>
      <td>2.34</td>
      <td>2.48</td>
      <td>2.45</td>
      <td>3.31</td>
      <td>3.40</td>
      <td>3.35</td>
    </tr>
    <tr>
      <th>D9 (0.97 to 0.98)</th>
      <td>0.04</td>
      <td>0.04</td>
      <td>0.06</td>
      <td>0.08</td>
      <td>0.09</td>
      <td>0.14</td>
      <td>0.28</td>
      <td>0.31</td>
      <td>0.35</td>
      <td>0.76</td>
      <td>...</td>
      <td>0.82</td>
      <td>1.22</td>
      <td>1.29</td>
      <td>1.32</td>
      <td>2.49</td>
      <td>2.60</td>
      <td>2.64</td>
      <td>3.35</td>
      <td>3.41</td>
      <td>3.36</td>
    </tr>
    <tr>
      <th>D10 (0.98 to 1.00)</th>
      <td>0.04</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.11</td>
      <td>0.11</td>
      <td>0.12</td>
      <td>0.24</td>
      <td>0.19</td>
      <td>0.23</td>
      <td>0.49</td>
      <td>...</td>
      <td>0.56</td>
      <td>1.59</td>
      <td>1.67</td>
      <td>1.67</td>
      <td>3.43</td>
      <td>3.65</td>
      <td>3.67</td>
      <td>4.56</td>
      <td>5.06</td>
      <td>5.08</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 8: Percentage of Positive Future Returns by 2w Total Rolling Correlation Decile



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
      <td>54.86</td>
      <td>53.68</td>
      <td>52.31</td>
      <td>58.76</td>
      <td>55.40</td>
      <td>54.00</td>
      <td>60.16</td>
      <td>56.97</td>
      <td>55.04</td>
      <td>63.88</td>
      <td>...</td>
      <td>57.26</td>
      <td>67.61</td>
      <td>62.30</td>
      <td>60.80</td>
      <td>71.67</td>
      <td>67.08</td>
      <td>65.61</td>
      <td>73.88</td>
      <td>69.46</td>
      <td>66.68</td>
    </tr>
    <tr>
      <th>D1 (-0.03 to 0.76)</th>
      <td>55.51</td>
      <td>48.23</td>
      <td>47.64</td>
      <td>61.02</td>
      <td>49.02</td>
      <td>48.23</td>
      <td>64.23</td>
      <td>53.75</td>
      <td>50.59</td>
      <td>69.37</td>
      <td>...</td>
      <td>55.53</td>
      <td>73.11</td>
      <td>58.96</td>
      <td>55.98</td>
      <td>75.85</td>
      <td>63.87</td>
      <td>64.07</td>
      <td>79.04</td>
      <td>67.27</td>
      <td>65.27</td>
    </tr>
    <tr>
      <th>D2 (0.76 to 0.83)</th>
      <td>54.81</td>
      <td>55.40</td>
      <td>54.62</td>
      <td>58.38</td>
      <td>56.61</td>
      <td>52.86</td>
      <td>60.75</td>
      <td>56.61</td>
      <td>53.85</td>
      <td>66.93</td>
      <td>...</td>
      <td>51.59</td>
      <td>70.82</td>
      <td>60.16</td>
      <td>57.75</td>
      <td>74.74</td>
      <td>66.32</td>
      <td>62.63</td>
      <td>78.59</td>
      <td>72.77</td>
      <td>65.70</td>
    </tr>
    <tr>
      <th>D3 (0.83 to 0.87)</th>
      <td>51.67</td>
      <td>53.44</td>
      <td>52.46</td>
      <td>54.42</td>
      <td>52.06</td>
      <td>51.08</td>
      <td>54.81</td>
      <td>53.05</td>
      <td>52.26</td>
      <td>57.17</td>
      <td>...</td>
      <td>51.08</td>
      <td>64.57</td>
      <td>59.65</td>
      <td>58.07</td>
      <td>72.06</td>
      <td>68.66</td>
      <td>66.47</td>
      <td>76.97</td>
      <td>72.32</td>
      <td>69.09</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.90)</th>
      <td>57.17</td>
      <td>55.80</td>
      <td>54.22</td>
      <td>57.76</td>
      <td>54.03</td>
      <td>52.26</td>
      <td>57.96</td>
      <td>55.99</td>
      <td>54.03</td>
      <td>63.85</td>
      <td>...</td>
      <td>57.17</td>
      <td>63.78</td>
      <td>58.07</td>
      <td>57.48</td>
      <td>67.98</td>
      <td>65.61</td>
      <td>61.46</td>
      <td>71.17</td>
      <td>64.61</td>
      <td>64.41</td>
    </tr>
    <tr>
      <th>D5 (0.90 to 0.92)</th>
      <td>54.22</td>
      <td>56.19</td>
      <td>51.87</td>
      <td>61.69</td>
      <td>60.31</td>
      <td>56.78</td>
      <td>62.28</td>
      <td>63.46</td>
      <td>56.58</td>
      <td>66.60</td>
      <td>...</td>
      <td>59.33</td>
      <td>70.53</td>
      <td>66.60</td>
      <td>64.44</td>
      <td>75.20</td>
      <td>69.69</td>
      <td>67.91</td>
      <td>75.90</td>
      <td>69.72</td>
      <td>67.13</td>
    </tr>
    <tr>
      <th>D6 (0.92 to 0.94)</th>
      <td>56.58</td>
      <td>54.03</td>
      <td>53.63</td>
      <td>57.96</td>
      <td>56.58</td>
      <td>53.83</td>
      <td>58.55</td>
      <td>55.40</td>
      <td>52.46</td>
      <td>61.30</td>
      <td>...</td>
      <td>55.80</td>
      <td>62.28</td>
      <td>60.31</td>
      <td>58.15</td>
      <td>67.19</td>
      <td>63.65</td>
      <td>63.65</td>
      <td>70.14</td>
      <td>65.62</td>
      <td>65.03</td>
    </tr>
    <tr>
      <th>D7 (0.94 to 0.95)</th>
      <td>55.99</td>
      <td>54.03</td>
      <td>49.51</td>
      <td>60.12</td>
      <td>56.58</td>
      <td>55.60</td>
      <td>57.76</td>
      <td>55.01</td>
      <td>56.19</td>
      <td>57.76</td>
      <td>...</td>
      <td>56.39</td>
      <td>62.67</td>
      <td>59.53</td>
      <td>58.74</td>
      <td>64.64</td>
      <td>59.14</td>
      <td>58.55</td>
      <td>63.26</td>
      <td>61.89</td>
      <td>59.53</td>
    </tr>
    <tr>
      <th>D8 (0.95 to 0.96)</th>
      <td>52.06</td>
      <td>48.72</td>
      <td>50.88</td>
      <td>57.17</td>
      <td>53.63</td>
      <td>55.01</td>
      <td>59.33</td>
      <td>55.80</td>
      <td>54.03</td>
      <td>63.26</td>
      <td>...</td>
      <td>58.35</td>
      <td>61.69</td>
      <td>62.28</td>
      <td>60.71</td>
      <td>66.60</td>
      <td>63.46</td>
      <td>61.69</td>
      <td>65.82</td>
      <td>65.42</td>
      <td>61.69</td>
    </tr>
    <tr>
      <th>D9 (0.96 to 0.97)</th>
      <td>56.39</td>
      <td>54.81</td>
      <td>53.24</td>
      <td>64.44</td>
      <td>60.51</td>
      <td>60.51</td>
      <td>66.40</td>
      <td>64.05</td>
      <td>63.06</td>
      <td>66.60</td>
      <td>...</td>
      <td>62.67</td>
      <td>72.30</td>
      <td>66.40</td>
      <td>64.05</td>
      <td>73.87</td>
      <td>71.12</td>
      <td>70.73</td>
      <td>75.83</td>
      <td>74.07</td>
      <td>69.55</td>
    </tr>
    <tr>
      <th>D10 (0.97 to 0.99)</th>
      <td>54.22</td>
      <td>56.19</td>
      <td>55.01</td>
      <td>54.62</td>
      <td>54.62</td>
      <td>53.83</td>
      <td>59.53</td>
      <td>56.58</td>
      <td>57.37</td>
      <td>66.01</td>
      <td>...</td>
      <td>64.64</td>
      <td>74.46</td>
      <td>70.92</td>
      <td>72.50</td>
      <td>78.78</td>
      <td>79.17</td>
      <td>78.78</td>
      <td>82.51</td>
      <td>81.14</td>
      <td>79.37</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 9: Mean Future Return (%) by 2w Total Rolling Correlation Decile



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
      <td>0.15</td>
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
      <td>2.02</td>
      <td>1.90</td>
      <td>1.88</td>
      <td>3.01</td>
      <td>2.85</td>
      <td>2.82</td>
    </tr>
    <tr>
      <th>D1 (-0.03 to 0.76)</th>
      <td>0.06</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>0.19</td>
      <td>0.09</td>
      <td>0.13</td>
      <td>0.31</td>
      <td>0.19</td>
      <td>0.30</td>
      <td>0.63</td>
      <td>...</td>
      <td>0.64</td>
      <td>1.11</td>
      <td>0.51</td>
      <td>0.66</td>
      <td>1.77</td>
      <td>0.90</td>
      <td>0.96</td>
      <td>2.97</td>
      <td>1.41</td>
      <td>0.95</td>
    </tr>
    <tr>
      <th>D2 (0.76 to 0.83)</th>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.07</td>
      <td>0.16</td>
      <td>0.14</td>
      <td>0.14</td>
      <td>0.24</td>
      <td>0.18</td>
      <td>0.14</td>
      <td>0.55</td>
      <td>...</td>
      <td>0.20</td>
      <td>1.02</td>
      <td>0.62</td>
      <td>0.44</td>
      <td>1.77</td>
      <td>1.21</td>
      <td>1.03</td>
      <td>2.91</td>
      <td>2.03</td>
      <td>1.91</td>
    </tr>
    <tr>
      <th>D3 (0.83 to 0.87)</th>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.03</td>
      <td>0.03</td>
      <td>-0.03</td>
      <td>-0.02</td>
      <td>0.08</td>
      <td>-0.01</td>
      <td>0.02</td>
      <td>0.17</td>
      <td>...</td>
      <td>0.04</td>
      <td>0.66</td>
      <td>0.57</td>
      <td>0.65</td>
      <td>2.01</td>
      <td>1.72</td>
      <td>1.95</td>
      <td>3.04</td>
      <td>2.63</td>
      <td>3.10</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.90)</th>
      <td>0.09</td>
      <td>0.10</td>
      <td>0.09</td>
      <td>0.13</td>
      <td>0.17</td>
      <td>0.17</td>
      <td>0.19</td>
      <td>0.23</td>
      <td>0.18</td>
      <td>0.34</td>
      <td>...</td>
      <td>0.37</td>
      <td>0.73</td>
      <td>0.95</td>
      <td>0.98</td>
      <td>1.35</td>
      <td>1.39</td>
      <td>1.31</td>
      <td>2.15</td>
      <td>2.09</td>
      <td>2.18</td>
    </tr>
    <tr>
      <th>D5 (0.90 to 0.92)</th>
      <td>0.06</td>
      <td>0.11</td>
      <td>0.07</td>
      <td>0.20</td>
      <td>0.29</td>
      <td>0.22</td>
      <td>0.38</td>
      <td>0.47</td>
      <td>0.39</td>
      <td>0.57</td>
      <td>...</td>
      <td>0.61</td>
      <td>1.34</td>
      <td>1.42</td>
      <td>1.39</td>
      <td>2.09</td>
      <td>2.07</td>
      <td>2.01</td>
      <td>2.98</td>
      <td>3.02</td>
      <td>3.05</td>
    </tr>
    <tr>
      <th>D6 (0.92 to 0.94)</th>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.05</td>
      <td>0.04</td>
      <td>0.03</td>
      <td>0.04</td>
      <td>0.12</td>
      <td>0.17</td>
      <td>0.19</td>
      <td>0.30</td>
      <td>...</td>
      <td>0.35</td>
      <td>0.59</td>
      <td>0.66</td>
      <td>0.63</td>
      <td>1.03</td>
      <td>0.88</td>
      <td>0.82</td>
      <td>1.96</td>
      <td>2.01</td>
      <td>1.93</td>
    </tr>
    <tr>
      <th>D7 (0.94 to 0.95)</th>
      <td>0.03</td>
      <td>0.01</td>
      <td>-0.03</td>
      <td>0.16</td>
      <td>0.13</td>
      <td>0.07</td>
      <td>0.09</td>
      <td>0.01</td>
      <td>-0.05</td>
      <td>0.14</td>
      <td>...</td>
      <td>0.02</td>
      <td>0.51</td>
      <td>0.41</td>
      <td>0.38</td>
      <td>1.19</td>
      <td>1.11</td>
      <td>0.94</td>
      <td>1.64</td>
      <td>1.78</td>
      <td>1.58</td>
    </tr>
    <tr>
      <th>D8 (0.95 to 0.96)</th>
      <td>0.03</td>
      <td>0.01</td>
      <td>0.02</td>
      <td>0.05</td>
      <td>0.01</td>
      <td>0.03</td>
      <td>0.16</td>
      <td>0.15</td>
      <td>0.14</td>
      <td>0.44</td>
      <td>...</td>
      <td>0.42</td>
      <td>0.60</td>
      <td>0.60</td>
      <td>0.58</td>
      <td>1.38</td>
      <td>1.46</td>
      <td>1.49</td>
      <td>2.56</td>
      <td>2.74</td>
      <td>2.77</td>
    </tr>
    <tr>
      <th>D9 (0.96 to 0.97)</th>
      <td>0.12</td>
      <td>0.12</td>
      <td>0.12</td>
      <td>0.42</td>
      <td>0.43</td>
      <td>0.49</td>
      <td>0.59</td>
      <td>0.59</td>
      <td>0.64</td>
      <td>0.65</td>
      <td>...</td>
      <td>0.62</td>
      <td>1.17</td>
      <td>1.11</td>
      <td>1.02</td>
      <td>3.05</td>
      <td>3.27</td>
      <td>3.25</td>
      <td>3.99</td>
      <td>4.27</td>
      <td>4.20</td>
    </tr>
    <tr>
      <th>D10 (0.97 to 0.99)</th>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.03</td>
      <td>0.10</td>
      <td>0.12</td>
      <td>0.11</td>
      <td>0.27</td>
      <td>0.31</td>
      <td>0.33</td>
      <td>1.05</td>
      <td>...</td>
      <td>1.24</td>
      <td>2.39</td>
      <td>2.66</td>
      <td>2.71</td>
      <td>4.50</td>
      <td>4.97</td>
      <td>5.03</td>
      <td>5.87</td>
      <td>6.44</td>
      <td>6.43</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 10: Percentage of Positive Future Returns by 1m Total Rolling Correlation Decile



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
      <td>54.86</td>
      <td>53.70</td>
      <td>52.32</td>
      <td>58.75</td>
      <td>55.44</td>
      <td>54.02</td>
      <td>60.17</td>
      <td>56.98</td>
      <td>55.05</td>
      <td>63.80</td>
      <td>...</td>
      <td>57.17</td>
      <td>67.54</td>
      <td>62.24</td>
      <td>60.72</td>
      <td>71.61</td>
      <td>67.00</td>
      <td>65.54</td>
      <td>73.82</td>
      <td>69.40</td>
      <td>66.61</td>
    </tr>
    <tr>
      <th>D1 (0.19 to 0.79)</th>
      <td>56.02</td>
      <td>51.68</td>
      <td>50.30</td>
      <td>59.21</td>
      <td>52.67</td>
      <td>49.11</td>
      <td>58.65</td>
      <td>52.49</td>
      <td>50.10</td>
      <td>63.40</td>
      <td>...</td>
      <td>54.20</td>
      <td>68.08</td>
      <td>59.19</td>
      <td>55.15</td>
      <td>74.44</td>
      <td>62.68</td>
      <td>60.04</td>
      <td>75.05</td>
      <td>60.45</td>
      <td>57.61</td>
    </tr>
    <tr>
      <th>D2 (0.79 to 0.84)</th>
      <td>54.92</td>
      <td>52.17</td>
      <td>51.38</td>
      <td>59.25</td>
      <td>50.98</td>
      <td>49.02</td>
      <td>61.02</td>
      <td>51.38</td>
      <td>50.00</td>
      <td>66.80</td>
      <td>...</td>
      <td>50.59</td>
      <td>65.60</td>
      <td>55.00</td>
      <td>53.60</td>
      <td>72.16</td>
      <td>65.36</td>
      <td>60.62</td>
      <td>80.54</td>
      <td>74.33</td>
      <td>69.98</td>
    </tr>
    <tr>
      <th>D3 (0.84 to 0.87)</th>
      <td>55.51</td>
      <td>54.33</td>
      <td>51.38</td>
      <td>58.46</td>
      <td>53.35</td>
      <td>50.79</td>
      <td>61.02</td>
      <td>56.10</td>
      <td>50.98</td>
      <td>65.16</td>
      <td>...</td>
      <td>51.57</td>
      <td>72.44</td>
      <td>61.02</td>
      <td>58.46</td>
      <td>78.17</td>
      <td>69.05</td>
      <td>63.29</td>
      <td>75.05</td>
      <td>68.30</td>
      <td>67.28</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.89)</th>
      <td>53.54</td>
      <td>54.92</td>
      <td>51.57</td>
      <td>58.27</td>
      <td>57.87</td>
      <td>53.35</td>
      <td>59.45</td>
      <td>60.83</td>
      <td>57.68</td>
      <td>60.24</td>
      <td>...</td>
      <td>56.30</td>
      <td>69.69</td>
      <td>62.60</td>
      <td>60.04</td>
      <td>72.83</td>
      <td>70.67</td>
      <td>69.49</td>
      <td>80.75</td>
      <td>71.83</td>
      <td>71.83</td>
    </tr>
    <tr>
      <th>D5 (0.89 to 0.92)</th>
      <td>56.10</td>
      <td>55.12</td>
      <td>54.72</td>
      <td>60.43</td>
      <td>58.46</td>
      <td>58.46</td>
      <td>59.06</td>
      <td>57.87</td>
      <td>56.50</td>
      <td>64.76</td>
      <td>...</td>
      <td>57.09</td>
      <td>67.91</td>
      <td>63.98</td>
      <td>60.63</td>
      <td>70.67</td>
      <td>64.37</td>
      <td>63.98</td>
      <td>71.85</td>
      <td>68.31</td>
      <td>65.94</td>
    </tr>
    <tr>
      <th>D6 (0.92 to 0.93)</th>
      <td>53.45</td>
      <td>52.27</td>
      <td>51.48</td>
      <td>58.78</td>
      <td>57.59</td>
      <td>55.62</td>
      <td>60.75</td>
      <td>60.36</td>
      <td>59.76</td>
      <td>57.40</td>
      <td>...</td>
      <td>57.79</td>
      <td>61.14</td>
      <td>60.16</td>
      <td>61.34</td>
      <td>58.78</td>
      <td>54.04</td>
      <td>52.47</td>
      <td>58.78</td>
      <td>54.64</td>
      <td>51.28</td>
    </tr>
    <tr>
      <th>D7 (0.93 to 0.94)</th>
      <td>55.71</td>
      <td>53.94</td>
      <td>52.56</td>
      <td>54.53</td>
      <td>50.79</td>
      <td>50.98</td>
      <td>55.31</td>
      <td>52.36</td>
      <td>52.56</td>
      <td>59.06</td>
      <td>...</td>
      <td>55.51</td>
      <td>63.98</td>
      <td>59.84</td>
      <td>58.66</td>
      <td>62.80</td>
      <td>61.81</td>
      <td>61.81</td>
      <td>65.16</td>
      <td>65.35</td>
      <td>58.07</td>
    </tr>
    <tr>
      <th>D8 (0.94 to 0.95)</th>
      <td>55.71</td>
      <td>53.74</td>
      <td>51.97</td>
      <td>59.06</td>
      <td>56.50</td>
      <td>58.86</td>
      <td>64.76</td>
      <td>60.04</td>
      <td>57.28</td>
      <td>63.98</td>
      <td>...</td>
      <td>60.04</td>
      <td>64.57</td>
      <td>63.98</td>
      <td>63.19</td>
      <td>71.46</td>
      <td>70.28</td>
      <td>72.05</td>
      <td>74.02</td>
      <td>73.43</td>
      <td>71.06</td>
    </tr>
    <tr>
      <th>D9 (0.95 to 0.97)</th>
      <td>54.33</td>
      <td>55.71</td>
      <td>54.33</td>
      <td>62.20</td>
      <td>58.86</td>
      <td>55.91</td>
      <td>60.43</td>
      <td>58.27</td>
      <td>56.10</td>
      <td>69.88</td>
      <td>...</td>
      <td>62.60</td>
      <td>69.09</td>
      <td>66.93</td>
      <td>65.75</td>
      <td>74.80</td>
      <td>73.62</td>
      <td>72.83</td>
      <td>73.82</td>
      <td>76.57</td>
      <td>73.03</td>
    </tr>
    <tr>
      <th>D10 (0.97 to 0.99)</th>
      <td>53.35</td>
      <td>53.15</td>
      <td>53.54</td>
      <td>57.28</td>
      <td>57.28</td>
      <td>58.07</td>
      <td>61.22</td>
      <td>60.04</td>
      <td>59.45</td>
      <td>67.32</td>
      <td>...</td>
      <td>65.94</td>
      <td>72.83</td>
      <td>69.49</td>
      <td>70.08</td>
      <td>80.12</td>
      <td>77.95</td>
      <td>78.35</td>
      <td>83.66</td>
      <td>80.71</td>
      <td>79.92</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 21 columns</p>
</div>



Table 11: Mean Future Return (%) by 1m Total Rolling Correlation Decile



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
      <td>0.15</td>
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
      <td>0.94</td>
      <td>2.01</td>
      <td>1.89</td>
      <td>1.87</td>
      <td>3.00</td>
      <td>2.84</td>
      <td>2.80</td>
    </tr>
    <tr>
      <th>D1 (0.19 to 0.79)</th>
      <td>0.03</td>
      <td>-0.00</td>
      <td>0.00</td>
      <td>0.10</td>
      <td>0.05</td>
      <td>0.08</td>
      <td>0.16</td>
      <td>0.09</td>
      <td>0.15</td>
      <td>0.39</td>
      <td>...</td>
      <td>0.35</td>
      <td>0.83</td>
      <td>0.51</td>
      <td>0.61</td>
      <td>1.28</td>
      <td>0.21</td>
      <td>-0.02</td>
      <td>2.51</td>
      <td>0.59</td>
      <td>-0.13</td>
    </tr>
    <tr>
      <th>D2 (0.79 to 0.84)</th>
      <td>0.06</td>
      <td>0.04</td>
      <td>0.06</td>
      <td>0.15</td>
      <td>0.04</td>
      <td>0.04</td>
      <td>0.28</td>
      <td>0.11</td>
      <td>0.10</td>
      <td>0.54</td>
      <td>...</td>
      <td>0.25</td>
      <td>0.67</td>
      <td>0.31</td>
      <td>0.32</td>
      <td>1.81</td>
      <td>1.09</td>
      <td>1.08</td>
      <td>3.33</td>
      <td>2.51</td>
      <td>2.66</td>
    </tr>
    <tr>
      <th>D3 (0.84 to 0.87)</th>
      <td>0.06</td>
      <td>0.05</td>
      <td>0.02</td>
      <td>0.19</td>
      <td>0.14</td>
      <td>0.07</td>
      <td>0.29</td>
      <td>0.17</td>
      <td>0.08</td>
      <td>0.60</td>
      <td>...</td>
      <td>0.20</td>
      <td>1.29</td>
      <td>0.95</td>
      <td>0.77</td>
      <td>2.38</td>
      <td>1.85</td>
      <td>1.81</td>
      <td>2.99</td>
      <td>2.23</td>
      <td>2.51</td>
    </tr>
    <tr>
      <th>D4 (0.87 to 0.89)</th>
      <td>0.02</td>
      <td>0.05</td>
      <td>0.04</td>
      <td>0.16</td>
      <td>0.21</td>
      <td>0.20</td>
      <td>0.24</td>
      <td>0.34</td>
      <td>0.34</td>
      <td>0.34</td>
      <td>...</td>
      <td>0.48</td>
      <td>1.23</td>
      <td>1.21</td>
      <td>1.27</td>
      <td>2.47</td>
      <td>2.33</td>
      <td>2.55</td>
      <td>3.44</td>
      <td>3.55</td>
      <td>4.09</td>
    </tr>
    <tr>
      <th>D5 (0.89 to 0.92)</th>
      <td>0.10</td>
      <td>0.11</td>
      <td>0.12</td>
      <td>0.19</td>
      <td>0.22</td>
      <td>0.27</td>
      <td>0.24</td>
      <td>0.31</td>
      <td>0.40</td>
      <td>0.53</td>
      <td>...</td>
      <td>0.73</td>
      <td>1.07</td>
      <td>1.12</td>
      <td>1.22</td>
      <td>1.56</td>
      <td>1.46</td>
      <td>1.63</td>
      <td>2.31</td>
      <td>2.35</td>
      <td>2.73</td>
    </tr>
    <tr>
      <th>D6 (0.92 to 0.93)</th>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.11</td>
      <td>0.15</td>
      <td>0.16</td>
      <td>0.15</td>
      <td>0.25</td>
      <td>0.25</td>
      <td>0.17</td>
      <td>...</td>
      <td>0.37</td>
      <td>0.17</td>
      <td>0.36</td>
      <td>0.35</td>
      <td>-0.46</td>
      <td>-0.38</td>
      <td>-0.58</td>
      <td>0.12</td>
      <td>0.21</td>
      <td>-0.13</td>
    </tr>
    <tr>
      <th>D7 (0.93 to 0.94)</th>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>-0.15</td>
      <td>-0.18</td>
      <td>-0.16</td>
      <td>-0.05</td>
      <td>-0.11</td>
      <td>-0.11</td>
      <td>0.11</td>
      <td>...</td>
      <td>0.03</td>
      <td>0.46</td>
      <td>0.27</td>
      <td>0.37</td>
      <td>0.78</td>
      <td>0.83</td>
      <td>0.75</td>
      <td>1.31</td>
      <td>1.51</td>
      <td>1.34</td>
    </tr>
    <tr>
      <th>D8 (0.94 to 0.95)</th>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.17</td>
      <td>0.19</td>
      <td>0.19</td>
      <td>0.28</td>
      <td>0.29</td>
      <td>0.28</td>
      <td>0.35</td>
      <td>...</td>
      <td>0.39</td>
      <td>0.55</td>
      <td>0.64</td>
      <td>0.58</td>
      <td>2.23</td>
      <td>2.60</td>
      <td>2.70</td>
      <td>3.26</td>
      <td>3.72</td>
      <td>3.68</td>
    </tr>
    <tr>
      <th>D9 (0.95 to 0.97)</th>
      <td>0.12</td>
      <td>0.10</td>
      <td>0.10</td>
      <td>0.26</td>
      <td>0.21</td>
      <td>0.17</td>
      <td>0.25</td>
      <td>0.18</td>
      <td>0.13</td>
      <td>0.65</td>
      <td>...</td>
      <td>0.44</td>
      <td>1.22</td>
      <td>1.31</td>
      <td>1.21</td>
      <td>2.81</td>
      <td>3.22</td>
      <td>3.24</td>
      <td>3.81</td>
      <td>4.29</td>
      <td>4.24</td>
    </tr>
    <tr>
      <th>D10 (0.97 to 0.99)</th>
      <td>0.05</td>
      <td>0.07</td>
      <td>0.07</td>
      <td>0.29</td>
      <td>0.34</td>
      <td>0.35</td>
      <td>0.59</td>
      <td>0.67</td>
      <td>0.68</td>
      <td>1.12</td>
      <td>...</td>
      <td>1.24</td>
      <td>2.59</td>
      <td>2.82</td>
      <td>2.71</td>
      <td>5.18</td>
      <td>5.64</td>
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


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_51_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_51_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_51_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_51_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_51_4.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_51_5.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_51_6.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_51_7.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_51_8.png)
    


It's interesting what the baseline (all days) columns reveal about future returns. For *every* plot, the positive future return percentage increases as time increases. We see a similar, but slightly less pronounced, trend for the total rolling correlation deciles, and this suggests that, on average, the likelihood of positive future returns grows over longer time horizons, regardless of the rolling correlation decile. There is certainly a "belly" present in some of the plots, particularly at the 6th and 7th deciles.

The 10th decile consistently shows the highest positive future return percentages across all time horizons, indicating that assets in this decile tend to perform better in the future compared to those in lower deciles, so let's cherry pick the 2 week total rolling correlation for IVV, IJH, and IJR, at the 10th decile, and the 3 month forward return to examine more closely.

## 2w Total Rolling Correlation, 10th Decile, 3m Forward Return for IVV


```python
# Assign each day to a correlation decile and record each decile's range
bucket = pd.qcut(total_rolling_corr_with_returns.dropna(subset=["total_rolling_correlation_2w"])["total_rolling_correlation_2w"], 10, labels=decile_labels)

# Merge the decile bucket back into the original DataFrame
total_rolling_corr_with_returns = total_rolling_corr_with_returns.dropna(subset=["total_rolling_correlation_2w"])
total_rolling_corr_with_returns["total_rolling_correlation_2w_decile"] = bucket

display(Markdown(f"Table {next(table_number)}: Total Rolling Correlations With 2w Decile Assignments"))
display(total_rolling_corr_with_returns)
```


Table 12: Total Rolling Correlations With 2w Decile Assignments



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
      <th>2026-10-22</th>
      <td>0.90</td>
      <td>0.87</td>
      <td>0.87</td>
      <td>0.75</td>
      <td>0.79</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.88</td>
      <td>0.90</td>
      <td>-0.05</td>
      <td>...</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>D1</td>
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
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>D1</td>
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
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>-0.05</td>
      <td>NaN</td>
      <td>D2</td>
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
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>-0.02</td>
      <td>NaN</td>
      <td>-0.03</td>
      <td>NaN</td>
      <td>D2</td>
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
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>-0.02</td>
      <td>NaN</td>
      <td>-0.04</td>
      <td>NaN</td>
      <td>D1</td>
    </tr>
  </tbody>
</table>
<p>5090 rows × 82 columns</p>
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


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_55_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_55_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_55_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_55_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_55_4.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_55_5.png)
    


## Trading Strategy

Next, let's develop a simple trading strategy. When the total rolling correlation hits the 10th decile, we will open a long position in the fund, hold the position for exactly 3 months, and then close it. We'll run the strategy separately for each of the three funds. Here's the complete details:

* Use the 10th decile of the total rolling correlation as the signal for entering a trade.
* Position sizing: we always go fully long on the fund when a signal occurs, and we do not scale in or out.
* Entry: when the 2w total correlation decile is D10 on day i, buy the fund at that day's close.
* Exit: hold for exactly 63 trading days (return_windows["3m"]), then sell at that day's close.
* Overlapping signals: a D10 day that comes while a position is open is ignored. If the exit day is itself a D10 day, the strategy buys again, so the position just continues.
* Shared signal: the signal comes from the total correlation across all three funds, so the entry and exit dates are the same for IVV, IJH, and IJR. Only the returns differ.
* Settings: strategy_tickers, signal_decile and hold_days are variables at the top, so we can easily modify them to try other combinations.

We'll start with the strategy, and the complete list of trades.


```python
# Strategy parameters
strategy_tickers = ["IVV", "IJH", "IJR"]
signal_column = "total_rolling_correlation_2w_decile"
signal_decile = "D10"
hold_days = return_windows["3m"]  # 63 trading days

strategy_df = total_rolling_corr_with_returns[
    ["total_rolling_correlation_2w", signal_column] + [f"{ticker}_Daily_Return" for ticker in strategy_tickers]
].copy()
for ticker in strategy_tickers:
    strategy_df[f"{ticker}_Daily_Return"] = strategy_df[f"{ticker}_Daily_Return"].fillna(0)
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


Table 13: Days in D10 With an Open Position



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
      <th>Signal</th>
      <th>Position</th>
      <th>IVV_Strategy_Return</th>
      <th>IJH_Strategy_Return</th>
      <th>IJR_Strategy_Return</th>
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
      <td>True</td>
      <td>1.00</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <th>2007-02-28</th>
      <td>0.98</td>
      <td>D10</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.01</td>
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
      <td>True</td>
      <td>1.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>2007-03-02</th>
      <td>0.97</td>
      <td>D10</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>True</td>
      <td>1.00</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.02</td>
    </tr>
    <tr>
      <th>2007-03-06</th>
      <td>0.97</td>
      <td>D10</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.02</td>
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
    </tr>
    <tr>
      <th>2025-04-22</th>
      <td>0.99</td>
      <td>D10</td>
      <td>0.03</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.03</td>
      <td>0.03</td>
      <td>0.02</td>
    </tr>
    <tr>
      <th>2025-04-23</th>
      <td>0.99</td>
      <td>D10</td>
      <td>0.02</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.02</td>
      <td>0.01</td>
      <td>0.01</td>
    </tr>
    <tr>
      <th>2026-04-09</th>
      <td>0.99</td>
      <td>D10</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.01</td>
    </tr>
    <tr>
      <th>2026-04-10</th>
      <td>0.99</td>
      <td>D10</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>True</td>
      <td>1.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>2026-04-13</th>
      <td>0.98</td>
      <td>D10</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>True</td>
      <td>1.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.01</td>
    </tr>
  </tbody>
</table>
<p>472 rows × 10 columns</p>
</div>



Table 14: Strategy Trades



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
    trade_returns = closed_trades[f"{ticker} Return"]
    print(f"\n{ticker}:")
    print(f"  Win rate (closed trades): {(trade_returns > 0).mean() * 100:.2f}%")
    print(f"  Average return per closed trade: {trade_returns.mean() * 100:.2f}%")
    print(f"  Max trade gain: {trade_returns.max() * 100:.2f}%")
    print(f"  Max trade loss: {trade_returns.min() * 100:.2f}%")
```

    Total trades: 44 (44 closed)
    Time in market: 54.46%
    
    IVV:
      Win rate (closed trades): 68.18%
      Average return per closed trade: 3.96%
      Max trade gain: 18.70%
      Max trade loss: -9.01%
    
    IJH:
      Win rate (closed trades): 68.18%
      Average return per closed trade: 4.37%
      Max trade gain: 23.09%
      Max trade loss: -11.54%
    
    IJR:
      Win rate (closed trades): 65.91%
      Average return per closed trade: 4.32%
      Max trade gain: 23.17%
      Max trade loss: -11.87%


Now we can compare the summary stats for the different funds and see how the strategy performed across IVV, IJH, and IJR.


```python
# Compare each strategy against buy and hold for the same period
strategy_stats = pd.concat(
    [
        summary_stats(
            fund_list=[ticker],
            df=strategy_df[[return_column]],
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


Table 15: Strategy vs Buy and Hold Summary Statistics



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
      <td>5090</td>
      <td>2006-08-04</td>
      <td>2026-10-28</td>
      <td>0.09</td>
      <td>0.15</td>
      <td>0.60</td>
      <td>0.08</td>
      <td>0.10</td>
      <td>2025-04-09</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.30</td>
      <td>2008-05-19</td>
      <td>2009-03-09</td>
      <td>2009-06-01</td>
      <td>84</td>
      <td>0.28</td>
    </tr>
    <tr>
      <th>IVV_Daily_Return</th>
      <td>5090</td>
      <td>2006-08-04</td>
      <td>2026-10-28</td>
      <td>0.13</td>
      <td>0.19</td>
      <td>0.66</td>
      <td>0.11</td>
      <td>0.11</td>
      <td>2008-10-28</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.55</td>
      <td>2007-10-09</td>
      <td>2009-03-09</td>
      <td>2012-08-16</td>
      <td>1256</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>IJH_Strategy_Return</th>
      <td>5090</td>
      <td>2006-08-04</td>
      <td>2026-10-28</td>
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
      <td>99</td>
      <td>0.25</td>
    </tr>
    <tr>
      <th>IJH_Daily_Return</th>
      <td>5090</td>
      <td>2006-08-04</td>
      <td>2026-10-28</td>
      <td>0.12</td>
      <td>0.22</td>
      <td>0.53</td>
      <td>0.10</td>
      <td>0.11</td>
      <td>2020-03-24</td>
      <td>-0.14</td>
      <td>2020-03-16</td>
      <td>-0.55</td>
      <td>2007-06-04</td>
      <td>2009-03-09</td>
      <td>2010-12-02</td>
      <td>633</td>
      <td>0.18</td>
    </tr>
    <tr>
      <th>IJR_Strategy_Return</th>
      <td>5090</td>
      <td>2006-08-04</td>
      <td>2026-10-28</td>
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
      <td>120</td>
      <td>0.25</td>
    </tr>
    <tr>
      <th>IJR_Daily_Return</th>
      <td>5090</td>
      <td>2006-08-04</td>
      <td>2026-10-28</td>
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
      <td>700</td>
      <td>0.16</td>
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

plot_time_series(
    df=strategy_df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{ticker}_Strategy_Cumulative_Return" for ticker in strategy_tickers]
    + [f"{ticker}_Buy_Hold_Cumulative_Return" for ticker in strategy_tickers],
    title=f"Figure {next(figure_number)}: Total Rolling Correlation {signal_decile} Strategies vs Buy and Hold",
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


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_64_0.png)
    



```python
# Drawdowns for each strategy and buy and hold, measured from the running peak of each equity curve
for ticker in strategy_tickers:
    strategy_equity = (1 + strategy_df[f"{ticker}_Strategy_Return"]).cumprod()
    buy_hold_equity = (1 + strategy_df[f"{ticker}_Daily_Return"]).cumprod()

    strategy_df[f"{ticker}_Strategy_Drawdown"] = strategy_equity / strategy_equity.cummax() - 1
    strategy_df[f"{ticker}_Buy_Hold_Drawdown"] = buy_hold_equity / buy_hold_equity.cummax() - 1

plot_time_series(
    df=strategy_df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{ticker}_Strategy_Drawdown" for ticker in strategy_tickers]
    + [f"{ticker}_Buy_Hold_Drawdown" for ticker in strategy_tickers],
    title=f"Figure {next(figure_number)}: Total Rolling Correlation {signal_decile} Strategies vs Buy and Hold Drawdowns",
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


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_65_0.png)
    


We end up with 44 trades over the 20 year period, with a win rate of 68% for IVV and IJH, and 66% for IJR, not bad overall. Since the signal is shared, all three strategies spend just under 55% of their time in the market, which really gives us an opportunity to use our capital the other 45% of the time, either in a risk free asset or another strategy altogether.

For IVV, with a CAGR of 8%, we underperform the buy-and-hold strategy over the same period, but we also experience lower volatility (16% vs 19%), and much lower max drawdowns (30% vs 55%). Our strategy gives us a MAR ratio of 0.28, vs 0.20 for the buy-and-hold strategy.

IJH and IJR tell a similar story, but the gap in CAGR is much smaller:

* IJH: a CAGR of 9.1% vs 9.7% for buy-and-hold, with lower volatility (18% vs 22%), lower max drawdowns (36% vs 55%), and a MAR ratio of 0.25 vs 0.18.
* IJR: a CAGR of 8.9% vs 9.3% for buy-and-hold, with lower volatility (19% vs 24%), lower max drawdowns (35% vs 58%), and a MAR ratio of 0.25 vs 0.16.

For IJH and IJR, we give up less than 1% of CAGR per year in exchange for the reduced risk, and both strategies also have a higher Sharpe ratio than their buy-and-hold counterparts, which is not the case for IVV.

The difference in CAGR does add up over the long term, the effect of which we can see in the cumulative return plot, particularly for IVV.

The drawdown plot further illustrates the reduced risk of the strategies compared to the buy-and-hold approach, highlighting the lower maximum drawdowns experienced over the same period. During the GFC, the IVV strategy experienced its max drawdown of 30%, which was significantly lower than that of the buy-and-hold strategy at 55%. Interestingly, the max drawdowns for the IJH and IJR strategies came during the COVID crash in early 2020 rather than the GFC, while all three buy-and-hold strategies saw their max drawdowns during the GFC.

## Conclusion

Overall, this was a brief but interesting study that dove into the historical correlations amongst a wide range of asset classes. We looked at a series of rolling correlations amongst the asset classes, and then delved into the different deciles of a "total correlation" metric, assembled from the rolling correlations of 3 well known US equity ETFs. This analysis, including comparison to a baseline, gave us insight into where the total correlations could be used to improve our ability to time market entries and exits. Finally, we built a simple trading strategy using a single total correlation window and decile and a single future return window, as a proof of concept for how these insights could be applied in practice. This strategy, while underperforming over the long-term, did have lower volatility and drawdowns, demonstrating the potential risk management benefits of incorporating total correlation information into trading decisions.

## Future Investigation

None

## References

None
