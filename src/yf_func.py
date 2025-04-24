import pandas as pd
import numpy as np
import yfinance as yf
import os
from IPython.display import display

def yf_pull_data(
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
) -> None:
    
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

    Returns:
    --------
    None
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

    # Print confirmation and display the first and last date 
    # of data
    print(f"The first and last date of data for {ticker} is: ")
    display(df[:1])
    display(df[-1:])
    print(f"Yahoo Finance data complete for {ticker}")
    return print(f"--------------------")

def yf_month_end(
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
) -> None:
    
    """
    Read daily data from an existing excel file and export month-end close prices.

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

    Returns:
    --------
    None
    """

    # Set location from where to read existing excel file
    location = f"{base_directory}/{source}/{asset_class}/Daily/{ticker}.xlsx"

    # Read data from excel
    try:
        df = pd.read_excel(location, sheet_name ="data", engine="calamine")
    except FileNotFoundError:
        print(f"File not found...please download the data for {ticker}")

    # Keep only required columns
    df = df[['Date', 'Close']]

    # Set index to date column
    df.set_index('Date', inplace=True)
    
    # Resample data to month end
    df_month_end = df.resample("ME").last()

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/Month_End"
    os.makedirs(directory, exist_ok=True)

    # Export to excel
    if excel_export == True:
        df_month_end.to_excel(f"{directory}/{ticker}_ME.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df_month_end.to_pickle(f"{directory}/{ticker}_ME.pkl")
    else:
        pass

    # Print confirmation and the first and last date of data
    # print(f"The first and last date of data for {ticker} is: ")
    # display(df[:1])
    # display(df[-1:])
    print(f"Month end data complete for {ticker}")
    return print(f"--------------------")

def yf_month_end_total_return(
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
) -> None:
    
    """
    Read daily data from an existing excel file and export month-end total return close prices.

    Uses 'Adj Close' if available, otherwise falls back to 'Close'.

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

    Returns:
    --------
    None
    """

    # Set location from where to read existing excel file
    location = f"{base_directory}/{source}/{asset_class}/Daily/{ticker}.xlsx"

    # Read data from excel
    try:
        df = pd.read_excel(location, sheet_name ="data", engine="calamine")
    except FileNotFoundError:
        print(f"File not found...please download the data for {ticker}")

    # Keep only required columns

    # Check if there is an 'Adj_Close' column
    if 'Adj Close' in df.columns:
        df = df[['Date', 'Adj Close']]

    # Check if there is a 'Close' column
    elif 'Close' in df.columns:
        df = df[['Date', 'Close']]

    # If neither is found, print an error message and exit
    else:
        print(f"Close or Adj Close not found in columns, skipping...")
        exit()

    # Set index to date column
    df.set_index('Date', inplace=True)

    # Resample data to month end
    df_month_end_total_return = df.resample("ME").last()

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/Month_End_Total_Return"
    os.makedirs(directory, exist_ok=True)

    # Export to excel
    if excel_export == True:
        df_month_end_total_return.to_excel(f"{directory}/{ticker}_ME_TR.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df_month_end_total_return.to_pickle(f"{directory}/{ticker}_ME_TR.pkl")
    else:
        pass

    # Print confirmation and the first and last date of data
    # print(f"The first and last date of data for {ticker} is: ")
    # display(df[:1])
    # display(df[-1:])
    print(f"Month end total return data complete for {ticker}")
    return print(f"--------------------")

def yf_quarter_end(
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
) -> None:
    
    """
    Read daily data from an existing excel file and export quarter-end close prices.

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

    Returns:
    --------
    None
    """

    # Set location from where to read existing excel file
    location = f"{base_directory}/{source}/{asset_class}/Daily/{ticker}.xlsx"

    # Read data from excel
    try:
        df = pd.read_excel(location, sheet_name="data", engine="calamine")
    except FileNotFoundError:
        print(f"File not found...please download the data for {ticker}")

    # Keep only required columns
    df = df[['Date', 'Close']]

    # Set index to date column
    df.set_index('Date', inplace=True)
    
    # Resample data to month end
    df_quarter_end = df.resample("QE").last()

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/Quarter_End"
    os.makedirs(directory, exist_ok=True)

    # Export to excel
    if excel_export == True:
        df_quarter_end.to_excel(f"{directory}/{ticker}_QE.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df_quarter_end.to_pickle(f"{directory}/{ticker}_QE.pkl")
    else:
        pass

    # Print confirmation and the first and last date of data
    # print(f"The first and last date of data for {ticker} is: ")
    # display(df[:1])
    # display(df[-1:])
    print(f"Quarter end data complete for {ticker}")
    return print(f"--------------------")

def yf_quarter_end_total_return(
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
) -> None:
    
    """
    Read daily data from an existing excel file and export quarter-end total return close prices.

    Uses 'Adj Close' if available, otherwise falls back to 'Close'.

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

    Returns:
    --------
    None
    """   

    # Set location from where to read existing excel file
    location = f"{base_directory}/{source}/{asset_class}/Daily/{ticker}.xlsx"

    # Read data from excel
    try:
        df = pd.read_excel(location, sheet_name="data", engine="calamine")
    except FileNotFoundError:
        print(f"File not found...please download the data for {ticker}")

    # Keep only required columns

    # Check if there is an 'Adj_Close' column
    if 'Adj Close' in df.columns:
        df = df[['Date', 'Adj Close']]

    # Check if there is a 'Close' column
    elif 'Close' in df.columns:
        df = df[['Date', 'Close']]

    # If neither is found, print an error message and exit
    else:
        print(f"Close or Adj Close not found in columns, skipping...")
        exit()

    # Set index to date column
    df.set_index('Date', inplace=True)
    
    # Resample data to quarter end
    df_quarter_end_total_return = df.resample("QE").last()

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/Quarter_End_Total_Return"
    os.makedirs(directory, exist_ok=True)

    # Export to excel
    if excel_export == True:
        df_quarter_end_total_return.to_excel(f"{directory}/{ticker}_QE_TR.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df_quarter_end_total_return.to_pickle(f"{directory}/{ticker}_QE_TR.pkl")
    else:
        pass

    # Print confirmation and the first and last date of data
    # print(f"The first and last date of data for {ticker} is: ")
    # display(df[:1])
    # display(df[-1:])
    print(f"Quarter end total return data complete for {ticker}")
    return print(f"--------------------")