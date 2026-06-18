## Introduction

Over the past 15 years (or so), leveraged ETFs have become frequently used for trading equity indices, sectors, and other asset classes by the investor that is seeking to use leverage for excess exposure to those asset classes. The question remains, however, what happens to the returns of leveraged ETFs over an extended time horizon and is there an optimal leverage ratio for the long-term buy-and-hold investor that allows them to take advantage of leverage to increase the up-side returns, while avoiding catastrophic losses on the down-side? In this investigation, we will delve into these ideas and see what the data shows.

 ## Python Imports


```python
# Standard Library
import os
import sys
import warnings

from pathlib import Path

# Data Handling
import pandas as pd

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

Here are the functions needed for this project:

* [load_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.
* [pandas_set_decimal_places](/posts/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.
* [plot_histogram](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_histogram): Plot the histogram of a data set from a DataFrame.
* [plot_scatter](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter): Plot the data from a DataFrame for a specified date range and columns.
* [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the timeseries data from a DataFrame for a specified date range and columns.
* [run_regression](/posts/reusable-extensible-python-functions-financial-data-analysis/#run_regression): Run a linear regression using statsmodels OLS and return the results.
* [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.
* [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.


```python
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_histogram import plot_histogram
from plot_scatter import plot_scatter
from plot_time_series import plot_time_series
from run_regression import run_regression
from summary_stats import summary_stats
from yf_pull_data import yf_pull_data
```

## Data Overview

For this exercise, we will investigate the long-term return relationships between the following:

* QQQ (Invesco QQQ Trust, Series 1) and TQQQ (ProShares  UltraPro QQQ)
* SPY (SPDR S&P 500 ETF Trust) and UPRO (ProShares UltraPro S&P 500)

Just to clarify, any time we are referring to "close prices" in this analysis, we are referring to the partially-adjusted close prices that account for splits, but not dividends. Because we are dealing with leveraged ETFs, we want to focus on the pure returns due to change in price, but exclude the dividends, which are not leveraged in the same way as the price changes.

## QQQ & TQQQ

### Acquire & Plot Data (QQQ)

First, let's get the data for QQQ. If we already have the desired data, we can load it from a local pickle file. Otherwise, we can download it from Yahoo Finance using the `yf_pull_data` function.


```python
pandas_set_decimal_places(2)

yf_pull_data(
    base_directory=DATA_DIR,
    ticker="QQQ",
    adjusted=False,
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

qqq = load_data(
    base_directory=DATA_DIR,
    ticker="QQQ",
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "QQQ_Close", etc.
qqq = qqq.rename(columns={
    "Adj Close": "QQQ_Adj_Close",
    "Close": "QQQ_Close",
    "High": "QQQ_High",
    "Low": "QQQ_Low",
    "Open": "QQQ_Open",
    "Volume": "QQQ_Volume"
})

display(qqq)
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
      <th>QQQ_Adj_Close</th>
      <th>QQQ_Close</th>
      <th>QQQ_High</th>
      <th>QQQ_Low</th>
      <th>QQQ_Open</th>
      <th>QQQ_Volume</th>
    </tr>
    <tr>
      <th>Date</th>
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
      <td>43.07</td>
      <td>51.06</td>
      <td>51.16</td>
      <td>50.28</td>
      <td>51.12</td>
      <td>5232000</td>
    </tr>
    <tr>
      <th>1999-03-11</th>
      <td>43.29</td>
      <td>51.31</td>
      <td>51.73</td>
      <td>50.31</td>
      <td>51.44</td>
      <td>9688600</td>
    </tr>
    <tr>
      <th>1999-03-12</th>
      <td>42.23</td>
      <td>50.06</td>
      <td>51.16</td>
      <td>49.66</td>
      <td>51.12</td>
      <td>8743600</td>
    </tr>
    <tr>
      <th>1999-03-15</th>
      <td>43.44</td>
      <td>51.50</td>
      <td>51.56</td>
      <td>49.91</td>
      <td>50.44</td>
      <td>6369000</td>
    </tr>
    <tr>
      <th>1999-03-16</th>
      <td>43.81</td>
      <td>51.94</td>
      <td>52.16</td>
      <td>51.16</td>
      <td>51.72</td>
      <td>4905800</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>693.69</td>
      <td>693.69</td>
      <td>711.28</td>
      <td>692.93</td>
      <td>701.66</td>
      <td>65334300</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>717.12</td>
      <td>717.12</td>
      <td>718.37</td>
      <td>695.00</td>
      <td>699.29</td>
      <td>71798900</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
      <td>721.34</td>
      <td>721.34</td>
      <td>724.01</td>
      <td>711.28</td>
      <td>717.61</td>
      <td>51168400</td>
    </tr>
    <tr>
      <th>2026-06-15</th>
      <td>744.00</td>
      <td>744.00</td>
      <td>744.76</td>
      <td>737.38</td>
      <td>738.10</td>
      <td>46710200</td>
    </tr>
    <tr>
      <th>2026-06-16</th>
      <td>729.86</td>
      <td>729.86</td>
      <td>744.22</td>
      <td>729.64</td>
      <td>742.25</td>
      <td>45348700</td>
    </tr>
  </tbody>
</table>
<p>6860 rows × 6 columns</p>
</div>


And the plot of the time series of partially adjusted close prices:


```python
plot_time_series(
    df=qqq,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Adj_Close"],
    title="QQQ Adjusted Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_9_0.png)
    


### Acquire & Plot Data (TQQQ)

Next, TQQQ:


```python
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="TQQQ",
    adjusted=False,
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

tqqq = load_data(
    base_directory=DATA_DIR,
    ticker="TQQQ",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "TQQQ_Close", etc.
tqqq = tqqq.rename(columns={
    "Adj Close": "TQQQ_Adj_Close",
    "Close": "TQQQ_Close", 
    "High": "TQQQ_High", 
    "Low": "TQQQ_Low", 
    "Open": "TQQQ_Open", 
    "Volume": "TQQQ_Volume"
})

display(tqqq)
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
      <th>TQQQ_Adj_Close</th>
      <th>TQQQ_Close</th>
      <th>TQQQ_High</th>
      <th>TQQQ_Low</th>
      <th>TQQQ_Open</th>
      <th>TQQQ_Volume</th>
    </tr>
    <tr>
      <th>Date</th>
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
      <th>2010-02-11</th>
      <td>0.21</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>0.20</td>
      <td>0.20</td>
      <td>6912000</td>
    </tr>
    <tr>
      <th>2010-02-12</th>
      <td>0.21</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>0.21</td>
      <td>0.21</td>
      <td>17203200</td>
    </tr>
    <tr>
      <th>2010-02-16</th>
      <td>0.21</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>19238400</td>
    </tr>
    <tr>
      <th>2010-02-17</th>
      <td>0.22</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>38361600</td>
    </tr>
    <tr>
      <th>2010-02-18</th>
      <td>0.22</td>
      <td>0.23</td>
      <td>0.24</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>77721600</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>69.27</td>
      <td>69.27</td>
      <td>74.70</td>
      <td>69.00</td>
      <td>71.68</td>
      <td>91465200</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>76.01</td>
      <td>76.01</td>
      <td>76.60</td>
      <td>69.59</td>
      <td>70.89</td>
      <td>116288800</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
      <td>77.52</td>
      <td>77.52</td>
      <td>78.36</td>
      <td>74.29</td>
      <td>76.34</td>
      <td>94070700</td>
    </tr>
    <tr>
      <th>2026-06-15</th>
      <td>84.59</td>
      <td>84.59</td>
      <td>85.03</td>
      <td>82.64</td>
      <td>82.88</td>
      <td>59758000</td>
    </tr>
    <tr>
      <th>2026-06-16</th>
      <td>79.93</td>
      <td>79.93</td>
      <td>84.83</td>
      <td>79.86</td>
      <td>84.19</td>
      <td>67086700</td>
    </tr>
  </tbody>
</table>
<p>4111 rows × 6 columns</p>
</div>


And the plot of the time series of partially adjusted close prices:


```python
plot_time_series(
    df=tqqq,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_Adj_Close"],
    title="TQQQ Adjusted Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_13_0.png)
    


Looking at the close prices doesn't give us a true picture of the magnitude of the difference in returns due to the leverage. In order to see that, we need to look at the cumulative returns and the drawdowns.

 ### Calculate & Plot Cumulative Returns, Rolling Returns, and Drawdowns (QQQ & TQQQ)

 Next, we will calculate the cumulative returns, rolling returns, and drawdowns. This involves aligning the data to start with the inception of TQQQ. For this excercise, we will not extrapolate the data for QQQ back to 1999, but rather just align the data from the inception of TQQQ in 2010.


```python
etfs = ["QQQ", "TQQQ"]

# Merge dataframes and drop rows with missing values
qqq_tqqq_aligned = tqqq.merge(qqq, left_index=True, right_index=True, how='left')
qqq_tqqq_aligned = qqq_tqqq_aligned.dropna()

# Calculate cumulative returns
for etf in etfs:
    qqq_tqqq_aligned[f"{etf}_Return"] = qqq_tqqq_aligned[f"{etf}_Close"].pct_change()
    qqq_tqqq_aligned[f"{etf}_Cumulative_Return"] = (1 + qqq_tqqq_aligned[f"{etf}_Return"]).cumprod() - 1
    qqq_tqqq_aligned[f"{etf}_Cumulative_Return_Plus_One"] = 1 + qqq_tqqq_aligned[f"{etf}_Cumulative_Return"]
    qqq_tqqq_aligned[f"{etf}_Rolling_Max"] = qqq_tqqq_aligned[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    qqq_tqqq_aligned[f"{etf}_Drawdown"] = qqq_tqqq_aligned[f"{etf}_Cumulative_Return_Plus_One"] / qqq_tqqq_aligned[f"{etf}_Rolling_Max"] - 1
    qqq_tqqq_aligned.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)

# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        qqq_tqqq_aligned[f"{etf}_Rolling_Return_{period_name}"] = (
            qqq_tqqq_aligned[f"{etf}_Close"].pct_change(periods=window)
        )
        
display(qqq_tqqq_aligned)
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
      <th>TQQQ_Adj_Close</th>
      <th>TQQQ_Close</th>
      <th>TQQQ_High</th>
      <th>TQQQ_Low</th>
      <th>TQQQ_Open</th>
      <th>TQQQ_Volume</th>
      <th>QQQ_Adj_Close</th>
      <th>QQQ_Close</th>
      <th>QQQ_High</th>
      <th>QQQ_Low</th>
      <th>...</th>
      <th>TQQQ_Rolling_Return_1d</th>
      <th>TQQQ_Rolling_Return_1w</th>
      <th>TQQQ_Rolling_Return_1m</th>
      <th>TQQQ_Rolling_Return_3m</th>
      <th>TQQQ_Rolling_Return_6m</th>
      <th>TQQQ_Rolling_Return_1y</th>
      <th>TQQQ_Rolling_Return_2y</th>
      <th>TQQQ_Rolling_Return_3y</th>
      <th>TQQQ_Rolling_Return_4y</th>
      <th>TQQQ_Rolling_Return_5y</th>
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
      <th>2010-02-11</th>
      <td>0.21</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>0.20</td>
      <td>0.20</td>
      <td>6912000</td>
      <td>37.90</td>
      <td>43.67</td>
      <td>43.79</td>
      <td>42.76</td>
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
      <th>2010-02-12</th>
      <td>0.21</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>0.21</td>
      <td>0.21</td>
      <td>17203200</td>
      <td>37.98</td>
      <td>43.76</td>
      <td>43.88</td>
      <td>43.16</td>
      <td>...</td>
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
    </tr>
    <tr>
      <th>2010-02-16</th>
      <td>0.21</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.22</td>
      <td>0.22</td>
      <td>19238400</td>
      <td>38.47</td>
      <td>44.32</td>
      <td>44.35</td>
      <td>43.85</td>
      <td>...</td>
      <td>0.04</td>
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
      <th>2010-02-17</th>
      <td>0.22</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>38361600</td>
      <td>38.69</td>
      <td>44.57</td>
      <td>44.57</td>
      <td>44.26</td>
      <td>...</td>
      <td>0.02</td>
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
      <th>2010-02-18</th>
      <td>0.22</td>
      <td>0.23</td>
      <td>0.24</td>
      <td>0.23</td>
      <td>0.23</td>
      <td>77721600</td>
      <td>38.93</td>
      <td>44.85</td>
      <td>44.93</td>
      <td>44.45</td>
      <td>...</td>
      <td>0.02</td>
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
      <th>2026-06-10</th>
      <td>69.27</td>
      <td>69.27</td>
      <td>74.70</td>
      <td>69.00</td>
      <td>71.68</td>
      <td>91465200</td>
      <td>693.69</td>
      <td>693.69</td>
      <td>711.28</td>
      <td>692.93</td>
      <td>...</td>
      <td>-0.06</td>
      <td>-0.20</td>
      <td>-0.10</td>
      <td>0.40</td>
      <td>0.24</td>
      <td>0.86</td>
      <td>1.05</td>
      <td>2.75</td>
      <td>2.97</td>
      <td>1.80</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>76.01</td>
      <td>76.01</td>
      <td>76.60</td>
      <td>69.59</td>
      <td>70.89</td>
      <td>116288800</td>
      <td>717.12</td>
      <td>717.12</td>
      <td>718.37</td>
      <td>695.00</td>
      <td>...</td>
      <td>0.10</td>
      <td>-0.11</td>
      <td>0.01</td>
      <td>0.62</td>
      <td>0.36</td>
      <td>1.00</td>
      <td>1.26</td>
      <td>3.12</td>
      <td>3.73</td>
      <td>1.92</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
      <td>77.52</td>
      <td>77.52</td>
      <td>78.36</td>
      <td>74.29</td>
      <td>76.34</td>
      <td>94070700</td>
      <td>721.34</td>
      <td>721.34</td>
      <td>724.01</td>
      <td>711.28</td>
      <td>...</td>
      <td>0.02</td>
      <td>0.06</td>
      <td>0.00</td>
      <td>0.69</td>
      <td>0.37</td>
      <td>1.06</td>
      <td>1.31</td>
      <td>3.43</td>
      <td>3.76</td>
      <td>1.96</td>
    </tr>
    <tr>
      <th>2026-06-15</th>
      <td>84.59</td>
      <td>84.59</td>
      <td>85.03</td>
      <td>82.64</td>
      <td>82.88</td>
      <td>59758000</td>
      <td>744.00</td>
      <td>744.00</td>
      <td>744.76</td>
      <td>737.38</td>
      <td>...</td>
      <td>0.09</td>
      <td>0.11</td>
      <td>0.07</td>
      <td>0.78</td>
      <td>0.51</td>
      <td>1.24</td>
      <td>1.49</td>
      <td>3.68</td>
      <td>4.08</td>
      <td>2.22</td>
    </tr>
    <tr>
      <th>2026-06-16</th>
      <td>79.93</td>
      <td>79.93</td>
      <td>84.83</td>
      <td>79.86</td>
      <td>84.19</td>
      <td>67086700</td>
      <td>729.86</td>
      <td>729.86</td>
      <td>744.22</td>
      <td>729.64</td>
      <td>...</td>
      <td>-0.06</td>
      <td>0.08</td>
      <td>0.06</td>
      <td>0.66</td>
      <td>0.51</td>
      <td>1.19</td>
      <td>1.31</td>
      <td>3.37</td>
      <td>3.90</td>
      <td>2.04</td>
    </tr>
  </tbody>
</table>
<p>4111 rows × 38 columns</p>
</div>


And now the plot for the cumulative returns:


```python
plot_time_series(
    df=qqq_tqqq_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Cumulative_Return", "TQQQ_Cumulative_Return"],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_17_0.png)
    


And the drawdown plot:


```python
plot_time_series(
    df=qqq_tqqq_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Drawdown", "TQQQ_Drawdown"],
    title="Drawdowns",
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
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_19_0.png)
    


Here is where we truly see the volatility of TQQQ relative to QQQ. In the past 5 years, TQQQ has had drawdowns of 50%, 60%, 70%, and 80%. While it has recovered to make new highs (with the exception of the current ~25% drawdown as of mid-March 2026), very few investors can endure those drawdowns and continue to hold their position. At the same time, we can see from the plot that a ~35% drawdown in QQQ equated to a ~80% drawdown in TQQQ, which is not in fact, 3x. So this tells us (which we already knew) that there is dispersion in the long-term returns relative to the short-term returns between the non-leveraged QQQ and 3x leveraged TQQQ. This idea is well documented in the financial literature as "volatility decay" or "volatility drag". But, and this is the question we are trying to answer, how significant is this effect over various time horizons?

### Summary Statistics (QQQ & TQQQ)

Looking at the summary statistics further confirms our intuitions about the volatility and drawdowns.


```python
qqq_sum_stats = summary_stats(
    fund_list=["QQQ"],
    df=qqq_tqqq_aligned[["QQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

tqqq_sum_stats = summary_stats(
    fund_list=["TQQQ"],
    df=qqq_tqqq_aligned[["TQQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([qqq_sum_stats, tqqq_sum_stats])

display(sum_stats)
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
      <th>QQQ_Return</th>
      <td>0.19</td>
      <td>0.21</td>
      <td>0.94</td>
      <td>0.19</td>
      <td>0.12</td>
      <td>2025-04-09</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.36</td>
      <td>2021-11-19</td>
      <td>2022-12-28</td>
      <td>2023-12-15</td>
      <td>352</td>
      <td>0.53</td>
    </tr>
    <tr>
      <th>TQQQ_Return</th>
      <td>0.55</td>
      <td>0.61</td>
      <td>0.90</td>
      <td>0.44</td>
      <td>0.35</td>
      <td>2025-04-09</td>
      <td>-0.34</td>
      <td>2020-03-16</td>
      <td>-0.82</td>
      <td>2021-11-19</td>
      <td>2022-12-28</td>
      <td>2024-12-11</td>
      <td>714</td>
      <td>0.53</td>
    </tr>
  </tbody>
</table>
</div>


Note that these statistics are being run on the partially-adjusted close prices, which are not the true returns (due to not accounting for dividends), but they do give us a picture of the relative volatility and drawdowns of the two ETFs. The mean return for TQQQ is much higher than that of QQQ, but the volatility is also much higher, which is consistent with the idea of leverage amplifying both the up-side and down-side. The maximum drawdown for TQQQ is also much higher than that of QQQ, which again confirms our observations from the drawdown plot.

Also note that the daily maximum return for both funds occured during "Liberation Day" and the daily minimum return for both funds occured early on during the COVID-19 pandemic.

### Plot Returns & Verify Beta (QQQ & TQQQ)

Before we look at the rolling returns, let us first verify that the daily returns for TQQQ are in fact ~3x those of QQQ. We can do that by plotting the daily returns for both funds against each other and running a linear regression to see if the beta is indeed ~3.


```python
plot_scatter(
    df=qqq_tqqq_aligned,
    x_plot_column="QQQ_Return",
    y_plot_columns=["TQQQ_Return"],
    title="QQQ & TQQQ Returns",
    x_label="QQQ Return",
    x_format="Decimal",
    x_format_decimal_places=2,
    x_tick_spacing="Auto",
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="TQQQ Return",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=True,
    OLS_column="TQQQ_Return",
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=True,
    RidgeCV_column="TQQQ_Return",
    regression_constant=True,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_23_0.png)
    



```python
model = run_regression(
    df=qqq_tqqq_aligned,
    x_plot_column="QQQ_Return",
    y_plot_column="TQQQ_Return",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)

print(model.summary())
```

                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:            TQQQ_Return   R-squared:                       0.997
    Model:                            OLS   Adj. R-squared:                  0.997
    Method:                 Least Squares   F-statistic:                 1.540e+06
    Date:                Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                        14:31:49   Log-Likelihood:                 19741.
    No. Observations:                4110   AIC:                        -3.948e+04
    Df Residuals:                    4108   BIC:                        -3.946e+04
    Df Model:                           1                                         
    Covariance Type:            nonrobust                                         
    ==============================================================================
                     coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------
    const      -8.798e-05    3.1e-05     -2.836      0.005      -0.000   -2.72e-05
    QQQ_Return     2.9553      0.002   1240.806      0.000       2.951       2.960
    ==============================================================================
    Omnibus:                     5361.302   Durbin-Watson:                   2.568
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):          9467735.605
    Skew:                          -6.352   Prob(JB):                         0.00
    Kurtosis:                     237.786   Cond. No.                         76.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.


Visually, this plot makes sense and we can see that there is a strong clustering of points, but we double check with the regression, regressing the TQQQ daily return (y) on the QQQ daily return (X).

Given the above result, with a coefficient of 2.96 and an R^2 of 0.997 (based on the statsmodels OLS regression), we can say that TQQQ does in fact return ~3x QQQ. We would also intuitively expect the coefficient to be 0, and it is nearly 0.

Interestingly, the coefficient varies between OLS and Ridge cross-validation, and both are less than 3.

### Extrapolate Data (QQQ & TQQQ)

With the above coefficient, we will now extrapolate the returns of QQQ to backfill the data from the inception of QQQ in 1999 to the inception of TQQQ in 2010 to expand our dataset of returns. For this, we'll use the coefficient of 2.96 that we found in the regression results above.


```python
# Set leverage multiplier based on regression coefficient
LEVERAGE_MULTIPLIER = model.params.iloc[1]

# Merge dataframes and extrapolate return values for QQQ back to 1999 using the leverage multiplier
qqq_tqqq_extrap = qqq[["QQQ_Close"]].merge(tqqq[["TQQQ_Close"]], left_index=True, right_index=True, how='left')

etfs = ["QQQ", "TQQQ"]

# Calculate cumulative returns
for etf in etfs:
    qqq_tqqq_extrap[f"{etf}_Return"] = qqq_tqqq_extrap[f"{etf}_Close"].pct_change()

# Extrapolate TQQQ returns for missing values
qqq_tqqq_extrap["TQQQ_Return"] = qqq_tqqq_extrap["TQQQ_Return"].fillna(LEVERAGE_MULTIPLIER * qqq_tqqq_extrap["QQQ_Return"])

# Find the first valid TQQQ_Close index and value
first_valid_idx = qqq_tqqq_extrap['TQQQ_Close'].first_valid_index()
print(first_valid_idx)
first_valid_price = qqq_tqqq_extrap.loc[first_valid_idx, 'TQQQ_Close']
print(first_valid_price)
```

    2010-02-11 00:00:00
    0.21627600491046906


Before we extrapolate, let's first look at the data we have for QQQ and TQQQ around the inception of TQQQ in 2010:


```python
# Check values around the first valid index
pandas_set_decimal_places(4)
display(qqq_tqqq_extrap.loc["2010-02-08":"2010-02-13"])
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
      <th>QQQ_Close</th>
      <th>TQQQ_Close</th>
      <th>QQQ_Return</th>
      <th>TQQQ_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2010-02-08</th>
      <td>42.6700</td>
      <td>NaN</td>
      <td>-0.0072</td>
      <td>-0.0213</td>
    </tr>
    <tr>
      <th>2010-02-09</th>
      <td>43.1100</td>
      <td>NaN</td>
      <td>0.0103</td>
      <td>0.0305</td>
    </tr>
    <tr>
      <th>2010-02-10</th>
      <td>43.0200</td>
      <td>NaN</td>
      <td>-0.0021</td>
      <td>-0.0062</td>
    </tr>
    <tr>
      <th>2010-02-11</th>
      <td>43.6700</td>
      <td>0.2163</td>
      <td>0.0151</td>
      <td>0.0447</td>
    </tr>
    <tr>
      <th>2010-02-12</th>
      <td>43.7600</td>
      <td>0.2172</td>
      <td>0.0021</td>
      <td>0.0041</td>
    </tr>
  </tbody>
</table>
</div>


Now, backfill the data for the TQQQ close price:


```python
# Iterate through the dataframe backwards
for i in range(qqq_tqqq_extrap.index.get_loc(first_valid_idx) - 1, -1, -1):
    
    # The return that led to the price the next day
    current_return = qqq_tqqq_extrap.iloc[i + 1]['TQQQ_Return']

    # Get the next day's price
    next_price = qqq_tqqq_extrap.iloc[i + 1]['TQQQ_Close']
    
    # Price_{t} = Price_{t+1} / (1 + Return_{t})
    qqq_tqqq_extrap.loc[qqq_tqqq_extrap.index[i], 'TQQQ_Close'] = next_price / (1 + current_return)
```

Finally, confirm the values are correct:


```python
# Confirm values around the first valid index after extrapolation
display(qqq_tqqq_extrap.loc["2010-02-08":"2010-02-13"])
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
      <th>QQQ_Close</th>
      <th>TQQQ_Close</th>
      <th>QQQ_Return</th>
      <th>TQQQ_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2010-02-08</th>
      <td>42.6700</td>
      <td>0.2022</td>
      <td>-0.0072</td>
      <td>-0.0213</td>
    </tr>
    <tr>
      <th>2010-02-09</th>
      <td>43.1100</td>
      <td>0.2083</td>
      <td>0.0103</td>
      <td>0.0305</td>
    </tr>
    <tr>
      <th>2010-02-10</th>
      <td>43.0200</td>
      <td>0.2070</td>
      <td>-0.0021</td>
      <td>-0.0062</td>
    </tr>
    <tr>
      <th>2010-02-11</th>
      <td>43.6700</td>
      <td>0.2163</td>
      <td>0.0151</td>
      <td>0.0447</td>
    </tr>
    <tr>
      <th>2010-02-12</th>
      <td>43.7600</td>
      <td>0.2172</td>
      <td>0.0021</td>
      <td>0.0041</td>
    </tr>
  </tbody>
</table>
</div>


And the complete DataFrame with the extrapolated values:


```python
pandas_set_decimal_places(2)
display(qqq_tqqq_extrap)
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
      <th>QQQ_Close</th>
      <th>TQQQ_Close</th>
      <th>QQQ_Return</th>
      <th>TQQQ_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1999-03-10</th>
      <td>51.06</td>
      <td>13.82</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1999-03-11</th>
      <td>51.31</td>
      <td>14.02</td>
      <td>0.00</td>
      <td>0.01</td>
    </tr>
    <tr>
      <th>1999-03-12</th>
      <td>50.06</td>
      <td>13.01</td>
      <td>-0.02</td>
      <td>-0.07</td>
    </tr>
    <tr>
      <th>1999-03-15</th>
      <td>51.50</td>
      <td>14.12</td>
      <td>0.03</td>
      <td>0.08</td>
    </tr>
    <tr>
      <th>1999-03-16</th>
      <td>51.94</td>
      <td>14.47</td>
      <td>0.01</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>693.69</td>
      <td>69.27</td>
      <td>-0.02</td>
      <td>-0.06</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>717.12</td>
      <td>76.01</td>
      <td>0.03</td>
      <td>0.10</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
      <td>721.34</td>
      <td>77.52</td>
      <td>0.01</td>
      <td>0.02</td>
    </tr>
    <tr>
      <th>2026-06-15</th>
      <td>744.00</td>
      <td>84.59</td>
      <td>0.03</td>
      <td>0.09</td>
    </tr>
    <tr>
      <th>2026-06-16</th>
      <td>729.86</td>
      <td>79.93</td>
      <td>-0.02</td>
      <td>-0.06</td>
    </tr>
  </tbody>
</table>
<p>6860 rows × 4 columns</p>
</div>


After the extrapolation, we now have the following plots for the prices, cumulative returns, and drawdowns:


```python
etfs = ["QQQ", "TQQQ"]

# Calculate cumulative returns
for etf in etfs:
    qqq_tqqq_extrap[f"{etf}_Return"] = qqq_tqqq_extrap[f"{etf}_Close"].pct_change()
    qqq_tqqq_extrap[f"{etf}_Cumulative_Return"] = (1 + qqq_tqqq_extrap[f"{etf}_Return"]).cumprod() - 1
    qqq_tqqq_extrap[f"{etf}_Cumulative_Return_Plus_One"] = 1 + qqq_tqqq_extrap[f"{etf}_Cumulative_Return"]
    qqq_tqqq_extrap[f"{etf}_Rolling_Max"] = qqq_tqqq_extrap[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    qqq_tqqq_extrap[f"{etf}_Drawdown"] = qqq_tqqq_extrap[f"{etf}_Cumulative_Return_Plus_One"] / qqq_tqqq_extrap[f"{etf}_Rolling_Max"] - 1
    qqq_tqqq_extrap.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)
```


```python
plot_time_series(
    df=qqq_tqqq_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Close"],
    title="QQQ Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_37_0.png)
    



```python
plot_time_series(
    df=qqq_tqqq_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_Close"],
    title="TQQQ Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_38_0.png)
    



```python
plot_time_series(
    df=qqq_tqqq_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Cumulative_Return", "TQQQ_Cumulative_Return"],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_39_0.png)
    



```python
plot_time_series(
    df=qqq_tqqq_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["QQQ_Drawdown", "TQQQ_Drawdown"],
    title="Drawdowns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
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
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_0.png)
    



```python
qqq_extrap_sum_stats = summary_stats(
    fund_list=["QQQ"],
    df=qqq_tqqq_extrap[["QQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

tqqq_extrap_sum_stats = summary_stats(
    fund_list=["TQQQ"],
    df=qqq_tqqq_extrap[["TQQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([qqq_sum_stats, tqqq_sum_stats, qqq_extrap_sum_stats, tqqq_extrap_sum_stats])
sum_stats.index = ["QQQ (2010 - Present)", "TQQQ (2010 - Present)", "QQQ (1999 - Present)", "TQQQ Extrapolated (1999 - Present)"]

display(sum_stats)
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
      <th>QQQ (2010 - Present)</th>
      <td>0.19</td>
      <td>0.21</td>
      <td>0.94</td>
      <td>0.19</td>
      <td>0.12</td>
      <td>2025-04-09</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.36</td>
      <td>2021-11-19</td>
      <td>2022-12-28</td>
      <td>2023-12-15</td>
      <td>352.00</td>
      <td>0.53</td>
    </tr>
    <tr>
      <th>TQQQ (2010 - Present)</th>
      <td>0.55</td>
      <td>0.61</td>
      <td>0.90</td>
      <td>0.44</td>
      <td>0.35</td>
      <td>2025-04-09</td>
      <td>-0.34</td>
      <td>2020-03-16</td>
      <td>-0.82</td>
      <td>2021-11-19</td>
      <td>2022-12-28</td>
      <td>2024-12-11</td>
      <td>714.00</td>
      <td>0.53</td>
    </tr>
    <tr>
      <th>QQQ (1999 - Present)</th>
      <td>0.13</td>
      <td>0.27</td>
      <td>0.50</td>
      <td>0.10</td>
      <td>0.17</td>
      <td>2001-01-03</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.83</td>
      <td>2000-03-27</td>
      <td>2002-10-09</td>
      <td>2016-09-06</td>
      <td>5081.00</td>
      <td>0.12</td>
    </tr>
    <tr>
      <th>TQQQ Extrapolated (1999 - Present)</th>
      <td>0.38</td>
      <td>0.80</td>
      <td>0.48</td>
      <td>0.07</td>
      <td>0.50</td>
      <td>2001-01-03</td>
      <td>-0.34</td>
      <td>2020-03-16</td>
      <td>-1.00</td>
      <td>2000-03-27</td>
      <td>2009-03-09</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>0.07</td>
    </tr>
  </tbody>
</table>
</div>


A few quick comments before we look at rolling returns:

* The cumulative return for TQQQ is *less* than that of QQQ - which is starkly different from the plot beginning in 2010 at the inception of TQQQ. So the return path really matters here.
* The drawdown for TQQQ is nearly 100%... which also represents nearly a total loss of capital for any allocation to the extrap-TQQQ. Furthermore, as we walk forward through time (2002, 2003, ... etc.), there is really no reason to believe that the returns would ever recover (even partially). So while we can look at the rolling returns and see how they compare to the 3x return of QQQ, we should keep in mind that the drawdown post-1999 is so severe that it would be very difficult for any investor to hold through it.
* The recovery time for QQQ was more than 5,000 days, or ~14 years. Note that this is calendar days, not trading days. While returns have been great for QQQ since 2016, the 14 year dry spell is a reminder of just how large the tech bubble was.
* The extrapolated TQQQ data remains in a drawdown and has never recovered to make new highs (as of March 2026).

### Plot Rolling Returns (QQQ & TQQQ)

Next, we will consider the following:

* Histogram and scatter plots of the rolling returns of QQQ and TQQQ
* Regressions to establish a "leverage factor" for the rolling returns
* The deviation from a 3x return for each time period

For this set of regressions, we will also allow the constant. First, we need the rolling returns for various time periods:



```python
# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        qqq_tqqq_extrap[f"{etf}_Rolling_Return_{period_name}"] = (
            qqq_tqqq_extrap[f"{etf}_Close"].pct_change(periods=window)
        )
```

This gives us the following series of histograms, scatter plots, and regression model results:


```python
# Create a dataframe to hold rolling returns stats
rolling_returns_stats = pd.DataFrame()

for period_name, window in rolling_windows.items():
    plot_histogram(
        df=qqq_tqqq_extrap,
        plot_columns=[f"QQQ_Rolling_Return_{period_name}", f"TQQQ_Rolling_Return_{period_name}"],
        title=f"QQQ & TQQQ {period_name} Rolling Returns",
        x_label="Rolling Return",
        x_tick_spacing="Auto",
        x_tick_rotation=30,
        y_label="# Of Datapoints",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    plot_scatter(
        df=qqq_tqqq_extrap,
        x_plot_column=f"QQQ_Rolling_Return_{period_name}",
        y_plot_columns=[f"TQQQ_Rolling_Return_{period_name}"],
        title=f"QQQ & TQQQ {period_name} Rolling Returns",
        x_label="QQQ Rolling Return",
        x_format="Decimal",
        x_format_decimal_places=2,
        x_tick_spacing="Auto",
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="TQQQ Rolling Return",
        y_format="Decimal",
        y_format_decimal_places=2,
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        plot_OLS_regression_line=True,
        OLS_column=f"TQQQ_Rolling_Return_{period_name}",
        plot_Ridge_regression_line=False,
        Ridge_column=None,
        plot_RidgeCV_regression_line=True,
        RidgeCV_column=f"TQQQ_Rolling_Return_{period_name}",
        regression_constant=True,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    # Run OLS regression with statsmodels
    model = run_regression(
        df=qqq_tqqq_extrap,
        x_plot_column=f"QQQ_Rolling_Return_{period_name}",
        y_plot_column=f"TQQQ_Rolling_Return_{period_name}",
        regression_model="OLS-statsmodels",
        regression_constant=True,
    )
    print(model.summary())

    # Add the regression results to the rolling returns stats dataframe
    intercept = model.params.iloc[0]
    intercept_pvalue = model.pvalues.iloc[0]   # p-value for Intercept
    slope = model.params.iloc[1]
    slope_pvalue = model.pvalues.iloc[1]       # p-value for QQQ_Return
    r_squared = model.rsquared

    # Calc skew
    return_ratio = qqq_tqqq_extrap[f'TQQQ_Rolling_Return_{period_name}'] / qqq_tqqq_extrap[f'QQQ_Rolling_Return_{period_name}']
    skew = return_ratio.skew()

    # Calc conditional symmetry
    up_markets = qqq_tqqq_extrap[qqq_tqqq_extrap[f'QQQ_Rolling_Return_{period_name}'] > 0]
    down_markets = qqq_tqqq_extrap[qqq_tqqq_extrap[f'QQQ_Rolling_Return_{period_name}'] <= 0]

    avg_beta_up = (up_markets[f'TQQQ_Rolling_Return_{period_name}'] / up_markets[f'QQQ_Rolling_Return_{period_name}']).mean()
    avg_beta_down = (down_markets[f'TQQQ_Rolling_Return_{period_name}'] / down_markets[f'QQQ_Rolling_Return_{period_name}']).mean()

    asymmetry = avg_beta_up - avg_beta_down

    rolling_returns_slope_int = pd.DataFrame({
        "Period": period_name,
        "Intercept": [intercept],
        # "Intercept_PValue": [intercept_pvalue],
        "Slope": [slope],
        # "Slope_PValue": [slope_pvalue],
        "R_Squared": [r_squared],
        "Return Skew": [skew],
        "Average Upside Beta": [avg_beta_up],
        "Average Downside Beta": [avg_beta_down],
        "Asymmetry": [asymmetry]
    })

    rolling_returns_stats = pd.concat([rolling_returns_stats, rolling_returns_slope_int])
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_0.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_1.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_1d   R-squared:                       0.999
    Model:                                OLS   Adj. R-squared:                  0.999
    Method:                     Least Squares   F-statistic:                 7.303e+06
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:31:57   Log-Likelihood:                 34698.
    No. Observations:                    6859   AIC:                        -6.939e+04
    Df Residuals:                        6857   BIC:                        -6.938e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                  -5.27e-05   1.86e-05     -2.837      0.005   -8.91e-05   -1.63e-05
    QQQ_Rolling_Return_1d     2.9553      0.001   2702.435      0.000       2.953       2.957
    ==============================================================================
    Omnibus:                    10277.277   Durbin-Watson:                   2.566
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         44417091.716
    Skew:                          -8.263   Prob(JB):                         0.00
    Kurtosis:                     396.884   Cond. No.                         58.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_3.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_4.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_1w   R-squared:                       0.994
    Model:                                OLS   Adj. R-squared:                  0.994
    Method:                     Least Squares   F-statistic:                 1.134e+06
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:32:01   Log-Likelihood:                 23396.
    No. Observations:                    6855   AIC:                        -4.679e+04
    Df Residuals:                        6853   BIC:                        -4.677e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0008   9.65e-05     -8.403      0.000      -0.001      -0.001
    QQQ_Rolling_Return_1w     2.9532      0.003   1064.980      0.000       2.948       2.959
    ==============================================================================
    Omnibus:                     2863.007   Durbin-Watson:                   0.931
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           576171.657
    Skew:                          -0.858   Prob(JB):                         0.00
    Kurtosis:                      47.881   Cond. No.                         28.8
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_6.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_7.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_1m   R-squared:                       0.982
    Model:                                OLS   Adj. R-squared:                  0.982
    Method:                     Least Squares   F-statistic:                 3.747e+05
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:32:05   Log-Likelihood:                 14971.
    No. Observations:                    6839   AIC:                        -2.994e+04
    Df Residuals:                        6837   BIC:                        -2.992e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0036      0.000    -10.803      0.000      -0.004      -0.003
    QQQ_Rolling_Return_1m     2.9365      0.005    612.153      0.000       2.927       2.946
    ==============================================================================
    Omnibus:                     1652.780   Durbin-Watson:                   0.293
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            67847.108
    Skew:                           0.383   Prob(JB):                         0.00
    Kurtosis:                      18.411   Cond. No.                         14.6
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_9.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_10.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_3m   R-squared:                       0.959
    Model:                                OLS   Adj. R-squared:                  0.959
    Method:                     Least Squares   F-statistic:                 1.577e+05
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:32:09   Log-Likelihood:                 8045.5
    No. Observations:                    6797   AIC:                        -1.609e+04
    Df Residuals:                        6795   BIC:                        -1.607e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0083      0.001     -8.979      0.000      -0.010      -0.007
    QQQ_Rolling_Return_3m     2.9871      0.008    397.059      0.000       2.972       3.002
    ==============================================================================
    Omnibus:                     3498.049   Durbin-Watson:                   0.105
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            80662.481
    Skew:                           1.963   Prob(JB):                         0.00
    Kurtosis:                      19.414   Cond. No.                         8.38
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_12.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_13.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_6m   R-squared:                       0.916
    Model:                                OLS   Adj. R-squared:                  0.916
    Method:                     Least Squares   F-statistic:                 7.321e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:32:12   Log-Likelihood:                 2661.5
    No. Observations:                    6734   AIC:                            -5319.
    Df Residuals:                        6732   BIC:                            -5305.
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0102      0.002     -4.853      0.000      -0.014      -0.006
    QQQ_Rolling_Return_6m     3.0396      0.011    270.569      0.000       3.018       3.062
    ==============================================================================
    Omnibus:                     3714.404   Durbin-Watson:                   0.056
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            61899.283
    Skew:                           2.278   Prob(JB):                         0.00
    Kurtosis:                      17.137   Cond. No.                         5.68
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_15.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_16.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_1y   R-squared:                       0.881
    Model:                                OLS   Adj. R-squared:                  0.881
    Method:                     Least Squares   F-statistic:                 4.869e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:32:16   Log-Likelihood:                -883.92
    No. Observations:                    6608   AIC:                             1772.
    Df Residuals:                        6606   BIC:                             1785.
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                     0.0191      0.004      5.072      0.000       0.012       0.027
    QQQ_Rolling_Return_1y     2.8417      0.013    220.652      0.000       2.816       2.867
    ==============================================================================
    Omnibus:                     3502.694   Durbin-Watson:                   0.037
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            67965.448
    Skew:                           2.104   Prob(JB):                         0.00
    Kurtosis:                      18.138   Cond. No.                         3.85
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_18.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_19.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_2y   R-squared:                       0.847
    Model:                                OLS   Adj. R-squared:                  0.847
    Method:                     Least Squares   F-statistic:                 3.529e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:32:20   Log-Likelihood:                -4464.1
    No. Observations:                    6356   AIC:                             8932.
    Df Residuals:                        6354   BIC:                             8946.
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                     0.0068      0.007      0.923      0.356      -0.008       0.021
    QQQ_Rolling_Return_2y     3.1236      0.017    187.862      0.000       3.091       3.156
    ==============================================================================
    Omnibus:                     1623.545   Durbin-Watson:                   0.019
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4249.364
    Skew:                           1.374   Prob(JB):                         0.00
    Kurtosis:                       5.914   Cond. No.                         2.90
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_21.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_22.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_3y   R-squared:                       0.808
    Model:                                OLS   Adj. R-squared:                  0.808
    Method:                     Least Squares   F-statistic:                 2.565e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:32:24   Log-Likelihood:                -6738.8
    No. Observations:                    6104   AIC:                         1.348e+04
    Df Residuals:                        6102   BIC:                         1.350e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0608      0.013     -4.850      0.000      -0.085      -0.036
    QQQ_Rolling_Return_3y     3.3335      0.021    160.141      0.000       3.293       3.374
    ==============================================================================
    Omnibus:                      871.091   Durbin-Watson:                   0.015
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1505.348
    Skew:                           0.941   Prob(JB):                         0.00
    Kurtosis:                       4.541   Cond. No.                         2.66
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_24.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_25.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_4y   R-squared:                       0.778
    Model:                                OLS   Adj. R-squared:                  0.778
    Method:                     Least Squares   F-statistic:                 2.048e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:32:28   Log-Likelihood:                -8910.6
    No. Observations:                    5852   AIC:                         1.783e+04
    Df Residuals:                        5850   BIC:                         1.784e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.2947      0.021    -13.729      0.000      -0.337      -0.253
    QQQ_Rolling_Return_4y     3.9098      0.027    143.110      0.000       3.856       3.963
    ==============================================================================
    Omnibus:                      221.269   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              114.248
    Skew:                           0.155   Prob(JB):                     1.55e-25
    Kurtosis:                       2.390   Cond. No.                         2.67
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_27.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_45_28.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     TQQQ_Rolling_Return_5y   R-squared:                       0.738
    Model:                                OLS   Adj. R-squared:                  0.738
    Method:                     Least Squares   F-statistic:                 1.579e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:32:31   Log-Likelihood:                -12238.
    No. Observations:                    5600   AIC:                         2.448e+04
    Df Residuals:                        5598   BIC:                         2.449e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.9068      0.045    -20.345      0.000      -0.994      -0.819
    QQQ_Rolling_Return_5y     5.1912      0.041    125.644      0.000       5.110       5.272
    ==============================================================================
    Omnibus:                      324.029   Durbin-Watson:                   0.009
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              464.545
    Skew:                           0.512   Prob(JB):                    1.33e-101
    Kurtosis:                       3.971   Cond. No.                         2.74
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.


You're welcome to digest each plot, but here's my observations on the above results:

* 1d: TQQQ tracks QQQ as expected (it's a 3x daily return leveraged ETF after all), with a regression coefficient of 2.96 and an R^2 of 0.997, and we extrapolated half the data with the same coefficient.
* 1w: Essentially the same as above. A few outliers, but the regression coefficient is still 2.95 with an R^2 of 0.994. We see a slight skew toward the positive in the rolling returns.
* 1m: The skew toward the positive is more pronounced, and we see more outliers. The regression coefficient has decreased to 2.93 and the R^2 has dropped to 0.98, which is still very high, but we are starting to see some dispersion in the returns.
* 3m: The skew toward the positive is even more pronounced, and we see even more outliers. The regression coefficient has *increased*, to 2.98 and the R^2 has dropped to 0.96.
* 6m: The skew toward the positive is very pronounced, and we see a significant number of outliers with pronounced curvanture in the plot. The regression coefficient has increased again, to 3.4 and the R^2 has dropped to 0.92.
* 1y: At this point, based on the plot and the regression results, we can start to see that the returns of TQQQ are no longer tracking 3x the returns of QQQ as closely as they did in the shorter time periods. The regression coefficient has is now 2.84 and the R^2 has dropped to 0.88.
* 4y and 5y: We can see that there are periods where the rolling returns of TQQQ are significantly higher *and* lower than 3x the returns of QQQ, which is consistent with the idea of volatility decay.

For 4y, based on the regression results, we see that if the rolling return of QQQ was 0, then we would expect a return of -0.30 for TQQQ.

$$
r_{TQQQ} = -0.30 + 3.93 \times r_{QQQ} = -0.30 + 3.93 \times 0 = -0.30
$$

On the other end of the spectrum, if the rolling return of QQQ was 1, then we would expect a return of:

$$
r_{TQQQ} = -0.30 + 3.93 \times r_{QQQ} = -0.30 + 3.93 \times 1 = 3.63
$$

In general, the positive skew of the rolling returns of TQQQ relative to QQQ is related to the general postive return performance of QQQ. With sustained positive returns, the leverage effect of TQQQ will amplify those returns, leading to a positive skew. However, during periods of negative returns for QQQ, the leverage effect will also amplify those losses, leading to a negative skew, and to the limit of a cumulative return of -1, or a 100% loss. The overall skewness of the rolling returns will depend on the balance of these positive and negative periods.

### Rolling Returns Deviation (QQQ & TQQQ)

Next, we will the rolling returns deviation from the expected 3x return for each time period. This will give us a better picture of the volatility decay effect and how it changes over different time horizons.


```python
rolling_returns_stats["Return_Deviation_From_3x"] = rolling_returns_stats["Slope"] - 3.0
pandas_set_decimal_places(3)
display(rolling_returns_stats.set_index("Period"))
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
      <th>Intercept</th>
      <th>Slope</th>
      <th>R_Squared</th>
      <th>Return Skew</th>
      <th>Average Upside Beta</th>
      <th>Average Downside Beta</th>
      <th>Asymmetry</th>
      <th>Return_Deviation_From_3x</th>
    </tr>
    <tr>
      <th>Period</th>
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
      <th>1d</th>
      <td>-0.000</td>
      <td>2.955</td>
      <td>0.999</td>
      <td>NaN</td>
      <td>2.958</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.045</td>
    </tr>
    <tr>
      <th>1w</th>
      <td>-0.001</td>
      <td>2.953</td>
      <td>0.994</td>
      <td>NaN</td>
      <td>2.557</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.047</td>
    </tr>
    <tr>
      <th>1m</th>
      <td>-0.004</td>
      <td>2.936</td>
      <td>0.982</td>
      <td>NaN</td>
      <td>2.213</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.064</td>
    </tr>
    <tr>
      <th>3m</th>
      <td>-0.008</td>
      <td>2.987</td>
      <td>0.959</td>
      <td>NaN</td>
      <td>1.997</td>
      <td>-inf</td>
      <td>inf</td>
      <td>-0.013</td>
    </tr>
    <tr>
      <th>6m</th>
      <td>-0.010</td>
      <td>3.040</td>
      <td>0.916</td>
      <td>-8.109</td>
      <td>1.482</td>
      <td>5.521</td>
      <td>-4.039</td>
      <td>0.040</td>
    </tr>
    <tr>
      <th>1y</th>
      <td>0.019</td>
      <td>2.842</td>
      <td>0.881</td>
      <td>NaN</td>
      <td>1.244</td>
      <td>-inf</td>
      <td>inf</td>
      <td>-0.158</td>
    </tr>
    <tr>
      <th>2y</th>
      <td>0.007</td>
      <td>3.124</td>
      <td>0.847</td>
      <td>36.342</td>
      <td>1.402</td>
      <td>12.342</td>
      <td>-10.939</td>
      <td>0.124</td>
    </tr>
    <tr>
      <th>3y</th>
      <td>-0.061</td>
      <td>3.334</td>
      <td>0.808</td>
      <td>NaN</td>
      <td>-0.049</td>
      <td>-inf</td>
      <td>inf</td>
      <td>0.334</td>
    </tr>
    <tr>
      <th>4y</th>
      <td>-0.295</td>
      <td>3.910</td>
      <td>0.778</td>
      <td>19.663</td>
      <td>1.763</td>
      <td>7.212</td>
      <td>-5.449</td>
      <td>0.910</td>
    </tr>
    <tr>
      <th>5y</th>
      <td>-0.907</td>
      <td>5.191</td>
      <td>0.738</td>
      <td>43.272</td>
      <td>2.421</td>
      <td>11.480</td>
      <td>-9.060</td>
      <td>2.191</td>
    </tr>
  </tbody>
</table>
</div>



```python
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Return_Deviation_From_3x"],
    title="TQQQ Deviation from Perfect 3x Leverage by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Deviation from 3x Leverage",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_48_0.png)
    



```python
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Slope"],
    title="TQQQ Slope by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Slope",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_49_0.png)
    



```python
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Intercept"],
    title="Intercept by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Intercept",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_50_0.png)
    



```python
display(rolling_returns_stats.set_index("Period"))
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
      <th>Intercept</th>
      <th>Slope</th>
      <th>R_Squared</th>
      <th>Return Skew</th>
      <th>Average Upside Beta</th>
      <th>Average Downside Beta</th>
      <th>Asymmetry</th>
      <th>Return_Deviation_From_3x</th>
    </tr>
    <tr>
      <th>Period</th>
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
      <th>1d</th>
      <td>-0.000</td>
      <td>2.955</td>
      <td>0.999</td>
      <td>NaN</td>
      <td>2.958</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.045</td>
    </tr>
    <tr>
      <th>1w</th>
      <td>-0.001</td>
      <td>2.953</td>
      <td>0.994</td>
      <td>NaN</td>
      <td>2.557</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.047</td>
    </tr>
    <tr>
      <th>1m</th>
      <td>-0.004</td>
      <td>2.936</td>
      <td>0.982</td>
      <td>NaN</td>
      <td>2.213</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.064</td>
    </tr>
    <tr>
      <th>3m</th>
      <td>-0.008</td>
      <td>2.987</td>
      <td>0.959</td>
      <td>NaN</td>
      <td>1.997</td>
      <td>-inf</td>
      <td>inf</td>
      <td>-0.013</td>
    </tr>
    <tr>
      <th>6m</th>
      <td>-0.010</td>
      <td>3.040</td>
      <td>0.916</td>
      <td>-8.109</td>
      <td>1.482</td>
      <td>5.521</td>
      <td>-4.039</td>
      <td>0.040</td>
    </tr>
    <tr>
      <th>1y</th>
      <td>0.019</td>
      <td>2.842</td>
      <td>0.881</td>
      <td>NaN</td>
      <td>1.244</td>
      <td>-inf</td>
      <td>inf</td>
      <td>-0.158</td>
    </tr>
    <tr>
      <th>2y</th>
      <td>0.007</td>
      <td>3.124</td>
      <td>0.847</td>
      <td>36.342</td>
      <td>1.402</td>
      <td>12.342</td>
      <td>-10.939</td>
      <td>0.124</td>
    </tr>
    <tr>
      <th>3y</th>
      <td>-0.061</td>
      <td>3.334</td>
      <td>0.808</td>
      <td>NaN</td>
      <td>-0.049</td>
      <td>-inf</td>
      <td>inf</td>
      <td>0.334</td>
    </tr>
    <tr>
      <th>4y</th>
      <td>-0.295</td>
      <td>3.910</td>
      <td>0.778</td>
      <td>19.663</td>
      <td>1.763</td>
      <td>7.212</td>
      <td>-5.449</td>
      <td>0.910</td>
    </tr>
    <tr>
      <th>5y</th>
      <td>-0.907</td>
      <td>5.191</td>
      <td>0.738</td>
      <td>43.272</td>
      <td>2.421</td>
      <td>11.480</td>
      <td>-9.060</td>
      <td>2.191</td>
    </tr>
  </tbody>
</table>
</div>


This is very interesting. Up to 1 year, there is minimal difference between the mean TQQQ 1 year rolling return and the hypothetical 3x leverage, with an R^2 of greater than 0.9.

However, as we extend the time period, we see that

* The "leverage factor" increases significantly, resulting in a deviation from the perfect 3x leverage.
* The intercept also begins to deviate significantly from 0.

The above highlight the impact of volatility magnification over longer time horizons. This phenomenon is happening likely due to the positive returns that QQQ has achieved since 2010 - resulting in TQQQ compounding at a much higher rate than 3x - but it may and likely is not exhibited by other 3x leveraged ETFs that have not had the same positive return profile as QQQ.

With the above results, the next logical question is, when is the opportune time to buy a 3x leveraged ETF like TQQQ? To answer this, we will look a the drawdown levels of TQQQ and the subsequent returns over various time horizons.

### Rolling Returns Following Drawdowns (QQQ & TQQQ)

We will identify the drawdown levels of TQQQ and then look at the subsequent rolling returns over various time horizons.


```python
# Copy DataFrame
qqq_tqqq_extrap_future = qqq_tqqq_extrap.copy()

# Create a list of drawdown levels to analyze
drawdown_levels = [-0.10, -0.20, -0.30, -0.40, -0.50, -0.60, -0.70, -0.80, -0.90]

# Shift the rolling return columns by the number of days in the rolling window to get the returns following the drawdown
for etf in etfs:
    for period_name, window in rolling_windows.items():
        qqq_tqqq_extrap_future[f"{etf}_Rolling_Future_Return_{period_name}"] = qqq_tqqq_extrap_future[f"{etf}_Rolling_Return_{period_name}"].shift(-window)
```

Now, we can analyze the future rolling returns following specific drawdown levels:


```python
# Create a dataframe to hold rolling returns stats
rolling_returns_drawdown_stats = pd.DataFrame()

for drawdown in drawdown_levels:

    for period_name, window in rolling_windows.items():

        try:
            plot_histogram(
                df=qqq_tqqq_extrap_future[qqq_tqqq_extrap_future["TQQQ_Drawdown"] <= drawdown],
                plot_columns=[f"QQQ_Rolling_Future_Return_{period_name}", f"TQQQ_Rolling_Future_Return_{period_name}"],
                title=f"QQQ & TQQQ {period_name} Rolling Future Returns Post {drawdown} TQQQ Drawdown",
                x_label="Rolling Return",
                x_tick_spacing="Auto",
                x_tick_rotation=30,
                y_label="# Of Datapoints",
                y_tick_spacing="Auto",
                y_tick_rotation=0,
                grid=True,
                legend=True,
                export_plot=False,
                plot_file_name=None,
            )

            plot_scatter(
                df=qqq_tqqq_extrap_future[qqq_tqqq_extrap_future["TQQQ_Drawdown"] <= drawdown],
                x_plot_column=f"QQQ_Rolling_Future_Return_{period_name}",
                y_plot_columns=[f"TQQQ_Rolling_Future_Return_{period_name}"],
                title=f"QQQ & TQQQ {period_name} Rolling Future Returns Post {drawdown} TQQQ Drawdown",
                x_label="QQQ Rolling Return",
                x_format="Decimal",
                x_format_decimal_places=2,
                x_tick_spacing="Auto",
                x_tick_start=None,
                x_tick_rotation=30,
                y_label="TQQQ Rolling Return",
                y_format="Decimal",
                y_format_decimal_places=2,
                y_tick_spacing="Auto",
                y_tick_rotation=0,
                plot_OLS_regression_line=True,
                OLS_column=f"TQQQ_Rolling_Future_Return_{period_name}",
                plot_Ridge_regression_line=False,
                Ridge_column=None,
                plot_RidgeCV_regression_line=True,
                RidgeCV_column=f"TQQQ_Rolling_Future_Return_{period_name}",
                regression_constant=True,
                grid=True,
                legend=True,
                export_plot=False,
                plot_file_name=None,
            )

            # Run OLS regression with statsmodels
            model = run_regression(
                df=qqq_tqqq_extrap_future[qqq_tqqq_extrap_future["TQQQ_Drawdown"] <= drawdown],
                x_plot_column=f"QQQ_Rolling_Future_Return_{period_name}",
                y_plot_column=f"TQQQ_Rolling_Future_Return_{period_name}",
                regression_model="OLS-statsmodels",
                regression_constant=True,
            )
            print(model.summary())

            # Filter by drawdown
            drawdown_filter = qqq_tqqq_extrap_future[qqq_tqqq_extrap_future["TQQQ_Drawdown"] <= drawdown]

            # Filter by period, drop rows with missing values
            future_filter = drawdown_filter[[f"TQQQ_Rolling_Future_Return_{period_name}"]].dropna()

            # Find length of future dataframe
            future_length = len(future_filter)

            # Find length of future dataframe where return is positive
            positive_future_length = len(future_filter[future_filter[f"TQQQ_Rolling_Future_Return_{period_name}"] > 0])

            # Calculate percentage of future returns that are positive
            positive_future_percentage = (positive_future_length / future_length) if future_length > 0 else 0

            # Add the regression results to the rolling returns stats dataframe
            intercept = model.params.iloc[0]
            # intercept_pvalue = model.pvalues.iloc[0]   # p-value for Intercept
            slope = model.params.iloc[1]
            # slope_pvalue = model.pvalues.iloc[1]       # p-value for Slope
            r_squared = model.rsquared

            rolling_returns_slope_int = pd.DataFrame({
                "Drawdown": drawdown,
                "Period": period_name,
                "Intercept": [intercept],
                # "Intercept_PValue": [intercept_pvalue],
                "Slope": [slope],
                # "Slope_PValue": [slope_pvalue],
                "R_Squared": [r_squared],
                "Positive_Future_Percentage": [positive_future_percentage],
            })
            
            rolling_returns_drawdown_stats = pd.concat([rolling_returns_drawdown_stats, rolling_returns_slope_int])

        except:
            print(f"Not enough data points for drawdown level {drawdown} and period {period_name} to run regression.")
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_0.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_1.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1d   R-squared:                       0.999
    Model:                                       OLS   Adj. R-squared:                  0.999
    Method:                            Least Squares   F-statistic:                 6.911e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:32:36   Log-Likelihood:                 33887.
    No. Observations:                           6713   AIC:                        -6.777e+04
    Df Residuals:                               6711   BIC:                        -6.776e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                        -5.384e-05    1.9e-05     -2.837      0.005    -9.1e-05   -1.66e-05
    QQQ_Rolling_Future_Return_1d     2.9553      0.001   2628.911      0.000       2.953       2.957
    ==============================================================================
    Omnibus:                    10002.255   Durbin-Watson:                   2.566
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         41625835.132
    Skew:                          -8.172   Prob(JB):                         0.00
    Kurtosis:                     388.424   Cond. No.                         59.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_3.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_4.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 1.107e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:32:39   Log-Likelihood:                 22953.
    No. Observations:                           6709   AIC:                        -4.590e+04
    Df Residuals:                               6707   BIC:                        -4.589e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0008   9.68e-05     -8.295      0.000      -0.001      -0.001
    QQQ_Rolling_Future_Return_1w     2.9534      0.003   1052.034      0.000       2.948       2.959
    ==============================================================================
    Omnibus:                     2724.426   Durbin-Watson:                   0.939
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           599408.005
    Skew:                          -0.772   Prob(JB):                         0.00
    Kurtosis:                      49.280   Cond. No.                         29.1
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_6.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_7.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1m   R-squared:                       0.982
    Model:                                       OLS   Adj. R-squared:                  0.982
    Method:                            Least Squares   F-statistic:                 3.756e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:32:43   Log-Likelihood:                 14814.
    No. Observations:                           6693   AIC:                        -2.962e+04
    Df Residuals:                               6691   BIC:                        -2.961e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0034      0.000    -10.258      0.000      -0.004      -0.003
    QQQ_Rolling_Future_Return_1m     2.9366      0.005    612.886      0.000       2.927       2.946
    ==============================================================================
    Omnibus:                     1708.914   Durbin-Watson:                   0.308
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            79259.198
    Skew:                           0.422   Prob(JB):                         0.00
    Kurtosis:                      19.837   Cond. No.                         14.8
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_9.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_10.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3m   R-squared:                       0.957
    Model:                                       OLS   Adj. R-squared:                  0.957
    Method:                            Least Squares   F-statistic:                 1.486e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:32:47   Log-Likelihood:                 8047.1
    No. Observations:                           6651   AIC:                        -1.609e+04
    Df Residuals:                               6649   BIC:                        -1.608e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0076      0.001     -8.388      0.000      -0.009      -0.006
    QQQ_Rolling_Future_Return_3m     2.9610      0.008    385.431      0.000       2.946       2.976
    ==============================================================================
    Omnibus:                     3434.679   Durbin-Watson:                   0.113
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            87217.860
    Skew:                           1.941   Prob(JB):                         0.00
    Kurtosis:                      20.310   Cond. No.                         8.69
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_12.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_13.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_6m   R-squared:                       0.921
    Model:                                       OLS   Adj. R-squared:                  0.921
    Method:                            Least Squares   F-statistic:                 7.644e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:32:50   Log-Likelihood:                 3210.4
    No. Observations:                           6588   AIC:                            -6417.
    Df Residuals:                               6586   BIC:                            -6403.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0048      0.002     -2.481      0.013      -0.009      -0.001
    QQQ_Rolling_Future_Return_6m     2.9627      0.011    276.474      0.000       2.942       2.984
    ==============================================================================
    Omnibus:                     4217.455   Durbin-Watson:                   0.065
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           103404.384
    Skew:                           2.663   Prob(JB):                         0.00
    Kurtosis:                      21.664   Cond. No.                         5.87
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_15.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_16.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1y   R-squared:                       0.894
    Model:                                       OLS   Adj. R-squared:                  0.894
    Method:                            Least Squares   F-statistic:                 5.421e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:32:54   Log-Likelihood:                -123.96
    No. Observations:                           6462   AIC:                             251.9
    Df Residuals:                               6460   BIC:                             265.5
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0229      0.003      6.693      0.000       0.016       0.030
    QQQ_Rolling_Future_Return_1y     2.8138      0.012    232.837      0.000       2.790       2.838
    ==============================================================================
    Omnibus:                     2629.651   Durbin-Watson:                   0.052
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            28944.026
    Skew:                           1.637   Prob(JB):                         0.00
    Kurtosis:                      12.837   Cond. No.                         4.00
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_18.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_19.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_2y   R-squared:                       0.847
    Model:                                       OLS   Adj. R-squared:                  0.847
    Method:                            Least Squares   F-statistic:                 3.430e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:32:57   Log-Likelihood:                -4303.6
    No. Observations:                           6210   AIC:                             8611.
    Df Residuals:                               6208   BIC:                             8625.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0215      0.008     -2.822      0.005      -0.036      -0.007
    QQQ_Rolling_Future_Return_2y     3.1933      0.017    185.210      0.000       3.159       3.227
    ==============================================================================
    Omnibus:                     1695.855   Durbin-Watson:                   0.019
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4735.104
    Skew:                           1.441   Prob(JB):                         0.00
    Kurtosis:                       6.161   Cond. No.                         3.03
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_21.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_22.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3y   R-squared:                       0.814
    Model:                                       OLS   Adj. R-squared:                  0.814
    Method:                            Least Squares   F-statistic:                 2.606e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:01   Log-Likelihood:                -6413.7
    No. Observations:                           5958   AIC:                         1.283e+04
    Df Residuals:                               5956   BIC:                         1.284e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1595      0.013    -12.233      0.000      -0.185      -0.134
    QQQ_Rolling_Future_Return_3y     3.5008      0.022    161.442      0.000       3.458       3.543
    ==============================================================================
    Omnibus:                      890.338   Durbin-Watson:                   0.015
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1586.185
    Skew:                           0.965   Prob(JB):                         0.00
    Kurtosis:                       4.632   Cond. No.                         2.86
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_24.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_25.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_4y   R-squared:                       0.779
    Model:                                       OLS   Adj. R-squared:                  0.779
    Method:                            Least Squares   F-statistic:                 2.015e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:06   Log-Likelihood:                -8622.3
    No. Observations:                           5706   AIC:                         1.725e+04
    Df Residuals:                               5704   BIC:                         1.726e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.4278      0.023    -18.865      0.000      -0.472      -0.383
    QQQ_Rolling_Future_Return_4y     4.0704      0.029    141.956      0.000       4.014       4.127
    ==============================================================================
    Omnibus:                      148.305   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               90.147
    Skew:                           0.162   Prob(JB):                     2.66e-20
    Kurtosis:                       2.476   Cond. No.                         2.86
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_27.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_28.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_5y   R-squared:                       0.741
    Model:                                       OLS   Adj. R-squared:                  0.741
    Method:                            Least Squares   F-statistic:                 1.558e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:11   Log-Likelihood:                -11885.
    No. Observations:                           5454   AIC:                         2.377e+04
    Df Residuals:                               5452   BIC:                         2.379e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.1362      0.047    -24.162      0.000      -1.228      -1.044
    QQQ_Rolling_Future_Return_5y     5.3839      0.043    124.822      0.000       5.299       5.469
    ==============================================================================
    Omnibus:                      283.895   Durbin-Watson:                   0.009
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              407.097
    Skew:                           0.473   Prob(JB):                     3.98e-89
    Kurtosis:                       3.946   Cond. No.                         2.92
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_30.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_31.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1d   R-squared:                       0.999
    Model:                                       OLS   Adj. R-squared:                  0.999
    Method:                            Least Squares   F-statistic:                 6.673e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:15   Log-Likelihood:                 33428.
    No. Observations:                           6630   AIC:                        -6.685e+04
    Df Residuals:                               6628   BIC:                        -6.684e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                        -5.435e-05   1.92e-05     -2.829      0.005    -9.2e-05   -1.67e-05
    QQQ_Rolling_Future_Return_1d     2.9552      0.001   2583.241      0.000       2.953       2.957
    ==============================================================================
    Omnibus:                     9847.883   Durbin-Watson:                   2.566
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         40121425.142
    Skew:                          -8.123   Prob(JB):                         0.00
    Kurtosis:                     383.752   Cond. No.                         59.6
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_33.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_34.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 1.085e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:19   Log-Likelihood:                 22679.
    No. Observations:                           6627   AIC:                        -4.535e+04
    Df Residuals:                               6625   BIC:                        -4.534e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0008   9.73e-05     -8.044      0.000      -0.001      -0.001
    QQQ_Rolling_Future_Return_1w     2.9524      0.003   1041.850      0.000       2.947       2.958
    ==============================================================================
    Omnibus:                     2728.411   Durbin-Watson:                   0.932
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           607972.381
    Skew:                          -0.798   Prob(JB):                         0.00
    Kurtosis:                      49.896   Cond. No.                         29.2
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_36.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_37.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1m   R-squared:                       0.983
    Model:                                       OLS   Adj. R-squared:                  0.983
    Method:                            Least Squares   F-statistic:                 3.754e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:22   Log-Likelihood:                 14767.
    No. Observations:                           6616   AIC:                        -2.953e+04
    Df Residuals:                               6614   BIC:                        -2.952e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0034      0.000    -10.499      0.000      -0.004      -0.003
    QQQ_Rolling_Future_Return_1m     2.9290      0.005    612.735      0.000       2.920       2.938
    ==============================================================================
    Omnibus:                     1557.724   Durbin-Watson:                   0.313
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            79422.712
    Skew:                           0.204   Prob(JB):                         0.00
    Kurtosis:                      19.969   Cond. No.                         15.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_39.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_40.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3m   R-squared:                       0.960
    Model:                                       OLS   Adj. R-squared:                  0.960
    Method:                            Least Squares   F-statistic:                 1.573e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:27   Log-Likelihood:                 8421.1
    No. Observations:                           6574   AIC:                        -1.684e+04
    Df Residuals:                               6572   BIC:                        -1.682e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0071      0.001     -8.281      0.000      -0.009      -0.005
    QQQ_Rolling_Future_Return_3m     2.9138      0.007    396.593      0.000       2.899       2.928
    ==============================================================================
    Omnibus:                     2170.483   Durbin-Watson:                   0.136
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            39171.367
    Skew:                           1.112   Prob(JB):                         0.00
    Kurtosis:                      14.750   Cond. No.                         8.87
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_42.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_43.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_6m   R-squared:                       0.926
    Model:                                       OLS   Adj. R-squared:                  0.926
    Method:                            Least Squares   F-statistic:                 8.187e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:30   Log-Likelihood:                 3840.6
    No. Observations:                           6511   AIC:                            -7677.
    Df Residuals:                               6509   BIC:                            -7664.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0021      0.002     -1.215      0.224      -0.006       0.001
    QQQ_Rolling_Future_Return_6m     2.8746      0.010    286.133      0.000       2.855       2.894
    ==============================================================================
    Omnibus:                     3235.775   Durbin-Watson:                   0.076
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            51105.740
    Skew:                           1.991   Prob(JB):                         0.00
    Kurtosis:                      16.135   Cond. No.                         6.06
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_45.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_46.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1y   R-squared:                       0.899
    Model:                                       OLS   Adj. R-squared:                  0.899
    Method:                            Least Squares   F-statistic:                 5.654e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:34   Log-Likelihood:                 129.52
    No. Observations:                           6385   AIC:                            -255.0
    Df Residuals:                               6383   BIC:                            -241.5
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0227      0.003      6.858      0.000       0.016       0.029
    QQQ_Rolling_Future_Return_1y     2.8392      0.012    237.784      0.000       2.816       2.863
    ==============================================================================
    Omnibus:                     2422.758   Durbin-Watson:                   0.068
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            19269.888
    Skew:                           1.604   Prob(JB):                         0.00
    Kurtosis:                      10.883   Cond. No.                         4.09
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_48.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_49.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_2y   R-squared:                       0.846
    Model:                                       OLS   Adj. R-squared:                  0.846
    Method:                            Least Squares   F-statistic:                 3.369e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:39   Log-Likelihood:                -4224.9
    No. Observations:                           6133   AIC:                             8454.
    Df Residuals:                               6131   BIC:                             8467.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0315      0.008     -4.051      0.000      -0.047      -0.016
    QQQ_Rolling_Future_Return_2y     3.2194      0.018    183.536      0.000       3.185       3.254
    ==============================================================================
    Omnibus:                     1720.128   Durbin-Watson:                   0.019
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4955.786
    Skew:                           1.467   Prob(JB):                         0.00
    Kurtosis:                       6.284   Cond. No.                         3.09
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_51.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_52.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3y   R-squared:                       0.817
    Model:                                       OLS   Adj. R-squared:                  0.817
    Method:                            Least Squares   F-statistic:                 2.632e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:42   Log-Likelihood:                -6236.8
    No. Observations:                           5881   AIC:                         1.248e+04
    Df Residuals:                               5879   BIC:                         1.249e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2171      0.013    -16.283      0.000      -0.243      -0.191
    QQQ_Rolling_Future_Return_3y     3.5972      0.022    162.238      0.000       3.554       3.641
    ==============================================================================
    Omnibus:                      898.619   Durbin-Watson:                   0.015
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1636.684
    Skew:                           0.974   Prob(JB):                         0.00
    Kurtosis:                       4.699   Cond. No.                         2.98
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_54.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_55.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_4y   R-squared:                       0.780
    Model:                                       OLS   Adj. R-squared:                  0.780
    Method:                            Least Squares   F-statistic:                 1.998e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:46   Log-Likelihood:                -8466.9
    No. Observations:                           5629   AIC:                         1.694e+04
    Df Residuals:                               5627   BIC:                         1.695e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.5060      0.023    -21.632      0.000      -0.552      -0.460
    QQQ_Rolling_Future_Return_4y     4.1639      0.029    141.365      0.000       4.106       4.222
    ==============================================================================
    Omnibus:                      110.238   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               75.087
    Skew:                           0.165   Prob(JB):                     4.95e-17
    Kurtosis:                       2.541   Cond. No.                         2.97
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_57.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_58.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_5y   R-squared:                       0.742
    Model:                                       OLS   Adj. R-squared:                  0.742
    Method:                            Least Squares   F-statistic:                 1.547e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:51   Log-Likelihood:                -11697.
    No. Observations:                           5377   AIC:                         2.340e+04
    Df Residuals:                               5375   BIC:                         2.341e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.2669      0.048    -26.156      0.000      -1.362      -1.172
    QQQ_Rolling_Future_Return_5y     5.4927      0.044    124.366      0.000       5.406       5.579
    ==============================================================================
    Omnibus:                      263.633   Durbin-Watson:                   0.009
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              380.037
    Skew:                           0.451   Prob(JB):                     2.99e-83
    Kurtosis:                       3.939   Cond. No.                         3.02
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_60.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_61.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1d   R-squared:                       0.999
    Model:                                       OLS   Adj. R-squared:                  0.999
    Method:                            Least Squares   F-statistic:                 6.487e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:55   Log-Likelihood:                 33121.
    No. Observations:                           6574   AIC:                        -6.624e+04
    Df Residuals:                               6572   BIC:                        -6.622e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                        -5.443e-05   1.94e-05     -2.811      0.005   -9.24e-05   -1.65e-05
    QQQ_Rolling_Future_Return_1d     2.9553      0.001   2546.890      0.000       2.953       2.958
    ==============================================================================
    Omnibus:                     9750.662   Durbin-Watson:                   2.564
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         39259436.337
    Skew:                          -8.100   Prob(JB):                         0.00
    Kurtosis:                     381.238   Cond. No.                         59.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_63.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_64.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 1.133e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:33:59   Log-Likelihood:                 22693.
    No. Observations:                           6573   AIC:                        -4.538e+04
    Df Residuals:                               6571   BIC:                        -4.537e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0008   9.47e-05     -8.330      0.000      -0.001      -0.001
    QQQ_Rolling_Future_Return_1w     2.9560      0.003   1064.455      0.000       2.951       2.961
    ==============================================================================
    Omnibus:                     3486.989   Durbin-Watson:                   0.902
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           393847.121
    Skew:                          -1.577   Prob(JB):                         0.00
    Kurtosis:                      40.790   Cond. No.                         29.4
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_66.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_67.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1m   R-squared:                       0.983
    Model:                                       OLS   Adj. R-squared:                  0.983
    Method:                            Least Squares   F-statistic:                 3.724e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:02   Log-Likelihood:                 14721.
    No. Observations:                           6570   AIC:                        -2.944e+04
    Df Residuals:                               6568   BIC:                        -2.943e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0034      0.000    -10.644      0.000      -0.004      -0.003
    QQQ_Rolling_Future_Return_1m     2.9245      0.005    610.236      0.000       2.915       2.934
    ==============================================================================
    Omnibus:                     1526.763   Durbin-Watson:                   0.304
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            80156.566
    Skew:                           0.132   Prob(JB):                         0.00
    Kurtosis:                      20.110   Cond. No.                         15.1
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_69.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_70.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3m   R-squared:                       0.961
    Model:                                       OLS   Adj. R-squared:                  0.961
    Method:                            Least Squares   F-statistic:                 1.614e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:06   Log-Likelihood:                 8557.4
    No. Observations:                           6534   AIC:                        -1.711e+04
    Df Residuals:                               6532   BIC:                        -1.710e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0068      0.001     -8.136      0.000      -0.008      -0.005
    QQQ_Rolling_Future_Return_3m     2.8980      0.007    401.740      0.000       2.884       2.912
    ==============================================================================
    Omnibus:                     1370.505   Durbin-Watson:                   0.103
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            15604.976
    Skew:                           0.673   Prob(JB):                         0.00
    Kurtosis:                      10.450   Cond. No.                         8.93
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_72.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_73.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_6m   R-squared:                       0.929
    Model:                                       OLS   Adj. R-squared:                  0.929
    Method:                            Least Squares   F-statistic:                 8.467e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:10   Log-Likelihood:                 4192.8
    No. Observations:                           6471   AIC:                            -8382.
    Df Residuals:                               6469   BIC:                            -8368.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0011      0.002     -0.693      0.488      -0.004       0.002
    QQQ_Rolling_Future_Return_6m     2.8227      0.010    290.977      0.000       2.804       2.842
    ==============================================================================
    Omnibus:                     2729.155   Durbin-Watson:                   0.109
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            37443.267
    Skew:                           1.642   Prob(JB):                         0.00
    Kurtosis:                      14.318   Cond. No.                         6.18
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_75.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_76.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1y   R-squared:                       0.902
    Model:                                       OLS   Adj. R-squared:                  0.902
    Method:                            Least Squares   F-statistic:                 5.862e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:14   Log-Likelihood:                 306.92
    No. Observations:                           6345   AIC:                            -609.8
    Df Residuals:                               6343   BIC:                            -596.3
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0223      0.003      6.928      0.000       0.016       0.029
    QQQ_Rolling_Future_Return_1y     2.8563      0.012    242.124      0.000       2.833       2.879
    ==============================================================================
    Omnibus:                     1986.105   Durbin-Watson:                   0.043
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8512.500
    Skew:                           1.479   Prob(JB):                         0.00
    Kurtosis:                       7.842   Cond. No.                         4.14
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_78.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_79.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_2y   R-squared:                       0.846
    Model:                                       OLS   Adj. R-squared:                  0.846
    Method:                            Least Squares   F-statistic:                 3.335e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:18   Log-Likelihood:                -4185.3
    No. Observations:                           6093   AIC:                             8375.
    Df Residuals:                               6091   BIC:                             8388.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0344      0.008     -4.390      0.000      -0.050      -0.019
    QQQ_Rolling_Future_Return_2y     3.2283      0.018    182.610      0.000       3.194       3.263
    ==============================================================================
    Omnibus:                     1727.215   Durbin-Watson:                   0.019
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5044.840
    Skew:                           1.477   Prob(JB):                         0.00
    Kurtosis:                       6.338   Cond. No.                         3.11
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_81.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_82.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3y   R-squared:                       0.820
    Model:                                       OLS   Adj. R-squared:                  0.819
    Method:                            Least Squares   F-statistic:                 2.651e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:22   Log-Likelihood:                -6139.3
    No. Observations:                           5841   AIC:                         1.228e+04
    Df Residuals:                               5839   BIC:                         1.230e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2500      0.013    -18.534      0.000      -0.276      -0.224
    QQQ_Rolling_Future_Return_3y     3.6520      0.022    162.821      0.000       3.608       3.696
    ==============================================================================
    Omnibus:                      902.038   Durbin-Watson:                   0.015
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1667.762
    Skew:                           0.976   Prob(JB):                         0.00
    Kurtosis:                       4.744   Cond. No.                         3.04
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_84.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_85.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_4y   R-squared:                       0.781
    Model:                                       OLS   Adj. R-squared:                  0.781
    Method:                            Least Squares   F-statistic:                 1.990e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:25   Log-Likelihood:                -8384.8
    No. Observations:                           5589   AIC:                         1.677e+04
    Df Residuals:                               5587   BIC:                         1.679e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.5491      0.024    -23.091      0.000      -0.596      -0.503
    QQQ_Rolling_Future_Return_4y     4.2152      0.030    141.074      0.000       4.157       4.274
    ==============================================================================
    Omnibus:                       91.895   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               66.824
    Skew:                           0.167   Prob(JB):                     3.09e-15
    Kurtosis:                       2.581   Cond. No.                         3.03
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_87.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_88.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_5y   R-squared:                       0.743
    Model:                                       OLS   Adj. R-squared:                  0.743
    Method:                            Least Squares   F-statistic:                 1.541e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:29   Log-Likelihood:                -11599.
    No. Observations:                           5337   AIC:                         2.320e+04
    Df Residuals:                               5335   BIC:                         2.321e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.3392      0.049    -27.216      0.000      -1.436      -1.243
    QQQ_Rolling_Future_Return_5y     5.5527      0.045    124.156      0.000       5.465       5.640
    ==============================================================================
    Omnibus:                      252.830   Durbin-Watson:                   0.009
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              366.376
    Skew:                           0.438   Prob(JB):                     2.77e-80
    Kurtosis:                       3.938   Cond. No.                         3.07
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_90.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_91.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1d   R-squared:                       0.999
    Model:                                       OLS   Adj. R-squared:                  0.999
    Method:                            Least Squares   F-statistic:                 6.423e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:33   Log-Likelihood:                 33007.
    No. Observations:                           6553   AIC:                        -6.601e+04
    Df Residuals:                               6551   BIC:                        -6.600e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         -5.37e-05   1.94e-05     -2.765      0.006   -9.18e-05   -1.56e-05
    QQQ_Rolling_Future_Return_1d     2.9553      0.001   2534.297      0.000       2.953       2.958
    ==============================================================================
    Omnibus:                     9718.348   Durbin-Watson:                   2.566
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         39023258.345
    Skew:                          -8.099   Prob(JB):                         0.00
    Kurtosis:                     380.701   Cond. No.                         60.1
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_93.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_94.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 1.129e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:38   Log-Likelihood:                 22667.
    No. Observations:                           6553   AIC:                        -4.533e+04
    Df Residuals:                               6551   BIC:                        -4.532e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0008   9.42e-05     -8.569      0.000      -0.001      -0.001
    QQQ_Rolling_Future_Return_1w     2.9541      0.003   1062.729      0.000       2.949       2.960
    ==============================================================================
    Omnibus:                     3613.538   Durbin-Watson:                   0.881
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           408611.855
    Skew:                          -1.685   Prob(JB):                         0.00
    Kurtosis:                      41.538   Cond. No.                         29.6
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_96.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_97.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1m   R-squared:                       0.983
    Model:                                       OLS   Adj. R-squared:                  0.983
    Method:                            Least Squares   F-statistic:                 3.704e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:43   Log-Likelihood:                 14702.
    No. Observations:                           6553   AIC:                        -2.940e+04
    Df Residuals:                               6551   BIC:                        -2.939e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0034      0.000    -10.643      0.000      -0.004      -0.003
    QQQ_Rolling_Future_Return_1m     2.9216      0.005    608.577      0.000       2.912       2.931
    ==============================================================================
    Omnibus:                     1521.866   Durbin-Watson:                   0.293
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            80945.795
    Skew:                           0.112   Prob(JB):                         0.00
    Kurtosis:                      20.217   Cond. No.                         15.1
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_99.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_100.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3m   R-squared:                       0.961
    Model:                                       OLS   Adj. R-squared:                  0.961
    Method:                            Least Squares   F-statistic:                 1.620e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:47   Log-Likelihood:                 8571.4
    No. Observations:                           6523   AIC:                        -1.714e+04
    Df Residuals:                               6521   BIC:                        -1.713e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0066      0.001     -7.965      0.000      -0.008      -0.005
    QQQ_Rolling_Future_Return_3m     2.8962      0.007    402.551      0.000       2.882       2.910
    ==============================================================================
    Omnibus:                     1401.017   Durbin-Watson:                   0.101
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            15929.868
    Skew:                           0.699   Prob(JB):                         0.00
    Kurtosis:                      10.527   Cond. No.                         8.94
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_102.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_103.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_6m   R-squared:                       0.931
    Model:                                       OLS   Adj. R-squared:                  0.931
    Method:                            Least Squares   F-statistic:                 8.747e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:51   Log-Likelihood:                 4370.9
    No. Observations:                           6460   AIC:                            -8738.
    Df Residuals:                               6458   BIC:                            -8724.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0006      0.002     -0.363      0.717      -0.004       0.003
    QQQ_Rolling_Future_Return_6m     2.8041      0.009    295.754      0.000       2.786       2.823
    ==============================================================================
    Omnibus:                     1674.962   Durbin-Watson:                   0.057
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8401.998
    Skew:                           1.159   Prob(JB):                         0.00
    Kurtosis:                       8.084   Cond. No.                         6.21
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_105.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_106.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1y   R-squared:                       0.903
    Model:                                       OLS   Adj. R-squared:                  0.903
    Method:                            Least Squares   F-statistic:                 5.905e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:55   Log-Likelihood:                 341.65
    No. Observations:                           6334   AIC:                            -679.3
    Df Residuals:                               6332   BIC:                            -665.8
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0210      0.003      6.538      0.000       0.015       0.027
    QQQ_Rolling_Future_Return_1y     2.8665      0.012    242.992      0.000       2.843       2.890
    ==============================================================================
    Omnibus:                     1983.991   Durbin-Watson:                   0.040
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8504.663
    Skew:                           1.480   Prob(JB):                         0.00
    Kurtosis:                       7.844   Cond. No.                         4.16
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_108.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_109.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_2y   R-squared:                       0.846
    Model:                                       OLS   Adj. R-squared:                  0.846
    Method:                            Least Squares   F-statistic:                 3.336e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:34:59   Log-Likelihood:                -4165.6
    No. Observations:                           6082   AIC:                             8335.
    Df Residuals:                               6080   BIC:                             8349.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0372      0.008     -4.736      0.000      -0.053      -0.022
    QQQ_Rolling_Future_Return_2y     3.2356      0.018    182.653      0.000       3.201       3.270
    ==============================================================================
    Omnibus:                     1735.957   Durbin-Watson:                   0.018
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5121.189
    Skew:                           1.483   Prob(JB):                         0.00
    Kurtosis:                       6.378   Cond. No.                         3.12
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_111.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_112.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3y   R-squared:                       0.821
    Model:                                       OLS   Adj. R-squared:                  0.821
    Method:                            Least Squares   F-statistic:                 2.666e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:04   Log-Likelihood:                -6103.9
    No. Observations:                           5830   AIC:                         1.221e+04
    Df Residuals:                               5828   BIC:                         1.223e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2615      0.014    -19.338      0.000      -0.288      -0.235
    QQQ_Rolling_Future_Return_3y     3.6714      0.022    163.272      0.000       3.627       3.715
    ==============================================================================
    Omnibus:                      895.755   Durbin-Watson:                   0.015
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1658.417
    Skew:                           0.971   Prob(JB):                         0.00
    Kurtosis:                       4.748   Cond. No.                         3.06
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_114.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_115.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_4y   R-squared:                       0.781
    Model:                                       OLS   Adj. R-squared:                  0.781
    Method:                            Least Squares   F-statistic:                 1.992e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:08   Log-Likelihood:                -8358.0
    No. Observations:                           5578   AIC:                         1.672e+04
    Df Residuals:                               5576   BIC:                         1.673e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.5638      0.024    -23.606      0.000      -0.611      -0.517
    QQQ_Rolling_Future_Return_4y     4.2329      0.030    141.127      0.000       4.174       4.292
    ==============================================================================
    Omnibus:                       86.160   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               63.664
    Skew:                           0.165   Prob(JB):                     1.50e-14
    Kurtosis:                       2.593   Cond. No.                         3.05
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_117.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_118.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_5y   R-squared:                       0.743
    Model:                                       OLS   Adj. R-squared:                  0.743
    Method:                            Least Squares   F-statistic:                 1.543e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:12   Log-Likelihood:                -11568.
    No. Observations:                           5326   AIC:                         2.314e+04
    Df Residuals:                               5324   BIC:                         2.315e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.3642      0.049    -27.608      0.000      -1.461      -1.267
    QQQ_Rolling_Future_Return_5y     5.5737      0.045    124.205      0.000       5.486       5.662
    ==============================================================================
    Omnibus:                      248.125   Durbin-Watson:                   0.009
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              360.908
    Skew:                           0.432   Prob(JB):                     4.26e-79
    Kurtosis:                       3.938   Cond. No.                         3.09
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_120.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_121.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1d   R-squared:                       0.999
    Model:                                       OLS   Adj. R-squared:                  0.999
    Method:                            Least Squares   F-statistic:                 6.278e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:16   Log-Likelihood:                 32614.
    No. Observations:                           6480   AIC:                        -6.522e+04
    Df Residuals:                               6478   BIC:                        -6.521e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         -4.98e-05   1.96e-05     -2.540      0.011   -8.82e-05   -1.14e-05
    QQQ_Rolling_Future_Return_1d     2.9551      0.001   2505.632      0.000       2.953       2.957
    ==============================================================================
    Omnibus:                     9606.715   Durbin-Watson:                   2.568
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         38196819.425
    Skew:                          -8.095   Prob(JB):                         0.00
    Kurtosis:                     378.776   Cond. No.                         60.2
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_123.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_124.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 1.118e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:20   Log-Likelihood:                 22412.
    No. Observations:                           6480   AIC:                        -4.482e+04
    Df Residuals:                               6478   BIC:                        -4.481e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0008   9.48e-05     -8.165      0.000      -0.001      -0.001
    QQQ_Rolling_Future_Return_1w     2.9535      0.003   1057.400      0.000       2.948       2.959
    ==============================================================================
    Omnibus:                     3552.509   Durbin-Watson:                   0.887
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           405301.538
    Skew:                          -1.666   Prob(JB):                         0.00
    Kurtosis:                      41.601   Cond. No.                         29.5
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_126.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_127.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1m   R-squared:                       0.983
    Model:                                       OLS   Adj. R-squared:                  0.983
    Method:                            Least Squares   F-statistic:                 3.642e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:24   Log-Likelihood:                 14518.
    No. Observations:                           6480   AIC:                        -2.903e+04
    Df Residuals:                               6478   BIC:                        -2.902e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0033      0.000    -10.350      0.000      -0.004      -0.003
    QQQ_Rolling_Future_Return_1m     2.9199      0.005    603.449      0.000       2.910       2.929
    ==============================================================================
    Omnibus:                     1498.953   Durbin-Watson:                   0.292
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            79274.697
    Skew:                           0.099   Prob(JB):                         0.00
    Kurtosis:                      20.134   Cond. No.                         15.1
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_129.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_130.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3m   R-squared:                       0.961
    Model:                                       OLS   Adj. R-squared:                  0.961
    Method:                            Least Squares   F-statistic:                 1.611e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:28   Log-Likelihood:                 8483.0
    No. Observations:                           6462   AIC:                        -1.696e+04
    Df Residuals:                               6460   BIC:                        -1.695e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0062      0.001     -7.423      0.000      -0.008      -0.005
    QQQ_Rolling_Future_Return_3m     2.8955      0.007    401.360      0.000       2.881       2.910
    ==============================================================================
    Omnibus:                     1385.700   Durbin-Watson:                   0.101
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            15646.097
    Skew:                           0.699   Prob(JB):                         0.00
    Kurtosis:                      10.494   Cond. No.                         8.91
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_132.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_133.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_6m   R-squared:                       0.931
    Model:                                       OLS   Adj. R-squared:                  0.931
    Method:                            Least Squares   F-statistic:                 8.720e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:32   Log-Likelihood:                 4343.3
    No. Observations:                           6424   AIC:                            -8683.
    Df Residuals:                               6422   BIC:                            -8669.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0002      0.002     -0.130      0.897      -0.003       0.003
    QQQ_Rolling_Future_Return_6m     2.8045      0.009    295.300      0.000       2.786       2.823
    ==============================================================================
    Omnibus:                     1672.145   Durbin-Watson:                   0.055
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8272.538
    Skew:                           1.168   Prob(JB):                         0.00
    Kurtosis:                       8.045   Cond. No.                         6.20
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_135.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_136.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1y   R-squared:                       0.903
    Model:                                       OLS   Adj. R-squared:                  0.903
    Method:                            Least Squares   F-statistic:                 5.911e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:38   Log-Likelihood:                 349.34
    No. Observations:                           6331   AIC:                            -694.7
    Df Residuals:                               6329   BIC:                            -681.2
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0205      0.003      6.376      0.000       0.014       0.027
    QQQ_Rolling_Future_Return_1y     2.8691      0.012    243.131      0.000       2.846       2.892
    ==============================================================================
    Omnibus:                     1982.778   Durbin-Watson:                   0.038
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8522.330
    Skew:                           1.479   Prob(JB):                         0.00
    Kurtosis:                       7.854   Cond. No.                         4.16
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_138.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_139.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_2y   R-squared:                       0.846
    Model:                                       OLS   Adj. R-squared:                  0.846
    Method:                            Least Squares   F-statistic:                 3.339e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:42   Log-Likelihood:                -4158.4
    No. Observations:                           6079   AIC:                             8321.
    Df Residuals:                               6077   BIC:                             8334.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0387      0.008     -4.920      0.000      -0.054      -0.023
    QQQ_Rolling_Future_Return_2y     3.2392      0.018    182.723      0.000       3.204       3.274
    ==============================================================================
    Omnibus:                     1741.033   Durbin-Watson:                   0.018
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5160.249
    Skew:                           1.487   Prob(JB):                         0.00
    Kurtosis:                       6.396   Cond. No.                         3.13
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_141.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_142.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3y   R-squared:                       0.821
    Model:                                       OLS   Adj. R-squared:                  0.821
    Method:                            Least Squares   F-statistic:                 2.673e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:46   Log-Likelihood:                -6091.1
    No. Observations:                           5827   AIC:                         1.219e+04
    Df Residuals:                               5825   BIC:                         1.220e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2656      0.014    -19.632      0.000      -0.292      -0.239
    QQQ_Rolling_Future_Return_3y     3.6783      0.022    163.500      0.000       3.634       3.722
    ==============================================================================
    Omnibus:                      892.642   Durbin-Watson:                   0.015
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1653.181
    Skew:                           0.968   Prob(JB):                         0.00
    Kurtosis:                       4.749   Cond. No.                         3.07
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_144.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_145.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_4y   R-squared:                       0.782
    Model:                                       OLS   Adj. R-squared:                  0.781
    Method:                            Least Squares   F-statistic:                 1.993e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:50   Log-Likelihood:                -8349.3
    No. Observations:                           5575   AIC:                         1.670e+04
    Df Residuals:                               5573   BIC:                         1.672e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.5688      0.024    -23.786      0.000      -0.616      -0.522
    QQQ_Rolling_Future_Return_4y     4.2389      0.030    141.186      0.000       4.180       4.298
    ==============================================================================
    Omnibus:                       84.267   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               62.495
    Skew:                           0.163   Prob(JB):                     2.69e-14
    Kurtosis:                       2.597   Cond. No.                         3.06
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_147.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_148.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_5y   R-squared:                       0.744
    Model:                                       OLS   Adj. R-squared:                  0.744
    Method:                            Least Squares   F-statistic:                 1.544e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:55   Log-Likelihood:                -11558.
    No. Observations:                           5323   AIC:                         2.312e+04
    Df Residuals:                               5321   BIC:                         2.313e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.3730      0.049    -27.756      0.000      -1.470      -1.276
    QQQ_Rolling_Future_Return_5y     5.5813      0.045    124.262      0.000       5.493       5.669
    ==============================================================================
    Omnibus:                      246.200   Durbin-Watson:                   0.009
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              358.803
    Skew:                           0.429   Prob(JB):                     1.22e-78
    Kurtosis:                       3.939   Cond. No.                         3.09
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_150.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_151.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1d   R-squared:                       0.999
    Model:                                       OLS   Adj. R-squared:                  0.999
    Method:                            Least Squares   F-statistic:                 6.009e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:35:59   Log-Likelihood:                 31565.
    No. Observations:                           6286   AIC:                        -6.313e+04
    Df Residuals:                               6284   BIC:                        -6.311e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                        -4.276e-05   2.01e-05     -2.123      0.034   -8.22e-05   -3.27e-06
    QQQ_Rolling_Future_Return_1d     2.9548      0.001   2451.416      0.000       2.952       2.957
    ==============================================================================
    Omnibus:                     9298.069   Durbin-Watson:                   2.569
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         35800414.567
    Skew:                          -8.062   Prob(JB):                         0.00
    Kurtosis:                     372.359   Cond. No.                         59.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_153.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_154.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 1.078e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:03   Log-Likelihood:                 21698.
    No. Observations:                           6286   AIC:                        -4.339e+04
    Df Residuals:                               6284   BIC:                        -4.338e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0007    9.7e-05     -7.558      0.000      -0.001      -0.001
    QQQ_Rolling_Future_Return_1w     2.9526      0.003   1038.340      0.000       2.947       2.958
    ==============================================================================
    Omnibus:                     3412.046   Durbin-Watson:                   0.895
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           385507.507
    Skew:                          -1.639   Prob(JB):                         0.00
    Kurtosis:                      41.225   Cond. No.                         29.4
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_156.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_157.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1m   R-squared:                       0.982
    Model:                                       OLS   Adj. R-squared:                  0.982
    Method:                            Least Squares   F-statistic:                 3.507e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:07   Log-Likelihood:                 14066.
    No. Observations:                           6286   AIC:                        -2.813e+04
    Df Residuals:                               6284   BIC:                        -2.811e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0032      0.000     -9.681      0.000      -0.004      -0.003
    QQQ_Rolling_Future_Return_1m     2.9159      0.005    592.181      0.000       2.906       2.926
    ==============================================================================
    Omnibus:                     1452.213   Durbin-Watson:                   0.296
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            77489.348
    Skew:                           0.072   Prob(JB):                         0.00
    Kurtosis:                      20.200   Cond. No.                         15.1
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_159.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_160.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3m   R-squared:                       0.961
    Model:                                       OLS   Adj. R-squared:                  0.961
    Method:                            Least Squares   F-statistic:                 1.567e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:11   Log-Likelihood:                 8267.6
    No. Observations:                           6282   AIC:                        -1.653e+04
    Df Residuals:                               6280   BIC:                        -1.652e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0059      0.001     -7.041      0.000      -0.008      -0.004
    QQQ_Rolling_Future_Return_3m     2.8978      0.007    395.838      0.000       2.883       2.912
    ==============================================================================
    Omnibus:                     1352.723   Durbin-Watson:                   0.102
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            15617.746
    Skew:                           0.696   Prob(JB):                         0.00
    Kurtosis:                      10.598   Cond. No.                         8.95
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_162.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_163.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_6m   R-squared:                       0.932
    Model:                                       OLS   Adj. R-squared:                  0.932
    Method:                            Least Squares   F-statistic:                 8.620e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:15   Log-Likelihood:                 4283.9
    No. Observations:                           6282   AIC:                            -8564.
    Df Residuals:                               6280   BIC:                            -8550.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0002      0.002     -0.119      0.905      -0.003       0.003
    QQQ_Rolling_Future_Return_6m     2.8190      0.010    293.591      0.000       2.800       2.838
    ==============================================================================
    Omnibus:                     1637.953   Durbin-Watson:                   0.057
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8397.666
    Skew:                           1.159   Prob(JB):                         0.00
    Kurtosis:                       8.168   Cond. No.                         6.24
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_165.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_166.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1y   R-squared:                       0.905
    Model:                                       OLS   Adj. R-squared:                  0.905
    Method:                            Least Squares   F-statistic:                 5.967e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:19   Log-Likelihood:                 422.25
    No. Observations:                           6265   AIC:                            -840.5
    Df Residuals:                               6263   BIC:                            -827.0
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0161      0.003      5.020      0.000       0.010       0.022
    QQQ_Rolling_Future_Return_1y     2.8965      0.012    244.270      0.000       2.873       2.920
    ==============================================================================
    Omnibus:                     1968.116   Durbin-Watson:                   0.039
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8688.728
    Skew:                           1.474   Prob(JB):                         0.00
    Kurtosis:                       7.959   Cond. No.                         4.22
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_168.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_169.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_2y   R-squared:                       0.849
    Model:                                       OLS   Adj. R-squared:                  0.849
    Method:                            Least Squares   F-statistic:                 3.403e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:22   Log-Likelihood:                -4055.4
    No. Observations:                           6043   AIC:                             8115.
    Df Residuals:                               6041   BIC:                             8128.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0531      0.008     -6.749      0.000      -0.069      -0.038
    QQQ_Rolling_Future_Return_2y     3.2773      0.018    184.459      0.000       3.242       3.312
    ==============================================================================
    Omnibus:                     1751.026   Durbin-Watson:                   0.018
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5355.377
    Skew:                           1.491   Prob(JB):                         0.00
    Kurtosis:                       6.519   Cond. No.                         3.17
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_171.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_172.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3y   R-squared:                       0.824
    Model:                                       OLS   Adj. R-squared:                  0.824
    Method:                            Least Squares   F-statistic:                 2.717e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:26   Log-Likelihood:                -5989.9
    No. Observations:                           5791   AIC:                         1.198e+04
    Df Residuals:                               5789   BIC:                         1.200e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2887      0.014    -21.256      0.000      -0.315      -0.262
    QQQ_Rolling_Future_Return_3y     3.7207      0.023    164.844      0.000       3.676       3.765
    ==============================================================================
    Omnibus:                      873.964   Durbin-Watson:                   0.015
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1632.502
    Skew:                           0.952   Prob(JB):                         0.00
    Kurtosis:                       4.772   Cond. No.                         3.12
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_174.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_175.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_4y   R-squared:                       0.784
    Model:                                       OLS   Adj. R-squared:                  0.784
    Method:                            Least Squares   F-statistic:                 2.014e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:30   Log-Likelihood:                -8253.1
    No. Observations:                           5539   AIC:                         1.651e+04
    Df Residuals:                               5537   BIC:                         1.652e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.6009      0.024    -24.966      0.000      -0.648      -0.554
    QQQ_Rolling_Future_Return_4y     4.2830      0.030    141.933      0.000       4.224       4.342
    ==============================================================================
    Omnibus:                       68.621   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               51.608
    Skew:                           0.143   Prob(JB):                     6.22e-12
    Kurtosis:                       2.624   Cond. No.                         3.10
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_177.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_178.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_5y   R-squared:                       0.746
    Model:                                       OLS   Adj. R-squared:                  0.746
    Method:                            Least Squares   F-statistic:                 1.555e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:34   Log-Likelihood:                -11492.
    No. Observations:                           5303   AIC:                         2.299e+04
    Df Residuals:                               5301   BIC:                         2.300e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.4342      0.050    -28.784      0.000      -1.532      -1.337
    QQQ_Rolling_Future_Return_5y     5.6336      0.045    124.683      0.000       5.545       5.722
    ==============================================================================
    Omnibus:                      232.608   Durbin-Watson:                   0.009
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              344.101
    Skew:                           0.408   Prob(JB):                     1.90e-75
    Kurtosis:                       3.945   Cond. No.                         3.13
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_180.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_181.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1d   R-squared:                       0.999
    Model:                                       OLS   Adj. R-squared:                  0.999
    Method:                            Least Squares   F-statistic:                 5.380e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:39   Log-Likelihood:                 29448.
    No. Observations:                           5891   AIC:                        -5.889e+04
    Df Residuals:                               5889   BIC:                        -5.888e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                        -3.067e-05   2.13e-05     -1.441      0.150   -7.24e-05    1.11e-05
    QQQ_Rolling_Future_Return_1d     2.9545      0.001   2319.462      0.000       2.952       2.957
    ==============================================================================
    Omnibus:                     8699.984   Durbin-Watson:                   2.576
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         31790095.902
    Skew:                          -8.044   Prob(JB):                         0.00
    Kurtosis:                     362.520   Cond. No.                         59.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_183.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_184.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 1.008e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:43   Log-Likelihood:                 20307.
    No. Observations:                           5891   AIC:                        -4.061e+04
    Df Residuals:                               5889   BIC:                        -4.060e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0006      0.000     -6.376      0.000      -0.001      -0.000
    QQQ_Rolling_Future_Return_1w     2.9526      0.003   1003.872      0.000       2.947       2.958
    ==============================================================================
    Omnibus:                     3288.180   Durbin-Watson:                   0.897
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           369125.880
    Skew:                          -1.719   Prob(JB):                         0.00
    Kurtosis:                      41.626   Cond. No.                         29.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_186.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_187.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1m   R-squared:                       0.983
    Model:                                       OLS   Adj. R-squared:                  0.983
    Method:                            Least Squares   F-statistic:                 3.372e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:47   Log-Likelihood:                 13212.
    No. Observations:                           5891   AIC:                        -2.642e+04
    Df Residuals:                               5889   BIC:                        -2.641e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0025      0.000     -7.390      0.000      -0.003      -0.002
    QQQ_Rolling_Future_Return_1m     2.9140      0.005    580.700      0.000       2.904       2.924
    ==============================================================================
    Omnibus:                     1415.634   Durbin-Watson:                   0.309
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            78310.905
    Skew:                           0.194   Prob(JB):                         0.00
    Kurtosis:                      20.857   Cond. No.                         15.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_189.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_190.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3m   R-squared:                       0.962
    Model:                                       OLS   Adj. R-squared:                  0.962
    Method:                            Least Squares   F-statistic:                 1.509e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:51   Log-Likelihood:                 7801.2
    No. Observations:                           5891   AIC:                        -1.560e+04
    Df Residuals:                               5889   BIC:                        -1.559e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0040      0.001     -4.630      0.000      -0.006      -0.002
    QQQ_Rolling_Future_Return_3m     2.9068      0.007    388.474      0.000       2.892       2.921
    ==============================================================================
    Omnibus:                     1368.852   Durbin-Watson:                   0.107
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            16453.777
    Skew:                           0.766   Prob(JB):                         0.00
    Kurtosis:                      11.043   Cond. No.                         8.93
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_192.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_193.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_6m   R-squared:                       0.934
    Model:                                       OLS   Adj. R-squared:                  0.934
    Method:                            Least Squares   F-statistic:                 8.379e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:55   Log-Likelihood:                 4199.5
    No. Observations:                           5891   AIC:                            -8395.
    Df Residuals:                               5889   BIC:                            -8382.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0018      0.002     -1.061      0.289      -0.005       0.001
    QQQ_Rolling_Future_Return_6m     2.8731      0.010    289.466      0.000       2.854       2.893
    ==============================================================================
    Omnibus:                     1462.858   Durbin-Watson:                   0.063
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8114.729
    Skew:                           1.074   Prob(JB):                         0.00
    Kurtosis:                       8.333   Cond. No.                         6.45
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_195.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_196.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1y   R-squared:                       0.912
    Model:                                       OLS   Adj. R-squared:                  0.912
    Method:                            Least Squares   F-statistic:                 6.137e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:36:59   Log-Likelihood:                 724.28
    No. Observations:                           5891   AIC:                            -1445.
    Df Residuals:                               5889   BIC:                            -1431.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0012      0.003     -0.381      0.703      -0.008       0.005
    QQQ_Rolling_Future_Return_1y     3.0156      0.012    247.739      0.000       2.992       3.039
    ==============================================================================
    Omnibus:                     1762.243   Durbin-Watson:                   0.044
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8262.363
    Skew:                           1.376   Prob(JB):                         0.00
    Kurtosis:                       8.108   Cond. No.                         4.45
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_198.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_199.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_2y   R-squared:                       0.864
    Model:                                       OLS   Adj. R-squared:                  0.864
    Method:                            Least Squares   F-statistic:                 3.704e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:03   Log-Likelihood:                -3557.0
    No. Observations:                           5835   AIC:                             7118.
    Df Residuals:                               5833   BIC:                             7131.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1141      0.008    -14.432      0.000      -0.130      -0.099
    QQQ_Rolling_Future_Return_2y     3.4455      0.018    192.447      0.000       3.410       3.481
    ==============================================================================
    Omnibus:                     1666.636   Durbin-Watson:                   0.020
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5633.507
    Skew:                           1.426   Prob(JB):                         0.00
    Kurtosis:                       6.878   Cond. No.                         3.37
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_201.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_202.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3y   R-squared:                       0.840
    Model:                                       OLS   Adj. R-squared:                  0.840
    Method:                            Least Squares   F-statistic:                 2.942e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:07   Log-Likelihood:                -5490.2
    No. Observations:                           5597   AIC:                         1.098e+04
    Df Residuals:                               5595   BIC:                         1.100e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.3824      0.014    -27.778      0.000      -0.409      -0.355
    QQQ_Rolling_Future_Return_3y     3.9011      0.023    171.519      0.000       3.857       3.946
    ==============================================================================
    Omnibus:                      704.792   Durbin-Watson:                   0.016
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1332.452
    Skew:                           0.810   Prob(JB):                    4.59e-290
    Kurtosis:                       4.757   Cond. No.                         3.30
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_204.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_205.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_4y   R-squared:                       0.801
    Model:                                       OLS   Adj. R-squared:                  0.801
    Method:                            Least Squares   F-statistic:                 2.144e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:11   Log-Likelihood:                -7744.0
    No. Observations:                           5345   AIC:                         1.549e+04
    Df Residuals:                               5343   BIC:                         1.551e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.7291      0.025    -29.679      0.000      -0.777      -0.681
    QQQ_Rolling_Future_Return_4y     4.4752      0.031    146.441      0.000       4.415       4.535
    ==============================================================================
    Omnibus:                       21.704   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               16.422
    Skew:                           0.009   Prob(JB):                     0.000272
    Kurtosis:                       2.729   Cond. No.                         3.26
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_207.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_208.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_5y   R-squared:                       0.755
    Model:                                       OLS   Adj. R-squared:                  0.755
    Method:                            Least Squares   F-statistic:                 1.605e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:15   Log-Likelihood:                -11217.
    No. Observations:                           5223   AIC:                         2.244e+04
    Df Residuals:                               5221   BIC:                         2.245e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.6991      0.051    -33.137      0.000      -1.800      -1.599
    QQQ_Rolling_Future_Return_5y     5.8591      0.046    126.703      0.000       5.768       5.950
    ==============================================================================
    Omnibus:                      170.924   Durbin-Watson:                   0.009
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              276.130
    Skew:                           0.299   Prob(JB):                     1.09e-60
    Kurtosis:                       3.955   Cond. No.                         3.29
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_210.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_211.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1d   R-squared:                       0.999
    Model:                                       OLS   Adj. R-squared:                  0.999
    Method:                            Least Squares   F-statistic:                 4.767e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:20   Log-Likelihood:                 27167.
    No. Observations:                           5450   AIC:                        -5.433e+04
    Df Residuals:                               5448   BIC:                        -5.432e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                        -1.603e-05   2.24e-05     -0.715      0.475      -6e-05     2.8e-05
    QQQ_Rolling_Future_Return_1d     2.9532      0.001   2183.322      0.000       2.951       2.956
    ==============================================================================
    Omnibus:                     8184.686   Durbin-Watson:                   2.578
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         30358332.792
    Skew:                          -8.327   Prob(JB):                         0.00
    Kurtosis:                     368.254   Cond. No.                         60.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_213.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_214.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 9.352e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:24   Log-Likelihood:                 18855.
    No. Observations:                           5450   AIC:                        -3.771e+04
    Df Residuals:                               5448   BIC:                        -3.769e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0006      0.000     -5.513      0.000      -0.001      -0.000
    QQQ_Rolling_Future_Return_1w     2.9496      0.003    967.067      0.000       2.944       2.956
    ==============================================================================
    Omnibus:                     3225.323   Durbin-Watson:                   0.872
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           383461.293
    Skew:                          -1.880   Prob(JB):                         0.00
    Kurtosis:                      43.921   Cond. No.                         29.6
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_216.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_217.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1m   R-squared:                       0.982
    Model:                                       OLS   Adj. R-squared:                  0.982
    Method:                            Least Squares   F-statistic:                 3.035e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:28   Log-Likelihood:                 12190.
    No. Observations:                           5450   AIC:                        -2.438e+04
    Df Residuals:                               5448   BIC:                        -2.436e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0021      0.000     -5.912      0.000      -0.003      -0.001
    QQQ_Rolling_Future_Return_1m     2.9064      0.005    550.928      0.000       2.896       2.917
    ==============================================================================
    Omnibus:                     1331.295   Durbin-Watson:                   0.299
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            76820.025
    Skew:                           0.205   Prob(JB):                         0.00
    Kurtosis:                      21.388   Cond. No.                         15.1
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_219.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_220.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3m   R-squared:                       0.961
    Model:                                       OLS   Adj. R-squared:                  0.961
    Method:                            Least Squares   F-statistic:                 1.352e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:33   Log-Likelihood:                 7159.6
    No. Observations:                           5450   AIC:                        -1.432e+04
    Df Residuals:                               5448   BIC:                        -1.430e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0036      0.001     -3.911      0.000      -0.005      -0.002
    QQQ_Rolling_Future_Return_3m     2.9142      0.008    367.681      0.000       2.899       2.930
    ==============================================================================
    Omnibus:                     1265.114   Durbin-Watson:                   0.097
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            15817.724
    Skew:                           0.752   Prob(JB):                         0.00
    Kurtosis:                      11.209   Cond. No.                         9.00
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_222.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_223.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_6m   R-squared:                       0.937
    Model:                                       OLS   Adj. R-squared:                  0.937
    Method:                            Least Squares   F-statistic:                 8.117e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:37   Log-Likelihood:                 4027.0
    No. Observations:                           5450   AIC:                            -8050.
    Df Residuals:                               5448   BIC:                            -8037.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0043      0.002     -2.531      0.011      -0.008      -0.001
    QQQ_Rolling_Future_Return_6m     2.9104      0.010    284.897      0.000       2.890       2.930
    ==============================================================================
    Omnibus:                      970.680   Durbin-Watson:                   0.061
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4547.099
    Skew:                           0.789   Prob(JB):                         0.00
    Kurtosis:                       7.187   Cond. No.                         6.55
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_225.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_226.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1y   R-squared:                       0.917
    Model:                                       OLS   Adj. R-squared:                  0.917
    Method:                            Least Squares   F-statistic:                 5.991e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:42   Log-Likelihood:                 791.96
    No. Observations:                           5450   AIC:                            -1580.
    Df Residuals:                               5448   BIC:                            -1567.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0019      0.003     -0.561      0.575      -0.008       0.005
    QQQ_Rolling_Future_Return_1y     3.0633      0.013    244.773      0.000       3.039       3.088
    ==============================================================================
    Omnibus:                     1400.204   Durbin-Watson:                   0.045
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             6196.957
    Skew:                           1.185   Prob(JB):                         0.00
    Kurtosis:                       7.655   Cond. No.                         4.51
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_228.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_229.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_2y   R-squared:                       0.876
    Model:                                       OLS   Adj. R-squared:                  0.876
    Method:                            Least Squares   F-statistic:                 3.833e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:47   Log-Likelihood:                -3105.3
    No. Observations:                           5446   AIC:                             6215.
    Df Residuals:                               5444   BIC:                             6228.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1258      0.008    -15.615      0.000      -0.142      -0.110
    QQQ_Rolling_Future_Return_2y     3.5394      0.018    195.792      0.000       3.504       3.575
    ==============================================================================
    Omnibus:                     1479.731   Durbin-Watson:                   0.022
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5094.412
    Skew:                           1.346   Prob(JB):                         0.00
    Kurtosis:                       6.899   Cond. No.                         3.45
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_231.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_232.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3y   R-squared:                       0.852
    Model:                                       OLS   Adj. R-squared:                  0.852
    Method:                            Least Squares   F-statistic:                 3.073e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:50   Log-Likelihood:                -5069.4
    No. Observations:                           5355   AIC:                         1.014e+04
    Df Residuals:                               5353   BIC:                         1.016e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.3905      0.014    -28.213      0.000      -0.418      -0.363
    QQQ_Rolling_Future_Return_3y     3.9604      0.023    175.287      0.000       3.916       4.005
    ==============================================================================
    Omnibus:                      617.659   Durbin-Watson:                   0.018
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1248.527
    Skew:                           0.730   Prob(JB):                    7.69e-272
    Kurtosis:                       4.861   Cond. No.                         3.35
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_234.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_235.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_4y   R-squared:                       0.817
    Model:                                       OLS   Adj. R-squared:                  0.817
    Method:                            Least Squares   F-statistic:                 2.274e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:54   Log-Likelihood:                -7208.2
    No. Observations:                           5103   AIC:                         1.442e+04
    Df Residuals:                               5101   BIC:                         1.443e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.7382      0.025    -30.125      0.000      -0.786      -0.690
    QQQ_Rolling_Future_Return_4y     4.5547      0.030    150.794      0.000       4.496       4.614
    ==============================================================================
    Omnibus:                       11.531   Durbin-Watson:                   0.011
    Prob(Omnibus):                  0.003   Jarque-Bera (JB):               11.440
    Skew:                          -0.104   Prob(JB):                      0.00328
    Kurtosis:                       2.895   Cond. No.                         3.30
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_237.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_238.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_5y   R-squared:                       0.766
    Model:                                       OLS   Adj. R-squared:                  0.766
    Method:                            Least Squares   F-statistic:                 1.658e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:37:58   Log-Likelihood:                -10802.
    No. Observations:                           5069   AIC:                         2.161e+04
    Df Residuals:                               5067   BIC:                         2.162e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.7617      0.052    -34.121      0.000      -1.863      -1.661
    QQQ_Rolling_Future_Return_5y     5.9670      0.046    128.779      0.000       5.876       6.058
    ==============================================================================
    Omnibus:                      145.326   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              276.824
    Skew:                           0.211   Prob(JB):                     7.74e-61
    Kurtosis:                       4.065   Cond. No.                         3.33
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_240.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_241.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1d   R-squared:                       0.999
    Model:                                       OLS   Adj. R-squared:                  0.999
    Method:                            Least Squares   F-statistic:                 3.965e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:01   Log-Likelihood:                 24386.
    No. Observations:                           4909   AIC:                        -4.877e+04
    Df Residuals:                               4907   BIC:                        -4.875e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         7.111e-06   2.41e-05      0.296      0.768      -4e-05    5.43e-05
    QQQ_Rolling_Future_Return_1d     2.9509      0.001   1991.326      0.000       2.948       2.954
    ==============================================================================
    Omnibus:                     7547.441   Durbin-Watson:                   2.588
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):         28792520.130
    Skew:                          -8.741   Prob(JB):                         0.00
    Kurtosis:                     377.781   Cond. No.                         61.6
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_243.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_244.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 8.425e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:05   Log-Likelihood:                 17077.
    No. Observations:                           4909   AIC:                        -3.415e+04
    Df Residuals:                               4907   BIC:                        -3.414e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0005      0.000     -4.399      0.000      -0.001      -0.000
    QQQ_Rolling_Future_Return_1w     2.9538      0.003    917.893      0.000       2.947       2.960
    ==============================================================================
    Omnibus:                     3458.321   Durbin-Watson:                   0.891
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           430383.612
    Skew:                          -2.502   Prob(JB):                         0.00
    Kurtosis:                      48.597   Cond. No.                         30.2
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_246.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_247.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1m   R-squared:                       0.982
    Model:                                       OLS   Adj. R-squared:                  0.982
    Method:                            Least Squares   F-statistic:                 2.620e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:08   Log-Likelihood:                 11004.
    No. Observations:                           4909   AIC:                        -2.200e+04
    Df Residuals:                               4907   BIC:                        -2.199e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0014      0.000     -3.885      0.000      -0.002      -0.001
    QQQ_Rolling_Future_Return_1m     2.8967      0.006    511.819      0.000       2.886       2.908
    ==============================================================================
    Omnibus:                     1234.803   Durbin-Watson:                   0.289
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            81528.836
    Skew:                           0.182   Prob(JB):                         0.00
    Kurtosis:                      22.961   Cond. No.                         15.4
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_249.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_250.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3m   R-squared:                       0.964
    Model:                                       OLS   Adj. R-squared:                  0.964
    Method:                            Least Squares   F-statistic:                 1.297e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:10   Log-Likelihood:                 6687.8
    No. Observations:                           4909   AIC:                        -1.337e+04
    Df Residuals:                               4907   BIC:                        -1.336e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0002      0.001      0.214      0.830      -0.002       0.002
    QQQ_Rolling_Future_Return_3m     2.8960      0.008    360.174      0.000       2.880       2.912
    ==============================================================================
    Omnibus:                     1438.562   Durbin-Watson:                   0.111
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            18131.784
    Skew:                           1.037   Prob(JB):                         0.00
    Kurtosis:                      12.184   Cond. No.                         9.10
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_252.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_253.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_6m   R-squared:                       0.940
    Model:                                       OLS   Adj. R-squared:                  0.940
    Method:                            Least Squares   F-statistic:                 7.744e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:12   Log-Likelihood:                 3782.9
    No. Observations:                           4909   AIC:                            -7562.
    Df Residuals:                               4907   BIC:                            -7549.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0006      0.002     -0.379      0.705      -0.004       0.003
    QQQ_Rolling_Future_Return_6m     2.9398      0.011    278.284      0.000       2.919       2.961
    ==============================================================================
    Omnibus:                     1092.199   Durbin-Watson:                   0.063
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5026.992
    Skew:                           1.005   Prob(JB):                         0.00
    Kurtosis:                       7.531   Cond. No.                         6.63
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_255.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_256.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_1y   R-squared:                       0.921
    Model:                                       OLS   Adj. R-squared:                  0.921
    Method:                            Least Squares   F-statistic:                 5.687e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:15   Log-Likelihood:                 835.10
    No. Observations:                           4909   AIC:                            -1666.
    Df Residuals:                               4907   BIC:                            -1653.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0041      0.003     -1.223      0.221      -0.011       0.002
    QQQ_Rolling_Future_Return_1y     3.1266      0.013    238.483      0.000       3.101       3.152
    ==============================================================================
    Omnibus:                     1289.790   Durbin-Watson:                   0.048
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5902.128
    Skew:                           1.201   Prob(JB):                         0.00
    Kurtosis:                       7.804   Cond. No.                         4.58
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_258.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_259.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_2y   R-squared:                       0.890
    Model:                                       OLS   Adj. R-squared:                  0.890
    Method:                            Least Squares   F-statistic:                 3.983e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:17   Log-Likelihood:                -2555.2
    No. Observations:                           4909   AIC:                             5114.
    Df Residuals:                               4907   BIC:                             5127.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1417      0.008    -17.613      0.000      -0.157      -0.126
    QQQ_Rolling_Future_Return_2y     3.6958      0.019    199.585      0.000       3.660       3.732
    ==============================================================================
    Omnibus:                     1260.235   Durbin-Watson:                   0.024
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4505.177
    Skew:                           1.255   Prob(JB):                         0.00
    Kurtosis:                       6.966   Cond. No.                         3.50
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_261.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_262.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_3y   R-squared:                       0.867
    Model:                                       OLS   Adj. R-squared:                  0.867
    Method:                            Least Squares   F-statistic:                 3.200e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:19   Log-Likelihood:                -4387.0
    No. Observations:                           4909   AIC:                             8778.
    Df Residuals:                               4907   BIC:                             8791.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.4053      0.014    -29.518      0.000      -0.432      -0.378
    QQQ_Rolling_Future_Return_3y     4.1032      0.023    178.878      0.000       4.058       4.148
    ==============================================================================
    Omnibus:                      498.163   Durbin-Watson:                   0.020
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1119.255
    Skew:                           0.622   Prob(JB):                    9.05e-244
    Kurtosis:                       4.981   Cond. No.                         3.40
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_264.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_265.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_4y   R-squared:                       0.841
    Model:                                       OLS   Adj. R-squared:                  0.841
    Method:                            Least Squares   F-statistic:                 2.561e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:22   Log-Likelihood:                -6578.4
    No. Observations:                           4854   AIC:                         1.316e+04
    Df Residuals:                               4852   BIC:                         1.317e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.7780      0.024    -32.745      0.000      -0.825      -0.731
    QQQ_Rolling_Future_Return_4y     4.7051      0.029    160.037      0.000       4.647       4.763
    ==============================================================================
    Omnibus:                       37.794   Durbin-Watson:                   0.012
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               38.920
    Skew:                          -0.203   Prob(JB):                     3.54e-09
    Kurtosis:                       3.167   Cond. No.                         3.31
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_267.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_55_268.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     TQQQ_Rolling_Future_Return_5y   R-squared:                       0.790
    Model:                                       OLS   Adj. R-squared:                  0.790
    Method:                            Least Squares   F-statistic:                 1.825e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:38:24   Log-Likelihood:                -10152.
    No. Observations:                           4854   AIC:                         2.031e+04
    Df Residuals:                               4852   BIC:                         2.032e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.8225      0.051    -36.000      0.000      -1.922      -1.723
    QQQ_Rolling_Future_Return_5y     6.1390      0.045    135.095      0.000       6.050       6.228
    ==============================================================================
    Omnibus:                      154.348   Durbin-Watson:                   0.011
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              381.530
    Skew:                           0.121   Prob(JB):                     1.42e-83
    Kurtosis:                       4.352   Cond. No.                         3.32
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.


### Rolling Returns Following Drawdowns Deviation (QQQ & TQQQ)


```python
rolling_returns_positive_future_returns = pd.DataFrame(index=rolling_windows.keys(), data=rolling_windows.values())
rolling_returns_positive_future_returns.reset_index(inplace=True)
rolling_returns_positive_future_returns.rename(columns={"index":"Period", 0:"Days"}, inplace=True)

for drawdown in drawdown_levels:
    temp = rolling_returns_drawdown_stats.loc[rolling_returns_drawdown_stats["Drawdown"] == drawdown]
    temp = temp[["Period", "Positive_Future_Percentage"]]
    temp.rename(columns={"Positive_Future_Percentage" : f"Positive_Future_Percentage_Post_{drawdown}_Drawdown"}, inplace=True)
    rolling_returns_positive_future_returns = pd.merge(rolling_returns_positive_future_returns, temp, left_on="Period", right_on="Period", how="outer")
    rolling_returns_positive_future_returns.sort_values(by="Days", ascending=True, inplace=True)

rolling_returns_positive_future_returns.drop(columns={"Days"}, inplace=True)
rolling_returns_positive_future_returns.reset_index(drop=True, inplace=True)
pandas_set_decimal_places(2)
display(rolling_returns_positive_future_returns.set_index("Period"))
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
      <th>Positive_Future_Percentage_Post_-0.1_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.2_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.3_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.4_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.5_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.6_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.7_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.8_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.9_Drawdown</th>
    </tr>
    <tr>
      <th>Period</th>
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
      <th>1d</th>
      <td>0.55</td>
      <td>0.54</td>
      <td>0.54</td>
      <td>0.54</td>
      <td>0.54</td>
      <td>0.55</td>
      <td>0.54</td>
      <td>0.54</td>
      <td>0.54</td>
    </tr>
    <tr>
      <th>1w</th>
      <td>0.56</td>
      <td>0.56</td>
      <td>0.56</td>
      <td>0.56</td>
      <td>0.56</td>
      <td>0.57</td>
      <td>0.57</td>
      <td>0.56</td>
      <td>0.56</td>
    </tr>
    <tr>
      <th>1m</th>
      <td>0.60</td>
      <td>0.60</td>
      <td>0.59</td>
      <td>0.59</td>
      <td>0.60</td>
      <td>0.60</td>
      <td>0.60</td>
      <td>0.60</td>
      <td>0.60</td>
    </tr>
    <tr>
      <th>3m</th>
      <td>0.64</td>
      <td>0.64</td>
      <td>0.64</td>
      <td>0.64</td>
      <td>0.64</td>
      <td>0.64</td>
      <td>0.65</td>
      <td>0.65</td>
      <td>0.65</td>
    </tr>
    <tr>
      <th>6m</th>
      <td>0.67</td>
      <td>0.66</td>
      <td>0.66</td>
      <td>0.66</td>
      <td>0.66</td>
      <td>0.67</td>
      <td>0.69</td>
      <td>0.68</td>
      <td>0.68</td>
    </tr>
    <tr>
      <th>1y</th>
      <td>0.71</td>
      <td>0.71</td>
      <td>0.71</td>
      <td>0.71</td>
      <td>0.71</td>
      <td>0.71</td>
      <td>0.73</td>
      <td>0.74</td>
      <td>0.73</td>
    </tr>
    <tr>
      <th>2y</th>
      <td>0.74</td>
      <td>0.75</td>
      <td>0.75</td>
      <td>0.75</td>
      <td>0.75</td>
      <td>0.76</td>
      <td>0.78</td>
      <td>0.80</td>
      <td>0.81</td>
    </tr>
    <tr>
      <th>3y</th>
      <td>0.75</td>
      <td>0.76</td>
      <td>0.76</td>
      <td>0.76</td>
      <td>0.76</td>
      <td>0.77</td>
      <td>0.78</td>
      <td>0.78</td>
      <td>0.78</td>
    </tr>
    <tr>
      <th>4y</th>
      <td>0.73</td>
      <td>0.74</td>
      <td>0.75</td>
      <td>0.75</td>
      <td>0.75</td>
      <td>0.75</td>
      <td>0.76</td>
      <td>0.76</td>
      <td>0.75</td>
    </tr>
    <tr>
      <th>5y</th>
      <td>0.73</td>
      <td>0.74</td>
      <td>0.75</td>
      <td>0.75</td>
      <td>0.75</td>
      <td>0.75</td>
      <td>0.76</td>
      <td>0.76</td>
      <td>0.76</td>
    </tr>
  </tbody>
</table>
</div>



```python
plot_scatter(
    df=rolling_returns_positive_future_returns,
    x_plot_column="Period",
    y_plot_columns=[col for col in rolling_returns_positive_future_returns.columns if col != "Period"],
    title="TQQQ Future Return by Time Period Post Drawdown",
    x_label="Rolling Return Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Positive Future Return Percentage",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_58_0.png)
    


This plot summarizes the future rolling returns well. For rolling returns up to ~3 months *following* all drawdown levels, we see the rolling returns of TQQQ are positive ~65% of the time.

As we extend the time horizon, the percentage of positive rolling returns increases, which is consistent with the idea that the longer you hold through and post drawdown, the more likely you are to recover and achieve positive returns.

From a timing standpoint, this analysis suggests that the optimal time to buy TQQQ would be following a drawdown of 70% or more, and holding for at least 3 years. The data tells us that having a positive rolling return over time is ~75%.

One might consider the idea of allocating to TQQQ via a ladder, starting at a drawdown of 50%, and continuing to add to the position as the drawdown deepens, with the idea that the more severe the drawdown, the higher the expected future returns. However, this strategy could require enduring significant volatility, as one would be adding to the position during periods of paper losses.

## SPY & UPRO

Next, we will repeat the same analysis for SPY and UPRO, and see how the results compare to those of QQQ and TQQQ.

### Acquire & Plot Data (SPY)

First, let's get the data for SPY. If we already have the desired data, we can load it from a local pickle file. Otherwise, we can download it from Yahoo Finance using the `yf_pull_data` function.


```python
pandas_set_decimal_places(2)

yf_pull_data(
    base_directory=DATA_DIR,
    ticker="SPY",
    adjusted=False,
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

spy = load_data(
    base_directory=DATA_DIR,
    ticker="SPY",
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "SPY_Close", etc.
spy = spy.rename(columns={
    "Adj Close": "SPY_Adj_Close",
    "Close": "SPY_Close",
    "High": "SPY_High",
    "Low": "SPY_Low",
    "Open": "SPY_Open",
    "Volume": "SPY_Volume"
})

display(spy)
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
      <th>SPY_Adj_Close</th>
      <th>SPY_Close</th>
      <th>SPY_High</th>
      <th>SPY_Low</th>
      <th>SPY_Open</th>
      <th>SPY_Volume</th>
    </tr>
    <tr>
      <th>Date</th>
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
      <th>1993-01-29</th>
      <td>24.18</td>
      <td>43.94</td>
      <td>43.97</td>
      <td>43.75</td>
      <td>43.97</td>
      <td>1003200</td>
    </tr>
    <tr>
      <th>1993-02-01</th>
      <td>24.35</td>
      <td>44.25</td>
      <td>44.25</td>
      <td>43.97</td>
      <td>43.97</td>
      <td>480500</td>
    </tr>
    <tr>
      <th>1993-02-02</th>
      <td>24.40</td>
      <td>44.34</td>
      <td>44.38</td>
      <td>44.12</td>
      <td>44.22</td>
      <td>201300</td>
    </tr>
    <tr>
      <th>1993-02-03</th>
      <td>24.66</td>
      <td>44.81</td>
      <td>44.84</td>
      <td>44.38</td>
      <td>44.41</td>
      <td>529400</td>
    </tr>
    <tr>
      <th>1993-02-04</th>
      <td>24.76</td>
      <td>45.00</td>
      <td>45.09</td>
      <td>44.47</td>
      <td>44.97</td>
      <td>531500</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>725.43</td>
      <td>725.43</td>
      <td>738.38</td>
      <td>725.33</td>
      <td>733.39</td>
      <td>60341300</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>737.76</td>
      <td>737.76</td>
      <td>740.00</td>
      <td>724.41</td>
      <td>728.76</td>
      <td>86330500</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
      <td>741.75</td>
      <td>741.75</td>
      <td>744.44</td>
      <td>735.03</td>
      <td>740.71</td>
      <td>57079500</td>
    </tr>
    <tr>
      <th>2026-06-15</th>
      <td>754.83</td>
      <td>754.83</td>
      <td>756.68</td>
      <td>751.76</td>
      <td>751.85</td>
      <td>60176400</td>
    </tr>
    <tr>
      <th>2026-06-16</th>
      <td>750.33</td>
      <td>750.33</td>
      <td>755.44</td>
      <td>749.88</td>
      <td>754.55</td>
      <td>67093100</td>
    </tr>
  </tbody>
</table>
<p>8402 rows × 6 columns</p>
</div>


And the plot of the time series of partially adjusted close prices:


```python
plot_time_series(
    df=spy,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Adj_Close"],
    title="SPY Adjusted Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_62_0.png)
    


### Acquire & Plot Data (UPRO)

Next, UPRO:


```python
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="UPRO",
    adjusted=False,
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)
    
upro = load_data(
    base_directory=DATA_DIR,
    ticker="UPRO",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "UPRO_Close", etc.
upro = upro.rename(columns={
    "Adj Close": "UPRO_Adj_Close",
    "Close": "UPRO_Close", 
    "High": "UPRO_High", 
    "Low": "UPRO_Low", 
    "Open": "UPRO_Open", 
    "Volume": "UPRO_Volume"
})

display(upro)
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
      <th>UPRO_Adj_Close</th>
      <th>UPRO_Close</th>
      <th>UPRO_High</th>
      <th>UPRO_Low</th>
      <th>UPRO_Open</th>
      <th>UPRO_Volume</th>
    </tr>
    <tr>
      <th>Date</th>
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
      <th>2009-06-25</th>
      <td>1.13</td>
      <td>1.21</td>
      <td>1.21</td>
      <td>1.13</td>
      <td>1.13</td>
      <td>2577600</td>
    </tr>
    <tr>
      <th>2009-06-26</th>
      <td>1.13</td>
      <td>1.20</td>
      <td>1.21</td>
      <td>1.18</td>
      <td>1.20</td>
      <td>13104000</td>
    </tr>
    <tr>
      <th>2009-06-29</th>
      <td>1.16</td>
      <td>1.23</td>
      <td>1.24</td>
      <td>1.19</td>
      <td>1.21</td>
      <td>8690400</td>
    </tr>
    <tr>
      <th>2009-06-30</th>
      <td>1.13</td>
      <td>1.20</td>
      <td>1.24</td>
      <td>1.18</td>
      <td>1.23</td>
      <td>17128800</td>
    </tr>
    <tr>
      <th>2009-07-01</th>
      <td>1.14</td>
      <td>1.22</td>
      <td>1.25</td>
      <td>1.21</td>
      <td>1.22</td>
      <td>12038400</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>130.69</td>
      <td>130.69</td>
      <td>137.97</td>
      <td>130.68</td>
      <td>135.18</td>
      <td>4295800</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>137.29</td>
      <td>137.29</td>
      <td>138.58</td>
      <td>130.15</td>
      <td>132.43</td>
      <td>3955000</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
      <td>139.41</td>
      <td>139.41</td>
      <td>140.95</td>
      <td>135.75</td>
      <td>138.87</td>
      <td>2894200</td>
    </tr>
    <tr>
      <th>2026-06-15</th>
      <td>146.74</td>
      <td>146.74</td>
      <td>147.87</td>
      <td>145.10</td>
      <td>145.14</td>
      <td>2673100</td>
    </tr>
    <tr>
      <th>2026-06-16</th>
      <td>144.14</td>
      <td>144.14</td>
      <td>147.11</td>
      <td>143.88</td>
      <td>146.64</td>
      <td>1787300</td>
    </tr>
  </tbody>
</table>
<p>4270 rows × 6 columns</p>
</div>


And the plot of the time series of partially adjusted close prices:


```python
plot_time_series(
    df=upro,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["UPRO_Adj_Close"],
    title="UPRO Adjusted Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_66_0.png)
    


Looking at the close prices doesn't give us a true picture of the magnitude of the difference in returns due to the leverage. In order to see that, we need to look at the cumulative returns and the drawdowns.

 ### Calculate & Plot Cumulative Returns, Rolling Returns, and Drawdowns (SPY & UPRO)

 Next, we will calculate the cumulative returns, rolling returns, and drawdowns. This involves aligning the data to start with the inception of UPRO. For this excercise, we will not extrapolate the data for SPY back to 1993, but rather just align the data from the inception of UPRO in 2009.


```python
etfs = ["SPY", "UPRO"]

# Merge dataframes and drop rows with missing values
spy_upro_aligned = upro.merge(spy, left_index=True, right_index=True, how='left')
spy_upro_aligned = spy_upro_aligned.dropna()

# Calculate cumulative returns
for etf in etfs:
    spy_upro_aligned[f"{etf}_Return"] = spy_upro_aligned[f"{etf}_Close"].pct_change()
    spy_upro_aligned[f"{etf}_Cumulative_Return"] = (1 + spy_upro_aligned[f"{etf}_Return"]).cumprod() - 1
    spy_upro_aligned[f"{etf}_Cumulative_Return_Plus_One"] = 1 + spy_upro_aligned[f"{etf}_Cumulative_Return"]
    spy_upro_aligned[f"{etf}_Rolling_Max"] = spy_upro_aligned[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    spy_upro_aligned[f"{etf}_Drawdown"] = spy_upro_aligned[f"{etf}_Cumulative_Return_Plus_One"] / spy_upro_aligned[f"{etf}_Rolling_Max"] - 1
    spy_upro_aligned.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)

# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        spy_upro_aligned[f"{etf}_Rolling_Return_{period_name}"] = (
            spy_upro_aligned[f"{etf}_Close"].pct_change(periods=window)
        )
        
display(spy_upro_aligned)
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
      <th>UPRO_Adj_Close</th>
      <th>UPRO_Close</th>
      <th>UPRO_High</th>
      <th>UPRO_Low</th>
      <th>UPRO_Open</th>
      <th>UPRO_Volume</th>
      <th>SPY_Adj_Close</th>
      <th>SPY_Close</th>
      <th>SPY_High</th>
      <th>SPY_Low</th>
      <th>...</th>
      <th>UPRO_Rolling_Return_1d</th>
      <th>UPRO_Rolling_Return_1w</th>
      <th>UPRO_Rolling_Return_1m</th>
      <th>UPRO_Rolling_Return_3m</th>
      <th>UPRO_Rolling_Return_6m</th>
      <th>UPRO_Rolling_Return_1y</th>
      <th>UPRO_Rolling_Return_2y</th>
      <th>UPRO_Rolling_Return_3y</th>
      <th>UPRO_Rolling_Return_4y</th>
      <th>UPRO_Rolling_Return_5y</th>
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
      <th>2009-06-25</th>
      <td>1.13</td>
      <td>1.21</td>
      <td>1.21</td>
      <td>1.13</td>
      <td>1.13</td>
      <td>2577600</td>
      <td>68.20</td>
      <td>92.08</td>
      <td>92.17</td>
      <td>89.57</td>
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
      <th>2009-06-26</th>
      <td>1.13</td>
      <td>1.20</td>
      <td>1.21</td>
      <td>1.18</td>
      <td>1.20</td>
      <td>13104000</td>
      <td>68.03</td>
      <td>91.84</td>
      <td>92.24</td>
      <td>91.27</td>
      <td>...</td>
      <td>-0.01</td>
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
      <th>2009-06-29</th>
      <td>1.16</td>
      <td>1.23</td>
      <td>1.24</td>
      <td>1.19</td>
      <td>1.21</td>
      <td>8690400</td>
      <td>68.66</td>
      <td>92.70</td>
      <td>92.82</td>
      <td>91.60</td>
      <td>...</td>
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
    </tr>
    <tr>
      <th>2009-06-30</th>
      <td>1.13</td>
      <td>1.20</td>
      <td>1.24</td>
      <td>1.18</td>
      <td>1.23</td>
      <td>17128800</td>
      <td>68.11</td>
      <td>91.95</td>
      <td>93.06</td>
      <td>91.27</td>
      <td>...</td>
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
    </tr>
    <tr>
      <th>2009-07-01</th>
      <td>1.14</td>
      <td>1.22</td>
      <td>1.25</td>
      <td>1.21</td>
      <td>1.22</td>
      <td>12038400</td>
      <td>68.39</td>
      <td>92.33</td>
      <td>93.23</td>
      <td>92.21</td>
      <td>...</td>
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
      <th>2026-06-10</th>
      <td>130.69</td>
      <td>130.69</td>
      <td>137.97</td>
      <td>130.68</td>
      <td>135.18</td>
      <td>4295800</td>
      <td>725.43</td>
      <td>725.43</td>
      <td>738.38</td>
      <td>725.33</td>
      <td>...</td>
      <td>-0.05</td>
      <td>-0.12</td>
      <td>-0.07</td>
      <td>0.19</td>
      <td>0.12</td>
      <td>0.56</td>
      <td>0.79</td>
      <td>2.08</td>
      <td>1.73</td>
      <td>1.48</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>137.29</td>
      <td>137.29</td>
      <td>138.58</td>
      <td>130.15</td>
      <td>132.43</td>
      <td>3955000</td>
      <td>737.76</td>
      <td>737.76</td>
      <td>740.00</td>
      <td>724.41</td>
      <td>...</td>
      <td>0.05</td>
      <td>-0.08</td>
      <td>-0.02</td>
      <td>0.31</td>
      <td>0.18</td>
      <td>0.61</td>
      <td>0.88</td>
      <td>2.21</td>
      <td>2.01</td>
      <td>1.54</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
      <td>139.41</td>
      <td>139.41</td>
      <td>140.95</td>
      <td>135.75</td>
      <td>138.87</td>
      <td>2894200</td>
      <td>741.75</td>
      <td>741.75</td>
      <td>744.44</td>
      <td>735.03</td>
      <td>...</td>
      <td>0.02</td>
      <td>0.01</td>
      <td>-0.02</td>
      <td>0.35</td>
      <td>0.17</td>
      <td>0.65</td>
      <td>0.92</td>
      <td>2.29</td>
      <td>2.04</td>
      <td>1.58</td>
    </tr>
    <tr>
      <th>2026-06-15</th>
      <td>146.74</td>
      <td>146.74</td>
      <td>147.87</td>
      <td>145.10</td>
      <td>145.14</td>
      <td>2673100</td>
      <td>754.83</td>
      <td>754.83</td>
      <td>756.68</td>
      <td>751.76</td>
      <td>...</td>
      <td>0.05</td>
      <td>0.06</td>
      <td>0.01</td>
      <td>0.38</td>
      <td>0.23</td>
      <td>0.72</td>
      <td>1.00</td>
      <td>2.41</td>
      <td>2.11</td>
      <td>1.72</td>
    </tr>
    <tr>
      <th>2026-06-16</th>
      <td>144.14</td>
      <td>144.14</td>
      <td>147.11</td>
      <td>143.88</td>
      <td>146.64</td>
      <td>1787300</td>
      <td>750.33</td>
      <td>750.33</td>
      <td>755.44</td>
      <td>749.88</td>
      <td>...</td>
      <td>-0.02</td>
      <td>0.05</td>
      <td>0.03</td>
      <td>0.35</td>
      <td>0.25</td>
      <td>0.75</td>
      <td>0.95</td>
      <td>2.33</td>
      <td>2.15</td>
      <td>1.68</td>
    </tr>
  </tbody>
</table>
<p>4270 rows × 38 columns</p>
</div>


And now the plot for the cumulative returns:


```python
plot_time_series(
    df=spy_upro_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Cumulative_Return", "UPRO_Cumulative_Return"],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_70_0.png)
    


And the drawdown plot:


```python
plot_time_series(
    df=spy_upro_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Drawdown", "UPRO_Drawdown"],
    title="Drawdowns",
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
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_72_0.png)
    


### Summary Statistics (SPY & UPRO)

Looking at the summary statistics further confirms our intuitions about the volatility and drawdowns.


```python
spy_sum_stats = summary_stats(
    fund_list=["SPY"],
    df=spy_upro_aligned[["SPY_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

upro_sum_stats = summary_stats(
    fund_list=["UPRO"],
    df=spy_upro_aligned[["UPRO_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([spy_sum_stats, upro_sum_stats])

display(sum_stats)
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
      <th>SPY_Return</th>
      <td>0.14</td>
      <td>0.17</td>
      <td>0.81</td>
      <td>0.13</td>
      <td>0.11</td>
      <td>2025-04-09</td>
      <td>-0.11</td>
      <td>2020-03-16</td>
      <td>-0.34</td>
      <td>2020-02-19</td>
      <td>2020-03-23</td>
      <td>2020-08-18</td>
      <td>148</td>
      <td>0.39</td>
    </tr>
    <tr>
      <th>UPRO_Return</th>
      <td>0.42</td>
      <td>0.51</td>
      <td>0.81</td>
      <td>0.33</td>
      <td>0.28</td>
      <td>2020-03-24</td>
      <td>-0.35</td>
      <td>2020-03-16</td>
      <td>-0.77</td>
      <td>2020-02-19</td>
      <td>2020-03-23</td>
      <td>2021-01-08</td>
      <td>291</td>
      <td>0.42</td>
    </tr>
  </tbody>
</table>
</div>


### Plot Returns & Verify Beta (SPY & UPRO)

Before we look at the rolling returns, let us first verify that the daily returns for UPRO are in fact ~3x those of SPY.


```python
plot_scatter(
    df=spy_upro_aligned,
    x_plot_column="SPY_Return",
    y_plot_columns=["UPRO_Return"],
    title="SPY & UPRO Returns",
    x_label="SPY Return",
    x_format="Decimal",
    x_format_decimal_places=2,
    x_tick_spacing="Auto",
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="UPRO Return",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=True,
    OLS_column="UPRO_Return",
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=True,
    RidgeCV_column="UPRO_Return",
    regression_constant=True,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_76_0.png)
    



```python
model = run_regression(
    df=spy_upro_aligned,
    x_plot_column="SPY_Return",
    y_plot_column="UPRO_Return",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)

print(model.summary())
```

                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:            UPRO_Return   R-squared:                       0.994
    Model:                            OLS   Adj. R-squared:                  0.994
    Method:                 Least Squares   F-statistic:                 6.917e+05
    Date:                Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                        14:38:31   Log-Likelihood:                 19473.
    No. Observations:                4269   AIC:                        -3.894e+04
    Df Residuals:                    4267   BIC:                        -3.893e+04
    Df Model:                           1                                         
    Covariance Type:            nonrobust                                         
    ==============================================================================
                     coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------
    const       1.289e-05   3.87e-05      0.333      0.739   -6.31e-05    8.88e-05
    SPY_Return     2.9758      0.004    831.659      0.000       2.969       2.983
    ==============================================================================
    Omnibus:                     2736.798   Durbin-Watson:                   2.589
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           536793.027
    Skew:                           2.001   Prob(JB):                         0.00
    Kurtosis:                      57.789   Cond. No.                         92.5
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.


Similar to QQQ/TQQQ, this plot makes sense and we can see that there is a strong clustering of points, but we double check with the regression, regressing the UPRO daily return (y) on the SPY daily return (X).

### Extrapolate Data (SPY & UPRO)

We will now extrapolate the returns of SPY to backfill the data from the inception of SPY in 1993 to the inception of UPRO in 2009. For this, we'll use the coefficient of 2.98 that we found in the regression results above.


```python
# Set leverage multiplier based on regression coefficient
LEVERAGE_MULTIPLIER = model.params.iloc[1]

# Merge dataframes and extrapolate return values for SPY back to 1993 using the leverage multiplier
spy_upro_extrap = spy[["SPY_Close"]].merge(upro[["UPRO_Close"]], left_index=True, right_index=True, how='left')

etfs = ["SPY", "UPRO"]

# Calculate cumulative returns
for etf in etfs:
    spy_upro_extrap[f"{etf}_Return"] = spy_upro_extrap[f"{etf}_Close"].pct_change()

# Extrapolate UPRO returns for missing values
spy_upro_extrap["UPRO_Return"] = spy_upro_extrap["UPRO_Return"].fillna(LEVERAGE_MULTIPLIER * spy_upro_extrap["SPY_Return"])

# Find the first valid UPRO_Close index and value
first_valid_idx = spy_upro_extrap['UPRO_Close'].first_valid_index()
print(first_valid_idx)
first_valid_price = spy_upro_extrap.loc[first_valid_idx, 'UPRO_Close']
print(first_valid_price)
```

    2009-06-25 00:00:00
    1.205556035041809


Before we extrapolate, let's first look at the data we have for SPY and UPRO around the inception of UPRO in 2009:


```python
# Check values around the first valid index
pandas_set_decimal_places(4)
display(spy_upro_extrap.loc["2009-06-20":"2009-06-30"])
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
      <th>SPY_Close</th>
      <th>UPRO_Close</th>
      <th>SPY_Return</th>
      <th>UPRO_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2009-06-22</th>
      <td>89.2800</td>
      <td>NaN</td>
      <td>-0.0300</td>
      <td>-0.0892</td>
    </tr>
    <tr>
      <th>2009-06-23</th>
      <td>89.3500</td>
      <td>NaN</td>
      <td>0.0008</td>
      <td>0.0023</td>
    </tr>
    <tr>
      <th>2009-06-24</th>
      <td>90.1200</td>
      <td>NaN</td>
      <td>0.0086</td>
      <td>0.0256</td>
    </tr>
    <tr>
      <th>2009-06-25</th>
      <td>92.0800</td>
      <td>1.2056</td>
      <td>0.0217</td>
      <td>0.0647</td>
    </tr>
    <tr>
      <th>2009-06-26</th>
      <td>91.8400</td>
      <td>1.1993</td>
      <td>-0.0026</td>
      <td>-0.0052</td>
    </tr>
    <tr>
      <th>2009-06-29</th>
      <td>92.7000</td>
      <td>1.2333</td>
      <td>0.0094</td>
      <td>0.0284</td>
    </tr>
    <tr>
      <th>2009-06-30</th>
      <td>91.9500</td>
      <td>1.2039</td>
      <td>-0.0081</td>
      <td>-0.0239</td>
    </tr>
  </tbody>
</table>
</div>


Now, backfill the data for the UPRO close price:


```python
# Iterate through the dataframe backwards
for i in range(spy_upro_extrap.index.get_loc(first_valid_idx) - 1, -1, -1):
    
    # The return that led to the price the next day
    current_return = spy_upro_extrap.iloc[i + 1]['UPRO_Return']

    # Get the next day's price
    next_price = spy_upro_extrap.iloc[i + 1]['UPRO_Close']
    
    # Price_{t} = Price_{t+1} / (1 + Return_{t})
    spy_upro_extrap.loc[spy_upro_extrap.index[i], 'UPRO_Close'] = next_price / (1 + current_return)
```

Finally, confirm the values are correct:


```python
# Confirm values around the first valid index after extrapolation
display(spy_upro_extrap.loc["2009-06-20":"2009-06-30"])
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
      <th>SPY_Close</th>
      <th>UPRO_Close</th>
      <th>SPY_Return</th>
      <th>UPRO_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2009-06-22</th>
      <td>89.2800</td>
      <td>1.1014</td>
      <td>-0.0300</td>
      <td>-0.0892</td>
    </tr>
    <tr>
      <th>2009-06-23</th>
      <td>89.3500</td>
      <td>1.1040</td>
      <td>0.0008</td>
      <td>0.0023</td>
    </tr>
    <tr>
      <th>2009-06-24</th>
      <td>90.1200</td>
      <td>1.1323</td>
      <td>0.0086</td>
      <td>0.0256</td>
    </tr>
    <tr>
      <th>2009-06-25</th>
      <td>92.0800</td>
      <td>1.2056</td>
      <td>0.0217</td>
      <td>0.0647</td>
    </tr>
    <tr>
      <th>2009-06-26</th>
      <td>91.8400</td>
      <td>1.1993</td>
      <td>-0.0026</td>
      <td>-0.0052</td>
    </tr>
    <tr>
      <th>2009-06-29</th>
      <td>92.7000</td>
      <td>1.2333</td>
      <td>0.0094</td>
      <td>0.0284</td>
    </tr>
    <tr>
      <th>2009-06-30</th>
      <td>91.9500</td>
      <td>1.2039</td>
      <td>-0.0081</td>
      <td>-0.0239</td>
    </tr>
  </tbody>
</table>
</div>


And the complete DataFrame with the extrapolated values:


```python
pandas_set_decimal_places(2)
display(spy_upro_extrap)
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
      <th>SPY_Close</th>
      <th>UPRO_Close</th>
      <th>SPY_Return</th>
      <th>UPRO_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1993-01-29</th>
      <td>43.94</td>
      <td>0.93</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1993-02-01</th>
      <td>44.25</td>
      <td>0.95</td>
      <td>0.01</td>
      <td>0.02</td>
    </tr>
    <tr>
      <th>1993-02-02</th>
      <td>44.34</td>
      <td>0.95</td>
      <td>0.00</td>
      <td>0.01</td>
    </tr>
    <tr>
      <th>1993-02-03</th>
      <td>44.81</td>
      <td>0.98</td>
      <td>0.01</td>
      <td>0.03</td>
    </tr>
    <tr>
      <th>1993-02-04</th>
      <td>45.00</td>
      <td>0.99</td>
      <td>0.00</td>
      <td>0.01</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-06-10</th>
      <td>725.43</td>
      <td>130.69</td>
      <td>-0.02</td>
      <td>-0.05</td>
    </tr>
    <tr>
      <th>2026-06-11</th>
      <td>737.76</td>
      <td>137.29</td>
      <td>0.02</td>
      <td>0.05</td>
    </tr>
    <tr>
      <th>2026-06-12</th>
      <td>741.75</td>
      <td>139.41</td>
      <td>0.01</td>
      <td>0.02</td>
    </tr>
    <tr>
      <th>2026-06-15</th>
      <td>754.83</td>
      <td>146.74</td>
      <td>0.02</td>
      <td>0.05</td>
    </tr>
    <tr>
      <th>2026-06-16</th>
      <td>750.33</td>
      <td>144.14</td>
      <td>-0.01</td>
      <td>-0.02</td>
    </tr>
  </tbody>
</table>
<p>8402 rows × 4 columns</p>
</div>


After the extrapolation, we now have the following plots for the prices, cumulative returns, and drawdowns:


```python
etfs = ["SPY", "UPRO"]

# Calculate cumulative returns
for etf in etfs:
    spy_upro_extrap[f"{etf}_Return"] = spy_upro_extrap[f"{etf}_Close"].pct_change()
    spy_upro_extrap[f"{etf}_Cumulative_Return"] = (1 + spy_upro_extrap[f"{etf}_Return"]).cumprod() - 1
    spy_upro_extrap[f"{etf}_Cumulative_Return_Plus_One"] = 1 + spy_upro_extrap[f"{etf}_Cumulative_Return"]
    spy_upro_extrap[f"{etf}_Rolling_Max"] = spy_upro_extrap[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    spy_upro_extrap[f"{etf}_Drawdown"] = spy_upro_extrap[f"{etf}_Cumulative_Return_Plus_One"] / spy_upro_extrap[f"{etf}_Rolling_Max"] - 1
    spy_upro_extrap.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)
```


```python
plot_time_series(
    df=spy_upro_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Close"],
    title="SPY Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_90_0.png)
    



```python
plot_time_series(
    df=spy_upro_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["UPRO_Close"],
    title="UPRO Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_91_0.png)
    



```python
plot_time_series(
    df=spy_upro_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Cumulative_Return", "UPRO_Cumulative_Return"],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_92_0.png)
    



```python
plot_time_series(
    df=spy_upro_extrap,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["SPY_Drawdown", "UPRO_Drawdown"],
    title="Drawdowns",
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
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_93_0.png)
    



```python
spy_extrap_sum_stats = summary_stats(
    fund_list=["SPY"],
    df=spy_upro_extrap[["SPY_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

upro_extrap_sum_stats = summary_stats(
    fund_list=["UPRO"],
    df=spy_upro_extrap[["UPRO_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([spy_sum_stats, upro_sum_stats, spy_extrap_sum_stats, upro_extrap_sum_stats])
sum_stats.index = ["SPY (2009 - Present)", "UPRO (2009 - Present)", "SPY (1993 - Present)", "UPRO Extrapolated (1993 - Present)"]

display(sum_stats)
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
      <th>SPY (2009 - Present)</th>
      <td>0.14</td>
      <td>0.17</td>
      <td>0.81</td>
      <td>0.13</td>
      <td>0.11</td>
      <td>2025-04-09</td>
      <td>-0.11</td>
      <td>2020-03-16</td>
      <td>-0.34</td>
      <td>2020-02-19</td>
      <td>2020-03-23</td>
      <td>2020-08-18</td>
      <td>148</td>
      <td>0.39</td>
    </tr>
    <tr>
      <th>UPRO (2009 - Present)</th>
      <td>0.42</td>
      <td>0.51</td>
      <td>0.81</td>
      <td>0.33</td>
      <td>0.28</td>
      <td>2020-03-24</td>
      <td>-0.35</td>
      <td>2020-03-16</td>
      <td>-0.77</td>
      <td>2020-02-19</td>
      <td>2020-03-23</td>
      <td>2021-01-08</td>
      <td>291</td>
      <td>0.42</td>
    </tr>
    <tr>
      <th>SPY (1993 - Present)</th>
      <td>0.10</td>
      <td>0.19</td>
      <td>0.55</td>
      <td>0.09</td>
      <td>0.15</td>
      <td>2008-10-13</td>
      <td>-0.11</td>
      <td>2020-03-16</td>
      <td>-0.56</td>
      <td>2007-10-09</td>
      <td>2009-03-09</td>
      <td>2013-03-14</td>
      <td>1466</td>
      <td>0.16</td>
    </tr>
    <tr>
      <th>UPRO Extrapolated (1993 - Present)</th>
      <td>0.31</td>
      <td>0.55</td>
      <td>0.55</td>
      <td>0.16</td>
      <td>0.43</td>
      <td>2008-10-13</td>
      <td>-0.35</td>
      <td>2020-03-16</td>
      <td>-0.98</td>
      <td>2000-03-24</td>
      <td>2009-03-09</td>
      <td>2017-11-30</td>
      <td>3188</td>
      <td>0.17</td>
    </tr>
  </tbody>
</table>
</div>


Interestingly, the maximum drawdown for UPRO is not as severe as that of TQQQ, which may be due to that SPY has not had the same extreme return profile as QQQ. This highlights the importance of the underlying asset's return profile on the performance of leveraged ETFs.

### Plot Rolling Returns (SPY & UPRO)

Next, we will consider the following:

* Histogram and scatter plots of the rolling returns of SPY and UPRO
* Regressions to establish a "leverage factor" for the rolling returns
* The deviation from a 3x return for each time period

For this set of regressions, we will also allow the constant. First, we need the rolling returns for various time periods:



```python
# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        spy_upro_extrap[f"{etf}_Rolling_Return_{period_name}"] = (
            spy_upro_extrap[f"{etf}_Close"].pct_change(periods=window)
        )
```

This gives us the following series of histograms, scatter plots, and regression model results:


```python
# Create a dataframe to hold rolling returns stats
rolling_returns_stats = pd.DataFrame()

for period_name, window in rolling_windows.items():
    plot_histogram(
        df=spy_upro_extrap,
        plot_columns=[f"SPY_Rolling_Return_{period_name}", f"UPRO_Rolling_Return_{period_name}"],
        title=f"SPY & UPRO {period_name} Rolling Returns",
        x_label="Rolling Return",
        x_tick_spacing="Auto",
        x_tick_rotation=30,
        y_label="# Of Datapoints",
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    plot_scatter(
        df=spy_upro_extrap,
        x_plot_column=f"SPY_Rolling_Return_{period_name}",
        y_plot_columns=[f"UPRO_Rolling_Return_{period_name}"],
        title=f"SPY & UPRO {period_name} Rolling Returns",
        x_label="SPY Rolling Return",
        x_format="Decimal",
        x_format_decimal_places=2,
        x_tick_spacing="Auto",
        x_tick_start=None,
        x_tick_rotation=30,
        y_label="UPRO Rolling Return",
        y_format="Decimal",
        y_format_decimal_places=2,
        y_tick_spacing="Auto",
        y_tick_rotation=0,
        plot_OLS_regression_line=True,
        OLS_column=f"UPRO_Rolling_Return_{period_name}",
        plot_Ridge_regression_line=False,
        Ridge_column=None,
        plot_RidgeCV_regression_line=True,
        RidgeCV_column=f"UPRO_Rolling_Return_{period_name}",
        regression_constant=True,
        grid=True,
        legend=True,
        export_plot=False,
        plot_file_name=None,
    )

    # Run OLS regression with statsmodels
    model = run_regression(
        df=spy_upro_extrap,
        x_plot_column=f"SPY_Rolling_Return_{period_name}",
        y_plot_column=f"UPRO_Rolling_Return_{period_name}",
        regression_model="OLS-statsmodels",
        regression_constant=True,
    )
    print(model.summary())

    # Add the regression results to the rolling returns stats dataframe
    intercept = model.params.iloc[0]
    intercept_pvalue = model.pvalues.iloc[0]   # p-value for Intercept
    slope = model.params.iloc[1]
    slope_pvalue = model.pvalues.iloc[1]       # p-value for SPY_Return
    r_squared = model.rsquared

    # Calc skew
    return_ratio = spy_upro_extrap[f'UPRO_Rolling_Return_{period_name}'] / spy_upro_extrap[f'SPY_Rolling_Return_{period_name}']
    skew = return_ratio.skew()

    # Calc conditional symmetry
    up_markets = spy_upro_extrap[spy_upro_extrap[f'SPY_Rolling_Return_{period_name}'] > 0]
    down_markets = spy_upro_extrap[spy_upro_extrap[f'SPY_Rolling_Return_{period_name}'] <= 0]

    avg_beta_up = (up_markets[f'UPRO_Rolling_Return_{period_name}'] / up_markets[f'SPY_Rolling_Return_{period_name}']).mean()
    avg_beta_down = (down_markets[f'UPRO_Rolling_Return_{period_name}'] / down_markets[f'SPY_Rolling_Return_{period_name}']).mean()

    asymmetry = avg_beta_up - avg_beta_down

    rolling_returns_slope_int = pd.DataFrame({
        "Period": period_name,
        "Intercept": [intercept],
        # "Intercept_PValue": [intercept_pvalue],
        "Slope": [slope],
        # "Slope_PValue": [slope_pvalue],
        "R_Squared": [r_squared],
        "Skew": [skew],
        "Average Upside Beta": [avg_beta_up],
        "Average Downside Beta": [avg_beta_down],
        "Asymmetry": [asymmetry]
    })

    rolling_returns_stats = pd.concat([rolling_returns_stats, rolling_returns_slope_int])
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_0.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_1.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_1d   R-squared:                       0.997
    Model:                                OLS   Adj. R-squared:                  0.997
    Method:                     Least Squares   F-statistic:                 3.150e+06
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:38:39   Log-Likelihood:                 41165.
    No. Observations:                    8401   AIC:                        -8.233e+04
    Df Residuals:                        8399   BIC:                        -8.231e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                  6.545e-06   1.97e-05      0.333      0.739    -3.2e-05    4.51e-05
    SPY_Rolling_Return_1d     2.9759      0.002   1774.746      0.000       2.973       2.979
    ==============================================================================
    Omnibus:                     6935.216   Durbin-Watson:                   2.589
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):          4305371.385
    Skew:                           2.818   Prob(JB):                         0.00
    Kurtosis:                     113.760   Cond. No.                         85.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_3.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_4.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_1w   R-squared:                       0.994
    Model:                                OLS   Adj. R-squared:                  0.994
    Method:                     Least Squares   F-statistic:                 1.422e+06
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:38:41   Log-Likelihood:                 31865.
    No. Observations:                    8397   AIC:                        -6.373e+04
    Df Residuals:                        8395   BIC:                        -6.371e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0003   5.96e-05     -4.437      0.000      -0.000      -0.000
    SPY_Rolling_Return_1w     2.9726      0.002   1192.595      0.000       2.968       2.977
    ==============================================================================
    Omnibus:                     3767.042   Durbin-Watson:                   0.954
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):          1513474.088
    Skew:                          -0.842   Prob(JB):                         0.00
    Kurtosis:                      68.749   Cond. No.                         42.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_6.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_7.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_1m   R-squared:                       0.988
    Model:                                OLS   Adj. R-squared:                  0.988
    Method:                     Least Squares   F-statistic:                 6.771e+05
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:38:44   Log-Likelihood:                 23325.
    No. Observations:                    8381   AIC:                        -4.665e+04
    Df Residuals:                        8379   BIC:                        -4.663e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0015      0.000     -9.082      0.000      -0.002      -0.001
    SPY_Rolling_Return_1m     2.9618      0.004    822.882      0.000       2.955       2.969
    ==============================================================================
    Omnibus:                     2889.453   Durbin-Watson:                   0.313
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           869076.673
    Skew:                          -0.269   Prob(JB):                         0.00
    Kurtosis:                      52.884   Cond. No.                         22.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_9.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_10.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_3m   R-squared:                       0.979
    Model:                                OLS   Adj. R-squared:                  0.979
    Method:                     Least Squares   F-statistic:                 3.867e+05
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:38:46   Log-Likelihood:                 16567.
    No. Observations:                    8339   AIC:                        -3.313e+04
    Df Residuals:                        8337   BIC:                        -3.312e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0070      0.000    -18.201      0.000      -0.008      -0.006
    SPY_Rolling_Return_3m     3.0477      0.005    621.860      0.000       3.038       3.057
    ==============================================================================
    Omnibus:                     2443.395   Durbin-Watson:                   0.136
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           134196.605
    Skew:                           0.591   Prob(JB):                         0.00
    Kurtosis:                      22.617   Cond. No.                         13.5
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_12.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_13.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_6m   R-squared:                       0.957
    Model:                                OLS   Adj. R-squared:                  0.957
    Method:                     Least Squares   F-statistic:                 1.839e+05
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:38:49   Log-Likelihood:                 10257.
    No. Observations:                    8276   AIC:                        -2.051e+04
    Df Residuals:                        8274   BIC:                        -2.050e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0113      0.001    -13.412      0.000      -0.013      -0.010
    SPY_Rolling_Return_6m     3.0704      0.007    428.867      0.000       3.056       3.084
    ==============================================================================
    Omnibus:                     2098.788   Durbin-Watson:                   0.055
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            26735.476
    Skew:                           0.854   Prob(JB):                         0.00
    Kurtosis:                      11.638   Cond. No.                         9.32
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_15.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_16.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_1y   R-squared:                       0.927
    Model:                                OLS   Adj. R-squared:                  0.927
    Method:                     Least Squares   F-statistic:                 1.036e+05
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:38:52   Log-Likelihood:                 3981.9
    No. Observations:                    8150   AIC:                            -7960.
    Df Residuals:                        8148   BIC:                            -7946.
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0199      0.002    -10.334      0.000      -0.024      -0.016
    SPY_Rolling_Return_1y     3.2103      0.010    321.847      0.000       3.191       3.230
    ==============================================================================
    Omnibus:                     1417.642   Durbin-Watson:                   0.031
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             6684.393
    Skew:                           0.770   Prob(JB):                         0.00
    Kurtosis:                       7.161   Cond. No.                         6.13
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_18.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_19.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_2y   R-squared:                       0.895
    Model:                                OLS   Adj. R-squared:                  0.895
    Method:                     Least Squares   F-statistic:                 6.755e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:38:55   Log-Likelihood:                -2159.8
    No. Observations:                    7898   AIC:                             4324.
    Df Residuals:                        7896   BIC:                             4338.
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.0530      0.005    -11.481      0.000      -0.062      -0.044
    SPY_Rolling_Return_2y     3.5538      0.014    259.906      0.000       3.527       3.581
    ==============================================================================
    Omnibus:                      968.075   Durbin-Watson:                   0.018
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1515.839
    Skew:                           0.873   Prob(JB):                         0.00
    Kurtosis:                       4.248   Cond. No.                         4.01
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_21.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_22.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_3y   R-squared:                       0.866
    Model:                                OLS   Adj. R-squared:                  0.866
    Method:                     Least Squares   F-statistic:                 4.922e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:38:58   Log-Likelihood:                -7086.8
    No. Observations:                    7646   AIC:                         1.418e+04
    Df Residuals:                        7644   BIC:                         1.419e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.2353      0.009    -24.772      0.000      -0.254      -0.217
    SPY_Rolling_Return_3y     4.3732      0.020    221.846      0.000       4.335       4.412
    ==============================================================================
    Omnibus:                     1346.677   Durbin-Watson:                   0.008
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             2615.290
    Skew:                           1.077   Prob(JB):                         0.00
    Kurtosis:                       4.889   Cond. No.                         3.16
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_24.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_25.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_4y   R-squared:                       0.860
    Model:                                OLS   Adj. R-squared:                  0.860
    Method:                     Least Squares   F-statistic:                 4.527e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:39:01   Log-Likelihood:                -10394.
    No. Observations:                    7394   AIC:                         2.079e+04
    Df Residuals:                        7392   BIC:                         2.081e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -0.5564      0.016    -34.922      0.000      -0.588      -0.525
    SPY_Rolling_Return_4y     5.3537      0.025    212.761      0.000       5.304       5.403
    ==============================================================================
    Omnibus:                     1112.745   Durbin-Watson:                   0.008
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             2314.886
    Skew:                           0.909   Prob(JB):                         0.00
    Kurtosis:                       5.052   Cond. No.                         2.70
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_27.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_98_28.png)
    


                                  OLS Regression Results                              
    ==================================================================================
    Dep. Variable:     UPRO_Rolling_Return_5y   R-squared:                       0.848
    Model:                                OLS   Adj. R-squared:                  0.848
    Method:                     Least Squares   F-statistic:                 3.973e+04
    Date:                    Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                            14:39:04   Log-Likelihood:                -12924.
    No. Observations:                    7142   AIC:                         2.585e+04
    Df Residuals:                        7140   BIC:                         2.587e+04
    Df Model:                               1                                         
    Covariance Type:                nonrobust                                         
    =========================================================================================
                                coef    std err          t      P>|t|      [0.025      0.975]
    -----------------------------------------------------------------------------------------
    const                    -1.0162      0.025    -41.008      0.000      -1.065      -0.968
    SPY_Rolling_Return_5y     6.2683      0.031    199.327      0.000       6.207       6.330
    ==============================================================================
    Omnibus:                      700.093   Durbin-Watson:                   0.007
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1322.133
    Skew:                           0.660   Prob(JB):                    7.99e-288
    Kurtosis:                       4.644   Cond. No.                         2.52
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.


### Rolling Returns Deviation (SPY & UPRO)

Next, we will the rolling returns deviation from the expected 3x return for each time period. This will give us a better picture of the volatility decay effect and how it changes over different time horizons.


```python
rolling_returns_stats["Return_Deviation_From_3x"] = rolling_returns_stats["Slope"] - 3.0
pandas_set_decimal_places(3)
display(rolling_returns_stats.set_index("Period"))
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
      <th>Intercept</th>
      <th>Slope</th>
      <th>R_Squared</th>
      <th>Skew</th>
      <th>Average Upside Beta</th>
      <th>Average Downside Beta</th>
      <th>Asymmetry</th>
      <th>Return_Deviation_From_3x</th>
    </tr>
    <tr>
      <th>Period</th>
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
      <th>1d</th>
      <td>0.000</td>
      <td>2.976</td>
      <td>0.997</td>
      <td>NaN</td>
      <td>2.938</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.024</td>
    </tr>
    <tr>
      <th>1w</th>
      <td>-0.000</td>
      <td>2.973</td>
      <td>0.994</td>
      <td>NaN</td>
      <td>2.756</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.027</td>
    </tr>
    <tr>
      <th>1m</th>
      <td>-0.002</td>
      <td>2.962</td>
      <td>0.988</td>
      <td>NaN</td>
      <td>2.496</td>
      <td>-inf</td>
      <td>inf</td>
      <td>-0.038</td>
    </tr>
    <tr>
      <th>3m</th>
      <td>-0.007</td>
      <td>3.048</td>
      <td>0.979</td>
      <td>NaN</td>
      <td>2.009</td>
      <td>-inf</td>
      <td>inf</td>
      <td>0.048</td>
    </tr>
    <tr>
      <th>6m</th>
      <td>-0.011</td>
      <td>3.070</td>
      <td>0.957</td>
      <td>NaN</td>
      <td>1.029</td>
      <td>-inf</td>
      <td>inf</td>
      <td>0.070</td>
    </tr>
    <tr>
      <th>1y</th>
      <td>-0.020</td>
      <td>3.210</td>
      <td>0.927</td>
      <td>NaN</td>
      <td>1.651</td>
      <td>-inf</td>
      <td>inf</td>
      <td>0.210</td>
    </tr>
    <tr>
      <th>2y</th>
      <td>-0.053</td>
      <td>3.554</td>
      <td>0.895</td>
      <td>0.351</td>
      <td>1.866</td>
      <td>9.298</td>
      <td>-7.432</td>
      <td>0.554</td>
    </tr>
    <tr>
      <th>3y</th>
      <td>-0.235</td>
      <td>4.373</td>
      <td>0.866</td>
      <td>-6.094</td>
      <td>1.594</td>
      <td>8.620</td>
      <td>-7.026</td>
      <td>1.373</td>
    </tr>
    <tr>
      <th>4y</th>
      <td>-0.556</td>
      <td>5.354</td>
      <td>0.860</td>
      <td>-66.216</td>
      <td>0.045</td>
      <td>7.234</td>
      <td>-7.190</td>
      <td>2.354</td>
    </tr>
    <tr>
      <th>5y</th>
      <td>-1.016</td>
      <td>6.268</td>
      <td>0.848</td>
      <td>-35.378</td>
      <td>-2.209</td>
      <td>21.002</td>
      <td>-23.210</td>
      <td>3.268</td>
    </tr>
  </tbody>
</table>
</div>



```python
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Return_Deviation_From_3x"],
    title="UPRO Deviation from Perfect 3x Leverage by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Deviation from 3x Leverage",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_101_0.png)
    



```python
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Slope"],
    title="UPRO Slope by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Slope",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_102_0.png)
    



```python
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_columns=["Intercept"],
    title="Intercept by Time Period",
    x_label="Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Intercept",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_103_0.png)
    



```python
display(rolling_returns_stats.set_index("Period"))
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
      <th>Intercept</th>
      <th>Slope</th>
      <th>R_Squared</th>
      <th>Skew</th>
      <th>Average Upside Beta</th>
      <th>Average Downside Beta</th>
      <th>Asymmetry</th>
      <th>Return_Deviation_From_3x</th>
    </tr>
    <tr>
      <th>Period</th>
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
      <th>1d</th>
      <td>0.000</td>
      <td>2.976</td>
      <td>0.997</td>
      <td>NaN</td>
      <td>2.938</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.024</td>
    </tr>
    <tr>
      <th>1w</th>
      <td>-0.000</td>
      <td>2.973</td>
      <td>0.994</td>
      <td>NaN</td>
      <td>2.756</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.027</td>
    </tr>
    <tr>
      <th>1m</th>
      <td>-0.002</td>
      <td>2.962</td>
      <td>0.988</td>
      <td>NaN</td>
      <td>2.496</td>
      <td>-inf</td>
      <td>inf</td>
      <td>-0.038</td>
    </tr>
    <tr>
      <th>3m</th>
      <td>-0.007</td>
      <td>3.048</td>
      <td>0.979</td>
      <td>NaN</td>
      <td>2.009</td>
      <td>-inf</td>
      <td>inf</td>
      <td>0.048</td>
    </tr>
    <tr>
      <th>6m</th>
      <td>-0.011</td>
      <td>3.070</td>
      <td>0.957</td>
      <td>NaN</td>
      <td>1.029</td>
      <td>-inf</td>
      <td>inf</td>
      <td>0.070</td>
    </tr>
    <tr>
      <th>1y</th>
      <td>-0.020</td>
      <td>3.210</td>
      <td>0.927</td>
      <td>NaN</td>
      <td>1.651</td>
      <td>-inf</td>
      <td>inf</td>
      <td>0.210</td>
    </tr>
    <tr>
      <th>2y</th>
      <td>-0.053</td>
      <td>3.554</td>
      <td>0.895</td>
      <td>0.351</td>
      <td>1.866</td>
      <td>9.298</td>
      <td>-7.432</td>
      <td>0.554</td>
    </tr>
    <tr>
      <th>3y</th>
      <td>-0.235</td>
      <td>4.373</td>
      <td>0.866</td>
      <td>-6.094</td>
      <td>1.594</td>
      <td>8.620</td>
      <td>-7.026</td>
      <td>1.373</td>
    </tr>
    <tr>
      <th>4y</th>
      <td>-0.556</td>
      <td>5.354</td>
      <td>0.860</td>
      <td>-66.216</td>
      <td>0.045</td>
      <td>7.234</td>
      <td>-7.190</td>
      <td>2.354</td>
    </tr>
    <tr>
      <th>5y</th>
      <td>-1.016</td>
      <td>6.268</td>
      <td>0.848</td>
      <td>-35.378</td>
      <td>-2.209</td>
      <td>21.002</td>
      <td>-23.210</td>
      <td>3.268</td>
    </tr>
  </tbody>
</table>
</div>


Similar as to QQQ/TQQQ, up to 1 year, there is minimal difference between the mean UPRO 1 year rolling return and the hypothetical 3x leverage, with an R^2 of greater than 0.9.

However, as we extend the time period, we see that

* The "leverage factor" increases significantly, resulting in a deviation from the perfect 3x leverage.
* The intercept also begins to deviate significantly from 0.

### Rolling Returns Following Drawdowns (SPY & UPRO)

We will identify the drawdown levels of UPRO and then look at the subsequent rolling returns over various time horizons.


```python
# Copy DataFrame
spy_upro_extrap_future = spy_upro_extrap.copy()

# Create a list of drawdown levels to analyze
drawdown_levels = [-0.10, -0.20, -0.30, -0.40, -0.50, -0.60, -0.70, -0.80, -0.90]

# Shift the rolling return columns by the number of days in the rolling window to get the returns following the drawdown
for etf in etfs:
    for period_name, window in rolling_windows.items():
        spy_upro_extrap_future[f"{etf}_Rolling_Future_Return_{period_name}"] = spy_upro_extrap_future[f"{etf}_Rolling_Return_{period_name}"].shift(-window)
```

Now, we can analyze the future rolling returns following specific drawdown levels:


```python
# Create a dataframe to hold rolling returns stats
rolling_returns_drawdown_stats = pd.DataFrame()

for drawdown in drawdown_levels:

    for period_name, window in rolling_windows.items():

        try:
            plot_histogram(
                df=spy_upro_extrap_future[spy_upro_extrap_future["UPRO_Drawdown"] <= drawdown],
                plot_columns=[f"SPY_Rolling_Future_Return_{period_name}", f"UPRO_Rolling_Future_Return_{period_name}"],
                title=f"SPY & UPRO {period_name} Rolling Future Returns Post {drawdown} UPRO Drawdown",
                x_label="Rolling Return",
                x_tick_spacing="Auto",
                x_tick_rotation=30,
                y_label="# Of Datapoints",
                y_tick_spacing="Auto",
                y_tick_rotation=0,
                grid=True,
                legend=True,
                export_plot=False,
                plot_file_name=None,
            )

            plot_scatter(
                df=spy_upro_extrap_future[spy_upro_extrap_future["UPRO_Drawdown"] <= drawdown],
                x_plot_column=f"SPY_Rolling_Future_Return_{period_name}",
                y_plot_columns=[f"UPRO_Rolling_Future_Return_{period_name}"],
                title=f"SPY & UPRO {period_name} Rolling Future Returns Post {drawdown} UPRO Drawdown",
                x_label="SPY Rolling Return",
                x_format="Decimal",
                x_format_decimal_places=2,
                x_tick_spacing="Auto",
                x_tick_start=None,
                x_tick_rotation=30,
                y_label="UPRO Rolling Return",
                y_format="Decimal",
                y_format_decimal_places=2,
                y_tick_spacing="Auto",
                y_tick_rotation=0,
                plot_OLS_regression_line=True,
                OLS_column=f"UPRO_Rolling_Future_Return_{period_name}",
                plot_Ridge_regression_line=False,
                Ridge_column=None,
                plot_RidgeCV_regression_line=True,
                RidgeCV_column=f"UPRO_Rolling_Future_Return_{period_name}",
                regression_constant=True,
                grid=True,
                legend=True,
                export_plot=False,
                plot_file_name=None,
            )

            # Run OLS regression with statsmodels
            model = run_regression(
                df=spy_upro_extrap_future[spy_upro_extrap_future["UPRO_Drawdown"] <= drawdown],
                x_plot_column=f"SPY_Rolling_Future_Return_{period_name}",
                y_plot_column=f"UPRO_Rolling_Future_Return_{period_name}",
                regression_model="OLS-statsmodels",
                regression_constant=True,
            )
            print(model.summary())

            # Filter by drawdown
            drawdown_filter = spy_upro_extrap_future[spy_upro_extrap_future["UPRO_Drawdown"] <= drawdown]

            # Filter by period, drop rows with missing values
            future_filter = drawdown_filter[[f"UPRO_Rolling_Future_Return_{period_name}"]].dropna()

            # Find length of future dataframe
            future_length = len(future_filter)

            # Find length of future dataframe where return is positive
            positive_future_length = len(future_filter[future_filter[f"UPRO_Rolling_Future_Return_{period_name}"] > 0])

            # Calculate percentage of future returns that are positive
            positive_future_percentage = (positive_future_length / future_length) if future_length > 0 else 0

            # Add the regression results to the rolling returns stats dataframe
            intercept = model.params.iloc[0]
            # intercept_pvalue = model.pvalues.iloc[0]   # p-value for Intercept
            slope = model.params.iloc[1]
            # slope_pvalue = model.pvalues.iloc[1]       # p-value for Slope
            r_squared = model.rsquared

            rolling_returns_slope_int = pd.DataFrame({
                "Drawdown": drawdown,
                "Period": period_name,
                "Intercept": [intercept],
                # "Intercept_PValue": [intercept_pvalue],
                "Slope": [slope],
                # "Slope_PValue": [slope_pvalue],
                "R_Squared": [r_squared],
                "Positive_Future_Percentage": [positive_future_percentage],
            })
            
            rolling_returns_drawdown_stats = pd.concat([rolling_returns_drawdown_stats, rolling_returns_slope_int])

        except:
            print(f"Not enough data points for drawdown level {drawdown} and period {period_name} to run regression.")
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_0.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_1.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1d   R-squared:                       0.997
    Model:                                       OLS   Adj. R-squared:                  0.997
    Method:                            Least Squares   F-statistic:                 2.294e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:07   Log-Likelihood:                 29954.
    No. Observations:                           6240   AIC:                        -5.990e+04
    Df Residuals:                               6238   BIC:                        -5.989e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         2.179e-05   2.52e-05      0.864      0.388   -2.77e-05    7.12e-05
    SPY_Rolling_Future_Return_1d     2.9763      0.002   1514.736      0.000       2.972       2.980
    ==============================================================================
    Omnibus:                     4615.098   Durbin-Watson:                   2.629
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):          2417082.827
    Skew:                           2.322   Prob(JB):                         0.00
    Kurtosis:                      99.306   Cond. No.                         78.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_3.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_4.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1w   R-squared:                       0.994
    Model:                                       OLS   Adj. R-squared:                  0.994
    Method:                            Least Squares   F-statistic:                 9.726e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:11   Log-Likelihood:                 22952.
    No. Observations:                           6239   AIC:                        -4.590e+04
    Df Residuals:                               6237   BIC:                        -4.589e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0002   7.77e-05     -3.053      0.002      -0.000   -8.49e-05
    SPY_Rolling_Future_Return_1w     2.9733      0.003    986.197      0.000       2.967       2.979
    ==============================================================================
    Omnibus:                     2742.577   Durbin-Watson:                   0.977
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           785868.247
    Skew:                          -0.875   Prob(JB):                         0.00
    Kurtosis:                      57.954   Cond. No.                         39.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_6.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_7.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1m   R-squared:                       0.988
    Model:                                       OLS   Adj. R-squared:                  0.988
    Method:                            Least Squares   F-statistic:                 5.043e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:15   Log-Likelihood:                 17020.
    No. Observations:                           6239   AIC:                        -3.404e+04
    Df Residuals:                               6237   BIC:                        -3.402e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0014      0.000     -7.114      0.000      -0.002      -0.001
    SPY_Rolling_Future_Return_1m     2.9760      0.004    710.158      0.000       2.968       2.984
    ==============================================================================
    Omnibus:                     3365.813   Durbin-Watson:                   0.336
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           388718.880
    Skew:                          -1.616   Prob(JB):                         0.00
    Kurtosis:                      41.534   Cond. No.                         20.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_9.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_10.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3m   R-squared:                       0.978
    Model:                                       OLS   Adj. R-squared:                  0.978
    Method:                            Least Squares   F-statistic:                 2.721e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:18   Log-Likelihood:                 11931.
    No. Observations:                           6224   AIC:                        -2.386e+04
    Df Residuals:                               6222   BIC:                        -2.384e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0048      0.000    -10.081      0.000      -0.006      -0.004
    SPY_Rolling_Future_Return_3m     3.0332      0.006    521.652      0.000       3.022       3.045
    ==============================================================================
    Omnibus:                     1726.920   Durbin-Watson:                   0.148
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            88015.830
    Skew:                           0.522   Prob(JB):                         0.00
    Kurtosis:                      21.393   Cond. No.                         12.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_12.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_13.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_6m   R-squared:                       0.961
    Model:                                       OLS   Adj. R-squared:                  0.961
    Method:                            Least Squares   F-statistic:                 1.538e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:21   Log-Likelihood:                 7705.0
    No. Observations:                           6218   AIC:                        -1.541e+04
    Df Residuals:                               6216   BIC:                        -1.539e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0015      0.001     -1.542      0.123      -0.003       0.000
    SPY_Rolling_Future_Return_6m     3.0328      0.008    392.132      0.000       3.018       3.048
    ==============================================================================
    Omnibus:                     2088.631   Durbin-Watson:                   0.070
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            20755.651
    Skew:                           1.316   Prob(JB):                         0.00
    Kurtosis:                      11.555   Cond. No.                         8.72
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_15.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_16.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1y   R-squared:                       0.934
    Model:                                       OLS   Adj. R-squared:                  0.934
    Method:                            Least Squares   F-statistic:                 8.738e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:25   Log-Likelihood:                 3111.2
    No. Observations:                           6206   AIC:                            -6218.
    Df Residuals:                               6204   BIC:                            -6205.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0012      0.002     -0.579      0.563      -0.005       0.003
    SPY_Rolling_Future_Return_1y     3.1963      0.011    295.607      0.000       3.175       3.218
    ==============================================================================
    Omnibus:                     1604.179   Durbin-Watson:                   0.041
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             7674.422
    Skew:                           1.169   Prob(JB):                         0.00
    Kurtosis:                       7.920   Cond. No.                         5.87
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_18.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_19.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_2y   R-squared:                       0.890
    Model:                                       OLS   Adj. R-squared:                  0.890
    Method:                            Least Squares   F-statistic:                 4.957e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:29   Log-Likelihood:                -1470.3
    No. Observations:                           6105   AIC:                             2945.
    Df Residuals:                               6103   BIC:                             2958.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0189      0.005     -3.886      0.000      -0.028      -0.009
    SPY_Rolling_Future_Return_2y     3.4194      0.015    222.635      0.000       3.389       3.450
    ==============================================================================
    Omnibus:                     1172.709   Durbin-Watson:                   0.024
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             2727.121
    Skew:                           1.085   Prob(JB):                         0.00
    Kurtosis:                       5.453   Cond. No.                         4.04
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_21.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_22.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3y   R-squared:                       0.860
    Model:                                       OLS   Adj. R-squared:                  0.860
    Method:                            Least Squares   F-statistic:                 3.616e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:33   Log-Likelihood:                -4765.4
    No. Observations:                           5874   AIC:                             9535.
    Df Residuals:                               5872   BIC:                             9548.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1518      0.009    -16.254      0.000      -0.170      -0.133
    SPY_Rolling_Future_Return_3y     4.0937      0.022    190.154      0.000       4.052       4.136
    ==============================================================================
    Omnibus:                     1619.804   Durbin-Watson:                   0.011
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5366.747
    Skew:                           1.382   Prob(JB):                         0.00
    Kurtosis:                       6.779   Cond. No.                         3.30
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_24.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_25.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_4y   R-squared:                       0.843
    Model:                                       OLS   Adj. R-squared:                  0.843
    Method:                            Least Squares   F-statistic:                 3.027e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:36   Log-Likelihood:                -7406.0
    No. Observations:                           5622   AIC:                         1.482e+04
    Df Residuals:                               5620   BIC:                         1.483e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.4470      0.016    -27.363      0.000      -0.479      -0.415
    SPY_Rolling_Future_Return_4y     5.1190      0.029    173.984      0.000       5.061       5.177
    ==============================================================================
    Omnibus:                     1921.179   Durbin-Watson:                   0.013
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            10320.915
    Skew:                           1.544   Prob(JB):                         0.00
    Kurtosis:                       8.876   Cond. No.                         2.84
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_27.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_28.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_5y   R-squared:                       0.838
    Model:                                       OLS   Adj. R-squared:                  0.838
    Method:                            Least Squares   F-statistic:                 2.842e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:39   Log-Likelihood:                -9619.6
    No. Observations:                           5509   AIC:                         1.924e+04
    Df Residuals:                               5507   BIC:                         1.926e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.9358      0.026    -35.725      0.000      -0.987      -0.884
    SPY_Rolling_Future_Return_5y     6.1972      0.037    168.571      0.000       6.125       6.269
    ==============================================================================
    Omnibus:                     1244.774   Durbin-Watson:                   0.010
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4372.151
    Skew:                           1.109   Prob(JB):                         0.00
    Kurtosis:                       6.759   Cond. No.                         2.58
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_30.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_31.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1d   R-squared:                       0.997
    Model:                                       OLS   Adj. R-squared:                  0.997
    Method:                            Least Squares   F-statistic:                 1.841e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:43   Log-Likelihood:                 25147.
    No. Observations:                           5298   AIC:                        -5.029e+04
    Df Residuals:                               5296   BIC:                        -5.028e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         3.538e-05   2.89e-05      1.225      0.221   -2.12e-05     9.2e-05
    SPY_Rolling_Future_Return_1d     2.9771      0.002   1356.703      0.000       2.973       2.981
    ==============================================================================
    Omnibus:                     3687.243   Durbin-Watson:                   2.648
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):          1791380.798
    Skew:                           2.083   Prob(JB):                         0.00
    Kurtosis:                      92.987   Cond. No.                         76.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_33.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_34.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1w   R-squared:                       0.993
    Model:                                       OLS   Adj. R-squared:                  0.993
    Method:                            Least Squares   F-statistic:                 7.731e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:46   Log-Likelihood:                 19180.
    No. Observations:                           5298   AIC:                        -3.836e+04
    Df Residuals:                               5296   BIC:                        -3.834e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0002   8.93e-05     -2.254      0.024      -0.000   -2.62e-05
    SPY_Rolling_Future_Return_1w     2.9708      0.003    879.244      0.000       2.964       2.977
    ==============================================================================
    Omnibus:                     2334.649   Durbin-Watson:                   0.986
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           566105.986
    Skew:                          -0.920   Prob(JB):                         0.00
    Kurtosis:                      53.607   Cond. No.                         37.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_36.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_37.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1m   R-squared:                       0.987
    Model:                                       OLS   Adj. R-squared:                  0.987
    Method:                            Least Squares   F-statistic:                 4.039e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:50   Log-Likelihood:                 14148.
    No. Observations:                           5298   AIC:                        -2.829e+04
    Df Residuals:                               5296   BIC:                        -2.828e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0014      0.000     -5.972      0.000      -0.002      -0.001
    SPY_Rolling_Future_Return_1m     2.9725      0.005    635.555      0.000       2.963       2.982
    ==============================================================================
    Omnibus:                     2849.543   Durbin-Watson:                   0.332
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           279709.297
    Skew:                          -1.647   Prob(JB):                         0.00
    Kurtosis:                      38.443   Cond. No.                         20.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_39.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_40.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3m   R-squared:                       0.977
    Model:                                       OLS   Adj. R-squared:                  0.977
    Method:                            Least Squares   F-statistic:                 2.274e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:53   Log-Likelihood:                 9942.4
    No. Observations:                           5293   AIC:                        -1.988e+04
    Df Residuals:                               5291   BIC:                        -1.987e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0036      0.001     -6.761      0.000      -0.005      -0.003
    SPY_Rolling_Future_Return_3m     3.0229      0.006    476.837      0.000       3.010       3.035
    ==============================================================================
    Omnibus:                     1416.127   Durbin-Watson:                   0.159
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            70526.237
    Skew:                           0.467   Prob(JB):                         0.00
    Kurtosis:                      20.858   Cond. No.                         12.5
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_42.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_43.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_6m   R-squared:                       0.960
    Model:                                       OLS   Adj. R-squared:                  0.960
    Method:                            Least Squares   F-statistic:                 1.281e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:56   Log-Likelihood:                 6392.4
    No. Observations:                           5293   AIC:                        -1.278e+04
    Df Residuals:                               5291   BIC:                        -1.277e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0016      0.001      1.528      0.127      -0.000       0.004
    SPY_Rolling_Future_Return_6m     3.0177      0.008    357.943      0.000       3.001       3.034
    ==============================================================================
    Omnibus:                     1752.040   Durbin-Watson:                   0.078
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            16362.810
    Skew:                           1.309   Prob(JB):                         0.00
    Kurtosis:                      11.206   Cond. No.                         8.50
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_45.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_46.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1y   R-squared:                       0.937
    Model:                                       OLS   Adj. R-squared:                  0.937
    Method:                            Least Squares   F-statistic:                 7.845e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:39:59   Log-Likelihood:                 2767.6
    No. Observations:                           5293   AIC:                            -5531.
    Df Residuals:                               5291   BIC:                            -5518.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0097      0.002      4.345      0.000       0.005       0.014
    SPY_Rolling_Future_Return_1y     3.1668      0.011    280.090      0.000       3.145       3.189
    ==============================================================================
    Omnibus:                     1742.227   Durbin-Watson:                   0.051
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            10046.362
    Skew:                           1.455   Prob(JB):                         0.00
    Kurtosis:                       9.090   Cond. No.                         5.78
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_48.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_49.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_2y   R-squared:                       0.895
    Model:                                       OLS   Adj. R-squared:                  0.895
    Method:                            Least Squares   F-statistic:                 4.480e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:01   Log-Likelihood:                -843.25
    No. Observations:                           5242   AIC:                             1690.
    Df Residuals:                               5240   BIC:                             1704.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0070      0.005     -1.442      0.149      -0.016       0.003
    SPY_Rolling_Future_Return_2y     3.3634      0.016    211.654      0.000       3.332       3.395
    ==============================================================================
    Omnibus:                     1355.004   Durbin-Watson:                   0.031
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4718.217
    Skew:                           1.274   Prob(JB):                         0.00
    Kurtosis:                       6.887   Cond. No.                         4.18
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_51.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_52.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3y   R-squared:                       0.886
    Model:                                       OLS   Adj. R-squared:                  0.886
    Method:                            Least Squares   F-statistic:                 3.921e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:04   Log-Likelihood:                -2559.6
    No. Observations:                           5063   AIC:                             5123.
    Df Residuals:                               5061   BIC:                             5136.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1032      0.008    -13.699      0.000      -0.118      -0.088
    SPY_Rolling_Future_Return_3y     3.7804      0.019    198.011      0.000       3.743       3.818
    ==============================================================================
    Omnibus:                     1581.235   Durbin-Watson:                   0.020
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             8945.329
    Skew:                           1.376   Prob(JB):                         0.00
    Kurtosis:                       8.902   Cond. No.                         3.64
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_54.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_55.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_4y   R-squared:                       0.856
    Model:                                       OLS   Adj. R-squared:                  0.856
    Method:                            Least Squares   F-statistic:                 2.851e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:07   Log-Likelihood:                -4919.0
    No. Observations:                           4811   AIC:                             9842.
    Df Residuals:                               4809   BIC:                             9855.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.3001      0.014    -22.221      0.000      -0.327      -0.274
    SPY_Rolling_Future_Return_4y     4.5633      0.027    168.861      0.000       4.510       4.616
    ==============================================================================
    Omnibus:                     2903.933   Durbin-Watson:                   0.019
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            67539.845
    Skew:                           2.452   Prob(JB):                         0.00
    Kurtosis:                      20.688   Cond. No.                         3.17
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_57.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_58.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_5y   R-squared:                       0.842
    Model:                                       OLS   Adj. R-squared:                  0.842
    Method:                            Least Squares   F-statistic:                 2.529e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:09   Log-Likelihood:                -6916.3
    No. Observations:                           4736   AIC:                         1.384e+04
    Df Residuals:                               4734   BIC:                         1.385e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.6491      0.022    -29.489      0.000      -0.692      -0.606
    SPY_Rolling_Future_Return_5y     5.4200      0.034    159.030      0.000       5.353       5.487
    ==============================================================================
    Omnibus:                     2512.083   Durbin-Watson:                   0.026
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            40947.865
    Skew:                           2.157   Prob(JB):                         0.00
    Kurtosis:                      16.744   Cond. No.                         2.84
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_60.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_61.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1d   R-squared:                       0.997
    Model:                                       OLS   Adj. R-squared:                  0.997
    Method:                            Least Squares   F-statistic:                 1.595e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:12   Log-Likelihood:                 22509.
    No. Observations:                           4774   AIC:                        -4.501e+04
    Df Residuals:                               4772   BIC:                        -4.500e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         4.703e-05   3.14e-05      1.498      0.134   -1.45e-05       0.000
    SPY_Rolling_Future_Return_1d     2.9768      0.002   1263.069      0.000       2.972       2.981
    ==============================================================================
    Omnibus:                     3250.937   Durbin-Watson:                   2.668
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):          1511103.280
    Skew:                           2.005   Prob(JB):                         0.00
    Kurtosis:                      90.067   Cond. No.                         75.1
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_63.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_64.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1w   R-squared:                       0.993
    Model:                                       OLS   Adj. R-squared:                  0.993
    Method:                            Least Squares   F-statistic:                 6.655e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:14   Log-Likelihood:                 17170.
    No. Observations:                           4774   AIC:                        -3.434e+04
    Df Residuals:                               4772   BIC:                        -3.432e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0002   9.63e-05     -1.928      0.054      -0.000    3.14e-06
    SPY_Rolling_Future_Return_1w     2.9715      0.004    815.809      0.000       2.964       2.979
    ==============================================================================
    Omnibus:                     1997.445   Durbin-Watson:                   0.986
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           483327.377
    Skew:                          -0.802   Prob(JB):                         0.00
    Kurtosis:                      52.267   Cond. No.                         37.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_66.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_67.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1m   R-squared:                       0.987
    Model:                                       OLS   Adj. R-squared:                  0.987
    Method:                            Least Squares   F-statistic:                 3.515e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:17   Log-Likelihood:                 12680.
    No. Observations:                           4774   AIC:                        -2.536e+04
    Df Residuals:                               4772   BIC:                        -2.534e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0011      0.000     -4.425      0.000      -0.002      -0.001
    SPY_Rolling_Future_Return_1m     2.9621      0.005    592.900      0.000       2.952       2.972
    ==============================================================================
    Omnibus:                     2677.078   Durbin-Watson:                   0.336
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           262784.361
    Skew:                          -1.764   Prob(JB):                         0.00
    Kurtosis:                      39.175   Cond. No.                         20.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_69.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_70.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3m   R-squared:                       0.978
    Model:                                       OLS   Adj. R-squared:                  0.978
    Method:                            Least Squares   F-statistic:                 2.123e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:19   Log-Likelihood:                 8982.2
    No. Observations:                           4774   AIC:                        -1.796e+04
    Df Residuals:                               4772   BIC:                        -1.795e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0024      0.001     -4.436      0.000      -0.004      -0.001
    SPY_Rolling_Future_Return_3m     3.0170      0.007    460.797      0.000       3.004       3.030
    ==============================================================================
    Omnibus:                     1428.917   Durbin-Watson:                   0.169
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            68289.215
    Skew:                           0.660   Prob(JB):                         0.00
    Kurtosis:                      21.481   Cond. No.                         12.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_72.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_73.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_6m   R-squared:                       0.960
    Model:                                       OLS   Adj. R-squared:                  0.960
    Method:                            Least Squares   F-statistic:                 1.138e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:23   Log-Likelihood:                 5697.1
    No. Observations:                           4774   AIC:                        -1.139e+04
    Df Residuals:                               4772   BIC:                        -1.138e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0029      0.001      2.545      0.011       0.001       0.005
    SPY_Rolling_Future_Return_6m     3.0134      0.009    337.351      0.000       2.996       3.031
    ==============================================================================
    Omnibus:                     1652.314   Durbin-Watson:                   0.081
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            14596.667
    Skew:                           1.398   Prob(JB):                         0.00
    Kurtosis:                      11.097   Cond. No.                         8.43
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_75.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_76.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1y   R-squared:                       0.937
    Model:                                       OLS   Adj. R-squared:                  0.937
    Method:                            Least Squares   F-statistic:                 7.138e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:25   Log-Likelihood:                 2503.5
    No. Observations:                           4774   AIC:                            -5003.
    Df Residuals:                               4772   BIC:                            -4990.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0150      0.002      6.469      0.000       0.010       0.019
    SPY_Rolling_Future_Return_1y     3.1483      0.012    267.163      0.000       3.125       3.171
    ==============================================================================
    Omnibus:                     1679.284   Durbin-Watson:                   0.054
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            10737.738
    Skew:                           1.532   Prob(JB):                         0.00
    Kurtosis:                       9.678   Cond. No.                         5.73
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_78.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_79.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_2y   R-squared:                       0.901
    Model:                                       OLS   Adj. R-squared:                  0.901
    Method:                            Least Squares   F-statistic:                 4.347e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:28   Log-Likelihood:                -568.45
    No. Observations:                           4753   AIC:                             1141.
    Df Residuals:                               4751   BIC:                             1154.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0020      0.005      0.410      0.682      -0.008       0.012
    SPY_Rolling_Future_Return_2y     3.3735      0.016    208.485      0.000       3.342       3.405
    ==============================================================================
    Omnibus:                     1332.933   Durbin-Watson:                   0.031
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5113.538
    Skew:                           1.349   Prob(JB):                         0.00
    Kurtosis:                       7.306   Cond. No.                         4.22
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_81.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_82.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3y   R-squared:                       0.904
    Model:                                       OLS   Adj. R-squared:                  0.904
    Method:                            Least Squares   F-statistic:                 4.346e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:31   Log-Likelihood:                -1616.8
    No. Observations:                           4610   AIC:                             3238.
    Df Residuals:                               4608   BIC:                             3250.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0838      0.007    -12.216      0.000      -0.097      -0.070
    SPY_Rolling_Future_Return_3y     3.7321      0.018    208.472      0.000       3.697       3.767
    ==============================================================================
    Omnibus:                      743.503   Durbin-Watson:                   0.020
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1945.772
    Skew:                           0.882   Prob(JB):                         0.00
    Kurtosis:                       5.649   Cond. No.                         3.79
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_84.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_85.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_4y   R-squared:                       0.911
    Model:                                       OLS   Adj. R-squared:                  0.911
    Method:                            Least Squares   F-statistic:                 4.442e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:34   Log-Likelihood:                -2774.5
    No. Observations:                           4358   AIC:                             5553.
    Df Residuals:                               4356   BIC:                             5566.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2110      0.010    -21.722      0.000      -0.230      -0.192
    SPY_Rolling_Future_Return_4y     4.3324      0.021    210.772      0.000       4.292       4.373
    ==============================================================================
    Omnibus:                      124.071   Durbin-Watson:                   0.022
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              252.668
    Skew:                          -0.181   Prob(JB):                     1.36e-55
    Kurtosis:                       4.123   Cond. No.                         3.33
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_87.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_88.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_5y   R-squared:                       0.887
    Model:                                       OLS   Adj. R-squared:                  0.887
    Method:                            Least Squares   F-statistic:                 3.391e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:36   Log-Likelihood:                -4969.9
    No. Observations:                           4317   AIC:                             9944.
    Df Residuals:                               4315   BIC:                             9956.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.4824      0.017    -28.175      0.000      -0.516      -0.449
    SPY_Rolling_Future_Return_5y     5.0841      0.028    184.148      0.000       5.030       5.138
    ==============================================================================
    Omnibus:                      712.684   Durbin-Watson:                   0.017
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             3462.070
    Skew:                           0.712   Prob(JB):                         0.00
    Kurtosis:                       7.149   Cond. No.                         2.94
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_90.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_91.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1d   R-squared:                       0.997
    Model:                                       OLS   Adj. R-squared:                  0.997
    Method:                            Least Squares   F-statistic:                 1.487e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:38   Log-Likelihood:                 21081.
    No. Observations:                           4464   AIC:                        -4.216e+04
    Df Residuals:                               4462   BIC:                        -4.214e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         4.399e-05   3.22e-05      1.365      0.172   -1.92e-05       0.000
    SPY_Rolling_Future_Return_1d     2.9792      0.002   1219.623      0.000       2.974       2.984
    ==============================================================================
    Omnibus:                     2686.311   Durbin-Watson:                   2.619
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):          1502847.576
    Skew:                           1.531   Prob(JB):                         0.00
    Kurtosis:                      92.836   Cond. No.                         75.8
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_93.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_94.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1w   R-squared:                       0.993
    Model:                                       OLS   Adj. R-squared:                  0.993
    Method:                            Least Squares   F-statistic:                 6.179e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:41   Log-Likelihood:                 16080.
    No. Observations:                           4464   AIC:                        -3.216e+04
    Df Residuals:                               4462   BIC:                        -3.214e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0002    9.9e-05     -1.777      0.076      -0.000    1.82e-05
    SPY_Rolling_Future_Return_1w     2.9717      0.004    786.083      0.000       2.964       2.979
    ==============================================================================
    Omnibus:                     1977.890   Durbin-Watson:                   0.971
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           519496.172
    Skew:                          -0.906   Prob(JB):                         0.00
    Kurtosis:                      55.818   Cond. No.                         38.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_96.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_97.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1m   R-squared:                       0.986
    Model:                                       OLS   Adj. R-squared:                  0.986
    Method:                            Least Squares   F-statistic:                 3.225e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:44   Log-Likelihood:                 11851.
    No. Observations:                           4464   AIC:                        -2.370e+04
    Df Residuals:                               4462   BIC:                        -2.368e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0009      0.000     -3.421      0.001      -0.001      -0.000
    SPY_Rolling_Future_Return_1m     2.9520      0.005    567.903      0.000       2.942       2.962
    ==============================================================================
    Omnibus:                     2550.136   Durbin-Watson:                   0.358
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           256159.655
    Skew:                          -1.810   Prob(JB):                         0.00
    Kurtosis:                      39.934   Cond. No.                         20.4
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_99.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_100.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3m   R-squared:                       0.978
    Model:                                       OLS   Adj. R-squared:                  0.978
    Method:                            Least Squares   F-statistic:                 2.007e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:47   Log-Likelihood:                 8451.6
    No. Observations:                           4464   AIC:                        -1.690e+04
    Df Residuals:                               4462   BIC:                        -1.689e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0018      0.001     -3.146      0.002      -0.003      -0.001
    SPY_Rolling_Future_Return_3m     3.0074      0.007    448.023      0.000       2.994       3.021
    ==============================================================================
    Omnibus:                     1648.709   Durbin-Watson:                   0.182
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            57091.218
    Skew:                           1.101   Prob(JB):                         0.00
    Kurtosis:                      20.381   Cond. No.                         12.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_102.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_103.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_6m   R-squared:                       0.959
    Model:                                       OLS   Adj. R-squared:                  0.959
    Method:                            Least Squares   F-statistic:                 1.039e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:50   Log-Likelihood:                 5314.5
    No. Observations:                           4464   AIC:                        -1.063e+04
    Df Residuals:                               4462   BIC:                        -1.061e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0040      0.001      3.494      0.000       0.002       0.006
    SPY_Rolling_Future_Return_6m     2.9973      0.009    322.291      0.000       2.979       3.016
    ==============================================================================
    Omnibus:                     1611.744   Durbin-Watson:                   0.081
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            13013.675
    Skew:                           1.500   Prob(JB):                         0.00
    Kurtosis:                      10.808   Cond. No.                         8.46
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_105.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_106.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1y   R-squared:                       0.936
    Model:                                       OLS   Adj. R-squared:                  0.936
    Method:                            Least Squares   F-statistic:                 6.531e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:55   Log-Likelihood:                 2342.5
    No. Observations:                           4464   AIC:                            -4681.
    Df Residuals:                               4462   BIC:                            -4668.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0162      0.002      6.870      0.000       0.012       0.021
    SPY_Rolling_Future_Return_1y     3.1343      0.012    255.552      0.000       3.110       3.158
    ==============================================================================
    Omnibus:                     1688.563   Durbin-Watson:                   0.054
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            11825.259
    Skew:                           1.634   Prob(JB):                         0.00
    Kurtosis:                      10.273   Cond. No.                         5.76
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_108.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_109.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_2y   R-squared:                       0.907
    Model:                                       OLS   Adj. R-squared:                  0.907
    Method:                            Least Squares   F-statistic:                 4.354e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:40:58   Log-Likelihood:                -457.03
    No. Observations:                           4456   AIC:                             918.1
    Df Residuals:                               4454   BIC:                             930.9
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0011      0.005      0.223      0.824      -0.009       0.011
    SPY_Rolling_Future_Return_2y     3.4516      0.017    208.651      0.000       3.419       3.484
    ==============================================================================
    Omnibus:                     1243.382   Durbin-Watson:                   0.033
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4602.362
    Skew:                           1.354   Prob(JB):                         0.00
    Kurtosis:                       7.178   Cond. No.                         4.25
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_111.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_112.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3y   R-squared:                       0.907
    Model:                                       OLS   Adj. R-squared:                  0.907
    Method:                            Least Squares   F-statistic:                 4.275e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:01   Log-Likelihood:                -1484.9
    No. Observations:                           4388   AIC:                             2974.
    Df Residuals:                               4386   BIC:                             2987.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0806      0.007    -11.574      0.000      -0.094      -0.067
    SPY_Rolling_Future_Return_3y     3.7638      0.018    206.771      0.000       3.728       3.799
    ==============================================================================
    Omnibus:                      756.129   Durbin-Watson:                   0.022
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1962.708
    Skew:                           0.940   Prob(JB):                         0.00
    Kurtosis:                       5.683   Cond. No.                         3.81
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_114.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_115.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_4y   R-squared:                       0.923
    Model:                                       OLS   Adj. R-squared:                  0.923
    Method:                            Least Squares   F-statistic:                 4.998e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:04   Log-Likelihood:                -2359.9
    No. Observations:                           4145   AIC:                             4724.
    Df Residuals:                               4143   BIC:                             4736.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2199      0.009    -23.590      0.000      -0.238      -0.202
    SPY_Rolling_Future_Return_4y     4.4469      0.020    223.555      0.000       4.408       4.486
    ==============================================================================
    Omnibus:                      131.101   Durbin-Watson:                   0.024
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              321.129
    Skew:                          -0.122   Prob(JB):                     1.85e-70
    Kurtosis:                       4.342   Cond. No.                         3.35
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_117.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_118.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_5y   R-squared:                       0.896
    Model:                                       OLS   Adj. R-squared:                  0.896
    Method:                            Least Squares   F-statistic:                 3.555e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:06   Log-Likelihood:                -4610.5
    No. Observations:                           4126   AIC:                             9225.
    Df Residuals:                               4124   BIC:                             9238.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.5058      0.017    -29.865      0.000      -0.539      -0.473
    SPY_Rolling_Future_Return_5y     5.2121      0.028    188.535      0.000       5.158       5.266
    ==============================================================================
    Omnibus:                      688.469   Durbin-Watson:                   0.019
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             3305.383
    Skew:                           0.724   Prob(JB):                         0.00
    Kurtosis:                       7.139   Cond. No.                         2.96
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_120.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_121.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1d   R-squared:                       0.997
    Model:                                       OLS   Adj. R-squared:                  0.997
    Method:                            Least Squares   F-statistic:                 1.337e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:09   Log-Likelihood:                 18280.
    No. Observations:                           3870   AIC:                        -3.656e+04
    Df Residuals:                               3868   BIC:                        -3.654e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         5.793e-05   3.46e-05      1.675      0.094   -9.86e-06       0.000
    SPY_Rolling_Future_Return_1d     2.9842      0.003   1156.432      0.000       2.979       2.989
    ==============================================================================
    Omnibus:                     2832.298   Durbin-Watson:                   2.689
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):          1197723.159
    Skew:                           2.308   Prob(JB):                         0.00
    Kurtosis:                      89.061   Cond. No.                         74.7
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_123.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_124.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1w   R-squared:                       0.993
    Model:                                       OLS   Adj. R-squared:                  0.993
    Method:                            Least Squares   F-statistic:                 5.122e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:11   Log-Likelihood:                 13824.
    No. Observations:                           3870   AIC:                        -2.764e+04
    Df Residuals:                               3868   BIC:                        -2.763e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0001      0.000     -0.995      0.320      -0.000       0.000
    SPY_Rolling_Future_Return_1w     2.9703      0.004    715.673      0.000       2.962       2.978
    ==============================================================================
    Omnibus:                     1719.279   Durbin-Watson:                   1.003
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           452041.648
    Skew:                          -0.906   Prob(JB):                         0.00
    Kurtosis:                      55.916   Cond. No.                         38.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_126.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_127.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1m   R-squared:                       0.986
    Model:                                       OLS   Adj. R-squared:                  0.986
    Method:                            Least Squares   F-statistic:                 2.738e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:14   Log-Likelihood:                 10216.
    No. Observations:                           3870   AIC:                        -2.043e+04
    Df Residuals:                               3868   BIC:                        -2.042e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0008      0.000     -2.723      0.006      -0.001      -0.000
    SPY_Rolling_Future_Return_1m     2.9438      0.006    523.248      0.000       2.933       2.955
    ==============================================================================
    Omnibus:                     2106.264   Durbin-Watson:                   0.385
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           199242.609
    Skew:                          -1.680   Prob(JB):                         0.00
    Kurtosis:                      37.990   Cond. No.                         20.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_129.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_130.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3m   R-squared:                       0.978
    Model:                                       OLS   Adj. R-squared:                  0.978
    Method:                            Least Squares   F-statistic:                 1.701e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:17   Log-Likelihood:                 7304.4
    No. Observations:                           3870   AIC:                        -1.460e+04
    Df Residuals:                               3868   BIC:                        -1.459e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0012      0.001     -1.903      0.057      -0.002    3.47e-05
    SPY_Rolling_Future_Return_3m     2.9839      0.007    412.396      0.000       2.970       2.998
    ==============================================================================
    Omnibus:                     1374.843   Durbin-Watson:                   0.193
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            43043.094
    Skew:                           1.059   Prob(JB):                         0.00
    Kurtosis:                      19.200   Cond. No.                         12.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_132.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_133.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_6m   R-squared:                       0.957
    Model:                                       OLS   Adj. R-squared:                  0.957
    Method:                            Least Squares   F-statistic:                 8.588e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:20   Log-Likelihood:                 4530.7
    No. Observations:                           3870   AIC:                            -9057.
    Df Residuals:                               3868   BIC:                            -9045.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0067      0.001      5.298      0.000       0.004       0.009
    SPY_Rolling_Future_Return_6m     2.9569      0.010    293.052      0.000       2.937       2.977
    ==============================================================================
    Omnibus:                     1292.264   Durbin-Watson:                   0.081
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             9388.095
    Skew:                           1.396   Prob(JB):                         0.00
    Kurtosis:                      10.101   Cond. No.                         8.37
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_135.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_136.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1y   R-squared:                       0.933
    Model:                                       OLS   Adj. R-squared:                  0.933
    Method:                            Least Squares   F-statistic:                 5.407e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:23   Log-Likelihood:                 1957.2
    No. Observations:                           3870   AIC:                            -3910.
    Df Residuals:                               3868   BIC:                            -3898.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0175      0.003      6.790      0.000       0.012       0.023
    SPY_Rolling_Future_Return_1y     3.1290      0.013    232.519      0.000       3.103       3.155
    ==============================================================================
    Omnibus:                     1514.284   Durbin-Watson:                   0.057
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            11128.001
    Skew:                           1.682   Prob(JB):                         0.00
    Kurtosis:                      10.596   Cond. No.                         5.77
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_138.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_139.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_2y   R-squared:                       0.912
    Model:                                       OLS   Adj. R-squared:                  0.912
    Method:                            Least Squares   F-statistic:                 4.021e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:26   Log-Likelihood:                -377.88
    No. Observations:                           3870   AIC:                             759.8
    Df Residuals:                               3868   BIC:                             772.3
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0141      0.005     -2.680      0.007      -0.024      -0.004
    SPY_Rolling_Future_Return_2y     3.5920      0.018    200.520      0.000       3.557       3.627
    ==============================================================================
    Omnibus:                     1083.656   Durbin-Watson:                   0.036
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             3627.502
    Skew:                           1.394   Prob(JB):                         0.00
    Kurtosis:                       6.837   Cond. No.                         4.30
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_141.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_142.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3y   R-squared:                       0.910
    Model:                                       OLS   Adj. R-squared:                  0.910
    Method:                            Least Squares   F-statistic:                 3.905e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:28   Log-Likelihood:                -1326.0
    No. Observations:                           3864   AIC:                             2656.
    Df Residuals:                               3862   BIC:                             2668.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0866      0.007    -11.721      0.000      -0.101      -0.072
    SPY_Rolling_Future_Return_3y     3.8539      0.020    197.605      0.000       3.816       3.892
    ==============================================================================
    Omnibus:                      647.380   Durbin-Watson:                   0.022
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1443.977
    Skew:                           0.967   Prob(JB):                         0.00
    Kurtosis:                       5.286   Cond. No.                         3.80
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_144.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_145.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_4y   R-squared:                       0.940
    Model:                                       OLS   Adj. R-squared:                  0.940
    Method:                            Least Squares   F-statistic:                 5.809e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:32   Log-Likelihood:                -1763.9
    No. Observations:                           3695   AIC:                             3532.
    Df Residuals:                               3693   BIC:                             3544.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2198      0.009    -24.580      0.000      -0.237      -0.202
    SPY_Rolling_Future_Return_4y     4.5977      0.019    241.020      0.000       4.560       4.635
    ==============================================================================
    Omnibus:                      140.904   Durbin-Watson:                   0.030
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              414.925
    Skew:                           0.068   Prob(JB):                     7.95e-91
    Kurtosis:                       4.636   Cond. No.                         3.32
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_147.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_148.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_5y   R-squared:                       0.907
    Model:                                       OLS   Adj. R-squared:                  0.907
    Method:                            Least Squares   F-statistic:                 3.594e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:36   Log-Likelihood:                -3995.9
    No. Observations:                           3695   AIC:                             7996.
    Df Residuals:                               3693   BIC:                             8008.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.5138      0.017    -30.033      0.000      -0.547      -0.480
    SPY_Rolling_Future_Return_5y     5.3991      0.028    189.569      0.000       5.343       5.455
    ==============================================================================
    Omnibus:                      550.522   Durbin-Watson:                   0.022
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             2876.716
    Skew:                           0.608   Prob(JB):                         0.00
    Kurtosis:                       7.148   Cond. No.                         2.96
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_150.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_151.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1d   R-squared:                       0.997
    Model:                                       OLS   Adj. R-squared:                  0.997
    Method:                            Least Squares   F-statistic:                 1.059e+06
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:39   Log-Likelihood:                 14432.
    No. Observations:                           3070   AIC:                        -2.886e+04
    Df Residuals:                               3068   BIC:                        -2.885e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         7.423e-05   3.97e-05      1.869      0.062   -3.66e-06       0.000
    SPY_Rolling_Future_Return_1d     2.9824      0.003   1028.892      0.000       2.977       2.988
    ==============================================================================
    Omnibus:                     2273.338   Durbin-Watson:                   2.537
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):          1052903.376
    Skew:                           2.319   Prob(JB):                         0.00
    Kurtosis:                      93.607   Cond. No.                         73.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_153.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_154.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1w   R-squared:                       0.992
    Model:                                       OLS   Adj. R-squared:                  0.992
    Method:                            Least Squares   F-statistic:                 3.762e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:41   Log-Likelihood:                 10750.
    No. Observations:                           3070   AIC:                        -2.150e+04
    Df Residuals:                               3068   BIC:                        -2.148e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0001      0.000     -1.042      0.297      -0.000       0.000
    SPY_Rolling_Future_Return_1w     2.9677      0.005    613.327      0.000       2.958       2.977
    ==============================================================================
    Omnibus:                     1399.668   Durbin-Watson:                   1.060
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           313387.446
    Skew:                          -0.996   Prob(JB):                         0.00
    Kurtosis:                      52.457   Cond. No.                         36.7
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_156.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_157.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1m   R-squared:                       0.986
    Model:                                       OLS   Adj. R-squared:                  0.986
    Method:                            Least Squares   F-statistic:                 2.086e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:44   Log-Likelihood:                 7938.4
    No. Observations:                           3070   AIC:                        -1.587e+04
    Df Residuals:                               3068   BIC:                        -1.586e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0006      0.000     -1.709      0.088      -0.001    8.37e-05
    SPY_Rolling_Future_Return_1m     2.9396      0.006    456.780      0.000       2.927       2.952
    ==============================================================================
    Omnibus:                     1387.377   Durbin-Watson:                   0.407
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           109399.191
    Skew:                          -1.256   Prob(JB):                         0.00
    Kurtosis:                      32.136   Cond. No.                         19.6
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_159.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_160.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3m   R-squared:                       0.977
    Model:                                       OLS   Adj. R-squared:                  0.977
    Method:                            Least Squares   F-statistic:                 1.313e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:46   Log-Likelihood:                 5610.6
    No. Observations:                           3070   AIC:                        -1.122e+04
    Df Residuals:                               3068   BIC:                        -1.121e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0004      0.001      0.591      0.554      -0.001       0.002
    SPY_Rolling_Future_Return_3m     2.9878      0.008    362.351      0.000       2.972       3.004
    ==============================================================================
    Omnibus:                     1129.279   Durbin-Watson:                   0.193
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            29411.736
    Skew:                           1.166   Prob(JB):                         0.00
    Kurtosis:                      17.983   Cond. No.                         11.7
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_162.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_163.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_6m   R-squared:                       0.956
    Model:                                       OLS   Adj. R-squared:                  0.956
    Method:                            Least Squares   F-statistic:                 6.658e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:49   Log-Likelihood:                 3373.7
    No. Observations:                           3070   AIC:                            -6743.
    Df Residuals:                               3068   BIC:                            -6731.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0138      0.002      9.064      0.000       0.011       0.017
    SPY_Rolling_Future_Return_6m     2.9411      0.011    258.025      0.000       2.919       2.963
    ==============================================================================
    Omnibus:                      862.192   Durbin-Watson:                   0.075
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5063.517
    Skew:                           1.201   Prob(JB):                         0.00
    Kurtosis:                       8.815   Cond. No.                         7.84
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_165.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_166.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1y   R-squared:                       0.932
    Model:                                       OLS   Adj. R-squared:                  0.932
    Method:                            Least Squares   F-statistic:                 4.197e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:52   Log-Likelihood:                 1581.3
    No. Observations:                           3070   AIC:                            -3159.
    Df Residuals:                               3068   BIC:                            -3146.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0132      0.003      4.454      0.000       0.007       0.019
    SPY_Rolling_Future_Return_1y     3.1761      0.016    204.863      0.000       3.146       3.207
    ==============================================================================
    Omnibus:                     1211.028   Durbin-Watson:                   0.065
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            10512.118
    Skew:                           1.634   Prob(JB):                         0.00
    Kurtosis:                      11.456   Cond. No.                         5.99
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_168.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_169.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_2y   R-squared:                       0.932
    Model:                                       OLS   Adj. R-squared:                  0.932
    Method:                            Least Squares   F-statistic:                 4.210e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:54   Log-Likelihood:                 230.84
    No. Observations:                           3070   AIC:                            -457.7
    Df Residuals:                               3068   BIC:                            -445.6
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1524      0.006    -26.792      0.000      -0.164      -0.141
    SPY_Rolling_Future_Return_2y     4.1801      0.020    205.186      0.000       4.140       4.220
    ==============================================================================
    Omnibus:                      971.657   Durbin-Watson:                   0.048
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             5573.550
    Skew:                           1.382   Prob(JB):                         0.00
    Kurtosis:                       8.994   Cond. No.                         5.23
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_171.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_172.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3y   R-squared:                       0.906
    Model:                                       OLS   Adj. R-squared:                  0.906
    Method:                            Least Squares   F-statistic:                 2.942e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:41:57   Log-Likelihood:                -1092.6
    No. Observations:                           3070   AIC:                             2189.
    Df Residuals:                               3068   BIC:                             2201.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1351      0.009    -15.221      0.000      -0.153      -0.118
    SPY_Rolling_Future_Return_3y     4.1098      0.024    171.517      0.000       4.063       4.157
    ==============================================================================
    Omnibus:                      523.451   Durbin-Watson:                   0.022
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              948.262
    Skew:                           1.070   Prob(JB):                    1.22e-206
    Kurtosis:                       4.683   Cond. No.                         4.13
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_174.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_175.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_4y   R-squared:                       0.942
    Model:                                       OLS   Adj. R-squared:                  0.942
    Method:                            Least Squares   F-statistic:                 4.920e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:00   Log-Likelihood:                -1478.4
    No. Observations:                           3055   AIC:                             2961.
    Df Residuals:                               3053   BIC:                             2973.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2228      0.010    -21.592      0.000      -0.243      -0.203
    SPY_Rolling_Future_Return_4y     4.6897      0.021    221.806      0.000       4.648       4.731
    ==============================================================================
    Omnibus:                      120.398   Durbin-Watson:                   0.033
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              311.753
    Skew:                           0.172   Prob(JB):                     2.01e-68
    Kurtosis:                       4.527   Cond. No.                         3.39
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_177.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_178.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_5y   R-squared:                       0.919
    Model:                                       OLS   Adj. R-squared:                  0.919
    Method:                            Least Squares   F-statistic:                 3.475e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:02   Log-Likelihood:                -3195.7
    No. Observations:                           3055   AIC:                             6395.
    Df Residuals:                               3053   BIC:                             6407.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.5516      0.019    -29.727      0.000      -0.588      -0.515
    SPY_Rolling_Future_Return_5y     5.6648      0.030    186.401      0.000       5.605       5.724
    ==============================================================================
    Omnibus:                      454.885   Durbin-Watson:                   0.025
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             2119.392
    Skew:                           0.640   Prob(JB):                         0.00
    Kurtosis:                       6.875   Cond. No.                         3.02
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_180.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_181.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1d   R-squared:                       0.997
    Model:                                       OLS   Adj. R-squared:                  0.997
    Method:                            Least Squares   F-statistic:                 7.538e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:05   Log-Likelihood:                 10930.
    No. Observations:                           2365   AIC:                        -2.186e+04
    Df Residuals:                               2363   BIC:                        -2.184e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         8.911e-05    4.9e-05      1.819      0.069   -6.98e-06       0.000
    SPY_Rolling_Future_Return_1d     2.9778      0.003    868.207      0.000       2.971       2.985
    ==============================================================================
    Omnibus:                     1557.931   Durbin-Watson:                   2.718
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           638187.039
    Skew:                           1.869   Prob(JB):                         0.00
    Kurtosis:                      83.389   Cond. No.                         70.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_183.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_184.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1w   R-squared:                       0.991
    Model:                                       OLS   Adj. R-squared:                  0.991
    Method:                            Least Squares   F-statistic:                 2.714e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:09   Log-Likelihood:                 8089.3
    No. Observations:                           2365   AIC:                        -1.617e+04
    Df Residuals:                               2363   BIC:                        -1.616e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         -7.27e-05      0.000     -0.446      0.656      -0.000       0.000
    SPY_Rolling_Future_Return_1w     2.9631      0.006    520.948      0.000       2.952       2.974
    ==============================================================================
    Omnibus:                      893.210   Durbin-Watson:                   1.046
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           167515.158
    Skew:                          -0.620   Prob(JB):                         0.00
    Kurtosis:                      44.212   Cond. No.                         34.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_186.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_187.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1m   R-squared:                       0.984
    Model:                                       OLS   Adj. R-squared:                  0.984
    Method:                            Least Squares   F-statistic:                 1.475e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:12   Log-Likelihood:                 5932.2
    No. Observations:                           2365   AIC:                        -1.186e+04
    Df Residuals:                               2363   BIC:                        -1.185e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0007      0.000     -1.731      0.084      -0.002     9.4e-05
    SPY_Rolling_Future_Return_1m     2.9413      0.008    384.059      0.000       2.926       2.956
    ==============================================================================
    Omnibus:                      954.846   Durbin-Watson:                   0.364
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            63616.774
    Skew:                          -1.056   Prob(JB):                         0.00
    Kurtosis:                      28.320   Cond. No.                         18.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_189.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_190.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3m   R-squared:                       0.976
    Model:                                       OLS   Adj. R-squared:                  0.976
    Method:                            Least Squares   F-statistic:                 9.454e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:16   Log-Likelihood:                 4110.8
    No. Observations:                           2365   AIC:                            -8218.
    Df Residuals:                               2363   BIC:                            -8206.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0012      0.001      1.376      0.169      -0.001       0.003
    SPY_Rolling_Future_Return_3m     2.9865      0.010    307.476      0.000       2.967       3.006
    ==============================================================================
    Omnibus:                      813.502   Durbin-Watson:                   0.169
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            16777.462
    Skew:                           1.111   Prob(JB):                         0.00
    Kurtosis:                      15.858   Cond. No.                         11.1
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_192.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_193.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_6m   R-squared:                       0.954
    Model:                                       OLS   Adj. R-squared:                  0.954
    Method:                            Least Squares   F-statistic:                 4.945e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:19   Log-Likelihood:                 2608.9
    No. Observations:                           2365   AIC:                            -5214.
    Df Residuals:                               2363   BIC:                            -5202.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0035      0.002      1.918      0.055   -7.76e-05       0.007
    SPY_Rolling_Future_Return_6m     3.0747      0.014    222.382      0.000       3.048       3.102
    ==============================================================================
    Omnibus:                      829.894   Durbin-Watson:                   0.069
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             7402.918
    Skew:                           1.399   Prob(JB):                         0.00
    Kurtosis:                      11.203   Cond. No.                         8.39
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_195.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_196.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1y   R-squared:                       0.941
    Model:                                       OLS   Adj. R-squared:                  0.941
    Method:                            Least Squares   F-statistic:                 3.754e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:22   Log-Likelihood:                 1607.5
    No. Observations:                           2365   AIC:                            -3211.
    Df Residuals:                               2363   BIC:                            -3199.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0550      0.003    -16.380      0.000      -0.062      -0.048
    SPY_Rolling_Future_Return_1y     3.5928      0.019    193.751      0.000       3.556       3.629
    ==============================================================================
    Omnibus:                      724.877   Durbin-Watson:                   0.076
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            11317.638
    Skew:                           1.018   Prob(JB):                         0.00
    Kurtosis:                      13.522   Cond. No.                         7.46
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_198.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_199.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_2y   R-squared:                       0.947
    Model:                                       OLS   Adj. R-squared:                  0.947
    Method:                            Least Squares   F-statistic:                 4.183e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:25   Log-Likelihood:                 728.42
    No. Observations:                           2365   AIC:                            -1453.
    Df Residuals:                               2363   BIC:                            -1441.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.3422      0.007    -49.481      0.000      -0.356      -0.329
    SPY_Rolling_Future_Return_2y     4.7991      0.023    204.536      0.000       4.753       4.845
    ==============================================================================
    Omnibus:                      261.162   Durbin-Watson:                   0.050
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1787.524
    Skew:                          -0.271   Prob(JB):                         0.00
    Kurtosis:                       7.225   Cond. No.                         6.82
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_201.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_202.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3y   R-squared:                       0.901
    Model:                                       OLS   Adj. R-squared:                  0.901
    Method:                            Least Squares   F-statistic:                 2.157e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:29   Log-Likelihood:                -648.60
    No. Observations:                           2365   AIC:                             1301.
    Df Residuals:                               2363   BIC:                             1313.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.3554      0.013    -28.106      0.000      -0.380      -0.331
    SPY_Rolling_Future_Return_3y     4.7081      0.032    146.883      0.000       4.645       4.771
    ==============================================================================
    Omnibus:                      350.092   Durbin-Watson:                   0.028
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              725.322
    Skew:                           0.885   Prob(JB):                    3.15e-158
    Kurtosis:                       5.057   Cond. No.                         5.47
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_204.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_205.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_4y   R-squared:                       0.925
    Model:                                       OLS   Adj. R-squared:                  0.925
    Method:                            Least Squares   F-statistic:                 2.909e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:32   Log-Likelihood:                -1339.2
    No. Observations:                           2365   AIC:                             2682.
    Df Residuals:                               2363   BIC:                             2694.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1851      0.014    -12.911      0.000      -0.213      -0.157
    SPY_Rolling_Future_Return_4y     4.6424      0.027    170.563      0.000       4.589       4.696
    ==============================================================================
    Omnibus:                       55.462   Durbin-Watson:                   0.030
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              118.230
    Skew:                           0.081   Prob(JB):                     2.12e-26
    Kurtosis:                       4.083   Cond. No.                         3.69
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_207.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_208.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_5y   R-squared:                       0.917
    Model:                                       OLS   Adj. R-squared:                  0.917
    Method:                            Least Squares   F-statistic:                 2.615e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:35   Log-Likelihood:                -2565.1
    No. Observations:                           2365   AIC:                             5134.
    Df Residuals:                               2363   BIC:                             5146.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.4704      0.023    -20.190      0.000      -0.516      -0.425
    SPY_Rolling_Future_Return_5y     5.6929      0.035    161.724      0.000       5.624       5.762
    ==============================================================================
    Omnibus:                      310.990   Durbin-Watson:                   0.028
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1362.143
    Skew:                           0.566   Prob(JB):                    1.64e-296
    Kurtosis:                       6.542   Cond. No.                         3.12
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_210.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_211.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1d   R-squared:                       0.997
    Model:                                       OLS   Adj. R-squared:                  0.997
    Method:                            Least Squares   F-statistic:                 4.359e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:38   Log-Likelihood:                 6602.3
    No. Observations:                           1478   AIC:                        -1.320e+04
    Df Residuals:                               1476   BIC:                        -1.319e+04
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0001   7.23e-05      1.541      0.123   -3.04e-05       0.000
    SPY_Rolling_Future_Return_1d     2.9735      0.005    660.249      0.000       2.965       2.982
    ==============================================================================
    Omnibus:                      758.987   Durbin-Watson:                   2.689
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):           237450.371
    Skew:                           1.143   Prob(JB):                         0.00
    Kurtosis:                      65.053   Cond. No.                         62.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_213.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_214.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1w   R-squared:                       0.990
    Model:                                       OLS   Adj. R-squared:                  0.990
    Method:                            Least Squares   F-statistic:                 1.474e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:40   Log-Likelihood:                 4775.6
    No. Observations:                           1478   AIC:                            -9547.
    Df Residuals:                               1476   BIC:                            -9537.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                         4.324e-06      0.000      0.017      0.986      -0.000       0.000
    SPY_Rolling_Future_Return_1w     2.9572      0.008    383.892      0.000       2.942       2.972
    ==============================================================================
    Omnibus:                      517.459   Durbin-Watson:                   1.023
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            52535.710
    Skew:                          -0.625   Prob(JB):                         0.00
    Kurtosis:                      32.181   Cond. No.                         31.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_216.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_217.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1m   R-squared:                       0.983
    Model:                                       OLS   Adj. R-squared:                  0.983
    Method:                            Least Squares   F-statistic:                 8.446e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:43   Log-Likelihood:                 3586.0
    No. Observations:                           1478   AIC:                            -7168.
    Df Residuals:                               1476   BIC:                            -7157.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0029      0.001     -5.071      0.000      -0.004      -0.002
    SPY_Rolling_Future_Return_1m     3.0166      0.010    290.613      0.000       2.996       3.037
    ==============================================================================
    Omnibus:                      950.842   Durbin-Watson:                   0.291
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            19703.166
    Skew:                          -2.648   Prob(JB):                         0.00
    Kurtosis:                      20.085   Cond. No.                         18.7
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_219.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_220.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3m   R-squared:                       0.980
    Model:                                       OLS   Adj. R-squared:                  0.980
    Method:                            Least Squares   F-statistic:                 7.176e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:46   Log-Likelihood:                 2747.3
    No. Observations:                           1478   AIC:                            -5491.
    Df Residuals:                               1476   BIC:                            -5480.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0120      0.001    -11.212      0.000      -0.014      -0.010
    SPY_Rolling_Future_Return_3m     3.2238      0.012    267.877      0.000       3.200       3.247
    ==============================================================================
    Omnibus:                      396.149   Durbin-Watson:                   0.203
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             3162.485
    Skew:                          -1.020   Prob(JB):                         0.00
    Kurtosis:                       9.869   Cond. No.                         12.3
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_222.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_223.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_6m   R-squared:                       0.971
    Model:                                       OLS   Adj. R-squared:                  0.971
    Method:                            Least Squares   F-statistic:                 4.870e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:49   Log-Likelihood:                 1994.5
    No. Observations:                           1478   AIC:                            -3985.
    Df Residuals:                               1476   BIC:                            -3974.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0411      0.002    -19.749      0.000      -0.045      -0.037
    SPY_Rolling_Future_Return_6m     3.5209      0.016    220.685      0.000       3.490       3.552
    ==============================================================================
    Omnibus:                      302.933   Durbin-Watson:                   0.139
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1794.276
    Skew:                          -0.817   Prob(JB):                         0.00
    Kurtosis:                       8.144   Cond. No.                         9.83
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_225.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_226.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1y   R-squared:                       0.945
    Model:                                       OLS   Adj. R-squared:                  0.945
    Method:                            Least Squares   F-statistic:                 2.529e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:52   Log-Likelihood:                 1207.7
    No. Observations:                           1478   AIC:                            -2411.
    Df Residuals:                               1476   BIC:                            -2401.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.1638      0.005    -32.560      0.000      -0.174      -0.154
    SPY_Rolling_Future_Return_1y     4.1147      0.026    159.043      0.000       4.064       4.165
    ==============================================================================
    Omnibus:                      635.753   Durbin-Watson:                   0.055
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4012.236
    Skew:                          -1.899   Prob(JB):                         0.00
    Kurtosis:                      10.122   Cond. No.                         9.55
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_228.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_229.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_2y   R-squared:                       0.940
    Model:                                       OLS   Adj. R-squared:                  0.940
    Method:                            Least Squares   F-statistic:                 2.321e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:54   Log-Likelihood:                 416.75
    No. Observations:                           1478   AIC:                            -829.5
    Df Residuals:                               1476   BIC:                            -818.9
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.5307      0.012    -45.546      0.000      -0.554      -0.508
    SPY_Rolling_Future_Return_2y     5.2902      0.035    152.337      0.000       5.222       5.358
    ==============================================================================
    Omnibus:                      349.925   Durbin-Watson:                   0.045
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              914.237
    Skew:                          -1.242   Prob(JB):                    2.99e-199
    Kurtosis:                       5.945   Cond. No.                         8.01
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_231.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_232.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3y   R-squared:                       0.884
    Model:                                       OLS   Adj. R-squared:                  0.884
    Method:                            Least Squares   F-statistic:                 1.127e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:56   Log-Likelihood:                -267.98
    No. Observations:                           1478   AIC:                             540.0
    Df Residuals:                               1476   BIC:                             550.6
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.0261      0.027    -38.067      0.000      -1.079      -0.973
    SPY_Rolling_Future_Return_3y     6.1824      0.058    106.180      0.000       6.068       6.297
    ==============================================================================
    Omnibus:                       75.106   Durbin-Watson:                   0.032
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               91.663
    Skew:                          -0.514   Prob(JB):                     1.25e-20
    Kurtosis:                       3.657   Cond. No.                         9.26
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_234.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_235.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_4y   R-squared:                       0.877
    Model:                                       OLS   Adj. R-squared:                  0.877
    Method:                            Least Squares   F-statistic:                 1.049e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:42:59   Log-Likelihood:                -459.80
    No. Observations:                           1478   AIC:                             923.6
    Df Residuals:                               1476   BIC:                             934.2
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.3239      0.040    -33.279      0.000      -1.402      -1.246
    SPY_Rolling_Future_Return_4y     6.5227      0.064    102.411      0.000       6.398       6.648
    ==============================================================================
    Omnibus:                      316.558   Durbin-Watson:                   0.032
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              745.315
    Skew:                          -1.168   Prob(JB):                    1.43e-162
    Kurtosis:                       5.578   Cond. No.                         10.2
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_237.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_238.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_5y   R-squared:                       0.895
    Model:                                       OLS   Adj. R-squared:                  0.895
    Method:                            Least Squares   F-statistic:                 1.257e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:43:01   Log-Likelihood:                -1477.7
    No. Observations:                           1478   AIC:                             2959.
    Df Residuals:                               1476   BIC:                             2970.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.3148      0.048    -27.521      0.000      -1.409      -1.221
    SPY_Rolling_Future_Return_5y     6.8269      0.061    112.133      0.000       6.707       6.946
    ==============================================================================
    Omnibus:                      180.874   Durbin-Watson:                   0.042
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              812.227
    Skew:                           0.496   Prob(JB):                    4.24e-177
    Kurtosis:                       6.493   Cond. No.                         5.57
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_240.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_241.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1d   R-squared:                       0.998
    Model:                                       OLS   Adj. R-squared:                  0.998
    Method:                            Least Squares   F-statistic:                 2.300e+05
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:43:03   Log-Likelihood:                 2171.6
    No. Observations:                            492   AIC:                            -4339.
    Df Residuals:                                490   BIC:                            -4331.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                            0.0001      0.000      0.853      0.394      -0.000       0.000
    SPY_Rolling_Future_Return_1d     2.9737      0.006    479.627      0.000       2.962       2.986
    ==============================================================================
    Omnibus:                      207.234   Durbin-Watson:                   2.771
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):            96838.420
    Skew:                           0.200   Prob(JB):                         0.00
    Kurtosis:                      71.729   Cond. No.                         46.8
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_243.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_244.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1w   R-squared:                       0.990
    Model:                                       OLS   Adj. R-squared:                  0.990
    Method:                            Least Squares   F-statistic:                 4.756e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:43:06   Log-Likelihood:                 1471.4
    No. Observations:                            492   AIC:                            -2939.
    Df Residuals:                                490   BIC:                            -2930.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0009      0.001     -1.610      0.108      -0.002       0.000
    SPY_Rolling_Future_Return_1w     2.9981      0.014    218.085      0.000       2.971       3.025
    ==============================================================================
    Omnibus:                      246.103   Durbin-Watson:                   1.337
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             7382.619
    Skew:                          -1.556   Prob(JB):                         0.00
    Kurtosis:                      21.720   Cond. No.                         25.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_246.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_247.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1m   R-squared:                       0.977
    Model:                                       OLS   Adj. R-squared:                  0.977
    Method:                            Least Squares   F-statistic:                 2.054e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:43:08   Log-Likelihood:                 1034.0
    No. Observations:                            492   AIC:                            -2064.
    Df Residuals:                                490   BIC:                            -2056.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0072      0.001     -5.051      0.000      -0.010      -0.004
    SPY_Rolling_Future_Return_1m     3.0527      0.021    143.318      0.000       3.011       3.095
    ==============================================================================
    Omnibus:                      246.880   Durbin-Watson:                   0.321
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             2046.076
    Skew:                          -2.018   Prob(JB):                         0.00
    Kurtosis:                      12.139   Cond. No.                         15.9
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_249.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_250.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3m   R-squared:                       0.976
    Model:                                       OLS   Adj. R-squared:                  0.976
    Method:                            Least Squares   F-statistic:                 2.001e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:43:10   Log-Likelihood:                 794.88
    No. Observations:                            492   AIC:                            -1586.
    Df Residuals:                                490   BIC:                            -1577.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0291      0.003    -11.077      0.000      -0.034      -0.024
    SPY_Rolling_Future_Return_3m     3.3540      0.024    141.466      0.000       3.307       3.401
    ==============================================================================
    Omnibus:                       75.895   Durbin-Watson:                   0.347
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              485.942
    Skew:                          -0.458   Prob(JB):                    3.01e-106
    Kurtosis:                       7.782   Cond. No.                         11.0
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_252.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_253.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_6m   R-squared:                       0.968
    Model:                                       OLS   Adj. R-squared:                  0.968
    Method:                            Least Squares   F-statistic:                 1.482e+04
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):               0.00
    Time:                                   14:43:13   Log-Likelihood:                 557.26
    No. Observations:                            492   AIC:                            -1111.
    Df Residuals:                                490   BIC:                            -1102.
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.0991      0.006    -17.983      0.000      -0.110      -0.088
    SPY_Rolling_Future_Return_6m     3.8451      0.032    121.754      0.000       3.783       3.907
    ==============================================================================
    Omnibus:                       89.885   Durbin-Watson:                   0.146
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              142.024
    Skew:                          -1.149   Prob(JB):                     1.45e-31
    Kurtosis:                       4.284   Cond. No.                         9.13
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_255.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_256.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_1y   R-squared:                       0.926
    Model:                                       OLS   Adj. R-squared:                  0.926
    Method:                            Least Squares   F-statistic:                     6156.
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):          1.39e-279
    Time:                                   14:43:15   Log-Likelihood:                 241.59
    No. Observations:                            492   AIC:                            -479.2
    Df Residuals:                                490   BIC:                            -470.8
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.2182      0.013    -16.797      0.000      -0.244      -0.193
    SPY_Rolling_Future_Return_1y     4.1968      0.053     78.460      0.000       4.092       4.302
    ==============================================================================
    Omnibus:                      129.416   Durbin-Watson:                   0.094
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              301.681
    Skew:                          -1.350   Prob(JB):                     3.10e-66
    Kurtosis:                       5.725   Cond. No.                         8.35
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_258.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_259.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_2y   R-squared:                       0.943
    Model:                                       OLS   Adj. R-squared:                  0.943
    Method:                            Least Squares   F-statistic:                     8092.
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):          8.78e-307
    Time:                                   14:43:18   Log-Likelihood:                 42.960
    No. Observations:                            492   AIC:                            -81.92
    Df Residuals:                                490   BIC:                            -73.52
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -0.5693      0.022    -26.067      0.000      -0.612      -0.526
    SPY_Rolling_Future_Return_2y     5.1161      0.057     89.953      0.000       5.004       5.228
    ==============================================================================
    Omnibus:                       62.745   Durbin-Watson:                   0.075
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              117.512
    Skew:                          -0.751   Prob(JB):                     3.04e-26
    Kurtosis:                       4.864   Cond. No.                         6.36
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_261.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_262.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_3y   R-squared:                       0.895
    Model:                                       OLS   Adj. R-squared:                  0.895
    Method:                            Least Squares   F-statistic:                     4166.
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):          1.06e-241
    Time:                                   14:43:21   Log-Likelihood:                -134.24
    No. Observations:                            492   AIC:                             272.5
    Df Residuals:                                490   BIC:                             280.9
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -1.2645      0.049    -25.786      0.000      -1.361      -1.168
    SPY_Rolling_Future_Return_3y     6.2301      0.097     64.542      0.000       6.040       6.420
    ==============================================================================
    Omnibus:                       10.395   Durbin-Watson:                   0.052
    Prob(Omnibus):                  0.006   Jarque-Bera (JB):               14.422
    Skew:                           0.184   Prob(JB):                     0.000738
    Kurtosis:                       3.754   Cond. No.                         8.34
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_264.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_265.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_4y   R-squared:                       0.874
    Model:                                       OLS   Adj. R-squared:                  0.874
    Method:                            Least Squares   F-statistic:                     3409.
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):          8.08e-223
    Time:                                   14:43:23   Log-Likelihood:                -226.89
    No. Observations:                            492   AIC:                             457.8
    Df Residuals:                                490   BIC:                             466.2
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -2.5519      0.101    -25.150      0.000      -2.751      -2.353
    SPY_Rolling_Future_Return_4y     7.9918      0.137     58.384      0.000       7.723       8.261
    ==============================================================================
    Omnibus:                       35.379   Durbin-Watson:                   0.062
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               41.084
    Skew:                          -0.696   Prob(JB):                     1.20e-09
    Kurtosis:                       3.261   Cond. No.                         12.2
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_267.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_108_268.png)
    


                                      OLS Regression Results                                 
    =========================================================================================
    Dep. Variable:     UPRO_Rolling_Future_Return_5y   R-squared:                       0.871
    Model:                                       OLS   Adj. R-squared:                  0.870
    Method:                            Least Squares   F-statistic:                     3297.
    Date:                           Wed, 17 Jun 2026   Prob (F-statistic):          9.92e-220
    Time:                                   14:43:27   Log-Likelihood:                -479.38
    No. Observations:                            492   AIC:                             962.8
    Df Residuals:                                490   BIC:                             971.2
    Df Model:                                      1                                         
    Covariance Type:                       nonrobust                                         
    ================================================================================================
                                       coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------------------------
    const                           -3.3977      0.155    -21.877      0.000      -3.703      -3.093
    SPY_Rolling_Future_Return_5y     8.9388      0.156     57.421      0.000       8.633       9.245
    ==============================================================================
    Omnibus:                      107.575   Durbin-Watson:                   0.059
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):              211.213
    Skew:                          -1.205   Prob(JB):                     1.37e-46
    Kurtosis:                       5.120   Cond. No.                         10.6
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.


### Rolling Returns Following Drawdowns Deviation (SPY & UPRO)


```python
rolling_returns_positive_future_returns = pd.DataFrame(index=rolling_windows.keys(), data=rolling_windows.values())
rolling_returns_positive_future_returns.reset_index(inplace=True)
rolling_returns_positive_future_returns.rename(columns={"index":"Period", 0:"Days"}, inplace=True)

for drawdown in drawdown_levels:
    temp = rolling_returns_drawdown_stats.loc[rolling_returns_drawdown_stats["Drawdown"] == drawdown]
    temp = temp[["Period", "Positive_Future_Percentage"]]
    temp.rename(columns={"Positive_Future_Percentage" : f"Positive_Future_Percentage_Post_{drawdown}_Drawdown"}, inplace=True)
    rolling_returns_positive_future_returns = pd.merge(rolling_returns_positive_future_returns, temp, left_on="Period", right_on="Period", how="outer")
    rolling_returns_positive_future_returns.sort_values(by="Days", ascending=True, inplace=True)

rolling_returns_positive_future_returns.drop(columns={"Days"}, inplace=True)
rolling_returns_positive_future_returns.reset_index(drop=True, inplace=True)
pandas_set_decimal_places(2)
display(rolling_returns_positive_future_returns.set_index("Period"))
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
      <th>Positive_Future_Percentage_Post_-0.1_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.2_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.3_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.4_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.5_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.6_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.7_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.8_Drawdown</th>
      <th>Positive_Future_Percentage_Post_-0.9_Drawdown</th>
    </tr>
    <tr>
      <th>Period</th>
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
      <th>1d</th>
      <td>0.54</td>
      <td>0.54</td>
      <td>0.54</td>
      <td>0.54</td>
      <td>0.54</td>
      <td>0.55</td>
      <td>0.55</td>
      <td>0.55</td>
      <td>0.55</td>
    </tr>
    <tr>
      <th>1w</th>
      <td>0.57</td>
      <td>0.57</td>
      <td>0.56</td>
      <td>0.56</td>
      <td>0.56</td>
      <td>0.56</td>
      <td>0.57</td>
      <td>0.57</td>
      <td>0.59</td>
    </tr>
    <tr>
      <th>1m</th>
      <td>0.63</td>
      <td>0.62</td>
      <td>0.61</td>
      <td>0.61</td>
      <td>0.62</td>
      <td>0.62</td>
      <td>0.62</td>
      <td>0.65</td>
      <td>0.67</td>
    </tr>
    <tr>
      <th>3m</th>
      <td>0.67</td>
      <td>0.65</td>
      <td>0.63</td>
      <td>0.63</td>
      <td>0.65</td>
      <td>0.65</td>
      <td>0.66</td>
      <td>0.68</td>
      <td>0.77</td>
    </tr>
    <tr>
      <th>6m</th>
      <td>0.70</td>
      <td>0.69</td>
      <td>0.68</td>
      <td>0.67</td>
      <td>0.69</td>
      <td>0.70</td>
      <td>0.73</td>
      <td>0.75</td>
      <td>0.79</td>
    </tr>
    <tr>
      <th>1y</th>
      <td>0.74</td>
      <td>0.73</td>
      <td>0.73</td>
      <td>0.73</td>
      <td>0.74</td>
      <td>0.79</td>
      <td>0.84</td>
      <td>0.87</td>
      <td>0.96</td>
    </tr>
    <tr>
      <th>2y</th>
      <td>0.77</td>
      <td>0.78</td>
      <td>0.78</td>
      <td>0.78</td>
      <td>0.77</td>
      <td>0.81</td>
      <td>0.92</td>
      <td>0.99</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>3y</th>
      <td>0.72</td>
      <td>0.72</td>
      <td>0.73</td>
      <td>0.73</td>
      <td>0.72</td>
      <td>0.74</td>
      <td>0.87</td>
      <td>0.99</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>4y</th>
      <td>0.69</td>
      <td>0.69</td>
      <td>0.68</td>
      <td>0.69</td>
      <td>0.68</td>
      <td>0.71</td>
      <td>0.81</td>
      <td>1.00</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>5y</th>
      <td>0.66</td>
      <td>0.66</td>
      <td>0.66</td>
      <td>0.66</td>
      <td>0.65</td>
      <td>0.67</td>
      <td>0.74</td>
      <td>0.97</td>
      <td>1.00</td>
    </tr>
  </tbody>
</table>
</div>



```python
plot_scatter(
    df=rolling_returns_positive_future_returns,
    x_plot_column="Period",
    y_plot_columns=[col for col in rolling_returns_positive_future_returns.columns if col != "Period"],
    title="UPRO Future Return by Time Period Post Drawdown",
    x_label="Rolling Return Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Positive Future Return Percentage",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_111_0.png)
    


This plot summarizes the future rolling returns well. Similar as to QQQ/TQQQ, for rolling returns up to ~3 months *following* all drawdown levels, we see the rolling returns of UPRO are positive ~65% of the time.

As we extend the time horizon, out to the 2y, 3y, 4y, and 5y mark, the percentage of positive rolling returns following an 80% drawdown increases significantly, and is greater than *95%*. This suggests that while the volatility decay effect is present for UPRO, it may not be as severe as that of TQQQ, which could be due to the less extreme return profile of SPY compared to QQQ.

As an investor, this suggests that the optimal time to buy UPRO would be following a drawdown of 50% or more, and holding for at least 2 years. One could dollar cost average into UPRO following a drawdown of 50% or more, and continue to add to the position with a consistent contribution schedule until all capital has been allocated.

## Future Investigation

There are a couple of ideas for future investigation that would be interesting to explore:

* Expand the analysis of SPY/UPRO to SPX/UPRO (using Bloomberg data for SPX), and extrapolate UPRO return data back to January of 1975.
* Implement and backtest a strategy that DCA's into UPRO on a consistent schdule (monthly, quarterly, etc.)


