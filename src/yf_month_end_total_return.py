import pandas as pd
import os
from IPython.display import display

def yf_month_end_total_return(
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
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
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    df_month_end_total_return : pd.DataFrame
        DataFrame containing month-end total return close prices.
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

    # Output confirmation
    if output_confirmation == True:
        print(f"Month end total return data complete for {ticker}")
        print(f"--------------------")
    else:
        pass

    return df_month_end_total_return