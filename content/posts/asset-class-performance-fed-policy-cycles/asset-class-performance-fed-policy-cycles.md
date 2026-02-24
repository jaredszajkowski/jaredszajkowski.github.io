## Introduction

In this post, we will look into the Fed Funds cycles and evaluate asset class performance during tightening and easing of monetary policy.

## Python Imports


```python
# Standard Library
import datetime
import os
import sys
import warnings

from datetime import datetime
from pathlib import Path

# Data Handling
import numpy as np
import pandas as pd

# Data Sources
import pandas_datareader.data as web

# Statistical Analysis
import statsmodels.api as sm

# Machine Learning
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

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

* [bb_clean_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#bb_clean_data): Takes an Excel export from Bloomberg, removes the miscellaneous headings/rows, and returns a DataFrame.
* [calc_fed_cycle_asset_performance](/posts/reusable-extensible-python-functions-financial-data-analysis/#calc_fed_cycle_asset_performance): Calculates metrics for an asset based on a specified Fed tightening/loosening cycle.
* [load_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.
* [pandas_set_decimal_places](/posts/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.
* [plot_bar_returns_ffr_change](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_bar_returns_ffr_change): Plot the bar chart of the cumulative or annualized returns for the asset class along with the change in the Fed Funds Rate.
* [plot_scatter_regression_ffr_vs_returns](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_scatter_regression_ffr_vs_returns): Plot the scatter plot and regression of the annualized return for the asset class along with the annualized change in the Fed Funds Rate.
* [plot_timeseries](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_timeseries): Plot the timeseries data from a DataFrame for a specified date range and columns.
* [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.


```python
from bb_clean_data import bb_clean_data
from calc_fed_cycle_asset_performance import calc_fed_cycle_asset_performance
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_bar_returns_ffr_change import plot_bar_returns_ffr_change
from plot_scatter_regression_ffr_vs_returns import plot_scatter_regression_ffr_vs_returns
from plot_timeseries import plot_timeseries
from summary_stats import summary_stats
```

## Data Overview

### Acquire & Plot Fed Funds Data

First, let's get the data for the Fed Funds target rate (FFR). This data is found in 3 different datasets from FRED.


```python
# Set decimal places
pandas_set_decimal_places(5)

# Pull Federal Funds Target Rate (DISCONTINUED) (DFEDTAR)
fedfunds_target_old = web.DataReader("DFEDTAR", "fred", start="1900-01-01", end=datetime.today())

# Pull Federal Funds Target Range - Upper Limit (DFEDTARU)
fedfunds_target_new_upper = web.DataReader("DFEDTARU", "fred", start="1900-01-01", end=datetime.today())

# Pull Federal Funds Target Range - Lower Limit (DFEDTARL)
fedfunds_target_new_lower = web.DataReader("DFEDTARL", "fred", start="1900-01-01", end=datetime.today())

# Merge the datasets together
fedfunds_combined = pd.concat([fedfunds_target_old, fedfunds_target_new_upper, fedfunds_target_new_lower], axis=1)

# Divide all values by 100 to get decimal rates
for col in fedfunds_combined.columns:
    fedfunds_combined[col] = fedfunds_combined[col] / 100

# Resample to month-end (as if we know the rate at the end of the month)
fedfunds_monthly = fedfunds_combined.resample("ME").last()

display(fedfunds_monthly)
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
      <th>DFEDTAR</th>
      <th>DFEDTARU</th>
      <th>DFEDTARL</th>
    </tr>
    <tr>
      <th>DATE</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1982-09-30</th>
      <td>0.10250</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1982-10-31</th>
      <td>0.09500</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1982-11-30</th>
      <td>0.09000</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1982-12-31</th>
      <td>0.08500</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1983-01-31</th>
      <td>0.08500</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2025-10-31</th>
      <td>NaN</td>
      <td>0.04000</td>
      <td>0.03750</td>
    </tr>
    <tr>
      <th>2025-11-30</th>
      <td>NaN</td>
      <td>0.04000</td>
      <td>0.03750</td>
    </tr>
    <tr>
      <th>2025-12-31</th>
      <td>NaN</td>
      <td>0.03750</td>
      <td>0.03500</td>
    </tr>
    <tr>
      <th>2026-01-31</th>
      <td>NaN</td>
      <td>0.03750</td>
      <td>0.03500</td>
    </tr>
    <tr>
      <th>2026-02-28</th>
      <td>NaN</td>
      <td>0.03750</td>
      <td>0.03500</td>
    </tr>
  </tbody>
</table>
<p>522 rows × 3 columns</p>
</div>


We can then generate several useful plots. First, the Fed Funds target rate:


```python
plot_timeseries(
    price_df=fedfunds_monthly,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["DFEDTAR", "DFEDTARU", "DFEDTARL"],
    title="Fed Funds Target Rate",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_rotation=45,
    y_label="Rate (%)",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing=0.01,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_10_0.png)
    



```python
# First drop the lower column and merge
fedfunds_monthly["fed_funds"] = fedfunds_monthly["DFEDTAR"].combine_first(fedfunds_monthly["DFEDTARU"])
fedfunds_monthly = fedfunds_monthly.drop(columns=["DFEDTARL", "DFEDTARU", "DFEDTAR"])

# Compute change in rate from either column
fedfunds_monthly["fed_funds_change"] = fedfunds_monthly["fed_funds"].diff()

display(fedfunds_monthly)
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
      <th>fed_funds</th>
      <th>fed_funds_change</th>
    </tr>
    <tr>
      <th>DATE</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1982-09-30</th>
      <td>0.10250</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1982-10-31</th>
      <td>0.09500</td>
      <td>-0.00750</td>
    </tr>
    <tr>
      <th>1982-11-30</th>
      <td>0.09000</td>
      <td>-0.00500</td>
    </tr>
    <tr>
      <th>1982-12-31</th>
      <td>0.08500</td>
      <td>-0.00500</td>
    </tr>
    <tr>
      <th>1983-01-31</th>
      <td>0.08500</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2025-10-31</th>
      <td>0.04000</td>
      <td>-0.00250</td>
    </tr>
    <tr>
      <th>2025-11-30</th>
      <td>0.04000</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>2025-12-31</th>
      <td>0.03750</td>
      <td>-0.00250</td>
    </tr>
    <tr>
      <th>2026-01-31</th>
      <td>0.03750</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>2026-02-28</th>
      <td>0.03750</td>
      <td>0.00000</td>
    </tr>
  </tbody>
</table>
<p>522 rows × 2 columns</p>
</div>


And then the change in FFR from month-to-month:


```python
plot_timeseries(
    price_df=fedfunds_monthly,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["fed_funds_change"],
    title="Fed Funds Change In Rate",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_rotation=45,
    y_label="Rate Change (%)",
    y_format="Percentage",
    y_format_decimal_places=2,
    y_tick_spacing=0.0025,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_13_0.png)
    


This plot, in particular, makes it easy to show the monthly increase and decrease in the FFR, as well as the magnitude of the change (i.e. slow, drawn-out increases or decreases or abrupt large increases or decreases).

### Define Fed Policy Cycles

Next, we will define the Fed policy tightening and easing cycles:


```python
# Set timeframe
start_date = "1989-12-15"
end_date = "2026-01-31"

# Copy DataFrame to avoid modifying original
fedfunds_cycles = fedfunds_monthly.copy()
fedfunds_cycles = fedfunds_cycles.loc[start_date:end_date]

# Reset index
fedfunds_cycles = fedfunds_cycles.reset_index()

# Drop the "fed_funds_change" column as we will use it to determine the cycle type later, but we don't need it in the final dataframe
fedfunds_cycles = fedfunds_cycles.drop(columns=["fed_funds_change"])

# Rename the date column to "Start Date", and the "fed_funds" column to "Fed Funds Start"
fedfunds_cycles = fedfunds_cycles.rename(columns={"DATE": "start_date", "fed_funds": "fed_funds_start"})

# Copy the "Start Date" column to a new column called "End Date" and shift it up by one row
fedfunds_cycles["end_date"] = fedfunds_cycles["start_date"].shift(-1)

# Copy the "Fed Funds Start" column to a new column called "Fed Funds End" and shift it up by one row
fedfunds_cycles["fed_funds_end"] = fedfunds_cycles["fed_funds_start"].shift(-1)

# Calculate the change in Fed Funds rate for each cycle
fedfunds_cycles["fed_funds_change"] = fedfunds_cycles["fed_funds_end"] - fedfunds_cycles["fed_funds_start"]

# Based on "Fed Funds Change" column, determine if the rate is increasing, decreasing, or unchanged
fedfunds_cycles["cycle"] = fedfunds_cycles["fed_funds_change"].apply(
    lambda x: "Tightening" if x > 0 else ("Easing" if x < 0 else "Neutral"))

display(fedfunds_cycles)
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
      <th>start_date</th>
      <th>fed_funds_start</th>
      <th>end_date</th>
      <th>fed_funds_end</th>
      <th>fed_funds_change</th>
      <th>cycle</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1989-12-31</td>
      <td>0.08250</td>
      <td>1990-01-31</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1990-01-31</td>
      <td>0.08250</td>
      <td>1990-02-28</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1990-02-28</td>
      <td>0.08250</td>
      <td>1990-03-31</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1990-03-31</td>
      <td>0.08250</td>
      <td>1990-04-30</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1990-04-30</td>
      <td>0.08250</td>
      <td>1990-05-31</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
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
      <th>429</th>
      <td>2025-09-30</td>
      <td>0.04250</td>
      <td>2025-10-31</td>
      <td>0.04000</td>
      <td>-0.00250</td>
      <td>Easing</td>
    </tr>
    <tr>
      <th>430</th>
      <td>2025-10-31</td>
      <td>0.04000</td>
      <td>2025-11-30</td>
      <td>0.04000</td>
      <td>0.00000</td>
      <td>Neutral</td>
    </tr>
    <tr>
      <th>431</th>
      <td>2025-11-30</td>
      <td>0.04000</td>
      <td>2025-12-31</td>
      <td>0.03750</td>
      <td>-0.00250</td>
      <td>Easing</td>
    </tr>
    <tr>
      <th>432</th>
      <td>2025-12-31</td>
      <td>0.03750</td>
      <td>2026-01-31</td>
      <td>0.03750</td>
      <td>0.00000</td>
      <td>Neutral</td>
    </tr>
    <tr>
      <th>433</th>
      <td>2026-01-31</td>
      <td>0.03750</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>Neutral</td>
    </tr>
  </tbody>
</table>
<p>434 rows × 6 columns</p>
</div>


Grouping the consecutive months of tightening and easing together, we can create a DataFrame that gives us the cumulative change in the FFR for each cycle, as well as the start and end dates for each cycle. This will be useful for evaluating asset class performance during these cycles.


```python
fedfunds_grouped_cycles = fedfunds_cycles.copy()

# Create a group key that increments whenever the Cycle value changes
fedfunds_grouped_cycles['group'] = (fedfunds_grouped_cycles['cycle'] != fedfunds_grouped_cycles['cycle'].shift(1)).cumsum()

# Group by both the group key and Cycle label
cycle_ranges = (
    fedfunds_grouped_cycles.groupby(['group', 'cycle'], sort=False)
    .agg(
        start_date=('start_date', 'first'),
        end_date=('end_date', 'last'),
        fed_funds_start=('fed_funds_start', 'first'),
        fed_funds_end=('fed_funds_end', 'last')
    )
    .reset_index(drop=False)
    .drop(columns='group')
)

display(cycle_ranges)
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
      <th>cycle</th>
      <th>start_date</th>
      <th>end_date</th>
      <th>fed_funds_start</th>
      <th>fed_funds_end</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Neutral</td>
      <td>1989-12-31</td>
      <td>1990-06-30</td>
      <td>0.08250</td>
      <td>0.08250</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Easing</td>
      <td>1990-06-30</td>
      <td>1990-07-31</td>
      <td>0.08250</td>
      <td>0.08000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Neutral</td>
      <td>1990-07-31</td>
      <td>1990-09-30</td>
      <td>0.08000</td>
      <td>0.08000</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Easing</td>
      <td>1990-09-30</td>
      <td>1991-04-30</td>
      <td>0.08000</td>
      <td>0.05750</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Neutral</td>
      <td>1991-04-30</td>
      <td>1991-07-31</td>
      <td>0.05750</td>
      <td>0.05750</td>
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
      <th>116</th>
      <td>Neutral</td>
      <td>2024-12-31</td>
      <td>2025-08-31</td>
      <td>0.04500</td>
      <td>0.04500</td>
    </tr>
    <tr>
      <th>117</th>
      <td>Easing</td>
      <td>2025-08-31</td>
      <td>2025-10-31</td>
      <td>0.04500</td>
      <td>0.04000</td>
    </tr>
    <tr>
      <th>118</th>
      <td>Neutral</td>
      <td>2025-10-31</td>
      <td>2025-11-30</td>
      <td>0.04000</td>
      <td>0.04000</td>
    </tr>
    <tr>
      <th>119</th>
      <td>Easing</td>
      <td>2025-11-30</td>
      <td>2025-12-31</td>
      <td>0.04000</td>
      <td>0.03750</td>
    </tr>
    <tr>
      <th>120</th>
      <td>Neutral</td>
      <td>2025-12-31</td>
      <td>2026-01-31</td>
      <td>0.03750</td>
      <td>0.03750</td>
    </tr>
  </tbody>
</table>
<p>121 rows × 5 columns</p>
</div>


Furthermore, we will make the assumption that any "Neutral" months (i.e. months where the FFR did not change) are part of the preceding cycle -- to a point. For example, if we have a tightening month followed by a neutral month, we will consider the neutral month to be part of the tightening cycle. This is a simplifying assumption, but it allows us to categorize all months into either tightening or easing cycles without having to create a separate category for neutral months. From a practical standpoint, this also makes it easier to evaluate asset class performance during these cycles, as we can simply look at the performance during the tightening and easing cycles without having to worry about the neutral months. We will foward fill no more than 6 months of neutral months, however, as it would be unreasonable to assume that a month of neutral policy is part of the preceding cycle if it has been 6 months since the last change in policy.


```python
fedfunds_grouped_cycles = fedfunds_cycles.copy()

# Forward fill cycle labels preceding "Neutral" cycles
fedfunds_grouped_cycles['cycle_filled'] = fedfunds_grouped_cycles['cycle'].replace('Neutral', pd.NA).ffill(limit=6)

# Replaced any remaining <NA> values with "Modified Tightening"
fedfunds_grouped_cycles['cycle_filled'] = fedfunds_grouped_cycles['cycle_filled'].fillna('Modified Tightening')

# Create a group key that increments whenever the Cycle value changes
fedfunds_grouped_cycles['group'] = (fedfunds_grouped_cycles['cycle_filled'] != fedfunds_grouped_cycles['cycle_filled'].shift(1)).cumsum()

# Group by both the group key and Cycle label
cycle_ranges = (
    fedfunds_grouped_cycles.groupby(['group', 'cycle_filled'], sort=False)
    .agg(
        start_date=('start_date', 'first'),
        end_date=('end_date', 'last'),
        fed_funds_start=('fed_funds_start', 'first'),
        fed_funds_end=('fed_funds_end', 'last')
    )
    .reset_index(drop=False)
    .drop(columns='group')
)

# Calc change in Fed Funds rate for each cycle
cycle_ranges["fed_funds_change"] = cycle_ranges["fed_funds_end"] - cycle_ranges["fed_funds_start"]

# Add cycle labels
cycle_labels = [f"Cycle {i+1}" for i in range(len(cycle_ranges))]

# Combine labels with cycle_ranges
cycle_ranges['cycle_label'] = cycle_labels

display(cycle_ranges)
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
      <th>cycle_filled</th>
      <th>start_date</th>
      <th>end_date</th>
      <th>fed_funds_start</th>
      <th>fed_funds_end</th>
      <th>fed_funds_change</th>
      <th>cycle_label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Modified Tightening</td>
      <td>1989-12-31</td>
      <td>1990-06-30</td>
      <td>0.08250</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Cycle 1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Easing</td>
      <td>1990-06-30</td>
      <td>1993-03-31</td>
      <td>0.08250</td>
      <td>0.03000</td>
      <td>-0.05250</td>
      <td>Cycle 2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Modified Tightening</td>
      <td>1993-03-31</td>
      <td>1994-01-31</td>
      <td>0.03000</td>
      <td>0.03000</td>
      <td>0.00000</td>
      <td>Cycle 3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Tightening</td>
      <td>1994-01-31</td>
      <td>1995-06-30</td>
      <td>0.03000</td>
      <td>0.06000</td>
      <td>0.03000</td>
      <td>Cycle 4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Easing</td>
      <td>1995-06-30</td>
      <td>1996-07-31</td>
      <td>0.06000</td>
      <td>0.05250</td>
      <td>-0.00750</td>
      <td>Cycle 5</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Modified Tightening</td>
      <td>1996-07-31</td>
      <td>1997-02-28</td>
      <td>0.05250</td>
      <td>0.05250</td>
      <td>0.00000</td>
      <td>Cycle 6</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Tightening</td>
      <td>1997-02-28</td>
      <td>1997-09-30</td>
      <td>0.05250</td>
      <td>0.05500</td>
      <td>0.00250</td>
      <td>Cycle 7</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Modified Tightening</td>
      <td>1997-09-30</td>
      <td>1998-08-31</td>
      <td>0.05500</td>
      <td>0.05500</td>
      <td>0.00000</td>
      <td>Cycle 8</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Easing</td>
      <td>1998-08-31</td>
      <td>1999-05-31</td>
      <td>0.05500</td>
      <td>0.04750</td>
      <td>-0.00750</td>
      <td>Cycle 9</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Tightening</td>
      <td>1999-05-31</td>
      <td>2000-11-30</td>
      <td>0.04750</td>
      <td>0.06500</td>
      <td>0.01750</td>
      <td>Cycle 10</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Modified Tightening</td>
      <td>2000-11-30</td>
      <td>2000-12-31</td>
      <td>0.06500</td>
      <td>0.06500</td>
      <td>0.00000</td>
      <td>Cycle 11</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Easing</td>
      <td>2000-12-31</td>
      <td>2002-06-30</td>
      <td>0.06500</td>
      <td>0.01750</td>
      <td>-0.04750</td>
      <td>Cycle 12</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Modified Tightening</td>
      <td>2002-06-30</td>
      <td>2002-10-31</td>
      <td>0.01750</td>
      <td>0.01750</td>
      <td>0.00000</td>
      <td>Cycle 13</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Easing</td>
      <td>2002-10-31</td>
      <td>2003-12-31</td>
      <td>0.01750</td>
      <td>0.01000</td>
      <td>-0.00750</td>
      <td>Cycle 14</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Modified Tightening</td>
      <td>2003-12-31</td>
      <td>2004-05-31</td>
      <td>0.01000</td>
      <td>0.01000</td>
      <td>0.00000</td>
      <td>Cycle 15</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Tightening</td>
      <td>2004-05-31</td>
      <td>2006-12-31</td>
      <td>0.01000</td>
      <td>0.05250</td>
      <td>0.04250</td>
      <td>Cycle 16</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Modified Tightening</td>
      <td>2006-12-31</td>
      <td>2007-08-31</td>
      <td>0.05250</td>
      <td>0.05250</td>
      <td>0.00000</td>
      <td>Cycle 17</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Easing</td>
      <td>2007-08-31</td>
      <td>2009-07-31</td>
      <td>0.05250</td>
      <td>0.00250</td>
      <td>-0.05000</td>
      <td>Cycle 18</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Modified Tightening</td>
      <td>2009-07-31</td>
      <td>2015-11-30</td>
      <td>0.00250</td>
      <td>0.00250</td>
      <td>0.00000</td>
      <td>Cycle 19</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Tightening</td>
      <td>2015-11-30</td>
      <td>2016-06-30</td>
      <td>0.00250</td>
      <td>0.00500</td>
      <td>0.00250</td>
      <td>Cycle 20</td>
    </tr>
    <tr>
      <th>20</th>
      <td>Modified Tightening</td>
      <td>2016-06-30</td>
      <td>2016-11-30</td>
      <td>0.00500</td>
      <td>0.00500</td>
      <td>0.00000</td>
      <td>Cycle 21</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Tightening</td>
      <td>2016-11-30</td>
      <td>2019-06-30</td>
      <td>0.00500</td>
      <td>0.02500</td>
      <td>0.02000</td>
      <td>Cycle 22</td>
    </tr>
    <tr>
      <th>22</th>
      <td>Modified Tightening</td>
      <td>2019-06-30</td>
      <td>2019-07-31</td>
      <td>0.02500</td>
      <td>0.02500</td>
      <td>0.00000</td>
      <td>Cycle 23</td>
    </tr>
    <tr>
      <th>23</th>
      <td>Easing</td>
      <td>2019-07-31</td>
      <td>2020-09-30</td>
      <td>0.02500</td>
      <td>0.00250</td>
      <td>-0.02250</td>
      <td>Cycle 24</td>
    </tr>
    <tr>
      <th>24</th>
      <td>Modified Tightening</td>
      <td>2020-09-30</td>
      <td>2022-02-28</td>
      <td>0.00250</td>
      <td>0.00250</td>
      <td>0.00000</td>
      <td>Cycle 25</td>
    </tr>
    <tr>
      <th>25</th>
      <td>Tightening</td>
      <td>2022-02-28</td>
      <td>2024-01-31</td>
      <td>0.00250</td>
      <td>0.05500</td>
      <td>0.05250</td>
      <td>Cycle 26</td>
    </tr>
    <tr>
      <th>26</th>
      <td>Modified Tightening</td>
      <td>2024-01-31</td>
      <td>2024-08-31</td>
      <td>0.05500</td>
      <td>0.05500</td>
      <td>0.00000</td>
      <td>Cycle 27</td>
    </tr>
    <tr>
      <th>27</th>
      <td>Easing</td>
      <td>2024-08-31</td>
      <td>2025-06-30</td>
      <td>0.05500</td>
      <td>0.04500</td>
      <td>-0.01000</td>
      <td>Cycle 28</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Modified Tightening</td>
      <td>2025-06-30</td>
      <td>2025-08-31</td>
      <td>0.04500</td>
      <td>0.04500</td>
      <td>0.00000</td>
      <td>Cycle 29</td>
    </tr>
    <tr>
      <th>29</th>
      <td>Easing</td>
      <td>2025-08-31</td>
      <td>2026-01-31</td>
      <td>0.04500</td>
      <td>0.03750</td>
      <td>-0.00750</td>
      <td>Cycle 30</td>
    </tr>
  </tbody>
</table>
</div>


## Return Performance By Fed Policy Cycle

Moving on, we will now look at the performance of four (4) different asset classes during each Fed cycle. We'll use the following Bloomberg indices:

* SPXT_S&P 500 Total Return Index (Stocks)
* SPBDU10T_S&P US Treasury Bond 7-10 Year Total Return Index (Bonds)
* LF98TRUU_Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD (High Yield Bonds)
* XAU_Gold USD Spot (Gold)

### Stocks

First, we will clean and load the data for the S&P 500 Total Return Index (SPXT):


```python
bb_clean_data(
    base_directory=DATA_DIR,
    fund_ticker_name="SPXT_S&P 500 Total Return Index",
    source="Bloomberg",
    asset_class="Indices",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

spxt = load_data(
    base_directory=DATA_DIR,
    ticker="SPXT_S&P 500 Total Return Index_Clean",
    source="Bloomberg", 
    asset_class="Indices",
    timeframe="Daily",
    file_format="pickle",
)

# Filter SPXT to date range
spxt = spxt[(spxt.index >= pd.to_datetime(start_date)) & (spxt.index <= pd.to_datetime(end_date))]

# Drop everything except the "close" column
spxt = spxt[["Close"]]

# Resample to monthly frequency
spxt_monthly = spxt.resample("M").last()
spxt_monthly["Monthly_Return"] = spxt_monthly["Close"].pct_change()
spxt_monthly = spxt_monthly.dropna()

display(spxt_monthly)
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
      <th>Monthly_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1990-01-31</th>
      <td>353.94000</td>
      <td>-0.06713</td>
    </tr>
    <tr>
      <th>1990-02-28</th>
      <td>358.50000</td>
      <td>0.01288</td>
    </tr>
    <tr>
      <th>1990-03-31</th>
      <td>368</td>
      <td>0.02650</td>
    </tr>
    <tr>
      <th>1990-04-30</th>
      <td>358.81000</td>
      <td>-0.02497</td>
    </tr>
    <tr>
      <th>1990-05-31</th>
      <td>393.80000</td>
      <td>0.09752</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2025-09-30</th>
      <td>14826.80000</td>
      <td>0.03650</td>
    </tr>
    <tr>
      <th>2025-10-31</th>
      <td>15173.95000</td>
      <td>0.02341</td>
    </tr>
    <tr>
      <th>2025-11-30</th>
      <td>15211.14000</td>
      <td>0.00245</td>
    </tr>
    <tr>
      <th>2025-12-31</th>
      <td>15220.45000</td>
      <td>0.00061</td>
    </tr>
    <tr>
      <th>2026-01-31</th>
      <td>15441.15000</td>
      <td>0.01450</td>
    </tr>
  </tbody>
</table>
<p>433 rows × 2 columns</p>
</div>


Next, we can plot the price history before calculating the cycle performance:


```python
plot_timeseries(
    price_df=spxt,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["Close"],
    title="S&P 500 Total Return Index Daily Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_rotation=45,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=1000,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_24_0.png)
    


Next, we will calculate the performance for SPY based on the pre-defined Fed cycles:


```python
spxt_cycles = calc_fed_cycle_asset_performance(
    start_date=cycle_ranges["start_date"],
    end_date=cycle_ranges["end_date"],
    label=cycle_ranges["cycle_label"],
    fed_funds_change=cycle_ranges["fed_funds_change"],
    monthly_returns=spxt_monthly,
)

display(spxt_cycles)
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
      <th>Cycle</th>
      <th>Start</th>
      <th>End</th>
      <th>Months</th>
      <th>CumulativeReturn</th>
      <th>CumulativeReturnPct</th>
      <th>AverageMonthlyReturn</th>
      <th>AverageMonthlyReturnPct</th>
      <th>AnnualizedReturn</th>
      <th>AnnualizedReturnPct</th>
      <th>Volatility</th>
      <th>FedFundsChange</th>
      <th>FedFundsChange_bps</th>
      <th>FFR_AnnualizedChange</th>
      <th>FFR_AnnualizedChange_bps</th>
      <th>Label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Cycle 1</td>
      <td>1989-12-31</td>
      <td>1990-06-30</td>
      <td>6</td>
      <td>0.03092</td>
      <td>3.09164</td>
      <td>0.00634</td>
      <td>0.63403</td>
      <td>0.06279</td>
      <td>6.27887</td>
      <td>0.19170</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 1, 1989-12-31 to 1990-06-30</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Cycle 2</td>
      <td>1990-06-30</td>
      <td>1993-03-31</td>
      <td>34</td>
      <td>0.36800</td>
      <td>36.80041</td>
      <td>0.00996</td>
      <td>0.99573</td>
      <td>0.11694</td>
      <td>11.69426</td>
      <td>0.13198</td>
      <td>-0.05250</td>
      <td>-525.00000</td>
      <td>-0.01853</td>
      <td>-185.29412</td>
      <td>Cycle 2, 1990-06-30 to 1993-03-31</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Cycle 3</td>
      <td>1993-03-31</td>
      <td>1994-01-31</td>
      <td>11</td>
      <td>0.11359</td>
      <td>11.35920</td>
      <td>0.01001</td>
      <td>1.00089</td>
      <td>0.12454</td>
      <td>12.45375</td>
      <td>0.06918</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 3, 1993-03-31 to 1994-01-31</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Cycle 4</td>
      <td>1994-01-31</td>
      <td>1995-06-30</td>
      <td>18</td>
      <td>0.21800</td>
      <td>21.80042</td>
      <td>0.01141</td>
      <td>1.14060</td>
      <td>0.14051</td>
      <td>14.05103</td>
      <td>0.09928</td>
      <td>0.03000</td>
      <td>300.00000</td>
      <td>0.02000</td>
      <td>200.00000</td>
      <td>Cycle 4, 1994-01-31 to 1995-06-30</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Cycle 5</td>
      <td>1995-06-30</td>
      <td>1996-07-31</td>
      <td>14</td>
      <td>0.23230</td>
      <td>23.23023</td>
      <td>0.01527</td>
      <td>1.52704</td>
      <td>0.19607</td>
      <td>19.60729</td>
      <td>0.07840</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00643</td>
      <td>-64.28571</td>
      <td>Cycle 5, 1995-06-30 to 1996-07-31</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Cycle 6</td>
      <td>1996-07-31</td>
      <td>1997-02-28</td>
      <td>8</td>
      <td>0.19592</td>
      <td>19.59152</td>
      <td>0.02336</td>
      <td>2.33576</td>
      <td>0.30783</td>
      <td>30.78278</td>
      <td>0.14361</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 6, 1996-07-31 to 1997-02-28</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Cycle 7</td>
      <td>1997-02-28</td>
      <td>1997-09-30</td>
      <td>8</td>
      <td>0.22017</td>
      <td>22.01713</td>
      <td>0.02631</td>
      <td>2.63056</td>
      <td>0.34782</td>
      <td>34.78178</td>
      <td>0.17547</td>
      <td>0.00250</td>
      <td>25.00000</td>
      <td>0.00375</td>
      <td>37.50000</td>
      <td>Cycle 7, 1997-02-28 to 1997-09-30</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Cycle 8</td>
      <td>1997-09-30</td>
      <td>1998-08-31</td>
      <td>12</td>
      <td>0.08094</td>
      <td>8.09434</td>
      <td>0.00812</td>
      <td>0.81242</td>
      <td>0.08094</td>
      <td>8.09434</td>
      <td>0.20028</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 8, 1997-09-30 to 1998-08-31</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Cycle 9</td>
      <td>1998-08-31</td>
      <td>1999-05-31</td>
      <td>10</td>
      <td>0.17553</td>
      <td>17.55334</td>
      <td>0.01849</td>
      <td>1.84915</td>
      <td>0.21418</td>
      <td>21.41769</td>
      <td>0.23543</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00900</td>
      <td>-90.00000</td>
      <td>Cycle 9, 1998-08-31 to 1999-05-31</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Cycle 10</td>
      <td>1999-05-31</td>
      <td>2000-11-30</td>
      <td>19</td>
      <td>0.00401</td>
      <td>0.40140</td>
      <td>0.00127</td>
      <td>0.12700</td>
      <td>0.00253</td>
      <td>0.25333</td>
      <td>0.16483</td>
      <td>0.01750</td>
      <td>175.00000</td>
      <td>0.01105</td>
      <td>110.52632</td>
      <td>Cycle 10, 1999-05-31 to 2000-11-30</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Cycle 11</td>
      <td>2000-11-30</td>
      <td>2000-12-31</td>
      <td>2</td>
      <td>-0.07433</td>
      <td>-7.43308</td>
      <td>-0.03697</td>
      <td>-3.69725</td>
      <td>-0.37088</td>
      <td>-37.08781</td>
      <td>0.20511</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 11, 2000-11-30 to 2000-12-31</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Cycle 12</td>
      <td>2000-12-31</td>
      <td>2002-06-30</td>
      <td>19</td>
      <td>-0.23106</td>
      <td>-23.10629</td>
      <td>-0.01254</td>
      <td>-1.25394</td>
      <td>-0.15291</td>
      <td>-15.29071</td>
      <td>0.17313</td>
      <td>-0.04750</td>
      <td>-475.00000</td>
      <td>-0.03000</td>
      <td>-300.00000</td>
      <td>Cycle 12, 2000-12-31 to 2002-06-30</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Cycle 13</td>
      <td>2002-06-30</td>
      <td>2002-10-31</td>
      <td>5</td>
      <td>-0.16407</td>
      <td>-16.40672</td>
      <td>-0.03266</td>
      <td>-3.26564</td>
      <td>-0.34955</td>
      <td>-34.95539</td>
      <td>0.27616</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 13, 2002-06-30 to 2002-10-31</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Cycle 14</td>
      <td>2002-10-31</td>
      <td>2003-12-31</td>
      <td>15</td>
      <td>0.39543</td>
      <td>39.54292</td>
      <td>0.02325</td>
      <td>2.32521</td>
      <td>0.30547</td>
      <td>30.54681</td>
      <td>0.14377</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00600</td>
      <td>-60.00000</td>
      <td>Cycle 14, 2002-10-31 to 2003-12-31</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Cycle 15</td>
      <td>2003-12-31</td>
      <td>2004-05-31</td>
      <td>6</td>
      <td>0.06792</td>
      <td>6.79152</td>
      <td>0.01127</td>
      <td>1.12720</td>
      <td>0.14044</td>
      <td>14.04429</td>
      <td>0.08737</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 15, 2003-12-31 to 2004-05-31</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Cycle 16</td>
      <td>2004-05-31</td>
      <td>2006-12-31</td>
      <td>32</td>
      <td>0.34572</td>
      <td>34.57166</td>
      <td>0.00952</td>
      <td>0.95192</td>
      <td>0.11778</td>
      <td>11.77833</td>
      <td>0.06998</td>
      <td>0.04250</td>
      <td>425.00000</td>
      <td>0.01594</td>
      <td>159.37500</td>
      <td>Cycle 16, 2004-05-31 to 2006-12-31</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Cycle 17</td>
      <td>2006-12-31</td>
      <td>2007-08-31</td>
      <td>9</td>
      <td>0.06671</td>
      <td>6.67103</td>
      <td>0.00748</td>
      <td>0.74817</td>
      <td>0.08992</td>
      <td>8.99217</td>
      <td>0.08722</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 17, 2006-12-31 to 2007-08-31</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Cycle 18</td>
      <td>2007-08-31</td>
      <td>2009-07-31</td>
      <td>24</td>
      <td>-0.28840</td>
      <td>-28.83990</td>
      <td>-0.01191</td>
      <td>-1.19125</td>
      <td>-0.15644</td>
      <td>-15.64355</td>
      <td>0.22888</td>
      <td>-0.05000</td>
      <td>-500.00000</td>
      <td>-0.02500</td>
      <td>-250.00000</td>
      <td>Cycle 18, 2007-08-31 to 2009-07-31</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Cycle 19</td>
      <td>2009-07-31</td>
      <td>2015-11-30</td>
      <td>77</td>
      <td>1.59039</td>
      <td>159.03905</td>
      <td>0.01314</td>
      <td>1.31414</td>
      <td>0.15990</td>
      <td>15.99000</td>
      <td>0.13125</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 19, 2009-07-31 to 2015-11-30</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Cycle 20</td>
      <td>2015-11-30</td>
      <td>2016-06-30</td>
      <td>8</td>
      <td>0.02502</td>
      <td>2.50250</td>
      <td>0.00356</td>
      <td>0.35617</td>
      <td>0.03777</td>
      <td>3.77714</td>
      <td>0.11389</td>
      <td>0.00250</td>
      <td>25.00000</td>
      <td>0.00375</td>
      <td>37.50000</td>
      <td>Cycle 20, 2015-11-30 to 2016-06-30</td>
    </tr>
    <tr>
      <th>20</th>
      <td>Cycle 21</td>
      <td>2016-06-30</td>
      <td>2016-11-30</td>
      <td>6</td>
      <td>0.06008</td>
      <td>6.00766</td>
      <td>0.00997</td>
      <td>0.99744</td>
      <td>0.12376</td>
      <td>12.37623</td>
      <td>0.07708</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 21, 2016-06-30 to 2016-11-30</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Cycle 22</td>
      <td>2016-11-30</td>
      <td>2019-06-30</td>
      <td>32</td>
      <td>0.46031</td>
      <td>46.03091</td>
      <td>0.01256</td>
      <td>1.25618</td>
      <td>0.15257</td>
      <td>15.25686</td>
      <td>0.12685</td>
      <td>0.02000</td>
      <td>200.00000</td>
      <td>0.00750</td>
      <td>75.00000</td>
      <td>Cycle 22, 2016-11-30 to 2019-06-30</td>
    </tr>
    <tr>
      <th>22</th>
      <td>Cycle 23</td>
      <td>2019-06-30</td>
      <td>2019-07-31</td>
      <td>2</td>
      <td>0.08586</td>
      <td>8.58628</td>
      <td>0.04242</td>
      <td>4.24249</td>
      <td>0.63927</td>
      <td>63.92672</td>
      <td>0.13743</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 23, 2019-06-30 to 2019-07-31</td>
    </tr>
    <tr>
      <th>23</th>
      <td>Cycle 24</td>
      <td>2019-07-31</td>
      <td>2020-09-30</td>
      <td>15</td>
      <td>0.17105</td>
      <td>17.10456</td>
      <td>0.01234</td>
      <td>1.23424</td>
      <td>0.13464</td>
      <td>13.46425</td>
      <td>0.21140</td>
      <td>-0.02250</td>
      <td>-225.00000</td>
      <td>-0.01800</td>
      <td>-180.00000</td>
      <td>Cycle 24, 2019-07-31 to 2020-09-30</td>
    </tr>
    <tr>
      <th>24</th>
      <td>Cycle 25</td>
      <td>2020-09-30</td>
      <td>2022-02-28</td>
      <td>18</td>
      <td>0.27728</td>
      <td>27.72844</td>
      <td>0.01457</td>
      <td>1.45670</td>
      <td>0.17722</td>
      <td>17.72221</td>
      <td>0.15078</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 25, 2020-09-30 to 2022-02-28</td>
    </tr>
    <tr>
      <th>25</th>
      <td>Cycle 26</td>
      <td>2022-02-28</td>
      <td>2024-01-31</td>
      <td>24</td>
      <td>0.10892</td>
      <td>10.89196</td>
      <td>0.00584</td>
      <td>0.58363</td>
      <td>0.05305</td>
      <td>5.30525</td>
      <td>0.19480</td>
      <td>0.05250</td>
      <td>525.00000</td>
      <td>0.02625</td>
      <td>262.50000</td>
      <td>Cycle 26, 2022-02-28 to 2024-01-31</td>
    </tr>
    <tr>
      <th>26</th>
      <td>Cycle 27</td>
      <td>2024-01-31</td>
      <td>2024-08-31</td>
      <td>8</td>
      <td>0.19526</td>
      <td>19.52588</td>
      <td>0.02293</td>
      <td>2.29282</td>
      <td>0.30675</td>
      <td>30.67513</td>
      <td>0.10238</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 27, 2024-01-31 to 2024-08-31</td>
    </tr>
    <tr>
      <th>27</th>
      <td>Cycle 28</td>
      <td>2024-08-31</td>
      <td>2025-06-30</td>
      <td>11</td>
      <td>0.13779</td>
      <td>13.77869</td>
      <td>0.01244</td>
      <td>1.24436</td>
      <td>0.15122</td>
      <td>15.12175</td>
      <td>0.13032</td>
      <td>-0.01000</td>
      <td>-100.00000</td>
      <td>-0.01091</td>
      <td>-109.09091</td>
      <td>Cycle 28, 2024-08-31 to 2025-06-30</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Cycle 29</td>
      <td>2025-06-30</td>
      <td>2025-08-31</td>
      <td>3</td>
      <td>0.09622</td>
      <td>9.62171</td>
      <td>0.03119</td>
      <td>3.11890</td>
      <td>0.44406</td>
      <td>44.40637</td>
      <td>0.05911</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 29, 2025-06-30 to 2025-08-31</td>
    </tr>
    <tr>
      <th>29</th>
      <td>Cycle 30</td>
      <td>2025-08-31</td>
      <td>2026-01-31</td>
      <td>6</td>
      <td>0.10133</td>
      <td>10.13298</td>
      <td>0.01629</td>
      <td>1.62914</td>
      <td>0.21293</td>
      <td>21.29273</td>
      <td>0.04688</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.01500</td>
      <td>-150.00000</td>
      <td>Cycle 30, 2025-08-31 to 2026-01-31</td>
    </tr>
  </tbody>
</table>
</div>


This gives us the following data points:

* Cycle start date
* Cycle end date
* Number of months in the cycle
* Cumulative return during the cycle (decimal and percent)
* Average monthly return during the cycle (decimal and percent)
* Annualized return during the cycle (decimal and percent)
* Return volatility during the cycle
* Cumulative change in FFR during the cycle (decimal and basis points)
* Annualized change in FFR during the cycle (decimal and basis points)

From the above DataFrame, we can then plot the cumulative and annualized returns for each cycle in a bar chart. First, the cumulative returns along with the cumulative change in FFR:


```python
plot_bar_returns_ffr_change(
    cycle_df=spxt_cycles,
    asset_label="SPXT",
    annualized_or_cumulative="Cumulative",
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_28_0.png)
    


And then the annualized returns along with the annualized change in FFR:


```python
plot_bar_returns_ffr_change(
    cycle_df=spxt_cycles,
    asset_label="SPXT",
    annualized_or_cumulative="Annualized",
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_30_0.png)
    


The cumulative returns plot is not particularly insightful, but there are some interesting observations to be gained from the annualized returns plot. During the past two (2) rate cutting cycles (cycles 11/12/13/14 and 18), stocks have exhibited negative returns during the rate cutting cycle. However, after the rate cutting cycle was complete, returns during the following cycle (when rates were usually flat) were quite strong and higher than the historical mean return for the S&P 500. The economic intuition for this behavior is valid; as the economy weakens, investors are concerned about the pricing of equities, the returns become negative, and the Fed responds with cutting rates. The exact timing of when the Fed begins cutting rates is one of the unknowns; the Fed could be ahead of the curve, cutting rates as economic data begins to prompt that action, or behind the curve, where the ecomony rolls over rapidly and even the Fed's actions are not enough to halt the economic contraction.

Finally, we can run an OLS regression to check fit:


```python
df = spxt_cycles

#=== Don't modify below this line ===

# Run OLS regression with statsmodels
X = df["FFR_AnnualizedChange_bps"]
y = df["AnnualizedReturnPct"]
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())
print(f"Intercept: {model.params[0]}, Slope: {model.params[1]}")  # Intercept and slope

# Calc X and Y values for regression line
X_vals = np.linspace(X.min(), X.max(), 100)
Y_vals = model.params[0] + model.params[1] * X_vals
```

                                 OLS Regression Results                            
    ===============================================================================
    Dep. Variable:     AnnualizedReturnPct   R-squared:                       0.017
    Model:                             OLS   Adj. R-squared:                 -0.018
    Method:                  Least Squares   F-statistic:                    0.4786
    Date:                 Tue, 24 Feb 2026   Prob (F-statistic):              0.495
    Time:                         13:51:24   Log-Likelihood:                -132.24
    No. Observations:                   30   AIC:                             268.5
    Df Residuals:                       28   BIC:                             271.3
    Df Model:                            1                                         
    Covariance Type:             nonrobust                                         
    ============================================================================================
                                   coef    std err          t      P>|t|      [0.025      0.975]
    --------------------------------------------------------------------------------------------
    const                       13.0760      3.792      3.448      0.002       5.308      20.844
    FFR_AnnualizedChange_bps     0.0221      0.032      0.692      0.495      -0.043       0.087
    ==============================================================================
    Omnibus:                        4.070   Durbin-Watson:                   1.523
    Prob(Omnibus):                  0.131   Jarque-Bera (JB):                2.894
    Skew:                          -0.320   Prob(JB):                        0.235
    Kurtosis:                       4.381   Cond. No.                         120.
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    Intercept: 13.076015539043272, Slope: 0.022056651501767076


And then plot the regression line along with the values:


```python
plot_scatter_regression_ffr_vs_returns(
    cycle_df=spxt_cycles,
    asset_label="SPXT",
    x_vals=X_vals,
    y_vals=Y_vals,
    intercept=model.params[0],
    slope=model.params[1],
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_34_0.png)
    


Here we can see the data points for cycles 11/12/13/14 and 18 as mentioned above. Interestingly, cycles 28/29/30 (which is the current rate cutting cycle) appears to be an outlier. Of course, the book is not yet finished for cycles 28/29/30, and we could certainly see a bear market in stocks over the next several years.

### Bonds

Next, we'll run a similar process for medium term bonds using SPBDU10T_S&P US Treasury Bond 7-10 Year Total Return Index.

First, we pull data with the following:


```python
bb_clean_data(
    base_directory=DATA_DIR,
    fund_ticker_name="SPBDU10T_S&P US Treasury Bond 7-10 Year Total Return Index",
    source="Bloomberg",
    asset_class="Indices",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

treas_10y = load_data(
    base_directory=DATA_DIR,
    ticker="SPBDU10T_S&P US Treasury Bond 7-10 Year Total Return Index_Clean",
    source="Bloomberg", 
    asset_class="Indices",
    timeframe="Daily",
    file_format="pickle",
)

# Filter TREAS_10Y to date range
treas_10y = treas_10y[(treas_10y.index >= pd.to_datetime(start_date)) & (treas_10y.index <= pd.to_datetime(end_date))]

# Drop everything except the "close" column
treas_10y = treas_10y[["Close"]]

# Resample to monthly frequency
treas_10y_monthly = treas_10y.resample("M").last()
treas_10y_monthly["Monthly_Return"] = treas_10y_monthly["Close"].pct_change()
treas_10y_monthly = treas_10y_monthly.dropna()

display(treas_10y_monthly)
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
      <th>Monthly_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1990-01-31</th>
      <td>98.01300</td>
      <td>-0.01987</td>
    </tr>
    <tr>
      <th>1990-02-28</th>
      <td>97.99000</td>
      <td>-0.00023</td>
    </tr>
    <tr>
      <th>1990-03-31</th>
      <td>97.98900</td>
      <td>-0.00001</td>
    </tr>
    <tr>
      <th>1990-04-30</th>
      <td>96.60600</td>
      <td>-0.01411</td>
    </tr>
    <tr>
      <th>1990-05-31</th>
      <td>99.64700</td>
      <td>0.03148</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2025-09-30</th>
      <td>645.58400</td>
      <td>0.00675</td>
    </tr>
    <tr>
      <th>2025-10-31</th>
      <td>650.00500</td>
      <td>0.00685</td>
    </tr>
    <tr>
      <th>2025-11-30</th>
      <td>656.63600</td>
      <td>0.01020</td>
    </tr>
    <tr>
      <th>2025-12-31</th>
      <td>652.28800</td>
      <td>-0.00662</td>
    </tr>
    <tr>
      <th>2026-01-31</th>
      <td>650.16900</td>
      <td>-0.00325</td>
    </tr>
  </tbody>
</table>
<p>433 rows × 2 columns</p>
</div>


Next, we can plot the price history before calculating the cycle performance:


```python
plot_timeseries(
    price_df=treas_10y,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["Close"],
    title="S&P US Treasury Bond 7-10 Year Total Return Index Daily Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_rotation=45,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=50,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_39_0.png)
    


Next, we will calculate the performance for SPY based on the pre-defined Fed cycles:


```python
treas_10y_cycles = calc_fed_cycle_asset_performance(
    start_date=cycle_ranges["start_date"],
    end_date=cycle_ranges["end_date"],
    label=cycle_ranges["cycle_label"],
    fed_funds_change=cycle_ranges["fed_funds_change"],
    monthly_returns=treas_10y_monthly,
)

display(treas_10y_cycles)
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
      <th>Cycle</th>
      <th>Start</th>
      <th>End</th>
      <th>Months</th>
      <th>CumulativeReturn</th>
      <th>CumulativeReturnPct</th>
      <th>AverageMonthlyReturn</th>
      <th>AverageMonthlyReturnPct</th>
      <th>AnnualizedReturn</th>
      <th>AnnualizedReturnPct</th>
      <th>Volatility</th>
      <th>FedFundsChange</th>
      <th>FedFundsChange_bps</th>
      <th>FFR_AnnualizedChange</th>
      <th>FFR_AnnualizedChange_bps</th>
      <th>Label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Cycle 1</td>
      <td>1989-12-31</td>
      <td>1990-06-30</td>
      <td>6</td>
      <td>0.01362</td>
      <td>1.36200</td>
      <td>0.00241</td>
      <td>0.24101</td>
      <td>0.02743</td>
      <td>2.74255</td>
      <td>0.06657</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 1, 1989-12-31 to 1990-06-30</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Cycle 2</td>
      <td>1990-06-30</td>
      <td>1993-03-31</td>
      <td>34</td>
      <td>0.45682</td>
      <td>45.68226</td>
      <td>0.01124</td>
      <td>1.12428</td>
      <td>0.14202</td>
      <td>14.20180</td>
      <td>0.05346</td>
      <td>-0.05250</td>
      <td>-525.00000</td>
      <td>-0.01853</td>
      <td>-185.29412</td>
      <td>Cycle 2, 1990-06-30 to 1993-03-31</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Cycle 3</td>
      <td>1993-03-31</td>
      <td>1994-01-31</td>
      <td>11</td>
      <td>0.08876</td>
      <td>8.87610</td>
      <td>0.00784</td>
      <td>0.78356</td>
      <td>0.09721</td>
      <td>9.72108</td>
      <td>0.04458</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 3, 1993-03-31 to 1994-01-31</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Cycle 4</td>
      <td>1994-01-31</td>
      <td>1995-06-30</td>
      <td>18</td>
      <td>0.07796</td>
      <td>7.79638</td>
      <td>0.00439</td>
      <td>0.43870</td>
      <td>0.05132</td>
      <td>5.13229</td>
      <td>0.07287</td>
      <td>0.03000</td>
      <td>300.00000</td>
      <td>0.02000</td>
      <td>200.00000</td>
      <td>Cycle 4, 1994-01-31 to 1995-06-30</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Cycle 5</td>
      <td>1995-06-30</td>
      <td>1996-07-31</td>
      <td>14</td>
      <td>0.04785</td>
      <td>4.78467</td>
      <td>0.00344</td>
      <td>0.34387</td>
      <td>0.04087</td>
      <td>4.08738</td>
      <td>0.04940</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00643</td>
      <td>-64.28571</td>
      <td>Cycle 5, 1995-06-30 to 1996-07-31</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Cycle 6</td>
      <td>1996-07-31</td>
      <td>1997-02-28</td>
      <td>8</td>
      <td>0.05301</td>
      <td>5.30118</td>
      <td>0.00658</td>
      <td>0.65819</td>
      <td>0.08056</td>
      <td>8.05623</td>
      <td>0.05365</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 6, 1996-07-31 to 1997-02-28</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Cycle 7</td>
      <td>1997-02-28</td>
      <td>1997-09-30</td>
      <td>8</td>
      <td>0.06453</td>
      <td>6.45298</td>
      <td>0.00799</td>
      <td>0.79904</td>
      <td>0.09834</td>
      <td>9.83398</td>
      <td>0.06285</td>
      <td>0.00250</td>
      <td>25.00000</td>
      <td>0.00375</td>
      <td>37.50000</td>
      <td>Cycle 7, 1997-02-28 to 1997-09-30</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Cycle 8</td>
      <td>1997-09-30</td>
      <td>1998-08-31</td>
      <td>12</td>
      <td>0.14428</td>
      <td>14.42797</td>
      <td>0.01135</td>
      <td>1.13516</td>
      <td>0.14428</td>
      <td>14.42797</td>
      <td>0.03891</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 8, 1997-09-30 to 1998-08-31</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Cycle 9</td>
      <td>1998-08-31</td>
      <td>1999-05-31</td>
      <td>10</td>
      <td>0.03052</td>
      <td>3.05162</td>
      <td>0.00326</td>
      <td>0.32630</td>
      <td>0.03673</td>
      <td>3.67303</td>
      <td>0.08244</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00900</td>
      <td>-90.00000</td>
      <td>Cycle 9, 1998-08-31 to 1999-05-31</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Cycle 10</td>
      <td>1999-05-31</td>
      <td>2000-11-30</td>
      <td>19</td>
      <td>0.08744</td>
      <td>8.74418</td>
      <td>0.00449</td>
      <td>0.44926</td>
      <td>0.05437</td>
      <td>5.43706</td>
      <td>0.04250</td>
      <td>0.01750</td>
      <td>175.00000</td>
      <td>0.01105</td>
      <td>110.52632</td>
      <td>Cycle 10, 1999-05-31 to 2000-11-30</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Cycle 11</td>
      <td>2000-11-30</td>
      <td>2000-12-31</td>
      <td>2</td>
      <td>0.04918</td>
      <td>4.91839</td>
      <td>0.02430</td>
      <td>2.42972</td>
      <td>0.33386</td>
      <td>33.38584</td>
      <td>0.00458</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 11, 2000-11-30 to 2000-12-31</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Cycle 12</td>
      <td>2000-12-31</td>
      <td>2002-06-30</td>
      <td>19</td>
      <td>0.14331</td>
      <td>14.33071</td>
      <td>0.00721</td>
      <td>0.72113</td>
      <td>0.08826</td>
      <td>8.82645</td>
      <td>0.05901</td>
      <td>-0.04750</td>
      <td>-475.00000</td>
      <td>-0.03000</td>
      <td>-300.00000</td>
      <td>Cycle 12, 2000-12-31 to 2002-06-30</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Cycle 13</td>
      <td>2002-06-30</td>
      <td>2002-10-31</td>
      <td>5</td>
      <td>0.09945</td>
      <td>9.94496</td>
      <td>0.01929</td>
      <td>1.92905</td>
      <td>0.25551</td>
      <td>25.55118</td>
      <td>0.06682</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 13, 2002-06-30 to 2002-10-31</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Cycle 14</td>
      <td>2002-10-31</td>
      <td>2003-12-31</td>
      <td>15</td>
      <td>0.02161</td>
      <td>2.16130</td>
      <td>0.00172</td>
      <td>0.17218</td>
      <td>0.01725</td>
      <td>1.72534</td>
      <td>0.08696</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00600</td>
      <td>-60.00000</td>
      <td>Cycle 14, 2002-10-31 to 2003-12-31</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Cycle 15</td>
      <td>2003-12-31</td>
      <td>2004-05-31</td>
      <td>6</td>
      <td>-0.00088</td>
      <td>-0.08831</td>
      <td>0.00006</td>
      <td>0.00600</td>
      <td>-0.00177</td>
      <td>-0.17654</td>
      <td>0.07653</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 15, 2003-12-31 to 2004-05-31</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Cycle 16</td>
      <td>2004-05-31</td>
      <td>2006-12-31</td>
      <td>32</td>
      <td>0.10267</td>
      <td>10.26670</td>
      <td>0.00314</td>
      <td>0.31382</td>
      <td>0.03733</td>
      <td>3.73293</td>
      <td>0.04440</td>
      <td>0.04250</td>
      <td>425.00000</td>
      <td>0.01594</td>
      <td>159.37500</td>
      <td>Cycle 16, 2004-05-31 to 2006-12-31</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Cycle 17</td>
      <td>2006-12-31</td>
      <td>2007-08-31</td>
      <td>9</td>
      <td>0.03300</td>
      <td>3.30047</td>
      <td>0.00371</td>
      <td>0.37102</td>
      <td>0.04425</td>
      <td>4.42466</td>
      <td>0.05098</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 17, 2006-12-31 to 2007-08-31</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Cycle 18</td>
      <td>2007-08-31</td>
      <td>2009-07-31</td>
      <td>24</td>
      <td>0.19843</td>
      <td>19.84327</td>
      <td>0.00792</td>
      <td>0.79193</td>
      <td>0.09473</td>
      <td>9.47295</td>
      <td>0.09432</td>
      <td>-0.05000</td>
      <td>-500.00000</td>
      <td>-0.02500</td>
      <td>-250.00000</td>
      <td>Cycle 18, 2007-08-31 to 2009-07-31</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Cycle 19</td>
      <td>2009-07-31</td>
      <td>2015-11-30</td>
      <td>77</td>
      <td>0.38995</td>
      <td>38.99485</td>
      <td>0.00443</td>
      <td>0.44302</td>
      <td>0.05265</td>
      <td>5.26537</td>
      <td>0.05945</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 19, 2009-07-31 to 2015-11-30</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Cycle 20</td>
      <td>2015-11-30</td>
      <td>2016-06-30</td>
      <td>8</td>
      <td>0.06790</td>
      <td>6.78998</td>
      <td>0.00835</td>
      <td>0.83470</td>
      <td>0.10356</td>
      <td>10.35595</td>
      <td>0.05317</td>
      <td>0.00250</td>
      <td>25.00000</td>
      <td>0.00375</td>
      <td>37.50000</td>
      <td>Cycle 20, 2015-11-30 to 2016-06-30</td>
    </tr>
    <tr>
      <th>20</th>
      <td>Cycle 21</td>
      <td>2016-06-30</td>
      <td>2016-11-30</td>
      <td>6</td>
      <td>-0.03175</td>
      <td>-3.17490</td>
      <td>-0.00513</td>
      <td>-0.51254</td>
      <td>-0.06249</td>
      <td>-6.24899</td>
      <td>0.08242</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 21, 2016-06-30 to 2016-11-30</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Cycle 22</td>
      <td>2016-11-30</td>
      <td>2019-06-30</td>
      <td>32</td>
      <td>0.05923</td>
      <td>5.92338</td>
      <td>0.00190</td>
      <td>0.19002</td>
      <td>0.02181</td>
      <td>2.18142</td>
      <td>0.04975</td>
      <td>0.02000</td>
      <td>200.00000</td>
      <td>0.00750</td>
      <td>75.00000</td>
      <td>Cycle 22, 2016-11-30 to 2019-06-30</td>
    </tr>
    <tr>
      <th>22</th>
      <td>Cycle 23</td>
      <td>2019-06-30</td>
      <td>2019-07-31</td>
      <td>2</td>
      <td>0.01306</td>
      <td>1.30568</td>
      <td>0.00653</td>
      <td>0.65261</td>
      <td>0.08094</td>
      <td>8.09429</td>
      <td>0.03024</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 23, 2019-06-30 to 2019-07-31</td>
    </tr>
    <tr>
      <th>23</th>
      <td>Cycle 24</td>
      <td>2019-07-31</td>
      <td>2020-09-30</td>
      <td>15</td>
      <td>0.13083</td>
      <td>13.08268</td>
      <td>0.00837</td>
      <td>0.83706</td>
      <td>0.10336</td>
      <td>10.33591</td>
      <td>0.06056</td>
      <td>-0.02250</td>
      <td>-225.00000</td>
      <td>-0.01800</td>
      <td>-180.00000</td>
      <td>Cycle 24, 2019-07-31 to 2020-09-30</td>
    </tr>
    <tr>
      <th>24</th>
      <td>Cycle 25</td>
      <td>2020-09-30</td>
      <td>2022-02-28</td>
      <td>18</td>
      <td>-0.06522</td>
      <td>-6.52177</td>
      <td>-0.00366</td>
      <td>-0.36622</td>
      <td>-0.04397</td>
      <td>-4.39653</td>
      <td>0.04430</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 25, 2020-09-30 to 2022-02-28</td>
    </tr>
    <tr>
      <th>25</th>
      <td>Cycle 26</td>
      <td>2022-02-28</td>
      <td>2024-01-31</td>
      <td>24</td>
      <td>-0.09878</td>
      <td>-9.87840</td>
      <td>-0.00394</td>
      <td>-0.39369</td>
      <td>-0.05068</td>
      <td>-5.06760</td>
      <td>0.09858</td>
      <td>0.05250</td>
      <td>525.00000</td>
      <td>0.02625</td>
      <td>262.50000</td>
      <td>Cycle 26, 2022-02-28 to 2024-01-31</td>
    </tr>
    <tr>
      <th>26</th>
      <td>Cycle 27</td>
      <td>2024-01-31</td>
      <td>2024-08-31</td>
      <td>8</td>
      <td>0.02748</td>
      <td>2.74817</td>
      <td>0.00357</td>
      <td>0.35718</td>
      <td>0.04150</td>
      <td>4.15045</td>
      <td>0.06957</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 27, 2024-01-31 to 2024-08-31</td>
    </tr>
    <tr>
      <th>27</th>
      <td>Cycle 28</td>
      <td>2024-08-31</td>
      <td>2025-06-30</td>
      <td>11</td>
      <td>0.03294</td>
      <td>3.29408</td>
      <td>0.00310</td>
      <td>0.31010</td>
      <td>0.03599</td>
      <td>3.59887</td>
      <td>0.06280</td>
      <td>-0.01000</td>
      <td>-100.00000</td>
      <td>-0.01091</td>
      <td>-109.09091</td>
      <td>Cycle 28, 2024-08-31 to 2025-06-30</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Cycle 29</td>
      <td>2025-06-30</td>
      <td>2025-08-31</td>
      <td>3</td>
      <td>0.02670</td>
      <td>2.66978</td>
      <td>0.00888</td>
      <td>0.88750</td>
      <td>0.11114</td>
      <td>11.11445</td>
      <td>0.04409</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 29, 2025-06-30 to 2025-08-31</td>
    </tr>
    <tr>
      <th>29</th>
      <td>Cycle 30</td>
      <td>2025-08-31</td>
      <td>2026-01-31</td>
      <td>6</td>
      <td>0.03081</td>
      <td>3.08068</td>
      <td>0.00510</td>
      <td>0.51007</td>
      <td>0.06256</td>
      <td>6.25626</td>
      <td>0.02992</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.01500</td>
      <td>-150.00000</td>
      <td>Cycle 30, 2025-08-31 to 2026-01-31</td>
    </tr>
  </tbody>
</table>
</div>


This gives us the following data points:

* Cycle start date
* Cycle end date
* Number of months in the cycle
* Cumulative return during the cycle (decimal and percent)
* Average monthly return during the cycle (decimal and percent)
* Annualized return during the cycle (decimal and percent)
* Return volatility during the cycle
* Cumulative change in FFR during the cycle (decimal and basis points)
* Annualized change in FFR during the cycle (decimal and basis points)

From the above DataFrame, we can then plot the cumulative and annualized returns for each cycle in a bar chart. First, the cumulative returns along with the cumulative change in FFR:


```python
plot_bar_returns_ffr_change(
    cycle_df=treas_10y_cycles,
    asset_label="TREAS_10Y",
    annualized_or_cumulative="Cumulative",
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_43_0.png)
    


And then the annualized returns along with the annualized change in FFR:


```python
plot_bar_returns_ffr_change(
    cycle_df=treas_10y_cycles,
    asset_label="TREAS_10Y",
    annualized_or_cumulative="Annualized",
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_45_0.png)
    


For this dataset, we have cycles 11/12/13/14 exhibiting strong returns, which is consistent with the economic intuition that bonds should perform well during periods of economic weakness and rate cuts. We also see this outcome with cycle 18. It becomes a little more interesting during cycles 25 and 26, where the correlations of stocks and bond returns seemed to align, so we see negative bond returns there. Finally, cycles 28/29/30 also exhibit positive bond returns, which is consistent with our thesis that bonds should perform well during periods of economic weakness and rate cuts.

Finally, we can run an OLS regression to check fit:


```python
df = treas_10y_cycles

#=== Don't modify below this line ===

# Run OLS regression with statsmodels
X = df["FFR_AnnualizedChange_bps"]
y = df["AnnualizedReturnPct"]
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())
print(f"Intercept: {model.params[0]}, Slope: {model.params[1]}")  # Intercept and slope

# Calc X and Y values for regression line
X_vals = np.linspace(X.min(), X.max(), 100)
Y_vals = model.params[0] + model.params[1] * X_vals
```

                                 OLS Regression Results                            
    ===============================================================================
    Dep. Variable:     AnnualizedReturnPct   R-squared:                       0.050
    Model:                             OLS   Adj. R-squared:                  0.016
    Method:                  Least Squares   F-statistic:                     1.462
    Date:                 Tue, 24 Feb 2026   Prob (F-statistic):              0.237
    Time:                         13:51:27   Log-Likelihood:                -103.64
    No. Observations:                   30   AIC:                             211.3
    Df Residuals:                       28   BIC:                             214.1
    Df Model:                            1                                         
    Covariance Type:             nonrobust                                         
    ============================================================================================
                                   coef    std err          t      P>|t|      [0.025      0.975]
    --------------------------------------------------------------------------------------------
    const                        6.7457      1.462      4.613      0.000       3.751       9.741
    FFR_AnnualizedChange_bps    -0.0149      0.012     -1.209      0.237      -0.040       0.010
    ==============================================================================
    Omnibus:                       19.978   Durbin-Watson:                   2.116
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               29.185
    Skew:                           1.582   Prob(JB):                     4.60e-07
    Kurtosis:                       6.651   Cond. No.                         120.
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    Intercept: 6.745718627069434, Slope: -0.01486255000436152


And then plot the regression line along with the values:


```python
plot_scatter_regression_ffr_vs_returns(
    cycle_df=treas_10y_cycles,
    asset_label="TREAS_10Y",
    x_vals=X_vals,
    y_vals=Y_vals,
    intercept=model.params[0],
    slope=model.params[1],
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_49_0.png)
    


The above plot is intriguing because of how well the OLS regression appears to fit the data. It certainly appears that during rate-cutting cycles, bonds are an asset that performs well.

### High Yield Bonds

Next, we'll run a similar process for high yield bonds using LF98TRUU_Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD.

First, we pull data with the following:


```python
bb_clean_data(
    base_directory=DATA_DIR,
    fund_ticker_name="LF98TRUU_Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD",
    source="Bloomberg",
    asset_class="Indices",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

hy_bonds = load_data(
    base_directory=DATA_DIR,
    ticker="LF98TRUU_Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD_Clean",
    source="Bloomberg", 
    asset_class="Indices",
    timeframe="Daily",
    file_format="pickle",
)

# Filter HY_BONDS to date range
hy_bonds = hy_bonds[(hy_bonds.index >= pd.to_datetime(start_date)) & (hy_bonds.index <= pd.to_datetime(end_date))]

# Drop everything except the "close" column
hy_bonds = hy_bonds[["Close"]]

# Resample to monthly frequency
hy_bonds_monthly = hy_bonds.resample("M").last()
hy_bonds_monthly["Monthly_Return"] = hy_bonds_monthly["Close"].pct_change()
hy_bonds_monthly = hy_bonds_monthly.dropna()

display(hy_bonds_monthly)
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
      <th>Monthly_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1990-01-31</th>
      <td>194.21000</td>
      <td>-0.02146</td>
    </tr>
    <tr>
      <th>1990-02-28</th>
      <td>190.20000</td>
      <td>-0.02065</td>
    </tr>
    <tr>
      <th>1990-03-31</th>
      <td>195.19000</td>
      <td>0.02624</td>
    </tr>
    <tr>
      <th>1990-04-30</th>
      <td>194.86000</td>
      <td>-0.00169</td>
    </tr>
    <tr>
      <th>1990-05-31</th>
      <td>198.62000</td>
      <td>0.01930</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2025-09-30</th>
      <td>2876.85000</td>
      <td>0.00816</td>
    </tr>
    <tr>
      <th>2025-10-31</th>
      <td>2881.38000</td>
      <td>0.00157</td>
    </tr>
    <tr>
      <th>2025-11-30</th>
      <td>2898.07000</td>
      <td>0.00579</td>
    </tr>
    <tr>
      <th>2025-12-31</th>
      <td>2914.49000</td>
      <td>0.00567</td>
    </tr>
    <tr>
      <th>2026-01-31</th>
      <td>2929.32000</td>
      <td>0.00509</td>
    </tr>
  </tbody>
</table>
<p>433 rows × 2 columns</p>
</div>


Next, we can plot the price history before calculating the cycle performance:


```python
plot_timeseries(
    price_df=hy_bonds,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["Close"],
    title="Bloomberg US Corporate High Yield Total Return Index Value Unhedged USD Daily Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_rotation=45,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=200,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_53_0.png)
    


Next, we will calculate the performance of high yield bonds based on the pre-defined Fed cycles:


```python
hy_bonds_cycles = calc_fed_cycle_asset_performance(
    start_date=cycle_ranges["start_date"],
    end_date=cycle_ranges["end_date"],
    label=cycle_ranges["cycle_label"],
    fed_funds_change=cycle_ranges["fed_funds_change"],
    monthly_returns=hy_bonds_monthly,
)

display(hy_bonds_cycles)
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
      <th>Cycle</th>
      <th>Start</th>
      <th>End</th>
      <th>Months</th>
      <th>CumulativeReturn</th>
      <th>CumulativeReturnPct</th>
      <th>AverageMonthlyReturn</th>
      <th>AverageMonthlyReturnPct</th>
      <th>AnnualizedReturn</th>
      <th>AnnualizedReturnPct</th>
      <th>Volatility</th>
      <th>FedFundsChange</th>
      <th>FedFundsChange_bps</th>
      <th>FFR_AnnualizedChange</th>
      <th>FFR_AnnualizedChange_bps</th>
      <th>Label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Cycle 1</td>
      <td>1989-12-31</td>
      <td>1990-06-30</td>
      <td>6</td>
      <td>0.02494</td>
      <td>2.49408</td>
      <td>0.00432</td>
      <td>0.43159</td>
      <td>0.05050</td>
      <td>5.05036</td>
      <td>0.07625</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 1, 1989-12-31 to 1990-06-30</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Cycle 2</td>
      <td>1990-06-30</td>
      <td>1993-03-31</td>
      <td>34</td>
      <td>0.62149</td>
      <td>62.14883</td>
      <td>0.01480</td>
      <td>1.47959</td>
      <td>0.18601</td>
      <td>18.60069</td>
      <td>0.10898</td>
      <td>-0.05250</td>
      <td>-525.00000</td>
      <td>-0.01853</td>
      <td>-185.29412</td>
      <td>Cycle 2, 1990-06-30 to 1993-03-31</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Cycle 3</td>
      <td>1993-03-31</td>
      <td>1994-01-31</td>
      <td>11</td>
      <td>0.14262</td>
      <td>14.26235</td>
      <td>0.01221</td>
      <td>1.22129</td>
      <td>0.15656</td>
      <td>15.65571</td>
      <td>0.02227</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 3, 1993-03-31 to 1994-01-31</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Cycle 4</td>
      <td>1994-01-31</td>
      <td>1995-06-30</td>
      <td>18</td>
      <td>0.11254</td>
      <td>11.25422</td>
      <td>0.00607</td>
      <td>0.60701</td>
      <td>0.07369</td>
      <td>7.36869</td>
      <td>0.05691</td>
      <td>0.03000</td>
      <td>300.00000</td>
      <td>0.02000</td>
      <td>200.00000</td>
      <td>Cycle 4, 1994-01-31 to 1995-06-30</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Cycle 5</td>
      <td>1995-06-30</td>
      <td>1996-07-31</td>
      <td>14</td>
      <td>0.10892</td>
      <td>10.89235</td>
      <td>0.00743</td>
      <td>0.74262</td>
      <td>0.09267</td>
      <td>9.26651</td>
      <td>0.01906</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00643</td>
      <td>-64.28571</td>
      <td>Cycle 5, 1995-06-30 to 1996-07-31</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Cycle 6</td>
      <td>1996-07-31</td>
      <td>1997-02-28</td>
      <td>8</td>
      <td>0.10479</td>
      <td>10.47889</td>
      <td>0.01255</td>
      <td>1.25548</td>
      <td>0.16123</td>
      <td>16.12319</td>
      <td>0.02366</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 6, 1996-07-31 to 1997-02-28</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Cycle 7</td>
      <td>1997-02-28</td>
      <td>1997-09-30</td>
      <td>8</td>
      <td>0.09557</td>
      <td>9.55703</td>
      <td>0.01156</td>
      <td>1.15581</td>
      <td>0.14673</td>
      <td>14.67279</td>
      <td>0.04792</td>
      <td>0.00250</td>
      <td>25.00000</td>
      <td>0.00375</td>
      <td>37.50000</td>
      <td>Cycle 7, 1997-02-28 to 1997-09-30</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Cycle 8</td>
      <td>1997-09-30</td>
      <td>1998-08-31</td>
      <td>12</td>
      <td>0.03219</td>
      <td>3.21938</td>
      <td>0.00282</td>
      <td>0.28169</td>
      <td>0.03219</td>
      <td>3.21938</td>
      <td>0.06631</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 8, 1997-09-30 to 1998-08-31</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Cycle 9</td>
      <td>1998-08-31</td>
      <td>1999-05-31</td>
      <td>10</td>
      <td>-0.00728</td>
      <td>-0.72813</td>
      <td>-0.00042</td>
      <td>-0.04217</td>
      <td>-0.00873</td>
      <td>-0.87312</td>
      <td>0.09026</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00900</td>
      <td>-90.00000</td>
      <td>Cycle 9, 1998-08-31 to 1999-05-31</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Cycle 10</td>
      <td>1999-05-31</td>
      <td>2000-11-30</td>
      <td>19</td>
      <td>-0.08916</td>
      <td>-8.91594</td>
      <td>-0.00480</td>
      <td>-0.47963</td>
      <td>-0.05728</td>
      <td>-5.72758</td>
      <td>0.05172</td>
      <td>0.01750</td>
      <td>175.00000</td>
      <td>0.01105</td>
      <td>110.52632</td>
      <td>Cycle 10, 1999-05-31 to 2000-11-30</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Cycle 11</td>
      <td>2000-11-30</td>
      <td>2000-12-31</td>
      <td>2</td>
      <td>-0.02105</td>
      <td>-2.10510</td>
      <td>-0.01014</td>
      <td>-1.01430</td>
      <td>-0.11984</td>
      <td>-11.98427</td>
      <td>0.14432</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 11, 2000-11-30 to 2000-12-31</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Cycle 12</td>
      <td>2000-12-31</td>
      <td>2002-06-30</td>
      <td>19</td>
      <td>0.02117</td>
      <td>2.11701</td>
      <td>0.00167</td>
      <td>0.16693</td>
      <td>0.01332</td>
      <td>1.33189</td>
      <td>0.11914</td>
      <td>-0.04750</td>
      <td>-475.00000</td>
      <td>-0.03000</td>
      <td>-300.00000</td>
      <td>Cycle 12, 2000-12-31 to 2002-06-30</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Cycle 13</td>
      <td>2002-06-30</td>
      <td>2002-10-31</td>
      <td>5</td>
      <td>-0.10874</td>
      <td>-10.87431</td>
      <td>-0.02215</td>
      <td>-2.21511</td>
      <td>-0.24141</td>
      <td>-24.14102</td>
      <td>0.13364</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 13, 2002-06-30 to 2002-10-31</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Cycle 14</td>
      <td>2002-10-31</td>
      <td>2003-12-31</td>
      <td>15</td>
      <td>0.37662</td>
      <td>37.66182</td>
      <td>0.02172</td>
      <td>2.17230</td>
      <td>0.29137</td>
      <td>29.13703</td>
      <td>0.07004</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00600</td>
      <td>-60.00000</td>
      <td>Cycle 14, 2002-10-31 to 2003-12-31</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Cycle 15</td>
      <td>2003-12-31</td>
      <td>2004-05-31</td>
      <td>6</td>
      <td>0.02188</td>
      <td>2.18782</td>
      <td>0.00371</td>
      <td>0.37115</td>
      <td>0.04424</td>
      <td>4.42350</td>
      <td>0.05322</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 15, 2003-12-31 to 2004-05-31</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Cycle 16</td>
      <td>2004-05-31</td>
      <td>2006-12-31</td>
      <td>32</td>
      <td>0.25625</td>
      <td>25.62459</td>
      <td>0.00722</td>
      <td>0.72211</td>
      <td>0.08931</td>
      <td>8.93138</td>
      <td>0.04056</td>
      <td>0.04250</td>
      <td>425.00000</td>
      <td>0.01594</td>
      <td>159.37500</td>
      <td>Cycle 16, 2004-05-31 to 2006-12-31</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Cycle 17</td>
      <td>2006-12-31</td>
      <td>2007-08-31</td>
      <td>9</td>
      <td>0.01683</td>
      <td>1.68350</td>
      <td>0.00199</td>
      <td>0.19914</td>
      <td>0.02251</td>
      <td>2.25094</td>
      <td>0.05992</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 17, 2006-12-31 to 2007-08-31</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Cycle 18</td>
      <td>2007-08-31</td>
      <td>2009-07-31</td>
      <td>24</td>
      <td>0.04908</td>
      <td>4.90805</td>
      <td>0.00371</td>
      <td>0.37092</td>
      <td>0.02425</td>
      <td>2.42463</td>
      <td>0.20404</td>
      <td>-0.05000</td>
      <td>-500.00000</td>
      <td>-0.02500</td>
      <td>-250.00000</td>
      <td>Cycle 18, 2007-08-31 to 2009-07-31</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Cycle 19</td>
      <td>2009-07-31</td>
      <td>2015-11-30</td>
      <td>77</td>
      <td>0.83146</td>
      <td>83.14599</td>
      <td>0.00808</td>
      <td>0.80820</td>
      <td>0.09889</td>
      <td>9.88931</td>
      <td>0.06867</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 19, 2009-07-31 to 2015-11-30</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Cycle 20</td>
      <td>2015-11-30</td>
      <td>2016-06-30</td>
      <td>8</td>
      <td>0.03948</td>
      <td>3.94781</td>
      <td>0.00515</td>
      <td>0.51508</td>
      <td>0.05980</td>
      <td>5.97977</td>
      <td>0.09107</td>
      <td>0.00250</td>
      <td>25.00000</td>
      <td>0.00375</td>
      <td>37.50000</td>
      <td>Cycle 20, 2015-11-30 to 2016-06-30</td>
    </tr>
    <tr>
      <th>20</th>
      <td>Cycle 21</td>
      <td>2016-06-30</td>
      <td>2016-11-30</td>
      <td>6</td>
      <td>0.06426</td>
      <td>6.42628</td>
      <td>0.01049</td>
      <td>1.04900</td>
      <td>0.13266</td>
      <td>13.26554</td>
      <td>0.04025</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 21, 2016-06-30 to 2016-11-30</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Cycle 22</td>
      <td>2016-11-30</td>
      <td>2019-06-30</td>
      <td>32</td>
      <td>0.17306</td>
      <td>17.30568</td>
      <td>0.00508</td>
      <td>0.50759</td>
      <td>0.06168</td>
      <td>6.16825</td>
      <td>0.04347</td>
      <td>0.02000</td>
      <td>200.00000</td>
      <td>0.00750</td>
      <td>75.00000</td>
      <td>Cycle 22, 2016-11-30 to 2019-06-30</td>
    </tr>
    <tr>
      <th>22</th>
      <td>Cycle 23</td>
      <td>2019-06-30</td>
      <td>2019-07-31</td>
      <td>2</td>
      <td>0.02856</td>
      <td>2.85572</td>
      <td>0.01421</td>
      <td>1.42144</td>
      <td>0.18405</td>
      <td>18.40520</td>
      <td>0.04203</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 23, 2019-06-30 to 2019-07-31</td>
    </tr>
    <tr>
      <th>23</th>
      <td>Cycle 24</td>
      <td>2019-07-31</td>
      <td>2020-09-30</td>
      <td>15</td>
      <td>0.04631</td>
      <td>4.63140</td>
      <td>0.00372</td>
      <td>0.37244</td>
      <td>0.03688</td>
      <td>3.68827</td>
      <td>0.13113</td>
      <td>-0.02250</td>
      <td>-225.00000</td>
      <td>-0.01800</td>
      <td>-180.00000</td>
      <td>Cycle 24, 2019-07-31 to 2020-09-30</td>
    </tr>
    <tr>
      <th>24</th>
      <td>Cycle 25</td>
      <td>2020-09-30</td>
      <td>2022-02-28</td>
      <td>18</td>
      <td>0.06775</td>
      <td>6.77496</td>
      <td>0.00374</td>
      <td>0.37444</td>
      <td>0.04467</td>
      <td>4.46712</td>
      <td>0.04952</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 25, 2020-09-30 to 2022-02-28</td>
    </tr>
    <tr>
      <th>25</th>
      <td>Cycle 26</td>
      <td>2022-02-28</td>
      <td>2024-01-31</td>
      <td>24</td>
      <td>0.03580</td>
      <td>3.58042</td>
      <td>0.00186</td>
      <td>0.18605</td>
      <td>0.01774</td>
      <td>1.77447</td>
      <td>0.09916</td>
      <td>0.05250</td>
      <td>525.00000</td>
      <td>0.02625</td>
      <td>262.50000</td>
      <td>Cycle 26, 2022-02-28 to 2024-01-31</td>
    </tr>
    <tr>
      <th>26</th>
      <td>Cycle 27</td>
      <td>2024-01-31</td>
      <td>2024-08-31</td>
      <td>8</td>
      <td>0.06285</td>
      <td>6.28480</td>
      <td>0.00769</td>
      <td>0.76866</td>
      <td>0.09574</td>
      <td>9.57381</td>
      <td>0.03255</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 27, 2024-01-31 to 2024-08-31</td>
    </tr>
    <tr>
      <th>27</th>
      <td>Cycle 28</td>
      <td>2024-08-31</td>
      <td>2025-06-30</td>
      <td>11</td>
      <td>0.08182</td>
      <td>8.18158</td>
      <td>0.00722</td>
      <td>0.72241</td>
      <td>0.08958</td>
      <td>8.95776</td>
      <td>0.03617</td>
      <td>-0.01000</td>
      <td>-100.00000</td>
      <td>-0.01091</td>
      <td>-109.09091</td>
      <td>Cycle 28, 2024-08-31 to 2025-06-30</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Cycle 29</td>
      <td>2025-06-30</td>
      <td>2025-08-31</td>
      <td>3</td>
      <td>0.03577</td>
      <td>3.57673</td>
      <td>0.01180</td>
      <td>1.17991</td>
      <td>0.15093</td>
      <td>15.09297</td>
      <td>0.02414</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 29, 2025-06-30 to 2025-08-31</td>
    </tr>
    <tr>
      <th>29</th>
      <td>Cycle 30</td>
      <td>2025-08-31</td>
      <td>2026-01-31</td>
      <td>6</td>
      <td>0.03937</td>
      <td>3.93741</td>
      <td>0.00646</td>
      <td>0.64627</td>
      <td>0.08030</td>
      <td>8.02985</td>
      <td>0.01260</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.01500</td>
      <td>-150.00000</td>
      <td>Cycle 30, 2025-08-31 to 2026-01-31</td>
    </tr>
  </tbody>
</table>
</div>


This gives us the following data points:

* Cycle start date
* Cycle end date
* Number of months in the cycle
* Cumulative return during the cycle (decimal and percent)
* Average monthly return during the cycle (decimal and percent)
* Annualized return during the cycle (decimal and percent)
* Return volatility during the cycle
* Cumulative change in FFR during the cycle (decimal and basis points)
* Annualized change in FFR during the cycle (decimal and basis points)

From the above DataFrame, we can then plot the cumulative and annualized returns for each cycle in a bar chart. First, the cumulative returns along with the cumulative change in FFR:


```python
plot_bar_returns_ffr_change(
    cycle_df=hy_bonds_cycles,
    asset_label="HY_BONDS",
    annualized_or_cumulative="Cumulative",
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_57_0.png)
    


And then the annualized returns along with the annualized change in FFR:


```python
plot_bar_returns_ffr_change(
    cycle_df=hy_bonds_cycles,
    asset_label="HY_BONDS",
    annualized_or_cumulative="Annualized",
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_59_0.png)
    


Finally, we can run an OLS regression to check fit:


```python
df = hy_bonds_cycles

#=== Don't modify below this line ===

# Run OLS regression with statsmodels
X = df["FFR_AnnualizedChange_bps"]
y = df["AnnualizedReturnPct"]
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())
print(f"Intercept: {model.params[0]}, Slope: {model.params[1]}")  # Intercept and slope

# Calc X and Y values for regression line
X_vals = np.linspace(X.min(), X.max(), 100)
Y_vals = model.params[0] + model.params[1] * X_vals
```

                                 OLS Regression Results                            
    ===============================================================================
    Dep. Variable:     AnnualizedReturnPct   R-squared:                       0.004
    Model:                             OLS   Adj. R-squared:                 -0.031
    Method:                  Least Squares   F-statistic:                    0.1171
    Date:                 Tue, 24 Feb 2026   Prob (F-statistic):              0.735
    Time:                         13:51:29   Log-Likelihood:                -110.57
    No. Observations:                   30   AIC:                             225.1
    Df Residuals:                       28   BIC:                             227.9
    Df Model:                            1                                         
    Covariance Type:             nonrobust                                         
    ============================================================================================
                                   coef    std err          t      P>|t|      [0.025      0.975]
    --------------------------------------------------------------------------------------------
    const                        6.6113      1.842      3.590      0.001       2.839      10.384
    FFR_AnnualizedChange_bps    -0.0053      0.015     -0.342      0.735      -0.037       0.026
    ==============================================================================
    Omnibus:                        9.087   Durbin-Watson:                   1.936
    Prob(Omnibus):                  0.011   Jarque-Bera (JB):                9.047
    Skew:                          -0.790   Prob(JB):                       0.0109
    Kurtosis:                       5.178   Cond. No.                         120.
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    Intercept: 6.611340605920211, Slope: -0.005299161729553994


And then plot the regression line along with the values:


```python
plot_scatter_regression_ffr_vs_returns(
    cycle_df=treas_10y_cycles,
    asset_label="TREAS_10Y",
    x_vals=X_vals,
    y_vals=Y_vals,
    intercept=model.params[0],
    slope=model.params[1],
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_63_0.png)
    


### Gold

Finally, we'll run a similar process for gold using XAU_Gold USD Spot.

First, we pull data with the following:


```python
bb_clean_data(
    base_directory=DATA_DIR,
    fund_ticker_name="XAU_Gold USD Spot",
    source="Bloomberg",
    asset_class="Commodities",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

gold = load_data(
    base_directory=DATA_DIR,
    ticker="XAU_Gold USD Spot_Clean",
    source="Bloomberg", 
    asset_class="Commodities",
    timeframe="Daily",
    file_format="pickle",
)

# Filter GOLD to date range
gold = gold[(gold.index >= pd.to_datetime(start_date)) & (gold.index <= pd.to_datetime(end_date))]

# Drop everything except the "close" column
gold = gold[["Close"]]

# Resample to monthly frequency
gold_monthly = gold.resample("M").last()
gold_monthly["Monthly_Return"] = gold_monthly["Close"].pct_change()
gold_monthly = gold_monthly.dropna()

display(gold_monthly)
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
      <th>Monthly_Return</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1990-01-31</th>
      <td>415.05000</td>
      <td>0.03439</td>
    </tr>
    <tr>
      <th>1990-02-28</th>
      <td>407.70000</td>
      <td>-0.01771</td>
    </tr>
    <tr>
      <th>1990-03-31</th>
      <td>368.50000</td>
      <td>-0.09615</td>
    </tr>
    <tr>
      <th>1990-04-30</th>
      <td>367.75000</td>
      <td>-0.00204</td>
    </tr>
    <tr>
      <th>1990-05-31</th>
      <td>363.05000</td>
      <td>-0.01278</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2025-09-30</th>
      <td>3858.96000</td>
      <td>0.11920</td>
    </tr>
    <tr>
      <th>2025-10-31</th>
      <td>4002.92000</td>
      <td>0.03731</td>
    </tr>
    <tr>
      <th>2025-11-30</th>
      <td>4239.43000</td>
      <td>0.05908</td>
    </tr>
    <tr>
      <th>2025-12-31</th>
      <td>4319.37000</td>
      <td>0.01886</td>
    </tr>
    <tr>
      <th>2026-01-31</th>
      <td>4894.23000</td>
      <td>0.13309</td>
    </tr>
  </tbody>
</table>
<p>433 rows × 2 columns</p>
</div>


Next, we can plot the price history before calculating the cycle performance:


```python
plot_timeseries(
    price_df=gold,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["Close"],
    title="XAU Gold USD Spot Daily Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_rotation=45,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=400,
    grid=True,
    legend=False,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_67_0.png)
    


Next, we will calculate the performance of gold based on the pre-defined Fed cycles:


```python
gold_cycles = calc_fed_cycle_asset_performance(
    start_date=cycle_ranges["start_date"],
    end_date=cycle_ranges["end_date"],
    label=cycle_ranges["cycle_label"],
    fed_funds_change=cycle_ranges["fed_funds_change"],
    monthly_returns=gold_monthly,
)

display(gold_cycles)
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
      <th>Cycle</th>
      <th>Start</th>
      <th>End</th>
      <th>Months</th>
      <th>CumulativeReturn</th>
      <th>CumulativeReturnPct</th>
      <th>AverageMonthlyReturn</th>
      <th>AverageMonthlyReturnPct</th>
      <th>AnnualizedReturn</th>
      <th>AnnualizedReturnPct</th>
      <th>Volatility</th>
      <th>FedFundsChange</th>
      <th>FedFundsChange_bps</th>
      <th>FFR_AnnualizedChange</th>
      <th>FFR_AnnualizedChange_bps</th>
      <th>Label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Cycle 1</td>
      <td>1989-12-31</td>
      <td>1990-06-30</td>
      <td>6</td>
      <td>-0.12224</td>
      <td>-12.22430</td>
      <td>-0.02069</td>
      <td>-2.06945</td>
      <td>-0.22954</td>
      <td>-22.95426</td>
      <td>0.14885</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 1, 1989-12-31 to 1990-06-30</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Cycle 2</td>
      <td>1990-06-30</td>
      <td>1993-03-31</td>
      <td>34</td>
      <td>-0.06624</td>
      <td>-6.62443</td>
      <td>-0.00158</td>
      <td>-0.15839</td>
      <td>-0.02390</td>
      <td>-2.39005</td>
      <td>0.10292</td>
      <td>-0.05250</td>
      <td>-525.00000</td>
      <td>-0.01853</td>
      <td>-185.29412</td>
      <td>Cycle 2, 1990-06-30 to 1993-03-31</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Cycle 3</td>
      <td>1993-03-31</td>
      <td>1994-01-31</td>
      <td>11</td>
      <td>0.15903</td>
      <td>15.90288</td>
      <td>0.01462</td>
      <td>1.46238</td>
      <td>0.17468</td>
      <td>17.46838</td>
      <td>0.17075</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 3, 1993-03-31 to 1994-01-31</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Cycle 4</td>
      <td>1994-01-31</td>
      <td>1995-06-30</td>
      <td>18</td>
      <td>-0.01561</td>
      <td>-1.56130</td>
      <td>-0.00070</td>
      <td>-0.06966</td>
      <td>-0.01044</td>
      <td>-1.04359</td>
      <td>0.06717</td>
      <td>0.03000</td>
      <td>300.00000</td>
      <td>0.02000</td>
      <td>200.00000</td>
      <td>Cycle 4, 1994-01-31 to 1995-06-30</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Cycle 5</td>
      <td>1995-06-30</td>
      <td>1996-07-31</td>
      <td>14</td>
      <td>0.00716</td>
      <td>0.71559</td>
      <td>0.00066</td>
      <td>0.06552</td>
      <td>0.00613</td>
      <td>0.61305</td>
      <td>0.06186</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00643</td>
      <td>-64.28571</td>
      <td>Cycle 5, 1995-06-30 to 1996-07-31</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Cycle 6</td>
      <td>1996-07-31</td>
      <td>1997-02-28</td>
      <td>8</td>
      <td>-0.04468</td>
      <td>-4.46839</td>
      <td>-0.00519</td>
      <td>-0.51936</td>
      <td>-0.06627</td>
      <td>-6.62715</td>
      <td>0.11737</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 6, 1996-07-31 to 1997-02-28</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Cycle 7</td>
      <td>1997-02-28</td>
      <td>1997-09-30</td>
      <td>8</td>
      <td>-0.02875</td>
      <td>-2.87498</td>
      <td>-0.00313</td>
      <td>-0.31292</td>
      <td>-0.04281</td>
      <td>-4.28133</td>
      <td>0.11886</td>
      <td>0.00250</td>
      <td>25.00000</td>
      <td>0.00375</td>
      <td>37.50000</td>
      <td>Cycle 7, 1997-02-28 to 1997-09-30</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Cycle 8</td>
      <td>1997-09-30</td>
      <td>1998-08-31</td>
      <td>12</td>
      <td>-0.14993</td>
      <td>-14.99306</td>
      <td>-0.01285</td>
      <td>-1.28489</td>
      <td>-0.14993</td>
      <td>-14.99306</td>
      <td>0.12433</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 8, 1997-09-30 to 1998-08-31</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Cycle 9</td>
      <td>1998-08-31</td>
      <td>1999-05-31</td>
      <td>10</td>
      <td>-0.05621</td>
      <td>-5.62053</td>
      <td>-0.00517</td>
      <td>-0.51718</td>
      <td>-0.06706</td>
      <td>-6.70614</td>
      <td>0.12709</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00900</td>
      <td>-90.00000</td>
      <td>Cycle 9, 1998-08-31 to 1999-05-31</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Cycle 10</td>
      <td>1999-05-31</td>
      <td>2000-11-30</td>
      <td>19</td>
      <td>-0.05619</td>
      <td>-5.61857</td>
      <td>-0.00193</td>
      <td>-0.19269</td>
      <td>-0.03586</td>
      <td>-3.58627</td>
      <td>0.17333</td>
      <td>0.01750</td>
      <td>175.00000</td>
      <td>0.01105</td>
      <td>110.52632</td>
      <td>Cycle 10, 1999-05-31 to 2000-11-30</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Cycle 11</td>
      <td>2000-11-30</td>
      <td>2000-12-31</td>
      <td>2</td>
      <td>0.02678</td>
      <td>2.67773</td>
      <td>0.01332</td>
      <td>1.33221</td>
      <td>0.17181</td>
      <td>17.18109</td>
      <td>0.03266</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 11, 2000-11-30 to 2000-12-31</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Cycle 12</td>
      <td>2000-12-31</td>
      <td>2002-06-30</td>
      <td>19</td>
      <td>0.16269</td>
      <td>16.26918</td>
      <td>0.00844</td>
      <td>0.84406</td>
      <td>0.09988</td>
      <td>9.98819</td>
      <td>0.11022</td>
      <td>-0.04750</td>
      <td>-475.00000</td>
      <td>-0.03000</td>
      <td>-300.00000</td>
      <td>Cycle 12, 2000-12-31 to 2002-06-30</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Cycle 13</td>
      <td>2002-06-30</td>
      <td>2002-10-31</td>
      <td>5</td>
      <td>-0.02695</td>
      <td>-2.69484</td>
      <td>-0.00496</td>
      <td>-0.49607</td>
      <td>-0.06346</td>
      <td>-6.34605</td>
      <td>0.12104</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 13, 2002-06-30 to 2002-10-31</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Cycle 14</td>
      <td>2002-10-31</td>
      <td>2003-12-31</td>
      <td>15</td>
      <td>0.28404</td>
      <td>28.40365</td>
      <td>0.01772</td>
      <td>1.77192</td>
      <td>0.22141</td>
      <td>22.14112</td>
      <td>0.15439</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.00600</td>
      <td>-60.00000</td>
      <td>Cycle 14, 2002-10-31 to 2003-12-31</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Cycle 15</td>
      <td>2003-12-31</td>
      <td>2004-05-31</td>
      <td>6</td>
      <td>-0.00653</td>
      <td>-0.65302</td>
      <td>0.00044</td>
      <td>0.04419</td>
      <td>-0.01302</td>
      <td>-1.30178</td>
      <td>0.20868</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 15, 2003-12-31 to 2004-05-31</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Cycle 16</td>
      <td>2004-05-31</td>
      <td>2006-12-31</td>
      <td>32</td>
      <td>0.64628</td>
      <td>64.62831</td>
      <td>0.01653</td>
      <td>1.65326</td>
      <td>0.20556</td>
      <td>20.55610</td>
      <td>0.14568</td>
      <td>0.04250</td>
      <td>425.00000</td>
      <td>0.01594</td>
      <td>159.37500</td>
      <td>Cycle 16, 2004-05-31 to 2006-12-31</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Cycle 17</td>
      <td>2006-12-31</td>
      <td>2007-08-31</td>
      <td>9</td>
      <td>0.03904</td>
      <td>3.90432</td>
      <td>0.00447</td>
      <td>0.44660</td>
      <td>0.05239</td>
      <td>5.23935</td>
      <td>0.07374</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 17, 2006-12-31 to 2007-08-31</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Cycle 18</td>
      <td>2007-08-31</td>
      <td>2009-07-31</td>
      <td>24</td>
      <td>0.43610</td>
      <td>43.60981</td>
      <td>0.01766</td>
      <td>1.76641</td>
      <td>0.19837</td>
      <td>19.83731</td>
      <td>0.24658</td>
      <td>-0.05000</td>
      <td>-500.00000</td>
      <td>-0.02500</td>
      <td>-250.00000</td>
      <td>Cycle 18, 2007-08-31 to 2009-07-31</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Cycle 19</td>
      <td>2009-07-31</td>
      <td>2015-11-30</td>
      <td>77</td>
      <td>0.14924</td>
      <td>14.92391</td>
      <td>0.00317</td>
      <td>0.31742</td>
      <td>0.02191</td>
      <td>2.19146</td>
      <td>0.18253</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 19, 2009-07-31 to 2015-11-30</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Cycle 20</td>
      <td>2015-11-30</td>
      <td>2016-06-30</td>
      <td>8</td>
      <td>0.15742</td>
      <td>15.74192</td>
      <td>0.02027</td>
      <td>2.02679</td>
      <td>0.24519</td>
      <td>24.51911</td>
      <td>0.22531</td>
      <td>0.00250</td>
      <td>25.00000</td>
      <td>0.00375</td>
      <td>37.50000</td>
      <td>Cycle 20, 2015-11-30 to 2016-06-30</td>
    </tr>
    <tr>
      <th>20</th>
      <td>Cycle 21</td>
      <td>2016-06-30</td>
      <td>2016-11-30</td>
      <td>6</td>
      <td>-0.03466</td>
      <td>-3.46575</td>
      <td>-0.00449</td>
      <td>-0.44887</td>
      <td>-0.06811</td>
      <td>-6.81139</td>
      <td>0.19940</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 21, 2016-06-30 to 2016-11-30</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Cycle 22</td>
      <td>2016-11-30</td>
      <td>2019-06-30</td>
      <td>32</td>
      <td>0.10362</td>
      <td>10.36165</td>
      <td>0.00355</td>
      <td>0.35519</td>
      <td>0.03766</td>
      <td>3.76642</td>
      <td>0.10758</td>
      <td>0.02000</td>
      <td>200.00000</td>
      <td>0.00750</td>
      <td>75.00000</td>
      <td>Cycle 22, 2016-11-30 to 2019-06-30</td>
    </tr>
    <tr>
      <th>22</th>
      <td>Cycle 23</td>
      <td>2019-06-30</td>
      <td>2019-07-31</td>
      <td>2</td>
      <td>0.08288</td>
      <td>8.28750</td>
      <td>0.04132</td>
      <td>4.13180</td>
      <td>0.61239</td>
      <td>61.23899</td>
      <td>0.18771</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 23, 2019-06-30 to 2019-07-31</td>
    </tr>
    <tr>
      <th>23</th>
      <td>Cycle 24</td>
      <td>2019-07-31</td>
      <td>2020-09-30</td>
      <td>15</td>
      <td>0.33789</td>
      <td>33.78880</td>
      <td>0.02043</td>
      <td>2.04336</td>
      <td>0.26222</td>
      <td>26.22222</td>
      <td>0.14899</td>
      <td>-0.02250</td>
      <td>-225.00000</td>
      <td>-0.01800</td>
      <td>-180.00000</td>
      <td>Cycle 24, 2019-07-31 to 2020-09-30</td>
    </tr>
    <tr>
      <th>24</th>
      <td>Cycle 25</td>
      <td>2020-09-30</td>
      <td>2022-02-28</td>
      <td>18</td>
      <td>-0.02989</td>
      <td>-2.98862</td>
      <td>-0.00076</td>
      <td>-0.07561</td>
      <td>-0.02002</td>
      <td>-2.00247</td>
      <td>0.15388</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 25, 2020-09-30 to 2022-02-28</td>
    </tr>
    <tr>
      <th>25</th>
      <td>Cycle 26</td>
      <td>2022-02-28</td>
      <td>2024-01-31</td>
      <td>24</td>
      <td>0.13485</td>
      <td>13.48509</td>
      <td>0.00605</td>
      <td>0.60516</td>
      <td>0.06529</td>
      <td>6.52938</td>
      <td>0.13996</td>
      <td>0.05250</td>
      <td>525.00000</td>
      <td>0.02625</td>
      <td>262.50000</td>
      <td>Cycle 26, 2022-02-28 to 2024-01-31</td>
    </tr>
    <tr>
      <th>26</th>
      <td>Cycle 27</td>
      <td>2024-01-31</td>
      <td>2024-08-31</td>
      <td>8</td>
      <td>0.21348</td>
      <td>21.34824</td>
      <td>0.02494</td>
      <td>2.49353</td>
      <td>0.33675</td>
      <td>33.67502</td>
      <td>0.11399</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 27, 2024-01-31 to 2024-08-31</td>
    </tr>
    <tr>
      <th>27</th>
      <td>Cycle 28</td>
      <td>2024-08-31</td>
      <td>2025-06-30</td>
      <td>11</td>
      <td>0.34954</td>
      <td>34.95424</td>
      <td>0.02824</td>
      <td>2.82419</td>
      <td>0.38683</td>
      <td>38.68250</td>
      <td>0.12923</td>
      <td>-0.01000</td>
      <td>-100.00000</td>
      <td>-0.01091</td>
      <td>-109.09091</td>
      <td>Cycle 28, 2024-08-31 to 2025-06-30</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Cycle 29</td>
      <td>2025-06-30</td>
      <td>2025-08-31</td>
      <td>3</td>
      <td>0.04825</td>
      <td>4.82481</td>
      <td>0.01609</td>
      <td>1.60850</td>
      <td>0.20741</td>
      <td>20.74143</td>
      <td>0.09689</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>Cycle 29, 2025-06-30 to 2025-08-31</td>
    </tr>
    <tr>
      <th>29</th>
      <td>Cycle 30</td>
      <td>2025-08-31</td>
      <td>2026-01-31</td>
      <td>6</td>
      <td>0.48764</td>
      <td>48.76396</td>
      <td>0.06926</td>
      <td>6.92618</td>
      <td>1.21307</td>
      <td>121.30714</td>
      <td>0.16013</td>
      <td>-0.00750</td>
      <td>-75.00000</td>
      <td>-0.01500</td>
      <td>-150.00000</td>
      <td>Cycle 30, 2025-08-31 to 2026-01-31</td>
    </tr>
  </tbody>
</table>
</div>


This gives us the following data points:

* Cycle start date
* Cycle end date
* Number of months in the cycle
* Cumulative return during the cycle (decimal and percent)
* Average monthly return during the cycle (decimal and percent)
* Annualized return during the cycle (decimal and percent)
* Return volatility during the cycle
* Cumulative change in FFR during the cycle (decimal and basis points)
* Annualized change in FFR during the cycle (decimal and basis points)

From the above DataFrame, we can then plot the cumulative and annualized returns for each cycle in a bar chart. First, the cumulative returns along with the cumulative change in FFR:


```python
plot_bar_returns_ffr_change(
    cycle_df=gold_cycles,
    asset_label="GOLD",
    annualized_or_cumulative="Cumulative",
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_71_0.png)
    


And then the annualized returns along with the annualized change in FFR:


```python
plot_bar_returns_ffr_change(
    cycle_df=gold_cycles,
    asset_label="GOLD",
    annualized_or_cumulative="Annualized",
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_73_0.png)
    


We see strong returns for gold across several different Fed cycles, so it is difficult to draw any kind of initial conclusion based on the bar charts.

Finally, we can run an OLS regression to check fit:


```python
df = gold_cycles

#=== Don't modify below this line ===

# Run OLS regression with statsmodels
X = df["FFR_AnnualizedChange_bps"]
y = df["AnnualizedReturnPct"]
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())
print(f"Intercept: {model.params[0]}, Slope: {model.params[1]}")  # Intercept and slope

# Calc X and Y values for regression line
X_vals = np.linspace(X.min(), X.max(), 100)
Y_vals = model.params[0] + model.params[1] * X_vals
```

                                 OLS Regression Results                            
    ===============================================================================
    Dep. Variable:     AnnualizedReturnPct   R-squared:                       0.064
    Model:                             OLS   Adj. R-squared:                  0.030
    Method:                  Least Squares   F-statistic:                     1.900
    Date:                 Tue, 24 Feb 2026   Prob (F-statistic):              0.179
    Time:                         13:51:32   Log-Likelihood:                -140.03
    No. Observations:                   30   AIC:                             284.1
    Df Residuals:                       28   BIC:                             286.9
    Df Model:                            1                                         
    Covariance Type:             nonrobust                                         
    ============================================================================================
                                   coef    std err          t      P>|t|      [0.025      0.975]
    --------------------------------------------------------------------------------------------
    const                       11.4670      4.917      2.332      0.027       1.396      21.539
    FFR_AnnualizedChange_bps    -0.0570      0.041     -1.378      0.179      -0.142       0.028
    ==============================================================================
    Omnibus:                       28.991   Durbin-Watson:                   1.081
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):               62.894
    Skew:                           2.093   Prob(JB):                     2.20e-14
    Kurtosis:                       8.727   Cond. No.                         120.
    ==============================================================================
    
    Notes:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    Intercept: 11.467013480569243, Slope: -0.056974234027166226


And then plot the regression line along with the values:


```python
plot_scatter_regression_ffr_vs_returns(
    cycle_df=gold_cycles,
    asset_label="GOLD",
    x_vals=X_vals,
    y_vals=Y_vals,
    intercept=model.params[0],
    slope=model.params[1],
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_77_0.png)
    


It's difficult to draw any strong conclusions with the above plot. Gold has traditionally been considered a hedge for inflation, and while one of the Fed's mandates is to manage inflation, there may not be a conclusion to draw in relationship to the historical returns that gold has exhibited.

## Hybrid Portfolio

With the above analysis (somewhat) complete, let's look at the optimal allocation for a portfolio based on the data and the hypythetical historical results.

### Asset Allocation

We have to be careful with our criteria for when to hold stocks, bonds, or gold, as hindsight bias is certainly possible. So, without overanalyzing the results, let's assume that we hold stocks as the default position during tightening cycles, and then hold bonds during easing cycles when the Fed starts cutting rates, and then resume holding stocks when the Fed stops cutting rates. If there is not any change in FFR, then we still hold stocks.

We can then combine the return series based on the above with the following:


```python
# Shift the "cycle_filled" column down by one row to create a new column called "cycle_invested" that represents the cycle label that an investor would be invested in for each month (i.e. the cycle label from the previous month)

fedfunds_grouped_cycles['cycle_invested'] = fedfunds_grouped_cycles['cycle_filled'].shift(1)

display(fedfunds_grouped_cycles)
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
      <th>start_date</th>
      <th>fed_funds_start</th>
      <th>end_date</th>
      <th>fed_funds_end</th>
      <th>fed_funds_change</th>
      <th>cycle</th>
      <th>cycle_filled</th>
      <th>group</th>
      <th>cycle_invested</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1989-12-31</td>
      <td>0.08250</td>
      <td>1990-01-31</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1990-01-31</td>
      <td>0.08250</td>
      <td>1990-02-28</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>Modified Tightening</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1990-02-28</td>
      <td>0.08250</td>
      <td>1990-03-31</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>Modified Tightening</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1990-03-31</td>
      <td>0.08250</td>
      <td>1990-04-30</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>Modified Tightening</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1990-04-30</td>
      <td>0.08250</td>
      <td>1990-05-31</td>
      <td>0.08250</td>
      <td>0.00000</td>
      <td>Neutral</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>Modified Tightening</td>
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
      <th>429</th>
      <td>2025-09-30</td>
      <td>0.04250</td>
      <td>2025-10-31</td>
      <td>0.04000</td>
      <td>-0.00250</td>
      <td>Easing</td>
      <td>Easing</td>
      <td>30</td>
      <td>Easing</td>
    </tr>
    <tr>
      <th>430</th>
      <td>2025-10-31</td>
      <td>0.04000</td>
      <td>2025-11-30</td>
      <td>0.04000</td>
      <td>0.00000</td>
      <td>Neutral</td>
      <td>Easing</td>
      <td>30</td>
      <td>Easing</td>
    </tr>
    <tr>
      <th>431</th>
      <td>2025-11-30</td>
      <td>0.04000</td>
      <td>2025-12-31</td>
      <td>0.03750</td>
      <td>-0.00250</td>
      <td>Easing</td>
      <td>Easing</td>
      <td>30</td>
      <td>Easing</td>
    </tr>
    <tr>
      <th>432</th>
      <td>2025-12-31</td>
      <td>0.03750</td>
      <td>2026-01-31</td>
      <td>0.03750</td>
      <td>0.00000</td>
      <td>Neutral</td>
      <td>Easing</td>
      <td>30</td>
      <td>Easing</td>
    </tr>
    <tr>
      <th>433</th>
      <td>2026-01-31</td>
      <td>0.03750</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>Neutral</td>
      <td>Easing</td>
      <td>30</td>
      <td>Easing</td>
    </tr>
  </tbody>
</table>
<p>434 rows × 9 columns</p>
</div>



```python
# Reset index to merge on date
stocks_merged = pd.merge_asof(
    spxt_monthly.reset_index(),
    fedfunds_grouped_cycles[['start_date', 'end_date', 'cycle_invested', 'group']],
    left_on='Date',
    right_on='start_date',
    direction='backward'
)

# Drop rows where the date falls outside the cycle's end_date
stocks_merged = stocks_merged[stocks_merged['Date'] <= stocks_merged['end_date']]

display(stocks_merged)
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
      <th>Date</th>
      <th>Close</th>
      <th>Monthly_Return</th>
      <th>start_date</th>
      <th>end_date</th>
      <th>cycle_invested</th>
      <th>group</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1990-01-31</td>
      <td>353.94000</td>
      <td>-0.06713</td>
      <td>1990-01-31</td>
      <td>1990-02-28</td>
      <td>Modified Tightening</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1990-02-28</td>
      <td>358.50000</td>
      <td>0.01288</td>
      <td>1990-02-28</td>
      <td>1990-03-31</td>
      <td>Modified Tightening</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1990-03-31</td>
      <td>368</td>
      <td>0.02650</td>
      <td>1990-03-31</td>
      <td>1990-04-30</td>
      <td>Modified Tightening</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1990-04-30</td>
      <td>358.81000</td>
      <td>-0.02497</td>
      <td>1990-04-30</td>
      <td>1990-05-31</td>
      <td>Modified Tightening</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1990-05-31</td>
      <td>393.80000</td>
      <td>0.09752</td>
      <td>1990-05-31</td>
      <td>1990-06-30</td>
      <td>Modified Tightening</td>
      <td>1</td>
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
    </tr>
    <tr>
      <th>427</th>
      <td>2025-08-31</td>
      <td>14304.68000</td>
      <td>0.02027</td>
      <td>2025-08-31</td>
      <td>2025-09-30</td>
      <td>Modified Tightening</td>
      <td>30</td>
    </tr>
    <tr>
      <th>428</th>
      <td>2025-09-30</td>
      <td>14826.80000</td>
      <td>0.03650</td>
      <td>2025-09-30</td>
      <td>2025-10-31</td>
      <td>Easing</td>
      <td>30</td>
    </tr>
    <tr>
      <th>429</th>
      <td>2025-10-31</td>
      <td>15173.95000</td>
      <td>0.02341</td>
      <td>2025-10-31</td>
      <td>2025-11-30</td>
      <td>Easing</td>
      <td>30</td>
    </tr>
    <tr>
      <th>430</th>
      <td>2025-11-30</td>
      <td>15211.14000</td>
      <td>0.00245</td>
      <td>2025-11-30</td>
      <td>2025-12-31</td>
      <td>Easing</td>
      <td>30</td>
    </tr>
    <tr>
      <th>431</th>
      <td>2025-12-31</td>
      <td>15220.45000</td>
      <td>0.00061</td>
      <td>2025-12-31</td>
      <td>2026-01-31</td>
      <td>Easing</td>
      <td>30</td>
    </tr>
  </tbody>
</table>
<p>432 rows × 7 columns</p>
</div>



```python
# Reset index to merge on date
bonds_merged = pd.merge_asof(
    treas_10y_monthly.reset_index(),
    fedfunds_grouped_cycles[['start_date', 'end_date', 'cycle_invested', 'group']],
    left_on='Date',
    right_on='start_date',
    direction='backward'
)

# Drop rows where the date falls outside the cycle's end_date
bonds_merged = bonds_merged[bonds_merged['Date'] <= bonds_merged['end_date']]

display(bonds_merged)
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
      <th>Date</th>
      <th>Close</th>
      <th>Monthly_Return</th>
      <th>start_date</th>
      <th>end_date</th>
      <th>cycle_invested</th>
      <th>group</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1990-01-31</td>
      <td>98.01300</td>
      <td>-0.01987</td>
      <td>1990-01-31</td>
      <td>1990-02-28</td>
      <td>Modified Tightening</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1990-02-28</td>
      <td>97.99000</td>
      <td>-0.00023</td>
      <td>1990-02-28</td>
      <td>1990-03-31</td>
      <td>Modified Tightening</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1990-03-31</td>
      <td>97.98900</td>
      <td>-0.00001</td>
      <td>1990-03-31</td>
      <td>1990-04-30</td>
      <td>Modified Tightening</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1990-04-30</td>
      <td>96.60600</td>
      <td>-0.01411</td>
      <td>1990-04-30</td>
      <td>1990-05-31</td>
      <td>Modified Tightening</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1990-05-31</td>
      <td>99.64700</td>
      <td>0.03148</td>
      <td>1990-05-31</td>
      <td>1990-06-30</td>
      <td>Modified Tightening</td>
      <td>1</td>
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
    </tr>
    <tr>
      <th>427</th>
      <td>2025-08-31</td>
      <td>641.25800</td>
      <td>0.01668</td>
      <td>2025-08-31</td>
      <td>2025-09-30</td>
      <td>Modified Tightening</td>
      <td>30</td>
    </tr>
    <tr>
      <th>428</th>
      <td>2025-09-30</td>
      <td>645.58400</td>
      <td>0.00675</td>
      <td>2025-09-30</td>
      <td>2025-10-31</td>
      <td>Easing</td>
      <td>30</td>
    </tr>
    <tr>
      <th>429</th>
      <td>2025-10-31</td>
      <td>650.00500</td>
      <td>0.00685</td>
      <td>2025-10-31</td>
      <td>2025-11-30</td>
      <td>Easing</td>
      <td>30</td>
    </tr>
    <tr>
      <th>430</th>
      <td>2025-11-30</td>
      <td>656.63600</td>
      <td>0.01020</td>
      <td>2025-11-30</td>
      <td>2025-12-31</td>
      <td>Easing</td>
      <td>30</td>
    </tr>
    <tr>
      <th>431</th>
      <td>2025-12-31</td>
      <td>652.28800</td>
      <td>-0.00662</td>
      <td>2025-12-31</td>
      <td>2026-01-31</td>
      <td>Easing</td>
      <td>30</td>
    </tr>
  </tbody>
</table>
<p>432 rows × 7 columns</p>
</div>



```python
# Select the appropriate return based on cycle
stocks_merged['strategy_return'] = stocks_merged.apply(
    lambda row: row['Monthly_Return'] if row['cycle_invested'] in ['Tightening', 'Modified Tightening'] else None,
    axis=1
)

bonds_merged['strategy_return'] = bonds_merged.apply(
    lambda row: row['Monthly_Return'] if row['cycle_invested'] == 'Easing' else None,
    axis=1
)

# Combine
strategy = pd.concat([stocks_merged, bonds_merged]).dropna(subset=['strategy_return'])
strategy = strategy.sort_values('Date')

display(strategy.head(20))
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
      <th>Date</th>
      <th>Close</th>
      <th>Monthly_Return</th>
      <th>start_date</th>
      <th>end_date</th>
      <th>cycle_invested</th>
      <th>group</th>
      <th>strategy_return</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1990-01-31</td>
      <td>353.94000</td>
      <td>-0.06713</td>
      <td>1990-01-31</td>
      <td>1990-02-28</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>-0.06713</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1990-02-28</td>
      <td>358.50000</td>
      <td>0.01288</td>
      <td>1990-02-28</td>
      <td>1990-03-31</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>0.01288</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1990-03-31</td>
      <td>368</td>
      <td>0.02650</td>
      <td>1990-03-31</td>
      <td>1990-04-30</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>0.02650</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1990-04-30</td>
      <td>358.81000</td>
      <td>-0.02497</td>
      <td>1990-04-30</td>
      <td>1990-05-31</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>-0.02497</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1990-05-31</td>
      <td>393.80000</td>
      <td>0.09752</td>
      <td>1990-05-31</td>
      <td>1990-06-30</td>
      <td>Modified Tightening</td>
      <td>1</td>
      <td>0.09752</td>
    </tr>
    <tr>
      <th>5</th>
      <td>1990-06-30</td>
      <td>391.14000</td>
      <td>-0.00675</td>
      <td>1990-06-30</td>
      <td>1990-07-31</td>
      <td>Modified Tightening</td>
      <td>2</td>
      <td>-0.00675</td>
    </tr>
    <tr>
      <th>6</th>
      <td>1990-07-31</td>
      <td>102.84500</td>
      <td>0.01463</td>
      <td>1990-07-31</td>
      <td>1990-08-31</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.01463</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1990-08-31</td>
      <td>100.78200</td>
      <td>-0.02006</td>
      <td>1990-08-31</td>
      <td>1990-09-30</td>
      <td>Easing</td>
      <td>2</td>
      <td>-0.02006</td>
    </tr>
    <tr>
      <th>8</th>
      <td>1990-09-30</td>
      <td>101.74000</td>
      <td>0.00951</td>
      <td>1990-09-30</td>
      <td>1990-10-31</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.00951</td>
    </tr>
    <tr>
      <th>9</th>
      <td>1990-10-31</td>
      <td>103.65200</td>
      <td>0.01879</td>
      <td>1990-10-31</td>
      <td>1990-11-30</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.01879</td>
    </tr>
    <tr>
      <th>10</th>
      <td>1990-11-30</td>
      <td>106.43100</td>
      <td>0.02681</td>
      <td>1990-11-30</td>
      <td>1990-12-31</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.02681</td>
    </tr>
    <tr>
      <th>11</th>
      <td>1990-12-31</td>
      <td>108.24900</td>
      <td>0.01708</td>
      <td>1990-12-31</td>
      <td>1991-01-31</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.01708</td>
    </tr>
    <tr>
      <th>12</th>
      <td>1991-01-31</td>
      <td>109.52500</td>
      <td>0.01179</td>
      <td>1991-01-31</td>
      <td>1991-02-28</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.01179</td>
    </tr>
    <tr>
      <th>13</th>
      <td>1991-02-28</td>
      <td>110.10400</td>
      <td>0.00529</td>
      <td>1991-02-28</td>
      <td>1991-03-31</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.00529</td>
    </tr>
    <tr>
      <th>14</th>
      <td>1991-03-31</td>
      <td>110.43400</td>
      <td>0.00300</td>
      <td>1991-03-31</td>
      <td>1991-04-30</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.00300</td>
    </tr>
    <tr>
      <th>15</th>
      <td>1991-04-30</td>
      <td>111.59800</td>
      <td>0.01054</td>
      <td>1991-04-30</td>
      <td>1991-05-31</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.01054</td>
    </tr>
    <tr>
      <th>16</th>
      <td>1991-05-31</td>
      <td>112.07800</td>
      <td>0.00430</td>
      <td>1991-05-31</td>
      <td>1991-06-30</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.00430</td>
    </tr>
    <tr>
      <th>17</th>
      <td>1991-06-30</td>
      <td>111.50200</td>
      <td>-0.00514</td>
      <td>1991-06-30</td>
      <td>1991-07-31</td>
      <td>Easing</td>
      <td>2</td>
      <td>-0.00514</td>
    </tr>
    <tr>
      <th>18</th>
      <td>1991-07-31</td>
      <td>113.05200</td>
      <td>0.01390</td>
      <td>1991-07-31</td>
      <td>1991-08-31</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.01390</td>
    </tr>
    <tr>
      <th>19</th>
      <td>1991-08-31</td>
      <td>116.06500</td>
      <td>0.02665</td>
      <td>1991-08-31</td>
      <td>1991-09-30</td>
      <td>Easing</td>
      <td>2</td>
      <td>0.02665</td>
    </tr>
  </tbody>
</table>
</div>



```python
# Calculate cumulative returns and drawdown for spxt
spxt_monthly['Cumulative_Return'] = (1 + spxt_monthly['Monthly_Return']).cumprod() - 1
spxt_monthly['Cumulative_Return_Plus_One'] = 1 + spxt_monthly['Cumulative_Return']
spxt_monthly['Rolling_Max'] = spxt_monthly['Cumulative_Return_Plus_One'].cummax()
spxt_monthly['Drawdown'] = spxt_monthly['Cumulative_Return_Plus_One'] / spxt_monthly['Rolling_Max'] - 1
spxt_monthly.drop(columns=['Cumulative_Return_Plus_One', 'Rolling_Max'], inplace=True)

# Calculate cumulative returns and drawdown for treas_10y
treas_10y_monthly['Cumulative_Return'] = (1 + treas_10y_monthly['Monthly_Return']).cumprod() - 1
treas_10y_monthly['Cumulative_Return_Plus_One'] = 1 + treas_10y_monthly['Cumulative_Return']
treas_10y_monthly['Rolling_Max'] = treas_10y_monthly['Cumulative_Return_Plus_One'].cummax()
treas_10y_monthly['Drawdown'] = treas_10y_monthly['Cumulative_Return_Plus_One'] / treas_10y_monthly['Rolling_Max'] - 1
treas_10y_monthly.drop(columns=['Cumulative_Return_Plus_One', 'Rolling_Max'], inplace=True)

# Convert to DataFrame
portfolio_monthly = strategy[['Date', 'strategy_return']].copy().set_index('Date')
portfolio_monthly = portfolio_monthly.rename(columns={'strategy_return': 'Portfolio_Monthly_Return'})

# Calculate cumulative returns and drawdown for the portfolio
portfolio_monthly['Portfolio_Cumulative_Return'] = (1 + portfolio_monthly['Portfolio_Monthly_Return']).cumprod() - 1
portfolio_monthly['Portfolio_Cumulative_Return_Plus_One'] = 1 + portfolio_monthly['Portfolio_Cumulative_Return']
portfolio_monthly['Portfolio_Rolling_Max'] = portfolio_monthly['Portfolio_Cumulative_Return_Plus_One'].cummax()
portfolio_monthly['Portfolio_Drawdown'] = portfolio_monthly['Portfolio_Cumulative_Return_Plus_One'] / portfolio_monthly['Portfolio_Rolling_Max'] - 1
portfolio_monthly.drop(columns=['Portfolio_Cumulative_Return_Plus_One', 'Portfolio_Rolling_Max'], inplace=True)

# Merge "spxt_monthly" and "treas_10y_monthly" into "portfolio_monthly" to compare cumulative returns
portfolio_monthly = portfolio_monthly.join(
    spxt_monthly['Monthly_Return'].rename('SPXT_Monthly_Return'),
    how='left'
).join(
    spxt_monthly['Cumulative_Return'].rename('SPXT_Cumulative_Return'),
    how='left'
).join(
    spxt_monthly['Drawdown'].rename('SPXT_Drawdown'),
    how='left'
).join(
    treas_10y_monthly['Monthly_Return'].rename('10Y_Monthly_Return'),
    how='left'
).join(
    treas_10y_monthly['Cumulative_Return'].rename('10Y_Cumulative_Return'),
    how='left'
).join(
    treas_10y_monthly['Drawdown'].rename('10Y_Drawdown'),
    how='left'
)
```


```python
display(portfolio_monthly)
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
      <th>Portfolio_Monthly_Return</th>
      <th>Portfolio_Cumulative_Return</th>
      <th>Portfolio_Drawdown</th>
      <th>SPXT_Monthly_Return</th>
      <th>SPXT_Cumulative_Return</th>
      <th>SPXT_Drawdown</th>
      <th>10Y_Monthly_Return</th>
      <th>10Y_Cumulative_Return</th>
      <th>10Y_Drawdown</th>
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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1990-01-31</th>
      <td>-0.06713</td>
      <td>-0.06713</td>
      <td>0.00000</td>
      <td>-0.06713</td>
      <td>-0.06713</td>
      <td>0.00000</td>
      <td>-0.01987</td>
      <td>-0.01987</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>1990-02-28</th>
      <td>0.01288</td>
      <td>-0.05511</td>
      <td>0.00000</td>
      <td>0.01288</td>
      <td>-0.05511</td>
      <td>0.00000</td>
      <td>-0.00023</td>
      <td>-0.02010</td>
      <td>-0.00023</td>
    </tr>
    <tr>
      <th>1990-03-31</th>
      <td>0.02650</td>
      <td>-0.03007</td>
      <td>0.00000</td>
      <td>0.02650</td>
      <td>-0.03007</td>
      <td>0.00000</td>
      <td>-0.00001</td>
      <td>-0.02011</td>
      <td>-0.00024</td>
    </tr>
    <tr>
      <th>1990-04-30</th>
      <td>-0.02497</td>
      <td>-0.05429</td>
      <td>-0.02497</td>
      <td>-0.02497</td>
      <td>-0.05429</td>
      <td>-0.02497</td>
      <td>-0.01411</td>
      <td>-0.03394</td>
      <td>-0.01436</td>
    </tr>
    <tr>
      <th>1990-05-31</th>
      <td>0.09752</td>
      <td>0.03793</td>
      <td>0.00000</td>
      <td>0.09752</td>
      <td>0.03793</td>
      <td>0.00000</td>
      <td>0.03148</td>
      <td>-0.00353</td>
      <td>0.00000</td>
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
      <th>2025-08-31</th>
      <td>0.02027</td>
      <td>42.28506</td>
      <td>0.00000</td>
      <td>0.02027</td>
      <td>36.70243</td>
      <td>0.00000</td>
      <td>0.01668</td>
      <td>5.41258</td>
      <td>-0.11316</td>
    </tr>
    <tr>
      <th>2025-09-30</th>
      <td>0.00675</td>
      <td>42.57706</td>
      <td>0.00000</td>
      <td>0.03650</td>
      <td>38.07857</td>
      <td>0.00000</td>
      <td>0.00675</td>
      <td>5.45584</td>
      <td>-0.10717</td>
    </tr>
    <tr>
      <th>2025-10-31</th>
      <td>0.00685</td>
      <td>42.87548</td>
      <td>0.00000</td>
      <td>0.02341</td>
      <td>38.99354</td>
      <td>0.00000</td>
      <td>0.00685</td>
      <td>5.50005</td>
      <td>-0.10106</td>
    </tr>
    <tr>
      <th>2025-11-30</th>
      <td>0.01020</td>
      <td>43.32308</td>
      <td>0.00000</td>
      <td>0.00245</td>
      <td>39.09156</td>
      <td>0.00000</td>
      <td>0.01020</td>
      <td>5.56636</td>
      <td>-0.09189</td>
    </tr>
    <tr>
      <th>2025-12-31</th>
      <td>-0.00662</td>
      <td>43.02959</td>
      <td>-0.00662</td>
      <td>0.00061</td>
      <td>39.11610</td>
      <td>0.00000</td>
      <td>-0.00662</td>
      <td>5.52288</td>
      <td>-0.09790</td>
    </tr>
  </tbody>
</table>
<p>432 rows × 9 columns</p>
</div>


Next, we'll look at performance for the assets and portfolio.

### Performance Statistics

We can then plot the monthly returns:


```python
plot_timeseries(
    price_df=portfolio_monthly,
    plot_start_date=start_date,
    plot_end_date=end_date,
    plot_columns=["Portfolio_Monthly_Return", "SPXT_Monthly_Return", "10Y_Monthly_Return"],
    title="Portfolio, SPXT, and 10Y Monthly Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_rotation=45,
    y_label="Return",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing=0.02,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_90_0.png)
    


And cumulative returns:


```python
plot_timeseries(
    price_df=portfolio_monthly,
    plot_start_date=start_date,
    plot_end_date=end_date,
    plot_columns=["Portfolio_Cumulative_Return", "SPXT_Cumulative_Return", "10Y_Cumulative_Return"],
    title="Portfolio, SPXT, and 10Y Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_rotation=45,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=3,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_92_0.png)
    


And drawdowns:


```python
plot_timeseries(
    price_df=portfolio_monthly,
    plot_start_date=start_date,
    plot_end_date=end_date,
    plot_columns=["Portfolio_Drawdown", "SPXT_Drawdown", "10Y_Drawdown"],
    title="Portfolio, SPXT, and 10Y Drawdowns",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_rotation=45,
    y_label="Drawdown",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing=0.05,
    grid=True,
    legend=True,
    export_plot=False,
    plot_file_name=None,
)
```


    
![png](asset-class-performance-fed-policy-cycles_files/asset-class-performance-fed-policy-cycles_94_0.png)
    


Finally, we can run the stats on the hybrid portfolio, SPY, and TLT with the following code:


```python
port_sum_stats = summary_stats(
    fund_list=["Portfolio", "SPXT", "10Y"],
    df=portfolio_monthly[["Portfolio_Monthly_Return"]],
    period="Monthly",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

spy_sum_stats = summary_stats(
    fund_list=["Portfolio", "SPXT", "10Y"],
    df=portfolio_monthly[["SPXT_Monthly_Return"]],
    period="Monthly",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

tlt_sum_stats = summary_stats(
    fund_list=["Portfolio", "SPXT", "10Y"],
    df=portfolio_monthly[["10Y_Monthly_Return"]],
    period="Monthly",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([port_sum_stats, spy_sum_stats, tlt_sum_stats])
sum_stats
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
      <th>Monthly Max Return</th>
      <th>Monthly Max Return (Date)</th>
      <th>Monthly Min Return</th>
      <th>Monthly Min Return (Date)</th>
      <th>Max Drawdown</th>
      <th>Peak</th>
      <th>Trough</th>
      <th>Recovery Date</th>
      <th>Days to Recovery</th>
      <th>MAR Ratio</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Portfolio_Monthly_Return</th>
      <td>0.11267</td>
      <td>0.11897</td>
      <td>0.94701</td>
      <td>0.11086</td>
      <td>0.10946</td>
      <td>2020-11-30</td>
      <td>-0.14458</td>
      <td>1998-08-31</td>
      <td>-0.23867</td>
      <td>2021-12-31</td>
      <td>2022-09-30</td>
      <td>2023-12-31</td>
      <td>457.00000</td>
      <td>0.46449</td>
    </tr>
    <tr>
      <th>SPXT_Monthly_Return</th>
      <td>0.11392</td>
      <td>0.14735</td>
      <td>0.77311</td>
      <td>0.10799</td>
      <td>0.12819</td>
      <td>2020-04-30</td>
      <td>-0.16795</td>
      <td>2008-10-31</td>
      <td>-0.50949</td>
      <td>2007-10-31</td>
      <td>2009-02-28</td>
      <td>2012-03-31</td>
      <td>1127.00000</td>
      <td>0.21196</td>
    </tr>
    <tr>
      <th>10Y_Monthly_Return</th>
      <td>0.05420</td>
      <td>0.06331</td>
      <td>0.85606</td>
      <td>0.05347</td>
      <td>0.08169</td>
      <td>2008-11-30</td>
      <td>-0.05558</td>
      <td>2003-07-31</td>
      <td>-0.22865</td>
      <td>2020-07-31</td>
      <td>2023-10-31</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>0.23386</td>
    </tr>
  </tbody>
</table>
</div>



Based on the above, our hybrid portfolio outperforms both stocks and bonds, with lower drawdowns.

## Conclusions

This was a interesting exercise to evaluate the performance of different asset classes during Fed tightening and easing cycles. The results are not particularly surprising, but it is interesting to see the data and plots to confirm the economic intuition that stocks perform well during tightening cycles (economic strength) and bonds perform well during easing cycles (economic weakness). The results are certainly dependent on the specific time period or regime, and also on the assumption made for how to handle the periods of neutral policy (i.e. no change in FFR).

## Future Investigation

A couple of ideas sound intriguing for future investigation:

* Does a commodity index (such as GSCI) exhibit differing behavior than gold?
* How does leverage affect the returns that are observed for the hybrid portfolio, stocks, and bonds?
* Do other Fed tightening/loosening cycles exhibit the same behavior for returns?

## References

1. https://fred.stlouisfed.org/series/DFEDTARU
2. https://fred.stlouisfed.org/series/DFEDTARL
3. https://fred.stlouisfed.org/series/DFEDTAR


