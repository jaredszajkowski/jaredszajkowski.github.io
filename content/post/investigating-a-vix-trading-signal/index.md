---
title: Investigating A VIX Trading Signal
description: A brief look at finding a trading signal based on moving averages of the VIX.
slug: investigating-a-vix-trading-signal
date: 2025-03-01 00:00:01+0000
lastmod: 2025-04-09 00:00:01+0000
image: cover.jpg
draft: false
categories:
    - Financial Data
    - Trading
tags:
    - Python
    - Yahoo Finance
    - pandas
    - VIX
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Post Updates

Update 4/8/2025: Added plot for signals for each year. VIX data through 4/7/25.</br>
Update 4/9/2025: VIX data through 4/8/25.</br>
Update 4/12/2025: VIX data through 4/10/25.

## Introduction

From the [CBOE VIX website](https://www.cboe.com/tradable_products/vix/):

"Cboe Global Markets revolutionized investing with the creation of the Cboe Volatility Index® (VIX® Index), the first benchmark index to measure the market’s expectation of future volatility. The VIX Index is based on options of the S&P 500® Index, considered the leading indicator of the broad U.S. stock market. The VIX Index is recognized as the world’s premier gauge of U.S. equity market volatility."

In this tutorial, we will investigate finding a signal to use as a basis to trade the VIX.

## VIX Data

I don't have access to data for the VIX through [Nasdaq Data Link](https://www.nasdaq.com/nasdaq-data-link), but for our purposes Yahoo Finance is sufficient.

Using the yfinance python module, we can pull what we need and quicky dump it to excel to retain it for future use.

## Python Functions

First, a couple of useful functions:

### Pull Data From Yahoo Finance

Here's the code for the function to pull the data and dump to Excel:

```python
# This function pulls data from Yahoo finance
def yf_data_updater(fund):
    
    # Download data from YF
    df_comp = yf.download(fund)

    # Drop the column level with the ticker symbol
    df_comp.columns = df_comp.columns.droplevel(1)

    # Reset index
    df_comp = df_comp.reset_index()

    # Remove the "Price" header from the index
    df_comp.columns.name = None

    # Reset date column
    df_comp['Date'] = df_comp['Date'].dt.tz_localize(None)

    # Set 'Date' column as index
    df_comp = df_comp.set_index('Date', drop=True)

    # Drop data from last day because it's not accrate until end of day
    df_comp = df_comp.drop(df_comp.index[-1])
    
    # Export data to excel
    file = fund + ".xlsx"
    df_comp.to_excel(file, sheet_name='data')

    print(f"The first and last date of data for {fund} is: ")
    print(df_comp[:1])
    print(df_comp[-1:])
    print(f"Data updater complete for {fund} data")
    
    return print(f"--------------------")
```

### Set Number Of Decimal Places

This is a quick function to set the number of decimal places that pandas displays. Useful for when using different data sets in a jupyter notebook when you want to change the number of decimal places displayed throughout the notebook:

```python
# Set number of decimal places in pandas
def dp(decimal_places):
    pd.set_option('display.float_format', lambda x: f'%.{decimal_places}f' % x)
```

### Import Data From CSV / XLSX

This function loads data from either a CSV file or excel file into a pandas dataframe:

```python
def load_data(file):
    # Import CSV
    try:
        df = pd.read_csv(file)
    except:
        pass

    # Import excel
    try:
        df = pd.read_excel(file, sheet_name='data', engine='openpyxl')
    except:
        pass
        
    return df
```

### Return Information About A Dataframe

```python
# The `df_info` function returns some useful information about
# a dataframe, such as the columns, data types, and size.

def df_info(df):
    print('The columns, shape, and data types are:')
    print(df.info())
    print('The first 5 rows are:')
    display(df.head())
    print('The last 5 rows are:')
    display(df.tail())
```

Although the above function is useful, sometimes it is simpler to run:

```python
df.info()
df.head()
df.tail()
```

## Data Overview

### Acquire Data

First, let's get the data:

```python
yf_data_updater('^VIX')
```

### Load Data

Then set our decimal places to something reasonable (like 2):

```python
dp(2)
```

Now that we have the data, let's load it up and take a look.

```python
# VIX
vix = load_data('^VIX.xlsx')

# Set 'Date' column as datetime
vix['Date'] = pd.to_datetime(vix['Date'])

# Drop 'Volume'
vix.drop(columns = {'Volume'}, inplace = True)

# Set Date as index
vix.set_index('Date', inplace = True)
```

### Check For Missing Values & Forward Fill Any Missing Values

```python
# Check to see if there are any NaN values
vix[vix['High'].isna()]

# Forward fill to clean up missing data
vix['High'] = vix['High'].ffill()
```

### DataFrame Info

Now, running:

```python
df_info(vix)
```

Gives us the following:

```text
The columns, shape, and data types are:

<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 8889 entries, 1990-01-02 to 2025-04-16
Data columns (total 4 columns):
 #   Column  Non-Null Count  Dtype  
---  ------  --------------  -----  
 0   Close   8889 non-null   float64
 1   High    8889 non-null   float64
 2   Low     8889 non-null   float64
 3   Open    8889 non-null   float64
dtypes: float64(4)
memory usage: 347.2 KB

```

The first 5 rows are:

| Date                |   Close |   High |   Low |   Open |
|:--------------------|--------:|-------:|------:|-------:|
| 1990-01-02 00:00:00 |   17.24 |  17.24 | 17.24 |  17.24 |
| 1990-01-03 00:00:00 |   18.19 |  18.19 | 18.19 |  18.19 |
| 1990-01-04 00:00:00 |   19.22 |  19.22 | 19.22 |  19.22 |
| 1990-01-05 00:00:00 |   20.11 |  20.11 | 20.11 |  20.11 |
| 1990-01-08 00:00:00 |   20.26 |  20.26 | 20.26 |  20.26 |

The last 5 rows are:

| Date                |   Close |   High |   Low |   Open |
|:--------------------|--------:|-------:|------:|-------:|
| 2025-04-10 00:00:00 |   40.72 |  54.87 | 34.44 |  34.44 |
| 2025-04-11 00:00:00 |   37.56 |  46.12 | 36.85 |  40.8  |
| 2025-04-14 00:00:00 |   30.89 |  35.17 | 29.75 |  34.76 |
| 2025-04-15 00:00:00 |   30.12 |  31.45 | 28.29 |  30.01 |
| 2025-04-16 00:00:00 |   32.64 |  34.96 | 29.48 |  33.24 |

### Statistics

Some interesting statistics jump out at us when we look at the mean, standard deviation, minimum, and maximum values. The following code:

```python
vix_stats = vix.describe()
num_std = [-1, 0, 1, 2, 3, 4, 5]
for num in num_std:
    vix_stats.loc[f"mean + {num} std"] = {'Open': vix_stats.loc['mean']['Open'] + num * vix_stats.loc['std']['Open'],
                                    'High': vix_stats.loc['mean']['High'] + num * vix_stats.loc['std']['High'],
                                    'Low': vix_stats.loc['mean']['Low'] + num * vix_stats.loc['std']['Low'],
                                    'Close': vix_stats.loc['mean']['Close'] + num * vix_stats.loc['std']['Close']}
```

Gives us:

|               |      Close |       High |       Low |       Open |
|:--------------|-----------:|-----------:|----------:|-----------:|
| count         | 8889       | 8889       | 8889      | 8889       |
| mean          |   19.4853  |   20.394   |   18.8118 |   19.5771  |
| std           |    7.84508 |    8.40417 |    7.3987 |    7.92027 |
| min           |    9.14    |    9.31    |    8.56   |    9.01    |
| 25%           |   13.85    |   14.52    |   13.4    |   13.93    |
| 50%           |   17.63    |   18.34    |   17.06   |   17.68    |
| 75%           |   22.82    |   23.81    |   22.14   |   22.97    |
| max           |   82.69    |   89.53    |   72.76   |   82.69    |
| mean + -1 std |   11.6403  |   11.9898  |   11.4131 |   11.6569  |
| mean + 0 std  |   19.4853  |   20.394   |   18.8118 |   19.5771  |
| mean + 1 std  |   27.3304  |   28.7981  |   26.2105 |   27.4974  |
| mean + 2 std  |   35.1755  |   37.2023  |   33.6092 |   35.4177  |
| mean + 3 std  |   43.0206  |   45.6065  |   41.0079 |   43.3379  |
| mean + 4 std  |   50.8657  |   54.0106  |   48.4066 |   51.2582  |
| mean + 5 std  |   58.7108  |   62.4148  |   55.8054 |   59.1785  |

### Deciles

And the levels for each decile:

```python
vix_deciles = vix.quantile(np.arange(0, 1.1, 0.1))
display(vix_deciles)
```

Gives us:

|     |   Close |   High |    Low |   Open |
|----:|--------:|-------:|-------:|-------:|
| 0   |   9.14  |  9.31  |  8.56  |  9.01  |
| 0.1 |  12.12  | 12.62  | 11.72  | 12.13  |
| 0.2 |  13.24  | 13.87  | 12.846 | 13.3   |
| 0.3 |  14.59  | 15.274 | 14.07  | 14.66  |
| 0.4 |  16.08  | 16.742 | 15.54  | 16.11  |
| 0.5 |  17.63  | 18.34  | 17.06  | 17.68  |
| 0.6 |  19.54  | 20.38  | 18.99  | 19.67  |
| 0.7 |  21.63  | 22.626 | 20.986 | 21.766 |
| 0.8 |  24.31  | 25.32  | 23.474 | 24.38  |
| 0.9 |  28.702 | 30     | 27.782 | 28.86  |
| 1   |  82.69  | 89.53  | 72.76  | 82.69  |

### Histogram Distribution

A quick histogram gives us the distribution for the entire dataset:

![Histogram](04_Histogram.png)

Now, let's add the levels for the mean, mean plus 1 standard deviation, mean minus 1 standard deviation, and mean plus 2 standard deviations:

![Histogram, Mean, And Standard Deviations](05_Histogram+Mean.png)

### Historical VIX Plot

Here's two plots for the dataset. The first covers 1990 - 2009, and the second 2010 - 2024. This is the daily high level.

![VIX Daily High, 1990 - 2009](06_Plot_1990-2009.png)

![VIX Daily High, 2010 - Present](07_Plot_2010-Present.png)

From this plot, we can see the following:

* The VIX has really only jumped above 50 several times (GFC, COVID, recently in August of 2024)
* The highest levels (> 80) occured only during the GFC & COVID
* Interestingly, the VIX did not ever get above 50 during the .com bubble

## Investigating A Signal

Next, we will consider the idea of a spike level in the VIX and how we might use a spike level to generate a signal. These elevated levels usually occur during market sell-off events or longer term drawdowns in the S&P 500. Sometimes the VIX reverts to recent levels after a spike, but other times levels remain elevated for weeks or even months.

### Spike Level

We will start the 10 day simple moving average (SMA) of the daily high level to get an idea of what is happening recently with the VIX. We'll then pick an arbitrary spike level (25% above the 10 day SMA), and our signal is generated if the VIX hits a level that is above the spike threshold.

The idea is that the 10 day SMA will smooth out the recent short term volatility in the VIX, and therefore any gradual increases in the VIX are not interpreted as spike events.

We also will generate the 20 and 50 day SMAs for reference, and again to see what is happening with the level of the VIX over slightly longer timeframes.

Here's the code for the above:

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

For this exercise, we will use simple moving averages.

### Spike Counts (Signals) By Year

To investigate the number of spike events (or signals) that we receive on a yearly basis, we can run the following:

```python
# Ensure the index is a DatetimeIndex
vix.index = pd.to_datetime(vix.index)

# Create a new column for the year extracted from the date index
vix['Year'] = vix.index.year

# Group by year and the "Spike_SMA" and "Spike_EMA" columns, then count occurrences
spike_count_SMA = vix.groupby(['Year', 'Spike_SMA']).size().unstack(fill_value=0)

spike_count_SMA
```

Which gives us the following:

![Spike Counts](08_Spike_Counts.png)

### Spike Count (Signal) Plots By Year

Here are the yearly plots for when signals are generated:

![Spike/Signals, 1990](09_VIX_SMA_Spike_1990_1990.png)

![Spike/Signals, 1991](09_VIX_SMA_Spike_1991_1991.png)

![Spike/Signals, 1992](09_VIX_SMA_Spike_1992_1992.png)

![Spike/Signals, 1993](09_VIX_SMA_Spike_1993_1993.png)

![Spike/Signals, 1994](09_VIX_SMA_Spike_1994_1994.png)

![Spike/Signals, 1995](09_VIX_SMA_Spike_1995_1995.png)

![Spike/Signals, 1996](09_VIX_SMA_Spike_1996_1996.png)

![Spike/Signals, 1997](09_VIX_SMA_Spike_1997_1997.png)

![Spike/Signals, 1998](09_VIX_SMA_Spike_1998_1998.png)

![Spike/Signals, 1999](09_VIX_SMA_Spike_1999_1999.png)

![Spike/Signals, 2000](09_VIX_SMA_Spike_2000_2000.png)

![Spike/Signals, 2001](09_VIX_SMA_Spike_2001_2001.png)

![Spike/Signals, 2002](09_VIX_SMA_Spike_2002_2002.png)

![Spike/Signals, 2003](09_VIX_SMA_Spike_2003_2003.png)

![Spike/Signals, 2004](09_VIX_SMA_Spike_2004_2004.png)

![Spike/Signals, 2005](09_VIX_SMA_Spike_2005_2005.png)

![Spike/Signals, 2006](09_VIX_SMA_Spike_2006_2006.png)

![Spike/Signals, 2007](09_VIX_SMA_Spike_2007_2007.png)

![Spike/Signals, 2008](09_VIX_SMA_Spike_2008_2008.png)

![Spike/Signals, 2009](09_VIX_SMA_Spike_2009_2009.png)

![Spike/Signals, 2010](09_VIX_SMA_Spike_2010_2010.png)

![Spike/Signals, 2011](09_VIX_SMA_Spike_2011_2011.png)

![Spike/Signals, 2012](09_VIX_SMA_Spike_2012_2012.png)

![Spike/Signals, 2013](09_VIX_SMA_Spike_2013_2013.png)

![Spike/Signals, 2014](09_VIX_SMA_Spike_2014_2014.png)

![Spike/Signals, 2015](09_VIX_SMA_Spike_2015_2015.png)

![Spike/Signals, 2016](09_VIX_SMA_Spike_2016_2016.png)

![Spike/Signals, 2017](09_VIX_SMA_Spike_2017_2017.png)

![Spike/Signals, 2018](09_VIX_SMA_Spike_2018_2018.png)

![Spike/Signals, 2019](09_VIX_SMA_Spike_2019_2019.png)

![Spike/Signals, 2020](09_VIX_SMA_Spike_2020_2020.png)

![Spike/Signals, 2021](09_VIX_SMA_Spike_2021_2021.png)

![Spike/Signals, 2022](09_VIX_SMA_Spike_2022_2022.png)

![Spike/Signals, 2023](09_VIX_SMA_Spike_2023_2023.png)

![Spike/Signals, 2024](09_VIX_SMA_Spike_2024_2024.png)

![Spike/Signals, 2025](09_VIX_SMA_Spike_2025_2025.png)

And here are the plots for the signals generated over the past 3 decades:

![Spike/Signals, 1990 - 1994](09_VIX_SMA_Spike_1990_1994.png)

![Spike/Signals, 1995 - 1999](09_VIX_SMA_Spike_1995_1999.png)

![Spike/Signals, 2000 - 2004](09_VIX_SMA_Spike_2000_2004.png)

![Spike/Signals, 2005 - 2009](09_VIX_SMA_Spike_2005_2009.png)

![Spike/Signals, 2010 - 2014](09_VIX_SMA_Spike_2010_2014.png)

![Spike/Signals, 2015 - 2019](09_VIX_SMA_Spike_2015_2019.png)

![Spike/Signals, 2020 - 2024](09_VIX_SMA_Spike_2020_2024.png)

![Spike/Signals, 2025 - Present](09_VIX_SMA_Spike_2025_2025.png)

More discussion to follow.

## References

https://www.cboe.com/tradable_products/vix/</br>
https://github.com/ranaroussi/yfinance

## Code

The jupyter notebook with the functions and all other code is available [here](investigating-a-vix-trading-signal.ipynb).</br>
The html export of the jupyter notebook is available [here](investigating-a-vix-trading-signal.html).</br>
The pdf export of the jupyter notebook is available [here](investigating-a-vix-trading-signal.pdf).
