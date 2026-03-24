# Investigating A VIX Trading Signal

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

# Data Sources
import yfinance as yf

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

# Print system path
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")
```

    0: /usr/lib/python313.zip
    1: /usr/lib/python3.13
    2: /usr/lib/python3.13/lib-dynload
    3: 
    4: /home/jared/python-virtual-envs/general-venv-p313/lib/python3.13/site-packages
    5: /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io/src


## Track Index Dependencies


```python
# Create file to track markdown dependencies
dep_file = Path("index_dep.txt")
dep_file.write_text("")
```




    0



## Python Functions


```python
from calc_vix_trade_pnl import calc_vix_trade_pnl
from df_info import df_info
from df_info_markdown import df_info_markdown
from export_track_md_deps import export_track_md_deps
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_stats import plot_stats
from plot_time_series import plot_time_series
from plot_vix_with_trades import plot_vix_with_trades
from yf_pull_data import yf_pull_data
```

## Data Overview - VIX

### Acquire CBOE Volatility Index (VIX) Data


```python
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="^VIX",
    adjusted=True,
    source="Yahoo_Finance", 
    asset_class="Indices", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)
```

    The first and last date of data for ^VIX is: 



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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1990-01-02</th>
      <td>17.24</td>
      <td>17.24</td>
      <td>17.24</td>
      <td>17.24</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2026-03-20</th>
      <td>26.780001</td>
      <td>29.280001</td>
      <td>23.68</td>
      <td>24.459999</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>


    Yahoo Finance data complete for ^VIX
    --------------------





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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1990-01-02</th>
      <td>17.240000</td>
      <td>17.240000</td>
      <td>17.240000</td>
      <td>17.240000</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1990-01-03</th>
      <td>18.190001</td>
      <td>18.190001</td>
      <td>18.190001</td>
      <td>18.190001</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1990-01-04</th>
      <td>19.219999</td>
      <td>19.219999</td>
      <td>19.219999</td>
      <td>19.219999</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1990-01-05</th>
      <td>20.110001</td>
      <td>20.110001</td>
      <td>20.110001</td>
      <td>20.110001</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1990-01-08</th>
      <td>20.260000</td>
      <td>20.260000</td>
      <td>20.260000</td>
      <td>20.260000</td>
      <td>0</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-03-16</th>
      <td>23.510000</td>
      <td>26.420000</td>
      <td>23.230000</td>
      <td>25.879999</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2026-03-17</th>
      <td>22.370001</td>
      <td>24.580000</td>
      <td>21.870001</td>
      <td>24.559999</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2026-03-18</th>
      <td>25.090000</td>
      <td>25.129999</td>
      <td>21.469999</td>
      <td>21.510000</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2026-03-19</th>
      <td>24.059999</td>
      <td>27.520000</td>
      <td>23.540001</td>
      <td>25.600000</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2026-03-20</th>
      <td>26.780001</td>
      <td>29.280001</td>
      <td>23.680000</td>
      <td>24.459999</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>9121 rows × 5 columns</p>
</div>



### Load Data - VIX


```python
# Set decimal places
pandas_set_decimal_places(2)

# VIX
vix = load_data(
    base_directory=DATA_DIR,
    ticker="^VIX",
    source="Yahoo_Finance", 
    asset_class="Indices",
    timeframe="Daily",
    file_format="excel",
)

# Set 'Date' column as datetime
vix['Date'] = pd.to_datetime(vix['Date'])

# Drop 'Volume'
vix.drop(columns = {'Volume'}, inplace = True)

# Set Date as index
vix.set_index('Date', inplace = True)

# Check to see if there are any NaN values
vix[vix['High'].isna()]

# Forward fill to clean up missing data
vix['High'] = vix['High'].ffill()
```

### DataFrame Info - VIX


```python
df_info(vix)
```

    The columns, shape, and data types are:
    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 9121 entries, 1990-01-02 to 2026-03-20
    Data columns (total 4 columns):
     #   Column  Non-Null Count  Dtype  
    ---  ------  --------------  -----  
     0   Close   9121 non-null   float64
     1   High    9121 non-null   float64
     2   Low     9121 non-null   float64
     3   Open    9121 non-null   float64
    dtypes: float64(4)
    memory usage: 356.3 KB
    None
    The first 5 rows are:



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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
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
      <th>1990-01-02</th>
      <td>17.24</td>
      <td>17.24</td>
      <td>17.24</td>
      <td>17.24</td>
    </tr>
    <tr>
      <th>1990-01-03</th>
      <td>18.19</td>
      <td>18.19</td>
      <td>18.19</td>
      <td>18.19</td>
    </tr>
    <tr>
      <th>1990-01-04</th>
      <td>19.22</td>
      <td>19.22</td>
      <td>19.22</td>
      <td>19.22</td>
    </tr>
    <tr>
      <th>1990-01-05</th>
      <td>20.11</td>
      <td>20.11</td>
      <td>20.11</td>
      <td>20.11</td>
    </tr>
    <tr>
      <th>1990-01-08</th>
      <td>20.26</td>
      <td>20.26</td>
      <td>20.26</td>
      <td>20.26</td>
    </tr>
  </tbody>
</table>
</div>


    The last 5 rows are:



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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
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
      <th>2026-03-16</th>
      <td>23.51</td>
      <td>26.42</td>
      <td>23.23</td>
      <td>25.88</td>
    </tr>
    <tr>
      <th>2026-03-17</th>
      <td>22.37</td>
      <td>24.58</td>
      <td>21.87</td>
      <td>24.56</td>
    </tr>
    <tr>
      <th>2026-03-18</th>
      <td>25.09</td>
      <td>25.13</td>
      <td>21.47</td>
      <td>21.51</td>
    </tr>
    <tr>
      <th>2026-03-19</th>
      <td>24.06</td>
      <td>27.52</td>
      <td>23.54</td>
      <td>25.60</td>
    </tr>
    <tr>
      <th>2026-03-20</th>
      <td>26.78</td>
      <td>29.28</td>
      <td>23.68</td>
      <td>24.46</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_01_VIX_DF_Info_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_VIX_DF_Info.md", 
    content=df_info_markdown(vix),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 01_VIX_DF_Info.md


### Statistics - VIX


```python
vix_stats = vix.describe()
num_std = range(-1, 6)  # Adjusted to include -1 to 5
for num in num_std:
    vix_stats.loc[f"mean + {num} std"] = {
        'Open': vix_stats.loc['mean']['Open'] + num * vix_stats.loc['std']['Open'],
        'High': vix_stats.loc['mean']['High'] + num * vix_stats.loc['std']['High'],
        'Low': vix_stats.loc['mean']['Low'] + num * vix_stats.loc['std']['Low'],
        'Close': vix_stats.loc['mean']['Close'] + num * vix_stats.loc['std']['Close'],
    }

display(vix_stats)
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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>9121.00</td>
      <td>9121.00</td>
      <td>9121.00</td>
      <td>9121.00</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>19.46</td>
      <td>20.37</td>
      <td>18.78</td>
      <td>19.55</td>
    </tr>
    <tr>
      <th>std</th>
      <td>7.77</td>
      <td>8.32</td>
      <td>7.32</td>
      <td>7.84</td>
    </tr>
    <tr>
      <th>min</th>
      <td>9.14</td>
      <td>9.31</td>
      <td>8.56</td>
      <td>9.01</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>13.96</td>
      <td>14.61</td>
      <td>13.47</td>
      <td>13.98</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>17.61</td>
      <td>18.33</td>
      <td>17.01</td>
      <td>17.66</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>22.74</td>
      <td>23.75</td>
      <td>22.06</td>
      <td>22.90</td>
    </tr>
    <tr>
      <th>max</th>
      <td>82.69</td>
      <td>89.53</td>
      <td>72.76</td>
      <td>82.69</td>
    </tr>
    <tr>
      <th>mean + -1 std</th>
      <td>11.69</td>
      <td>12.05</td>
      <td>11.46</td>
      <td>11.71</td>
    </tr>
    <tr>
      <th>mean + 0 std</th>
      <td>19.46</td>
      <td>20.37</td>
      <td>18.78</td>
      <td>19.55</td>
    </tr>
    <tr>
      <th>mean + 1 std</th>
      <td>27.22</td>
      <td>28.70</td>
      <td>26.10</td>
      <td>27.39</td>
    </tr>
    <tr>
      <th>mean + 2 std</th>
      <td>34.99</td>
      <td>37.02</td>
      <td>33.43</td>
      <td>35.24</td>
    </tr>
    <tr>
      <th>mean + 3 std</th>
      <td>42.76</td>
      <td>45.35</td>
      <td>40.75</td>
      <td>43.08</td>
    </tr>
    <tr>
      <th>mean + 4 std</th>
      <td>50.53</td>
      <td>53.67</td>
      <td>48.07</td>
      <td>50.92</td>
    </tr>
    <tr>
      <th>mean + 5 std</th>
      <td>58.29</td>
      <td>61.99</td>
      <td>55.40</td>
      <td>58.76</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_01_VIX_Stats_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_VIX_Stats.md", 
    content=vix_stats.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 01_VIX_Stats.md



```python
# Group by year and calculate mean and std for OHLC
vix_stats_by_year = vix.groupby(vix.index.year)[["Open", "High", "Low", "Close"]].agg(["mean", "std" ,"min", "max"])

# Flatten the column MultiIndex
vix_stats_by_year.columns = ['_'.join(col).strip() for col in vix_stats_by_year.columns.values]
vix_stats_by_year.index.name = "Year"

display(vix_stats_by_year)
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
      <th>Open_mean</th>
      <th>Open_std</th>
      <th>Open_min</th>
      <th>Open_max</th>
      <th>High_mean</th>
      <th>High_std</th>
      <th>High_min</th>
      <th>High_max</th>
      <th>Low_mean</th>
      <th>Low_std</th>
      <th>Low_min</th>
      <th>Low_max</th>
      <th>Close_mean</th>
      <th>Close_std</th>
      <th>Close_min</th>
      <th>Close_max</th>
    </tr>
    <tr>
      <th>Year</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
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
      <th>1990</th>
      <td>23.06</td>
      <td>4.74</td>
      <td>14.72</td>
      <td>36.47</td>
      <td>23.06</td>
      <td>4.74</td>
      <td>14.72</td>
      <td>36.47</td>
      <td>23.06</td>
      <td>4.74</td>
      <td>14.72</td>
      <td>36.47</td>
      <td>23.06</td>
      <td>4.74</td>
      <td>14.72</td>
      <td>36.47</td>
    </tr>
    <tr>
      <th>1991</th>
      <td>18.38</td>
      <td>3.68</td>
      <td>13.95</td>
      <td>36.20</td>
      <td>18.38</td>
      <td>3.68</td>
      <td>13.95</td>
      <td>36.20</td>
      <td>18.38</td>
      <td>3.68</td>
      <td>13.95</td>
      <td>36.20</td>
      <td>18.38</td>
      <td>3.68</td>
      <td>13.95</td>
      <td>36.20</td>
    </tr>
    <tr>
      <th>1992</th>
      <td>15.23</td>
      <td>2.26</td>
      <td>10.29</td>
      <td>20.67</td>
      <td>16.03</td>
      <td>2.19</td>
      <td>11.90</td>
      <td>25.13</td>
      <td>14.85</td>
      <td>2.14</td>
      <td>10.29</td>
      <td>19.67</td>
      <td>15.45</td>
      <td>2.12</td>
      <td>11.51</td>
      <td>21.02</td>
    </tr>
    <tr>
      <th>1993</th>
      <td>12.70</td>
      <td>1.37</td>
      <td>9.18</td>
      <td>16.20</td>
      <td>13.34</td>
      <td>1.40</td>
      <td>9.55</td>
      <td>18.31</td>
      <td>12.25</td>
      <td>1.28</td>
      <td>8.89</td>
      <td>15.77</td>
      <td>12.69</td>
      <td>1.33</td>
      <td>9.31</td>
      <td>17.30</td>
    </tr>
    <tr>
      <th>1994</th>
      <td>13.79</td>
      <td>2.06</td>
      <td>9.86</td>
      <td>23.61</td>
      <td>14.58</td>
      <td>2.28</td>
      <td>10.31</td>
      <td>28.30</td>
      <td>13.38</td>
      <td>1.99</td>
      <td>9.59</td>
      <td>23.61</td>
      <td>13.93</td>
      <td>2.07</td>
      <td>9.94</td>
      <td>23.87</td>
    </tr>
    <tr>
      <th>1995</th>
      <td>12.27</td>
      <td>1.03</td>
      <td>10.29</td>
      <td>15.79</td>
      <td>12.93</td>
      <td>1.07</td>
      <td>10.95</td>
      <td>16.99</td>
      <td>11.96</td>
      <td>0.98</td>
      <td>10.06</td>
      <td>14.97</td>
      <td>12.39</td>
      <td>0.97</td>
      <td>10.36</td>
      <td>15.74</td>
    </tr>
    <tr>
      <th>1996</th>
      <td>16.31</td>
      <td>1.92</td>
      <td>11.24</td>
      <td>23.90</td>
      <td>16.99</td>
      <td>2.12</td>
      <td>12.29</td>
      <td>27.05</td>
      <td>15.94</td>
      <td>1.82</td>
      <td>11.11</td>
      <td>21.43</td>
      <td>16.44</td>
      <td>1.94</td>
      <td>12.00</td>
      <td>21.99</td>
    </tr>
    <tr>
      <th>1997</th>
      <td>22.43</td>
      <td>4.33</td>
      <td>16.67</td>
      <td>45.69</td>
      <td>23.11</td>
      <td>4.56</td>
      <td>18.02</td>
      <td>48.64</td>
      <td>21.85</td>
      <td>3.98</td>
      <td>16.36</td>
      <td>36.43</td>
      <td>22.38</td>
      <td>4.14</td>
      <td>17.09</td>
      <td>38.20</td>
    </tr>
    <tr>
      <th>1998</th>
      <td>25.68</td>
      <td>6.96</td>
      <td>16.42</td>
      <td>47.95</td>
      <td>26.61</td>
      <td>7.36</td>
      <td>16.50</td>
      <td>49.53</td>
      <td>24.89</td>
      <td>6.58</td>
      <td>16.10</td>
      <td>45.58</td>
      <td>25.60</td>
      <td>6.86</td>
      <td>16.23</td>
      <td>45.74</td>
    </tr>
    <tr>
      <th>1999</th>
      <td>24.39</td>
      <td>2.90</td>
      <td>18.05</td>
      <td>32.62</td>
      <td>25.20</td>
      <td>3.01</td>
      <td>18.48</td>
      <td>33.66</td>
      <td>23.75</td>
      <td>2.76</td>
      <td>17.07</td>
      <td>31.13</td>
      <td>24.37</td>
      <td>2.88</td>
      <td>17.42</td>
      <td>32.98</td>
    </tr>
    <tr>
      <th>2000</th>
      <td>23.41</td>
      <td>3.43</td>
      <td>16.81</td>
      <td>33.70</td>
      <td>24.10</td>
      <td>3.66</td>
      <td>17.06</td>
      <td>34.31</td>
      <td>22.75</td>
      <td>3.19</td>
      <td>16.28</td>
      <td>30.56</td>
      <td>23.32</td>
      <td>3.41</td>
      <td>16.53</td>
      <td>33.49</td>
    </tr>
    <tr>
      <th>2001</th>
      <td>26.04</td>
      <td>4.98</td>
      <td>19.21</td>
      <td>48.93</td>
      <td>26.64</td>
      <td>5.19</td>
      <td>19.37</td>
      <td>49.35</td>
      <td>25.22</td>
      <td>4.61</td>
      <td>18.74</td>
      <td>42.66</td>
      <td>25.75</td>
      <td>4.78</td>
      <td>18.76</td>
      <td>43.74</td>
    </tr>
    <tr>
      <th>2002</th>
      <td>27.53</td>
      <td>7.03</td>
      <td>17.23</td>
      <td>48.17</td>
      <td>28.28</td>
      <td>7.25</td>
      <td>17.51</td>
      <td>48.46</td>
      <td>26.60</td>
      <td>6.64</td>
      <td>17.02</td>
      <td>42.05</td>
      <td>27.29</td>
      <td>6.91</td>
      <td>17.40</td>
      <td>45.08</td>
    </tr>
    <tr>
      <th>2003</th>
      <td>22.21</td>
      <td>5.31</td>
      <td>15.59</td>
      <td>35.21</td>
      <td>22.61</td>
      <td>5.35</td>
      <td>16.19</td>
      <td>35.66</td>
      <td>21.64</td>
      <td>5.18</td>
      <td>14.66</td>
      <td>33.99</td>
      <td>21.98</td>
      <td>5.24</td>
      <td>15.58</td>
      <td>34.69</td>
    </tr>
    <tr>
      <th>2004</th>
      <td>15.59</td>
      <td>1.93</td>
      <td>11.41</td>
      <td>21.06</td>
      <td>16.05</td>
      <td>2.02</td>
      <td>11.64</td>
      <td>22.67</td>
      <td>15.05</td>
      <td>1.79</td>
      <td>11.14</td>
      <td>20.61</td>
      <td>15.48</td>
      <td>1.92</td>
      <td>11.23</td>
      <td>21.58</td>
    </tr>
    <tr>
      <th>2005</th>
      <td>12.84</td>
      <td>1.44</td>
      <td>10.23</td>
      <td>18.33</td>
      <td>13.28</td>
      <td>1.59</td>
      <td>10.48</td>
      <td>18.59</td>
      <td>12.39</td>
      <td>1.32</td>
      <td>9.88</td>
      <td>16.41</td>
      <td>12.81</td>
      <td>1.47</td>
      <td>10.23</td>
      <td>17.74</td>
    </tr>
    <tr>
      <th>2006</th>
      <td>12.90</td>
      <td>2.18</td>
      <td>9.68</td>
      <td>23.45</td>
      <td>13.33</td>
      <td>2.46</td>
      <td>10.06</td>
      <td>23.81</td>
      <td>12.38</td>
      <td>1.96</td>
      <td>9.39</td>
      <td>21.45</td>
      <td>12.81</td>
      <td>2.25</td>
      <td>9.90</td>
      <td>23.81</td>
    </tr>
    <tr>
      <th>2007</th>
      <td>17.59</td>
      <td>5.36</td>
      <td>9.99</td>
      <td>32.68</td>
      <td>18.44</td>
      <td>5.76</td>
      <td>10.26</td>
      <td>37.50</td>
      <td>16.75</td>
      <td>4.95</td>
      <td>9.70</td>
      <td>30.44</td>
      <td>17.54</td>
      <td>5.36</td>
      <td>9.89</td>
      <td>31.09</td>
    </tr>
    <tr>
      <th>2008</th>
      <td>32.83</td>
      <td>16.41</td>
      <td>16.30</td>
      <td>80.74</td>
      <td>34.57</td>
      <td>17.83</td>
      <td>17.84</td>
      <td>89.53</td>
      <td>30.96</td>
      <td>14.96</td>
      <td>15.82</td>
      <td>72.76</td>
      <td>32.69</td>
      <td>16.38</td>
      <td>16.30</td>
      <td>80.86</td>
    </tr>
    <tr>
      <th>2009</th>
      <td>31.75</td>
      <td>9.20</td>
      <td>19.54</td>
      <td>52.65</td>
      <td>32.78</td>
      <td>9.61</td>
      <td>19.67</td>
      <td>57.36</td>
      <td>30.50</td>
      <td>8.63</td>
      <td>19.25</td>
      <td>49.27</td>
      <td>31.48</td>
      <td>9.08</td>
      <td>19.47</td>
      <td>56.65</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>22.73</td>
      <td>5.29</td>
      <td>15.44</td>
      <td>47.66</td>
      <td>23.69</td>
      <td>5.82</td>
      <td>16.00</td>
      <td>48.20</td>
      <td>21.69</td>
      <td>4.61</td>
      <td>15.23</td>
      <td>40.30</td>
      <td>22.55</td>
      <td>5.27</td>
      <td>15.45</td>
      <td>45.79</td>
    </tr>
    <tr>
      <th>2011</th>
      <td>24.27</td>
      <td>8.17</td>
      <td>14.31</td>
      <td>46.18</td>
      <td>25.40</td>
      <td>8.78</td>
      <td>14.99</td>
      <td>48.00</td>
      <td>23.15</td>
      <td>7.59</td>
      <td>14.27</td>
      <td>41.51</td>
      <td>24.20</td>
      <td>8.14</td>
      <td>14.62</td>
      <td>48.00</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>17.93</td>
      <td>2.60</td>
      <td>13.68</td>
      <td>26.35</td>
      <td>18.59</td>
      <td>2.72</td>
      <td>14.08</td>
      <td>27.73</td>
      <td>17.21</td>
      <td>2.37</td>
      <td>13.30</td>
      <td>25.72</td>
      <td>17.80</td>
      <td>2.54</td>
      <td>13.45</td>
      <td>26.66</td>
    </tr>
    <tr>
      <th>2013</th>
      <td>14.29</td>
      <td>1.67</td>
      <td>11.52</td>
      <td>20.87</td>
      <td>14.82</td>
      <td>1.88</td>
      <td>11.75</td>
      <td>21.91</td>
      <td>13.80</td>
      <td>1.51</td>
      <td>11.05</td>
      <td>19.04</td>
      <td>14.23</td>
      <td>1.74</td>
      <td>11.30</td>
      <td>20.49</td>
    </tr>
    <tr>
      <th>2014</th>
      <td>14.23</td>
      <td>2.65</td>
      <td>10.40</td>
      <td>29.26</td>
      <td>14.95</td>
      <td>3.02</td>
      <td>10.76</td>
      <td>31.06</td>
      <td>13.61</td>
      <td>2.21</td>
      <td>10.28</td>
      <td>24.64</td>
      <td>14.17</td>
      <td>2.62</td>
      <td>10.32</td>
      <td>25.27</td>
    </tr>
    <tr>
      <th>2015</th>
      <td>16.71</td>
      <td>3.99</td>
      <td>11.77</td>
      <td>31.91</td>
      <td>17.79</td>
      <td>5.03</td>
      <td>12.22</td>
      <td>53.29</td>
      <td>15.85</td>
      <td>3.65</td>
      <td>10.88</td>
      <td>29.91</td>
      <td>16.67</td>
      <td>4.34</td>
      <td>11.95</td>
      <td>40.74</td>
    </tr>
    <tr>
      <th>2016</th>
      <td>16.01</td>
      <td>4.05</td>
      <td>11.32</td>
      <td>29.01</td>
      <td>16.85</td>
      <td>4.40</td>
      <td>11.49</td>
      <td>32.09</td>
      <td>15.16</td>
      <td>3.66</td>
      <td>10.93</td>
      <td>26.67</td>
      <td>15.83</td>
      <td>3.97</td>
      <td>11.27</td>
      <td>28.14</td>
    </tr>
    <tr>
      <th>2017</th>
      <td>11.14</td>
      <td>1.34</td>
      <td>9.23</td>
      <td>16.19</td>
      <td>11.72</td>
      <td>1.54</td>
      <td>9.52</td>
      <td>17.28</td>
      <td>10.64</td>
      <td>1.16</td>
      <td>8.56</td>
      <td>14.97</td>
      <td>11.09</td>
      <td>1.36</td>
      <td>9.14</td>
      <td>16.04</td>
    </tr>
    <tr>
      <th>2018</th>
      <td>16.63</td>
      <td>5.01</td>
      <td>9.01</td>
      <td>37.32</td>
      <td>18.03</td>
      <td>6.12</td>
      <td>9.31</td>
      <td>50.30</td>
      <td>15.53</td>
      <td>4.25</td>
      <td>8.92</td>
      <td>29.66</td>
      <td>16.64</td>
      <td>5.09</td>
      <td>9.15</td>
      <td>37.32</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>15.57</td>
      <td>2.74</td>
      <td>11.55</td>
      <td>27.54</td>
      <td>16.41</td>
      <td>3.06</td>
      <td>11.79</td>
      <td>28.53</td>
      <td>14.76</td>
      <td>2.38</td>
      <td>11.03</td>
      <td>24.05</td>
      <td>15.39</td>
      <td>2.61</td>
      <td>11.54</td>
      <td>25.45</td>
    </tr>
    <tr>
      <th>2020</th>
      <td>29.52</td>
      <td>12.45</td>
      <td>12.20</td>
      <td>82.69</td>
      <td>31.46</td>
      <td>13.89</td>
      <td>12.42</td>
      <td>85.47</td>
      <td>27.50</td>
      <td>10.85</td>
      <td>11.75</td>
      <td>70.37</td>
      <td>29.25</td>
      <td>12.34</td>
      <td>12.10</td>
      <td>82.69</td>
    </tr>
    <tr>
      <th>2021</th>
      <td>19.83</td>
      <td>3.47</td>
      <td>15.02</td>
      <td>35.16</td>
      <td>21.12</td>
      <td>4.22</td>
      <td>15.54</td>
      <td>37.51</td>
      <td>18.65</td>
      <td>2.93</td>
      <td>14.10</td>
      <td>29.24</td>
      <td>19.66</td>
      <td>3.62</td>
      <td>15.01</td>
      <td>37.21</td>
    </tr>
    <tr>
      <th>2022</th>
      <td>25.98</td>
      <td>4.30</td>
      <td>16.57</td>
      <td>37.50</td>
      <td>27.25</td>
      <td>4.59</td>
      <td>17.81</td>
      <td>38.94</td>
      <td>24.69</td>
      <td>3.91</td>
      <td>16.34</td>
      <td>33.11</td>
      <td>25.62</td>
      <td>4.22</td>
      <td>16.60</td>
      <td>36.45</td>
    </tr>
    <tr>
      <th>2023</th>
      <td>17.12</td>
      <td>3.17</td>
      <td>11.96</td>
      <td>27.77</td>
      <td>17.83</td>
      <td>3.58</td>
      <td>12.46</td>
      <td>30.81</td>
      <td>16.36</td>
      <td>2.89</td>
      <td>11.81</td>
      <td>24.00</td>
      <td>16.87</td>
      <td>3.14</td>
      <td>12.07</td>
      <td>26.52</td>
    </tr>
    <tr>
      <th>2024</th>
      <td>15.69</td>
      <td>3.14</td>
      <td>11.53</td>
      <td>33.71</td>
      <td>16.65</td>
      <td>4.73</td>
      <td>12.23</td>
      <td>65.73</td>
      <td>14.92</td>
      <td>2.58</td>
      <td>10.62</td>
      <td>24.02</td>
      <td>15.61</td>
      <td>3.36</td>
      <td>11.86</td>
      <td>38.57</td>
    </tr>
    <tr>
      <th>2025</th>
      <td>19.19</td>
      <td>5.57</td>
      <td>14.09</td>
      <td>60.13</td>
      <td>20.44</td>
      <td>6.74</td>
      <td>14.16</td>
      <td>60.13</td>
      <td>18.07</td>
      <td>4.22</td>
      <td>13.38</td>
      <td>38.58</td>
      <td>18.96</td>
      <td>5.32</td>
      <td>13.47</td>
      <td>52.33</td>
    </tr>
    <tr>
      <th>2026</th>
      <td>19.83</td>
      <td>4.15</td>
      <td>14.85</td>
      <td>35.12</td>
      <td>21.29</td>
      <td>4.57</td>
      <td>15.21</td>
      <td>35.30</td>
      <td>18.44</td>
      <td>3.13</td>
      <td>14.43</td>
      <td>24.76</td>
      <td>19.57</td>
      <td>3.85</td>
      <td>14.49</td>
      <td>29.49</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_01_VIX_Stats_By_Year_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_VIX_Stats_By_Year.md", 
    content=vix_stats_by_year.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 01_VIX_Stats_By_Year.md



```python
# Group by month and calculate mean and std for OHLC
vix_stats_by_month = vix.groupby(vix.index.month)[["Open", "High", "Low", "Close"]].agg(["mean", "std", "min", "max"])

# Flatten the column MultiIndex
vix_stats_by_month.columns = ['_'.join(col).strip() for col in vix_stats_by_month.columns.values]
vix_stats_by_month.index.name = "Month"

display(vix_stats_by_month)
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
      <th>Open_mean</th>
      <th>Open_std</th>
      <th>Open_min</th>
      <th>Open_max</th>
      <th>High_mean</th>
      <th>High_std</th>
      <th>High_min</th>
      <th>High_max</th>
      <th>Low_mean</th>
      <th>Low_std</th>
      <th>Low_min</th>
      <th>Low_max</th>
      <th>Close_mean</th>
      <th>Close_std</th>
      <th>Close_min</th>
      <th>Close_max</th>
    </tr>
    <tr>
      <th>Month</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
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
      <th>1</th>
      <td>19.26</td>
      <td>7.13</td>
      <td>9.01</td>
      <td>51.52</td>
      <td>20.05</td>
      <td>7.50</td>
      <td>9.31</td>
      <td>57.36</td>
      <td>18.52</td>
      <td>6.80</td>
      <td>8.92</td>
      <td>49.27</td>
      <td>19.14</td>
      <td>7.09</td>
      <td>9.15</td>
      <td>56.65</td>
    </tr>
    <tr>
      <th>2</th>
      <td>19.66</td>
      <td>7.12</td>
      <td>10.19</td>
      <td>52.50</td>
      <td>20.52</td>
      <td>7.55</td>
      <td>10.26</td>
      <td>53.16</td>
      <td>18.88</td>
      <td>6.72</td>
      <td>9.70</td>
      <td>48.97</td>
      <td>19.57</td>
      <td>7.04</td>
      <td>10.02</td>
      <td>52.62</td>
    </tr>
    <tr>
      <th>3</th>
      <td>20.56</td>
      <td>9.57</td>
      <td>10.59</td>
      <td>82.69</td>
      <td>21.50</td>
      <td>10.43</td>
      <td>11.24</td>
      <td>85.47</td>
      <td>19.60</td>
      <td>8.59</td>
      <td>10.53</td>
      <td>70.37</td>
      <td>20.43</td>
      <td>9.49</td>
      <td>10.74</td>
      <td>82.69</td>
    </tr>
    <tr>
      <th>4</th>
      <td>19.43</td>
      <td>7.48</td>
      <td>10.39</td>
      <td>60.13</td>
      <td>20.24</td>
      <td>7.93</td>
      <td>10.89</td>
      <td>60.59</td>
      <td>18.65</td>
      <td>6.88</td>
      <td>10.22</td>
      <td>52.76</td>
      <td>19.29</td>
      <td>7.28</td>
      <td>10.36</td>
      <td>57.06</td>
    </tr>
    <tr>
      <th>5</th>
      <td>18.60</td>
      <td>6.04</td>
      <td>9.75</td>
      <td>47.66</td>
      <td>19.40</td>
      <td>6.43</td>
      <td>10.14</td>
      <td>48.20</td>
      <td>17.89</td>
      <td>5.63</td>
      <td>9.56</td>
      <td>40.30</td>
      <td>18.51</td>
      <td>5.96</td>
      <td>9.77</td>
      <td>45.79</td>
    </tr>
    <tr>
      <th>6</th>
      <td>18.46</td>
      <td>5.75</td>
      <td>9.79</td>
      <td>44.09</td>
      <td>19.15</td>
      <td>6.02</td>
      <td>10.28</td>
      <td>44.44</td>
      <td>17.73</td>
      <td>5.40</td>
      <td>9.37</td>
      <td>34.97</td>
      <td>18.34</td>
      <td>5.68</td>
      <td>9.75</td>
      <td>40.79</td>
    </tr>
    <tr>
      <th>7</th>
      <td>17.83</td>
      <td>5.67</td>
      <td>9.18</td>
      <td>48.17</td>
      <td>18.53</td>
      <td>5.90</td>
      <td>9.52</td>
      <td>48.46</td>
      <td>17.21</td>
      <td>5.41</td>
      <td>8.84</td>
      <td>42.05</td>
      <td>17.76</td>
      <td>5.60</td>
      <td>9.36</td>
      <td>44.92</td>
    </tr>
    <tr>
      <th>8</th>
      <td>19.09</td>
      <td>6.67</td>
      <td>10.04</td>
      <td>45.34</td>
      <td>20.03</td>
      <td>7.38</td>
      <td>10.32</td>
      <td>65.73</td>
      <td>18.35</td>
      <td>6.32</td>
      <td>9.52</td>
      <td>41.77</td>
      <td>19.09</td>
      <td>6.80</td>
      <td>9.93</td>
      <td>48.00</td>
    </tr>
    <tr>
      <th>9</th>
      <td>20.37</td>
      <td>8.23</td>
      <td>9.59</td>
      <td>48.93</td>
      <td>21.21</td>
      <td>8.55</td>
      <td>9.83</td>
      <td>49.35</td>
      <td>19.62</td>
      <td>7.82</td>
      <td>9.36</td>
      <td>43.74</td>
      <td>20.29</td>
      <td>8.12</td>
      <td>9.51</td>
      <td>46.72</td>
    </tr>
    <tr>
      <th>10</th>
      <td>21.72</td>
      <td>10.16</td>
      <td>9.23</td>
      <td>79.13</td>
      <td>22.73</td>
      <td>10.97</td>
      <td>9.62</td>
      <td>89.53</td>
      <td>20.82</td>
      <td>9.40</td>
      <td>9.11</td>
      <td>67.80</td>
      <td>21.64</td>
      <td>10.12</td>
      <td>9.19</td>
      <td>80.06</td>
    </tr>
    <tr>
      <th>11</th>
      <td>20.34</td>
      <td>9.54</td>
      <td>9.31</td>
      <td>80.74</td>
      <td>21.06</td>
      <td>9.91</td>
      <td>9.74</td>
      <td>81.48</td>
      <td>19.53</td>
      <td>8.91</td>
      <td>8.56</td>
      <td>72.76</td>
      <td>20.16</td>
      <td>9.41</td>
      <td>9.14</td>
      <td>80.86</td>
    </tr>
    <tr>
      <th>12</th>
      <td>19.24</td>
      <td>8.16</td>
      <td>9.36</td>
      <td>66.68</td>
      <td>19.98</td>
      <td>8.43</td>
      <td>9.55</td>
      <td>68.60</td>
      <td>18.53</td>
      <td>7.79</td>
      <td>8.89</td>
      <td>62.31</td>
      <td>19.18</td>
      <td>8.07</td>
      <td>9.31</td>
      <td>68.51</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_01_VIX_Stats_By_Month_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_VIX_Stats_By_Month.md", 
    content=vix_stats_by_month.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 01_VIX_Stats_By_Month.md


### Deciles - VIX


```python
vix_deciles = vix.quantile(np.arange(0, 1.1, 0.1))
display(vix_deciles)
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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0.00</th>
      <td>9.14</td>
      <td>9.31</td>
      <td>8.56</td>
      <td>9.01</td>
    </tr>
    <tr>
      <th>0.10</th>
      <td>12.14</td>
      <td>12.66</td>
      <td>11.74</td>
      <td>12.16</td>
    </tr>
    <tr>
      <th>0.20</th>
      <td>13.31</td>
      <td>13.91</td>
      <td>12.90</td>
      <td>13.35</td>
    </tr>
    <tr>
      <th>0.30</th>
      <td>14.68</td>
      <td>15.39</td>
      <td>14.18</td>
      <td>14.76</td>
    </tr>
    <tr>
      <th>0.40</th>
      <td>16.12</td>
      <td>16.78</td>
      <td>15.60</td>
      <td>16.16</td>
    </tr>
    <tr>
      <th>0.50</th>
      <td>17.61</td>
      <td>18.33</td>
      <td>17.01</td>
      <td>17.66</td>
    </tr>
    <tr>
      <th>0.60</th>
      <td>19.49</td>
      <td>20.35</td>
      <td>18.92</td>
      <td>19.60</td>
    </tr>
    <tr>
      <th>0.70</th>
      <td>21.55</td>
      <td>22.56</td>
      <td>20.90</td>
      <td>21.67</td>
    </tr>
    <tr>
      <th>0.80</th>
      <td>24.23</td>
      <td>25.22</td>
      <td>23.35</td>
      <td>24.32</td>
    </tr>
    <tr>
      <th>0.90</th>
      <td>28.60</td>
      <td>29.90</td>
      <td>27.59</td>
      <td>28.75</td>
    </tr>
    <tr>
      <th>1.00</th>
      <td>82.69</td>
      <td>89.53</td>
      <td>72.76</td>
      <td>82.69</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_01_VIX_Deciles_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_VIX_Deciles.md", 
    content=vix_deciles.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 01_VIX_Deciles.md



```python
# Group by year for deciles
vix_deciles_by_year = vix.groupby(vix.index.year)[["Open", "High", "Low", "Close"]].quantile(np.arange(0, 1.1, 0.1))

display(vix_deciles_by_year)
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
      <th></th>
      <th>Open</th>
      <th>High</th>
      <th>Low</th>
      <th>Close</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">1990</th>
      <th>0.00</th>
      <td>14.72</td>
      <td>14.72</td>
      <td>14.72</td>
      <td>14.72</td>
    </tr>
    <tr>
      <th>0.10</th>
      <td>17.18</td>
      <td>17.18</td>
      <td>17.18</td>
      <td>17.18</td>
    </tr>
    <tr>
      <th>0.20</th>
      <td>18.47</td>
      <td>18.47</td>
      <td>18.47</td>
      <td>18.47</td>
    </tr>
    <tr>
      <th>0.30</th>
      <td>20.08</td>
      <td>20.08</td>
      <td>20.08</td>
      <td>20.08</td>
    </tr>
    <tr>
      <th>0.40</th>
      <td>21.15</td>
      <td>21.15</td>
      <td>21.15</td>
      <td>21.15</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">2026</th>
      <th>0.60</th>
      <td>19.95</td>
      <td>21.44</td>
      <td>18.89</td>
      <td>20.20</td>
    </tr>
    <tr>
      <th>0.70</th>
      <td>21.48</td>
      <td>22.97</td>
      <td>19.78</td>
      <td>21.02</td>
    </tr>
    <tr>
      <th>0.80</th>
      <td>24.39</td>
      <td>25.48</td>
      <td>21.63</td>
      <td>23.53</td>
    </tr>
    <tr>
      <th>0.90</th>
      <td>24.83</td>
      <td>27.46</td>
      <td>23.45</td>
      <td>25.04</td>
    </tr>
    <tr>
      <th>1.00</th>
      <td>35.12</td>
      <td>35.30</td>
      <td>24.76</td>
      <td>29.49</td>
    </tr>
  </tbody>
</table>
<p>407 rows × 4 columns</p>
</div>



```python
# Copy this <!-- INSERT_01_VIX_Deciles_By_Year_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_VIX_Deciles_By_Year.md", 
    content=vix_deciles_by_year.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 01_VIX_Deciles_By_Year.md



```python
current_year = datetime.now().year
last_year = current_year - 1

print(f"Last year: {last_year}")
vix_deciles_last_year = vix_deciles_by_year.loc[last_year]
display(vix_deciles_last_year)

print(f"Current year: {current_year}")
vix_deciles_current_year = vix_deciles_by_year.loc[current_year]
display(vix_deciles_current_year)
```

    Last year: 2025



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
      <th>Open</th>
      <th>High</th>
      <th>Low</th>
      <th>Close</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0.00</th>
      <td>14.09</td>
      <td>14.16</td>
      <td>13.38</td>
      <td>13.47</td>
    </tr>
    <tr>
      <th>0.10</th>
      <td>15.15</td>
      <td>15.80</td>
      <td>14.74</td>
      <td>15.04</td>
    </tr>
    <tr>
      <th>0.20</th>
      <td>15.88</td>
      <td>16.50</td>
      <td>15.28</td>
      <td>15.72</td>
    </tr>
    <tr>
      <th>0.30</th>
      <td>16.40</td>
      <td>17.09</td>
      <td>15.77</td>
      <td>16.31</td>
    </tr>
    <tr>
      <th>0.40</th>
      <td>16.79</td>
      <td>17.48</td>
      <td>16.19</td>
      <td>16.64</td>
    </tr>
    <tr>
      <th>0.50</th>
      <td>17.45</td>
      <td>18.21</td>
      <td>16.61</td>
      <td>17.20</td>
    </tr>
    <tr>
      <th>0.60</th>
      <td>18.25</td>
      <td>19.31</td>
      <td>17.42</td>
      <td>17.96</td>
    </tr>
    <tr>
      <th>0.70</th>
      <td>19.52</td>
      <td>21.01</td>
      <td>18.23</td>
      <td>19.13</td>
    </tr>
    <tr>
      <th>0.80</th>
      <td>21.16</td>
      <td>22.84</td>
      <td>19.57</td>
      <td>21.21</td>
    </tr>
    <tr>
      <th>0.90</th>
      <td>24.57</td>
      <td>26.37</td>
      <td>23.29</td>
      <td>24.66</td>
    </tr>
    <tr>
      <th>1.00</th>
      <td>60.13</td>
      <td>60.13</td>
      <td>38.58</td>
      <td>52.33</td>
    </tr>
  </tbody>
</table>
</div>


    Current year: 2026



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
      <th>Open</th>
      <th>High</th>
      <th>Low</th>
      <th>Close</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0.00</th>
      <td>14.85</td>
      <td>15.21</td>
      <td>14.43</td>
      <td>14.49</td>
    </tr>
    <tr>
      <th>0.10</th>
      <td>15.51</td>
      <td>15.96</td>
      <td>14.89</td>
      <td>15.40</td>
    </tr>
    <tr>
      <th>0.20</th>
      <td>16.05</td>
      <td>16.61</td>
      <td>15.30</td>
      <td>16.05</td>
    </tr>
    <tr>
      <th>0.30</th>
      <td>16.64</td>
      <td>18.09</td>
      <td>16.05</td>
      <td>16.71</td>
    </tr>
    <tr>
      <th>0.40</th>
      <td>17.89</td>
      <td>19.78</td>
      <td>16.78</td>
      <td>17.68</td>
    </tr>
    <tr>
      <th>0.50</th>
      <td>19.30</td>
      <td>20.90</td>
      <td>17.68</td>
      <td>18.86</td>
    </tr>
    <tr>
      <th>0.60</th>
      <td>19.95</td>
      <td>21.44</td>
      <td>18.89</td>
      <td>20.20</td>
    </tr>
    <tr>
      <th>0.70</th>
      <td>21.48</td>
      <td>22.97</td>
      <td>19.78</td>
      <td>21.02</td>
    </tr>
    <tr>
      <th>0.80</th>
      <td>24.39</td>
      <td>25.48</td>
      <td>21.63</td>
      <td>23.53</td>
    </tr>
    <tr>
      <th>0.90</th>
      <td>24.83</td>
      <td>27.46</td>
      <td>23.45</td>
      <td>25.04</td>
    </tr>
    <tr>
      <th>1.00</th>
      <td>35.12</td>
      <td>35.30</td>
      <td>24.76</td>
      <td>29.49</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_01_Last_Year_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_Last_Year.md", 
    content=f"{last_year}",
    output_type="markdown",
)

# Copy this <!-- INSERT_01_VIX_Deciles_Last_Year_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_VIX_Deciles_Last_Year.md", 
    content=vix_deciles_last_year.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 01_Last_Year.md
    ✅ Exported and tracked: 01_VIX_Deciles_Last_Year.md



```python
# Copy this <!-- INSERT_01_Current_Year_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_Current_Year.md", 
    content=f"{current_year}",
    output_type="markdown",
)

# Copy this <!-- INSERT_01_VIX_Deciles_Current_Year_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file,
    md_filename="01_VIX_Deciles_Current_Year.md",
    content=vix_deciles_current_year.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 01_Current_Year.md
    ✅ Exported and tracked: 01_VIX_Deciles_Current_Year.md


## Time Between Levels


```python
import pandas as pd
import math
from typing import Literal

Op = Literal["==", ">=", ">", "<=", "<"]

def compare(value: float, threshold: float, op: Op) -> bool:
    if op == "==":
        return value == threshold
    if op == ">=":
        return value >= threshold
    if op == ">":
        return value > threshold
    if op == "<=":
        return value <= threshold
    if op == "<":
        return value < threshold
    raise ValueError(f"Unsupported op: {op}")

def compute_waits(
    df: pd.DataFrame,
    high_col: str = "High",
    trigger_a: float = 20.0,
    trigger_b: float = 20.0,
    op_a: Op = ">=",
    op_b: Op = ">=",
    strictly_after: bool = True,
) -> pd.DataFrame:
    """
    For each day i where df[high_col] op_a trigger_a, find the next day j
    (j > i if strictly_after else j >= i) where df[high_col] op_b trigger_b.
    """
    df = df.sort_index()
    idx = df.index
    highs = df[high_col].values
    n = len(df)

    rows = []
    for i in range(n):
        if compare(highs[i], trigger_a, op_a):
            start_j = i + 1 if strictly_after else i
            j_found = None
            for j in range(start_j, n):
                if compare(highs[j], trigger_b, op_b):
                    j_found = j
                    break

            if j_found is None:
                next_date = pd.NaT if isinstance(idx, pd.DatetimeIndex) else None
                next_high = math.nan
                wait_td = math.nan
                wait_cd = math.nan
            else:
                next_date = idx[j_found]
                next_high = float(highs[j_found])
                wait_td = j_found - i
                if isinstance(idx, pd.DatetimeIndex):
                    wait_cd = (idx[j_found].normalize() - idx[i].normalize()).days
                else:
                    wait_cd = math.nan

            rows.append(
                {
                    "date_a": idx[i],
                    "high_at_a": float(highs[i]),
                    "date_b": next_date,
                    "high_at_b": next_high,
                    "wait_trading_days": wait_td,
                    "wait_calendar_days": wait_cd,
                }
            )

    return pd.DataFrame(rows)

```


```python
# When daily high <= 15, how long until next daily high >= 20?
res_lt15_to_gt20 = compute_waits(
    df=vix,
    high_col="High", 
    trigger_a=15, 
    trigger_b=20, 
    op_a="<=", 
    op_b=">=",
    strictly_after=True,
)

res_lt15_to_gt20
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
      <th>date_a</th>
      <th>high_at_a</th>
      <th>date_b</th>
      <th>high_at_b</th>
      <th>wait_trading_days</th>
      <th>wait_calendar_days</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1990-06-21</td>
      <td>14.72</td>
      <td>1990-07-23</td>
      <td>23.68</td>
      <td>21</td>
      <td>32</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1991-03-14</td>
      <td>14.94</td>
      <td>1991-04-09</td>
      <td>20.12</td>
      <td>17</td>
      <td>26</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1991-03-15</td>
      <td>14.90</td>
      <td>1991-04-09</td>
      <td>20.12</td>
      <td>16</td>
      <td>25</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1991-08-13</td>
      <td>14.73</td>
      <td>1991-08-19</td>
      <td>21.19</td>
      <td>4</td>
      <td>6</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1991-08-22</td>
      <td>14.59</td>
      <td>1991-11-15</td>
      <td>21.18</td>
      <td>60</td>
      <td>85</td>
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
      <th>2530</th>
      <td>2025-09-12</td>
      <td>14.97</td>
      <td>2025-10-10</td>
      <td>22.44</td>
      <td>20</td>
      <td>28</td>
    </tr>
    <tr>
      <th>2531</th>
      <td>2025-12-23</td>
      <td>14.45</td>
      <td>2026-01-20</td>
      <td>20.99</td>
      <td>17</td>
      <td>28</td>
    </tr>
    <tr>
      <th>2532</th>
      <td>2025-12-24</td>
      <td>14.16</td>
      <td>2026-01-20</td>
      <td>20.99</td>
      <td>16</td>
      <td>27</td>
    </tr>
    <tr>
      <th>2533</th>
      <td>2025-12-26</td>
      <td>14.29</td>
      <td>2026-01-20</td>
      <td>20.99</td>
      <td>15</td>
      <td>25</td>
    </tr>
    <tr>
      <th>2534</th>
      <td>2025-12-30</td>
      <td>14.62</td>
      <td>2026-01-20</td>
      <td>20.99</td>
      <td>13</td>
      <td>21</td>
    </tr>
  </tbody>
</table>
<p>2535 rows × 6 columns</p>
</div>




```python
# Plot histogram for wait times
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.hist(res_lt15_to_gt20['wait_trading_days'].dropna(), bins=200, alpha=0.5, label='LT 15 to GT 20')
plt.xlabel('Days')
plt.ylabel('Frequency')
plt.title('Wait Times for VIX Highs')
plt.legend()
plt.show()
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_34_0.png)
    



```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Tuple

def compute_wait_cdf(
    waits_df: pd.DataFrame,
    column: str = "wait_trading_days",
) -> pd.DataFrame:
    """
    Compute the empirical CDF for wait times.

    Returns a DataFrame with:
      - 'wait': unique wait values (sorted)
      - 'count': frequency for each wait
      - 'cdf': cumulative probability P(Wait <= x)
      - 'ccdf': complementary CDF = 1 - cdf (P(Wait > x))
    """
    # Drop NaNs; don't cast to int (keep original type)
    waits = waits_df[column].dropna().to_numpy()
    if waits.size == 0:
        return pd.DataFrame(columns=["wait", "count", "cdf", "ccdf"])

    # Unique values and counts
    vals, counts = np.unique(waits, return_counts=True)
    cum_counts = np.cumsum(counts)
    n = waits.size
    cdf = cum_counts / n
    ccdf = 1.0 - cdf

    out = pd.DataFrame(
        {"wait": vals, "count": counts, "cdf": cdf, "ccdf": ccdf}
    )
    return out
```


```python
cdf_df = compute_wait_cdf(
    waits_df=res_lt15_to_gt20,
    column="wait_trading_days")

cdf_df

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
      <th>wait</th>
      <th>count</th>
      <th>cdf</th>
      <th>ccdf</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>1</td>
      <td>0.00</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>7</td>
      <td>0.00</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>11</td>
      <td>0.01</td>
      <td>0.99</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>15</td>
      <td>0.01</td>
      <td>0.99</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>15</td>
      <td>0.02</td>
      <td>0.98</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>461</th>
      <td>472</td>
      <td>1</td>
      <td>1.00</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>462</th>
      <td>478</td>
      <td>1</td>
      <td>1.00</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>463</th>
      <td>479</td>
      <td>1</td>
      <td>1.00</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>464</th>
      <td>493</td>
      <td>1</td>
      <td>1.00</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>465</th>
      <td>494</td>
      <td>1</td>
      <td>1.00</td>
      <td>0.00</td>
    </tr>
  </tbody>
</table>
<p>466 rows × 4 columns</p>
</div>




```python
# Plot CDF
plt.figure(figsize=(10, 6))
plt.plot(cdf_df['wait'], cdf_df['cdf'])
plt.title('CDF of LT 15 to GT 20')
plt.xlabel('Wait')
plt.ylabel('CDF')
plt.grid()
plt.show()
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_37_0.png)
    



```python
import pandas as pd
import numpy as np

def empirical_hit_probabilities(
    df: pd.DataFrame,
    high_col: str,
    thresholds,
    horizons,
) -> pd.DataFrame:
    
    """
    Compute empirical probability of reaching a threshold high within given horizons.

    Parameters
    ----------
    df : pd.DataFrame
        Sorted daily data with a High column.
    high_col : str
        Name of the column with daily highs.
    thresholds : list of floats
        Target levels (e.g. [18,19,20,21,22]).
    horizons : list of ints
        Lookahead windows in trading days.

    Returns
    -------
    pd.DataFrame
        Rows = horizons, Cols = thresholds, entries = probability [0,1].
    """

    df = df.sort_index()
    highs = df[high_col].values
    n = len(highs)

    probs = pd.DataFrame(index=horizons, columns=thresholds, dtype=float)

    for h in horizons:
        valid_starts = n - h  # last h days have incomplete windows
        if valid_starts <= 0:
            continue
        window_max = np.array([highs[i+1:i+h+1].max() for i in range(valid_starts)])
        # note: exclude same day (i+1:...) so it's "future" only
        for thr in thresholds:
            hits = (window_max >= thr).sum()
            probs.loc[h, thr] = hits / valid_starts

    return probs

```


```python
probs = empirical_hit_probabilities(
    df=vix, 
    high_col="High",
    thresholds=range(15, 35),
    horizons=range(5, 101, 5),
)

display(probs)
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
      <th>15</th>
      <th>16</th>
      <th>17</th>
      <th>18</th>
      <th>19</th>
      <th>20</th>
      <th>21</th>
      <th>22</th>
      <th>23</th>
      <th>24</th>
      <th>25</th>
      <th>26</th>
      <th>27</th>
      <th>28</th>
      <th>29</th>
      <th>30</th>
      <th>31</th>
      <th>32</th>
      <th>33</th>
      <th>34</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>5</th>
      <td>0.79</td>
      <td>0.73</td>
      <td>0.66</td>
      <td>0.59</td>
      <td>0.54</td>
      <td>0.49</td>
      <td>0.44</td>
      <td>0.39</td>
      <td>0.35</td>
      <td>0.30</td>
      <td>0.26</td>
      <td>0.23</td>
      <td>0.21</td>
      <td>0.18</td>
      <td>0.16</td>
      <td>0.14</td>
      <td>0.12</td>
      <td>0.10</td>
      <td>0.09</td>
      <td>0.08</td>
    </tr>
    <tr>
      <th>10</th>
      <td>0.83</td>
      <td>0.78</td>
      <td>0.71</td>
      <td>0.65</td>
      <td>0.59</td>
      <td>0.54</td>
      <td>0.49</td>
      <td>0.43</td>
      <td>0.40</td>
      <td>0.35</td>
      <td>0.31</td>
      <td>0.27</td>
      <td>0.25</td>
      <td>0.22</td>
      <td>0.19</td>
      <td>0.17</td>
      <td>0.15</td>
      <td>0.13</td>
      <td>0.12</td>
      <td>0.10</td>
    </tr>
    <tr>
      <th>15</th>
      <td>0.86</td>
      <td>0.81</td>
      <td>0.75</td>
      <td>0.68</td>
      <td>0.62</td>
      <td>0.58</td>
      <td>0.53</td>
      <td>0.47</td>
      <td>0.43</td>
      <td>0.38</td>
      <td>0.34</td>
      <td>0.31</td>
      <td>0.28</td>
      <td>0.26</td>
      <td>0.22</td>
      <td>0.20</td>
      <td>0.17</td>
      <td>0.15</td>
      <td>0.14</td>
      <td>0.12</td>
    </tr>
    <tr>
      <th>20</th>
      <td>0.88</td>
      <td>0.83</td>
      <td>0.78</td>
      <td>0.71</td>
      <td>0.65</td>
      <td>0.61</td>
      <td>0.56</td>
      <td>0.50</td>
      <td>0.46</td>
      <td>0.41</td>
      <td>0.37</td>
      <td>0.33</td>
      <td>0.31</td>
      <td>0.28</td>
      <td>0.25</td>
      <td>0.22</td>
      <td>0.19</td>
      <td>0.17</td>
      <td>0.15</td>
      <td>0.14</td>
    </tr>
    <tr>
      <th>25</th>
      <td>0.89</td>
      <td>0.86</td>
      <td>0.80</td>
      <td>0.74</td>
      <td>0.68</td>
      <td>0.63</td>
      <td>0.59</td>
      <td>0.52</td>
      <td>0.49</td>
      <td>0.43</td>
      <td>0.39</td>
      <td>0.36</td>
      <td>0.34</td>
      <td>0.31</td>
      <td>0.27</td>
      <td>0.24</td>
      <td>0.22</td>
      <td>0.18</td>
      <td>0.17</td>
      <td>0.16</td>
    </tr>
    <tr>
      <th>30</th>
      <td>0.91</td>
      <td>0.87</td>
      <td>0.82</td>
      <td>0.76</td>
      <td>0.70</td>
      <td>0.65</td>
      <td>0.61</td>
      <td>0.54</td>
      <td>0.51</td>
      <td>0.45</td>
      <td>0.42</td>
      <td>0.39</td>
      <td>0.36</td>
      <td>0.33</td>
      <td>0.29</td>
      <td>0.26</td>
      <td>0.23</td>
      <td>0.20</td>
      <td>0.19</td>
      <td>0.17</td>
    </tr>
    <tr>
      <th>35</th>
      <td>0.92</td>
      <td>0.89</td>
      <td>0.83</td>
      <td>0.77</td>
      <td>0.72</td>
      <td>0.67</td>
      <td>0.64</td>
      <td>0.56</td>
      <td>0.53</td>
      <td>0.47</td>
      <td>0.44</td>
      <td>0.41</td>
      <td>0.38</td>
      <td>0.35</td>
      <td>0.31</td>
      <td>0.28</td>
      <td>0.25</td>
      <td>0.22</td>
      <td>0.20</td>
      <td>0.19</td>
    </tr>
    <tr>
      <th>40</th>
      <td>0.93</td>
      <td>0.90</td>
      <td>0.84</td>
      <td>0.79</td>
      <td>0.74</td>
      <td>0.69</td>
      <td>0.66</td>
      <td>0.58</td>
      <td>0.55</td>
      <td>0.49</td>
      <td>0.46</td>
      <td>0.42</td>
      <td>0.40</td>
      <td>0.37</td>
      <td>0.33</td>
      <td>0.29</td>
      <td>0.27</td>
      <td>0.23</td>
      <td>0.22</td>
      <td>0.20</td>
    </tr>
    <tr>
      <th>45</th>
      <td>0.94</td>
      <td>0.91</td>
      <td>0.86</td>
      <td>0.80</td>
      <td>0.75</td>
      <td>0.71</td>
      <td>0.67</td>
      <td>0.60</td>
      <td>0.57</td>
      <td>0.51</td>
      <td>0.47</td>
      <td>0.44</td>
      <td>0.42</td>
      <td>0.39</td>
      <td>0.34</td>
      <td>0.31</td>
      <td>0.28</td>
      <td>0.25</td>
      <td>0.23</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>50</th>
      <td>0.94</td>
      <td>0.92</td>
      <td>0.86</td>
      <td>0.81</td>
      <td>0.77</td>
      <td>0.72</td>
      <td>0.69</td>
      <td>0.61</td>
      <td>0.58</td>
      <td>0.52</td>
      <td>0.49</td>
      <td>0.46</td>
      <td>0.44</td>
      <td>0.41</td>
      <td>0.36</td>
      <td>0.32</td>
      <td>0.30</td>
      <td>0.26</td>
      <td>0.24</td>
      <td>0.23</td>
    </tr>
    <tr>
      <th>55</th>
      <td>0.95</td>
      <td>0.93</td>
      <td>0.87</td>
      <td>0.82</td>
      <td>0.78</td>
      <td>0.74</td>
      <td>0.71</td>
      <td>0.63</td>
      <td>0.60</td>
      <td>0.53</td>
      <td>0.50</td>
      <td>0.47</td>
      <td>0.45</td>
      <td>0.42</td>
      <td>0.37</td>
      <td>0.34</td>
      <td>0.31</td>
      <td>0.27</td>
      <td>0.26</td>
      <td>0.24</td>
    </tr>
    <tr>
      <th>60</th>
      <td>0.95</td>
      <td>0.93</td>
      <td>0.88</td>
      <td>0.83</td>
      <td>0.80</td>
      <td>0.75</td>
      <td>0.72</td>
      <td>0.64</td>
      <td>0.61</td>
      <td>0.54</td>
      <td>0.52</td>
      <td>0.49</td>
      <td>0.47</td>
      <td>0.43</td>
      <td>0.38</td>
      <td>0.35</td>
      <td>0.32</td>
      <td>0.29</td>
      <td>0.27</td>
      <td>0.25</td>
    </tr>
    <tr>
      <th>65</th>
      <td>0.96</td>
      <td>0.94</td>
      <td>0.89</td>
      <td>0.84</td>
      <td>0.81</td>
      <td>0.77</td>
      <td>0.74</td>
      <td>0.65</td>
      <td>0.62</td>
      <td>0.55</td>
      <td>0.53</td>
      <td>0.50</td>
      <td>0.48</td>
      <td>0.45</td>
      <td>0.40</td>
      <td>0.37</td>
      <td>0.34</td>
      <td>0.30</td>
      <td>0.28</td>
      <td>0.26</td>
    </tr>
    <tr>
      <th>70</th>
      <td>0.96</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.85</td>
      <td>0.82</td>
      <td>0.78</td>
      <td>0.75</td>
      <td>0.66</td>
      <td>0.64</td>
      <td>0.56</td>
      <td>0.54</td>
      <td>0.51</td>
      <td>0.50</td>
      <td>0.46</td>
      <td>0.41</td>
      <td>0.38</td>
      <td>0.35</td>
      <td>0.31</td>
      <td>0.29</td>
      <td>0.27</td>
    </tr>
    <tr>
      <th>75</th>
      <td>0.97</td>
      <td>0.95</td>
      <td>0.91</td>
      <td>0.86</td>
      <td>0.83</td>
      <td>0.79</td>
      <td>0.77</td>
      <td>0.67</td>
      <td>0.65</td>
      <td>0.57</td>
      <td>0.55</td>
      <td>0.53</td>
      <td>0.51</td>
      <td>0.47</td>
      <td>0.42</td>
      <td>0.39</td>
      <td>0.36</td>
      <td>0.32</td>
      <td>0.30</td>
      <td>0.29</td>
    </tr>
    <tr>
      <th>80</th>
      <td>0.97</td>
      <td>0.95</td>
      <td>0.91</td>
      <td>0.87</td>
      <td>0.84</td>
      <td>0.80</td>
      <td>0.78</td>
      <td>0.68</td>
      <td>0.66</td>
      <td>0.58</td>
      <td>0.56</td>
      <td>0.54</td>
      <td>0.52</td>
      <td>0.48</td>
      <td>0.43</td>
      <td>0.41</td>
      <td>0.37</td>
      <td>0.33</td>
      <td>0.31</td>
      <td>0.30</td>
    </tr>
    <tr>
      <th>85</th>
      <td>0.97</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.87</td>
      <td>0.84</td>
      <td>0.80</td>
      <td>0.79</td>
      <td>0.69</td>
      <td>0.67</td>
      <td>0.59</td>
      <td>0.57</td>
      <td>0.55</td>
      <td>0.53</td>
      <td>0.49</td>
      <td>0.44</td>
      <td>0.42</td>
      <td>0.39</td>
      <td>0.34</td>
      <td>0.32</td>
      <td>0.31</td>
    </tr>
    <tr>
      <th>90</th>
      <td>0.98</td>
      <td>0.96</td>
      <td>0.92</td>
      <td>0.88</td>
      <td>0.85</td>
      <td>0.81</td>
      <td>0.80</td>
      <td>0.70</td>
      <td>0.68</td>
      <td>0.60</td>
      <td>0.58</td>
      <td>0.56</td>
      <td>0.54</td>
      <td>0.50</td>
      <td>0.45</td>
      <td>0.43</td>
      <td>0.40</td>
      <td>0.36</td>
      <td>0.33</td>
      <td>0.32</td>
    </tr>
    <tr>
      <th>95</th>
      <td>0.98</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>0.88</td>
      <td>0.85</td>
      <td>0.82</td>
      <td>0.81</td>
      <td>0.71</td>
      <td>0.69</td>
      <td>0.61</td>
      <td>0.59</td>
      <td>0.57</td>
      <td>0.55</td>
      <td>0.51</td>
      <td>0.46</td>
      <td>0.44</td>
      <td>0.41</td>
      <td>0.37</td>
      <td>0.35</td>
      <td>0.33</td>
    </tr>
    <tr>
      <th>100</th>
      <td>0.98</td>
      <td>0.97</td>
      <td>0.93</td>
      <td>0.89</td>
      <td>0.86</td>
      <td>0.83</td>
      <td>0.82</td>
      <td>0.72</td>
      <td>0.69</td>
      <td>0.62</td>
      <td>0.60</td>
      <td>0.58</td>
      <td>0.56</td>
      <td>0.52</td>
      <td>0.47</td>
      <td>0.45</td>
      <td>0.42</td>
      <td>0.38</td>
      <td>0.36</td>
      <td>0.34</td>
    </tr>
  </tbody>
</table>
</div>



```python
import pandas as pd
import numpy as np

def conditional_hit_probabilities(
    df: pd.DataFrame,
    today_high: float,
    high_col: str,
    thresholds,
    horizons,
    tolerance: float,  # how close history must be to today's high
) -> pd.DataFrame:
    
    """
    Conditional probability of hitting thresholds within horizons,
    given today's high is near `today_high`.

    Parameters
    ----------
    df : pd.DataFrame
        Daily data with highs.
    today_high : float
        Today's observed high.
    high_col : str
        Column containing the daily highs.
    thresholds : list of floats
        Target levels to evaluate (e.g., [18,19,20,...]).
    horizons : list of ints
        Lookahead windows (in trading days).
    tolerance : float
        Acceptable deviation from today's high when finding historical analogues.

    Returns
    -------
    pd.DataFrame
        Probabilities indexed by horizon (rows) and thresholds (columns).
    """
    
    df = df.sort_index()
    highs = df[high_col].values
    n = len(highs)

    # Find indices where the high ~ today's high
    candidates = np.where((highs >= today_high - tolerance) & (highs <= today_high + tolerance))[0]
    if len(candidates) == 0:
        raise ValueError("No historical days found within tolerance of today's high")

    probs = pd.DataFrame(index=horizons, columns=thresholds, dtype=float)

    for h in horizons:
        valid_hits = 0
        total = 0
        for i in candidates:
            if i + h < n:  # need full window
                window_max = highs[i+1:i+h+1].max()  # strictly future days
                for thr in thresholds:
                    if np.isnan(probs.loc[h, thr]):
                        probs.loc[h, thr] = 0.0
                    if window_max >= thr:
                        probs.loc[h, thr] += 1
                total += 1
        if total > 0:
            probs.loc[h] /= total  # normalize to probability
        else:
            probs.loc[h] = np.nan  # no valid examples

    return probs

```


```python
# Get yesterday's high as an example
yesterday = vix.iloc[-2]
yesterday_high = vix['High'].iloc[-2]

display(yesterday)
display(yesterday_high)

cond_probs = conditional_hit_probabilities(
    df=vix,
    today_high=yesterday_high,
    high_col="High",
    thresholds=range(15, 31),
    horizons=range(5, 71, 5),
    tolerance=0.25
)

display(cond_probs)
```


    Close   24.06
    High    27.52
    Low     23.54
    Open    25.60
    Name: 2026-03-19 00:00:00, dtype: float64



    np.float64(27.52000045776367)



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
      <th>15</th>
      <th>16</th>
      <th>17</th>
      <th>18</th>
      <th>19</th>
      <th>20</th>
      <th>21</th>
      <th>22</th>
      <th>23</th>
      <th>24</th>
      <th>25</th>
      <th>26</th>
      <th>27</th>
      <th>28</th>
      <th>29</th>
      <th>30</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>5</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.98</td>
      <td>0.94</td>
      <td>0.84</td>
      <td>0.75</td>
      <td>0.60</td>
      <td>0.46</td>
      <td>0.41</td>
    </tr>
    <tr>
      <th>10</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.99</td>
      <td>0.95</td>
      <td>0.86</td>
      <td>0.81</td>
      <td>0.70</td>
      <td>0.56</td>
      <td>0.50</td>
    </tr>
    <tr>
      <th>15</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.96</td>
      <td>0.89</td>
      <td>0.82</td>
      <td>0.74</td>
      <td>0.61</td>
      <td>0.55</td>
    </tr>
    <tr>
      <th>20</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.96</td>
      <td>0.89</td>
      <td>0.82</td>
      <td>0.76</td>
      <td>0.62</td>
      <td>0.56</td>
    </tr>
    <tr>
      <th>25</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.91</td>
      <td>0.86</td>
      <td>0.79</td>
      <td>0.64</td>
      <td>0.57</td>
    </tr>
    <tr>
      <th>30</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.93</td>
      <td>0.89</td>
      <td>0.81</td>
      <td>0.66</td>
      <td>0.60</td>
    </tr>
    <tr>
      <th>35</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.85</td>
      <td>0.70</td>
      <td>0.62</td>
    </tr>
    <tr>
      <th>40</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.86</td>
      <td>0.76</td>
      <td>0.65</td>
    </tr>
    <tr>
      <th>45</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.86</td>
      <td>0.78</td>
      <td>0.68</td>
    </tr>
    <tr>
      <th>50</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.94</td>
      <td>0.90</td>
      <td>0.86</td>
      <td>0.78</td>
      <td>0.70</td>
    </tr>
    <tr>
      <th>55</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.94</td>
      <td>0.91</td>
      <td>0.88</td>
      <td>0.78</td>
      <td>0.70</td>
    </tr>
    <tr>
      <th>60</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.94</td>
      <td>0.91</td>
      <td>0.88</td>
      <td>0.78</td>
      <td>0.70</td>
    </tr>
    <tr>
      <th>65</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.94</td>
      <td>0.91</td>
      <td>0.88</td>
      <td>0.79</td>
      <td>0.70</td>
    </tr>
    <tr>
      <th>70</th>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>0.99</td>
      <td>0.94</td>
      <td>0.93</td>
      <td>0.89</td>
      <td>0.80</td>
      <td>0.71</td>
    </tr>
  </tbody>
</table>
</div>


## Plots - VIX

### Histogram Distribution - VIX


```python
# Plotting
plt.figure(figsize=(10, 6))

# Histogram
plt.hist([vix['High']], label=['High'], bins=200, edgecolor='black', color='steelblue', alpha=0.7)
plt.hist([vix['Low']], label=['Low'], bins=200, edgecolor='black', color='lightblue', alpha=0.7)

# Plot a vertical line at the mean, mean + 1 std, and mean + 2 std
plt.axvline(vix_stats.loc['mean + -1 std']['High'], color='brown', linestyle='dashed', linewidth=1, label=f'High Mean - 1 std: {vix_stats.loc['mean + -1 std']['High']:.2f}')
plt.axvline(vix_stats.loc['mean + -1 std']['Low'], color='brown', linestyle='solid', linewidth=1, label=f'Low Mean - 1 std: {vix_stats.loc['mean + -1 std']['Low']:.2f}')

plt.axvline(vix_stats.loc['mean']['High'], color='red', linestyle='dashed', linewidth=1, label=f'High Mean: {vix_stats.loc['mean']['High']:.2f}')
plt.axvline(vix_stats.loc['mean']['Low'], color='red', linestyle='solid', linewidth=1, label=f'Low Mean: {vix_stats.loc['mean']['Low']:.2f}')

plt.axvline(vix_stats.loc['mean + 1 std']['High'], color='green', linestyle='dashed', linewidth=1, label=f'High Mean + 1 std: {vix_stats.loc['mean + 1 std']['High']:.2f}')
plt.axvline(vix_stats.loc['mean + 1 std']['Low'], color='green', linestyle='solid', linewidth=1, label=f'Low Mean + 1 std: {vix_stats.loc['mean + 1 std']['Low']:.2f}')

plt.axvline(vix_stats.loc['mean + 2 std']['High'], color='orange', linestyle='dashed', linewidth=1, label=f'High Mean + 2 std: {vix_stats.loc['mean + 2 std']['High']:.2f}')
plt.axvline(vix_stats.loc['mean + 2 std']['Low'], color='orange', linestyle='solid', linewidth=1, label=f'Low Mean + 2 std: {vix_stats.loc['mean + 2 std']['Low']:.2f}')

plt.axvline(vix_stats.loc['mean + 3 std']['High'], color='black', linestyle='dashed', linewidth=1, label=f'High Mean + 3 std: {vix_stats.loc['mean + 3 std']['High']:.2f}')
plt.axvline(vix_stats.loc['mean + 3 std']['Low'], color='black', linestyle='solid', linewidth=1, label=f'Low Mean + 3 std: {vix_stats.loc['mean + 3 std']['Low']:.2f}')

plt.axvline(vix_stats.loc['mean + 4 std']['High'], color='yellow', linestyle='dashed', linewidth=1, label=f'High Mean + 4 std: {vix_stats.loc['mean + 4 std']['High']:.2f}')
plt.axvline(vix_stats.loc['mean + 4 std']['Low'], color='yellow', linestyle='solid', linewidth=1, label=f'Low Mean + 4 std: {vix_stats.loc['mean + 4 std']['Low']:.2f}')

# Set X axis
x_tick_spacing = 5  # Specify the interval for y-axis ticks
plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
plt.xlabel("VIX")
plt.xticks(rotation=30)

# Set Y axis
y_tick_spacing = 25  # Specify the interval for y-axis ticks
plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
plt.ylabel("# Of Datapoints")
plt.yticks()

# Set title, layout, grid, and legend
plt.title("CBOE Volatility Index (VIX) Histogram (200 Bins)", fontsize=12)
plt.tight_layout()
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Save figure and display plot
plt.savefig("01_Histogram+Mean+SD.png", dpi=300, bbox_inches="tight")
plt.show()
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_44_0.png)
    


### Historical Data - VIX


```python
plot_time_series(
    df=vix,
    plot_start_date=None,
    plot_end_date="2009-12-31",
    plot_columns=["High", "Low"],
    title="CBOE Volatility Index (VIX), 1990 - 2009",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=5,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="01_VIX_Plot_1990-2009",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_46_0.png)
    



```python
plot_time_series(
    df=vix,
    plot_start_date="2010-01-01",
    plot_end_date=None,
    plot_columns=["High", "Low"],
    title="CBOE Volatility Index (VIX), 2010 - Present",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=5,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="01_VIX_Plot_2010-Present",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_47_0.png)
    



```python
plot_time_series(
    df=vix,
    plot_start_date="2024-01-01",
    plot_end_date=None,
    plot_columns=["High", "Low"],
    title="CBOE Volatility Index (VIX), 2024 - Present",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=5,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="01_VIX_Plot_2024-Present",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_48_0.png)
    



```python
plot_time_series(
    df=vix,
    plot_start_date="2025-01-01",
    plot_end_date=None,
    plot_columns=["High", "Low"],
    title="CBOE Volatility Index (VIX), 2025 - Present",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=5,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="01_VIX_Plot_2025-Present",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_49_0.png)
    


### Stats By Year - VIX


```python
plot_stats(
    stats_df=vix_stats_by_year,
    plot_columns=["Open_mean", "High_mean", "Low_mean", "Close_mean"],
    title="VIX Mean OHLC By Year",
    x_label="Year",
    x_rotation=30,
    x_tick_spacing=2,
    y_label="Price",
    y_tick_spacing=2,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="01_VIX_Stats_By_Year"
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_51_0.png)
    


### Stats By Month - VIX


```python
plot_stats(
    stats_df=vix_stats_by_month,
    plot_columns=["Open_mean", "High_mean", "Low_mean", "Close_mean"],
    title="VIX Mean OHLC By Month",
    x_label="Month",
    x_rotation=0,
    x_tick_spacing=1,
    y_label="Price",
    y_tick_spacing=1,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="01_VIX_Stats_By_Month"
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_53_0.png)
    


## Data Overview - VVIX

### Acquire CBOE VVIX Data


```python
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="^VVIX",
    adjusted=True,
    source="Yahoo_Finance", 
    asset_class="Indices", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)
```

    The first and last date of data for ^VVIX is: 



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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2007-01-03</th>
      <td>87.63</td>
      <td>87.63</td>
      <td>87.63</td>
      <td>87.63</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2026-03-20</th>
      <td>126.28</td>
      <td>131.93</td>
      <td>118.88</td>
      <td>119.02</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>


    Yahoo Finance data complete for ^VVIX
    --------------------





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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2007-01-03</th>
      <td>87.63</td>
      <td>87.63</td>
      <td>87.63</td>
      <td>87.63</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2007-01-04</th>
      <td>88.19</td>
      <td>88.19</td>
      <td>88.19</td>
      <td>88.19</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2007-01-05</th>
      <td>90.17</td>
      <td>90.17</td>
      <td>90.17</td>
      <td>90.17</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2007-01-08</th>
      <td>92.04</td>
      <td>92.04</td>
      <td>92.04</td>
      <td>92.04</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2007-01-09</th>
      <td>92.76</td>
      <td>92.76</td>
      <td>92.76</td>
      <td>92.76</td>
      <td>0</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2026-03-16</th>
      <td>116.78</td>
      <td>125.80</td>
      <td>116.71</td>
      <td>125.42</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2026-03-17</th>
      <td>110.55</td>
      <td>115.03</td>
      <td>108.33</td>
      <td>115.03</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2026-03-18</th>
      <td>126.50</td>
      <td>126.55</td>
      <td>113.96</td>
      <td>114.82</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2026-03-19</th>
      <td>118.09</td>
      <td>134.26</td>
      <td>116.63</td>
      <td>134.00</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2026-03-20</th>
      <td>126.28</td>
      <td>131.93</td>
      <td>118.88</td>
      <td>119.02</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>4825 rows × 5 columns</p>
</div>



### Load Data - VVIX


```python
# Set decimal places
pandas_set_decimal_places(2)

# VVIX
vvix = load_data(
    base_directory=DATA_DIR,
    ticker="^VVIX",
    source="Yahoo_Finance", 
    asset_class="Indices",
    timeframe="Daily",
    file_format="excel",
)

# Set 'Date' column as datetime
vvix['Date'] = pd.to_datetime(vvix['Date'])

# Drop 'Volume'
vvix.drop(columns = {'Volume'}, inplace = True)

# Set Date as index
vvix.set_index('Date', inplace = True)

# Check to see if there are any NaN values
vvix[vvix['High'].isna()]

# Forward fill to clean up missing data
vvix['High'] = vvix['High'].ffill()
```

### DataFrame Info - VVIX


```python
df_info(vvix)
```

    The columns, shape, and data types are:
    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 4825 entries, 2007-01-03 to 2026-03-20
    Data columns (total 4 columns):
     #   Column  Non-Null Count  Dtype  
    ---  ------  --------------  -----  
     0   Close   4825 non-null   float64
     1   High    4825 non-null   float64
     2   Low     4825 non-null   float64
     3   Open    4825 non-null   float64
    dtypes: float64(4)
    memory usage: 188.5 KB
    None
    The first 5 rows are:



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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
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
      <th>2007-01-03</th>
      <td>87.63</td>
      <td>87.63</td>
      <td>87.63</td>
      <td>87.63</td>
    </tr>
    <tr>
      <th>2007-01-04</th>
      <td>88.19</td>
      <td>88.19</td>
      <td>88.19</td>
      <td>88.19</td>
    </tr>
    <tr>
      <th>2007-01-05</th>
      <td>90.17</td>
      <td>90.17</td>
      <td>90.17</td>
      <td>90.17</td>
    </tr>
    <tr>
      <th>2007-01-08</th>
      <td>92.04</td>
      <td>92.04</td>
      <td>92.04</td>
      <td>92.04</td>
    </tr>
    <tr>
      <th>2007-01-09</th>
      <td>92.76</td>
      <td>92.76</td>
      <td>92.76</td>
      <td>92.76</td>
    </tr>
  </tbody>
</table>
</div>


    The last 5 rows are:



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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
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
      <th>2026-03-16</th>
      <td>116.78</td>
      <td>125.80</td>
      <td>116.71</td>
      <td>125.42</td>
    </tr>
    <tr>
      <th>2026-03-17</th>
      <td>110.55</td>
      <td>115.03</td>
      <td>108.33</td>
      <td>115.03</td>
    </tr>
    <tr>
      <th>2026-03-18</th>
      <td>126.50</td>
      <td>126.55</td>
      <td>113.96</td>
      <td>114.82</td>
    </tr>
    <tr>
      <th>2026-03-19</th>
      <td>118.09</td>
      <td>134.26</td>
      <td>116.63</td>
      <td>134.00</td>
    </tr>
    <tr>
      <th>2026-03-20</th>
      <td>126.28</td>
      <td>131.93</td>
      <td>118.88</td>
      <td>119.02</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_02_VVIX_DF_Info_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="02_VVIX_DF_Info.md", 
    content=df_info_markdown(vix),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 02_VVIX_DF_Info.md


### Statistics - VVIX


```python
vvix_stats = vvix.describe()
num_std = [-1, 0, 1, 2, 3, 4, 5]
for num in num_std:
    vvix_stats.loc[f"mean + {num} std"] = {
        'Open': vvix_stats.loc['mean']['Open'] + num * vvix_stats.loc['std']['Open'],
        'High': vvix_stats.loc['mean']['High'] + num * vvix_stats.loc['std']['High'],
        'Low': vvix_stats.loc['mean']['Low'] + num * vvix_stats.loc['std']['Low'],
        'Close': vvix_stats.loc['mean']['Close'] + num * vvix_stats.loc['std']['Close'],
    }
display(vvix_stats)
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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>4825.00</td>
      <td>4825.00</td>
      <td>4825.00</td>
      <td>4825.00</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>93.81</td>
      <td>95.93</td>
      <td>92.20</td>
      <td>94.07</td>
    </tr>
    <tr>
      <th>std</th>
      <td>16.31</td>
      <td>17.95</td>
      <td>14.94</td>
      <td>16.36</td>
    </tr>
    <tr>
      <th>min</th>
      <td>59.74</td>
      <td>59.74</td>
      <td>59.31</td>
      <td>59.31</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>82.65</td>
      <td>83.88</td>
      <td>81.72</td>
      <td>82.90</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>91.07</td>
      <td>92.84</td>
      <td>89.88</td>
      <td>91.42</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>102.49</td>
      <td>105.46</td>
      <td>100.26</td>
      <td>102.86</td>
    </tr>
    <tr>
      <th>max</th>
      <td>207.59</td>
      <td>212.22</td>
      <td>187.27</td>
      <td>212.22</td>
    </tr>
    <tr>
      <th>mean + -1 std</th>
      <td>77.50</td>
      <td>77.99</td>
      <td>77.26</td>
      <td>77.70</td>
    </tr>
    <tr>
      <th>mean + 0 std</th>
      <td>93.81</td>
      <td>95.93</td>
      <td>92.20</td>
      <td>94.07</td>
    </tr>
    <tr>
      <th>mean + 1 std</th>
      <td>110.11</td>
      <td>113.88</td>
      <td>107.14</td>
      <td>110.43</td>
    </tr>
    <tr>
      <th>mean + 2 std</th>
      <td>126.42</td>
      <td>131.83</td>
      <td>122.08</td>
      <td>126.79</td>
    </tr>
    <tr>
      <th>mean + 3 std</th>
      <td>142.72</td>
      <td>149.77</td>
      <td>137.01</td>
      <td>143.16</td>
    </tr>
    <tr>
      <th>mean + 4 std</th>
      <td>159.03</td>
      <td>167.72</td>
      <td>151.95</td>
      <td>159.52</td>
    </tr>
    <tr>
      <th>mean + 5 std</th>
      <td>175.33</td>
      <td>185.66</td>
      <td>166.89</td>
      <td>175.89</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_02_VVIX_Stats_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="02_VVIX_Stats.md", 
    content=vvix_stats.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 02_VVIX_Stats.md



```python
# Group by year and calculate mean and std for OHLC
vvix_stats_by_year = vvix.groupby(vvix.index.year)[["Open", "High", "Low", "Close"]].agg(["mean", "std", "min", "max"])

# Flatten the column MultiIndex
vvix_stats_by_year.columns = ['_'.join(col).strip() for col in vvix_stats_by_year.columns.values]
vvix_stats_by_year.index.name = "Year"

display(vvix_stats_by_year)
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
      <th>Open_mean</th>
      <th>Open_std</th>
      <th>Open_min</th>
      <th>Open_max</th>
      <th>High_mean</th>
      <th>High_std</th>
      <th>High_min</th>
      <th>High_max</th>
      <th>Low_mean</th>
      <th>Low_std</th>
      <th>Low_min</th>
      <th>Low_max</th>
      <th>Close_mean</th>
      <th>Close_std</th>
      <th>Close_min</th>
      <th>Close_max</th>
    </tr>
    <tr>
      <th>Year</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
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
      <th>2007</th>
      <td>87.68</td>
      <td>13.31</td>
      <td>63.52</td>
      <td>142.99</td>
      <td>87.68</td>
      <td>13.31</td>
      <td>63.52</td>
      <td>142.99</td>
      <td>87.68</td>
      <td>13.31</td>
      <td>63.52</td>
      <td>142.99</td>
      <td>87.68</td>
      <td>13.31</td>
      <td>63.52</td>
      <td>142.99</td>
    </tr>
    <tr>
      <th>2008</th>
      <td>81.85</td>
      <td>15.60</td>
      <td>59.74</td>
      <td>134.87</td>
      <td>81.85</td>
      <td>15.60</td>
      <td>59.74</td>
      <td>134.87</td>
      <td>81.85</td>
      <td>15.60</td>
      <td>59.74</td>
      <td>134.87</td>
      <td>81.85</td>
      <td>15.60</td>
      <td>59.74</td>
      <td>134.87</td>
    </tr>
    <tr>
      <th>2009</th>
      <td>79.78</td>
      <td>8.63</td>
      <td>64.95</td>
      <td>104.02</td>
      <td>79.78</td>
      <td>8.63</td>
      <td>64.95</td>
      <td>104.02</td>
      <td>79.78</td>
      <td>8.63</td>
      <td>64.95</td>
      <td>104.02</td>
      <td>79.78</td>
      <td>8.63</td>
      <td>64.95</td>
      <td>104.02</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>88.36</td>
      <td>13.07</td>
      <td>64.87</td>
      <td>145.12</td>
      <td>88.36</td>
      <td>13.07</td>
      <td>64.87</td>
      <td>145.12</td>
      <td>88.36</td>
      <td>13.07</td>
      <td>64.87</td>
      <td>145.12</td>
      <td>88.36</td>
      <td>13.07</td>
      <td>64.87</td>
      <td>145.12</td>
    </tr>
    <tr>
      <th>2011</th>
      <td>92.94</td>
      <td>10.21</td>
      <td>75.94</td>
      <td>134.63</td>
      <td>92.94</td>
      <td>10.21</td>
      <td>75.94</td>
      <td>134.63</td>
      <td>92.94</td>
      <td>10.21</td>
      <td>75.94</td>
      <td>134.63</td>
      <td>92.94</td>
      <td>10.21</td>
      <td>75.94</td>
      <td>134.63</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>94.84</td>
      <td>8.38</td>
      <td>78.42</td>
      <td>117.44</td>
      <td>94.84</td>
      <td>8.38</td>
      <td>78.42</td>
      <td>117.44</td>
      <td>94.84</td>
      <td>8.38</td>
      <td>78.42</td>
      <td>117.44</td>
      <td>94.84</td>
      <td>8.38</td>
      <td>78.42</td>
      <td>117.44</td>
    </tr>
    <tr>
      <th>2013</th>
      <td>80.52</td>
      <td>8.97</td>
      <td>62.71</td>
      <td>111.43</td>
      <td>80.52</td>
      <td>8.97</td>
      <td>62.71</td>
      <td>111.43</td>
      <td>80.52</td>
      <td>8.97</td>
      <td>62.71</td>
      <td>111.43</td>
      <td>80.52</td>
      <td>8.97</td>
      <td>62.71</td>
      <td>111.43</td>
    </tr>
    <tr>
      <th>2014</th>
      <td>83.01</td>
      <td>14.33</td>
      <td>61.76</td>
      <td>138.60</td>
      <td>83.01</td>
      <td>14.33</td>
      <td>61.76</td>
      <td>138.60</td>
      <td>83.01</td>
      <td>14.33</td>
      <td>61.76</td>
      <td>138.60</td>
      <td>83.01</td>
      <td>14.33</td>
      <td>61.76</td>
      <td>138.60</td>
    </tr>
    <tr>
      <th>2015</th>
      <td>95.44</td>
      <td>15.59</td>
      <td>73.07</td>
      <td>212.22</td>
      <td>98.47</td>
      <td>16.39</td>
      <td>76.41</td>
      <td>212.22</td>
      <td>92.15</td>
      <td>13.35</td>
      <td>72.20</td>
      <td>148.68</td>
      <td>94.82</td>
      <td>14.75</td>
      <td>73.18</td>
      <td>168.75</td>
    </tr>
    <tr>
      <th>2016</th>
      <td>93.36</td>
      <td>10.02</td>
      <td>77.96</td>
      <td>131.95</td>
      <td>95.82</td>
      <td>10.86</td>
      <td>78.86</td>
      <td>132.42</td>
      <td>90.54</td>
      <td>8.99</td>
      <td>76.17</td>
      <td>115.15</td>
      <td>92.80</td>
      <td>10.07</td>
      <td>76.17</td>
      <td>125.13</td>
    </tr>
    <tr>
      <th>2017</th>
      <td>90.50</td>
      <td>8.65</td>
      <td>75.09</td>
      <td>134.98</td>
      <td>92.94</td>
      <td>9.64</td>
      <td>77.34</td>
      <td>135.32</td>
      <td>87.85</td>
      <td>7.78</td>
      <td>71.75</td>
      <td>117.29</td>
      <td>90.01</td>
      <td>8.80</td>
      <td>75.64</td>
      <td>135.32</td>
    </tr>
    <tr>
      <th>2018</th>
      <td>102.60</td>
      <td>13.22</td>
      <td>83.70</td>
      <td>176.72</td>
      <td>106.27</td>
      <td>16.26</td>
      <td>85.00</td>
      <td>203.73</td>
      <td>99.17</td>
      <td>11.31</td>
      <td>82.60</td>
      <td>165.35</td>
      <td>102.26</td>
      <td>14.04</td>
      <td>83.21</td>
      <td>180.61</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>91.28</td>
      <td>8.43</td>
      <td>75.58</td>
      <td>112.75</td>
      <td>93.61</td>
      <td>8.98</td>
      <td>75.95</td>
      <td>117.63</td>
      <td>88.90</td>
      <td>7.86</td>
      <td>74.36</td>
      <td>111.48</td>
      <td>91.03</td>
      <td>8.36</td>
      <td>74.98</td>
      <td>114.40</td>
    </tr>
    <tr>
      <th>2020</th>
      <td>118.64</td>
      <td>19.32</td>
      <td>88.39</td>
      <td>203.03</td>
      <td>121.91</td>
      <td>20.88</td>
      <td>88.54</td>
      <td>209.76</td>
      <td>115.05</td>
      <td>17.37</td>
      <td>85.31</td>
      <td>187.27</td>
      <td>118.36</td>
      <td>19.39</td>
      <td>86.87</td>
      <td>207.59</td>
    </tr>
    <tr>
      <th>2021</th>
      <td>115.51</td>
      <td>9.37</td>
      <td>96.09</td>
      <td>151.35</td>
      <td>119.29</td>
      <td>11.70</td>
      <td>98.36</td>
      <td>168.78</td>
      <td>111.99</td>
      <td>8.14</td>
      <td>95.92</td>
      <td>144.19</td>
      <td>115.32</td>
      <td>10.20</td>
      <td>97.09</td>
      <td>157.69</td>
    </tr>
    <tr>
      <th>2022</th>
      <td>102.58</td>
      <td>18.01</td>
      <td>76.48</td>
      <td>161.09</td>
      <td>105.32</td>
      <td>19.16</td>
      <td>77.93</td>
      <td>172.82</td>
      <td>99.17</td>
      <td>16.81</td>
      <td>76.13</td>
      <td>153.26</td>
      <td>101.81</td>
      <td>17.81</td>
      <td>77.05</td>
      <td>154.38</td>
    </tr>
    <tr>
      <th>2023</th>
      <td>90.95</td>
      <td>8.64</td>
      <td>74.43</td>
      <td>127.73</td>
      <td>93.72</td>
      <td>9.98</td>
      <td>75.31</td>
      <td>137.65</td>
      <td>88.01</td>
      <td>7.37</td>
      <td>72.27</td>
      <td>119.64</td>
      <td>90.34</td>
      <td>8.38</td>
      <td>73.88</td>
      <td>124.75</td>
    </tr>
    <tr>
      <th>2024</th>
      <td>92.88</td>
      <td>15.06</td>
      <td>59.31</td>
      <td>169.68</td>
      <td>97.32</td>
      <td>18.33</td>
      <td>74.79</td>
      <td>192.49</td>
      <td>89.51</td>
      <td>13.16</td>
      <td>59.31</td>
      <td>137.05</td>
      <td>92.81</td>
      <td>15.60</td>
      <td>73.26</td>
      <td>173.32</td>
    </tr>
    <tr>
      <th>2025</th>
      <td>101.94</td>
      <td>12.83</td>
      <td>83.19</td>
      <td>186.33</td>
      <td>106.13</td>
      <td>15.40</td>
      <td>84.54</td>
      <td>189.03</td>
      <td>98.38</td>
      <td>10.11</td>
      <td>81.72</td>
      <td>146.51</td>
      <td>101.32</td>
      <td>12.36</td>
      <td>81.89</td>
      <td>170.92</td>
    </tr>
    <tr>
      <th>2026</th>
      <td>108.88</td>
      <td>11.83</td>
      <td>89.81</td>
      <td>137.07</td>
      <td>112.72</td>
      <td>12.64</td>
      <td>90.43</td>
      <td>140.99</td>
      <td>104.40</td>
      <td>9.52</td>
      <td>86.70</td>
      <td>125.01</td>
      <td>107.94</td>
      <td>11.70</td>
      <td>88.19</td>
      <td>140.44</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_02_VVIX_Stats_By_Year_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="02_VVIX_Stats_By_Year.md", 
    content=vvix_stats_by_year.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 02_VVIX_Stats_By_Year.md



```python
# Group by month and calculate mean and std for OHLC
vvix_stats_by_month = vvix.groupby(vvix.index.month)[["Open", "High", "Low", "Close"]].agg(["mean", "std", "min", "max"])

# Flatten the column MultiIndex
vvix_stats_by_month.columns = ['_'.join(col).strip() for col in vvix_stats_by_month.columns.values]
vvix_stats_by_month.index.name = "Year"

display(vvix_stats_by_month)
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
      <th>Open_mean</th>
      <th>Open_std</th>
      <th>Open_min</th>
      <th>Open_max</th>
      <th>High_mean</th>
      <th>High_std</th>
      <th>High_min</th>
      <th>High_max</th>
      <th>Low_mean</th>
      <th>Low_std</th>
      <th>Low_min</th>
      <th>Low_max</th>
      <th>Close_mean</th>
      <th>Close_std</th>
      <th>Close_min</th>
      <th>Close_max</th>
    </tr>
    <tr>
      <th>Year</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
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
      <th>1</th>
      <td>92.79</td>
      <td>15.40</td>
      <td>64.87</td>
      <td>161.09</td>
      <td>94.74</td>
      <td>17.36</td>
      <td>64.87</td>
      <td>172.82</td>
      <td>90.96</td>
      <td>13.99</td>
      <td>64.87</td>
      <td>153.26</td>
      <td>92.54</td>
      <td>15.52</td>
      <td>64.87</td>
      <td>157.69</td>
    </tr>
    <tr>
      <th>2</th>
      <td>94.21</td>
      <td>18.11</td>
      <td>65.47</td>
      <td>176.72</td>
      <td>96.22</td>
      <td>20.53</td>
      <td>65.47</td>
      <td>203.73</td>
      <td>92.02</td>
      <td>16.28</td>
      <td>65.47</td>
      <td>165.35</td>
      <td>93.82</td>
      <td>18.41</td>
      <td>65.47</td>
      <td>180.61</td>
    </tr>
    <tr>
      <th>3</th>
      <td>96.27</td>
      <td>21.92</td>
      <td>66.97</td>
      <td>203.03</td>
      <td>98.45</td>
      <td>23.86</td>
      <td>66.97</td>
      <td>209.76</td>
      <td>93.74</td>
      <td>19.65</td>
      <td>66.97</td>
      <td>187.27</td>
      <td>95.82</td>
      <td>21.82</td>
      <td>66.97</td>
      <td>207.59</td>
    </tr>
    <tr>
      <th>4</th>
      <td>92.18</td>
      <td>19.03</td>
      <td>59.74</td>
      <td>186.33</td>
      <td>94.01</td>
      <td>20.57</td>
      <td>59.74</td>
      <td>189.03</td>
      <td>90.30</td>
      <td>17.21</td>
      <td>59.74</td>
      <td>152.01</td>
      <td>91.88</td>
      <td>18.60</td>
      <td>59.74</td>
      <td>170.92</td>
    </tr>
    <tr>
      <th>5</th>
      <td>92.25</td>
      <td>16.93</td>
      <td>61.76</td>
      <td>145.18</td>
      <td>93.95</td>
      <td>17.99</td>
      <td>61.76</td>
      <td>151.50</td>
      <td>90.54</td>
      <td>16.14</td>
      <td>61.76</td>
      <td>145.12</td>
      <td>91.79</td>
      <td>16.79</td>
      <td>61.76</td>
      <td>146.28</td>
    </tr>
    <tr>
      <th>6</th>
      <td>93.16</td>
      <td>14.86</td>
      <td>63.52</td>
      <td>155.48</td>
      <td>94.76</td>
      <td>16.11</td>
      <td>63.52</td>
      <td>172.21</td>
      <td>91.49</td>
      <td>13.79</td>
      <td>63.52</td>
      <td>140.15</td>
      <td>92.98</td>
      <td>14.83</td>
      <td>63.52</td>
      <td>151.60</td>
    </tr>
    <tr>
      <th>7</th>
      <td>90.10</td>
      <td>12.82</td>
      <td>67.21</td>
      <td>138.42</td>
      <td>91.63</td>
      <td>13.88</td>
      <td>67.21</td>
      <td>149.60</td>
      <td>88.60</td>
      <td>11.94</td>
      <td>67.21</td>
      <td>133.82</td>
      <td>89.98</td>
      <td>12.78</td>
      <td>67.21</td>
      <td>139.54</td>
    </tr>
    <tr>
      <th>8</th>
      <td>96.84</td>
      <td>16.53</td>
      <td>68.05</td>
      <td>212.22</td>
      <td>98.99</td>
      <td>18.33</td>
      <td>68.05</td>
      <td>212.22</td>
      <td>94.67</td>
      <td>14.50</td>
      <td>68.05</td>
      <td>148.68</td>
      <td>96.61</td>
      <td>16.24</td>
      <td>68.05</td>
      <td>173.32</td>
    </tr>
    <tr>
      <th>9</th>
      <td>94.91</td>
      <td>13.70</td>
      <td>67.94</td>
      <td>135.17</td>
      <td>96.84</td>
      <td>15.36</td>
      <td>67.94</td>
      <td>147.14</td>
      <td>93.04</td>
      <td>12.20</td>
      <td>67.94</td>
      <td>128.46</td>
      <td>94.58</td>
      <td>13.44</td>
      <td>67.94</td>
      <td>138.93</td>
    </tr>
    <tr>
      <th>10</th>
      <td>98.05</td>
      <td>13.86</td>
      <td>64.97</td>
      <td>149.60</td>
      <td>99.88</td>
      <td>15.05</td>
      <td>64.97</td>
      <td>154.99</td>
      <td>96.36</td>
      <td>13.11</td>
      <td>64.97</td>
      <td>144.55</td>
      <td>97.87</td>
      <td>14.02</td>
      <td>64.97</td>
      <td>152.01</td>
    </tr>
    <tr>
      <th>11</th>
      <td>94.24</td>
      <td>14.31</td>
      <td>63.77</td>
      <td>142.68</td>
      <td>95.93</td>
      <td>15.64</td>
      <td>63.77</td>
      <td>161.76</td>
      <td>92.55</td>
      <td>13.40</td>
      <td>63.77</td>
      <td>140.44</td>
      <td>93.95</td>
      <td>14.37</td>
      <td>63.77</td>
      <td>149.74</td>
    </tr>
    <tr>
      <th>12</th>
      <td>93.32</td>
      <td>14.67</td>
      <td>59.31</td>
      <td>151.35</td>
      <td>95.31</td>
      <td>16.24</td>
      <td>62.71</td>
      <td>168.37</td>
      <td>91.71</td>
      <td>13.37</td>
      <td>59.31</td>
      <td>144.19</td>
      <td>93.38</td>
      <td>14.72</td>
      <td>62.71</td>
      <td>156.10</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_02_VVIX_Stats_By_Month_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="02_VVIX_Stats_By_Month.md", 
    content=vvix_stats_by_month.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 02_VVIX_Stats_By_Month.md


### Deciles - VVIX


```python
vvix_deciles = vvix.quantile(np.arange(0, 1.1, 0.1))
display(vvix_deciles)
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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0.00</th>
      <td>59.74</td>
      <td>59.74</td>
      <td>59.31</td>
      <td>59.31</td>
    </tr>
    <tr>
      <th>0.10</th>
      <td>76.15</td>
      <td>76.43</td>
      <td>75.61</td>
      <td>76.17</td>
    </tr>
    <tr>
      <th>0.20</th>
      <td>80.88</td>
      <td>81.72</td>
      <td>80.10</td>
      <td>81.04</td>
    </tr>
    <tr>
      <th>0.30</th>
      <td>84.30</td>
      <td>85.64</td>
      <td>83.39</td>
      <td>84.58</td>
    </tr>
    <tr>
      <th>0.40</th>
      <td>87.62</td>
      <td>89.08</td>
      <td>86.49</td>
      <td>87.91</td>
    </tr>
    <tr>
      <th>0.50</th>
      <td>91.07</td>
      <td>92.84</td>
      <td>89.88</td>
      <td>91.42</td>
    </tr>
    <tr>
      <th>0.60</th>
      <td>94.75</td>
      <td>97.00</td>
      <td>93.45</td>
      <td>94.97</td>
    </tr>
    <tr>
      <th>0.70</th>
      <td>99.48</td>
      <td>102.01</td>
      <td>97.75</td>
      <td>99.68</td>
    </tr>
    <tr>
      <th>0.80</th>
      <td>106.12</td>
      <td>109.73</td>
      <td>103.96</td>
      <td>106.58</td>
    </tr>
    <tr>
      <th>0.90</th>
      <td>115.47</td>
      <td>118.88</td>
      <td>112.39</td>
      <td>115.57</td>
    </tr>
    <tr>
      <th>1.00</th>
      <td>207.59</td>
      <td>212.22</td>
      <td>187.27</td>
      <td>212.22</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_02_VVIX_Deciles_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="02_VVIX_Deciles.md", 
    content=vvix_deciles.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 02_VVIX_Deciles.md


## Plots - VVIX

### Histogram Distribution - VVIX


```python
# Plotting
plt.figure(figsize=(10, 6))

# Histogram
plt.hist([vvix['High']], label=['High'], bins=200, edgecolor='black', color='steelblue', alpha=0.7)
plt.hist([vvix['Low']], label=['Low'], bins=200, edgecolor='black', color='lightblue', alpha=0.7)

# Plot a vertical line at the mean, mean + 1 std, and mean + 2 std
plt.axvline(vvix_stats.loc['mean + -1 std']['High'], color='brown', linestyle='dashed', linewidth=1, label=f'High Mean - 1 std: {vvix_stats.loc['mean + -1 std']['High']:.2f}')
plt.axvline(vvix_stats.loc['mean + -1 std']['Low'], color='brown', linestyle='solid', linewidth=1, label=f'Low Mean - 1 std: {vvix_stats.loc['mean + -1 std']['Low']:.2f}')

plt.axvline(vvix_stats.loc['mean']['High'], color='red', linestyle='dashed', linewidth=1, label=f'High Mean: {vvix_stats.loc['mean']['High']:.2f}')
plt.axvline(vvix_stats.loc['mean']['Low'], color='red', linestyle='solid', linewidth=1, label=f'Low Mean: {vvix_stats.loc['mean']['Low']:.2f}')

plt.axvline(vvix_stats.loc['mean + 1 std']['High'], color='green', linestyle='dashed', linewidth=1, label=f'High Mean + 1 std: {vvix_stats.loc['mean + 1 std']['High']:.2f}')
plt.axvline(vvix_stats.loc['mean + 1 std']['Low'], color='green', linestyle='solid', linewidth=1, label=f'Low Mean + 1 std: {vvix_stats.loc['mean + 1 std']['Low']:.2f}')

plt.axvline(vvix_stats.loc['mean + 2 std']['High'], color='orange', linestyle='dashed', linewidth=1, label=f'High Mean + 2 std: {vvix_stats.loc['mean + 2 std']['High']:.2f}')
plt.axvline(vvix_stats.loc['mean + 2 std']['Low'], color='orange', linestyle='solid', linewidth=1, label=f'Low Mean + 2 std: {vvix_stats.loc['mean + 2 std']['Low']:.2f}')

plt.axvline(vvix_stats.loc['mean + 3 std']['High'], color='black', linestyle='dashed', linewidth=1, label=f'High Mean + 3 std: {vvix_stats.loc['mean + 3 std']['High']:.2f}')
plt.axvline(vvix_stats.loc['mean + 3 std']['Low'], color='black', linestyle='solid', linewidth=1, label=f'Low Mean + 3 std: {vvix_stats.loc['mean + 3 std']['Low']:.2f}')

plt.axvline(vvix_stats.loc['mean + 4 std']['High'], color='yellow', linestyle='dashed', linewidth=1, label=f'High Mean + 4 std: {vvix_stats.loc['mean + 4 std']['High']:.2f}')
plt.axvline(vvix_stats.loc['mean + 4 std']['Low'], color='yellow', linestyle='solid', linewidth=1, label=f'Low Mean + 4 std: {vvix_stats.loc['mean + 4 std']['Low']:.2f}')

# Set X axis
x_tick_spacing = 10  # Specify the interval for x-axis ticks
plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
plt.xlabel("VVIX")
plt.xticks(rotation=30)

# Set Y axis
y_tick_spacing = 15  # Specify the interval for y-axis ticks
plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
plt.ylabel("# Of Datapoints")
plt.yticks()

# Set title, layout, grid, and legend
plt.title("CBOE VVIX Histogram (200 Bins)")
plt.tight_layout()
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Save figure and display plot
plt.savefig("02_Histogram+Mean+SD.png", dpi=300, bbox_inches="tight")
plt.show()
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_74_0.png)
    


### Historical Data - VVIX


```python
plot_time_series(
    df=vvix,
    plot_start_date=None,
    plot_end_date="2016-12-31",
    plot_columns=["High", "Low"],
    title="CBOE VVIX, 2007 - 2016",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=15,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="02_VVIX_Plot_2007-2016",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_76_0.png)
    



```python
plot_time_series(
    df=vvix,
    plot_start_date="2017-01-01",
    plot_end_date=None,
    plot_columns=["High", "Low"],
    title="CBOE VVIX, 2017 - Present",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=15,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="02_VVIX_Plot_2017-Present",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_77_0.png)
    



```python
plot_time_series(
    df=vvix,
    plot_start_date="2024-01-01",
    plot_end_date=None,
    plot_columns=["High", "Low"],
    title="CBOE VVIX, 2024 - Present",
    x_label="Date",
    x_format="Month",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=15,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="02_VVIX_Plot_2024-Present",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_78_0.png)
    



```python
plot_time_series(
    df=vvix,
    plot_start_date="2025-01-01",
    plot_end_date=None,
    plot_columns=["High", "Low"],
    title="CBOE VVIX, 2025 - Present",
    x_label="Date",
    x_format="Month",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=15,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="02_VVIX_Plot_2025-Present",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_79_0.png)
    


### Stats By Year - VVIX


```python
plot_stats(
    stats_df=vvix_stats_by_year,
    plot_columns=["Open_mean", "High_mean", "Low_mean", "Close_mean"],
    title="VVIX Mean OHLC By Year",
    x_label="Year",
    x_rotation=45,
    x_tick_spacing=1,
    y_label="Price",
    y_tick_spacing=5,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="02_VVIX_Stats_By_Year"
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_81_0.png)
    


### Stats By Month - VVIX


```python
plot_stats(
    stats_df=vvix_stats_by_month,
    plot_columns=["Open_mean", "High_mean", "Low_mean", "Close_mean"],
    title="VVIX Mean OHLC By Month",
    x_label="Month",
    x_rotation=0,
    x_tick_spacing=1,
    y_label="Price",
    y_tick_spacing=1,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="02_VVIX_Stats_By_Month"
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_83_0.png)
    


## Data Overview - VIX/VVIX

### Merge VIX & VVIX Data


```python
# Merge VIX and VVIX dataframes on Date
vix_over_vvix = pd.merge(vix, vvix, left_index=True, right_index=True, suffixes=('_VIX', '_VVIX'))

# Calc VIX/VVIX ratios
vix_over_vvix['Close_VIX_to_VVIX_Ratio'] = vix_over_vvix['Close_VIX'] / vix_over_vvix['Close_VVIX']
vix_over_vvix['High_VIX_to_VVIX_Ratio'] = vix_over_vvix['High_VIX'] / vix_over_vvix['High_VVIX']
vix_over_vvix['Low_VIX_to_VVIX_Ratio'] = vix_over_vvix['Low_VIX'] / vix_over_vvix['Low_VVIX']
vix_over_vvix['Open_VIX_to_VVIX_Ratio'] = vix_over_vvix['Open_VIX'] / vix_over_vvix['Open_VVIX']

# Drop VIX and VVIX columns, keep only ratio columns
vix_over_vvix = vix_over_vvix[['Close_VIX_to_VVIX_Ratio', 'High_VIX_to_VVIX_Ratio', 'Low_VIX_to_VVIX_Ratio', 'Open_VIX_to_VVIX_Ratio']]
```


```python
df_info(vix_over_vvix)
```

    The columns, shape, and data types are:
    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 4825 entries, 2007-01-03 to 2026-03-20
    Data columns (total 4 columns):
     #   Column                   Non-Null Count  Dtype  
    ---  ------                   --------------  -----  
     0   Close_VIX_to_VVIX_Ratio  4825 non-null   float64
     1   High_VIX_to_VVIX_Ratio   4825 non-null   float64
     2   Low_VIX_to_VVIX_Ratio    4825 non-null   float64
     3   Open_VIX_to_VVIX_Ratio   4825 non-null   float64
    dtypes: float64(4)
    memory usage: 188.5 KB
    None
    The first 5 rows are:



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
      <th>Close_VIX_to_VVIX_Ratio</th>
      <th>High_VIX_to_VVIX_Ratio</th>
      <th>Low_VIX_to_VVIX_Ratio</th>
      <th>Open_VIX_to_VVIX_Ratio</th>
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
      <th>2007-01-03</th>
      <td>0.14</td>
      <td>0.15</td>
      <td>0.13</td>
      <td>0.14</td>
    </tr>
    <tr>
      <th>2007-01-04</th>
      <td>0.13</td>
      <td>0.14</td>
      <td>0.13</td>
      <td>0.14</td>
    </tr>
    <tr>
      <th>2007-01-05</th>
      <td>0.13</td>
      <td>0.14</td>
      <td>0.13</td>
      <td>0.13</td>
    </tr>
    <tr>
      <th>2007-01-08</th>
      <td>0.13</td>
      <td>0.14</td>
      <td>0.13</td>
      <td>0.14</td>
    </tr>
    <tr>
      <th>2007-01-09</th>
      <td>0.13</td>
      <td>0.13</td>
      <td>0.13</td>
      <td>0.13</td>
    </tr>
  </tbody>
</table>
</div>


    The last 5 rows are:



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
      <th>Close_VIX_to_VVIX_Ratio</th>
      <th>High_VIX_to_VVIX_Ratio</th>
      <th>Low_VIX_to_VVIX_Ratio</th>
      <th>Open_VIX_to_VVIX_Ratio</th>
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
      <th>2026-03-16</th>
      <td>0.20</td>
      <td>0.21</td>
      <td>0.20</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>2026-03-17</th>
      <td>0.20</td>
      <td>0.21</td>
      <td>0.20</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>2026-03-18</th>
      <td>0.20</td>
      <td>0.20</td>
      <td>0.19</td>
      <td>0.19</td>
    </tr>
    <tr>
      <th>2026-03-19</th>
      <td>0.20</td>
      <td>0.20</td>
      <td>0.20</td>
      <td>0.19</td>
    </tr>
    <tr>
      <th>2026-03-20</th>
      <td>0.21</td>
      <td>0.22</td>
      <td>0.20</td>
      <td>0.21</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_03_VIX_Over_VVIX_DF_Info_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="03_VIX_Over_VVIX_DF_Info.md", 
    content=df_info_markdown(vix_over_vvix),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 03_VIX_Over_VVIX_DF_Info.md


### Statistics - VIX/VVIX


```python
vix_over_vvix_stats = vix_over_vvix.describe()
num_std = [-1, 0, 1, 2, 3, 4, 5]
for num in num_std:
    vix_over_vvix_stats.loc[f"mean + {num} std"] = {
        'Open_VIX_to_VVIX_Ratio': vix_over_vvix_stats.loc['mean']['Open_VIX_to_VVIX_Ratio'] + num * vix_over_vvix_stats.loc['std']['Open_VIX_to_VVIX_Ratio'],
        'High_VIX_to_VVIX_Ratio': vix_over_vvix_stats.loc['mean']['High_VIX_to_VVIX_Ratio'] + num * vix_over_vvix_stats.loc['std']['High_VIX_to_VVIX_Ratio'],
        'Low_VIX_to_VVIX_Ratio': vix_over_vvix_stats.loc['mean']['Low_VIX_to_VVIX_Ratio'] + num * vix_over_vvix_stats.loc['std']['Low_VIX_to_VVIX_Ratio'],
        'Close_VIX_to_VVIX_Ratio': vix_over_vvix_stats.loc['mean']['Close_VIX_to_VVIX_Ratio'] + num * vix_over_vvix_stats.loc['std']['Close_VIX_to_VVIX_Ratio'],
    }
    
display(vix_over_vvix_stats)
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
      <th>Close_VIX_to_VVIX_Ratio</th>
      <th>High_VIX_to_VVIX_Ratio</th>
      <th>Low_VIX_to_VVIX_Ratio</th>
      <th>Open_VIX_to_VVIX_Ratio</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>4825.00</td>
      <td>4825.00</td>
      <td>4825.00</td>
      <td>4825.00</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>0.21</td>
      <td>0.22</td>
      <td>0.21</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>std</th>
      <td>0.09</td>
      <td>0.09</td>
      <td>0.08</td>
      <td>0.09</td>
    </tr>
    <tr>
      <th>min</th>
      <td>0.10</td>
      <td>0.10</td>
      <td>0.10</td>
      <td>0.10</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>0.16</td>
      <td>0.16</td>
      <td>0.16</td>
      <td>0.16</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>0.18</td>
      <td>0.19</td>
      <td>0.18</td>
      <td>0.19</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>0.24</td>
      <td>0.25</td>
      <td>0.23</td>
      <td>0.24</td>
    </tr>
    <tr>
      <th>max</th>
      <td>0.76</td>
      <td>0.81</td>
      <td>0.72</td>
      <td>0.81</td>
    </tr>
    <tr>
      <th>mean + -1 std</th>
      <td>0.13</td>
      <td>0.13</td>
      <td>0.12</td>
      <td>0.13</td>
    </tr>
    <tr>
      <th>mean + 0 std</th>
      <td>0.21</td>
      <td>0.22</td>
      <td>0.21</td>
      <td>0.21</td>
    </tr>
    <tr>
      <th>mean + 1 std</th>
      <td>0.30</td>
      <td>0.31</td>
      <td>0.29</td>
      <td>0.30</td>
    </tr>
    <tr>
      <th>mean + 2 std</th>
      <td>0.38</td>
      <td>0.40</td>
      <td>0.37</td>
      <td>0.39</td>
    </tr>
    <tr>
      <th>mean + 3 std</th>
      <td>0.47</td>
      <td>0.49</td>
      <td>0.45</td>
      <td>0.47</td>
    </tr>
    <tr>
      <th>mean + 4 std</th>
      <td>0.56</td>
      <td>0.59</td>
      <td>0.53</td>
      <td>0.56</td>
    </tr>
    <tr>
      <th>mean + 5 std</th>
      <td>0.64</td>
      <td>0.68</td>
      <td>0.61</td>
      <td>0.65</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_03_VIX_Over_VVIX_Stats_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="03_VIX_Over_VVIX_Stats.md", 
    content=vix_over_vvix_stats.to_markdown(floatfmt=".2f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 03_VIX_Over_VVIX_Stats.md



```python
# # Group by year and calculate mean and std for OHLC
# vvix_stats_by_year = vvix.groupby(vvix.index.year)[["Open", "High", "Low", "Close"]].agg(["mean", "std", "min", "max"])

# # Flatten the column MultiIndex
# vvix_stats_by_year.columns = ['_'.join(col).strip() for col in vvix_stats_by_year.columns.values]
# vvix_stats_by_year.index.name = "Year"

# display(vvix_stats_by_year)
```


```python
# # Copy this <!-- INSERT_02_VVIX_Stats_By_Year_HERE --> to index_temp.md
# export_track_md_deps(dep_file=dep_file, md_filename="02_VVIX_Stats_By_Year.md", content=vvix_stats_by_year.to_markdown(floatfmt=".2f"))
```


```python
# # Group by month and calculate mean and std for OHLC
# vvix_stats_by_month = vvix.groupby(vvix.index.month)[["Open", "High", "Low", "Close"]].agg(["mean", "std", "min", "max"])

# # Flatten the column MultiIndex
# vvix_stats_by_month.columns = ['_'.join(col).strip() for col in vvix_stats_by_month.columns.values]
# vvix_stats_by_month.index.name = "Year"

# display(vvix_stats_by_month)
```


```python
# # Copy this <!-- INSERT_02_VVIX_Stats_By_Month_HERE --> to index_temp.md
# export_track_md_deps(dep_file=dep_file, md_filename="02_VVIX_Stats_By_Month.md", content=vvix_stats_by_month.to_markdown(floatfmt=".2f"))
```

### Deciles - VIX/VVIX


```python
vix_over_vvix_deciles = vix_over_vvix.quantile(np.arange(0, 1.1, 0.1))
display(vix_over_vvix_deciles)
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
      <th>Close_VIX_to_VVIX_Ratio</th>
      <th>High_VIX_to_VVIX_Ratio</th>
      <th>Low_VIX_to_VVIX_Ratio</th>
      <th>Open_VIX_to_VVIX_Ratio</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0.00</th>
      <td>0.10</td>
      <td>0.10</td>
      <td>0.10</td>
      <td>0.10</td>
    </tr>
    <tr>
      <th>0.10</th>
      <td>0.14</td>
      <td>0.15</td>
      <td>0.14</td>
      <td>0.14</td>
    </tr>
    <tr>
      <th>0.20</th>
      <td>0.16</td>
      <td>0.16</td>
      <td>0.15</td>
      <td>0.16</td>
    </tr>
    <tr>
      <th>0.30</th>
      <td>0.16</td>
      <td>0.17</td>
      <td>0.16</td>
      <td>0.17</td>
    </tr>
    <tr>
      <th>0.40</th>
      <td>0.17</td>
      <td>0.18</td>
      <td>0.17</td>
      <td>0.17</td>
    </tr>
    <tr>
      <th>0.50</th>
      <td>0.18</td>
      <td>0.19</td>
      <td>0.18</td>
      <td>0.19</td>
    </tr>
    <tr>
      <th>0.60</th>
      <td>0.20</td>
      <td>0.21</td>
      <td>0.19</td>
      <td>0.20</td>
    </tr>
    <tr>
      <th>0.70</th>
      <td>0.22</td>
      <td>0.23</td>
      <td>0.21</td>
      <td>0.22</td>
    </tr>
    <tr>
      <th>0.80</th>
      <td>0.26</td>
      <td>0.27</td>
      <td>0.25</td>
      <td>0.26</td>
    </tr>
    <tr>
      <th>0.90</th>
      <td>0.32</td>
      <td>0.33</td>
      <td>0.31</td>
      <td>0.32</td>
    </tr>
    <tr>
      <th>1.00</th>
      <td>0.76</td>
      <td>0.81</td>
      <td>0.72</td>
      <td>0.81</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_03_VIX_Over_VVIX_Deciles_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="03_VIX_Over_VVIX_Deciles.md", content=vix_over_vvix_deciles.to_markdown(floatfmt=".2f"))
```

    ✅ Exported and tracked: 03_VIX_Over_VVIX_Deciles.md


## Plots - VIX/VVIX

### Histogram Distribution - VIX/VVIX


```python
# Plotting
plt.figure(figsize=(10, 6))

# Histogram
plt.hist([vix_over_vvix['High_VIX_to_VVIX_Ratio']], label=['High_VIX_to_VVIX_Ratio'], bins=200, edgecolor='black', color='steelblue', alpha=0.7)
plt.hist([vix_over_vvix['Low_VIX_to_VVIX_Ratio']], label=['Low_VIX_to_VVIX_Ratio'], bins=200, edgecolor='black', color='lightblue', alpha=0.7)

# Plot a vertical line at the mean, mean + 1 std, and mean + 2 std
plt.axvline(vix_over_vvix_stats.loc['mean + -1 std']['High_VIX_to_VVIX_Ratio'], color='brown', linestyle='dashed', linewidth=1, label=f'High Mean - 1 std: {vix_over_vvix_stats.loc['mean + -1 std']['High_VIX_to_VVIX_Ratio']:.2f}')
plt.axvline(vix_over_vvix_stats.loc['mean + -1 std']['Low_VIX_to_VVIX_Ratio'], color='brown', linestyle='solid', linewidth=1, label=f'Low Mean - 1 std: {vix_over_vvix_stats.loc['mean + -1 std']['Low_VIX_to_VVIX_Ratio']:.2f}')

plt.axvline(vix_over_vvix_stats.loc['mean']['High_VIX_to_VVIX_Ratio'], color='red', linestyle='dashed', linewidth=1, label=f'High Mean: {vix_over_vvix_stats.loc['mean']['High_VIX_to_VVIX_Ratio']:.2f}')
plt.axvline(vix_over_vvix_stats.loc['mean']['Low_VIX_to_VVIX_Ratio'], color='red', linestyle='solid', linewidth=1, label=f'Low Mean: {vix_over_vvix_stats.loc['mean']['Low_VIX_to_VVIX_Ratio']:.2f}')

plt.axvline(vix_over_vvix_stats.loc['mean + 1 std']['High_VIX_to_VVIX_Ratio'], color='green', linestyle='dashed', linewidth=1, label=f'High Mean + 1 std: {vix_over_vvix_stats.loc['mean + 1 std']['High_VIX_to_VVIX_Ratio']:.2f}')
plt.axvline(vix_over_vvix_stats.loc['mean + 1 std']['Low_VIX_to_VVIX_Ratio'], color='green', linestyle='solid', linewidth=1, label=f'Low Mean + 1 std: {vix_over_vvix_stats.loc['mean + 1 std']['Low_VIX_to_VVIX_Ratio']:.2f}')

plt.axvline(vix_over_vvix_stats.loc['mean + 2 std']['High_VIX_to_VVIX_Ratio'], color='orange', linestyle='dashed', linewidth=1, label=f'High Mean + 2 std: {vix_over_vvix_stats.loc['mean + 2 std']['High_VIX_to_VVIX_Ratio']:.2f}')
plt.axvline(vix_over_vvix_stats.loc['mean + 2 std']['Low_VIX_to_VVIX_Ratio'], color='orange', linestyle='solid', linewidth=1, label=f'Low Mean + 2 std: {vix_over_vvix_stats.loc['mean + 2 std']['Low_VIX_to_VVIX_Ratio']:.2f}')

plt.axvline(vix_over_vvix_stats.loc['mean + 3 std']['High_VIX_to_VVIX_Ratio'], color='black', linestyle='dashed', linewidth=1, label=f'High Mean + 3 std: {vix_over_vvix_stats.loc['mean + 3 std']['High_VIX_to_VVIX_Ratio']:.2f}')
plt.axvline(vix_over_vvix_stats.loc['mean + 3 std']['Low_VIX_to_VVIX_Ratio'], color='black', linestyle='solid', linewidth=1, label=f'Low Mean + 3 std: {vix_over_vvix_stats.loc['mean + 3 std']['Low_VIX_to_VVIX_Ratio']:.2f}')

plt.axvline(vix_over_vvix_stats.loc['mean + 4 std']['High_VIX_to_VVIX_Ratio'], color='yellow', linestyle='dashed', linewidth=1, label=f'High Mean + 4 std: {vix_over_vvix_stats.loc['mean + 4 std']['High_VIX_to_VVIX_Ratio']:.2f}')
plt.axvline(vix_over_vvix_stats.loc['mean + 4 std']['Low_VIX_to_VVIX_Ratio'], color='yellow', linestyle='solid', linewidth=1, label=f'Low Mean + 4 std: {vix_over_vvix_stats.loc['mean + 4 std']['Low_VIX_to_VVIX_Ratio']:.2f}')

# Set X axis
x_tick_spacing = 0.05  # Specify the interval for y-axis ticks
plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
plt.xlabel("VIX/VVIX")
plt.xticks(rotation=0)

# Set Y axis
y_tick_spacing = 25  # Specify the interval for y-axis ticks
plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
plt.ylabel("# Of Datapoints")
plt.yticks()

# Set title, layout, grid, and legend
plt.title("CBOE VIX/VVIX Histogram (200 Bins)")
plt.tight_layout()
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Save figure and display plot
plt.savefig("03_Histogram+Mean+SD.png", dpi=300, bbox_inches="tight")
plt.show()
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_101_0.png)
    


### Historical Data - VIX/VVIX


```python
plot_time_series(
    df=vix_over_vvix,
    plot_start_date=None,
    plot_end_date="2016-12-31",
    plot_columns=["High_VIX_to_VVIX_Ratio", "Low_VIX_to_VVIX_Ratio"],
    title="CBOE VIX/VVIX, 2007 - 2016",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX/VVIX",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing=0.10,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="03_VIX_Over_VVIX_Plot_2007-2016",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_103_0.png)
    



```python
plot_time_series(
    df=vix_over_vvix,
    plot_start_date="2017-01-01",
    plot_end_date=None,
    plot_columns=["High_VIX_to_VVIX_Ratio", "Low_VIX_to_VVIX_Ratio"],
    title="CBOE VIX/VVIX, 2017 - Present",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX/VVIX",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing=0.10,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="03_VIX_Over_VVIX_Plot_2017-Present",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_104_0.png)
    



```python
plot_time_series(
    df=vix_over_vvix,
    plot_start_date="2024-01-01",
    plot_end_date=None,
    plot_columns=["High_VIX_to_VVIX_Ratio", "Low_VIX_to_VVIX_Ratio"],
    title="CBOE VIX/VVIX, 2024 - Present",
    x_label="Date",
    x_format="Month",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX/VVIX",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing=0.05,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="03_VIX_Over_VVIX_Plot_2024-Present",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_105_0.png)
    



```python
plot_time_series(
    df=vix_over_vvix,
    plot_start_date="2025-01-01",
    plot_end_date=None,
    plot_columns=["High_VIX_to_VVIX_Ratio", "Low_VIX_to_VVIX_Ratio"],
    title="CBOE VIX/VVIX, 2025 - Present",
    x_label="Date",
    x_format="Month",
    x_tick_spacing=1,
    x_tick_rotation=30,
    y_label="VIX/VVIX",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing=0.05,
    y_tick_rotation=0,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="03_VIX_Over_VVIX_Plot_2025-Present",
)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_106_0.png)
    


### Stats By Year - VIX/VVIX


```python
# plot_stats(
#     stats_df=vvix_stats_by_year,
#     plot_columns=["Open_mean", "High_mean", "Low_mean", "Close_mean"],
#     title="VVIX Mean OHLC By Year",
#     x_label="Year",
#     x_rotation=45,
#     x_tick_spacing=1,
#     y_label="Price",
#     y_tick_spacing=5,
#     grid=True,
#     legend=True,
#     export_plot=True,
#     plot_file_name="02_VVIX_Stats_By_Year"
# )
```

### Stats By Month - VIX/VVIX


```python
# plot_stats(
#     stats_df=vvix_stats_by_month,
#     plot_columns=["Open_mean", "High_mean", "Low_mean", "Close_mean"],
#     title="VVIX Mean OHLC By Month",
#     x_label="Month",
#     x_rotation=0,
#     x_tick_spacing=1,
#     y_label="Price",
#     y_tick_spacing=1,
#     grid=True,
#     legend=True,
#     export_plot=True,
#     plot_file_name="02_VVIX_Stats_By_Month"
# )
```

## Investigating A Signal

### Determining A Spike Level


```python
# Define the spike multiplier for detecting significant spikes
spike_level = 1.25

# =========================
# Simple Moving Averages (SMA)
# =========================

# Calculate 10-period SMA of 'High'
vix['High_SMA_10'] = vix['High'].rolling(window=10).mean()

# Shift the 10-period SMA by 1 to compare with current 'High'
vix['High_SMA_10_Shift'] = vix['High_SMA_10'].shift(1)

# Calculate the spike level based on shifted SMA and spike multiplier
vix['Spike_Level_SMA'] = vix['High_SMA_10_Shift'] * spike_level

# Calculate 20-period SMA of 'High'
vix['High_SMA_20'] = vix['High'].rolling(window=20).mean()

# Determine if 'High' exceeds the spike level (indicates a spike)
vix['Spike_SMA'] = vix['High'] >= vix['Spike_Level_SMA']

# Calculate 50-period SMA of 'High' for trend analysis
vix['High_SMA_50'] = vix['High'].rolling(window=50).mean()

# =========================
# Exponential Moving Averages (EMA)
# =========================

# Calculate 10-period EMA of 'High'
vix['High_EMA_10'] = vix['High'].ewm(span=10, adjust=False).mean()

# Shift the 10-period EMA by 1 to compare with current 'High'
vix['High_EMA_10_Shift'] = vix['High_EMA_10'].shift(1)

# Calculate the spike level based on shifted EMA and spike multiplier
vix['Spike_Level_EMA'] = vix['High_EMA_10_Shift'] * spike_level

# Calculate 20-period EMA of 'High'
vix['High_EMA_20'] = vix['High'].ewm(span=20, adjust=False).mean()

# Determine if 'High' exceeds the spike level (indicates a spike)
vix['Spike_EMA'] = vix['High'] >= vix['Spike_Level_EMA']

# Calculate 50-period EMA of 'High' for trend analysis
vix['High_EMA_50'] = vix['High'].ewm(span=50, adjust=False).mean()
```


```python
display(vix)
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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>High_SMA_10</th>
      <th>High_SMA_10_Shift</th>
      <th>Spike_Level_SMA</th>
      <th>High_SMA_20</th>
      <th>Spike_SMA</th>
      <th>High_SMA_50</th>
      <th>High_EMA_10</th>
      <th>High_EMA_10_Shift</th>
      <th>Spike_Level_EMA</th>
      <th>High_EMA_20</th>
      <th>Spike_EMA</th>
      <th>High_EMA_50</th>
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
      <th>1990-01-02</th>
      <td>17.24</td>
      <td>17.24</td>
      <td>17.24</td>
      <td>17.24</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>False</td>
      <td>NaN</td>
      <td>17.24</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>17.24</td>
      <td>False</td>
      <td>17.24</td>
    </tr>
    <tr>
      <th>1990-01-03</th>
      <td>18.19</td>
      <td>18.19</td>
      <td>18.19</td>
      <td>18.19</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>False</td>
      <td>NaN</td>
      <td>17.41</td>
      <td>17.24</td>
      <td>21.55</td>
      <td>17.33</td>
      <td>False</td>
      <td>17.28</td>
    </tr>
    <tr>
      <th>1990-01-04</th>
      <td>19.22</td>
      <td>19.22</td>
      <td>19.22</td>
      <td>19.22</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>False</td>
      <td>NaN</td>
      <td>17.74</td>
      <td>17.41</td>
      <td>21.77</td>
      <td>17.51</td>
      <td>False</td>
      <td>17.35</td>
    </tr>
    <tr>
      <th>1990-01-05</th>
      <td>20.11</td>
      <td>20.11</td>
      <td>20.11</td>
      <td>20.11</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>False</td>
      <td>NaN</td>
      <td>18.17</td>
      <td>17.74</td>
      <td>22.18</td>
      <td>17.76</td>
      <td>False</td>
      <td>17.46</td>
    </tr>
    <tr>
      <th>1990-01-08</th>
      <td>20.26</td>
      <td>20.26</td>
      <td>20.26</td>
      <td>20.26</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>False</td>
      <td>NaN</td>
      <td>18.55</td>
      <td>18.17</td>
      <td>22.71</td>
      <td>18.00</td>
      <td>False</td>
      <td>17.57</td>
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
      <th>2026-03-16</th>
      <td>23.51</td>
      <td>26.42</td>
      <td>23.23</td>
      <td>25.88</td>
      <td>27.85</td>
      <td>27.74</td>
      <td>34.67</td>
      <td>24.77</td>
      <td>False</td>
      <td>20.86</td>
      <td>26.91</td>
      <td>27.02</td>
      <td>33.78</td>
      <td>25.29</td>
      <td>False</td>
      <td>22.33</td>
    </tr>
    <tr>
      <th>2026-03-17</th>
      <td>22.37</td>
      <td>24.58</td>
      <td>21.87</td>
      <td>24.56</td>
      <td>27.50</td>
      <td>27.85</td>
      <td>34.82</td>
      <td>24.85</td>
      <td>False</td>
      <td>21.05</td>
      <td>26.49</td>
      <td>26.91</td>
      <td>33.64</td>
      <td>25.22</td>
      <td>False</td>
      <td>22.42</td>
    </tr>
    <tr>
      <th>2026-03-18</th>
      <td>25.09</td>
      <td>25.13</td>
      <td>21.47</td>
      <td>21.51</td>
      <td>27.52</td>
      <td>27.50</td>
      <td>34.37</td>
      <td>25.09</td>
      <td>False</td>
      <td>21.24</td>
      <td>26.24</td>
      <td>26.49</td>
      <td>33.11</td>
      <td>25.21</td>
      <td>False</td>
      <td>22.53</td>
    </tr>
    <tr>
      <th>2026-03-19</th>
      <td>24.06</td>
      <td>27.52</td>
      <td>23.54</td>
      <td>25.60</td>
      <td>27.69</td>
      <td>27.52</td>
      <td>34.40</td>
      <td>25.41</td>
      <td>False</td>
      <td>21.49</td>
      <td>26.48</td>
      <td>26.24</td>
      <td>32.80</td>
      <td>25.43</td>
      <td>False</td>
      <td>22.72</td>
    </tr>
    <tr>
      <th>2026-03-20</th>
      <td>26.78</td>
      <td>29.28</td>
      <td>23.68</td>
      <td>24.46</td>
      <td>27.63</td>
      <td>27.69</td>
      <td>34.61</td>
      <td>25.82</td>
      <td>False</td>
      <td>21.76</td>
      <td>26.99</td>
      <td>26.48</td>
      <td>33.09</td>
      <td>25.80</td>
      <td>False</td>
      <td>22.98</td>
    </tr>
  </tbody>
</table>
<p>9121 rows × 16 columns</p>
</div>



```python
vix[vix['High'] >= 50]
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
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>High_SMA_10</th>
      <th>High_SMA_10_Shift</th>
      <th>Spike_Level_SMA</th>
      <th>High_SMA_20</th>
      <th>Spike_SMA</th>
      <th>High_SMA_50</th>
      <th>High_EMA_10</th>
      <th>High_EMA_10_Shift</th>
      <th>Spike_Level_EMA</th>
      <th>High_EMA_20</th>
      <th>Spike_EMA</th>
      <th>High_EMA_50</th>
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
      <th>2008-10-06</th>
      <td>52.05</td>
      <td>58.24</td>
      <td>45.12</td>
      <td>45.12</td>
      <td>42.92</td>
      <td>40.52</td>
      <td>50.65</td>
      <td>37.24</td>
      <td>True</td>
      <td>28.17</td>
      <td>44.33</td>
      <td>41.24</td>
      <td>51.55</td>
      <td>38.82</td>
      <td>True</td>
      <td>31.65</td>
    </tr>
    <tr>
      <th>2008-10-07</th>
      <td>53.68</td>
      <td>54.19</td>
      <td>47.03</td>
      <td>52.05</td>
      <td>44.73</td>
      <td>42.92</td>
      <td>53.65</td>
      <td>38.66</td>
      <td>True</td>
      <td>28.76</td>
      <td>46.12</td>
      <td>44.33</td>
      <td>55.41</td>
      <td>40.29</td>
      <td>False</td>
      <td>32.53</td>
    </tr>
    <tr>
      <th>2008-10-08</th>
      <td>57.53</td>
      <td>59.06</td>
      <td>51.90</td>
      <td>53.68</td>
      <td>46.97</td>
      <td>44.73</td>
      <td>55.91</td>
      <td>40.34</td>
      <td>True</td>
      <td>29.46</td>
      <td>48.47</td>
      <td>46.12</td>
      <td>57.65</td>
      <td>42.07</td>
      <td>True</td>
      <td>33.57</td>
    </tr>
    <tr>
      <th>2008-10-09</th>
      <td>63.92</td>
      <td>64.92</td>
      <td>52.54</td>
      <td>57.57</td>
      <td>49.94</td>
      <td>46.97</td>
      <td>58.71</td>
      <td>42.27</td>
      <td>True</td>
      <td>30.31</td>
      <td>51.46</td>
      <td>48.47</td>
      <td>60.59</td>
      <td>44.25</td>
      <td>True</td>
      <td>34.80</td>
    </tr>
    <tr>
      <th>2008-10-10</th>
      <td>69.95</td>
      <td>76.94</td>
      <td>65.63</td>
      <td>65.85</td>
      <td>53.99</td>
      <td>49.94</td>
      <td>62.42</td>
      <td>44.79</td>
      <td>True</td>
      <td>31.39</td>
      <td>56.10</td>
      <td>51.46</td>
      <td>64.33</td>
      <td>47.36</td>
      <td>True</td>
      <td>36.46</td>
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
      <th>2024-08-05</th>
      <td>38.57</td>
      <td>65.73</td>
      <td>23.39</td>
      <td>23.39</td>
      <td>23.84</td>
      <td>18.95</td>
      <td>23.69</td>
      <td>19.11</td>
      <td>True</td>
      <td>15.66</td>
      <td>28.04</td>
      <td>19.66</td>
      <td>24.58</td>
      <td>22.15</td>
      <td>True</td>
      <td>17.62</td>
    </tr>
    <tr>
      <th>2025-04-07</th>
      <td>46.98</td>
      <td>60.13</td>
      <td>38.58</td>
      <td>60.13</td>
      <td>28.60</td>
      <td>24.51</td>
      <td>30.63</td>
      <td>26.10</td>
      <td>True</td>
      <td>22.35</td>
      <td>33.61</td>
      <td>27.72</td>
      <td>34.65</td>
      <td>28.48</td>
      <td>True</td>
      <td>23.95</td>
    </tr>
    <tr>
      <th>2025-04-08</th>
      <td>52.33</td>
      <td>57.52</td>
      <td>36.48</td>
      <td>44.04</td>
      <td>32.58</td>
      <td>28.60</td>
      <td>35.76</td>
      <td>27.50</td>
      <td>True</td>
      <td>23.05</td>
      <td>37.96</td>
      <td>33.61</td>
      <td>42.01</td>
      <td>31.25</td>
      <td>True</td>
      <td>25.27</td>
    </tr>
    <tr>
      <th>2025-04-09</th>
      <td>33.62</td>
      <td>57.96</td>
      <td>31.90</td>
      <td>50.98</td>
      <td>36.47</td>
      <td>32.58</td>
      <td>40.72</td>
      <td>29.05</td>
      <td>True</td>
      <td>23.84</td>
      <td>41.60</td>
      <td>37.96</td>
      <td>47.45</td>
      <td>33.79</td>
      <td>True</td>
      <td>26.55</td>
    </tr>
    <tr>
      <th>2025-04-10</th>
      <td>40.72</td>
      <td>54.87</td>
      <td>34.44</td>
      <td>34.44</td>
      <td>40.03</td>
      <td>36.47</td>
      <td>45.59</td>
      <td>30.49</td>
      <td>True</td>
      <td>24.58</td>
      <td>44.01</td>
      <td>41.60</td>
      <td>51.99</td>
      <td>35.80</td>
      <td>True</td>
      <td>27.66</td>
    </tr>
  </tbody>
</table>
<p>97 rows × 16 columns</p>
</div>



### Spike Counts (Signals) By Year


```python
# Ensure the index is a DatetimeIndex
vix.index = pd.to_datetime(vix.index)

# Create a new column for the year extracted from the date index
vix['Year'] = vix.index.year

# Group by year and the "Spike_SMA" and "Spike_EMA" columns, then count occurrences
spike_count_SMA = vix.groupby(['Year', 'Spike_SMA']).size().unstack(fill_value=0)

display(spike_count_SMA)
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
      <th>Spike_SMA</th>
      <th>False</th>
      <th>True</th>
    </tr>
    <tr>
      <th>Year</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1990</th>
      <td>248</td>
      <td>5</td>
    </tr>
    <tr>
      <th>1991</th>
      <td>249</td>
      <td>4</td>
    </tr>
    <tr>
      <th>1992</th>
      <td>250</td>
      <td>4</td>
    </tr>
    <tr>
      <th>1993</th>
      <td>251</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1994</th>
      <td>243</td>
      <td>9</td>
    </tr>
    <tr>
      <th>1995</th>
      <td>252</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1996</th>
      <td>248</td>
      <td>6</td>
    </tr>
    <tr>
      <th>1997</th>
      <td>247</td>
      <td>6</td>
    </tr>
    <tr>
      <th>1998</th>
      <td>243</td>
      <td>9</td>
    </tr>
    <tr>
      <th>1999</th>
      <td>250</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2000</th>
      <td>248</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2001</th>
      <td>240</td>
      <td>8</td>
    </tr>
    <tr>
      <th>2002</th>
      <td>248</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2003</th>
      <td>251</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2004</th>
      <td>250</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2005</th>
      <td>250</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2006</th>
      <td>242</td>
      <td>9</td>
    </tr>
    <tr>
      <th>2007</th>
      <td>239</td>
      <td>12</td>
    </tr>
    <tr>
      <th>2008</th>
      <td>238</td>
      <td>15</td>
    </tr>
    <tr>
      <th>2009</th>
      <td>249</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>239</td>
      <td>13</td>
    </tr>
    <tr>
      <th>2011</th>
      <td>240</td>
      <td>12</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>248</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2013</th>
      <td>249</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2014</th>
      <td>235</td>
      <td>17</td>
    </tr>
    <tr>
      <th>2015</th>
      <td>240</td>
      <td>12</td>
    </tr>
    <tr>
      <th>2016</th>
      <td>234</td>
      <td>18</td>
    </tr>
    <tr>
      <th>2017</th>
      <td>244</td>
      <td>7</td>
    </tr>
    <tr>
      <th>2018</th>
      <td>228</td>
      <td>23</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>241</td>
      <td>11</td>
    </tr>
    <tr>
      <th>2020</th>
      <td>224</td>
      <td>29</td>
    </tr>
    <tr>
      <th>2021</th>
      <td>235</td>
      <td>17</td>
    </tr>
    <tr>
      <th>2022</th>
      <td>239</td>
      <td>12</td>
    </tr>
    <tr>
      <th>2023</th>
      <td>246</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2024</th>
      <td>237</td>
      <td>15</td>
    </tr>
    <tr>
      <th>2025</th>
      <td>231</td>
      <td>19</td>
    </tr>
    <tr>
      <th>2026</th>
      <td>49</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Copy this <!-- INSERT_08_Spike_Counts_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="08_Spike_Counts.md", content=spike_count_SMA.to_markdown())
```

    ✅ Exported and tracked: 08_Spike_Counts.md



```python
# Ensure the index is a DatetimeIndex
vix.index = pd.to_datetime(vix.index)

# Create a new column for the year extracted from the date index
vix['Year'] = vix.index.year

# Group by year and the "Spike_SMA" and "Spike_EMA" columns, then count occurrences
spike_count_EMA = vix.groupby(['Year', 'Spike_EMA']).size().unstack(fill_value=0)

display(spike_count_EMA)
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
      <th>Spike_EMA</th>
      <th>False</th>
      <th>True</th>
    </tr>
    <tr>
      <th>Year</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1990</th>
      <td>247</td>
      <td>6</td>
    </tr>
    <tr>
      <th>1991</th>
      <td>251</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1992</th>
      <td>253</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1993</th>
      <td>251</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1994</th>
      <td>247</td>
      <td>5</td>
    </tr>
    <tr>
      <th>1995</th>
      <td>252</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1996</th>
      <td>252</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1997</th>
      <td>250</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1998</th>
      <td>246</td>
      <td>6</td>
    </tr>
    <tr>
      <th>1999</th>
      <td>250</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2000</th>
      <td>250</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2001</th>
      <td>241</td>
      <td>7</td>
    </tr>
    <tr>
      <th>2002</th>
      <td>250</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2003</th>
      <td>251</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2004</th>
      <td>251</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2005</th>
      <td>250</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2006</th>
      <td>248</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2007</th>
      <td>242</td>
      <td>9</td>
    </tr>
    <tr>
      <th>2008</th>
      <td>240</td>
      <td>13</td>
    </tr>
    <tr>
      <th>2009</th>
      <td>251</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>243</td>
      <td>9</td>
    </tr>
    <tr>
      <th>2011</th>
      <td>242</td>
      <td>10</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>250</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2013</th>
      <td>250</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2014</th>
      <td>236</td>
      <td>16</td>
    </tr>
    <tr>
      <th>2015</th>
      <td>243</td>
      <td>9</td>
    </tr>
    <tr>
      <th>2016</th>
      <td>238</td>
      <td>14</td>
    </tr>
    <tr>
      <th>2017</th>
      <td>244</td>
      <td>7</td>
    </tr>
    <tr>
      <th>2018</th>
      <td>230</td>
      <td>21</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>242</td>
      <td>10</td>
    </tr>
    <tr>
      <th>2020</th>
      <td>228</td>
      <td>25</td>
    </tr>
    <tr>
      <th>2021</th>
      <td>239</td>
      <td>13</td>
    </tr>
    <tr>
      <th>2022</th>
      <td>244</td>
      <td>7</td>
    </tr>
    <tr>
      <th>2023</th>
      <td>248</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2024</th>
      <td>244</td>
      <td>8</td>
    </tr>
    <tr>
      <th>2025</th>
      <td>236</td>
      <td>14</td>
    </tr>
    <tr>
      <th>2026</th>
      <td>50</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Plotting
plt.figure(figsize=(10, 6))

# Bar positions
x = np.arange(len(spike_count_SMA[True].index))
width = 0.35

# Plot SMA bars
plt.bar(x - width / 2, spike_count_SMA[True].values, width, color="steelblue", label="Spike Counts Using SMA")

# Plot EMA bars
plt.bar(x + width / 2, spike_count_EMA[True].values, width, color="forestgreen", label="Spike Counts Using EMA")

# Set X axis
plt.xlabel("Year", fontsize=10)
plt.xticks(x, spike_count_SMA[True].index, rotation=30)
plt.xlim(x[0] - 2 * width, x[-1] + 2 * width)

# Set Y axis
y_tick_spacing = 2  # Specify the interval for y-axis ticks
plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
plt.ylabel("Count")
plt.yticks()

# Set title, layout, grid, and legend
plt.title("Yearly Totals Of Spike Counts")
plt.tight_layout()
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Save figure and display plot
plt.savefig("08_Spike_Counts.png", dpi=300, bbox_inches="tight")
plt.show()
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_120_0.png)
    


### Spike Counts (Signals) Plots By Year


```python
def vix_plot(start_year, end_year, x_tick_spacing):
    # Start and end dates
    start_date = start_year + '-01-01'
    end_date = end_year + '-12-31'

    # Create temporary dataframe for the specified date range
    vix_temp = vix[(vix.index >= start_date) & (vix.index <= end_date)]

    # Plotting
    plt.figure(figsize=(10, 6))

    # Plot data
    plt.plot(vix_temp.index, vix_temp['High'], label='High', linestyle='-', color='steelblue', linewidth=1)
    plt.plot(vix_temp.index, vix_temp['Low'], label='Low', linestyle='-', color='brown', linewidth=1)
    plt.plot(vix_temp.index, vix_temp['High_SMA_10'], label='10 Day High SMA', linestyle='-', color='red', linewidth=1)
    plt.plot(vix_temp.index, vix_temp['High_SMA_20'], label='20 Day High SMA', linestyle='-', color='orange', linewidth=1)
    plt.plot(vix_temp.index, vix_temp['High_SMA_50'], label='50 Day High SMA', linestyle='-', color='green', linewidth=1)
    plt.scatter(vix_temp[vix_temp['Spike_SMA'] == True].index, vix_temp[vix_temp['Spike_SMA'] == True]['High'], label='Spike (High > 1.25 * 10 Day High SMA)', linestyle='-', color='black', s=20)

    # Set X axis
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=x_tick_spacing))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xlabel("Date")
    plt.xticks(rotation=30)

    # Set Y axis
    y_tick_spacing = 5  # Specify the interval for y-axis ticks
    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel("VIX")
    plt.yticks()

    # Set title, layout, grid, and legend
    plt.title(f"CBOE Volatility Index (VIX), {start_year} - {end_year}")
    plt.tight_layout()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # Save figure and display plot
    plt.savefig(f"09_VIX_SMA_Spike_{start_year}_{end_year}.png", dpi=300, bbox_inches="tight")
    plt.show()
```

#### Yearly Plots


```python
for year in range(1990, 2027):
    vix_plot(str(year), str(year), x_tick_spacing=1)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_0.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_1.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_2.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_3.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_4.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_5.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_6.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_7.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_8.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_9.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_10.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_11.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_12.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_13.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_14.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_15.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_16.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_17.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_18.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_19.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_20.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_21.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_22.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_23.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_24.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_25.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_26.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_27.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_28.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_29.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_30.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_31.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_32.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_33.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_34.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_35.png)
    



    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_124_36.png)
    


### Spike Counts (Signals) Plots By Decade

#### 1990 - 1994


```python
vix_plot('1990', '1994', x_tick_spacing=2)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_127_0.png)
    


#### 1995 - 1999


```python
vix_plot('1995', '1999', x_tick_spacing=2)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_129_0.png)
    


#### 2000 - 2004


```python
vix_plot('2000', '2004', x_tick_spacing=2)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_131_0.png)
    


#### 2005 - 2009


```python
vix_plot('2005', '2009', x_tick_spacing=2)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_133_0.png)
    


#### 2010 - 2014


```python
vix_plot('2010', '2014', x_tick_spacing=2)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_135_0.png)
    


#### 2015 - 2019


```python
vix_plot('2015', '2019', x_tick_spacing=2)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_137_0.png)
    


#### 2020 - 2024


```python
vix_plot('2020', '2024', x_tick_spacing=2)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_139_0.png)
    


#### 2025 - Present


```python
vix_plot('2025', '2029', x_tick_spacing=1)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_141_0.png)
    


## Trading History

### Trades Executed


```python
# from schwab_order_history import schwab_order_history
```


```python
# from datetime import datetime
# import pandas as pd

# # Define your date ranges
# range_2024 = {
#     "from": "2024-01-01T00:00:00.000Z",
#     "to": "2024-12-31T23:59:59.000Z",
# }

# range_2025 = {
#     "from": "2025-01-01T00:00:00.000Z",
#     "to": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
# }

# # Pull both sets of orders
# df_2024 = schwab_order_history(
#     max_results=1000,  # or whatever large number you want
#     from_entered_time=range_2024["from"],
#     to_entered_time=range_2024["to"],
#     account_id=None,  # or pass your specific encrypted account ID
# )

# df_2025 = schwab_order_history(
#     max_results=1000,
#     from_entered_time=range_2025["from"],
#     to_entered_time=range_2025["to"],
#     account_id=None,
# )

# # Combine the two dataframes
# df_all = pd.concat([df_2024, df_2025], ignore_index=True)

```


```python
# df_2024
```


```python
# # Filter for symbols that start with "VIX"
# df_vix = df_all[df_all["symbol"].str.startswith("VIX")].copy()
# df_vix = df_vix.sort_values(by=['symbol', 'execution_time'], ascending=[True, True])
```


```python
# df_vix
```

### Trades Executed


```python
# Import CSV file of VIX transactions from IRA and Brokerage accounts
vix_transactions_IRA = pd.read_csv(DATA_MANUAL_DIR / "VIX_Transactions_IRA.csv")
vix_transactions_Brokerage = pd.read_excel(DATA_MANUAL_DIR / "VIX_Transactions_Brokerage.xlsx", sheet_name="VIX_Transactions_Brokerage")
```


```python
# Combine the two DataFrames
vix_transactions = pd.concat([vix_transactions_IRA, vix_transactions_Brokerage], ignore_index=True)

# Drop unnecessary columns
vix_transactions.drop(columns = {'Description'}, inplace=True)

# Convert Amount, Price, and Fees & Comm columns to numeric
vix_transactions['Amount'] = vix_transactions['Amount'].replace({'\$': '', ',': ''}, regex=True).astype(float)
vix_transactions['Price'] = vix_transactions['Price'].replace({'\$': '', ',': ''}, regex=True).astype(float)
vix_transactions['Fees & Comm'] = vix_transactions['Fees & Comm'].replace({'\$': '', ',': ''}, regex=True).astype(float)

# Convert Amount column to absolute values
vix_transactions['Amount'] = abs(vix_transactions['Amount'])

# Extract date for option expiration with regex (MM/DD/YYYY)
vix_transactions["Exp_Date"] = vix_transactions["Symbol"].str.extract(r'(\d{2}/\d{2}/\d{4})')

# Extract date for option strike price with regex and convert to float
vix_transactions["Strike_Price"] = vix_transactions["Symbol"].str.extract(r'(\d{2}\.\d{2})').astype(float)

# Convert expiration date and trade date to datetime
vix_transactions["Exp_Date"] = pd.to_datetime(vix_transactions["Exp_Date"], format="%m/%d/%Y")
vix_transactions['Date'] = pd.to_datetime(vix_transactions['Date'])

# Rename date to trade date
vix_transactions.rename(columns={'Date': 'Trade_Date'}, inplace=True)

# Sort by Exp_Date, then Strike_Price, then Trade_Date
vix_transactions.sort_values(by=['Exp_Date', 'Strike_Price', 'Trade_Date'], ascending=[True, True, True], inplace=True)

# Reset index
vix_transactions.reset_index(drop=True, inplace=True)
vix_transactions
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
      <th>Trade_Date</th>
      <th>Action</th>
      <th>Symbol</th>
      <th>Quantity</th>
      <th>Price</th>
      <th>Fees &amp; Comm</th>
      <th>Amount</th>
      <th>Approx_VIX_Level</th>
      <th>Comments</th>
      <th>Exp_Date</th>
      <th>Strike_Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2024-08-05</td>
      <td>Buy to Open</td>
      <td>VIX 09/18/2024 34.00 P</td>
      <td>1</td>
      <td>10.95</td>
      <td>1.08</td>
      <td>1096.08</td>
      <td>34.33</td>
      <td>NaN</td>
      <td>2024-09-18</td>
      <td>34.00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2024-08-21</td>
      <td>Sell to Close</td>
      <td>VIX 09/18/2024 34.00 P</td>
      <td>1</td>
      <td>17.95</td>
      <td>1.08</td>
      <td>1793.92</td>
      <td>16.50</td>
      <td>NaN</td>
      <td>2024-09-18</td>
      <td>34.00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2024-08-05</td>
      <td>Buy to Open</td>
      <td>VIX 10/16/2024 40.00 P</td>
      <td>1</td>
      <td>16.35</td>
      <td>1.08</td>
      <td>1636.08</td>
      <td>42.71</td>
      <td>NaN</td>
      <td>2024-10-16</td>
      <td>40.00</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2024-09-18</td>
      <td>Sell to Close</td>
      <td>VIX 10/16/2024 40.00 P</td>
      <td>1</td>
      <td>21.54</td>
      <td>1.08</td>
      <td>2152.92</td>
      <td>18.85</td>
      <td>NaN</td>
      <td>2024-10-16</td>
      <td>40.00</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2024-08-07</td>
      <td>Buy to Open</td>
      <td>VIX 11/20/2024 25.00 P</td>
      <td>2</td>
      <td>5.90</td>
      <td>2.16</td>
      <td>1182.16</td>
      <td>27.11</td>
      <td>NaN</td>
      <td>2024-11-20</td>
      <td>25.00</td>
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
    </tr>
    <tr>
      <th>61</th>
      <td>2025-10-08</td>
      <td>Sell to Close</td>
      <td>VIX 11/19/2025 21.00 C</td>
      <td>10</td>
      <td>1.83</td>
      <td>9.31</td>
      <td>1820.69</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2025-11-19</td>
      <td>21.00</td>
    </tr>
    <tr>
      <th>62</th>
      <td>2025-09-11</td>
      <td>Buy to Open</td>
      <td>VIX 12/17/2025 17.00 C</td>
      <td>10</td>
      <td>3.90</td>
      <td>10.81</td>
      <td>3910.81</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2025-12-17</td>
      <td>17.00</td>
    </tr>
    <tr>
      <th>63</th>
      <td>2025-10-10</td>
      <td>Sell to Close</td>
      <td>VIX 12/17/2025 17.00 C</td>
      <td>10</td>
      <td>4.60</td>
      <td>10.81</td>
      <td>4589.19</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2025-12-17</td>
      <td>17.00</td>
    </tr>
    <tr>
      <th>64</th>
      <td>2025-12-19</td>
      <td>Buy to Open</td>
      <td>VIX 02/18/2026 22.00 C</td>
      <td>10</td>
      <td>1.69</td>
      <td>9.31</td>
      <td>1699.31</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2026-02-18</td>
      <td>22.00</td>
    </tr>
    <tr>
      <th>65</th>
      <td>2026-01-20</td>
      <td>Sell to Close</td>
      <td>VIX 02/18/2026 22.00 C</td>
      <td>10</td>
      <td>1.74</td>
      <td>9.31</td>
      <td>1730.69</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2026-02-18</td>
      <td>22.00</td>
    </tr>
  </tbody>
</table>
<p>66 rows × 11 columns</p>
</div>




```python
vix_transactions_no_exp = vix_transactions.drop(columns=['Exp_Date', 'Strike_Price'])
vix_transactions_no_exp
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
      <th>Trade_Date</th>
      <th>Action</th>
      <th>Symbol</th>
      <th>Quantity</th>
      <th>Price</th>
      <th>Fees &amp; Comm</th>
      <th>Amount</th>
      <th>Approx_VIX_Level</th>
      <th>Comments</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2024-08-05</td>
      <td>Buy to Open</td>
      <td>VIX 09/18/2024 34.00 P</td>
      <td>1</td>
      <td>10.95</td>
      <td>1.08</td>
      <td>1096.08</td>
      <td>34.33</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2024-08-21</td>
      <td>Sell to Close</td>
      <td>VIX 09/18/2024 34.00 P</td>
      <td>1</td>
      <td>17.95</td>
      <td>1.08</td>
      <td>1793.92</td>
      <td>16.50</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2024-08-05</td>
      <td>Buy to Open</td>
      <td>VIX 10/16/2024 40.00 P</td>
      <td>1</td>
      <td>16.35</td>
      <td>1.08</td>
      <td>1636.08</td>
      <td>42.71</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2024-09-18</td>
      <td>Sell to Close</td>
      <td>VIX 10/16/2024 40.00 P</td>
      <td>1</td>
      <td>21.54</td>
      <td>1.08</td>
      <td>2152.92</td>
      <td>18.85</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2024-08-07</td>
      <td>Buy to Open</td>
      <td>VIX 11/20/2024 25.00 P</td>
      <td>2</td>
      <td>5.90</td>
      <td>2.16</td>
      <td>1182.16</td>
      <td>27.11</td>
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
    </tr>
    <tr>
      <th>61</th>
      <td>2025-10-08</td>
      <td>Sell to Close</td>
      <td>VIX 11/19/2025 21.00 C</td>
      <td>10</td>
      <td>1.83</td>
      <td>9.31</td>
      <td>1820.69</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>62</th>
      <td>2025-09-11</td>
      <td>Buy to Open</td>
      <td>VIX 12/17/2025 17.00 C</td>
      <td>10</td>
      <td>3.90</td>
      <td>10.81</td>
      <td>3910.81</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>63</th>
      <td>2025-10-10</td>
      <td>Sell to Close</td>
      <td>VIX 12/17/2025 17.00 C</td>
      <td>10</td>
      <td>4.60</td>
      <td>10.81</td>
      <td>4589.19</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>64</th>
      <td>2025-12-19</td>
      <td>Buy to Open</td>
      <td>VIX 02/18/2026 22.00 C</td>
      <td>10</td>
      <td>1.69</td>
      <td>9.31</td>
      <td>1699.31</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>65</th>
      <td>2026-01-20</td>
      <td>Sell to Close</td>
      <td>VIX 02/18/2026 22.00 C</td>
      <td>10</td>
      <td>1.74</td>
      <td>9.31</td>
      <td>1730.69</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>66 rows × 9 columns</p>
</div>




```python
# Copy this <!-- INSERT_10_Trades_Executed_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="10_Trades_Executed.md", content=vix_transactions_no_exp.to_markdown(index=False, floatfmt=".2f"))
```

    ✅ Exported and tracked: 10_Trades_Executed.md


#### Volatility In August 2024


```python
# Variables to be modifed
esd = "2024-09-18" # Expiration Start Date
eed = "2024-12-18" # Expiration End Date
tsd = "2024-08-05" # Trade Start Date
ted = "2024-11-27" # Trade End Date
index_number = "11"
x_tick_spacing = 10
y_tick_spacing = 5

############################################
## Do not modify the code below this line ##
############################################

trades, closed_pos, open_pos, per_pnl, pnl, tot_opened_pos_mkt_val, tot_closed_pos_mkt_val = calc_vix_trade_pnl(
    transaction_df=vix_transactions,
    exp_start_date=esd,
    exp_end_date=eed,
    trade_start_date=tsd,
    trade_end_date=ted,
)

# Convert to datetime objects
tsd_dt = datetime.strptime(tsd, "%Y-%m-%d")
ted_dt = datetime.strptime(ted, "%Y-%m-%d")

# Adjust the plot start and end dates
plot_start = tsd_dt - timedelta(days=10)
plot_end = ted_dt + timedelta(days=10)

plot_vix_with_trades(
    vix_price_df=vix,
    trades_df=trades,
    plot_start_date=plot_start.strftime("%Y-%m-%d"),
    plot_end_date=plot_end.strftime("%Y-%m-%d"),
    x_tick_spacing=x_tick_spacing,
    y_tick_spacing=y_tick_spacing,
    index_number=index_number,
    export_plot=True,
)

print(f"<!-- INSERT_{index_number}_Closed_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Open_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Opened_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Closed_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_PnL_HERE -->")
print(f"<!-- INSERT_{index_number}_Percent_PnL_HERE -->")
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Closed_Positions.md", content=closed_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Open_Positions.md", content=open_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Opened_Position_Market_Value.txt", content=tot_opened_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Closed_Position_Market_Value.txt", content=tot_closed_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_PnL.txt", content=pnl)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Percent_PnL.txt", content=per_pnl)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_155_0.png)
    


    <!-- INSERT_11_Closed_Positions_HERE -->
    <!-- INSERT_11_Open_Positions_HERE -->
    <!-- INSERT_11_Total_Opened_Position_Market_Value_HERE -->
    <!-- INSERT_11_Total_Closed_Position_Market_Value_HERE -->
    <!-- INSERT_11_PnL_HERE -->
    <!-- INSERT_11_Percent_PnL_HERE -->
    ✅ Exported and tracked: 11_Closed_Positions.md
    ✅ Exported and tracked: 11_Open_Positions.md
    ✅ Exported and tracked: 11_Total_Opened_Position_Market_Value.txt
    ✅ Exported and tracked: 11_Total_Closed_Position_Market_Value.txt
    ✅ Exported and tracked: 11_PnL.txt
    ✅ Exported and tracked: 11_Percent_PnL.txt


#### Volatility In March 2025


```python
# Variables to be modifed
esd = "2025-04-16" # Expiration Start Date
eed = "2025-04-16" # Expiration End Date
tsd = "2025-03-04" # Trade Start Date
ted = "2025-03-24" # Trade End Date
index_number = "12"
x_tick_spacing = 2
y_tick_spacing = 2

############################################
## Do not modify the code below this line ##
############################################

trades, closed_pos, open_pos, per_pnl, pnl, tot_opened_pos_mkt_val, tot_closed_pos_mkt_val = calc_vix_trade_pnl(
    transaction_df=vix_transactions,
    exp_start_date=esd,
    exp_end_date=eed,
    trade_start_date=tsd,
    trade_end_date=ted,
)

# Convert to datetime objects
tsd_dt = datetime.strptime(tsd, "%Y-%m-%d")
ted_dt = datetime.strptime(ted, "%Y-%m-%d")

# Adjust the plot start and end dates
plot_start = tsd_dt - timedelta(days=10)
plot_end = ted_dt + timedelta(days=10)

plot_vix_with_trades(
    vix_price_df=vix,
    trades_df=trades,
    plot_start_date=plot_start.strftime("%Y-%m-%d"),
    plot_end_date=plot_end.strftime("%Y-%m-%d"),
    x_tick_spacing=x_tick_spacing,
    y_tick_spacing=y_tick_spacing,
    index_number=index_number,
    export_plot=True,
)

print(f"<!-- INSERT_{index_number}_Closed_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Open_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Opened_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Closed_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_PnL_HERE -->")
print(f"<!-- INSERT_{index_number}_Percent_PnL_HERE -->")
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Closed_Positions.md", content=closed_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Open_Positions.md", content=open_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Opened_Position_Market_Value.txt", content=tot_opened_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Closed_Position_Market_Value.txt", content=tot_closed_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_PnL.txt", content=pnl)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Percent_PnL.txt", content=per_pnl)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_157_0.png)
    


    <!-- INSERT_12_Closed_Positions_HERE -->
    <!-- INSERT_12_Open_Positions_HERE -->
    <!-- INSERT_12_Total_Opened_Position_Market_Value_HERE -->
    <!-- INSERT_12_Total_Closed_Position_Market_Value_HERE -->
    <!-- INSERT_12_PnL_HERE -->
    <!-- INSERT_12_Percent_PnL_HERE -->
    ✅ Exported and tracked: 12_Closed_Positions.md
    ✅ Exported and tracked: 12_Open_Positions.md
    ✅ Exported and tracked: 12_Total_Opened_Position_Market_Value.txt
    ✅ Exported and tracked: 12_Total_Closed_Position_Market_Value.txt
    ✅ Exported and tracked: 12_PnL.txt
    ✅ Exported and tracked: 12_Percent_PnL.txt


#### Volatility In April 2025


```python
# Variables to be modifed
esd = "2025-05-21" # Expiration Start Date
eed = "2025-08-20" # Expiration End Date
tsd = "2025-03-10" # Trade Start Date
ted = "2025-05-13" # Trade End Date
index_number = "13"
x_tick_spacing = 5
y_tick_spacing = 5

############################################
## Do not modify the code below this line ##
############################################

trades, closed_pos, open_pos, per_pnl, pnl, tot_opened_pos_mkt_val, tot_closed_pos_mkt_val = calc_vix_trade_pnl(
    transaction_df=vix_transactions,
    exp_start_date=esd,
    exp_end_date=eed,
    trade_start_date=tsd,
    trade_end_date=ted,
)

# Convert to datetime objects
tsd_dt = datetime.strptime(tsd, "%Y-%m-%d")
ted_dt = datetime.strptime(ted, "%Y-%m-%d")

# Adjust the plot start and end dates
plot_start = tsd_dt - timedelta(days=10)
plot_end = ted_dt + timedelta(days=10)

plot_vix_with_trades(
    vix_price_df=vix,
    trades_df=trades,
    plot_start_date=plot_start.strftime("%Y-%m-%d"),
    plot_end_date=plot_end.strftime("%Y-%m-%d"),
    x_tick_spacing=x_tick_spacing,
    y_tick_spacing=y_tick_spacing,
    index_number=index_number,
    export_plot=True,
)

print(f"<!-- INSERT_{index_number}_Closed_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Open_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Opened_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Closed_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_PnL_HERE -->")
print(f"<!-- INSERT_{index_number}_Percent_PnL_HERE -->")
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Closed_Positions.md", content=closed_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Open_Positions.md", content=open_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Opened_Position_Market_Value.txt", content=tot_opened_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Closed_Position_Market_Value.txt", content=tot_closed_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_PnL.txt", content=pnl)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Percent_PnL.txt", content=per_pnl)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_159_0.png)
    


    <!-- INSERT_13_Closed_Positions_HERE -->
    <!-- INSERT_13_Open_Positions_HERE -->
    <!-- INSERT_13_Total_Opened_Position_Market_Value_HERE -->
    <!-- INSERT_13_Total_Closed_Position_Market_Value_HERE -->
    <!-- INSERT_13_PnL_HERE -->
    <!-- INSERT_13_Percent_PnL_HERE -->
    ✅ Exported and tracked: 13_Closed_Positions.md
    ✅ Exported and tracked: 13_Open_Positions.md
    ✅ Exported and tracked: 13_Total_Opened_Position_Market_Value.txt
    ✅ Exported and tracked: 13_Total_Closed_Position_Market_Value.txt
    ✅ Exported and tracked: 13_PnL.txt
    ✅ Exported and tracked: 13_Percent_PnL.txt


#### Low Volatility In June, July, August, September, October, November 2025


```python
# Variables to be modifed
esd = "2025-09-17" # Expiration Start Date
eed = "2025-12-31" # Expiration End Date
tsd = "2025-06-26" # Trade Start Date
ted = "2025-12-31"  # Trade End Date
index_number = "14"
x_tick_spacing = 5
y_tick_spacing = 1

############################################
## Do not modify the code below this line ##
############################################

trades, closed_pos, open_pos, per_pnl, pnl, tot_opened_pos_mkt_val, tot_closed_pos_mkt_val = calc_vix_trade_pnl(
    transaction_df=vix_transactions,
    exp_start_date=esd,
    exp_end_date=eed,
    trade_start_date=tsd,
    trade_end_date=ted,
)

# Convert to datetime objects
tsd_dt = datetime.strptime(tsd, "%Y-%m-%d")
ted_dt = datetime.strptime(ted, "%Y-%m-%d")

# Adjust the plot start and end dates
plot_start = tsd_dt - timedelta(days=10)
plot_end = ted_dt + timedelta(days=10)

plot_vix_with_trades(
    vix_price_df=vix,
    trades_df=trades,
    plot_start_date=plot_start.strftime("%Y-%m-%d"),
    plot_end_date=plot_end.strftime("%Y-%m-%d"),
    x_tick_spacing=x_tick_spacing,
    y_tick_spacing=y_tick_spacing,
    index_number=index_number,
    export_plot=True,
)

print(f"<!-- INSERT_{index_number}_Closed_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Open_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Opened_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Closed_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_PnL_HERE -->")
print(f"<!-- INSERT_{index_number}_Percent_PnL_HERE -->")
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Closed_Positions.md", content=closed_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Open_Positions.md", content=open_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Opened_Position_Market_Value.txt", content=tot_opened_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Closed_Position_Market_Value.txt", content=tot_closed_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_PnL.txt", content=pnl)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Percent_PnL.txt", content=per_pnl)
```


    
![png](investigating-a-vix-trading-signal-part-1-vix-and-vvix_files/investigating-a-vix-trading-signal-part-1-vix-and-vvix_161_0.png)
    


    <!-- INSERT_14_Closed_Positions_HERE -->
    <!-- INSERT_14_Open_Positions_HERE -->
    <!-- INSERT_14_Total_Opened_Position_Market_Value_HERE -->
    <!-- INSERT_14_Total_Closed_Position_Market_Value_HERE -->
    <!-- INSERT_14_PnL_HERE -->
    <!-- INSERT_14_Percent_PnL_HERE -->
    ✅ Exported and tracked: 14_Closed_Positions.md
    ✅ Exported and tracked: 14_Open_Positions.md
    ✅ Exported and tracked: 14_Total_Opened_Position_Market_Value.txt
    ✅ Exported and tracked: 14_Total_Closed_Position_Market_Value.txt
    ✅ Exported and tracked: 14_PnL.txt
    ✅ Exported and tracked: 14_Percent_PnL.txt


#### Complete Trade History


```python
# Variables to be modifed
esd = None
eed = None
tsd = None
ted = None
index_number = "99"

############################################
## Do not modify the code below this line ##
############################################

trades, closed_pos, open_pos, per_pnl, pnl, tot_opened_pos_mkt_val, tot_closed_pos_mkt_val = calc_vix_trade_pnl(
    transaction_df=vix_transactions,
    exp_start_date=esd,
    exp_end_date=eed,
    trade_start_date=tsd,
    trade_end_date=ted,
)

print(f"<!-- INSERT_{index_number}_Closed_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Open_Positions_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Opened_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_Total_Closed_Position_Market_Value_HERE -->")
print(f"<!-- INSERT_{index_number}_PnL_HERE -->")
print(f"<!-- INSERT_{index_number}_Percent_PnL_HERE -->")
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Closed_Positions.md", content=closed_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Open_Positions.md", content=open_pos.to_markdown(index=False, floatfmt=".2f"))
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Opened_Position_Market_Value.txt", content=tot_opened_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Total_Closed_Position_Market_Value.txt", content=tot_closed_pos_mkt_val)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_PnL.txt", content=pnl)
export_track_md_deps(dep_file=dep_file, md_filename=f"{index_number}_Percent_PnL.txt", content=per_pnl)
```

    <!-- INSERT_99_Closed_Positions_HERE -->
    <!-- INSERT_99_Open_Positions_HERE -->
    <!-- INSERT_99_Total_Opened_Position_Market_Value_HERE -->
    <!-- INSERT_99_Total_Closed_Position_Market_Value_HERE -->
    <!-- INSERT_99_PnL_HERE -->
    <!-- INSERT_99_Percent_PnL_HERE -->
    ✅ Exported and tracked: 99_Closed_Positions.md
    ✅ Exported and tracked: 99_Open_Positions.md
    ✅ Exported and tracked: 99_Total_Opened_Position_Market_Value.txt
    ✅ Exported and tracked: 99_Total_Closed_Position_Market_Value.txt
    ✅ Exported and tracked: 99_PnL.txt
    ✅ Exported and tracked: 99_Percent_PnL.txt

