---
title: Automating Execution of Jupyter Notebook Files, Python Scripts, and Hugo Static Site Generation
description: A full-stack approach using doit.
slug: automating-execution-jupyter-notebook-files-python-scripts-hugo-static-site-generation
date: 2025-06-24 00:00:01+0000
# lastmod: 2025-05-07 00:00:01+0000
image: cover.jpg
draft: true
categories:
    - Financial Data
    - Tech
tags:
    - Python
    - Hugo
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Introduction

In this post, I'll cover the implementation of [doit](https://pydoit.org/) to automate the execution of Jupyter notebook files, Python scripts, and building the Hugo static site. Many of the concepts covered below were introduced recently in [FINM 32900 - Full-Stack Quantitative Finance](https://finmath.uchicago.edu/curriculum/degree-concentrations/financial-computing/finm-32900/). This course emphasized the "full stack" approach, including the following:

* Use of GitHub
* Virtual environments
* Environment variables
* Use of various data sources (particularly WRDS)
* Processing/cleaning data
* GitHub actions
* Publishing data
* Restricting access to GitHub hosted sites

## Motivation

The primary motivation for automation came from several realizations:

1. Setting directory variables would avoid any issues with managing where the static files were stored locally
2. I wanted to be able to pull updated data, execute Jupyter notebooks, and update the posts within my Hugo site without a lot of manual intervention and manual processes
3. I like to include the html and PDF exports of the Jupyter notebooks, which required copying the exports to the "Public" folder of the website
4. I needed a system to build the "index.md" files that are present in each post directory, and automatically include Python code and functions (again, without copying/pasting or manual processes especially as functions are modified)

## Python Functions

Here are the functions needed for this project:

* [calc_vix_trade_pnl](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#calc_vix_trade_pnl): Calculates the profit/loss from VIX options trades.</br>
* [df_info](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#df_info): A simple function to display the information about a DataFrame and the first five rows and last five rows.</br>
* [df_info_markdown](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#df_info_markdown): Similar to the `df_info` function above, except that it coverts the output to markdown.</br>
* [export_track_md_deps](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#export_track_md_deps): Exports various text outputs to markdown files, which are included in the `index.md` file created when building the site with Hugo.</br>
* [load_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.</br>
* [pandas_set_decimal_places](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.</br>
* [plot_price](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#plot_price): Plot the price data from a DataFrame for a specified date range and columns.</br>
* [plot_stats](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#plot_stats): Generate a scatter plot for the mean OHLC prices.</br>
* [plot_vix_with_trades](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#plot_vix_with_trades): Plot the VIX daily high and low prices, along with the VIX spikes, and trades.</br>
* [yf_pull_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.

## Data Overview (VIX)

### Acquire CBOE Volatility Index (VIX) Data

First, let's get the data:

```python
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="^VIX",
    source="Yahoo_Finance", 
    asset_class="Indices", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)
```

### Load Data - VIX

Now that we have the data, let's load it up and take a look:

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

Now, running:

```python
df_info(vix)
```

Gives us the following:

<!-- INSERT_01_VIX_DF_Info_HERE -->

### Statistics - VIX

Some interesting statistics jump out at us when we look at the mean, standard deviation, minimum, and maximum values for the full dataset. The following code:

```python
vix_stats = vix.describe()
num_std = [-1, 0, 1, 2, 3, 4, 5]
for num in num_std:
    vix_stats.loc[f"mean + {num} std"] = {
        'Open': vix_stats.loc['mean']['Open'] + num * vix_stats.loc['std']['Open'],
        'High': vix_stats.loc['mean']['High'] + num * vix_stats.loc['std']['High'],
        'Low': vix_stats.loc['mean']['Low'] + num * vix_stats.loc['std']['Low'],
        'Close': vix_stats.loc['mean']['Close'] + num * vix_stats.loc['std']['Close'],
    }
display(vix_stats)
```

Gives us:

<!-- INSERT_01_VIX_Stats_HERE -->

We can also run the statistics individually for each year:

```python
# Group by year and calculate mean and std for OHLC
vix_stats_by_year = vix.groupby(vix.index.year)[["Open", "High", "Low", "Close"]].agg(["mean", "std"])

# Flatten the column MultiIndex
vix_stats_by_year.columns = ['_'.join(col).strip() for col in vix_stats_by_year.columns.values]
vix_stats_by_year.index.name = "Year"

display(vix_stats_by_year)
```

Gives us:

<!-- INSERT_01_VIX_Stats_By_Year_HERE -->

It is interesting to see how much the mean OHLC values vary by year.

And finally, we can run the statistics individually for each month:

```python
# Group by month and calculate mean and std for OHLC
vix_stats_by_month = vix.groupby(vix.index.month)[["Open", "High", "Low", "Close"]].agg(["mean", "std"])

# Flatten the column MultiIndex
vix_stats_by_month.columns = ['_'.join(col).strip() for col in vix_stats_by_month.columns.values]
vix_stats_by_month.index.name = "Month"

display(vix_stats_by_month)
```

Gives us:

<!-- INSERT_01_VIX_Stats_By_Month_HERE -->

### Deciles - VIX

Here are the levels for each decile, for the full dataset:

```python
vix_deciles = vix.quantile(np.arange(0, 1.1, 0.1))
display(vix_deciles)
```

Gives us:

<!-- INSERT_01_VIX_Deciles_HERE -->

## Plots - VIX

### Histogram Distribution - VIX

A quick histogram gives us the distribution for the entire dataset, along with the levels for the mean minus 1 standard deviation, mean, mean plus 1 standard deviation, mean plus 2 standard deviations, mean plus 3 standard deviations, and mean plus 4 standard deviations:

![Histogram, Mean, And Standard Deviations](01_Histogram+Mean+SD.png)

### Historical Data - VIX

Here's two plots for the dataset. The first covers 1990 - 2009, and the second 2010 - Present. This is the daily high level:

![VIX Daily High, 1990 - 2009](01_VIX_Plot_1990-2009.png)

![VIX Daily High, 2010 - Present](01_VIX_Plot_2010-Present.png)

From these plots, we can see the following:

* The VIX has really only jumped above 50 several times (GFC, COVID, recently in August of 2024)
* The highest levels (> 80) occured only during the GFC & COVID
* Interestingly, the VIX did not ever get above 50 during the .com bubble

### Stats By Year - VIX

Here's the plot for the mean OHLC values for the VIX by year:

![VIX OHLC Stats By Year](01_VIX_Stats_By_Year.png)

### Stats By Month - VIX

Here's the plot for the mean OHLC values for the VIX by month:

![VIX OHLC Stats By Month](01_VIX_Stats_By_Month.png)

## Data Overview (VVIX)

Before moving on to generating a signal, let's run the above data overview code again, but this time for the CBOE VVIX. From the [CBOE VVIX website](https://www.cboe.com/us/indices/dashboard/vvix/):

"Volatility is often called a new asset class, and every asset class deserves its own volatility index.  The Cboe VVIX IndexSM represents the expected volatility of the VIX®.  VVIX derives the expected 30-day volatility of VIX by applying the VIX algorithm to VIX options."

Looking at the statistics of the VVIX should give us an idea of the volatility of the VIX.

### Acquire CBOE VVIX Data

First, let's get the data:

```python
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="^VVIX",
    source="Yahoo_Finance", 
    asset_class="Indices", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)
```

### Load Data - VVIX

Now that we have the data, let's load it up and take a look:

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

Now, running:

```python
df_info(vvix)
```

Gives us the following:

<!-- INSERT_02_VVIX_DF_Info_HERE -->

### Statistics - VVIX

Here are the statistics for the VVIX, generated in the same manner as above for the VIX:

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

Gives us:

<!-- INSERT_02_VVIX_Stats_HERE -->

We can also run the statistics individually for each year:

```python
# Group by year and calculate mean and std for OHLC
vvix_stats_by_year = vvix.groupby(vvix.index.year)[["Open", "High", "Low", "Close"]].agg(["mean", "std"])

# Flatten the column MultiIndex
vvix_stats_by_year.columns = ['_'.join(col).strip() for col in vvix_stats_by_year.columns.values]
vvix_stats_by_year.index.name = "Year"

display(vvix_stats_by_year)
```

Gives us:

<!-- INSERT_02_VVIX_Stats_By_Year_HERE -->

And finally, we can run the statistics individually for each month:

```python
# Group by month and calculate mean and std for OHLC
vvix_stats_by_month = vvix.groupby(vvix.index.month)[["Open", "High", "Low", "Close"]].agg(["mean", "std"])

# Flatten the column MultiIndex
vvix_stats_by_month.columns = ['_'.join(col).strip() for col in vvix_stats_by_month.columns.values]
vvix_stats_by_month.index.name = "Year"

display(vvix_stats_by_month)
```

Gives us:

<!-- INSERT_02_VVIX_Stats_By_Month_HERE -->

### Deciles - VVIX

Here are the levels for each decile, for the full dataset:

```python
vvix_deciles = vvix.quantile(np.arange(0, 1.1, 0.1))
display(vvix_deciles)
```

Gives us:

<!-- INSERT_02_VVIX_Deciles_HERE -->

## Plots - VVIX

### Histogram Distribution - VVIX

A quick histogram gives us the distribution for the entire dataset, along with the levels for the mean minus 1 standard deviation, mean, mean plus 1 standard deviation, mean plus 2 standard deviations, mean plus 3 standard deviations, and mean plus 4 standard deviations:

![Histogram, Mean, And Standard Deviations](02_Histogram+Mean+SD.png)

### Historical Data - VVIX

Here's two plots for the dataset. The first covers 2007 - 2016, and the second 2017 - Present. This is the daily high level:

![VVIX Daily High, 2007 - 2016](02_VVIX_Plot_2007-2016.png)

![VVIX Daily High, 2017 - Present](02_VVIX_Plot_2017-Present.png)

### Stats By Year - VVIX

Here's the plot for the mean OHLC values for the VVIX by year:

![VVIX OHLC Stats By Year](02_VVIX_Stats_By_Year.png)

### Stats By Month - VVIX

Here's the plot for the mean OHLC values for the VVIX by month:

![VVIX OHLC Stats By Month](02_VVIX_Stats_By_Month.png)

## References

1. https://www.cboe.com/tradable_products/vix/
2. https://github.com/ranaroussi/yfinance

## Code

The jupyter notebook with the functions and all other code is available [here](investigating-a-vix-trading-signal-part-1-vix-and-vvix.ipynb).</br>
The html export of the jupyter notebook is available [here](investigating-a-vix-trading-signal-part-1-vix-and-vvix.html).</br>
The pdf export of the jupyter notebook is available [here](investigating-a-vix-trading-signal-part-1-vix-and-vvix.pdf).