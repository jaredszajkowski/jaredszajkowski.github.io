import os
import pandas as pd

from IPython.display import display

def ndl_month_end_total_return(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
    """
    Read daily data from an existing excel file and export month-end total return close prices.

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
    df_month_end_total_return : pd.DataFrame
        DataFrame containing month-end total return close prices.
    """

    # Set location from where to read existing excel file
    location = f"{base_directory}/{source}/{asset_class}/Daily/{ticker}.xlsx"

    # Read data from excel
    df = pd.read_excel(location, sheet_name="data", engine="calamine")
    
    # Keep only required columns
    df = df[['Date', 'adj_close']]

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