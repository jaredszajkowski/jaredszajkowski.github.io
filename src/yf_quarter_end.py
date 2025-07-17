import os
import pandas as pd

from IPython.display import display

def yf_quarter_end(
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
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
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    df_quarter_end : pd.DataFrame
        DataFrame containing quarter-end close prices.
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

    # Output confirmation
    if output_confirmation == True:
        print(f"Quarter end data complete for {ticker}")
        print(f"--------------------")
    else:
        pass
    
    return df_quarter_end