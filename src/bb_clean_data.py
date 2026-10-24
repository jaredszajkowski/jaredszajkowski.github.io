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
    This function takes an excel export from Bloomberg and removes all
    excess data leaving date and close columns.

    Parameters
    ----------
    base_directory : str
        Root path to store downloaded data.
    fund_ticker_name : str
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

    Returns
    -------
    df : pd.DataFrame
        DataFrame containing cleaned data prices.

    Raises
    ------
    FileNotFoundError:
        If the excel export for `fund_ticker_name` has not been downloaded.
    ValueError:
        If the export contains no header row beginning with "Date".
    """

    # Set location from where to read existing excel file
    location = f"{base_directory}/{source}/{asset_class}/Daily/{fund_ticker_name}.xlsx"

    # Read data from excel, treating every row as data so the header row can be
    # located below
    try:
        df = pd.read_excel(
            location, sheet_name="Worksheet", engine="calamine", header=None
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"File not found...please download the data for {fund_ticker_name}: {location}"
        ) from e

    # Find the header row - Bloomberg writes a variable number of metadata rows
    # (Security, Start Date, End Date, Period, and sometimes Currency or Pricing
    # Source) above the row whose first cell is "Date"
    header_rows = df.index[df.iloc[:, 0].astype(str).str.strip() == "Date"]
    if len(header_rows) == 0:
        raise ValueError(f"No row starting with 'Date' found in {location}")
    header_row = header_rows[0]

    # Set the column headings from the header row
    df.columns = df.iloc[header_row]

    # Set the column heading for the index to be "None"
    df.rename_axis(None, axis=1, inplace=True)

    # Drop the metadata rows along with the header row itself
    df.drop(df.index[0 : header_row + 1], inplace=True)

    # Set the date column as the index
    df.set_index("Date", inplace=True)

    # Drop the volume column
    try:
        df.drop(columns={"PX_VOLUME"}, inplace=True)
    except KeyError:
        pass

    # Rename column
    try:
        df.rename(columns={"PX_LAST": "Close"}, inplace=True)
        df.rename(columns={"PX_OPEN": "Open"}, inplace=True)
        df.rename(columns={"PX_HIGH": "High"}, inplace=True)
        df.rename(columns={"PX_LOW": "Low"}, inplace=True)
    except KeyError:
        pass

    # Sort by date
    df.sort_values(by=["Date"], inplace=True)

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
