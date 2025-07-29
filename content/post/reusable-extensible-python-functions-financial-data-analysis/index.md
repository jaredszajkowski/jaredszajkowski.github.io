---
title: Reusable And Extensible Python Functions For Financial Data Analysis
description: A list of common functions used for data acquisition, cleaning, analysis, etc.
slug: reusable-extensible-python-functions-financial-data-analysis
date: 2025-02-02 00:00:01+0000
lastmod: 2025-07-28 00:00:01+0000
image: cover.jpg
draft: false
categories:
    - Bloomberg
    - Nasdaq Data Link
    - Pandas
    - Python
    - Yahoo Finance
# tags:
#     - Bloomberg
#     - Nasdaq Data Link
#     - pandas
#     - Python
#     - Yahoo Finance
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

<!-- ## Post Updates

Update 4/8/2025: Added plot for signals for each year. VIX data through 4/7/25.</br>
Update 4/9/2025: VIX data through 4/8/25.</br>
Update 4/12/2025: VIX data through 4/10/25.</br>
Update 4/22/2025: VIX data through 4/18/25.</br>
Update 4/23/2025: VIX data through 4/22/25.</br>
Update 4/25/2025: VIX data through 4/23/25. Added section for trade history, including open and closed positions.</br>
Update 4/28/2025: VIX data through 4/25/25.</br>
Update 5/6/2025: Data through 5/5/25. Added section for the VVIX.</br>
Update 5/7/2025: Data through 5/6/25.</br>
Update 5/21/2025: Data through 5/20/25.</br> -->

## Introduction

This post intends to provide the code for all of the python functions that I use in my analysis. The goal here is that when writing another post I will simply be able to link to the functions below as opposed to providing the function code in each post.

## Function Index

* [bb_clean_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#bb_clean_data): Takes an Excel export from Bloomberg, removes the miscellaneous headings/rows, and returns a DataFrame.</br>
* [build_index](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#build_index): Reads the `index_temp.md` markdown file, inserts the markdown dependencies where indicated, and then saves the file as `index.md`.</br>
* [calc_vix_trade_pnl](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#calc_vix_trade_pnl): Calculates the profit/loss from VIX options trades.</br>
* [coinbase_fetch_available_products](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_available_products): Fetch available products from Coinbase Exchange API.</br>
* [coinbase_fetch_full_history](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_full_history): Fetch full historical data for a given product from Coinbase Exchange API.</br>
* [coinbase_fetch_historical_candles](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#coinbase_fetch_historical_candles): Fetch historical candle data for a given product from Coinbase Exchange API.</br>
* [coinbase_pull_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#coinbase_pull_data): Update existing record or pull full historical data for a given product from Coinbase Exchange API.</br>
* [df_info](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#df_info): A simple function to display the information about a DataFrame and the first five rows and last five rows.</br>
* [df_info_markdown](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#df_info_markdown): Similar to the `df_info` function above, except that it coverts the output to markdown.</br>
* [export_track_md_deps](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#export_track_md_deps): Exports various text outputs to markdown files, which are included in the `index.md` file created when building the site with Hugo.</br>
* [load_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.</br>
* [pandas_set_decimal_places](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.</br>
* [plot_price](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#plot_price): Plot the price data from a DataFrame for a specified date range and columns.</br>
* [plot_stats](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#plot_stats): Generate a scatter plot for the mean OHLC prices.</br>
* [plot_vix_with_trades](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#plot_vix_with_trades): Plot the VIX daily high and low prices, along with the VIX spikes, and trades.</br>
* [strategy_harry_brown_perm_port](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#strategy_harry_brown_perm_port): Execute the strategy for the Harry Brown permanent portfolio.</br>
* [summary_stats](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.</br>
* [yf_pull_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.

## Python Functions

### bb_clean_data

```python
import os
import pandas as pd

from IPython.display import display

def bb_clean_data(
    base_directory: str,
    fund_ticker_name: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:

    """
    This function takes an excel export from Bloomberg and removes all excess data 
    leaving date and close columns.

    Parameters:
    -----------
    base_directory : str
        Root path to store downloaded data.
    fund : str
        The fund to clean the data from.
    source : str
        Name of the data source (e.g., 'Bloomberg').
    asset_class : str
        Asset class name (e.g., 'Equities').
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.
        
    Returns:
    --------
    df : pd.DataFrame
        DataFrame containing cleaned data prices.
    """

    # Set location from where to read existing excel file
    location = f"{base_directory}/{source}/{asset_class}/Daily/{fund_ticker_name}.xlsx"

    # Read data from excel
    try:
        df = pd.read_excel(location, sheet_name ="Worksheet", engine="calamine")
    except FileNotFoundError:
        print(f"File not found...please download the data for {fund_ticker_name}")
    
    # Set the column headings from row 5 (which is physically row 6)
    df.columns = df.iloc[5]
    
    # Set the column heading for the index to be "None"
    df.rename_axis(None, axis=1, inplace = True)
    
    # Drop the first 6 rows, 0 - 5
    df.drop(df.index[0:6], inplace=True)
    
    # Set the date column as the index
    df.set_index('Date', inplace = True)
    
    # Drop the volume column
    try:
        df.drop(columns = {'PX_VOLUME'}, inplace = True)
    except KeyError:
        pass
        
    # Rename column
    df.rename(columns = {'PX_LAST':'Close'}, inplace = True)
    
    # Sort by date
    df.sort_values(by=['Date'], inplace = True)

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/Daily"
    os.makedirs(directory, exist_ok=True)

    # Export to excel
    if excel_export == True:
        df.to_excel(f"{directory}/{fund_ticker_name}_Clean.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df.to_pickle(f"{directory}/{fund_ticker_name}_Clean.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        print(f"The first and last date of data for {fund_ticker_name} is: ")
        display(df[:1])
        display(df[-1:])
        print(f"Bloomberg data cleaning complete for {fund_ticker_name}")
        print(f"--------------------")
    else:
        pass
    
    return df
```

### build_index

```python
from pathlib import Path

def build_index() -> None:
    
    """
    Build a Hugo-compatible index.md by combining Markdown fragments.

    This function reads a template file (`index_temp.md`) and a list of markdown dependencies 
    from `index_dep.txt`. For each entry in the dependency list, it replaces a corresponding 
    placeholder in the template (formatted as <!-- INSERT_<name>_HERE -->) with the content 
    from the markdown file. If a file is missing, the placeholder is replaced with a warning note.

    Output:
    -------
    - Writes the final assembled content to `index.md`.

    Raises:
    -------
    FileNotFoundError:
        If either `index_temp.md` or `index_dep.txt` does not exist.

    Example:
    --------
    If `index_dep.txt` contains:
        01_intro.md
        02_analysis.md

    And `index_temp.md` contains:
        <!-- INSERT_01_intro_HERE -->
        <!-- INSERT_02_analysis_HERE -->

    The resulting `index.md` will include the contents of the respective markdown files in place 
    of their placeholders.
    """
    
    temp_index_path = Path("index_temp.md")
    final_index_path = Path("index.md")
    dependencies_path = Path("index_dep.txt")

    # Read the index template
    if not temp_index_path.exists():
        raise FileNotFoundError("Missing index_temp.md")

    temp_index_content = temp_index_path.read_text()

    # Read dependency list
    if not dependencies_path.exists():
        raise FileNotFoundError("Missing index_dep.txt")

    with dependencies_path.open("r") as f:
        markdown_files = [line.strip() for line in f if line.strip()]

    # Replace placeholders for each dependency
    final_index_content = temp_index_content
    for md_file in markdown_files:
        placeholder = f"<!-- INSERT_{Path(md_file).stem}_HERE -->"
        if Path(md_file).exists():
            content = Path(md_file).read_text()
            final_index_content = final_index_content.replace(placeholder, content)
        else:
            print(f"⚠️  Warning: {md_file} not found, skipping placeholder {placeholder}")
            final_index_content = final_index_content.replace(placeholder, f"*{md_file} not found*")

    # Write final index.md
    final_index_path.write_text(final_index_content)
    print("✅ index.md successfully built!")

if __name__ == "__main__":
    build_index()

```

### calc_vix_trade_pnl

```python
import pandas as pd

def calc_vix_trade_pnl(
    transaction_df: pd.DataFrame,
    exp_start_date: str,
    exp_end_date: str,
    trade_start_date: str,
    trade_end_date: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, str, str, str]:
    
    """
    Calculate the profit and loss (PnL) of trades based on transaction data.

    Parameters:
    -----------
    transaction_df : pd.DataFrame
        DataFrame containing transaction data.
    exp_start_date : str
        Start date for filtering transactions in 'YYYY-MM-DD' format. This is the start of the range for the option expiration date.
    exp_end_date : str
        End date for filtering transactions in 'YYYY-MM-DD' format. This is the end of the range for the option expiration date.
    trade_start_date : str
        Start date for filtering transactions in 'YYYY-MM-DD' format. This is the start of the range for the trade date.
    trade_end_date : str
        End date for filtering transactions in 'YYYY-MM-DD' format. This is the end of the range for the trade date.

    Returns:
    --------
    transactions_data : pd.DataFrame
        Dataframe containing the transactions for the specified timeframe.
    closed_trades : pd.DataFrame
        DataFrame containing the closed trades with realized PnL and percent PnL.
    open_trades : pd.DataFrame
        DataFrame containing the open trades.
    net_PnL_percent_str : str
        String representation of the net profit percentage.
    net_PnL_str : str
        String representation of the net profit and loss in dollars.
    """

    # If start and end dates for trades and expirations are None, use the entire DataFrame
    if exp_start_date is None and exp_end_date is None and trade_start_date is None and trade_end_date is None:
        transactions_data = transaction_df
    
    # If both start and end dates for trades and expirations are provided then filter by both
    else:
        transactions_data = transaction_df[
            (transaction_df['Exp_Date'] >= exp_start_date) & (transaction_df['Exp_Date'] <= exp_end_date) &
            (transaction_df['Trade_Date'] >= trade_start_date) & (transaction_df['Trade_Date'] <= trade_end_date)
        ]

    # Combine the 'Action' and 'Symbol' columns to create a unique identifier for each transaction
    transactions_data['TradeDate_Action_Symbol_VIX'] = (
        transactions_data['Trade_Date'].astype(str) + 
        ", " + 
        transactions_data['Action'] + 
        ", " + 
        transactions_data['Symbol'] + 
        ", VIX = " + 
        transactions_data['Approx_VIX_Level'].astype(str)
    )

    # Split buys and sells and sum the notional amounts
    transactions_sells = transactions_data[transactions_data['Action'] == 'Sell to Close']
    transactions_sells = transactions_sells.groupby(['Symbol', 'Exp_Date'], as_index=False)[['Amount', 'Quantity']].sum()

    transactions_buys = transactions_data[transactions_data['Action'] == 'Buy to Open']
    transactions_buys = transactions_buys.groupby(['Symbol', 'Exp_Date'], as_index=False)[['Amount', 'Quantity']].sum()

    # Merge buys and sells dataframes back together
    merged_transactions = pd.merge(transactions_buys, transactions_sells, on=['Symbol', 'Exp_Date'], how='outer', suffixes=('_Buy', '_Sell'))
    merged_transactions = merged_transactions.sort_values(by=['Exp_Date'], ascending=[True])
    merged_transactions = merged_transactions.reset_index(drop=True)

    # Identify the closed positions
    merged_transactions['Closed'] = (~merged_transactions['Amount_Sell'].isna()) & (~merged_transactions['Amount_Buy'].isna()) & (merged_transactions['Quantity_Buy'] == merged_transactions['Quantity_Sell'])

    # Create a new dataframe for closed positions
    closed_trades = merged_transactions[merged_transactions['Closed']]
    closed_trades = closed_trades.reset_index(drop=True)
    closed_trades['Realized_PnL'] = closed_trades['Amount_Sell'] - closed_trades['Amount_Buy']
    closed_trades['Percent_PnL'] = closed_trades['Realized_PnL'] / closed_trades['Amount_Buy']
    closed_trades.drop(columns={'Closed', 'Exp_Date'}, inplace=True)
    closed_trades['Quantity_Sell'] = closed_trades['Quantity_Sell'].astype(int)

    # Calculate the net % PnL
    net_PnL_percent = closed_trades['Realized_PnL'].sum() / closed_trades['Amount_Buy'].sum()
    net_PnL_percent_str = f"{round(net_PnL_percent * 100, 2)}%"

    # Calculate the net $ PnL
    net_PnL = closed_trades['Realized_PnL'].sum()
    net_PnL_str = f"${net_PnL:,.2f}"

    # Create a new dataframe for open positions
    open_trades = merged_transactions[~merged_transactions['Closed']]
    open_trades = open_trades.reset_index(drop=True)
    open_trades.drop(columns={'Closed', 'Amount_Sell', 'Quantity_Sell', 'Exp_Date'}, inplace=True)

    # Calculate the total market value of opened positions
    # If start and end dates for trades and expirations are None, use only the closed positions
    if exp_start_date is None and exp_end_date is None and trade_start_date is None and trade_end_date is None:
        total_opened_pos_mkt_val = closed_trades['Amount_Buy'].sum()
    else:
        total_opened_pos_mkt_val = closed_trades['Amount_Buy'].sum() + open_trades['Amount_Buy'].sum()
    total_opened_pos_mkt_val_str = f"${total_opened_pos_mkt_val:,.2f}"

    # Calculate the total market value of closed positions
    total_closed_pos_mkt_val = closed_trades['Amount_Sell'].sum()
    total_closed_pos_mkt_val_str = f"${total_closed_pos_mkt_val:,.2f}"

    return transactions_data, closed_trades, open_trades, net_PnL_percent_str, net_PnL_str, total_opened_pos_mkt_val_str, total_closed_pos_mkt_val_str
```

### coinbase_fetch_available_products

```python
import pandas as pd
import requests

def coinbase_fetch_available_products(
    base_currency: str,
    quote_currency: str,
    status: str,
) -> pd.DataFrame:

    """
    Fetch available products from Coinbase Exchange API.
    
    Parameters:
    -----------
    base_currency : str, optional
        Filter products by base currency (e.g., 'BTC').
    quote_currency : str, optional
        Filter products by quote currency (e.g., 'USD').
    status : str, optional
        Filter products by status (e.g., 'online', 'offline').

    Returns:
    --------
    pd.DataFrame
        DataFrame containing available products with their details.
    """

    url = 'https://api.exchange.coinbase.com/products'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        products = response.json()

        # Convert the list of products into a pandas DataFrame
        df = pd.DataFrame(products)
        
        # Filter by base_currency if provided
        if base_currency:
            df = df[df['base_currency'] == base_currency]
        
        # Filter by quote_currency if provided
        if quote_currency:
            df = df[df['quote_currency'] == quote_currency]

        # Filter by status if provided
        if status:
            df = df[df['status'] == status]

        # Sort by "id"
        df = df.sort_values(by='id')
        
        return df
    
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Oops: Something Else {err}")

if __name__ == "__main__":
    
    # Example usage
    df = coinbase_fetch_available_products(
        base_currency=None,
        quote_currency="USD",
        status="online",
    )

    if df is not None:
        print(df)
    else:
        print("No data returned.")
```

### coinbase_fetch_full_history

```python
import pandas as pd
import time

from coinbase_fetch_historical_candles import coinbase_fetch_historical_candles
from datetime import datetime, timedelta

def coinbase_fetch_full_history(
    product_id: str,
    start: datetime,
    end: datetime,
    granularity: int,
) -> pd.DataFrame:
    
    """
    Fetch full historical data for a given product from Coinbase Exchange API.
    
    Parameters:
    -----------
    product_id : str
        The trading pair (e.g., 'BTC-USD').
    start : datetime
        Start time in UTC.
    end : datetime
        End time in UTC.
    granularity : int
        Time slice in seconds (e.g., 3600 for hourly candles).

    Returns:
    --------
    pd.DataFrame
        DataFrame containing time, low, high, open, close, volume.
    """
    
    all_data = []
    current_start = start

    while current_start < end:
        current_end = min(current_start + timedelta(seconds=granularity * 300), end)  # Fetch max 300 candles per request
        df = coinbase_fetch_historical_candles(product_id, current_start, current_end, granularity)
        if df.empty:
            break
        all_data.append(df)
        current_start = df['time'].iloc[-1] + timedelta(seconds=granularity)
        time.sleep(0.2)  # Small delay to respect rate limits

    if all_data:
        full_df = pd.concat(all_data).reset_index(drop=True)
        return full_df
    else:
        return pd.DataFrame()
    
if __name__ == "__main__":
    
    # Example usage
    df = coinbase_fetch_full_history(
        product_id="BTC-USD",
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 31),
        granularity=86_400,
    )

    if df is not None:
        print(df)
    else:
        print("No data returned.")
```

### coinbase_fetch_historical_candles

```python
import pandas as pd
import requests
import time

from datetime import datetime

def coinbase_fetch_historical_candles(
    product_id: str,
    start: datetime,
    end: datetime,
    granularity: int,
) -> pd.DataFrame:

    """
    Fetch historical candle data for a given product from Coinbase Exchange API.

    Parameters:
    -----------
    product_id : str
        The trading pair (e.g., 'BTC-USD').
    start : str
        Start time in UTC.
    end : str
        End time in UTC.
    granularity : int
        Time slice in seconds (e.g., 3600 for hourly candles).

    Returns:
    --------
    pd.DataFrame
        DataFrame containing time, low, high, open, close, volume.
    """

    url = f'https://api.exchange.coinbase.com/products/{product_id}/candles'
    params = {
        'start': start.isoformat(),
        'end': end.isoformat(),
        'granularity': granularity
    }

    max_retries = 5
    retry_delay = 1  # initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Coinbase Exchange API returns data in reverse chronological order
            data = data[::-1]

            # Convert to DataFrame
            df = pd.DataFrame(data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df

        except requests.exceptions.HTTPError as errh:
            if response.status_code == 429:
                print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"HTTP Error: {errh}")
                break
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
            time.sleep(retry_delay)
            retry_delay *= 2
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
            time.sleep(retry_delay)
            retry_delay *= 2
        except requests.exceptions.RequestException as err:
            print(f"OOps: Something Else {err}")
            break

    raise Exception("Failed to fetch data after multiple retries.")

if __name__ == "__main__":
    
    # Example usage
    df = coinbase_fetch_historical_candles(
        product_id="BTC-USD",
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 1),
        granularity=86_400,
    )

    if df is not None:
        print(df)
    else:
        print("No data returned.")
```

### coinbase_pull_data

```python
import calendar
import os
import pandas as pd

from coinbase_fetch_available_products import coinbase_fetch_available_products
from coinbase_fetch_full_history import coinbase_fetch_full_history
from datetime import datetime, timedelta
from settings import config

# Get the data directory from the configuration
DATA_DIR = config("DATA_DIR")

def coinbase_pull_data(
    base_directory,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
    base_currency: str,
    quote_currency: str,
    granularity: int=3600, # 60=minute, 3600=hourly, 86400=daily
    status: str='online', # default status is 'online'
    start_date: datetime=datetime(2025, 1, 1), # default start date
    end_date: datetime=datetime.now() - timedelta(days=1), # updates data through 1 day ago due to lag in data availability
) -> pd.DataFrame:
    
    """
    Update existing record or pull full historical data for a given product from Coinbase Exchange API.

    Parameters:
    -----------
    base_directory
        Root path to store downloaded data.
    source : str
        Name of the data source (e.g., 'Nasdaq_Data_Link').
    asset_class : str
        Asset class name (e.g., 'Equities').
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.
    base_currency : str
        The base currency (e.g., 'BTC').
    quote_currency : str
        The quote currency (e.g., 'USD').
    status : str, optional
        Filter products by status (default is 'online').
    granularity : int
        Time slice in seconds (e.g., 3600 for hourly candles).
    start_date : str, optional
        Start date in UTC (ISO format).
    end_date : str, optional
        End date in UTC (ISO format).

    Returns:
    --------
    None
    """

    # List of crypto assets
    filtered_products = coinbase_fetch_available_products(base_currency=base_currency, quote_currency=quote_currency, status=status)
    filtered_products_list = filtered_products['id'].tolist()
    filtered_products_list = sorted(filtered_products_list)

    if not filtered_products.empty:
        print(filtered_products[['id', 'base_currency', 'quote_currency', 'status']])
        print(filtered_products_list)
        print(len(filtered_products_list))

    else:
        print("No products found with the specified base and/or quote currencies.")

    missing_data = []
    omitted_data = []
    num_products = len(filtered_products_list)
    counter = 0

    # Loop for updates
    for product in filtered_products_list:
        
        counter+=1
        print(f"Updating product {counter} of {num_products}.")

        if granularity == 60:
            time_length = "Minute"
        elif granularity == 3600:
            time_length = "Hourly"
        elif granularity == 86400:
            time_length = "Daily"
        else:
            print("Error - please confirm timeframe.")
            break

        # Set file location based on parameters
        file_location = f"{base_directory}/{source}/{asset_class}/{time_length}/{product}.pkl"
    
        try:
            # Attempt to read existing pickle data file
            ex_data = pd.read_pickle(file_location)
            ex_data = ex_data.reset_index()
            print(f"File found...updating the {product} data")
            print("Existing data:")
            print(ex_data)

            # Pull recent data
            new_data = coinbase_fetch_full_history(product, start_date, end_date, granularity)
            new_data = new_data.rename(columns={'time':'Date'})
            new_data['Date'] = new_data['Date'].dt.tz_localize(None)
            print("New data:")
            print(new_data)

            # Combine existing data with recent data
            full_history_df = pd.concat([ex_data,new_data[new_data['Date'].isin(ex_data['Date']) == False]])
            full_history_df = full_history_df.sort_values(by='Date')
            full_history_df['Date'] = full_history_df['Date'].dt.tz_localize(None)
            full_history_df = full_history_df.set_index('Date')
            
            print("Combined data:")
            print(full_history_df)

            # Create directory
            directory = f"{base_directory}/{source}/{asset_class}/{time_length}"
            os.makedirs(directory, exist_ok=True)

            # Export to excel
            if excel_export == True:
                full_history_df.to_excel(f"{directory}/{product}.xlsx", sheet_name="data")
            else:
                pass

            # Export to pickle
            if pickle_export == True:
                full_history_df.to_pickle(f"{directory}/{product}.pkl")
            else:
                pass

            # Output confirmation
            if output_confirmation == True:
                print(f"Data update complete for {time_length} {product}.")
                print("--------------------")
            else:
                pass
            
        except FileNotFoundError:
            # Starting year for fetching initial data
            starting_year = 2025

            # Print error
            print(f"File not found...downloading the {product} data starting with {starting_year}.")

            def get_full_hist(year):
                try:
                    # Define the start and end dates
                    start_date = datetime(year, 1, 1) # Default start date
                    end_date = datetime.now() - timedelta(days = 1) # Updates data through 1 day ago

                    # Fetch and process the data
                    full_history_df = coinbase_fetch_full_history(product, start_date, end_date, granularity)
                    full_history_df = full_history_df.rename(columns={'time': 'Date'})
                    full_history_df = full_history_df.sort_values(by='Date')

                    # Iterate through rows to see if the value of the asset ever exceeds a specified threshold
                    # Default value for the price threshold is 0 USD
                    # If the price never exceeds this threshold, the asset is omitted from the final list
                    def find_first_close_above_threshold(full_history_df, threshold=0):
                        # Ensure 'Date' is the index before proceeding
                        if 'Date' in full_history_df.columns:
                            full_history_df.set_index('Date', inplace=True)
                        full_history_df.index = full_history_df.index.tz_localize(None)
                        
                        # Iterate through the DataFrame
                        for index, row in full_history_df.iterrows():
                            if row['close'] >= threshold:
                                print(f"First occurrence: {index}, close={row['close']}")

                                # Return the filtered DataFrame starting from this row
                                return full_history_df.loc[index:]
                        
                        # If no value meets the condition, return an empty DataFrame
                        print(f"Share price never exceeds {threshold} USD.")
                        omitted_data.append(product)
                        return None
                    
                    full_history_above_threshold_df = find_first_close_above_threshold(full_history_df, threshold=0)

                    return full_history_above_threshold_df

                except KeyError:
                    print(f"KeyError: No data available for {product} in {year}. Trying next year...")
                    next_year = year + 1

                    # Base case: Stop if the next year exceeds the current year
                    if next_year > datetime.now().year:
                        print("No more data available for any future years.")
                        missing_data.append(product)
                        return None

                    # Recursive call for the next year
                    return get_full_hist(year=next_year)

            # Fetch the full history starting from the given year
            full_history_df = get_full_hist(year=starting_year)

            if full_history_df is not None:

                # Create directory
                directory = f"{base_directory}/{source}/{asset_class}/{time_length}"
                os.makedirs(directory, exist_ok=True)

                # Export to excel
                if excel_export == True:
                    full_history_df.to_excel(f"{directory}/{product}.xlsx", sheet_name="data")
                else:
                    pass

                # Export to pickle
                if pickle_export == True:
                    full_history_df.to_pickle(f"{directory}/{product}.pkl")
                else:
                    pass

                # Output confirmation
                if output_confirmation == True:
                    print(f"Initial data fetching completed successfully for {time_length} {product}.")
                    print("--------------------")
                else:
                    pass

            else:
                print("No data could be fetched for the specified range.")
                
        except Exception as e:
            print(str(e))

    # Remove the cryptocurrencies with missing data from the final list
    missing_data = sorted(missing_data)
    print(f"Data missing for: {missing_data}")

    for asset in missing_data:
        try:
            print(f"Removing {asset} from the list because it is missing data.")
            filtered_products_list.remove(asset)
        except ValueError:
            print(f"{asset} not in list.")
            pass

    # Remove the cryptocurrencies with share prices that never exceed 1 USD from the final list
    omitted_data = sorted(omitted_data)
    print(f"Data omitted due to price for: {omitted_data}")

    for asset in omitted_data:
        try:
            print(f"Removing {asset} from the list because the share price never exceeds 1 USD.")
            filtered_products_list.remove(asset)
        except ValueError:
            print(f"{asset} not in list.")
            pass  
    
    # Remove stablecoins from the final list
    stablecoins_to_remove = ['USDT-USD', 'USDC-USD', 'PAX-USD', 'DAI-USD', 'PYUSD-USD', 'GUSD-USD']
    stablecoins_to_remove = sorted(stablecoins_to_remove)
    print(f"Data for stable coins not to be used: {stablecoins_to_remove}")
    
    for asset in stablecoins_to_remove:
        try:
            filtered_products_list.remove(asset)
            # print(f"Removing {asset} from the list because it is a stablecoin.")
        except ValueError:
            # print(f"{asset} not in list.")
            pass 

    # Remove the wrapped coins from the final list
    wrapped_coins_to_remove = ['WAXL-USD', 'WBTC-USD']
    wrapped_coins_to_remove = sorted(wrapped_coins_to_remove)
    print(f"Data for wrapped coins not to be used: {wrapped_coins_to_remove}")
    
    for asset in wrapped_coins_to_remove:
        try:
            filtered_products_list.remove(asset)
            # print(f"Removing {asset} from the list because it is a wrapped coin.")
        except ValueError:
            # print(f"{asset} not in list.")
            pass

    # Print the final list of token and the length of the list
    print(f"Final list of tokens: {filtered_products_list}")
    print(f"Length of final list of tokens: {len(filtered_products_list)}")

    return full_history_df

if __name__ == "__main__":
     
    # # Example usage to pull all data for each month from 2010 to 2024
    # for granularity in [60, 3600, 86400]:
    #     for year in range(2010, 2025):
    #         for month in range(1, 13):
    #             print(f"Pulling data for {year}-{month:02d}...")
    #             try:
    #                 # Get the last day of the month
    #                 last_day = calendar.monthrange(year, month)[1]
    #                 coinbase_pull_data(
    #                     base_directory=DATA_DIR,
    #                     source="Coinbase",
    #                     asset_class="Cryptocurrencies",
    #                     excel_export=False,
    #                     pickle_export=True,
    #                     output_confirmation=True,
    #                     base_currency="XRP",
    #                     quote_currency="USD",
    #                     granularity=granularity, # 60=minute, 3600=hourly, 86400=daily
    #                     status='online',
    #                     start_date=datetime(year, month, 1),
    #                     end_date=datetime(year, month, last_day),
    #                 )
    #             except Exception as e:
    #                 print(f"Failed to pull data for {year}-{month:02d}: {e}")

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    # Crypto Data
    currencies = ["BTC", "ETH", "SOL", "XRP"]

    # Iterate through each currency
    for cur in currencies:
        # Example usage - minute
        coinbase_pull_data(
            base_directory=DATA_DIR,
            source="Coinbase",
            asset_class="Cryptocurrencies",
            excel_export=False,
            pickle_export=True,
            output_confirmation=True,
            base_currency=cur,
            quote_currency="USD",
            granularity=60, # 60=minute, 3600=hourly, 86400=daily
            status='online', # default status is 'online'
            start_date=datetime(current_year, current_month - 1, 1), # default start date
            end_date=datetime.now() - timedelta(days=1), # updates data through 1 day ago due to lag in data availability
        )

        # Example usage - hourly
        coinbase_pull_data(
            base_directory=DATA_DIR,
            source="Coinbase",
            asset_class="Cryptocurrencies",
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
            base_currency=cur,
            quote_currency="USD",
            granularity=3600, # 60=minute, 3600=hourly, 86400=daily
            status='online', # default status is 'online'
            start_date=datetime(current_year, current_month - 1, 1), # default start date
            end_date=datetime.now() - timedelta(days=1), # updates data through 1 day ago due to lag in data availability
        )

        # Example usage - daily
        coinbase_pull_data(
            base_directory=DATA_DIR,
            source="Coinbase",
            asset_class="Cryptocurrencies",
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
            base_currency=cur,
            quote_currency="USD",
            granularity=86400, # 60=minute, 3600=hourly, 86400=daily
            status='online', # default status is 'online'
            start_date=datetime(current_year, current_month - 1, 1), # default start date
            end_date=datetime.now() - timedelta(days=1), # updates data through 1 day ago due to lag in data availability
        )
```

### df_info

```python
import pandas as pd
from IPython.display import display

def df_info(
    df: pd.DataFrame,
) -> None:
    
    """
    Display summary information about a pandas DataFrame.

    This function prints:
    - The DataFrame's column names, shape, and data types via `df.info()`
    - The first 5 rows using `df.head()`
    - The last 5 rows using `df.tail()`

    It uses `display()` for better output formatting in environments like Jupyter notebooks.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame to inspect.

    Returns:
    --------
    None

    Example:
    --------
    >>> df_info(my_dataframe)
    """
    
    print("The columns, shape, and data types are:")
    print(df.info())
    print("The first 5 rows are:")
    display(df.head())
    print("The last 5 rows are:")
    display(df.tail())
```

### df_info_markdown

```python
import io
import pandas as pd

def df_info_markdown(
    df: pd.DataFrame
) -> str:
    
    """
    Generate a Markdown-formatted summary of a pandas DataFrame.

    This function captures and formats the output of `df.info()`, `df.head()`, 
    and `df.tail()` in Markdown for easy inclusion in reports, documentation, 
    or web-based rendering (e.g., Hugo or Jupyter export workflows).

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame to summarize.

    Returns:
    --------
    str
        A string containing the DataFrame's info, head, and tail 
        formatted in Markdown.

    Example:
    --------
    >>> print(df_info_markdown(df))
    ```text
    The columns, shape, and data types are:
    <output from df.info()>
    ```
    The first 5 rows are:
    |   | col1 | col2 |
    |---|------|------|
    | 0 | ...  | ...  |

    The last 5 rows are:
    ...
    """
    
    buffer = io.StringIO()

    # Capture df.info() output
    df.info(buf=buffer)
    info_str = buffer.getvalue()

    # Convert head and tail to Markdown
    head_str = df.head().to_markdown(floatfmt=".2f")
    tail_str = df.tail().to_markdown(floatfmt=".2f")

    markdown = [
        "```text",
        "The columns, shape, and data types are:\n",
        info_str,
        "```",
        "\nThe first 5 rows are:\n",
        head_str,
        "\nThe last 5 rows are:\n",
        tail_str
    ]

    return "\n".join(markdown)
```

### export_track_md_deps

```python
from pathlib import Path

def export_track_md_deps(
    dep_file: Path, 
    md_filename: str, 
    content: str,
) -> None:
    
    """
    Export Markdown content to a file and track it as a dependency.

    This function writes the provided content to the specified Markdown file and 
    appends the filename to the given dependency file (typically `index_dep.txt`).
    This is useful in workflows where Markdown fragments are later assembled 
    into a larger document (e.g., a Hugo `index.md`).

    Parameters:
    -----------
    dep_file : Path
        Path to the dependency file that tracks Markdown fragment filenames.
    md_filename : str
        The name of the Markdown file to export.
    content : str
        The Markdown-formatted content to write to the file.

    Returns:
    --------
    None

    Example:
    --------
    >>> export_track_md_deps(Path("index_dep.txt"), "01_intro.md", "# Introduction\n...")
    ✅ Exported and tracked: 01_intro.md
    """
    
    Path(md_filename).write_text(content)
    with dep_file.open("a") as f:
        f.write(md_filename + "\n")
    print(f"✅ Exported and tracked: {md_filename}")
```

### load_api_keys

```python
import os

from dotenv import load_dotenv
from pathlib import Path
from settings import config

# Get the environment variable file path from the configuration
ENV_PATH = config("ENV_PATH")

def load_api_keys(
    env_path: Path=ENV_PATH
) -> dict:
    
    """
    Load API keys from a .env file.

    Parameters:
    -----------
    env_path : Path
        Path to the .env file. Default is the ENV_PATH from settings.

    Returns:
    --------
    keys : dict
        Dictionary of API keys.
    """

    load_dotenv(dotenv_path=env_path)

    keys = {
        "INFURA_KEY": os.getenv("INFURA_KEY"),
        "NASDAQ_DATA_LINK_KEY": os.getenv("NASDAQ_DATA_LINK_KEY"),
        "COINBASE_KEY": os.getenv("COINBASE_KEY"),
        "COINBASE_SECRET": os.getenv("COINBASE_SECRET"),
        "SCHWAB_APP_KEY": os.getenv("SCHWAB_APP_KEY"),
        "SCHWAB_SECRET": os.getenv("SCHWAB_SECRET"),
        "SCHWAB_ACCOUNT_NUMBER_1": os.getenv("SCHWAB_ACCOUNT_NUMBER_1"),
        "SCHWAB_ENCRYPTED_ACCOUNT_ID_1": os.getenv("SCHWAB_ENCRYPTED_ACCOUNT_ID_1"),
        "SCHWAB_ACCOUNT_NUMBER_2": os.getenv("SCHWAB_ACCOUNT_NUMBER_2"),
        "SCHWAB_ENCRYPTED_ACCOUNT_ID_2": os.getenv("SCHWAB_ENCRYPTED_ACCOUNT_ID_2"),
        "SCHWAB_ACCOUNT_NUMBER_3": os.getenv("SCHWAB_ACCOUNT_NUMBER_3"),
        "SCHWAB_ENCRYPTED_ACCOUNT_ID_3": os.getenv("SCHWAB_ENCRYPTED_ACCOUNT_ID_3"),
        "POLYGON_KEY": os.getenv("POLYGON_KEY"),
    }

    # Raise error if any key is missing
    for k, v in keys.items():
        if not v:
            raise ValueError(f"Missing environment variable: {k}")

    return keys

if __name__ == "__main__":
    # Example usage
    api_keys = load_api_keys()
    print("API keys loaded successfully.")
```

### load_data

```python
import pandas as pd
from pathlib import Path

def load_data(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    timeframe: str,
    file_format: str,
) -> pd.DataFrame:
    
    """
    Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.

    This function attempts to read a file first as a CSV, then as an Excel file 
    (specifically looking for a sheet named 'data' and using the 'calamine' engine).
    If both attempts fail, a ValueError is raised.

    Parameters:
    -----------
    base_directory
        Root path to read data file.
    ticker : str
        Ticker symbol to read.
    source : str
        Name of the data source (e.g., 'Yahoo').
    asset_class : str
        Asset class name (e.g., 'Equities').
    timeframe : str
        Timeframe for the data (e.g., 'Daily', 'Month_End').
    file_format : str
        Format of the file to load ('csv', 'excel', or 'pickle')

    Returns:
    --------
    pd.DataFrame
        The loaded data.

    Raises:
    -------
    ValueError
        If the file could not be loaded as either CSV or Excel.

    Example:
    --------
    >>> df = load_data(DATA_DIR, "^VIX", "Yahoo_Finance", "Indices")
    """

    if file_format == "csv":
        csv_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.csv"
        df = pd.read_csv(csv_path)
        return df
    
    elif file_format == "excel":
        xlsx_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.xlsx"
        df = pd.read_excel(xlsx_path, sheet_name="data", engine="calamine")
        return df

    elif file_format == "pickle":
        pickle_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.pkl"
        df = pd.read_pickle(pickle_path)
        return df
    
    else:
        raise ValueError(f"❌ Unsupported file format: {file_format}. Please use 'csv', 'excel', or 'pickle'.")
```

### pandas_set_decimal_places

```python
import pandas as pd

def pandas_set_decimal_places(
    decimal_places: int,
) -> None:
    
    """
    Set the number of decimal places displayed for floating-point numbers in pandas.

    Parameters:
    ----------
    decimal_places : int
        The number of decimal places to display for float values in pandas DataFrames and Series.

    Returns:
    --------
    None

    Example:
    --------
    >>> dp(3)
    >>> pd.DataFrame([1.23456789])
           0
    0   1.235
    """
    
    pd.set_option('display.float_format', lambda x: f'%.{decimal_places}f' % x)
```

### plot_price

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import pandas as pd

from matplotlib.ticker import FormatStrFormatter, MultipleLocator

def plot_price(
    price_df: pd.DataFrame,
    plot_start_date: str,
    plot_end_date: str,
    plot_columns,
    title: str,
    x_label: str,
    x_format: str,
    y_label: str,
    y_format: str,
    y_tick_spacing: int,
    grid: bool,
    legend: bool,
    export_plot: bool,
    plot_file_name: str,
) -> None:

    """
    Plot the price data from a DataFrame for a specified date range and columns.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the price data to plot.
    plot_start_date : str
        Start date for the plot in 'YYYY-MM-DD' format.
    plot_end_date : str
        End date for the plot in 'YYYY-MM-DD' format.
    plot_columns : str OR list
        List of columns to plot from the DataFrame. If none, all columns will be plotted.
    title : str
        Title of the plot.
    x_label : str
        Label for the x-axis.
    x_axis_format : str
        Format for the x-axis date labels.
    y_label : str
        Label for the y-axis.
    y_tick_spacing : int
        Spacing for the y-axis ticks.
    grid : bool
        Whether to display a grid on the plot.
    legend : bool
        Whether to display a legend on the plot.
    export_plot : bool
        Whether to save the figure as a PNG file.
    plot_file_name : str
        File name for saving the figure (if save_fig is True).

    Returns:
    --------
    None
    """

    # If start date and end date are None, use the entire DataFrame
    if plot_start_date is None and plot_end_date is None:
        df_filtered = price_df

    # If only end date is specified, filter by end date
    elif plot_start_date is None and plot_end_date is not None:
        df_filtered = price_df[(price_df.index <= plot_end_date)]

    # If only start date is specified, filter by start date
    elif plot_start_date is not None and plot_end_date is None:
        df_filtered = price_df[(price_df.index >= plot_start_date)]

    # If both start date and end date are specified, filter by both
    else:
        df_filtered = price_df[(price_df.index >= plot_start_date) & (price_df.index <= plot_end_date)]

    # Set plot figure size and background color
    plt.figure(figsize=(12, 6), facecolor="#F5F5F5")

    # Plot data
    if plot_columns =="All":
        for col in df_filtered.columns:
            plt.plot(df_filtered.index, df_filtered[col], label=col, linestyle='-', linewidth=1.5)
    else:
        for col in plot_columns:
            plt.plot(df_filtered.index, df_filtered[col], label=col, linestyle='-', linewidth=1.5)

    # Format X axis
    if x_format == "Day":
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    elif x_format == "Week":
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    elif x_format == "Month":
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    elif x_format == "Year":
        plt.gca().xaxis.set_major_locator(mdates.YearLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    else:
        raise ValueError(f"Unrecognized x_format: {x_format}. Use 'Day', 'Week', 'Month', or 'Year'.")

    plt.xlabel(x_label, fontsize=10)
    plt.xticks(rotation=45, fontsize=8)

    # Format Y axis
    if y_format == "Decimal":
        plt.gca().yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    elif y_format == "Percentage":
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))
    elif y_format == "Scientific":
        plt.gca().yaxis.set_major_formatter(FormatStrFormatter("%.2e"))
    elif y_format == "log":
        plt.yscale("log")
    else:
        raise ValueError(f"Unrecognized y_format: {y_format}. Use 'Decimal', 'Percentage', or 'Scientific'.")
    
    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel(y_label, fontsize=10)
    plt.yticks(fontsize=8)

    # Format title, layout, grid, and legend
    plt.title(title, fontsize=12)
    plt.tight_layout()

    if grid == True:
        plt.grid(True, linestyle='--', alpha=0.7)

    if legend == True:
        plt.legend(fontsize=9)

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None
```

### plot_stats

```python
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.ticker import MultipleLocator

def plot_stats(
    stats_df: pd.DataFrame,
    plot_columns,
    title: str,
    x_label: str,
    x_rotation: int,
    x_tick_spacing: int,
    y_label: str,
    y_tick_spacing: int,
    grid: bool,
    legend: bool,
    export_plot: bool,
    plot_file_name: str,
) -> None:

    """
    Plot the price data from a DataFrame for a specified date range and columns.

    Parameters:
    -----------
    stats_df : pd.DataFrame
        DataFrame containing the price data to plot.
    plot_columns : str OR list
        List of columns to plot from the DataFrame. If none, all columns will be plotted.
    title : str
        Title of the plot.
    x_label : str
        Label for the x-axis.
    x_rotation : int
        Rotation angle for the x-axis date labels.
    x_tick_spacing : int
        Spacing for the x-axis ticks.
    y_label : str
        Label for the y-axis.
    y_tick_spacing : int
        Spacing for the y-axis ticks.
    grid : bool
        Whether to display a grid on the plot.
    legend : bool
        Whether to display a legend on the plot.
    export_plot : bool
        Whether to save the figure as a PNG file.
    plot_file_name : str
        File name for saving the figure (if save_fig is True).

    Returns:
    --------
    None
    """

    # Set plot figure size and background color
    plt.figure(figsize=(12, 6), facecolor="#F5F5F5")

    # Plot data
    if plot_columns == "All":
        for col in stats_df.columns:
            plt.scatter(stats_df.index, stats_df[col], label=col, linestyle='-', linewidth=1.5)
    else:
        for col in plot_columns:
            plt.scatter(stats_df.index, stats_df[col], label=col, linestyle='-', linewidth=1.5)

    # Format X axis
    plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
    plt.xlabel(x_label, fontsize=10)
    plt.xticks(rotation=x_rotation, fontsize=8)

    # Format Y axis
    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel(y_label, fontsize=10)
    plt.yticks(fontsize=8)

    # Format title, layout, grid, and legend
    plt.title(title, fontsize=12)
    plt.tight_layout()

    if grid == True:
        plt.grid(True, linestyle='--', alpha=0.7)

    if legend == True:
        plt.legend(fontsize=9)

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None
```

### plot_vix_with_trades

```python
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.ticker import MultipleLocator

def plot_vix_with_trades(
    vix_price_df: pd.DataFrame,
    trades_df: pd.DataFrame,
    plot_start_date: str,
    plot_end_date: str,
    x_tick_spacing: int,
    y_tick_spacing: int,
    index_number: str,
    export_plot: bool,
) -> pd.DataFrame:
    
    """
    Plot the VIX daily high and low prices, along with the VIX spikes, and trades.

    Parameters:
    -----------
    vix_price_df : pd.DataFrame
        Dataframe containing the VIX price data to plot.
    trades_df : pd.DataFrame
        Dataframe containing the trades data.
    plot_start_date : str
        Start date for the plot in 'YYYY-MM-DD' format.
    plot_end_date : str
        End date for the plot in 'YYYY-MM-DD' format.
    index_number : str
        Index number to be used in the file name of the plot export.
    export_plot : bool
        Whether to save the figure as a PNG file.

    Returns:
    --------
    vix_data : pd.DataFrame
        Dataframe containing the VIX price data for the specified timeframe.
    """

    # Create temporary dataframe for the specified date range
    vix_data = vix_price_df[(vix_price_df.index >= plot_start_date) & (vix_price_df.index <= plot_end_date)]

    # Set plot figure size and background color
    plt.figure(figsize=(12, 6), facecolor="#F5F5F5")

    # Plot VIX high and low price data
    plt.plot(vix_data.index, vix_data['High'], label='High', linestyle='-', color='steelblue', linewidth=1)
    plt.plot(vix_data.index, vix_data['Low'], label='Low', linestyle='-', color='brown', linewidth=1)

    # Plot VIX spikes
    plt.scatter(vix_data[vix_data['Spike_SMA'] == True].index, vix_data[vix_data['Spike_SMA'] == True]['High'], label='Spike (High > 1.25 * 10 Day High SMA)', color='black', s=20)
    
    # Plot trades
    plt.scatter(trades_df['Trade_Date'], trades_df['Approx_VIX_Level'], label='Trades', color='red', s=20)

    # Annotate each point in trades_df with the corresponding Action_Symbol
    for _, row in trades_df.iterrows():
        plt.text(
            row['Trade_Date'] + pd.Timedelta(days=1),
            row['Approx_VIX_Level'] + 0.1,
            row['TradeDate_Action_Symbol_VIX'],
            fontsize=9
        )

    # Format X axis
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=x_tick_spacing))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xlabel("Date", fontsize=10)
    plt.xticks(rotation=45, fontsize=8)

    # Format Y axis
    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel("VIX", fontsize=10)
    plt.yticks(fontsize=8)

    # Format title, layout, grid, and legend
    plt.title(f"CBOE Volatility Index (VIX), VIX Spikes, Trades, {plot_start_date} - {plot_end_date}", fontsize=12)
    plt.tight_layout()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=9)

    # Save figure and display plot
    if export_plot == True:
        # plt.savefig(f"{index_number}_VIX_Spike_Trades_{plot_start_date}_{plot_end_date}.png", dpi=300, bbox_inches="tight")
        plt.savefig(f"{index_number}_VIX_Spike_Trades.png", dpi=300, bbox_inches="tight")
    
    # Display the plot
    plt.show()

    return vix_data
```

### strategy_harry_brown_perm_port

```python
import pandas as pd

def strategy_harry_brown_perm_port(
    fund_list: str, 
    starting_cash: int, 
    cash_contrib: int, 
    close_prices_df: pd.DataFrame, 
    rebal_month: int, 
    rebal_day: int, 
    rebal_per_high: float, 
    rebal_per_low: float,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
    """
    Execute the re-balance strategy based on specified criteria.

    Parameters:
    -----------
    fund_list (str):
        List of funds for data to be combined from. Funds are strings in the form "BTC-USD".
    starting_cash (int):
        Starting investment balance.
    cash_contrib (int):
        Cash contribution to be made daily.
    close_prices_df (pd.DataFrame):
        DataFrame containing date and close prices for all funds to be included.
    rebal_month (int):
        Month for annual rebalance.
    rebal_day (int):
        Day for annual rebalance.
    rebal_per_high (float):
        High percentage for rebalance.
    rebal_per_low (float):
        Low percentage for rebalance.
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    df (pd.DataFrame):
        DataFrame containing strategy data for all funds to be included. Also dumps the df to excel for reference later.
    """

    num_funds = len(fund_list)

    df = close_prices_df.copy()
    df.reset_index(inplace = True)

    # Date to be used for annual rebalance
    target_month = rebal_month
    target_day = rebal_day

    # Create a dataframe with dates from the specific month
    rebal_date = df[df['Date'].dt.month == target_month]

    # Specify the date or the next closest
    rebal_date = rebal_date[rebal_date['Date'].dt.day >= target_day]

    # Group by year and take the first entry for each year
    rebal_dates_by_year = rebal_date.groupby(rebal_date['Date'].dt.year).first().reset_index(drop=True)

    '''
    Column order for the dataframe:
    df[fund + "_BA_Shares"]
    df[fund + "_BA_$_Invested"]
    df[fund + "_BA_Port_%"]
    df['Total_BA_$_Invested']
    df['Contribution']
    df['Rebalance']
    df[fund + "_AA_Shares"]
    df[fund + "_AA_$_Invested"]
    df[fund + "_AA_Port_%"]
    df['Total_AA_$_Invested']
    '''

    # Calculate the columns and initial values for before action (BA) shares, $ invested, and port %
    for fund in fund_list:
        df[fund + "_BA_Shares"] = starting_cash / num_funds / df[fund + "_Close"]
        df[fund + "_BA_$_Invested"] = df[fund + "_BA_Shares"] * df[fund + "_Close"]
        df[fund + "_BA_Port_%"] = 0.25

    # Set column values initially
    df['Total_BA_$_Invested'] = starting_cash
    df['Contribution'] = cash_contrib
    df['Rebalance'] = "No"

    # Set columns and values initially for after action (AA) shares, $ invested, and port %
    for fund in fund_list:
        df[fund + "_AA_Shares"] = starting_cash / num_funds / df[fund + "_Close"]
        df[fund + "_AA_$_Invested"] = df[fund + "_AA_Shares"] * df[fund + "_Close"]
        df[fund + "_AA_Port_%"] = 0.25
        
    # Set column value for after action (AA) total $ invested
    df['Total_AA_$_Invested'] = starting_cash

    # Iterate through the dataframe and execute the strategy
    for index, row in df.iterrows():

        # Ensure there's a previous row to reference by checking the index value
        if index > 0:

            # Initialize variable
            Total_BA_Invested = 0

            # Calculate before action (BA) shares and $ invested values
            for fund in fund_list:
                df.at[index, fund + "_BA_Shares"] = df.at[index - 1, fund + "_AA_Shares"]
                df.at[index, fund + "_BA_$_Invested"] = df.at[index, fund + "_BA_Shares"] * row[fund + "_Close"]

                # Sum the asset values to find the total
                Total_BA_Invested = Total_BA_Invested + df.at[index, fund + "_BA_$_Invested"]

            # Calculate before action (BA) port % values
            for fund in fund_list:
                df.at[index, fund + "_BA_Port_%"] = df.at[index, fund + "_BA_$_Invested"] / Total_BA_Invested

            # Set column for before action (BA) total $ invested
            df.at[index, 'Total_BA_$_Invested'] = Total_BA_Invested

            # Initialize variables
            rebalance = "No"
            date = row['Date']

            # Check for a specific date annually
            # Simple if statement to check if date_to_check is in jan_28_or_after_each_year
            if date in rebal_dates_by_year['Date'].values:
                rebalance = "Yes"
            else:
                pass

            # Check to see if any asset has portfolio percentage of greater than 35% or less than 15% and if so set variable
            for fund in fund_list:
                if df.at[index, fund + "_BA_Port_%"] > rebal_per_high or df.at[index, fund + "_BA_Port_%"] < rebal_per_low:
                    rebalance = "Yes"
                else:
                    pass

            # If rebalance is required, rebalance back to 25% for each asset, else just divide contribution evenly across assets
            if rebalance == "Yes":
                df.at[index, 'Rebalance'] = rebalance
                for fund in fund_list:
                        df.at[index, fund + "_AA_$_Invested"] = (Total_BA_Invested + df.at[index, 'Contribution']) * 0.25
            else:
                df.at[index, 'Rebalance'] = rebalance
                for fund in fund_list:
                        df.at[index, fund + "_AA_$_Invested"] = df.at[index, fund + "_BA_$_Invested"] + df.at[index, 'Contribution'] * 0.25

            # Initialize variable
            Total_AA_Invested = 0

            # Set column values for after action (AA) shares and port %
            for fund in fund_list:
                df.at[index, fund + "_AA_Shares"] = df.at[index, fund + "_AA_$_Invested"] / row[fund + "_Close"]

                # Sum the asset values to find the total
                Total_AA_Invested = Total_AA_Invested + df.at[index, fund + "_AA_$_Invested"]

            # Calculate after action (AA) port % values
            for fund in fund_list:
                df.at[index, fund + "_AA_Port_%"] = df.at[index, fund + "_AA_$_Invested"] / Total_AA_Invested

            # Set column for after action (AA) total $ invested
            df.at[index, 'Total_AA_$_Invested'] = Total_AA_Invested

        # If this is the first row
        else:
            pass

    df['Return'] = df['Total_AA_$_Invested'].pct_change()
    df['Cumulative_Return'] = (1 + df['Return']).cumprod()

    plan_name = '_'.join(fund_list)

    # Export to excel
    if excel_export == True:
        df.to_excel(f"{plan_name}_Strategy.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df.to_pickle(f"{plan_name}_Strategy.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        print(f"Strategy complete for {plan_name}")
    else:
        pass

    return df
```

### summary_stats

```python
import pandas as pd
import numpy as np

def summary_stats(
    fund_list: list[str], 
    df: pd.DataFrame, 
    period: str,
    use_calendar_days: bool,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
    """
    Calculate summary statistics for the given fund list and return data.

    Parameters:
    -----------
    fund_list (str):
        List of funds. This is used below in the excel/pickle export but not in the analysis.. Funds are strings in the form "BTC-USD".
    df (pd.DataFrame):
        Dataframe with return data.
    period (str):
        Period for which to calculate statistics. Options are "Monthly", "Weekly", "Daily".
    use_calendar_days (bool):
        If True, use calendar days for calculations. If False, use trading days.
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    df_stats (pd.DataFrame):
        pd.DataFrame: DataFrame containing various portfolio statistics.
    """

    period = period.strip().capitalize()

    # Map base timeframes
    period_to_timeframe = {
        "Monthly": 12,
        "Weekly": 52,
        "Daily": 365 if use_calendar_days else 252,
    }

    try:
        timeframe = period_to_timeframe[period]
    except KeyError:
        raise ValueError(f"Invalid period: {period}. Must be one of {list(period_to_timeframe.keys())}")

    df_stats = pd.DataFrame(df.mean(axis=0) * timeframe) # annualized
    # df_stats = pd.DataFrame((1 + df.mean(axis=0)) ** timeframe - 1) # annualized, this is this true annualized return but we will simply use the mean
    df_stats.columns = ['Annualized Mean']
    df_stats['Annualized Volatility'] = df.std() * np.sqrt(timeframe) # annualized
    df_stats['Annualized Sharpe Ratio'] = df_stats['Annualized Mean'] / df_stats['Annualized Volatility']

    df_cagr = (1 + df['Return']).cumprod()
    cagr = (df_cagr.iloc[-1] / 1) ** ( 1 / (len(df_cagr) / timeframe)) - 1
    df_stats['CAGR'] = cagr

    df_stats[f'{period} Max Return'] = df.max()
    df_stats[f'{period} Max Return (Date)'] = df.idxmax().values[0]
    df_stats[f'{period} Min Return'] = df.min()
    df_stats[f'{period} Min Return (Date)'] = df.idxmin().values[0]
    
    wealth_index = 1000 * (1 + df).cumprod()
    previous_peaks = wealth_index.cummax()
    drawdowns = (wealth_index - previous_peaks) / previous_peaks

    df_stats['Max Drawdown'] = drawdowns.min()
    df_stats['Peak'] = [previous_peaks[col][:drawdowns[col].idxmin()].idxmax() for col in previous_peaks.columns]
    df_stats['Bottom'] = drawdowns.idxmin()

    recovery_date = []
    for col in wealth_index.columns:
        prev_max = previous_peaks[col][:drawdowns[col].idxmin()].max()
        recovery_wealth = pd.DataFrame([wealth_index[col][drawdowns[col].idxmin():]]).T
        recovery_date.append(recovery_wealth[recovery_wealth[col] >= prev_max].index.min())
    df_stats['Recovery Date'] = recovery_date

    plan_name = '_'.join(fund_list)

    # Export to excel
    if excel_export == True:
        df_stats.to_excel(f"{plan_name}_Summary_Stats.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df_stats.to_pickle(f"{plan_name}_Summary_Stats.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        print(f"Summary stats complete for {plan_name}")
    else:
        pass
    
    return df_stats
```

### yf_pull_data

```python
import os
import pandas as pd
import yfinance as yf

from IPython.display import display

def yf_pull_data(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
    """
    Download daily price data from Yahoo Finance and export it.

    Parameters:
    -----------
    base_directory
        Root path to store downloaded data.
    ticker : str
        Ticker symbol to download.
    source : str
        Name of the data source (e.g., 'Yahoo').
    asset_class : str
        Asset class name (e.g., 'Equities').
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    df : pd.DataFrame
        DataFrame containing the downloaded data.
    """
    
    # Download data from YF
    df = yf.download(ticker)

    # Drop the column level with the ticker symbol
    df.columns = df.columns.droplevel(1)

    # Reset index
    df = df.reset_index()

    # Remove the "Price" header from the index
    df.columns.name = None

    # Reset date column
    df['Date'] = df['Date'].dt.tz_localize(None)

    # Set 'Date' column as index
    df = df.set_index('Date', drop=True)

    # Drop data from last day because it's not accrate until end of day
    df = df.drop(df.index[-1])
    
    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/Daily"
    os.makedirs(directory, exist_ok=True)

    # Export to excel
    if excel_export == True:
        df.to_excel(f"{directory}/{ticker}.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df.to_pickle(f"{directory}/{ticker}.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        print(f"The first and last date of data for {ticker} is: ")
        display(df[:1])
        display(df[-1:])
        print(f"Yahoo Finance data complete for {ticker}")
        print(f"--------------------")
    else:
        pass

    return df
```

## References

None

## Code

The jupyter notebook with the functions and all other code is available [here](reusable-extensible-python-functions-financial-data-analysis.ipynb).</br>
The html export of the jupyter notebook is available [here](reusable-extensible-python-functions-financial-data-analysis.html).</br>
The pdf export of the jupyter notebook is available [here](reusable-extensible-python-functions-financial-data-analysis.pdf).