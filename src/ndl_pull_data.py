import nasdaqdatalink
import numpy as np
import os
import pandas as pd

from IPython.display import display
from load_api_keys import load_api_keys
from pathlib import Path
from settings import config

# Load API keys from the environment
api_keys = load_api_keys()

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

def ndl_pull_data(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
    """
    Download daily price ata from Nasdaq Data Link and add many missing columns and export it.

    Parameters:
    -----------
    base_directory
        Root path to store downloaded data.
    ticker : str
        Ticker symbol to download.
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

    Returns:
    --------
    df : pd.DataFrame
        DataFrame containing the downloaded data.
    """

    # Command to pull data
    # If start date and end date are not specified the entire data set is included
    df = nasdaqdatalink.get_table("QUOTEMEDIA/PRICES", ticker=ticker, paginate=True, api_key=api_keys["NASDAQ_DATA_LINK_KEY"])

    # Sort columns by date ascending
    df.sort_values('date', ascending = True, inplace = True)

    # Rename the date column
    df.rename(columns = {'date':'Date'}, inplace = True)

    # Set index to date column
    df.set_index('Date', inplace = True)

    # Replace all split values of 1.0 with NaN
    df['split'] = df['split'].replace(1.0, np.nan)

    # Create a new data frame with split values only
    df_splits = df.drop(columns = {'ticker', 'open', 'high', 'low', 
                                   'close', 'volume', 'dividend', 
                                   'adj_open', 'adj_high', 
                                   'adj_low', 'adj_close', 
                                   'adj_volume'}).dropna()

    # Create a new column for cumulative split
    df_splits['Cum_Split'] = df_splits['split'].cumprod()

    # Drop original split column before combining dataframes
    df_splits.drop(columns = {'split'}, inplace = True)

    # Merge df and df_split dataframes
    df_comp = pd.merge(df, df_splits, on='Date', how="outer")

    # Forward fill for all cumulative split values
    df_comp['Cum_Split'] = df_comp['Cum_Split'].ffill()

    # Replace all split and cumulative split values of NaN with 1.0 to have complete split values
    df_comp['split'] = df_comp['split'].replace(np.nan, 1.0)
    df_comp['Cum_Split'] = df_comp['Cum_Split'].replace(np.nan, 1.0)

    # Calculate the non adjusted prices based on the splits only
    df_comp['non_adj_open_split_only'] = df_comp['open'] * df_comp['Cum_Split']
    df_comp['non_adj_high_split_only'] = df_comp['high'] * df_comp['Cum_Split']
    df_comp['non_adj_low_split_only'] = df_comp['low'] * df_comp['Cum_Split']
    df_comp['non_adj_close_split_only'] = df_comp['close'] * df_comp['Cum_Split']
    df_comp['non_adj_dividend_split_only'] = df_comp['dividend'] * df_comp['Cum_Split']

    # Calculate the adjusted prices based on the splits
    df_comp['Open'] = df_comp['non_adj_open_split_only'] / df_comp['Cum_Split'][-1]
    df_comp['High'] = df_comp['non_adj_high_split_only'] / df_comp['Cum_Split'][-1]
    df_comp['Low'] = df_comp['non_adj_low_split_only'] / df_comp['Cum_Split'][-1]
    df_comp['Close'] = df_comp['non_adj_close_split_only'] / df_comp['Cum_Split'][-1]
    df_comp['Dividend'] = df_comp['non_adj_dividend_split_only'] / df_comp['Cum_Split'][-1]
    df_comp['Dividend_Pct_Orig'] = df_comp['dividend'] / df_comp['close']
    df_comp['Dividend_Pct_Adj'] = df_comp['Dividend'] / df_comp['Close']

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/Daily"
    os.makedirs(directory, exist_ok=True)

    # Export to excel
    if excel_export == True:
        df_comp.to_excel(f"{directory}/{ticker}.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df_comp.to_pickle(f"{directory}/{ticker}.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        print(f"The first and last date of data for {ticker} is: ")
        display(df_comp[:1])
        display(df_comp[-1:])
        print(f"NDL data complete for {ticker}")
        print(f"--------------------")
    else:
        pass

    return df_comp

if __name__ == "__main__":

    ndl_pull_data(
        base_directory=DATA_DIR,
        ticker="TLT",
        source="Nasdaq_Data_Link",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )