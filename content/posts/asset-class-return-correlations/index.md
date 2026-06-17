---
title: Asset Class Return Correlations
description: A look at historical return correlations between asset classes.
summary: A look at historical return correlations between asset classes.
slug: asset-class-return-correlations
date: 2026-04-20 00:00:01+0000
lastmod: 2026-04-20 00:00:01+0000
feature:
coverCaption:
draft: true
topics: [
]
---
{{< katex >}}

## Introduction

In this post, we'll take a look at historical return correlations between asset classes, including rolling returns, and how those correlations have changed over time.

 ## Python Imports


```python
# Standard Library
import datetime
import io
import os
import random
import sys
import warnings

from datetime import datetime, timedelta
from pathlib import Path

# Data Handling
import numpy as np
import pandas as pd

# Data Visualization
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from matplotlib.ticker import FormatStrFormatter, FuncFormatter, MultipleLocator

# Statistical Analysis
import statsmodels.api as sm

# Machine Learning
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Suppress warnings
warnings.filterwarnings("ignore")
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
* [pandas_set_decimal_places](/posts/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.
* [plot_histogram](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_histogram): Plot the histogram of a data set from a DataFrame.
* [plot_scatter](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter): Plot the data from a DataFrame for a specified date range and columns.
* [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the timeseries data from a DataFrame for a specified date range and columns.
* [run_linear_regression](/posts/reusable-extensible-python-functions-financial-data-analysis/#run_linear_regression): Run a linear regression using statsmodels OLS and return the results.
* [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.
* [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.


```python
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_heatmap import plot_heatmap
from plot_histogram import plot_histogram
from plot_scatter import plot_scatter
from plot_time_series import plot_time_series
from run_regression import run_regression
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

## Acquire & Plot Data

We'll now pull the data for all the ETFs and cryptocurrencies listed above.


```python
pandas_set_decimal_places(2)

# Create list of tickers to pull data for
us_equity_tickers = ["IVV", "IJH", "IJR", "QQQ", "IWB", "IWD", "IWF", "IWM"]
intl_equity_tickers = ["EFA", "EEM", "IEV"]
equity_tickers = us_equity_tickers + intl_equity_tickers
bond_tickers = ["SHY", "IEF", "TLT", "AGG"]
commodity_tickers = ["GLD", "GSG"]
real_estate_tickers = ["IYR"]
cryptoasset_tickers = ["BTC-USD", "ETH-USD"]
etf_tickers = us_equity_tickers + intl_equity_tickers + bond_tickers + commodity_tickers + real_estate_tickers
tickers_dict = {
    "IVV" : "Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)",
    "IJH" : "Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)",
    "IJR" : "Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)",
    "QQQ" : "US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)",
    "IWB" : "Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)",
    "IWM" : "Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)",
    "IWD" : "Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)",
    "IWF" : "Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)",
    "EFA" : "International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)",
    "EEM" : "Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)",
    "IEV" : "European Stocks -- IEV (iShares S&P Europe 350 ETF)",
    "SHY" : "Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)",
    "IEF" : "Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)",
    "TLT" : "Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)",
    "AGG" : "Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)",
    "GLD" : "Gold -- GLD (SPDR Gold Shares)",
    "GSG" : "Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)",
    "IYR" : "Real Estate -- IYR (iShares U.S. Real Estate ETF)",
    "BTC-USD" : "Bitcoin -- BTC-USD (Bitcoin USD)",
    "ETH-USD" : "Ethereum -- ETH-USD (Ethereum USD)",
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

We'll then peform the following:
* Load data
* Rename columns to include the ticker (e.g. "QQQ_Close", "QQQ_Adj_Close", etc.)
* Drop all columns except for "Adj Close"
* Calculate the daily returns
* Combine the data into a single DataFrame


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
    data = data.rename(columns={
        "Adj Close": f"{ticker}_Adj_Close",
        "Close": f"{ticker}_Close",
        "High": f"{ticker}_High",
        "Low": f"{ticker}_Low",
        "Open": f"{ticker}_Open",
        "Volume": f"{ticker}_Volume"
    })

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
    data = data.rename(columns={
        "Adj Close": f"{ticker}_Adj_Close",
        "Close": f"{ticker}_Close",
        "High": f"{ticker}_High",
        "Low": f"{ticker}_Low",
        "Open": f"{ticker}_Open",
        "Volume": f"{ticker}_Volume"
    })

    # Drop all columns except for the adjusted close price and date index
    data = data[[f"{ticker}_Adj_Close"]]

    # Calculate daily returns and add as new column
    data[f"{ticker}_Daily_Return"] = data[f"{ticker}_Adj_Close"].pct_change()

    # Concatenate the data for this ticker with the main fund_data DataFrame
    fund_data = pd.concat([fund_data, data], axis=1)

display(fund_data)
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
      <td>43.07</td>
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
      <td>43.29</td>
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
      <td>42.23</td>
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
      <td>43.44</td>
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
      <td>43.81</td>
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
      <th>2026-06-09</th>
      <td>740.75</td>
      <td>-0.00</td>
      <td>74.73</td>
      <td>0.01</td>
      <td>139.89</td>
      <td>0.01</td>
      <td>707.83</td>
      <td>-0.01</td>
      <td>403.11</td>
      <td>-0.00</td>
      <td>...</td>
      <td>390.78</td>
      <td>-0.02</td>
      <td>31.24</td>
      <td>-0.02</td>
      <td>103.49</td>
      <td>0.02</td>
      <td>61643.78</td>
      <td>-0.02</td>
      <td>1637.71</td>
      <td>-0.03</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>728.92</td>
      <td>-0.02</td>
      <td>73.65</td>
      <td>-0.01</td>
      <td>138.90</td>
      <td>-0.01</td>
      <td>693.69</td>
      <td>-0.02</td>
      <td>396.80</td>
      <td>-0.02</td>
      <td>...</td>
      <td>374.58</td>
      <td>-0.04</td>
      <td>31.46</td>
      <td>0.01</td>
      <td>103.52</td>
      <td>0.00</td>
      <td>61449.29</td>
      <td>-0.00</td>
      <td>1620.14</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>741.05</td>
      <td>0.02</td>
      <td>75.50</td>
      <td>0.03</td>
      <td>142.29</td>
      <td>0.02</td>
      <td>717.12</td>
      <td>0.03</td>
      <td>403.53</td>
      <td>0.02</td>
      <td>...</td>
      <td>386.32</td>
      <td>0.03</td>
      <td>30.96</td>
      <td>-0.02</td>
      <td>103.45</td>
      <td>-0.00</td>
      <td>63561.05</td>
      <td>0.03</td>
      <td>1672.28</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
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
      <td>63543.20</td>
      <td>-0.00</td>
      <td>1665.13</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>2026-06-13</th>
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
      <td>64421.32</td>
      <td>0.01</td>
      <td>1680.21</td>
      <td>0.01</td>
    </tr>
  </tbody>
</table>
<p>8194 rows × 40 columns</p>
</div>


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
        title=f"{tickers_dict[ticker]} Adjusted Close Price",
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
        grid=True,
        legend=False,
        export_plot=False,
        plot_file_name=None,
    )
```


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_4.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_5.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_6.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_7.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_8.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_9.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_10.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_11.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_12.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_13.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_14.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_15.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_16.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_17.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_18.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_12_19.png)
    


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

display(correlation_matrix_no_crypto)
```

    Shape of fund_data_daily_returns_no_crypto: (8194, 18)
    Rows to drop due to missing data: (5003, 18)



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
      <td>0.93</td>
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
      <td>-0.02</td>
      <td>0.06</td>
      <td>0.38</td>
      <td>0.76</td>
    </tr>
    <tr>
      <th>IJH_Daily_Return</th>
      <td>0.93</td>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.84</td>
      <td>0.94</td>
      <td>0.96</td>
      <td>0.94</td>
      <td>0.88</td>
      <td>0.85</td>
      <td>0.79</td>
      <td>0.83</td>
      <td>-0.21</td>
      <td>-0.29</td>
      <td>-0.30</td>
      <td>-0.01</td>
      <td>0.07</td>
      <td>0.38</td>
      <td>0.79</td>
    </tr>
    <tr>
      <th>IJR_Daily_Return</th>
      <td>0.88</td>
      <td>0.96</td>
      <td>1.00</td>
      <td>0.79</td>
      <td>0.89</td>
      <td>0.98</td>
      <td>0.90</td>
      <td>0.82</td>
      <td>0.80</td>
      <td>0.73</td>
      <td>0.78</td>
      <td>-0.20</td>
      <td>-0.28</td>
      <td>-0.29</td>
      <td>-0.03</td>
      <td>0.05</td>
      <td>0.36</td>
      <td>0.76</td>
    </tr>
    <tr>
      <th>QQQ_Daily_Return</th>
      <td>0.93</td>
      <td>0.84</td>
      <td>0.79</td>
      <td>1.00</td>
      <td>0.93</td>
      <td>0.82</td>
      <td>0.82</td>
      <td>0.97</td>
      <td>0.79</td>
      <td>0.76</td>
      <td>0.76</td>
      <td>-0.19</td>
      <td>-0.25</td>
      <td>-0.25</td>
      <td>0.00</td>
      <td>0.05</td>
      <td>0.30</td>
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
      <td>0.97</td>
      <td>0.88</td>
      <td>0.82</td>
      <td>0.86</td>
      <td>-0.23</td>
      <td>-0.30</td>
      <td>-0.31</td>
      <td>-0.01</td>
      <td>0.07</td>
      <td>0.38</td>
      <td>0.77</td>
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
      <td>-0.20</td>
      <td>-0.28</td>
      <td>-0.29</td>
      <td>-0.03</td>
      <td>0.06</td>
      <td>0.36</td>
      <td>0.77</td>
    </tr>
    <tr>
      <th>IWD_Daily_Return</th>
      <td>0.96</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.82</td>
      <td>0.96</td>
      <td>0.90</td>
      <td>1.00</td>
      <td>0.87</td>
      <td>0.88</td>
      <td>0.81</td>
      <td>0.87</td>
      <td>-0.24</td>
      <td>-0.31</td>
      <td>-0.33</td>
      <td>-0.02</td>
      <td>0.06</td>
      <td>0.40</td>
      <td>0.80</td>
    </tr>
    <tr>
      <th>IWF_Daily_Return</th>
      <td>0.96</td>
      <td>0.88</td>
      <td>0.82</td>
      <td>0.97</td>
      <td>0.97</td>
      <td>0.85</td>
      <td>0.87</td>
      <td>1.00</td>
      <td>0.83</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>-0.20</td>
      <td>-0.26</td>
      <td>-0.27</td>
      <td>0.02</td>
      <td>0.07</td>
      <td>0.34</td>
      <td>0.68</td>
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
      <td>0.83</td>
      <td>1.00</td>
      <td>0.88</td>
      <td>0.98</td>
      <td>-0.18</td>
      <td>-0.26</td>
      <td>-0.29</td>
      <td>0.04</td>
      <td>0.16</td>
      <td>0.41</td>
      <td>0.70</td>
    </tr>
    <tr>
      <th>EEM_Daily_Return</th>
      <td>0.82</td>
      <td>0.79</td>
      <td>0.73</td>
      <td>0.76</td>
      <td>0.82</td>
      <td>0.76</td>
      <td>0.81</td>
      <td>0.78</td>
      <td>0.88</td>
      <td>1.00</td>
      <td>0.84</td>
      <td>-0.21</td>
      <td>-0.27</td>
      <td>-0.27</td>
      <td>-0.01</td>
      <td>0.18</td>
      <td>0.41</td>
      <td>0.67</td>
    </tr>
    <tr>
      <th>IEV_Daily_Return</th>
      <td>0.86</td>
      <td>0.83</td>
      <td>0.78</td>
      <td>0.76</td>
      <td>0.86</td>
      <td>0.80</td>
      <td>0.87</td>
      <td>0.80</td>
      <td>0.98</td>
      <td>0.84</td>
      <td>1.00</td>
      <td>-0.18</td>
      <td>-0.27</td>
      <td>-0.29</td>
      <td>0.02</td>
      <td>0.16</td>
      <td>0.41</td>
      <td>0.69</td>
    </tr>
    <tr>
      <th>SHY_Daily_Return</th>
      <td>-0.23</td>
      <td>-0.21</td>
      <td>-0.20</td>
      <td>-0.19</td>
      <td>-0.23</td>
      <td>-0.20</td>
      <td>-0.24</td>
      <td>-0.20</td>
      <td>-0.18</td>
      <td>-0.21</td>
      <td>-0.18</td>
      <td>1.00</td>
      <td>0.76</td>
      <td>0.57</td>
      <td>0.60</td>
      <td>0.22</td>
      <td>-0.14</td>
      <td>-0.13</td>
    </tr>
    <tr>
      <th>IEF_Daily_Return</th>
      <td>-0.30</td>
      <td>-0.29</td>
      <td>-0.28</td>
      <td>-0.25</td>
      <td>-0.30</td>
      <td>-0.28</td>
      <td>-0.31</td>
      <td>-0.26</td>
      <td>-0.26</td>
      <td>-0.27</td>
      <td>-0.27</td>
      <td>0.76</td>
      <td>1.00</td>
      <td>0.91</td>
      <td>0.77</td>
      <td>0.22</td>
      <td>-0.21</td>
      <td>-0.14</td>
    </tr>
    <tr>
      <th>TLT_Daily_Return</th>
      <td>-0.31</td>
      <td>-0.30</td>
      <td>-0.29</td>
      <td>-0.25</td>
      <td>-0.31</td>
      <td>-0.29</td>
      <td>-0.33</td>
      <td>-0.27</td>
      <td>-0.29</td>
      <td>-0.27</td>
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
      <td>-0.02</td>
      <td>-0.01</td>
      <td>-0.03</td>
      <td>0.00</td>
      <td>-0.01</td>
      <td>-0.03</td>
      <td>-0.02</td>
      <td>0.02</td>
      <td>0.04</td>
      <td>-0.01</td>
      <td>0.02</td>
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
      <td>0.06</td>
      <td>0.07</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.07</td>
      <td>0.06</td>
      <td>0.06</td>
      <td>0.07</td>
      <td>0.16</td>
      <td>0.18</td>
      <td>0.16</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>0.16</td>
      <td>0.22</td>
      <td>1.00</td>
      <td>0.26</td>
      <td>0.07</td>
    </tr>
    <tr>
      <th>GSG_Daily_Return</th>
      <td>0.38</td>
      <td>0.38</td>
      <td>0.36</td>
      <td>0.30</td>
      <td>0.38</td>
      <td>0.36</td>
      <td>0.40</td>
      <td>0.34</td>
      <td>0.41</td>
      <td>0.41</td>
      <td>0.41</td>
      <td>-0.14</td>
      <td>-0.21</td>
      <td>-0.24</td>
      <td>-0.06</td>
      <td>0.26</td>
      <td>1.00</td>
      <td>0.26</td>
    </tr>
    <tr>
      <th>IYR_Daily_Return</th>
      <td>0.76</td>
      <td>0.79</td>
      <td>0.76</td>
      <td>0.64</td>
      <td>0.77</td>
      <td>0.77</td>
      <td>0.80</td>
      <td>0.68</td>
      <td>0.70</td>
      <td>0.67</td>
      <td>0.69</td>
      <td>-0.13</td>
      <td>-0.14</td>
      <td>-0.15</td>
      <td>0.03</td>
      <td>0.07</td>
      <td>0.26</td>
      <td>1.00</td>
    </tr>
  </tbody>
</table>
</div>


And then the heatmap:


```python
plot_heatmap(
    df=correlation_matrix_no_crypto,
    title="Correlation Matrix of Daily Returns (Excluding BTC and ETH)",
)
```


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_16_0.png)
    


We'll now include the BTC and ETH data and recalculate the correlation matrix and heatmap. Keep in mind that the BTC and ETH data only goes back to 2015 and 2018 respectively, so the correlation matrix will be calculated using a shorter time period than the other assets.


```python
# Print the shape of the fund_data_daily_returns DataFrame to confirm that the rows with missing data have been dropped
print(f"Shape of fund_data_daily_returns: {fund_data_daily_returns_all.shape}")
print(f"Rows to drop due to missing data: {fund_data_daily_returns_all.dropna().shape}")

# Drop the NaN values
fund_data_daily_returns = fund_data_daily_returns_all.dropna()

# Calculate the correlation matrix of the daily returns
correlation_matrix = fund_data_daily_returns.corr()

display(correlation_matrix)
```

    Shape of fund_data_daily_returns: (8194, 20)
    Rows to drop due to missing data: (2156, 20)



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
      <td>0.94</td>
      <td>1.00</td>
      <td>0.87</td>
      <td>0.93</td>
      <td>0.96</td>
      <td>0.85</td>
      <td>0.75</td>
      <td>0.82</td>
      <td>-0.05</td>
      <td>-0.12</td>
      <td>-0.15</td>
      <td>0.14</td>
      <td>0.11</td>
      <td>0.30</td>
      <td>0.74</td>
      <td>0.30</td>
      <td>0.33</td>
    </tr>
    <tr>
      <th>IJH_Daily_Return</th>
      <td>0.90</td>
      <td>1.00</td>
      <td>0.96</td>
      <td>0.78</td>
      <td>0.91</td>
      <td>0.96</td>
      <td>0.94</td>
      <td>0.81</td>
      <td>0.84</td>
      <td>0.72</td>
      <td>0.81</td>
      <td>-0.05</td>
      <td>-0.11</td>
      <td>-0.13</td>
      <td>0.15</td>
      <td>0.11</td>
      <td>0.31</td>
      <td>0.78</td>
      <td>0.29</td>
      <td>0.31</td>
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
      <td>0.74</td>
      <td>0.79</td>
      <td>0.67</td>
      <td>0.76</td>
      <td>-0.03</td>
      <td>-0.10</td>
      <td>-0.13</td>
      <td>0.15</td>
      <td>0.09</td>
      <td>0.30</td>
      <td>0.73</td>
      <td>0.28</td>
      <td>0.30</td>
    </tr>
    <tr>
      <th>QQQ_Daily_Return</th>
      <td>0.94</td>
      <td>0.78</td>
      <td>0.71</td>
      <td>1.00</td>
      <td>0.94</td>
      <td>0.77</td>
      <td>0.76</td>
      <td>0.98</td>
      <td>0.76</td>
      <td>0.73</td>
      <td>0.72</td>
      <td>-0.02</td>
      <td>-0.07</td>
      <td>-0.09</td>
      <td>0.14</td>
      <td>0.13</td>
      <td>0.24</td>
      <td>0.59</td>
      <td>0.31</td>
      <td>0.34</td>
    </tr>
    <tr>
      <th>IWB_Daily_Return</th>
      <td>1.00</td>
      <td>0.91</td>
      <td>0.85</td>
      <td>0.94</td>
      <td>1.00</td>
      <td>0.88</td>
      <td>0.93</td>
      <td>0.96</td>
      <td>0.85</td>
      <td>0.76</td>
      <td>0.82</td>
      <td>-0.04</td>
      <td>-0.11</td>
      <td>-0.14</td>
      <td>0.15</td>
      <td>0.12</td>
      <td>0.30</td>
      <td>0.74</td>
      <td>0.30</td>
      <td>0.33</td>
    </tr>
    <tr>
      <th>IWM_Daily_Return</th>
      <td>0.87</td>
      <td>0.96</td>
      <td>0.98</td>
      <td>0.77</td>
      <td>0.88</td>
      <td>1.00</td>
      <td>0.89</td>
      <td>0.79</td>
      <td>0.80</td>
      <td>0.71</td>
      <td>0.78</td>
      <td>-0.02</td>
      <td>-0.08</td>
      <td>-0.11</td>
      <td>0.17</td>
      <td>0.12</td>
      <td>0.30</td>
      <td>0.73</td>
      <td>0.31</td>
      <td>0.33</td>
    </tr>
    <tr>
      <th>IWD_Daily_Return</th>
      <td>0.93</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.76</td>
      <td>0.93</td>
      <td>0.89</td>
      <td>1.00</td>
      <td>0.80</td>
      <td>0.85</td>
      <td>0.71</td>
      <td>0.83</td>
      <td>-0.06</td>
      <td>-0.14</td>
      <td>-0.18</td>
      <td>0.12</td>
      <td>0.10</td>
      <td>0.34</td>
      <td>0.80</td>
      <td>0.26</td>
      <td>0.28</td>
    </tr>
    <tr>
      <th>IWF_Daily_Return</th>
      <td>0.96</td>
      <td>0.81</td>
      <td>0.74</td>
      <td>0.98</td>
      <td>0.96</td>
      <td>0.79</td>
      <td>0.80</td>
      <td>1.00</td>
      <td>0.78</td>
      <td>0.73</td>
      <td>0.75</td>
      <td>-0.03</td>
      <td>-0.07</td>
      <td>-0.09</td>
      <td>0.15</td>
      <td>0.11</td>
      <td>0.24</td>
      <td>0.64</td>
      <td>0.31</td>
      <td>0.34</td>
    </tr>
    <tr>
      <th>EFA_Daily_Return</th>
      <td>0.85</td>
      <td>0.84</td>
      <td>0.79</td>
      <td>0.76</td>
      <td>0.85</td>
      <td>0.80</td>
      <td>0.85</td>
      <td>0.78</td>
      <td>1.00</td>
      <td>0.83</td>
      <td>0.98</td>
      <td>0.02</td>
      <td>-0.04</td>
      <td>-0.09</td>
      <td>0.21</td>
      <td>0.24</td>
      <td>0.29</td>
      <td>0.69</td>
      <td>0.29</td>
      <td>0.32</td>
    </tr>
    <tr>
      <th>EEM_Daily_Return</th>
      <td>0.75</td>
      <td>0.72</td>
      <td>0.67</td>
      <td>0.73</td>
      <td>0.76</td>
      <td>0.71</td>
      <td>0.71</td>
      <td>0.73</td>
      <td>0.83</td>
      <td>1.00</td>
      <td>0.80</td>
      <td>0.01</td>
      <td>-0.06</td>
      <td>-0.09</td>
      <td>0.16</td>
      <td>0.26</td>
      <td>0.28</td>
      <td>0.54</td>
      <td>0.26</td>
      <td>0.31</td>
    </tr>
    <tr>
      <th>IEV_Daily_Return</th>
      <td>0.82</td>
      <td>0.81</td>
      <td>0.76</td>
      <td>0.72</td>
      <td>0.82</td>
      <td>0.78</td>
      <td>0.83</td>
      <td>0.75</td>
      <td>0.98</td>
      <td>0.80</td>
      <td>1.00</td>
      <td>0.02</td>
      <td>-0.05</td>
      <td>-0.09</td>
      <td>0.21</td>
      <td>0.23</td>
      <td>0.28</td>
      <td>0.68</td>
      <td>0.29</td>
      <td>0.31</td>
    </tr>
    <tr>
      <th>SHY_Daily_Return</th>
      <td>-0.05</td>
      <td>-0.05</td>
      <td>-0.03</td>
      <td>-0.02</td>
      <td>-0.04</td>
      <td>-0.02</td>
      <td>-0.06</td>
      <td>-0.03</td>
      <td>0.02</td>
      <td>0.01</td>
      <td>0.02</td>
      <td>1.00</td>
      <td>0.82</td>
      <td>0.60</td>
      <td>0.74</td>
      <td>0.32</td>
      <td>-0.12</td>
      <td>0.13</td>
      <td>0.03</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>IEF_Daily_Return</th>
      <td>-0.12</td>
      <td>-0.11</td>
      <td>-0.10</td>
      <td>-0.07</td>
      <td>-0.11</td>
      <td>-0.08</td>
      <td>-0.14</td>
      <td>-0.07</td>
      <td>-0.04</td>
      <td>-0.06</td>
      <td>-0.05</td>
      <td>0.82</td>
      <td>1.00</td>
      <td>0.91</td>
      <td>0.89</td>
      <td>0.31</td>
      <td>-0.15</td>
      <td>0.09</td>
      <td>-0.00</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>TLT_Daily_Return</th>
      <td>-0.15</td>
      <td>-0.13</td>
      <td>-0.13</td>
      <td>-0.09</td>
      <td>-0.14</td>
      <td>-0.11</td>
      <td>-0.18</td>
      <td>-0.09</td>
      <td>-0.09</td>
      <td>-0.09</td>
      <td>-0.09</td>
      <td>0.60</td>
      <td>0.91</td>
      <td>1.00</td>
      <td>0.84</td>
      <td>0.23</td>
      <td>-0.17</td>
      <td>0.04</td>
      <td>-0.01</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <th>AGG_Daily_Return</th>
      <td>0.14</td>
      <td>0.15</td>
      <td>0.15</td>
      <td>0.14</td>
      <td>0.15</td>
      <td>0.17</td>
      <td>0.12</td>
      <td>0.15</td>
      <td>0.21</td>
      <td>0.16</td>
      <td>0.21</td>
      <td>0.74</td>
      <td>0.89</td>
      <td>0.84</td>
      <td>1.00</td>
      <td>0.31</td>
      <td>-0.03</td>
      <td>0.29</td>
      <td>0.12</td>
      <td>0.11</td>
    </tr>
    <tr>
      <th>GLD_Daily_Return</th>
      <td>0.11</td>
      <td>0.11</td>
      <td>0.09</td>
      <td>0.13</td>
      <td>0.12</td>
      <td>0.12</td>
      <td>0.10</td>
      <td>0.11</td>
      <td>0.24</td>
      <td>0.26</td>
      <td>0.23</td>
      <td>0.32</td>
      <td>0.31</td>
      <td>0.23</td>
      <td>0.31</td>
      <td>1.00</td>
      <td>0.19</td>
      <td>0.14</td>
      <td>0.11</td>
      <td>0.11</td>
    </tr>
    <tr>
      <th>GSG_Daily_Return</th>
      <td>0.30</td>
      <td>0.31</td>
      <td>0.30</td>
      <td>0.24</td>
      <td>0.30</td>
      <td>0.30</td>
      <td>0.34</td>
      <td>0.24</td>
      <td>0.29</td>
      <td>0.28</td>
      <td>0.28</td>
      <td>-0.12</td>
      <td>-0.15</td>
      <td>-0.17</td>
      <td>-0.03</td>
      <td>0.19</td>
      <td>1.00</td>
      <td>0.21</td>
      <td>0.09</td>
      <td>0.11</td>
    </tr>
    <tr>
      <th>IYR_Daily_Return</th>
      <td>0.74</td>
      <td>0.78</td>
      <td>0.73</td>
      <td>0.59</td>
      <td>0.74</td>
      <td>0.73</td>
      <td>0.80</td>
      <td>0.64</td>
      <td>0.69</td>
      <td>0.54</td>
      <td>0.68</td>
      <td>0.13</td>
      <td>0.09</td>
      <td>0.04</td>
      <td>0.29</td>
      <td>0.14</td>
      <td>0.21</td>
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
      <td>0.11</td>
      <td>0.09</td>
      <td>0.19</td>
      <td>1.00</td>
      <td>0.80</td>
    </tr>
    <tr>
      <th>ETH-USD_Daily_Return</th>
      <td>0.33</td>
      <td>0.31</td>
      <td>0.30</td>
      <td>0.34</td>
      <td>0.33</td>
      <td>0.33</td>
      <td>0.28</td>
      <td>0.34</td>
      <td>0.32</td>
      <td>0.31</td>
      <td>0.31</td>
      <td>0.03</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>0.11</td>
      <td>0.11</td>
      <td>0.11</td>
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
    title="Correlation Matrix of Daily Returns (Including BTC and ETH)",
)
```


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_20_0.png)
    


These are interesting results, but expected. The stock funds tend to have low correlations with the bond funds, the commodities don't really correlate with anything, etc. But we know that the correlations between these asset classes have changed over time, so let's take a look at how the correlations have evolved over time by calculating rolling correlations.

 ## Calculate Rolling Correlations

 Next, we will calculate the rolling correlations for several different periods:
 * 1 month
 * 3 month
 * 6 month
 * 1 year
 * 5 years
 * 10 years


```python
# Define rolling windows in trading days
rolling_windows = {
    '3d': 3,      # 3 days (~3 trading days)
    '1w': 5,      # 1 week (~5 trading days)
    '2w': 10,     # 2 weeks (~10 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
    '10y': 2520,  # 10 years (~2520 trading days)
}
```

Before we run all of these, let's take a quick look at each of the rolling windows.


```python
temp_df = fund_data_daily_returns_all[["IVV_Daily_Return", "IJH_Daily_Return"]].dropna()

for window_name, window_size in rolling_windows.items():
    rolling_corr = temp_df["IVV_Daily_Return"].rolling(window=window_size).corr(temp_df["IJH_Daily_Return"])

    print(tickers_dict["IVV"])
    print(tickers_dict["IJH"])

    plot_time_series(
        df=rolling_corr.to_frame(name="IVV_IJH_Rolling_Correlation"),
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=["IVV_IJH_Rolling_Correlation"],
        title=f"IVV vs IJH Rolling Correlation ({window_name} window)",
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
        legend=False,
        export_plot=False,
        plot_file_name=None,
    )
```

    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_25_1.png)
    


    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_25_3.png)
    


    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_25_5.png)
    


    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_25_7.png)
    


    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_25_9.png)
    


    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_25_11.png)
    


    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_25_13.png)
    


    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_25_15.png)
    


    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_25_17.png)
    


Need to update 

<!-- Some inital thoughts here:
* The 1 month and 3 month rolling windows are very noisy... it's going to be difficult to capture any kinds of meaningful trends with these short rolling windows - and these short-term movements are not the point of our investigation here.
* The 6 months and 1 year rolling windows look like they might be a bit better, but still pretty noisy. We'll keep both of those.
* The 5 year also looks potentially useful, but the 10 year is too long - it doesn't capture any of the medium-term movements that we are interested in. We'll keep the 5 year and drop the 10 year.

So that leaves us with:
* 6 months
* 1 year
* 5 years

We are essentially looking to capture market movements over the months-to-years time frame (from a macro perspective), so the 6 month, 1 year, and 5 year rolling windows are the most appropriate for this analysis. -->


```python
# Define rolling windows in trading days
rolling_windows = {
    '3d': 3,      # 3 days (~3 trading days)
    '1w': 5,      # 1 week (~5 trading days)
    '2w': 10,     # 2 weeks (~10 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
}
```


```python
from itertools import combinations

# Create temp list for tickers
temp_tickers = list(tickers_dict.keys())
pairs = list(combinations(temp_tickers, 2))

# Create empty dictionary to store rolling correlation results
rolling_correlation_results_no_crypto_dict = {}
rolling_correlation_results_no_crypto_df = pd.DataFrame()

for ticker1, ticker2 in pairs:
    try:
        temp_df = fund_data_daily_returns_no_crypto[[f"{ticker1}_Daily_Return", f"{ticker2}_Daily_Return"]].dropna()
    except Exception as e:
        print(f"Error creating temp_df for {ticker1} and {ticker2}: {e}")
        continue
        
    for window_name, window_size in rolling_windows.items():
        try:
            rolling_corr = temp_df[f"{ticker1}_Daily_Return"].rolling(window=window_size).corr(temp_df[f"{ticker2}_Daily_Return"])

            print(tickers_dict[f"{ticker1}"])
            print(tickers_dict[f"{ticker2}"])

            rolling_correlation_results_no_crypto_dict[f"{ticker1}_{ticker2}_{window_name}"] = rolling_corr
            rolling_correlation_results_no_crypto_df = pd.concat([rolling_correlation_results_no_crypto_df, rolling_corr.to_frame(name=f"{ticker1}_{ticker2}_{window_name}")], axis=1)

        except Exception as e:
            print(f"Error calculating rolling correlation for {ticker1} and {ticker2} with window {window_name}: {e}")
```

    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large Cap US Stocks / S&P 500 -- IVV (iShares S&P 500 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for IVV and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IVV and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)


    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Mid Cap US Stocks / S&P MidCap 400 -- IJH (iShares S&P MidCap 400 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for IJH and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IJH and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)


    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Small Cap US Stocks / S&P SmallCap 600 -- IJR (iShares S&P SmallCap 600 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for IJR and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IJR and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)


    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Gold -- GLD (SPDR Gold Shares)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Gold -- GLD (SPDR Gold Shares)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Gold -- GLD (SPDR Gold Shares)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Gold -- GLD (SPDR Gold Shares)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Gold -- GLD (SPDR Gold Shares)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)


    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    US Tech Stocks / Nasdaq 100 -- QQQ (Invesco QQQ Trust, Series 1)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for QQQ and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for QQQ and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)


    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)


    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Stocks -- IWB (iShares Russell 1000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for IWB and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IWB and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Gold -- GLD (SPDR Gold Shares)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)


    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Small Cap US Stocks -- IWM (iShares Russell 2000 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for IWM and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IWM and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Gold -- GLD (SPDR Gold Shares)


    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Value Stocks -- IWD (iShares Russell 1000 Value ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for IWD and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IWD and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)


    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Gold -- GLD (SPDR Gold Shares)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Large & Mid Cap US Growth Stocks -- IWF (iShares Russell 1000 Growth ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for IWF and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IWF and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)


    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)


    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Gold -- GLD (SPDR Gold Shares)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Gold -- GLD (SPDR Gold Shares)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Gold -- GLD (SPDR Gold Shares)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Gold -- GLD (SPDR Gold Shares)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Gold -- GLD (SPDR Gold Shares)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    International Developed Market Stocks -- EFA (iShares MSCI EAFE ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for EFA and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for EFA and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)


    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Gold -- GLD (SPDR Gold Shares)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Gold -- GLD (SPDR Gold Shares)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Gold -- GLD (SPDR Gold Shares)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Gold -- GLD (SPDR Gold Shares)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Gold -- GLD (SPDR Gold Shares)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Emerging Market Stocks -- EEM (iShares MSCI Emerging Markets ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for EEM and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for EEM and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)


    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Gold -- GLD (SPDR Gold Shares)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Gold -- GLD (SPDR Gold Shares)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Gold -- GLD (SPDR Gold Shares)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Gold -- GLD (SPDR Gold Shares)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Gold -- GLD (SPDR Gold Shares)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    European Stocks -- IEV (iShares S&P Europe 350 ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for IEV and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IEV and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)


    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Short-Term US Treasuries -- SHY (iShares 1-3 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for SHY and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for SHY and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)


    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Medium-Term US Treasuries -- IEF (iShares 7-10 Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for IEF and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IEF and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)


    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Long-Term US Treasuries -- TLT (iShares 20+ Year Treasury Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for TLT and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for TLT and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Gold -- GLD (SPDR Gold Shares)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Aggregate Bonds -- AGG (iShares Core U.S. Aggregate Bond ETF)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for AGG and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for AGG and ETH-USD: "['ETH-USD_Daily_Return'] not in index"


    Gold -- GLD (SPDR Gold Shares)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Gold -- GLD (SPDR Gold Shares)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Gold -- GLD (SPDR Gold Shares)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Gold -- GLD (SPDR Gold Shares)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Gold -- GLD (SPDR Gold Shares)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Gold -- GLD (SPDR Gold Shares)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Gold -- GLD (SPDR Gold Shares)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Gold -- GLD (SPDR Gold Shares)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Gold -- GLD (SPDR Gold Shares)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Gold -- GLD (SPDR Gold Shares)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for GLD and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for GLD and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Commodities -- GSG (iShares S&P GSCI Commodity-Indexed Trust)
    Real Estate -- IYR (iShares U.S. Real Estate ETF)
    Error creating temp_df for GSG and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for GSG and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Error creating temp_df for IYR and BTC-USD: "['BTC-USD_Daily_Return'] not in index"
    Error creating temp_df for IYR and ETH-USD: "['ETH-USD_Daily_Return'] not in index"
    Error creating temp_df for BTC-USD and ETH-USD: "None of [Index(['BTC-USD_Daily_Return', 'ETH-USD_Daily_Return'], dtype='str')] are in the [columns]"



```python
display(rolling_correlation_results_no_crypto_df)
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
      <th>IVV_IJR_3d</th>
      <th>IVV_IJR_1w</th>
      <th>IVV_IJR_2w</th>
      <th>IVV_IJR_1m</th>
      <th>IVV_IJR_3m</th>
      <th>...</th>
      <th>GLD_IYR_3d</th>
      <th>GLD_IYR_1w</th>
      <th>GLD_IYR_2w</th>
      <th>GLD_IYR_1m</th>
      <th>GLD_IYR_3m</th>
      <th>GSG_IYR_3d</th>
      <th>GSG_IYR_1w</th>
      <th>GSG_IYR_2w</th>
      <th>GSG_IYR_1m</th>
      <th>GSG_IYR_3m</th>
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
      <td>0.96</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>-0.99</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.40</td>
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
      <td>0.93</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>-0.99</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.75</td>
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
      <td>0.99</td>
      <td>0.97</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>-0.99</td>
      <td>-0.89</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.91</td>
      <td>-0.41</td>
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
      <th>2026-06-05</th>
      <td>0.98</td>
      <td>0.92</td>
      <td>0.86</td>
      <td>0.81</td>
      <td>0.87</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.79</td>
      <td>0.77</td>
      <td>0.85</td>
      <td>...</td>
      <td>0.50</td>
      <td>0.28</td>
      <td>0.03</td>
      <td>0.28</td>
      <td>0.41</td>
      <td>-0.60</td>
      <td>-0.82</td>
      <td>-0.59</td>
      <td>-0.39</td>
      <td>-0.43</td>
    </tr>
    <tr>
      <th>2026-06-08</th>
      <td>1.00</td>
      <td>0.95</td>
      <td>0.85</td>
      <td>0.83</td>
      <td>0.87</td>
      <td>0.99</td>
      <td>0.95</td>
      <td>0.79</td>
      <td>0.77</td>
      <td>0.85</td>
      <td>...</td>
      <td>-0.08</td>
      <td>-0.06</td>
      <td>-0.04</td>
      <td>0.24</td>
      <td>0.39</td>
      <td>-0.79</td>
      <td>-0.64</td>
      <td>-0.62</td>
      <td>-0.39</td>
      <td>-0.43</td>
    </tr>
    <tr>
      <th>2026-06-09</th>
      <td>0.93</td>
      <td>0.92</td>
      <td>0.81</td>
      <td>0.80</td>
      <td>0.86</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>0.73</td>
      <td>0.73</td>
      <td>0.84</td>
      <td>...</td>
      <td>-0.55</td>
      <td>-0.17</td>
      <td>-0.20</td>
      <td>0.09</td>
      <td>0.35</td>
      <td>-0.74</td>
      <td>-0.71</td>
      <td>-0.63</td>
      <td>-0.43</td>
      <td>-0.44</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>0.86</td>
      <td>0.93</td>
      <td>0.87</td>
      <td>0.83</td>
      <td>0.86</td>
      <td>0.91</td>
      <td>0.98</td>
      <td>0.74</td>
      <td>0.75</td>
      <td>0.84</td>
      <td>...</td>
      <td>-0.30</td>
      <td>0.02</td>
      <td>-0.17</td>
      <td>0.07</td>
      <td>0.34</td>
      <td>-0.89</td>
      <td>-0.71</td>
      <td>-0.71</td>
      <td>-0.48</td>
      <td>-0.43</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>0.98</td>
      <td>0.97</td>
      <td>0.92</td>
      <td>0.86</td>
      <td>0.86</td>
      <td>0.99</td>
      <td>0.99</td>
      <td>0.84</td>
      <td>0.81</td>
      <td>0.84</td>
      <td>...</td>
      <td>-0.21</td>
      <td>-0.32</td>
      <td>-0.13</td>
      <td>0.05</td>
      <td>0.32</td>
      <td>-0.48</td>
      <td>-0.61</td>
      <td>-0.65</td>
      <td>-0.50</td>
      <td>-0.41</td>
    </tr>
  </tbody>
</table>
<p>5003 rows × 765 columns</p>
</div>



```python
for window in rolling_windows.keys():
    plot_time_series(
        df=rolling_correlation_results_no_crypto_df,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[col for col in rolling_correlation_results_no_crypto_df.columns if f"{window}" in col],
        title=f"Rolling {window} Correlation, No Crypto",
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
        legend=False,
        export_plot=False,
        plot_file_name=None,
    )
```


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_30_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_30_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_30_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_30_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_30_4.png)
    


## Rolling Correlations Amongst US Stocks

We'll now look specifically at the rolling correlations between the US S&P index ETFs (IVV, IJH, and IJR). We'll isolate the data for the rolling correlations for these three assets and see how the correlations have changed over time.


```python
corr_list = [f'IVV_IJH_{window}', f'IVV_IJR_{window}', f'IJH_IJR_{window}']

for window in rolling_windows.keys():
    plot_time_series(
        df=rolling_correlation_results_no_crypto_df,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=corr_list,
        title=f"Rolling {window} Correlation - US Equity ETFs (S&P 500, 400, 600)",
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
    )
```


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_32_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_32_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_32_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_32_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_32_4.png)
    


With the above plot, we can see that there are periods of time when the correlations abruptly increase, such as:

* Early-mid 2007 (the start of the financial crisis)
* Mid 2011 (the European debt crisis)
* Late 2015 into 2016
* Late 2018 (rate hikes?)
* Early 2020 (COVID-19 pandemic)
* Late 2022 into early 2023 (rate hikes, recession fears, COVID tech bubble, etc.)
* Mid 2024 (banking crisis, rate hikes)
* Early 2025 (Liberation day)

We're not necessarily looking to explain away each of these time periods or delve into the macro factors that may have been at play or driving the correlations, but we are more interested in the change in correlation over time on response to some kind of market shock or event.

As an attempt to find some kind of signal, let's simply add the three correlations together to get a "total correlation" metric, and then plot that total correlation metric over time to see if we can identify any trends or patterns.


```python
# Define rolling windows in trading days
return_windows = {
    '1d': 1,      # 1 day (~1 trading day)
    '3d': 3,      # 3 days (~3 trading days)
    '1w': 5,      # 1 week (~5 trading days)
    '2w': 10,     # 2 weeks (~10 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '2m': 42,     # 2 months (~42 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    # '4m': 84,     # 4 months (~84 trading days)
    # '6m': 126,    # 6 months (~126 trading days)
    # '8m': 168,    # 8 months (~168 trading days)
    # '10m': 210,   # 10 months (~210 trading days)
    # '1y': 252,    # 1 year (~252 trading days)
    # '1y2m': 294,  # 1 year + 2 months (~294 trading days)
    # '1y4m': 336,  # 1 year + 4 months (~336 trading days)
    # '1y6m': 378,  # 1 year + 6 months (~378 trading days)
    # '1y8m': 420,  # 1 year + 8 months (~420 trading days)
    # '1y10m': 462, # 1 year + 10 months (~462 trading days)
    # '2y': 504,    # 2 years (~504 trading days)
}
```


```python
corr_list = [f'IVV_IJH_{window}', f'IVV_IJR_{window}', f'IJH_IJR_{window}']
fund_tickers = ["IVV", "IJH", "IJR"]

for window in rolling_windows.keys():
    us_sp_etfs = rolling_correlation_results_no_crypto_df[corr_list].dropna()

    # Add the correlations together
    us_sp_etfs["total_correlation"] = us_sp_etfs.sum(axis=1)

    # Merge daily returns into us_sp_etfs for the three ETFs
    us_sp_etfs = us_sp_etfs.merge(
        fund_data_daily_returns_all[[f"{ft}_Daily_Return" for ft in fund_tickers]].dropna(),
        left_index=True,
        right_index=True,
        how="left"
    )

    plot_time_series(
        df=us_sp_etfs.dropna(),
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=["total_correlation"],
        title=f"Rolling {window} Total Correlation - US Equity ETFs (S&P 500, 400, 600)",
        x_label="Date",
        x_format="Year",
        x_tick_spacing=1,
        x_tick_start=None,
        x_tick_rotation=30,
        y_label=f"Rolling {window} Total Correlation",
        y_format="Decimal",
        y_format_decimal_places="Auto",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    for rw in return_windows.keys():
        for ft in fund_tickers:
            us_sp_etfs[f"{ft}_Daily_Return_{rw}_CRR"] = us_sp_etfs[f"{ft}_Daily_Return"].rolling(window=return_windows[rw]).apply(lambda x: (1 + x).prod() - 1)
            us_sp_etfs[f"{ft}_Daily_Return_fwd_{rw}_CRR"] = us_sp_etfs[f"{ft}_Daily_Return_{rw}_CRR"].shift(-return_windows[rw])

        plot_scatter(
            df=us_sp_etfs,
            x_plot_column="total_correlation",
            y_plot_columns=[col for col in us_sp_etfs.columns if f"fwd_{rw}_CRR" in col],
            title=f"Rolling {window} Total Correlation vs Future {rw} Cumulative Rolling Return - US Equity ETFs (S&P 500, 400, 600)",
            x_label=f"Rolling {window} Total Correlation",
            x_format="Decimal",
            x_format_decimal_places=2,
            x_tick_spacing="Auto",
            x_tick_start=None,
            x_tick_rotation=30,
            y_label=f"Future {rw} Cumulative Rolling Return",
            y_format="Decimal",
            y_format_decimal_places=2,
            y_tick_spacing="Auto",
            y_tick_rotation=0,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        plot_histogram(
            df=us_sp_etfs,
            plot_columns=[col for col in us_sp_etfs.columns if f"fwd_{rw}_CRR" in col],
            title=f"Rolling {window} Total Correlation, Distribution of Future {rw} Cumulative Rolling Returns - US Equity ETFs (S&P 500, 400, 600)",
            x_label=f"Rolling {window} Total Correlation",
            x_tick_spacing="Auto",
            x_tick_rotation=30,
            y_label="Frequency",
            y_tick_spacing="Auto",
            y_tick_rotation=0,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )
```


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_4.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_5.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_6.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_7.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_8.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_9.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_10.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_11.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_12.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_13.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_14.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_15.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_16.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_17.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_18.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_19.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_20.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_21.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_22.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_23.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_24.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_25.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_26.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_27.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_28.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_29.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_30.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_31.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_32.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_33.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_34.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_35.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_36.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_37.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_38.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_39.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_40.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_41.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_42.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_43.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_44.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_45.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_46.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_47.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_48.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_49.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_50.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_51.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_52.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_53.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_54.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_55.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_56.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_57.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_58.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_59.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_60.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_61.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_62.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_63.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_64.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_65.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_66.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_67.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_68.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_69.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_70.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_71.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_72.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_73.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_35_74.png)
    


Now we'll look at a few different moving averages of the total correlation metric, the difference between the total correlation and the moving averages, and the percentage difference.


```python
us_sp_etfs
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
      <th>IVV_IJH_3m</th>
      <th>IVV_IJR_3m</th>
      <th>IJH_IJR_3m</th>
      <th>total_correlation</th>
      <th>IVV_Daily_Return</th>
      <th>IJH_Daily_Return</th>
      <th>IJR_Daily_Return</th>
      <th>IVV_Daily_Return_1d_CRR</th>
      <th>IVV_Daily_Return_fwd_1d_CRR</th>
      <th>IJH_Daily_Return_1d_CRR</th>
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
      <th>2006-10-19</th>
      <td>0.92</td>
      <td>0.90</td>
      <td>0.96</td>
      <td>2.78</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>0.05</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>2006-10-20</th>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.96</td>
      <td>2.75</td>
      <td>0.00</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>-0.01</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>0.05</td>
    </tr>
    <tr>
      <th>2006-10-23</th>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.96</td>
      <td>2.74</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.05</td>
      <td>NaN</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>2006-10-24</th>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.96</td>
      <td>2.75</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.02</td>
      <td>NaN</td>
      <td>0.02</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>2006-10-25</th>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.96</td>
      <td>2.75</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>...</td>
      <td>NaN</td>
      <td>0.02</td>
      <td>NaN</td>
      <td>0.02</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>NaN</td>
      <td>0.04</td>
      <td>NaN</td>
      <td>0.03</td>
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
      <th>2026-06-05</th>
      <td>0.87</td>
      <td>0.85</td>
      <td>0.95</td>
      <td>2.67</td>
      <td>-0.03</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>-0.03</td>
      <td>0.00</td>
      <td>-0.02</td>
      <td>...</td>
      <td>0.08</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.10</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.11</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2026-06-08</th>
      <td>0.87</td>
      <td>0.85</td>
      <td>0.95</td>
      <td>2.67</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>0.00</td>
      <td>...</td>
      <td>0.05</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.08</td>
      <td>NaN</td>
      <td>0.11</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2026-06-09</th>
      <td>0.86</td>
      <td>0.84</td>
      <td>0.95</td>
      <td>2.65</td>
      <td>-0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>-0.00</td>
      <td>-0.02</td>
      <td>0.01</td>
      <td>...</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.09</td>
      <td>NaN</td>
      <td>0.12</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>0.86</td>
      <td>0.84</td>
      <td>0.95</td>
      <td>2.65</td>
      <td>-0.02</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>0.02</td>
      <td>-0.01</td>
      <td>...</td>
      <td>0.05</td>
      <td>NaN</td>
      <td>0.07</td>
      <td>NaN</td>
      <td>0.08</td>
      <td>NaN</td>
      <td>0.08</td>
      <td>NaN</td>
      <td>0.12</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>0.86</td>
      <td>0.84</td>
      <td>0.95</td>
      <td>2.65</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>...</td>
      <td>0.06</td>
      <td>NaN</td>
      <td>0.08</td>
      <td>NaN</td>
      <td>0.11</td>
      <td>NaN</td>
      <td>0.13</td>
      <td>NaN</td>
      <td>0.17</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>4941 rows × 49 columns</p>
</div>




```python
ma_windows = [5, 10, 15, 20, 25]

for window in ma_windows:
    us_sp_etfs[f"total_correlation_{window}d_ma"] = us_sp_etfs["total_correlation"].rolling(window=window).mean()
    us_sp_etfs[f"total_correlation_diff_{window}d"] = us_sp_etfs["total_correlation"] - us_sp_etfs[f"total_correlation_{window}d_ma"]

display(us_sp_etfs)
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
      <th>IVV_IJH_3m</th>
      <th>IVV_IJR_3m</th>
      <th>IJH_IJR_3m</th>
      <th>total_correlation</th>
      <th>IVV_Daily_Return</th>
      <th>IJH_Daily_Return</th>
      <th>IJR_Daily_Return</th>
      <th>IVV_Daily_Return_1d_CRR</th>
      <th>IVV_Daily_Return_fwd_1d_CRR</th>
      <th>IJH_Daily_Return_1d_CRR</th>
      <th>...</th>
      <th>total_correlation_5d_ma</th>
      <th>total_correlation_diff_5d</th>
      <th>total_correlation_10d_ma</th>
      <th>total_correlation_diff_10d</th>
      <th>total_correlation_15d_ma</th>
      <th>total_correlation_diff_15d</th>
      <th>total_correlation_20d_ma</th>
      <th>total_correlation_diff_20d</th>
      <th>total_correlation_25d_ma</th>
      <th>total_correlation_diff_25d</th>
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
      <th>2006-10-19</th>
      <td>0.92</td>
      <td>0.90</td>
      <td>0.96</td>
      <td>2.78</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
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
      <th>2006-10-20</th>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.96</td>
      <td>2.75</td>
      <td>0.00</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>-0.01</td>
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
      <th>2006-10-23</th>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.96</td>
      <td>2.74</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
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
      <th>2006-10-24</th>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.96</td>
      <td>2.75</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
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
      <th>2006-10-25</th>
      <td>0.90</td>
      <td>0.89</td>
      <td>0.96</td>
      <td>2.75</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>...</td>
      <td>2.75</td>
      <td>-0.00</td>
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
      <th>2026-06-05</th>
      <td>0.87</td>
      <td>0.85</td>
      <td>0.95</td>
      <td>2.67</td>
      <td>-0.03</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>-0.03</td>
      <td>0.00</td>
      <td>-0.02</td>
      <td>...</td>
      <td>2.68</td>
      <td>-0.01</td>
      <td>2.68</td>
      <td>-0.01</td>
      <td>2.69</td>
      <td>-0.02</td>
      <td>2.68</td>
      <td>-0.01</td>
      <td>2.69</td>
      <td>-0.02</td>
    </tr>
    <tr>
      <th>2026-06-08</th>
      <td>0.87</td>
      <td>0.85</td>
      <td>0.95</td>
      <td>2.67</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>0.00</td>
      <td>...</td>
      <td>2.68</td>
      <td>-0.01</td>
      <td>2.68</td>
      <td>-0.01</td>
      <td>2.68</td>
      <td>-0.01</td>
      <td>2.68</td>
      <td>-0.01</td>
      <td>2.69</td>
      <td>-0.02</td>
    </tr>
    <tr>
      <th>2026-06-09</th>
      <td>0.86</td>
      <td>0.84</td>
      <td>0.95</td>
      <td>2.65</td>
      <td>-0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>-0.00</td>
      <td>-0.02</td>
      <td>0.01</td>
      <td>...</td>
      <td>2.67</td>
      <td>-0.02</td>
      <td>2.68</td>
      <td>-0.03</td>
      <td>2.68</td>
      <td>-0.03</td>
      <td>2.68</td>
      <td>-0.03</td>
      <td>2.69</td>
      <td>-0.03</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>0.86</td>
      <td>0.84</td>
      <td>0.95</td>
      <td>2.65</td>
      <td>-0.02</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>0.02</td>
      <td>-0.01</td>
      <td>...</td>
      <td>2.66</td>
      <td>-0.01</td>
      <td>2.68</td>
      <td>-0.02</td>
      <td>2.68</td>
      <td>-0.03</td>
      <td>2.68</td>
      <td>-0.03</td>
      <td>2.68</td>
      <td>-0.03</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>0.86</td>
      <td>0.84</td>
      <td>0.95</td>
      <td>2.65</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>NaN</td>
      <td>0.03</td>
      <td>...</td>
      <td>2.66</td>
      <td>-0.01</td>
      <td>2.67</td>
      <td>-0.02</td>
      <td>2.68</td>
      <td>-0.03</td>
      <td>2.68</td>
      <td>-0.03</td>
      <td>2.68</td>
      <td>-0.03</td>
    </tr>
  </tbody>
</table>
<p>4941 rows × 59 columns</p>
</div>



```python
us_sp_etfs[(us_sp_etfs.index >= "2020-01-01") & (us_sp_etfs.index <= "2021-01-01")]
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
      <th>IVV_IJH_3m</th>
      <th>IVV_IJR_3m</th>
      <th>IJH_IJR_3m</th>
      <th>total_correlation</th>
      <th>IVV_Daily_Return</th>
      <th>IJH_Daily_Return</th>
      <th>IJR_Daily_Return</th>
      <th>IVV_Daily_Return_1d_CRR</th>
      <th>IVV_Daily_Return_fwd_1d_CRR</th>
      <th>IJH_Daily_Return_1d_CRR</th>
      <th>...</th>
      <th>total_correlation_5d_ma</th>
      <th>total_correlation_diff_5d</th>
      <th>total_correlation_10d_ma</th>
      <th>total_correlation_diff_10d</th>
      <th>total_correlation_15d_ma</th>
      <th>total_correlation_diff_15d</th>
      <th>total_correlation_20d_ma</th>
      <th>total_correlation_diff_20d</th>
      <th>total_correlation_25d_ma</th>
      <th>total_correlation_diff_25d</th>
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
      <th>2020-01-02</th>
      <td>0.86</td>
      <td>0.73</td>
      <td>0.90</td>
      <td>2.49</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>-0.01</td>
      <td>0.00</td>
      <td>...</td>
      <td>2.55</td>
      <td>-0.06</td>
      <td>2.58</td>
      <td>-0.09</td>
      <td>2.59</td>
      <td>-0.10</td>
      <td>2.59</td>
      <td>-0.10</td>
      <td>2.58</td>
      <td>-0.10</td>
    </tr>
    <tr>
      <th>2020-01-03</th>
      <td>0.86</td>
      <td>0.73</td>
      <td>0.90</td>
      <td>2.49</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>0.00</td>
      <td>-0.01</td>
      <td>...</td>
      <td>2.53</td>
      <td>-0.04</td>
      <td>2.56</td>
      <td>-0.08</td>
      <td>2.58</td>
      <td>-0.10</td>
      <td>2.58</td>
      <td>-0.10</td>
      <td>2.58</td>
      <td>-0.09</td>
    </tr>
    <tr>
      <th>2020-01-06</th>
      <td>0.85</td>
      <td>0.72</td>
      <td>0.89</td>
      <td>2.47</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>...</td>
      <td>2.51</td>
      <td>-0.04</td>
      <td>2.55</td>
      <td>-0.08</td>
      <td>2.57</td>
      <td>-0.10</td>
      <td>2.58</td>
      <td>-0.11</td>
      <td>2.58</td>
      <td>-0.10</td>
    </tr>
    <tr>
      <th>2020-01-07</th>
      <td>0.85</td>
      <td>0.73</td>
      <td>0.90</td>
      <td>2.48</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>-0.00</td>
      <td>0.01</td>
      <td>-0.00</td>
      <td>...</td>
      <td>2.49</td>
      <td>-0.01</td>
      <td>2.54</td>
      <td>-0.06</td>
      <td>2.56</td>
      <td>-0.08</td>
      <td>2.58</td>
      <td>-0.10</td>
      <td>2.57</td>
      <td>-0.09</td>
    </tr>
    <tr>
      <th>2020-01-08</th>
      <td>0.82</td>
      <td>0.69</td>
      <td>0.89</td>
      <td>2.39</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>...</td>
      <td>2.46</td>
      <td>-0.07</td>
      <td>2.52</td>
      <td>-0.13</td>
      <td>2.55</td>
      <td>-0.16</td>
      <td>2.57</td>
      <td>-0.18</td>
      <td>2.56</td>
      <td>-0.17</td>
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
      <th>2020-12-24</th>
      <td>0.82</td>
      <td>0.73</td>
      <td>0.96</td>
      <td>2.51</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>...</td>
      <td>2.52</td>
      <td>-0.01</td>
      <td>2.53</td>
      <td>-0.02</td>
      <td>2.54</td>
      <td>-0.03</td>
      <td>2.55</td>
      <td>-0.04</td>
      <td>2.56</td>
      <td>-0.05</td>
    </tr>
    <tr>
      <th>2020-12-28</th>
      <td>0.80</td>
      <td>0.71</td>
      <td>0.96</td>
      <td>2.47</td>
      <td>0.01</td>
      <td>-0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>...</td>
      <td>2.51</td>
      <td>-0.03</td>
      <td>2.53</td>
      <td>-0.05</td>
      <td>2.53</td>
      <td>-0.06</td>
      <td>2.54</td>
      <td>-0.07</td>
      <td>2.55</td>
      <td>-0.08</td>
    </tr>
    <tr>
      <th>2020-12-29</th>
      <td>0.80</td>
      <td>0.71</td>
      <td>0.96</td>
      <td>2.46</td>
      <td>-0.00</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.00</td>
      <td>0.00</td>
      <td>-0.01</td>
      <td>...</td>
      <td>2.49</td>
      <td>-0.03</td>
      <td>2.52</td>
      <td>-0.05</td>
      <td>2.53</td>
      <td>-0.06</td>
      <td>2.54</td>
      <td>-0.07</td>
      <td>2.55</td>
      <td>-0.08</td>
    </tr>
    <tr>
      <th>2020-12-30</th>
      <td>0.80</td>
      <td>0.71</td>
      <td>0.96</td>
      <td>2.47</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>...</td>
      <td>2.48</td>
      <td>-0.02</td>
      <td>2.51</td>
      <td>-0.04</td>
      <td>2.52</td>
      <td>-0.05</td>
      <td>2.53</td>
      <td>-0.07</td>
      <td>2.55</td>
      <td>-0.08</td>
    </tr>
    <tr>
      <th>2020-12-31</th>
      <td>0.79</td>
      <td>0.71</td>
      <td>0.96</td>
      <td>2.46</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>-0.01</td>
      <td>0.00</td>
      <td>...</td>
      <td>2.47</td>
      <td>-0.02</td>
      <td>2.50</td>
      <td>-0.04</td>
      <td>2.52</td>
      <td>-0.06</td>
      <td>2.53</td>
      <td>-0.07</td>
      <td>2.54</td>
      <td>-0.08</td>
    </tr>
  </tbody>
</table>
<p>253 rows × 59 columns</p>
</div>




```python
plot_time_series(
    df=us_sp_etfs[(us_sp_etfs.index >= "2020-01-01") & (us_sp_etfs.index <= "2021-01-01")],
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[col for col in us_sp_etfs.columns if "total_correlation" in col and "diff" not in col],
    title="Total Correlation - US Equity ETFs (S&P 500, 400, 600)",
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
)
```


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_40_0.png)
    



```python
fund_data_daily_returns_all
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
      <td>0.00</td>
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
      <td>-0.02</td>
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
      <td>0.03</td>
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
      <td>0.01</td>
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
    </tr>
    <tr>
      <th>2026-06-09</th>
      <td>-0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>-0.01</td>
      <td>-0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>-0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>0.02</td>
      <td>-0.02</td>
      <td>-0.03</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>-0.02</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.01</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.04</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.03</td>
      <td>0.04</td>
      <td>0.03</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.01</td>
      <td>0.03</td>
      <td>-0.02</td>
      <td>-0.00</td>
      <td>0.03</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
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
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.00</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>2026-06-13</th>
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
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.01</td>
      <td>0.01</td>
    </tr>
  </tbody>
</table>
<p>8194 rows × 20 columns</p>
</div>




```python
for ticker in us_equity_tickers:
    if ticker not in ["QQQ", "IWD", "IWF"]:
        plot_time_series(
            df=fund_data[(fund_data.index >= "2020-01-01") & (fund_data.index <= "2021-01-01")],
            plot_start_date=None,
            plot_end_date=None,
            plot_columns=[f"{ticker}_Adj_Close"],
        title=f"{tickers_dict[ticker]} Adjusted Close Price",
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
        grid=True,
        legend=False,
        export_plot=False,
        plot_file_name=None,
    )
```


    
![png](asset-class-return-correlations_files/asset-class-return-correlations_42_0.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_42_1.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_42_2.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_42_3.png)
    



    
![png](asset-class-return-correlations_files/asset-class-return-correlations_42_4.png)
    


## Future Investigation

None for now.

## References

None for now.

## Code

{{< post-files >}}
