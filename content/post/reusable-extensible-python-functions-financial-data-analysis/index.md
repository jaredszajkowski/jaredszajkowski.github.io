---
title: Reusable And Extensible Python Functions For Financial Data Analysis
description: A list of common functions used for data acquisition, cleaning, analysis, etc.
slug: reusable-extensible-python-functions-financial-data-analysis
date: 2025-02-02 00:00:01+0000
lastmod: 2025-06-04 00:00:01+0000
image: cover.jpg
draft: false
categories:
    - Tutorials
    - Tech
tags:
    - Bloomberg
    - Nasdaq Data Link
    - pandas
    - Python
    - Yahoo Finance
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
* [df_info](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#df_info): A simple function to display the information about a DataFrame and the first five rows and last five rows.</br>
* [df_info_markdown](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#df_info_markdown): Similar to the `df_info` function above, except that it coverts the output to markdown.</br>
* [export_track_md_deps](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#export_track_md_deps): Exports various text outputs to markdown files, which are included in the `index.md` file created when building the site with Hugo.</br>
* [load_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.</br>
* [pandas_set_decimal_places](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.</br>
* [plot_price](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#plot_price): Plot the price data from a DataFrame for a specified date range and columns.</br>
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
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, str]:
    
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

    # Calculate the net % PnL and $ PnL
    net_PnL_percent = closed_trades['Realized_PnL'].sum() / closed_trades['Amount_Buy'].sum()
    net_PnL_percent_str = f"{round(net_PnL_percent * 100, 2)}%"

    net_PnL = closed_trades['Realized_PnL'].sum()
    net_PnL_str = f"${net_PnL:,.2f}"

    # Create a new dataframe for open positions
    open_trades = merged_transactions[~merged_transactions['Closed']]
    open_trades = open_trades.reset_index(drop=True)
    open_trades.drop(columns={'Closed', 'Amount_Sell', 'Quantity_Sell', 'Exp_Date'}, inplace=True)

    return transactions_data, closed_trades, open_trades, net_PnL_percent_str, net_PnL_str
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
    }

    # Raise error if any key is missing
    for k, v in keys.items():
        if not v:
            raise ValueError(f"Missing environment variable: {k}")

    return keys

```

### load_data

```python
import pandas as pd
from pathlib import Path

def load_data(
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    timeframe: str,
) -> pd.DataFrame:
    
    """
    Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.

    This function attempts to read a file first as a CSV, then as an Excel file 
    (specifically looking for a sheet named 'data' and using the 'calamine' engine).
    If both attempts fail, a ValueError is raised.

    Parameters:
    -----------
    base_directory : str
        Root path to read data file.
    ticker : str
        Ticker symbol to read.
    source : str
        Name of the data source (e.g., 'Yahoo').
    asset_class : str
        Asset class name (e.g., 'Equities').
    timeframe : str
        Timeframe for the data (e.g., 'Daily', 'Month_End').
    
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

    # Build file paths using pathlib
    csv_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.csv"
    csv_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.zip"
    xlsx_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.xlsx"
    pickle_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.pkl"

    # Try CSV
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception:
        pass

    # Try Zip
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception:
        pass

    # Try Excel
    try:
        df = pd.read_excel(xlsx_path)
        return df
    except Exception:
        pass

    # Try Pickle
    try:
        df = pd.read_pickle(pickle_path)
        return df
    except Exception:
        pass

    raise ValueError(f"❌ Unable to load file: {ticker}. Ensure it's a valid CSV, Excel, Zip, or Pickle file with a 'data' sheet (if required).")
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
        plt.savefig(f"{index_number}_VIX_Spike_Trades_{plot_start_date}_{plot_end_date}.png", dpi=300, bbox_inches="tight")
    
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
    fund_list: str, 
    df: pd.DataFrame, 
    period: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
    """
    Calculate summary statistics for the given fund list and return data.

    Parameters:
    -----------
    fund_list (str):
        List of funds for data to be combined from. Funds are strings in the form "BTC-USD".
    df (pd.DataFrame):
        Dataframe with return data.
    period (str):
        Period for which to calculate statistics. Options are "Monthly", "Weekly", "Daily", "Hourly".
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

    if period == "Monthly":
        timeframe = 12 # months
    elif period == "Weekly":
        timeframe = 52 # weeks
    elif period == "Daily":
        timeframe = 252 # days
        # timeframe = 365 # days
    elif period == "Hourly":
        timeframe = 252 * 6.5 # hours
    #     timeframe = 8760 # hours
    # else:
        return print("Error, check inputs")

    df_stats = pd.DataFrame(df.mean(axis=0) * timeframe) # annualized
    # df_stats = pd.DataFrame((1 + df.mean(axis=0)) ** timeframe - 1) # annualized, this is this true annualized return but we will simply use the mean
    df_stats.columns = ['Annualized Mean']
    df_stats['Annualized Volatility'] = df.std() * np.sqrt(timeframe) # annualized
    df_stats['Annualized Sharpe Ratio'] = df_stats['Annualized Mean'] / df_stats['Annualized Volatility']

    df_cagr = (1 + df['Return']).cumprod()
    cagr = (df_cagr.iloc[-1] / 1) ** (1/(len(df_cagr) / timeframe)) - 1
    df_stats['CAGR'] = cagr

    df_stats[period + ' Max Return'] = df.max()
    df_stats[period + ' Max Return (Date)'] = df.idxmax().values[0]
    df_stats[period + ' Min Return'] = df.min()
    df_stats[period + ' Min Return (Date)'] = df.idxmin().values[0]
    
    wealth_index = 1000 * (1 + df).cumprod()
    previous_peaks = wealth_index.cummax()
    drawdowns = (wealth_index - previous_peaks)/previous_peaks

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
    base_directory: str,
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
    base_directory : str
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