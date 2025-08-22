---
title: Data Pipelining With Polygon
description: Acquiring and managing minute, hour, and daily equity and ETF data from Polygon.io.
slug: data-pipelining-with-polygon
date: 2025-08-10 00:00:01+0000
lastmod: 2025-08-10 00:00:01+0000
image: data-pipelining-with-polygon_original2.png
draft: false
categories:
    - Polygon
    - Pandas
    - Python
# tags:
#     - Python
#     - Yahoo Finance
#     - pandas
#     - VIX
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Introduction

Similar to the recent post about [how I collect and store crypto asset data from Coinbase](http://localhost:1313/2025/07/06/data-pipelining-with-coinbase/), the scripts below pull minute, hour, and daily data for equities and ETFs from [Polygon.io](polygon.io).

The scripts check for an existing data record, and if found then the existing record is updated to include the most recent data. If there is not an existing data record, then the complete historical record from Polygon is pulled and stored.

## Python Functions

Here are the functions needed for this project:

* [polygon_fetch_full_history](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#polygon_fetch_full_history): Fetch full historical data for a given product from Polygon API.</br>
* [polygon_pull_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#polygon_pull_data): Read existing data file, download price data from Polygon, and export data.</br>

## Function Usage

### Polygon Fetch Full History

Here's the docstring with the parameters/variables:

```python
    """
    Fetch full historical data for a given product from Polygon API.

    Parameters:
    -----------
    client
        Polygon API client instance.
    ticker : str
        Ticker symbol to download.
    timespan : str
        Time span for the data (e.g., "minute", "hour", "day", "week", "month", "quarter", "year").
    multiplier : int
        Multiplier for the time span (e.g., 1 for daily data).
    adjusted : bool
        If True, return adjusted data; if False, return raw data.
    full_history_df : pd.DataFrame
        DataFrame containing the data.
    current_start : datetime
        Date for which to start pulling data in datetime format.
    free_tier : bool
        If True, then pause to avoid API limits.
    verbose : bool
        If True, print detailed information about the data being processed.

    Returns:
    --------
    full_history_df : pd.DataFrame
        DataFrame containing the data.
    """
```

This script pulls the full history for a specified asset:

```python
from load_api_keys import load_api_keys
from polygon import RESTClient

# Load API keys from the environment
api_keys = load_api_keys()

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Open client connection
client = RESTClient(api_key=api_keys["POLYGON_KEY"])

# Create an empty DataFrame
df = pd.DataFrame({
    'Date': pd.Series(dtype="datetime64[ns]"),
    'open': pd.Series(dtype="float64"),
    'high': pd.Series(dtype="float64"),
    'low': pd.Series(dtype="float64"),
    'close': pd.Series(dtype="float64"),
    'volume': pd.Series(dtype="float64"),
    'vwap': pd.Series(dtype="float64"),
    'transactions': pd.Series(dtype="int64"),
    'otc': pd.Series(dtype="object")
})

# Example usage - minute
df = polygon_fetch_full_history(
    client=client,
    ticker="AMZN",
    timespan="day",
    multiplier=1,
    adjusted=True,
    full_history_df=df,
    current_start=datetime(2025, 1, 1),
    free_tier=True,
    verbose=True,
)
```

The example above pulls the daily data since 1/1/2025, but can handle data ranges of years because it pulls only a specific number of records at a time as recommended by Polygon (less than 5,000 records per API request), and then combines the records in the dataframe before returning the dataframe.

<!-- INSERT_polygon_fetch_full_history_HERE -->

### Polygon Pull Data

This script uses the above function to perform the following:

1. Attempt to read an existing pickle data file
2. If a data file exists, then pull updated data
3. Otherwise, pull all historical data available for that asset for the past 2 years (using the free tier from Polygon)
4. Store pickle and/or excel files of the data in the specified directories

Here's the docstring with the parameters/variables:

```python
    """
    Read existing data file, download price data from Polygon, and export data.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    ticker : str
        Ticker symbol to download.
    source : str
        Name of the data source (e.g., 'Polygon').
    asset_class : str
        Asset class name (e.g., 'Equities').
    start_date : datetime
        Start date for the data in datetime format.
    timespan : str
        Time span for the data (e.g., "minute", "hour", "day", "week", "month", "quarter", "year").
    multiplier : int
        Multiplier for the time span (e.g., 1 for daily data).
    adjusted : bool
        If True, return adjusted data; if False, return raw data.
    force_existing_check : bool
        If True, force a complete check of the existing data file to verify that there are not any gaps in the data.
    free_tier : bool
        If True, then pause to avoid API limits.
    verbose : bool
        If True, print detailed information about the data being processed.
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    None
    """
```

Through the `base_directory`, `source`, and `asset_class` variables the script knows where in the local filesystem to look for an existing pickle file and the store the resulting updated pickle and/or excel files:

```python
current_year = datetime.now().year
current_month = datetime.now().month
current_day = datetime.now().day

# Example usage - daily
df = polygon_pull_data(
    base_directory=DATA_DIR,
    ticker="AMZN",
    source="Polygon",
    asset_class="Equities",
    start_date=datetime(current_year - 2, current_month, current_day),
    timespan="day",
    multiplier=1,
    adjusted=True,
    force_existing_check=True,
    free_tier=True,
    verbose=True,
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)
```

Here's the output from above:

<!-- INSERT_polygon_pull_data_HERE -->

We can see that the index is not continuous - but this is not an issue because use of the data would likely need to re-index the data or simply set the date column as the index.

## References

1. https://polygon.io/
2. https://polygon.io/docs/rest/quickstart

## Code

The jupyter notebook with the functions and all other code is available [here](data-pipelining-with-polygon.ipynb).</br>
The html export of the jupyter notebook is available [here](data-pipelining-with-polygon.html).</br>
The pdf export of the jupyter notebook is available [here](data-pipelining-with-polygon.pdf).