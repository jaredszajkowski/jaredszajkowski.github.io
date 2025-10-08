import os
import pandas as pd
import time

from datetime import datetime, timedelta
from IPython.display import display
from load_api_keys import load_api_keys
from polygon import RESTClient
from polygon_fetch_full_history import polygon_fetch_full_history
from settings import config

# Load API keys from the environment
api_keys = load_api_keys()

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

def polygon_pull_data(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    start_date: datetime,
    timespan: str,
    multiplier: int,
    adjusted: bool,
    force_existing_check: bool,
    free_tier: bool,
    verbose: bool,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
    """
    Read existing data file, download price data from Polygon, and export data.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    ticker : str
        Ticker symbol to download.
    source : str
        Name of the data source (e.g., 'Polygon').
    asset_class : str
        Asset class name (e.g., 'Equities').
    start_date : datetime
        Start date for the data in datetime format.
    timespan : str
        Time span for the data (e.g., "minute", "hour", "day", "week", "month", "quarter", "year").
    multiplier : int
        Multiplier for the time span (e.g., 1 for daily data).
    adjusted : bool
        If True, return adjusted data; if False, return raw data.
    force_existing_check : bool
        If True, force a complete check of the existing data file to verify that there are not any gaps in the data.
    free_tier : bool
        If True, then pause to avoid API limits.
    verbose : bool
        If True, print detailed information about the data being processed.
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    None
    """

    # Open client connection
    client = RESTClient(api_key=api_keys["POLYGON_KEY"])

    # Set file location based on parameters
    file_location = f"{base_directory}/{source}/{asset_class}/{timespan}/{ticker}.pkl"

    if timespan == "minute":
        time_delta = 15
        time_overlap = 1
    elif timespan == "hour":
        time_delta = 15
        time_overlap = 1
    elif timespan == "day":
        time_delta = 180
        time_overlap = 1
    else:
        raise Exception(f"Invalid {timespan}.")

    try:
        # Attempt to read existing pickle data file
        existing_history_df = pd.read_pickle(file_location)

        # Reset index if 'Date' is column is the index
        if 'Date' not in existing_history_df.columns:
            existing_history_df = existing_history_df.reset_index()

        print(f"File found...updating the {ticker} {timespan} data.")

        if verbose ==True:
            print("Existing data:")
            print(existing_history_df)

        # Find last date in existing data
        last_data_date = existing_history_df['Date'].max()
        print(f"Last date in existing data: {last_data_date}")

        starting_rows = len(existing_history_df)
        print(f"Number of rows in existing data: {starting_rows}")

        # Overlap with existing data to capture all data
        current_start = last_data_date - timedelta(days=time_overlap)

    except FileNotFoundError:
        # Print error
        print(f"File not found...downloading the {ticker} {timespan} data.")

        # Create an empty DataFrame
        existing_history_df = pd.DataFrame({
            'Date': pd.Series(dtype="datetime64[ns]"),
            'open': pd.Series(dtype="float64"),
            'high': pd.Series(dtype="float64"),
            'low': pd.Series(dtype="float64"),
            'close': pd.Series(dtype="float64"),
            'volume': pd.Series(dtype="float64"),
            'vwap': pd.Series(dtype="float64"),
            'transactions': pd.Series(dtype="int64"),
            'otc': pd.Series(dtype="object")
        })

        # Set current date to start date
        current_start = start_date

    # Check for force_existing_check flag
    if force_existing_check == True:
        print("Forcing check of existing data...")
        current_start = start_date

    full_history_df = polygon_fetch_full_history(
        client=client,
        ticker=ticker,
        timespan=timespan,
        multiplier=multiplier,
        adjusted=adjusted,
        existing_history_df=existing_history_df,
        current_start=current_start,
        free_tier=free_tier,
        verbose=verbose,
    )

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/{timespan}"
    os.makedirs(directory, exist_ok=True)

    # Export to Excel
    if excel_export == True:
        print(f"Exporting {ticker} {timespan} data to Excel...")
        full_history_df.to_excel(f"{directory}/{ticker}.xlsx", sheet_name="data")

    # Export to Pickle
    if pickle_export == True:
        print(f"Exporting {ticker} {timespan} data to Pickle...")
        full_history_df.to_pickle(f"{directory}/{ticker}.pkl")

    total_rows = len(full_history_df)

    # Output confirmation
    if output_confirmation == True:
        print(f"The first and last date of {timespan} data for {ticker} is: ")
        display(full_history_df[:1])
        display(full_history_df[-1:])
        print(f"Number of rows after data update: {total_rows}")

        if starting_rows:
            print(f"Number of rows added during update: {total_rows - starting_rows}")

        print(f"Polygon data complete for {ticker} {timespan} data.")
        print(f"--------------------")

    return full_history_df

if __name__ == "__main__":

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    # Stock Data
    equities = ["AMZN", "AAPL"]

    # Iterate through each stock
    for stock in equities:
        # Example usage - minute
        polygon_pull_data(
            base_directory=DATA_DIR,
            ticker=stock,
            source="Polygon",
            asset_class="Equities",
            start_date=datetime(current_year - 2, current_month, current_day),
            timespan="minute",
            multiplier=1,
            adjusted=True,
            force_existing_check=False,
            free_tier=True,
            verbose=False,
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
        )

        time.sleep(12)

        # Example usage - hourly
        polygon_pull_data(
            base_directory=DATA_DIR,
            ticker=stock,
            source="Polygon",
            asset_class="Equities",
            start_date=datetime(current_year - 2, current_month, current_day),
            timespan="hour",
            multiplier=1,
            adjusted=True,
            force_existing_check=False,
            free_tier=True,
            verbose=False,
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
        )

        time.sleep(12)

        # Example usage - daily
        polygon_pull_data(
            base_directory=DATA_DIR,
            ticker=stock,
            source="Polygon",
            asset_class="Equities",
            start_date=datetime(current_year - 2, current_month, current_day),
            timespan="day",
            multiplier=1,
            adjusted=True,
            force_existing_check=False,
            free_tier=True,
            verbose=False,
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
        )

        time.sleep(12)