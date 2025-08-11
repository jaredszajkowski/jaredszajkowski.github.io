```python
import os
import pandas as pd

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

    try:
        # Attempt to read existing pickle data file
        full_history_df = pd.read_pickle(file_location)

        # Reset index if 'Date' is column is the index
        if 'Date' not in full_history_df.columns:
            full_history_df = full_history_df.reset_index()

        print(f"File found...updating the {ticker} {timespan} data.")
        print("Existing data:")
        print(full_history_df)

        # Find last date in existing data
        last_date = full_history_df['Date'].max()
        print(f"Last date in existing data: {last_date}")

        # Overlap 1 day with existing data to capture all data
        current_start = last_date - timedelta(days=1)

    except FileNotFoundError:
        # Print error
        print(f"File not found...downloading the {ticker} {timespan} data.")

        # Create an empty DataFrame
        full_history_df = pd.DataFrame({
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

    full_history_df = polygon_fetch_full_history(
        client=client,
        ticker=ticker,
        timespan=timespan,
        multiplier=multiplier,
        adjusted=adjusted,
        full_history_df=full_history_df,
        current_start=current_start,
        free_tier=True,
    )

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/{timespan}"
    os.makedirs(directory, exist_ok=True)

    # Export to Excel
    if excel_export == True:
        print(f"Exporting {ticker} {timespan} data to Excel...")
        full_history_df.to_excel(f"{directory}/{ticker}.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        print(f"Exporting {ticker} {timespan} data to pickle...")
        full_history_df.to_pickle(f"{directory}/{ticker}.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        print(f"The first and last date of data for {ticker} is: ")
        display(full_history_df[:1])
        display(full_history_df[-1:])
        print(f"Polygon data complete for {ticker}")
        print(f"--------------------")
    else:
        pass

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
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
        )

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
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
        )

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
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
        )
```