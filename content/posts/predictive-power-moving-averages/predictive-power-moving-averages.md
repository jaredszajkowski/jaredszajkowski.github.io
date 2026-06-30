## Introduction

The idea of time series momentum (AKA, trend following) heavily relies on the idea that if a price is higher than its recent moving average, it is more likely to continue to be higher than its moving average in the future, and vice versa. In this post, we will investigate the idea of moving averages, and whether at a given point in time a price that is higher or lower than the moving average up until that point in time has any predictive power for future returns. 

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

For this exercise, we will investigate the predictive power of moving averages for the following ETFs:

* IVV - iShares Core S&P 500 ETF
* EFA - iShares MSCI EAFE ETF
* EEM - iShares MSCI Emerging Markets ETF
* GSG - iShares S&P GSCI Commodity-Indexed Trust
* IAU - iShares Gold Trust
* IEF - iShares 7-10 Year Treasury Bond ETF
* TLT - iShares 20+ Year Treasury Bond ETF

We'll use the adjusted close prices for each of these ETFs.

## Acquire Data

First, let's get the data for these ETFs. If we already have the desired data, we can load it from a local pickle file. Otherwise, we can download it from Yahoo Finance using the `yf_pull_data` function.


```python
pandas_set_decimal_places(2)

# Create a list of the ETF tickers
fund_list = ["IVV", "EFA", "EEM", "GSG", "IAU", "IEF", "TLT"]
```


```python
# Pull data for each ETF and cache it locally
for fund in fund_list:
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        adjusted=False,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=False,
    )
```

## Create Data Dictionary

Then, create a dictionary to hold the data for each ETF, and plot the adjusted close price for each ETF over time.


```python
# Create an empty dictionary to hold the data for each ETF
fund_data = {}

# Load the data for each ETF, rename the columns to include the ticker, store it in the fund_data dictionary
for fund in fund_list:
    data = load_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        timeframe="Daily",
        file_format="pickle",
    )

    data = data.rename(columns={
        "Adj Close": f"{fund}_Adj_Close",
        "Close": f"{fund}_Close",
        "High": f"{fund}_High",
        "Low": f"{fund}_Low",
        "Open": f"{fund}_Open",
        "Volume": f"{fund}_Volume"
    })
    
    fund_data[fund] = data
```

## Plot Data

Next, we will:

* Check the date ranges
* Plot the adjusted close prices
* Plot the cumulative returns
* Plot the drawdowns


```python
for fund, data in fund_data.items():    
    display(data)

    plot_time_series(
        df=data,
        plot_start_date=None,
        plot_end_date=None,
        plot_columns=[f"{fund}_Adj_Close"],
        title=f"{fund} Adjusted Close Price",
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
      <th>IVV_Close</th>
      <th>IVV_High</th>
      <th>IVV_Low</th>
      <th>IVV_Open</th>
      <th>IVV_Volume</th>
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
      <th>2000-05-19</th>
      <td>88.33</td>
      <td>140.69</td>
      <td>142.66</td>
      <td>140.25</td>
      <td>142.66</td>
      <td>775500</td>
    </tr>
    <tr>
      <th>2000-05-22</th>
      <td>87.79</td>
      <td>139.81</td>
      <td>140.59</td>
      <td>136.81</td>
      <td>140.59</td>
      <td>1850600</td>
    </tr>
    <tr>
      <th>2000-05-23</th>
      <td>86.45</td>
      <td>137.69</td>
      <td>140.22</td>
      <td>137.69</td>
      <td>140.22</td>
      <td>373900</td>
    </tr>
    <tr>
      <th>2000-05-24</th>
      <td>87.75</td>
      <td>139.75</td>
      <td>140.06</td>
      <td>136.66</td>
      <td>137.75</td>
      <td>400300</td>
    </tr>
    <tr>
      <th>2000-05-25</th>
      <td>86.94</td>
      <td>138.47</td>
      <td>140.94</td>
      <td>137.88</td>
      <td>140.03</td>
      <td>69600</td>
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
      <th>2026-06-22</th>
      <td>747.78</td>
      <td>747.78</td>
      <td>753.66</td>
      <td>746.58</td>
      <td>751.16</td>
      <td>16420300</td>
    </tr>
    <tr>
      <th>2026-06-23</th>
      <td>737.14</td>
      <td>737.14</td>
      <td>743.02</td>
      <td>735.75</td>
      <td>737.15</td>
      <td>15553500</td>
    </tr>
    <tr>
      <th>2026-06-24</th>
      <td>736.66</td>
      <td>736.66</td>
      <td>743.40</td>
      <td>734.26</td>
      <td>738.56</td>
      <td>9014700</td>
    </tr>
    <tr>
      <th>2026-06-25</th>
      <td>736.50</td>
      <td>736.50</td>
      <td>742.80</td>
      <td>733.04</td>
      <td>742.32</td>
      <td>25573300</td>
    </tr>
    <tr>
      <th>2026-06-26</th>
      <td>730.17</td>
      <td>730.17</td>
      <td>739.97</td>
      <td>728.74</td>
      <td>732.29</td>
      <td>5944000</td>
    </tr>
  </tbody>
</table>
<p>6564 rows × 6 columns</p>
</div>



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_19_1.png)
    



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
      <th>EFA_Adj_Close</th>
      <th>EFA_Close</th>
      <th>EFA_High</th>
      <th>EFA_Low</th>
      <th>EFA_Open</th>
      <th>EFA_Volume</th>
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
      <th>2001-08-27</th>
      <td>21.86</td>
      <td>42.83</td>
      <td>42.92</td>
      <td>42.76</td>
      <td>42.92</td>
      <td>44700</td>
    </tr>
    <tr>
      <th>2001-08-28</th>
      <td>21.61</td>
      <td>42.34</td>
      <td>42.58</td>
      <td>42.26</td>
      <td>42.53</td>
      <td>319800</td>
    </tr>
    <tr>
      <th>2001-08-29</th>
      <td>21.51</td>
      <td>42.15</td>
      <td>42.47</td>
      <td>42.10</td>
      <td>42.45</td>
      <td>128400</td>
    </tr>
    <tr>
      <th>2001-08-30</th>
      <td>21.20</td>
      <td>41.55</td>
      <td>41.67</td>
      <td>41.43</td>
      <td>41.67</td>
      <td>36900</td>
    </tr>
    <tr>
      <th>2001-08-31</th>
      <td>21.25</td>
      <td>41.65</td>
      <td>41.72</td>
      <td>41.47</td>
      <td>41.53</td>
      <td>1656900</td>
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
      <th>2026-06-22</th>
      <td>104.58</td>
      <td>104.58</td>
      <td>104.84</td>
      <td>104.43</td>
      <td>104.59</td>
      <td>9596200</td>
    </tr>
    <tr>
      <th>2026-06-23</th>
      <td>102.46</td>
      <td>102.46</td>
      <td>103.02</td>
      <td>102.32</td>
      <td>102.38</td>
      <td>17425700</td>
    </tr>
    <tr>
      <th>2026-06-24</th>
      <td>102.26</td>
      <td>102.26</td>
      <td>102.65</td>
      <td>101.92</td>
      <td>102.24</td>
      <td>12504200</td>
    </tr>
    <tr>
      <th>2026-06-25</th>
      <td>103.15</td>
      <td>103.15</td>
      <td>103.73</td>
      <td>102.73</td>
      <td>103.48</td>
      <td>13135400</td>
    </tr>
    <tr>
      <th>2026-06-26</th>
      <td>102.54</td>
      <td>102.54</td>
      <td>103.07</td>
      <td>102.30</td>
      <td>102.46</td>
      <td>21219200</td>
    </tr>
  </tbody>
</table>
<p>6244 rows × 6 columns</p>
</div>



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_19_3.png)
    



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
      <th>EEM_Adj_Close</th>
      <th>EEM_Close</th>
      <th>EEM_High</th>
      <th>EEM_Low</th>
      <th>EEM_Open</th>
      <th>EEM_Volume</th>
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
      <th>2003-04-14</th>
      <td>7.20</td>
      <td>11.22</td>
      <td>11.22</td>
      <td>11.14</td>
      <td>11.14</td>
      <td>93600</td>
    </tr>
    <tr>
      <th>2003-04-15</th>
      <td>7.28</td>
      <td>11.36</td>
      <td>11.39</td>
      <td>11.29</td>
      <td>11.29</td>
      <td>421200</td>
    </tr>
    <tr>
      <th>2003-04-16</th>
      <td>7.37</td>
      <td>11.49</td>
      <td>11.53</td>
      <td>11.48</td>
      <td>11.48</td>
      <td>9000</td>
    </tr>
    <tr>
      <th>2003-04-17</th>
      <td>7.42</td>
      <td>11.57</td>
      <td>11.57</td>
      <td>11.53</td>
      <td>11.55</td>
      <td>17100</td>
    </tr>
    <tr>
      <th>2003-04-21</th>
      <td>7.42</td>
      <td>11.56</td>
      <td>11.58</td>
      <td>11.56</td>
      <td>11.58</td>
      <td>72900</td>
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
      <th>2026-06-22</th>
      <td>71.21</td>
      <td>71.21</td>
      <td>71.57</td>
      <td>70.99</td>
      <td>71.29</td>
      <td>25302200</td>
    </tr>
    <tr>
      <th>2026-06-23</th>
      <td>67.17</td>
      <td>67.17</td>
      <td>68.23</td>
      <td>67.07</td>
      <td>67.25</td>
      <td>39069000</td>
    </tr>
    <tr>
      <th>2026-06-24</th>
      <td>67.25</td>
      <td>67.25</td>
      <td>67.61</td>
      <td>66.60</td>
      <td>67.38</td>
      <td>22973300</td>
    </tr>
    <tr>
      <th>2026-06-25</th>
      <td>67.96</td>
      <td>67.96</td>
      <td>68.99</td>
      <td>67.27</td>
      <td>68.91</td>
      <td>24474400</td>
    </tr>
    <tr>
      <th>2026-06-26</th>
      <td>67.19</td>
      <td>67.19</td>
      <td>67.72</td>
      <td>66.27</td>
      <td>66.34</td>
      <td>24158700</td>
    </tr>
  </tbody>
</table>
<p>5838 rows × 6 columns</p>
</div>



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_19_5.png)
    



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
      <th>GSG_Adj_Close</th>
      <th>GSG_Close</th>
      <th>GSG_High</th>
      <th>GSG_Low</th>
      <th>GSG_Open</th>
      <th>GSG_Volume</th>
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
      <th>2006-07-21</th>
      <td>49.25</td>
      <td>49.25</td>
      <td>49.64</td>
      <td>49.22</td>
      <td>49.35</td>
      <td>37400</td>
    </tr>
    <tr>
      <th>2006-07-24</th>
      <td>49.70</td>
      <td>49.70</td>
      <td>49.70</td>
      <td>48.98</td>
      <td>49.25</td>
      <td>220900</td>
    </tr>
    <tr>
      <th>2006-07-25</th>
      <td>49.25</td>
      <td>49.25</td>
      <td>50.15</td>
      <td>49.20</td>
      <td>50.15</td>
      <td>41600</td>
    </tr>
    <tr>
      <th>2006-07-26</th>
      <td>49.62</td>
      <td>49.62</td>
      <td>49.80</td>
      <td>49.35</td>
      <td>49.35</td>
      <td>17800</td>
    </tr>
    <tr>
      <th>2006-07-27</th>
      <td>50.15</td>
      <td>50.15</td>
      <td>50.35</td>
      <td>49.93</td>
      <td>50.15</td>
      <td>41800</td>
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
      <th>2026-06-22</th>
      <td>29.25</td>
      <td>29.25</td>
      <td>29.38</td>
      <td>29.12</td>
      <td>29.34</td>
      <td>567600</td>
    </tr>
    <tr>
      <th>2026-06-23</th>
      <td>28.95</td>
      <td>28.95</td>
      <td>28.99</td>
      <td>28.79</td>
      <td>28.86</td>
      <td>572000</td>
    </tr>
    <tr>
      <th>2026-06-24</th>
      <td>28.23</td>
      <td>28.23</td>
      <td>28.46</td>
      <td>28.21</td>
      <td>28.26</td>
      <td>600700</td>
    </tr>
    <tr>
      <th>2026-06-25</th>
      <td>28.88</td>
      <td>28.88</td>
      <td>28.93</td>
      <td>28.35</td>
      <td>28.35</td>
      <td>556900</td>
    </tr>
    <tr>
      <th>2026-06-26</th>
      <td>28.39</td>
      <td>28.39</td>
      <td>28.49</td>
      <td>28.27</td>
      <td>28.46</td>
      <td>510000</td>
    </tr>
  </tbody>
</table>
<p>5014 rows × 6 columns</p>
</div>



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_19_7.png)
    



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
      <th>IAU_Adj_Close</th>
      <th>IAU_Close</th>
      <th>IAU_High</th>
      <th>IAU_Low</th>
      <th>IAU_Open</th>
      <th>IAU_Volume</th>
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
      <th>2005-01-28</th>
      <td>8.54</td>
      <td>8.54</td>
      <td>8.55</td>
      <td>8.49</td>
      <td>8.55</td>
      <td>2888500</td>
    </tr>
    <tr>
      <th>2005-01-31</th>
      <td>8.45</td>
      <td>8.45</td>
      <td>8.46</td>
      <td>8.40</td>
      <td>8.45</td>
      <td>759500</td>
    </tr>
    <tr>
      <th>2005-02-01</th>
      <td>8.42</td>
      <td>8.42</td>
      <td>8.43</td>
      <td>8.39</td>
      <td>8.42</td>
      <td>347500</td>
    </tr>
    <tr>
      <th>2005-02-02</th>
      <td>8.45</td>
      <td>8.45</td>
      <td>8.45</td>
      <td>8.41</td>
      <td>8.45</td>
      <td>1496500</td>
    </tr>
    <tr>
      <th>2005-02-03</th>
      <td>8.34</td>
      <td>8.34</td>
      <td>8.35</td>
      <td>8.30</td>
      <td>8.32</td>
      <td>534000</td>
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
      <th>2026-06-22</th>
      <td>78.80</td>
      <td>78.80</td>
      <td>79.18</td>
      <td>78.42</td>
      <td>78.75</td>
      <td>9674400</td>
    </tr>
    <tr>
      <th>2026-06-23</th>
      <td>77.33</td>
      <td>77.33</td>
      <td>77.94</td>
      <td>77.29</td>
      <td>77.40</td>
      <td>4652100</td>
    </tr>
    <tr>
      <th>2026-06-24</th>
      <td>74.99</td>
      <td>74.99</td>
      <td>76.01</td>
      <td>74.44</td>
      <td>74.78</td>
      <td>10609200</td>
    </tr>
    <tr>
      <th>2026-06-25</th>
      <td>75.71</td>
      <td>75.71</td>
      <td>76.04</td>
      <td>75.18</td>
      <td>75.63</td>
      <td>6287200</td>
    </tr>
    <tr>
      <th>2026-06-26</th>
      <td>76.56</td>
      <td>76.56</td>
      <td>77.02</td>
      <td>76.07</td>
      <td>76.29</td>
      <td>4671800</td>
    </tr>
  </tbody>
</table>
<p>5386 rows × 6 columns</p>
</div>



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_19_9.png)
    



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
      <th>IEF_Adj_Close</th>
      <th>IEF_Close</th>
      <th>IEF_High</th>
      <th>IEF_Low</th>
      <th>IEF_Open</th>
      <th>IEF_Volume</th>
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
      <th>2002-07-30</th>
      <td>40.55</td>
      <td>81.77</td>
      <td>82.12</td>
      <td>81.70</td>
      <td>81.94</td>
      <td>41300</td>
    </tr>
    <tr>
      <th>2002-07-31</th>
      <td>40.93</td>
      <td>82.52</td>
      <td>82.58</td>
      <td>82.05</td>
      <td>82.05</td>
      <td>32600</td>
    </tr>
    <tr>
      <th>2002-08-01</th>
      <td>41.10</td>
      <td>82.86</td>
      <td>82.90</td>
      <td>82.52</td>
      <td>82.54</td>
      <td>71400</td>
    </tr>
    <tr>
      <th>2002-08-02</th>
      <td>41.41</td>
      <td>83.50</td>
      <td>83.70</td>
      <td>82.90</td>
      <td>83.02</td>
      <td>120300</td>
    </tr>
    <tr>
      <th>2002-08-05</th>
      <td>41.62</td>
      <td>83.92</td>
      <td>83.92</td>
      <td>83.53</td>
      <td>83.68</td>
      <td>159300</td>
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
      <th>2026-06-22</th>
      <td>94.00</td>
      <td>94.00</td>
      <td>94.13</td>
      <td>93.97</td>
      <td>94.11</td>
      <td>4572200</td>
    </tr>
    <tr>
      <th>2026-06-23</th>
      <td>94.12</td>
      <td>94.12</td>
      <td>94.26</td>
      <td>94.09</td>
      <td>94.16</td>
      <td>6504600</td>
    </tr>
    <tr>
      <th>2026-06-24</th>
      <td>94.73</td>
      <td>94.73</td>
      <td>94.78</td>
      <td>94.56</td>
      <td>94.57</td>
      <td>5179800</td>
    </tr>
    <tr>
      <th>2026-06-25</th>
      <td>94.79</td>
      <td>94.79</td>
      <td>95.02</td>
      <td>94.78</td>
      <td>94.86</td>
      <td>5630500</td>
    </tr>
    <tr>
      <th>2026-06-26</th>
      <td>95.03</td>
      <td>95.03</td>
      <td>95.08</td>
      <td>94.83</td>
      <td>94.83</td>
      <td>5584100</td>
    </tr>
  </tbody>
</table>
<p>6016 rows × 6 columns</p>
</div>



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_19_11.png)
    



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
      <th>TLT_Adj_Close</th>
      <th>TLT_Close</th>
      <th>TLT_High</th>
      <th>TLT_Low</th>
      <th>TLT_Open</th>
      <th>TLT_Volume</th>
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
      <th>2002-07-30</th>
      <td>35.97</td>
      <td>81.52</td>
      <td>81.90</td>
      <td>81.52</td>
      <td>81.75</td>
      <td>6100</td>
    </tr>
    <tr>
      <th>2002-07-31</th>
      <td>36.41</td>
      <td>82.53</td>
      <td>82.80</td>
      <td>81.90</td>
      <td>81.95</td>
      <td>29400</td>
    </tr>
    <tr>
      <th>2002-08-01</th>
      <td>36.62</td>
      <td>83.00</td>
      <td>83.02</td>
      <td>82.54</td>
      <td>82.54</td>
      <td>25000</td>
    </tr>
    <tr>
      <th>2002-08-02</th>
      <td>37.00</td>
      <td>83.85</td>
      <td>84.10</td>
      <td>82.88</td>
      <td>83.16</td>
      <td>52800</td>
    </tr>
    <tr>
      <th>2002-08-05</th>
      <td>37.16</td>
      <td>84.22</td>
      <td>84.44</td>
      <td>83.85</td>
      <td>84.04</td>
      <td>61100</td>
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
      <th>2026-06-22</th>
      <td>86.09</td>
      <td>86.09</td>
      <td>86.33</td>
      <td>85.97</td>
      <td>86.30</td>
      <td>28595100</td>
    </tr>
    <tr>
      <th>2026-06-23</th>
      <td>86.20</td>
      <td>86.20</td>
      <td>86.43</td>
      <td>86.10</td>
      <td>86.12</td>
      <td>19145500</td>
    </tr>
    <tr>
      <th>2026-06-24</th>
      <td>87.38</td>
      <td>87.38</td>
      <td>87.47</td>
      <td>87.12</td>
      <td>87.15</td>
      <td>41837000</td>
    </tr>
    <tr>
      <th>2026-06-25</th>
      <td>87.35</td>
      <td>87.35</td>
      <td>87.79</td>
      <td>87.29</td>
      <td>87.58</td>
      <td>28380000</td>
    </tr>
    <tr>
      <th>2026-06-26</th>
      <td>87.36</td>
      <td>87.36</td>
      <td>87.37</td>
      <td>87.00</td>
      <td>87.01</td>
      <td>21650800</td>
    </tr>
  </tbody>
</table>
<p>6016 rows × 6 columns</p>
</div>



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_19_13.png)
    



```python
# Create empty DF
data_merged = pd.DataFrame()

# Merge all data, calc cumulative returns, drawdowns
for fund, data in fund_data.items():
    data_merged = data_merged.merge(data[[f"{fund}_Adj_Close"]], left_index=True, right_index=True, how='outer') if not data_merged.empty else data[[f"{fund}_Adj_Close"]]
    data_merged[f"{fund}_Return"] = data_merged[f"{fund}_Adj_Close"].pct_change()
    data_merged[f"{fund}_Cumulative_Return"] = (1 + data_merged[f"{fund}_Return"]).cumprod() - 1
    data_merged[f"{fund}_Cumulative_Return_Plus_One"] = 1 + data_merged[f"{fund}_Cumulative_Return"]
    data_merged[f"{fund}_Rolling_Max"] = data_merged[f"{fund}_Cumulative_Return_Plus_One"].cummax()
    data_merged[f"{fund}_Drawdown"] = data_merged[f"{fund}_Cumulative_Return_Plus_One"] / data_merged[f"{fund}_Rolling_Max"] - 1
    data_merged.drop(columns=[f"{fund}_Cumulative_Return_Plus_One", f"{fund}_Rolling_Max"], inplace=True)
        
display(data_merged)
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
      <th>IVV_Return</th>
      <th>IVV_Cumulative_Return</th>
      <th>IVV_Drawdown</th>
      <th>EFA_Adj_Close</th>
      <th>EFA_Return</th>
      <th>EFA_Cumulative_Return</th>
      <th>EFA_Drawdown</th>
      <th>EEM_Adj_Close</th>
      <th>EEM_Return</th>
      <th>...</th>
      <th>IAU_Cumulative_Return</th>
      <th>IAU_Drawdown</th>
      <th>IEF_Adj_Close</th>
      <th>IEF_Return</th>
      <th>IEF_Cumulative_Return</th>
      <th>IEF_Drawdown</th>
      <th>TLT_Adj_Close</th>
      <th>TLT_Return</th>
      <th>TLT_Cumulative_Return</th>
      <th>TLT_Drawdown</th>
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
      <th>2000-05-19</th>
      <td>88.33</td>
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
      <th>2000-05-22</th>
      <td>87.79</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>0.00</td>
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
      <th>2000-05-23</th>
      <td>86.45</td>
      <td>-0.02</td>
      <td>-0.02</td>
      <td>-0.02</td>
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
      <th>2000-05-24</th>
      <td>87.75</td>
      <td>0.01</td>
      <td>-0.01</td>
      <td>-0.00</td>
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
      <th>2000-05-25</th>
      <td>86.94</td>
      <td>-0.01</td>
      <td>-0.02</td>
      <td>-0.01</td>
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
      <th>2026-06-22</th>
      <td>747.78</td>
      <td>-0.00</td>
      <td>7.47</td>
      <td>-0.02</td>
      <td>104.58</td>
      <td>0.00</td>
      <td>3.78</td>
      <td>0.00</td>
      <td>71.21</td>
      <td>0.01</td>
      <td>...</td>
      <td>8.23</td>
      <td>-0.22</td>
      <td>94.00</td>
      <td>-0.00</td>
      <td>1.32</td>
      <td>-0.11</td>
      <td>86.09</td>
      <td>-0.01</td>
      <td>1.39</td>
      <td>-0.40</td>
    </tr>
    <tr>
      <th>2026-06-23</th>
      <td>737.14</td>
      <td>-0.01</td>
      <td>7.34</td>
      <td>-0.03</td>
      <td>102.46</td>
      <td>-0.02</td>
      <td>3.69</td>
      <td>-0.02</td>
      <td>67.17</td>
      <td>-0.06</td>
      <td>...</td>
      <td>8.06</td>
      <td>-0.24</td>
      <td>94.12</td>
      <td>0.00</td>
      <td>1.32</td>
      <td>-0.11</td>
      <td>86.20</td>
      <td>0.00</td>
      <td>1.40</td>
      <td>-0.40</td>
    </tr>
    <tr>
      <th>2026-06-24</th>
      <td>736.66</td>
      <td>-0.00</td>
      <td>7.34</td>
      <td>-0.03</td>
      <td>102.26</td>
      <td>-0.00</td>
      <td>3.68</td>
      <td>-0.02</td>
      <td>67.25</td>
      <td>0.00</td>
      <td>...</td>
      <td>7.78</td>
      <td>-0.26</td>
      <td>94.73</td>
      <td>0.01</td>
      <td>1.34</td>
      <td>-0.11</td>
      <td>87.38</td>
      <td>0.01</td>
      <td>1.43</td>
      <td>-0.39</td>
    </tr>
    <tr>
      <th>2026-06-25</th>
      <td>736.50</td>
      <td>-0.00</td>
      <td>7.34</td>
      <td>-0.03</td>
      <td>103.15</td>
      <td>0.01</td>
      <td>3.72</td>
      <td>-0.01</td>
      <td>67.96</td>
      <td>0.01</td>
      <td>...</td>
      <td>7.87</td>
      <td>-0.25</td>
      <td>94.79</td>
      <td>0.00</td>
      <td>1.34</td>
      <td>-0.11</td>
      <td>87.35</td>
      <td>-0.00</td>
      <td>1.43</td>
      <td>-0.39</td>
    </tr>
    <tr>
      <th>2026-06-26</th>
      <td>730.17</td>
      <td>-0.01</td>
      <td>7.27</td>
      <td>-0.04</td>
      <td>102.54</td>
      <td>-0.01</td>
      <td>3.69</td>
      <td>-0.02</td>
      <td>67.19</td>
      <td>-0.01</td>
      <td>...</td>
      <td>7.97</td>
      <td>-0.25</td>
      <td>95.03</td>
      <td>0.00</td>
      <td>1.34</td>
      <td>-0.10</td>
      <td>87.36</td>
      <td>0.00</td>
      <td>1.43</td>
      <td>-0.39</td>
    </tr>
  </tbody>
</table>
<p>6564 rows × 28 columns</p>
</div>


And now the plots for the cumulative returns and drawdowns:


```python
plot_time_series(
    df=data_merged,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[col for col in data_merged.columns if "Cumulative_Return" in col],
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

plot_time_series(
    df=data_merged,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[col for col in data_merged.columns if "Drawdown" in col],
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


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_22_0.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_22_1.png)
    


This time we'll drop the empty rows to give a more accurate comparison, but this will reduce our data set to the inception of GSG in 2006:


```python
# Create empty DF
data_merged_aligned = pd.DataFrame()

# Merge all data, calc cumulative returns, drawdowns
for fund, data in fund_data.items():
    data_merged_aligned = data_merged_aligned.merge(data[[f"{fund}_Adj_Close"]], left_index=True, right_index=True, how='outer') if not data_merged_aligned.empty else data[[f"{fund}_Adj_Close"]]
    data_merged_aligned = data_merged_aligned.dropna()

for fund in fund_data.keys():
    data_merged_aligned[f"{fund}_Return"] = data_merged_aligned[f"{fund}_Adj_Close"].pct_change()
    data_merged_aligned[f"{fund}_Cumulative_Return"] = (1 + data_merged_aligned[f"{fund}_Return"]).cumprod() - 1
    data_merged_aligned[f"{fund}_Cumulative_Return_Plus_One"] = 1 + data_merged_aligned[f"{fund}_Cumulative_Return"]
    data_merged_aligned[f"{fund}_Rolling_Max"] = data_merged_aligned[f"{fund}_Cumulative_Return_Plus_One"].cummax()
    data_merged_aligned[f"{fund}_Drawdown"] = data_merged_aligned[f"{fund}_Cumulative_Return_Plus_One"] / data_merged_aligned[f"{fund}_Rolling_Max"] - 1
    data_merged_aligned.drop(columns=[f"{fund}_Cumulative_Return_Plus_One", f"{fund}_Rolling_Max"], inplace=True)
        
display(data_merged_aligned)
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
      <th>EFA_Adj_Close</th>
      <th>EEM_Adj_Close</th>
      <th>GSG_Adj_Close</th>
      <th>IAU_Adj_Close</th>
      <th>IEF_Adj_Close</th>
      <th>TLT_Adj_Close</th>
      <th>IVV_Return</th>
      <th>IVV_Cumulative_Return</th>
      <th>IVV_Drawdown</th>
      <th>...</th>
      <th>GSG_Drawdown</th>
      <th>IAU_Return</th>
      <th>IAU_Cumulative_Return</th>
      <th>IAU_Drawdown</th>
      <th>IEF_Return</th>
      <th>IEF_Cumulative_Return</th>
      <th>IEF_Drawdown</th>
      <th>TLT_Return</th>
      <th>TLT_Cumulative_Return</th>
      <th>TLT_Drawdown</th>
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
      <th>2006-07-21</th>
      <td>85.98</td>
      <td>34.42</td>
      <td>19.76</td>
      <td>49.25</td>
      <td>12.37</td>
      <td>48.32</td>
      <td>45.51</td>
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
      <th>2006-07-24</th>
      <td>87.44</td>
      <td>35.04</td>
      <td>20.65</td>
      <td>49.70</td>
      <td>12.22</td>
      <td>48.32</td>
      <td>45.49</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.00</td>
      <td>...</td>
      <td>0.00</td>
      <td>-0.01</td>
      <td>-0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>2006-07-25</th>
      <td>87.78</td>
      <td>35.03</td>
      <td>20.70</td>
      <td>49.25</td>
      <td>12.34</td>
      <td>48.28</td>
      <td>45.35</td>
      <td>0.00</td>
      <td>0.02</td>
      <td>0.00</td>
      <td>...</td>
      <td>-0.01</td>
      <td>0.01</td>
      <td>-0.00</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
    </tr>
    <tr>
      <th>2006-07-26</th>
      <td>87.95</td>
      <td>35.28</td>
      <td>20.62</td>
      <td>49.62</td>
      <td>12.40</td>
      <td>48.40</td>
      <td>45.52</td>
      <td>0.00</td>
      <td>0.02</td>
      <td>0.00</td>
      <td>...</td>
      <td>-0.00</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>2006-07-27</th>
      <td>87.83</td>
      <td>35.50</td>
      <td>20.90</td>
      <td>50.15</td>
      <td>12.59</td>
      <td>48.39</td>
      <td>45.45</td>
      <td>-0.00</td>
      <td>0.02</td>
      <td>-0.00</td>
      <td>...</td>
      <td>0.00</td>
      <td>0.02</td>
      <td>0.02</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
      <td>-0.00</td>
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
      <th>2026-06-22</th>
      <td>747.78</td>
      <td>104.58</td>
      <td>71.21</td>
      <td>29.25</td>
      <td>78.80</td>
      <td>94.00</td>
      <td>86.09</td>
      <td>-0.00</td>
      <td>7.70</td>
      <td>-0.02</td>
      <td>...</td>
      <td>-0.62</td>
      <td>-0.01</td>
      <td>5.37</td>
      <td>-0.22</td>
      <td>-0.00</td>
      <td>0.95</td>
      <td>-0.11</td>
      <td>-0.01</td>
      <td>0.89</td>
      <td>-0.40</td>
    </tr>
    <tr>
      <th>2026-06-23</th>
      <td>737.14</td>
      <td>102.46</td>
      <td>67.17</td>
      <td>28.95</td>
      <td>77.33</td>
      <td>94.12</td>
      <td>86.20</td>
      <td>-0.01</td>
      <td>7.57</td>
      <td>-0.03</td>
      <td>...</td>
      <td>-0.62</td>
      <td>-0.02</td>
      <td>5.25</td>
      <td>-0.24</td>
      <td>0.00</td>
      <td>0.95</td>
      <td>-0.11</td>
      <td>0.00</td>
      <td>0.89</td>
      <td>-0.40</td>
    </tr>
    <tr>
      <th>2026-06-24</th>
      <td>736.66</td>
      <td>102.26</td>
      <td>67.25</td>
      <td>28.23</td>
      <td>74.99</td>
      <td>94.73</td>
      <td>87.38</td>
      <td>-0.00</td>
      <td>7.57</td>
      <td>-0.03</td>
      <td>...</td>
      <td>-0.63</td>
      <td>-0.03</td>
      <td>5.06</td>
      <td>-0.26</td>
      <td>0.01</td>
      <td>0.96</td>
      <td>-0.11</td>
      <td>0.01</td>
      <td>0.92</td>
      <td>-0.39</td>
    </tr>
    <tr>
      <th>2026-06-25</th>
      <td>736.50</td>
      <td>103.15</td>
      <td>67.96</td>
      <td>28.88</td>
      <td>75.71</td>
      <td>94.79</td>
      <td>87.35</td>
      <td>-0.00</td>
      <td>7.57</td>
      <td>-0.03</td>
      <td>...</td>
      <td>-0.62</td>
      <td>0.01</td>
      <td>5.12</td>
      <td>-0.25</td>
      <td>0.00</td>
      <td>0.96</td>
      <td>-0.11</td>
      <td>-0.00</td>
      <td>0.92</td>
      <td>-0.39</td>
    </tr>
    <tr>
      <th>2026-06-26</th>
      <td>730.17</td>
      <td>102.54</td>
      <td>67.19</td>
      <td>28.39</td>
      <td>76.56</td>
      <td>95.03</td>
      <td>87.36</td>
      <td>-0.01</td>
      <td>7.49</td>
      <td>-0.04</td>
      <td>...</td>
      <td>-0.63</td>
      <td>0.01</td>
      <td>5.19</td>
      <td>-0.25</td>
      <td>0.00</td>
      <td>0.97</td>
      <td>-0.10</td>
      <td>0.00</td>
      <td>0.92</td>
      <td>-0.39</td>
    </tr>
  </tbody>
</table>
<p>5014 rows × 28 columns</p>
</div>



```python
plot_time_series(
    df=data_merged_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[col for col in data_merged_aligned.columns if "Cumulative_Return" in col],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=30,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)

plot_time_series(
    df=data_merged_aligned,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[col for col in data_merged_aligned.columns if "Drawdown" in col],
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


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_25_0.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_25_1.png)
    


Several things to note here:

* Gold wins! Almost...
* You lose most of your money investing in commodies...
* Gold diversified well during the financial crisis
* The equity funds all had similar drawdowns

## Summary Statistics

Let's look at the summary statistics. Keep in mind that we are not aligning the dates here, so the number of observations is different for each ETF.


```python
sum_stats = pd.DataFrame()

for fund in fund_data.keys():
    data_stats = summary_stats(
        fund_list=[f"{fund}"],
        df=data_merged[[f"{fund}_Return"]].dropna(),
        period="Daily",
        use_calendar_days=False,
        excel_export=False,
        pickle_export=False,
        output_confirmation=False,
    )

    sum_stats = pd.concat([sum_stats, data_stats])

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
      <th>IVV_Return</th>
      <td>6563</td>
      <td>2000-05-22</td>
      <td>2026-06-26</td>
      <td>0.10</td>
      <td>0.19</td>
      <td>0.52</td>
      <td>0.08</td>
      <td>0.11</td>
      <td>2008-10-28</td>
      <td>-0.12</td>
      <td>2020-03-16</td>
      <td>-0.55</td>
      <td>2007-10-09</td>
      <td>2009-03-09</td>
      <td>2012-08-16</td>
      <td>1256.00</td>
      <td>0.15</td>
    </tr>
    <tr>
      <th>EFA_Return</th>
      <td>6243</td>
      <td>2001-08-28</td>
      <td>2026-06-26</td>
      <td>0.08</td>
      <td>0.21</td>
      <td>0.40</td>
      <td>0.06</td>
      <td>0.16</td>
      <td>2008-10-13</td>
      <td>-0.11</td>
      <td>2008-09-29</td>
      <td>-0.61</td>
      <td>2007-10-31</td>
      <td>2009-03-09</td>
      <td>2014-06-06</td>
      <td>1915.00</td>
      <td>0.11</td>
    </tr>
    <tr>
      <th>EEM_Return</th>
      <td>5837</td>
      <td>2003-04-15</td>
      <td>2026-06-26</td>
      <td>0.13</td>
      <td>0.27</td>
      <td>0.49</td>
      <td>0.10</td>
      <td>0.23</td>
      <td>2008-10-13</td>
      <td>-0.16</td>
      <td>2008-10-15</td>
      <td>-0.66</td>
      <td>2007-10-31</td>
      <td>2008-11-20</td>
      <td>2017-09-18</td>
      <td>3224.00</td>
      <td>0.15</td>
    </tr>
    <tr>
      <th>GSG_Return</th>
      <td>5013</td>
      <td>2006-07-24</td>
      <td>2026-06-26</td>
      <td>-0.00</td>
      <td>0.23</td>
      <td>-0.00</td>
      <td>-0.03</td>
      <td>0.08</td>
      <td>2008-11-04</td>
      <td>-0.12</td>
      <td>2020-03-09</td>
      <td>-0.90</td>
      <td>2008-07-02</td>
      <td>2020-04-28</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>-0.03</td>
    </tr>
    <tr>
      <th>IAU_Return</th>
      <td>5385</td>
      <td>2005-01-31</td>
      <td>2026-06-26</td>
      <td>0.12</td>
      <td>0.18</td>
      <td>0.65</td>
      <td>0.11</td>
      <td>0.12</td>
      <td>2008-09-17</td>
      <td>-0.10</td>
      <td>2026-01-30</td>
      <td>-0.45</td>
      <td>2011-08-22</td>
      <td>2015-12-02</td>
      <td>2020-07-27</td>
      <td>1699.00</td>
      <td>0.24</td>
    </tr>
    <tr>
      <th>IEF_Return</th>
      <td>6015</td>
      <td>2002-07-31</td>
      <td>2026-06-26</td>
      <td>0.04</td>
      <td>0.07</td>
      <td>0.56</td>
      <td>0.04</td>
      <td>0.03</td>
      <td>2009-03-18</td>
      <td>-0.03</td>
      <td>2020-03-17</td>
      <td>-0.24</td>
      <td>2020-08-04</td>
      <td>2023-10-19</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>0.15</td>
    </tr>
    <tr>
      <th>TLT_Return</th>
      <td>6015</td>
      <td>2002-07-31</td>
      <td>2026-06-26</td>
      <td>0.05</td>
      <td>0.14</td>
      <td>0.33</td>
      <td>0.04</td>
      <td>0.08</td>
      <td>2020-03-20</td>
      <td>-0.07</td>
      <td>2020-03-17</td>
      <td>-0.48</td>
      <td>2020-08-04</td>
      <td>2023-10-19</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>0.08</td>
    </tr>
  </tbody>
</table>
</div>


## Calculate Moving Averages

Now, let's calculate the various different moving averages for each ETF. We will calculate the 3, 4, 5, 6, 7, 8, 9, 10, 11, and 12 month moving averages, using the equivalent number of trading days for each time period (63, 84, 105, 126, 147, 168, 189, 210, 231, and 252 trading days).


```python
# Define moving average windows in trading days
ma_windows = {
    '3m': 63,     # 3 months (~63 trading days)
    '4m': 84,     # 4 months (~84 trading days)
    '5m': 105,    # 5 months (~105 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '7m': 147,    # 7 months (~147 trading days)
    '8m': 168,    # 8 months (~168 trading days)
    '9m': 189,    # 9 months (~189 trading days)
    '10m': 210,   # 10 months (~210 trading days)
    '11m': 231,   # 11 months (~231 trading days)
    '12m': 252    # 12 months (~252 trading days)
}
```


```python
for fund, data in fund_data.items():
    for window, days in ma_windows.items():
        data[f"{fund}_MA_{window}"] = data[f"{fund}_Adj_Close"].rolling(window=days).mean()
```

## Calculate Forward Return Windows

Next, we will calculate the forward return for each ETF for the same time periods as the moving averages. For example, we will calculate the 3 month forward return, which is the return from the current date to 3 months in the future, and so on for each of the other time periods.


```python
# Define forward return windows in trading days
forward_return_windows = {
    '3m': 63,     # 3 months (~63 trading days)
    '4m': 84,     # 4 months (~84 trading days)
    '5m': 105,    # 5 months (~105 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '7m': 147,    # 7 months (~147 trading days)
    '8m': 168,    # 8 months (~168 trading days)
    '9m': 189,    # 9 months (~189 trading days)
    '10m': 210,   # 10 months (~210 trading days)
    '11m': 231,   # 11 months (~231 trading days)
    '12m': 252    # 12 months (~252 trading days)
}
```


```python
for fund, data in fund_data.items():
    for window, days in forward_return_windows.items():
        data[f"{fund}_Forward_Return_{window}"] = data[f"{fund}_Adj_Close"].shift(-days) / data[f"{fund}_Adj_Close"] - 1
```

## Calculate Moving Average Predictions

Now, we will calculate the moving average predictions, as follows:

* If the price is above the moving average, the prediction is 1 (i.e. the price will be above the moving average in the future).
* If the price is below the moving average, the prediction is -1 (i.e. the price will be below the moving average in the future).
* Calculate the accuracy of the predictions by comparing them to the actual forward returns (i.e. if the forward return is positive, the actual outcome is 1, and if the forward return is negative, the actual outcome is -1).
* Calculate the difference between the price and moving average (percentage), z-score (standardize) both that difference and the forward returns, and run a standardized OLS regression of forward return on the price-MA difference. Standardizing both sides puts every fund, moving average, and forward return window on the same scale, so the regression slope (a standardized beta, equal to the Pearson correlation) is directly comparable across them.


```python
ma_prediction_results = pd.DataFrame(columns=[
    "Fund",
    "MA_Window",
    "Forward_Return_Window",
    "Overall_Accuracy",
    "Positive_Accuracy",
    "Negative_Accuracy",
    "Std_Beta",
    "Std_Beta_PValue",
    "R_Squared",
])

for fund, data in fund_data.items():
    for ma_label, ma_window in ma_windows.items():
        # Prediction and the price-vs-MA gap depend only on the MA window, so compute them
        # once per MA on the full frame (these columns persist for the plots further down).
        data[f"{fund}_MA_Prediction_{ma_label}"] = 0
        data.loc[data[f"{fund}_Adj_Close"] > data[f"{fund}_MA_{ma_label}"], f"{fund}_MA_Prediction_{ma_label}"] = 1
        data.loc[data[f"{fund}_Adj_Close"] < data[f"{fund}_MA_{ma_label}"], f"{fund}_MA_Prediction_{ma_label}"] = -1

        # Calculate the percentage difference between price and moving average
        data[f"{fund}_Price_MA_Diff_Percent_{ma_label}"] = (data[f"{fund}_Adj_Close"] - data[f"{fund}_MA_{ma_label}"]) / data[f"{fund}_MA_{ma_label}"]

        for fr_label, fr_window in forward_return_windows.items():
            data[f"{fund}_Actual_{fr_label}"] = 0
            data.loc[data[f"{fund}_Forward_Return_{fr_label}"] > 0, f"{fund}_Actual_{fr_label}"] = 1
            data.loc[data[f"{fund}_Forward_Return_{fr_label}"] < 0, f"{fund}_Actual_{fr_label}"] = -1

            pred_col = f"{fund}_MA_Prediction_{ma_label}"
            actual_col = f"{fund}_Actual_{fr_label}"
            diff_col = f"{fund}_Price_MA_Diff_Percent_{ma_label}"
            fr_col = f"{fund}_Forward_Return_{fr_label}"

            # Restrict to rows where THIS MA and THIS forward return are both defined, so each
            # window pair is evaluated on its own full sample rather than the intersection of all
            # 12 windows. (Dropping NaN on every column collapsed every pair onto the 12m-MA /
            # 12m-forward overlap, discarding most of the data for the shorter windows.)
            pair_data = data.dropna(subset=[f"{fund}_MA_{ma_label}", fr_col])
            # pair_data = pair_data.resample("W").last()

            overall_accuracy = (pair_data[pred_col] == pair_data[actual_col]).mean()
            pos_accuracy = ((pair_data[pred_col] == 1) & (pair_data[actual_col] == 1)).sum() / (pair_data[pred_col] == 1).sum()
            neg_accuracy = ((pair_data[pred_col] == -1) & (pair_data[actual_col] == -1)).sum() / (pair_data[pred_col] == -1).sum()

            # Calculate the mean forward return (and +/- 2 std bands) for the cases where the MA predicted a positive return and where it predicted a negative return
            positive_returns = pair_data.loc[pair_data[pred_col] == 1, fr_col]
            positive_mean_return = positive_returns.mean()
            positive_mean_plus_two_std = positive_mean_return + positive_returns.std() * 2
            positive_mean_minus_two_std = positive_mean_return - positive_returns.std() * 2
            negative_returns = pair_data.loc[pair_data[pred_col] == -1, fr_col]
            negative_mean_return = negative_returns.mean()
            negative_mean_plus_two_std = negative_mean_return + negative_returns.std() * 2
            negative_mean_minus_two_std = negative_mean_return - negative_returns.std() * 2

            # Z-score (standardize) the predictor and the forward return so the regression
            # slope is a standardized beta, comparable across funds, MAs, and forward windows.
            # With both sides standardized the slope equals the Pearson correlation.
            diff_z_col = f"{diff_col}_Z"
            fr_z_col = f"{fr_col}_Z"
            pair_data = pair_data.assign(**{
                diff_z_col: (pair_data[diff_col] - pair_data[diff_col].mean()) / pair_data[diff_col].std(),
                fr_z_col: (pair_data[fr_col] - pair_data[fr_col].mean()) / pair_data[fr_col].std(),
            })

            # Run a standardized OLS regression of forward return on the price-MA difference
            model = run_regression(
                df=pair_data,
                x_plot_column=diff_z_col,
                y_plot_column=fr_z_col,
                regression_model="OLS-statsmodels",
                regression_constant=True,
            )
            std_beta = model.params.iloc[1]          # standardized slope (== Pearson correlation)
            std_beta_pvalue = model.pvalues.iloc[1]  # p-value for the slope
            r_squared = model.rsquared               # R-squared of the regression

            results = pd.DataFrame([{
                    "Fund": fund,
                    "MA_Window": ma_label,
                    "Forward_Return_Window": fr_label,
                    "Overall_Accuracy": overall_accuracy,
                    "Positive_Accuracy": pos_accuracy,
                    "Negative_Accuracy": neg_accuracy,
                    "Positive_Mean_Return": positive_mean_return,
                    "Positive_Mean_Plus_Two_Std": positive_mean_plus_two_std,
                    "Positive_Mean_Minus_Two_Std": positive_mean_minus_two_std,
                    "Negative_Mean_Return": negative_mean_return,
                    "Negative_Mean_Plus_Two_Std": negative_mean_plus_two_std,
                    "Negative_Mean_Minus_Two_Std": negative_mean_minus_two_std,
                    "Std_Beta": std_beta,
                    "Std_Beta_PValue": std_beta_pvalue,
                    "R_Squared": r_squared,
            }])
            
            ma_prediction_results = pd.concat([ma_prediction_results, results], ignore_index=True)
```


```python
display(ma_prediction_results)
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
      <th>Fund</th>
      <th>MA_Window</th>
      <th>Forward_Return_Window</th>
      <th>Overall_Accuracy</th>
      <th>Positive_Accuracy</th>
      <th>Negative_Accuracy</th>
      <th>Std_Beta</th>
      <th>Std_Beta_PValue</th>
      <th>R_Squared</th>
      <th>Positive_Mean_Return</th>
      <th>Positive_Mean_Plus_Two_Std</th>
      <th>Positive_Mean_Minus_Two_Std</th>
      <th>Negative_Mean_Return</th>
      <th>Negative_Mean_Plus_Two_Std</th>
      <th>Negative_Mean_Minus_Two_Std</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>IVV</td>
      <td>3m</td>
      <td>3m</td>
      <td>0.59</td>
      <td>0.71</td>
      <td>0.34</td>
      <td>-0.01</td>
      <td>0.30</td>
      <td>0.00</td>
      <td>0.02</td>
      <td>0.15</td>
      <td>-0.10</td>
      <td>0.02</td>
      <td>0.23</td>
      <td>-0.18</td>
    </tr>
    <tr>
      <th>1</th>
      <td>IVV</td>
      <td>3m</td>
      <td>4m</td>
      <td>0.61</td>
      <td>0.73</td>
      <td>0.35</td>
      <td>0.02</td>
      <td>0.05</td>
      <td>0.00</td>
      <td>0.03</td>
      <td>0.18</td>
      <td>-0.11</td>
      <td>0.03</td>
      <td>0.26</td>
      <td>-0.21</td>
    </tr>
    <tr>
      <th>2</th>
      <td>IVV</td>
      <td>3m</td>
      <td>5m</td>
      <td>0.64</td>
      <td>0.76</td>
      <td>0.36</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>0.00</td>
      <td>0.04</td>
      <td>0.21</td>
      <td>-0.12</td>
      <td>0.03</td>
      <td>0.30</td>
      <td>-0.24</td>
    </tr>
    <tr>
      <th>3</th>
      <td>IVV</td>
      <td>3m</td>
      <td>6m</td>
      <td>0.64</td>
      <td>0.77</td>
      <td>0.35</td>
      <td>0.02</td>
      <td>0.10</td>
      <td>0.00</td>
      <td>0.05</td>
      <td>0.24</td>
      <td>-0.14</td>
      <td>0.04</td>
      <td>0.33</td>
      <td>-0.25</td>
    </tr>
    <tr>
      <th>4</th>
      <td>IVV</td>
      <td>3m</td>
      <td>7m</td>
      <td>0.66</td>
      <td>0.80</td>
      <td>0.36</td>
      <td>0.04</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.06</td>
      <td>0.27</td>
      <td>-0.14</td>
      <td>0.05</td>
      <td>0.36</td>
      <td>-0.27</td>
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
    </tr>
    <tr>
      <th>695</th>
      <td>TLT</td>
      <td>12m</td>
      <td>8m</td>
      <td>0.46</td>
      <td>0.54</td>
      <td>0.34</td>
      <td>-0.07</td>
      <td>0.00</td>
      <td>0.01</td>
      <td>0.02</td>
      <td>0.23</td>
      <td>-0.19</td>
      <td>0.04</td>
      <td>0.26</td>
      <td>-0.18</td>
    </tr>
    <tr>
      <th>696</th>
      <td>TLT</td>
      <td>12m</td>
      <td>9m</td>
      <td>0.46</td>
      <td>0.56</td>
      <td>0.31</td>
      <td>-0.06</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.03</td>
      <td>0.25</td>
      <td>-0.20</td>
      <td>0.04</td>
      <td>0.27</td>
      <td>-0.19</td>
    </tr>
    <tr>
      <th>697</th>
      <td>TLT</td>
      <td>12m</td>
      <td>10m</td>
      <td>0.47</td>
      <td>0.58</td>
      <td>0.31</td>
      <td>-0.06</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>0.03</td>
      <td>0.27</td>
      <td>-0.21</td>
      <td>0.04</td>
      <td>0.29</td>
      <td>-0.20</td>
    </tr>
    <tr>
      <th>698</th>
      <td>TLT</td>
      <td>12m</td>
      <td>11m</td>
      <td>0.49</td>
      <td>0.61</td>
      <td>0.32</td>
      <td>-0.04</td>
      <td>0.01</td>
      <td>0.00</td>
      <td>0.04</td>
      <td>0.28</td>
      <td>-0.21</td>
      <td>0.05</td>
      <td>0.30</td>
      <td>-0.21</td>
    </tr>
    <tr>
      <th>699</th>
      <td>TLT</td>
      <td>12m</td>
      <td>12m</td>
      <td>0.50</td>
      <td>0.63</td>
      <td>0.33</td>
      <td>-0.02</td>
      <td>0.13</td>
      <td>0.00</td>
      <td>0.04</td>
      <td>0.30</td>
      <td>-0.22</td>
      <td>0.05</td>
      <td>0.31</td>
      <td>-0.22</td>
    </tr>
  </tbody>
</table>
<p>700 rows × 15 columns</p>
</div>


## Plot Moving Average Predictions

The following plots show the relationship between the price-MA difference and the forward returns for each ETF, moving average, and forward return window. Simply comment out the MA and forward return windows you don't want to plot. we'll use the 3 month MA for a brief look at the results.


```python
# Define moving average windows in trading days
ma_windows = {
    '3m': 63,     # 3 months (~63 trading days)
    # '4m': 84,     # 4 months (~84 trading days)
    # '5m': 105,    # 5 months (~105 trading days)
    # '6m': 126,    # 6 months (~126 trading days)
    # '7m': 147,    # 7 months (~147 trading days)
    # '8m': 168,    # 8 months (~168 trading days)
    # '9m': 189,    # 9 months (~189 trading days)
    # '10m': 210,   # 10 months (~210 trading days)
    # '11m': 231,   # 11 months (~231 trading days)
    # '12m': 252    # 12 months (~252 trading days)
}

# Define forward return windows in trading days
forward_return_windows = {
    '3m': 63,     # 3 months (~63 trading days)
    '4m': 84,     # 4 months (~84 trading days)
    '5m': 105,    # 5 months (~105 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '7m': 147,    # 7 months (~147 trading days)
    '8m': 168,    # 8 months (~168 trading days)
    '9m': 189,    # 9 months (~189 trading days)
    '10m': 210,   # 10 months (~210 trading days)
    '11m': 231,   # 11 months (~231 trading days)
    '12m': 252    # 12 months (~252 trading days)
}
```

### IVV, EFA, and EEM


```python
for fund, data in fund_data.items():
    if fund not in ["IVV", "EFA", "EEM"]:
        continue
    for ma_label, ma_window in ma_windows.items():
        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Overall_Accuracy", "Positive_Accuracy", "Negative_Accuracy"],
            title=f"{fund} MA ({ma_label}) Prediction Accuracy vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Accuracy",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Positive_Mean_Return", "Positive_Mean_Plus_Two_Std", "Positive_Mean_Minus_Two_Std", "Negative_Mean_Return", "Negative_Mean_Plus_Two_Std", "Negative_Mean_Minus_Two_Std"],
            title=f"{fund} MA ({ma_label}) Forward Mean, +/- 2 Std Return vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Return",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        for fr_label, fr_window in forward_return_windows.items():
            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == 1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Positive Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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

            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == -1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Negative Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_0.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_1.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_2.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_3.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_4.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_5.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_6.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_7.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_8.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_9.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_10.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_11.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_12.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_13.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_14.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_15.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_16.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_17.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_18.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_19.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_20.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_21.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_22.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_23.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_24.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_25.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_26.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_27.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_28.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_29.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_30.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_31.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_32.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_33.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_34.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_35.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_36.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_37.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_38.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_39.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_40.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_41.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_42.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_43.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_44.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_45.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_46.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_47.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_48.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_49.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_50.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_51.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_52.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_53.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_54.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_55.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_56.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_57.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_58.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_59.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_60.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_61.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_62.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_63.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_64.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_44_65.png)
    


### GSG and IAU


```python
for fund, data in fund_data.items():
    if fund not in ["GSG", "IAU"]:
        continue
    for ma_label, ma_window in ma_windows.items():
        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Overall_Accuracy", "Positive_Accuracy", "Negative_Accuracy"],
            title=f"{fund} MA ({ma_label}) Prediction Accuracy vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Accuracy",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Positive_Mean_Return", "Positive_Mean_Plus_Two_Std", "Positive_Mean_Minus_Two_Std", "Negative_Mean_Return", "Negative_Mean_Plus_Two_Std", "Negative_Mean_Minus_Two_Std"],
            title=f"{fund} MA ({ma_label}) Forward Mean, +/- 2 Std Return vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Return",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        for fr_label, fr_window in forward_return_windows.items():
            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == 1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Positive Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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

            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == -1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Negative Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_0.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_1.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_2.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_3.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_4.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_5.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_6.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_7.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_8.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_9.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_10.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_11.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_12.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_13.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_14.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_15.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_16.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_17.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_18.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_19.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_20.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_21.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_22.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_23.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_24.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_25.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_26.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_27.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_28.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_29.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_30.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_31.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_32.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_33.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_34.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_35.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_36.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_37.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_38.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_39.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_40.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_41.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_42.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_46_43.png)
    


### IEF and TLT


```python
for fund, data in fund_data.items():
    if fund not in ["IEF", "TLT"]:
        continue
    for ma_label, ma_window in ma_windows.items():
        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Overall_Accuracy", "Positive_Accuracy", "Negative_Accuracy"],
            title=f"{fund} MA ({ma_label}) Prediction Accuracy vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Accuracy",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Positive_Mean_Return", "Positive_Mean_Plus_Two_Std", "Positive_Mean_Minus_Two_Std", "Negative_Mean_Return", "Negative_Mean_Plus_Two_Std", "Negative_Mean_Minus_Two_Std"],
            title=f"{fund} MA ({ma_label}) Forward Mean, +/- 2 Std Return vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Return",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )

        for fr_label, fr_window in forward_return_windows.items():
            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == 1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Positive Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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

            plot_histogram(
                df=data[data[f"{fund}_MA_Prediction_{ma_label}"] == -1],
                plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
                title=f"MA ({ma_label}) Predicts Negative Return, {fund} Forward Return ({fr_label}) Distribution",
                x_label="Return",
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
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_0.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_1.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_2.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_3.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_4.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_5.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_6.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_7.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_8.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_9.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_10.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_11.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_12.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_13.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_14.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_15.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_16.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_17.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_18.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_19.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_20.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_21.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_22.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_23.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_24.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_25.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_26.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_27.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_28.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_29.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_30.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_31.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_32.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_33.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_34.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_35.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_36.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_37.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_38.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_39.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_40.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_41.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_42.png)
    



    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_48_43.png)
    



```python
# for fund, data in fund_data.items():
    # for ma_label, ma_window in ma_windows.items():
        # for fr_label, fr_window in forward_return_windows.items():
            # plot_scatter(
            #     df=data,
            #     x_plot_column=f"{fund}_Price_MA_Diff_Percent_{ma_label}",
            #     y_plot_columns=[f"{fund}_Forward_Return_{fr_label}"],
            #     title=f"{fund} MA Diff (Percent) ({ma_label}) vs Forward Return ({fr_label})",
            #     x_label="MA Diff (Percent)",
            #     x_format="Decimal",
            #     x_format_decimal_places=2,
            #     x_tick_spacing="Auto",
            #     x_tick_start=None,
            #     x_tick_rotation=30,
            #     y_label="Forward Return",
            #     y_format="Decimal",
            #     y_format_decimal_places=2,
            #     y_tick_spacing="Auto",
            #     y_tick_rotation=0,
            #     plot_OLS_regression_line=True,
            #     OLS_column=f"{fund}_Forward_Return_{fr_label}",
            #     plot_Ridge_regression_line=True,
            #     Ridge_column=f"{fund}_Forward_Return_{fr_label}",
            #     plot_RidgeCV_regression_line=True,
            #     RidgeCV_column=f"{fund}_Forward_Return_{fr_label}",
            #     regression_constant=True,
            #     grid=True,
            #     legend=True,
            #     export_plot=False,
            #     plot_file_name=None,
            # )
```

## Analysis Of Results

### 1. Positive, Negative, and Overall Accuracy

From the above plots, we can see that some ETFs (which we are - kind of - using as a proxy for asset classes), appear to have a stronger relationship between the price-MA difference and the forward returns than others. This "relationship" takes the form of the overall accuracy of the predictions, which tells us how well the price-MA difference predicts the direction of the future returns.

#### 1.1. Mean Overall Accuracy by Fund and MA Window

Here we plot the overall mean prediction accuracy for each ETF and MA window combination.


```python
# Calc overall mean accuracy for each fund across all MA windows
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Overall_Accuracy"].mean().reset_index()

# Create a new DataFrame with unique MA_Window values and merge the mean accuracy for each fund
accuracy = pd.DataFrame({"MA_Window": temp["MA_Window"].unique()})

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Overall_Accuracy"]].rename(
        columns={"Overall_Accuracy": f"{fund}_Overall_Accuracy"}
    )
    accuracy = pd.merge(accuracy, fund_temp, on="MA_Window", how="outer")
    
plot_scatter(
    df=accuracy,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Overall_Accuracy", 
                    "EFA_Overall_Accuracy", 
                    "EEM_Overall_Accuracy", 
                    "GSG_Overall_Accuracy", 
                    "IAU_Overall_Accuracy", 
                    "IEF_Overall_Accuracy", 
                    "TLT_Overall_Accuracy"],
    title="Mean Overall Accuracy by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Accuracy",
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
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_55_0.png)
    


The stock funds (IVV, EFA, and EEM) have the highest mean overall accuracy, which tells us that the price-MA difference is a better predictor of the direction of future returns for these funds than for the other funds. The commodity fund (GSG) has the lowest mean overall accuracy, followed by long-term bonds (TLT), which both rank below the 50% threshold. If the mean overall accuracy does not exceed the 50% mark, then essentially the price-MA difference is not any better than a coin flip at predicting the direction of future returns.

#### 1.2. Mean Positive Accuracy by Fund and MA Window

The overall accuracy statistic includes the predicted accuracy of both the positive (are future returns positive when the price-MA is positive) and the negative (are future returns negative when the price-MA is negative) directions. The overall accuracy is useful from a long-short standpoint, but from a long-only perspective, we care only about the positive direction, which we plot next.


```python
# Calc overall mean accuracy for each fund across all MA windows
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Positive_Accuracy"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Positive_Accuracy"]].rename(
        columns={"Positive_Accuracy": f"{fund}_Positive_Accuracy"}
    )
    accuracy = pd.merge(accuracy, fund_temp, on="MA_Window", how="outer")
    
plot_scatter(
    df=accuracy,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Positive_Accuracy",
                    "EFA_Positive_Accuracy",
                    "EEM_Positive_Accuracy",
                    "GSG_Positive_Accuracy",
                    "IAU_Positive_Accuracy",
                    "IEF_Positive_Accuracy",
                    "TLT_Positive_Accuracy"],
    title="Mean Positive Accuracy by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Accuracy",
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
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_59_0.png)
    


What we see is a nearly uniform shift up in the mean positive accuracy for all of the funds, relative to the overall accuracy. And not just by a little bit - it's significant, as we will see below.

#### 1.3. Difference Between Positive and Overall Accuracy by Fund and MA Window

Here's the plot of the difference betweent he mean and positive accuracy.


```python
for fund in fund_list:
    accuracy[f"{fund}_Positive_Overall_Mean_Diff"] = accuracy[f"{fund}_Positive_Accuracy"] - accuracy[f"{fund}_Overall_Accuracy"]

plot_scatter(
    df=accuracy,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Positive_Overall_Mean_Diff", 
                    "EFA_Positive_Overall_Mean_Diff", 
                    "EEM_Positive_Overall_Mean_Diff", 
                    "GSG_Positive_Overall_Mean_Diff", 
                    "IAU_Positive_Overall_Mean_Diff", 
                    "IEF_Positive_Overall_Mean_Diff", 
                    "TLT_Positive_Overall_Mean_Diff"],
    title="Difference Between Positive and Overall Accuracy by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Accuracy Difference",
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
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_63_0.png)
    


IVV shows a 10 - 14% difference, while GSG show only a 2 or 3% improvement. The other funds show a 9 - 12%. If we were interested in using the price-MA difference to predict the direction of future returns, we would be better off using only the positive predictions.

### 2. Distribution of Future Returns Based on Price-MA Difference

Next, we can consider the shape of the distribution of the future returns, split on whether the the price-MA difference is positive or negative.

#### 2.1. Mean Future Return When Price-MA Difference is Positive by Fund and MA Window

First, the distribution of future returns when the price-MA difference is positive.


```python
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Positive_Mean_Return"].mean().reset_index()

distribution = pd.DataFrame({"MA_Window": temp["MA_Window"].unique()})

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Positive_Mean_Return"]].rename(
        columns={"Positive_Mean_Return": f"{fund}_Positive_Mean_Return"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Positive_Mean_Return",
                    "EFA_Positive_Mean_Return",
                    "EEM_Positive_Mean_Return",
                    "GSG_Positive_Mean_Return",
                    "IAU_Positive_Mean_Return",
                    "IEF_Positive_Mean_Return",
                    "TLT_Positive_Mean_Return"],
    title="Mean Future Return When Price-MA Difference is Positive by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Return",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)


```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_69_0.png)
    


In a perfect world, we want to see similar numbers across all MA windows, and all of those numbers would be relatively high. If every window gives us roughly the same distribution of future returns, that would indicate a consistent predictive relationship across all windows. But, what we often see is that the distributions vary quite a bit depending on the window, which suggests that it's useful to consider a combination of windows to form a more robust signal.

Note that gold (IAU) has a smaller variation and much higher values (mean return is ~1.5% greater than IVV) across MA windows compared to the other funds.

#### 2.2. Mean Future Return When Price-MA Difference is Negative by Fund and MA Window

On to the distribution of future returns when the price-MA difference is negative.


```python
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Negative_Mean_Return"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Negative_Mean_Return"]].rename(
        columns={"Negative_Mean_Return": f"{fund}_Negative_Mean_Return"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Negative_Mean_Return",
                    "EFA_Negative_Mean_Return",
                    "EEM_Negative_Mean_Return",
                    "GSG_Negative_Mean_Return",
                    "IAU_Negative_Mean_Return",
                    "IEF_Negative_Mean_Return",
                    "TLT_Negative_Mean_Return"],
    title="Mean Future Return When Price-MA Difference is Negative by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Return",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_73_0.png)
    


Interesting, the mean returns are mostly still positive. That suggests that even when the price-MA difference is negative, future returns tend to be positive on average, though perhaps smaller than when the difference is positive.

#### 2.3. Difference Between Predicted Positive and Negative Mean Returns by Fund and MA Window

Next, we can look at the *difference* in mean future returns between when the price-MA difference is positive and when it is negative.


```python
for fund in fund_list:
    distribution[f"{fund}_Mean_Return_Diff"] = distribution[f"{fund}_Positive_Mean_Return"] - distribution[f"{fund}_Negative_Mean_Return"]

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Mean_Return_Diff", 
                    "EFA_Mean_Return_Diff", 
                    "EEM_Mean_Return_Diff", 
                    "GSG_Mean_Return_Diff", 
                    "IAU_Mean_Return_Diff", 
                    "IEF_Mean_Return_Diff", 
                    "TLT_Mean_Return_Diff"],
    title="Difference Between Predicted Positive and Negative Mean Returns by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Return Difference",
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
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_77_0.png)
    


 In general, the mean of the future positive predicted returns is higher than the mean of the future negative predicted returns, which is what we would expect if the price-MA difference has any predictive power. However, the distributions are not normal, and there are some outliers that skew the distributions. These outliers show up as the long tails in the distributions, and the number and magnitude of the outliers can be seen in the mean +/- 2 standard deviations.

 Note again, gold has the highest difference in mean return between when the price-MA difference is positive and when it is negative.

#### 2.4. Difference Between Positive Mean +2 Std and Positive Mean -2 Std Returns by Fund and MA Window

As mentioned above, we think that there are outliers that skew the distributions of the forward returns. But by how much? And how can we quantify their impact? One way is to look at the standard deviations. Here's the plots for the difference between  2 standard deviations above and below the mean for the forward returns.


```python
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Positive_Mean_Plus_Two_Std"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Positive_Mean_Plus_Two_Std"]].rename(
        columns={"Positive_Mean_Plus_Two_Std": f"{fund}_Positive_Mean_Plus_Two_Std"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Positive_Mean_Minus_Two_Std"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Positive_Mean_Minus_Two_Std"]].rename(
        columns={"Positive_Mean_Minus_Two_Std": f"{fund}_Positive_Mean_Minus_Two_Std"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

for fund in fund_list:
    distribution[f"{fund}_Positive_Mean_Plus_Minus_2Std_Diff"] = distribution[f"{fund}_Positive_Mean_Plus_Two_Std"] - distribution[f"{fund}_Positive_Mean_Minus_Two_Std"]

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Positive_Mean_Plus_Minus_2Std_Diff",
                    "EFA_Positive_Mean_Plus_Minus_2Std_Diff",
                    "EEM_Positive_Mean_Plus_Minus_2Std_Diff",
                    "GSG_Positive_Mean_Plus_Minus_2Std_Diff",
                    "IAU_Positive_Mean_Plus_Minus_2Std_Diff",
                    "IEF_Positive_Mean_Plus_Minus_2Std_Diff",
                    "TLT_Positive_Mean_Plus_Minus_2Std_Diff"],
    title="Difference Between Positive Mean +2 Std and Positive Mean -2 Std Returns by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Mean Return 2 Std Difference",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_81_0.png)
    


GSG is a mess... the commodity fund has a lot of noise and outliers. We'd like to see a tight distribution, that might give us confidence that the forward returns are within a reasonable range and not being dominated by extreme values. Here, the 7-10 year bond ETF is the leader, with a much tighter distribution and fewer extreme values skewing the results.

#### 2.5. Difference Between Negative Mean +2 Std and Negative Mean -2 Std Returns by Fund and MA Window

Now for the e difference between 2 standard deviations above and below the mean for the forward returns when price-MA is negative.


```python
temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Negative_Mean_Plus_Two_Std"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Negative_Mean_Plus_Two_Std"]].rename(
        columns={"Negative_Mean_Plus_Two_Std": f"{fund}_Negative_Mean_Plus_Two_Std"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

temp = ma_prediction_results.groupby(["Fund", "MA_Window"])["Negative_Mean_Minus_Two_Std"].mean().reset_index()

for fund in fund_list:
    fund_temp = temp[temp["Fund"] == fund][["MA_Window", "Negative_Mean_Minus_Two_Std"]].rename(
        columns={"Negative_Mean_Minus_Two_Std": f"{fund}_Negative_Mean_Minus_Two_Std"}
    )
    distribution = pd.merge(distribution, fund_temp, on="MA_Window", how="outer")

for fund in fund_list:
    distribution[f"{fund}_Negative_Mean_Plus_Minus_2Std_Diff"] = distribution[f"{fund}_Negative_Mean_Plus_Two_Std"] - distribution[f"{fund}_Negative_Mean_Minus_Two_Std"]

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_Negative_Mean_Plus_Minus_2Std_Diff",
                    "EFA_Negative_Mean_Plus_Minus_2Std_Diff",
                    "EEM_Negative_Mean_Plus_Minus_2Std_Diff",
                    "GSG_Negative_Mean_Plus_Minus_2Std_Diff",
                    "IAU_Negative_Mean_Plus_Minus_2Std_Diff",
                    "IEF_Negative_Mean_Plus_Minus_2Std_Diff",
                    "TLT_Negative_Mean_Plus_Minus_2Std_Diff"],
    title="Difference Between Negative Mean +2 Std and Negative Mean -2 Std Returns by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Mean Return 2 Std Difference",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_85_0.png)
    


This might not be as relevant to us (from a long-only perspective), but it's still worth looking at to understand how the asset classes rank. Emerging markets tend to have more volatility and outliers, so this plot makes sense intuitively.

#### 2.6. Difference Between Positive and Negative +/-2 Std Return Spreads by Fund and MA Window

Finally, we have the difference between the 2 standard deviation spreads.


```python
for fund in fund_list:
    distribution[f"{fund}_2Std_Spread_Diff"] = distribution[f"{fund}_Positive_Mean_Plus_Minus_2Std_Diff"] - distribution[f"{fund}_Negative_Mean_Plus_Minus_2Std_Diff"]

plot_scatter(
    df=distribution,
    x_plot_column="MA_Window",
    y_plot_columns=["IVV_2Std_Spread_Diff",
                    "EFA_2Std_Spread_Diff",
                    "EEM_2Std_Spread_Diff",
                    "GSG_2Std_Spread_Diff",
                    "IAU_2Std_Spread_Diff",
                    "IEF_2Std_Spread_Diff",
                    "TLT_2Std_Spread_Diff"],
    title="Difference Between Positive and Negative +/-2 Std Return Spreads by Fund and MA Window",
    x_label="MA Window",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Mean Return 2 Std Difference (Positive - Negative)",
    y_format="Decimal",
    y_format_decimal_places=3,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    plot_OLS_regression_line=False,
    OLS_column=None,
    plot_Ridge_regression_line=False,
    Ridge_column=None,
    plot_RidgeCV_regression_line=False,
    RidgeCV_column=None,
    regression_constant=True,
    grid=True,
    legend=True,
    legend_location="upper left",
    legend_anchor=(1, 1),
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_89_0.png)
    


This plot really compares the kurtosis of the forward return distributions by looking at the difference between the 2 standard deviation spreads for positive and negative price-MA conditions. If these values are positive, it means that the forward return distributions have fatter tails for positive price-MA conditions relative to negative price-MA conditions, and the opposite is true if the values are negative.

So anything <=0 is good here, which brings us back to gold, which is positive. Pulling up one of the earlier plots:


```python
for fund, data in fund_data.items():
    if fund not in ["IAU"]:
        continue
    for ma_label, ma_window in ma_windows.items():
        plot_scatter(
            df=ma_prediction_results[(ma_prediction_results["Fund"] == fund) & (ma_prediction_results["MA_Window"] == ma_label)],
            x_plot_column="Forward_Return_Window",
            y_plot_columns=["Positive_Mean_Return", "Positive_Mean_Plus_Two_Std", "Positive_Mean_Minus_Two_Std", "Negative_Mean_Return", "Negative_Mean_Plus_Two_Std", "Negative_Mean_Minus_Two_Std"],
            title=f"{fund} MA ({ma_label}) Forward Mean, +/- 2 Std Return vs Forward Return Window",
            x_label="Forward Return Window",
            x_format="String",
            x_format_decimal_places=0,
            x_tick_spacing=1,
            x_tick_start=None,
            x_tick_rotation=0,
            y_label="Return",
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
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=False,
            plot_file_name=None,
        )
```


    
![png](predictive-power-moving-averages_files/predictive-power-moving-averages_91_0.png)
    


We can see that the mean +2 std return line is for the positive price-MA condition is actually above the mean +2 std return line for the negative price-MA condition, whichi is different than any of the other funds. The explanation? The forward positive return tail is fatter, which is actually a more desirable condition. While we'd like a tight distribution, we also will accept a fatter positive tail, as that means that the forward returns are more likely to be positive and larger than they would be otherwise.

## Conclusion

This analysis shows that the predictive power of moving averages varies across different asset classes. While some ETFs, particularly those representing equities, demonstrate a stronger relationship between price-MA differences and future returns, others, like commodities and long-term bonds, show less predictive power. The findings suggest that investors may benefit from using the price-MA relationship when developing trend following investment strategies.


