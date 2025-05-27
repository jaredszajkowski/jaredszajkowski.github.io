---
title: Reusable And Extensible Python Functions For Financial Data Analysis
description: A list of common functions used for data acquisition, cleaning, analysis, etc.
slug: reusable-extensible-python-functions-financial-data-analysis
date: 2025-02-02 00:00:01+0000
lastmod: 2025-05-26 00:00:01+0000
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

### Functions For Assembling/Processing Posts

[build_index](#build_index): Reads the `index_temp.md` markdown file and inserts the markdown dependencies where indicated.</br>
[export_track_md_deps](#export_track_md_deps): exports various text outputs to markdown files, which are included in the index.md file created when building the site with Hugo.

### Bloomberg Functions

[bb_clean_data](#bb_clean_data): Takes an Excel export from Bloomberg, removes the miscellaneous headings/rows, and returns a DataFrame.

### Analysis Functions

[calc_vix_trade_pnl](#calc_vix_trade_pnl): Calculates the profit/loss from VIX options trades.

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

## References

None

## Code

The jupyter notebook with the functions and all other code is available [here](reusable-extensible-python-functions-financial-data-analysis.ipynb).</br>
The html export of the jupyter notebook is available [here](reusable-extensible-python-functions-financial-data-analysis.html).</br>
The pdf export of the jupyter notebook is available [here](reusable-extensible-python-functions-financial-data-analysis.pdf).