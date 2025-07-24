import os
import pandas as pd

from IPython.display import display

def yf_month_end(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
    """
    Read daily data from an existing excel file and export month-end close prices.

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
    df_month_end : pd.DataFrame
        DataFrame containing month-end close prices.
    """

    # Set location from where to read existing excel file
    location = f"{base_directory}/{source}/{asset_class}/Daily/{ticker}.xlsx"

    # Read data from excel
    df = pd.read_excel(location, sheet_name ="data", engine="calamine")

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

    # Output confirmation
    if output_confirmation == True:
        print(f"Month end data complete for {ticker}")
        print(f"--------------------")
    else:
        pass

    return df_month_end