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