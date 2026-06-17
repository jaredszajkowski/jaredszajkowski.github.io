import databento as db
import os
import pandas as pd

from datetime import datetime, timedelta
from IPython.display import display
from databento_fetch_full_history import databento_fetch_full_history
from settings import config

# Load API key from the environment variables
DATABENTO_KEY = config("DATABENTO_KEY")

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")


def databento_pull_data(
    base_directory,
    symbol: str,
    dataset: str,
    source: str,
    asset_class: str,
    start_date: datetime,
    schema: str,
    force_existing_check: bool,
    verbose: bool,
    excel_export: bool,
    pickle_export: bool,
    parquet_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    """
    Read existing data file, download OHLCV data from DataBento, and export data.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    symbol : str
        Symbol to download (e.g., "AAPL").
    dataset : str
        DataBento dataset identifier (e.g., "XNAS.ITCH", "DBEQ.BASIC", "GLBX.MDP3").
    source : str
        Name of the data source (e.g., "DataBento").
    asset_class : str
        Asset class name (e.g., "Equities").
    start_date : datetime
        Start date for the data in datetime format.
    schema : str
        DataBento schema (e.g., "ohlcv-1m", "ohlcv-1h", "ohlcv-1d").
    force_existing_check : bool
        If True, force a complete check of the existing data file to verify there are no gaps.
    verbose : bool
        If True, print detailed information about the data being processed.
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    parquet_export : bool
        If True, export data to Parquet format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    pd.DataFrame
        DataFrame containing the updated OHLCV data.
    """

    # Open client connection
    client = db.Historical(key=DATABENTO_KEY)

    # Validate schema
    acceptable_schemas = ["ohlcv-1m", "ohlcv-1h", "ohlcv-1d"]
    if schema not in acceptable_schemas:
        raise ValueError(
            f"Invalid schema: {schema}. Acceptable schemas are: {acceptable_schemas}."
        )

    # Set file location based on parameters
    file_location = f"{base_directory}/{source}/{asset_class}/{schema}/{symbol}.pkl"

    try:
        # Attempt to read existing pickle data file
        existing_history_df = pd.read_pickle(file_location)

        # Reset index if 'Date' is the index
        if "Date" not in existing_history_df.columns:
            existing_history_df = existing_history_df.reset_index()

        print(f"File found...updating the {symbol} {schema} data.")

        if verbose:
            print("Existing data:")
            print(existing_history_df)

        last_data_date = existing_history_df["Date"].max()
        print(f"Last date in existing data: {last_data_date}")

        starting_rows = len(existing_history_df)
        print(f"Number of rows in existing data: {starting_rows}")

        current_start = last_data_date - timedelta(days=1)

    except FileNotFoundError:
        print(f"File not found...downloading the {symbol} {schema} data.")

        existing_history_df = pd.DataFrame(
            {
                "Date": pd.Series(dtype="datetime64[ns]"),
                "open": pd.Series(dtype="float64"),
                "high": pd.Series(dtype="float64"),
                "low": pd.Series(dtype="float64"),
                "close": pd.Series(dtype="float64"),
                "volume": pd.Series(dtype="int64"),
            }
        )

        starting_rows = 0
        current_start = start_date

    if force_existing_check:
        print("Forcing check of existing data...")
        current_start = start_date

    full_history_df = databento_fetch_full_history(
        client=client,
        dataset=dataset,
        symbol=symbol,
        schema=schema,
        existing_history_df=existing_history_df,
        current_start=current_start,
        verbose=verbose,
    )

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/{schema}"
    os.makedirs(directory, exist_ok=True)

    if excel_export:
        print(f"Exporting {symbol} {schema} data to Excel...")
        full_history_df.to_excel(f"{directory}/{symbol}.xlsx", sheet_name="data")

    if pickle_export:
        print(f"Exporting {symbol} {schema} data to Pickle...")
        full_history_df.to_pickle(f"{directory}/{symbol}.pkl")

    if parquet_export:
        print(f"Exporting {symbol} {schema} data to Parquet...")
        full_history_df.to_parquet(f"{directory}/{symbol}.parquet")

    total_rows = len(full_history_df)

    if output_confirmation:
        print(f"The first and last date of {schema} data for {symbol} is: ")
        display(full_history_df[:1])
        display(full_history_df[-1:])
        print(f"Number of rows after data update: {total_rows}")

        if starting_rows:
            print(f"Number of rows added during update: {total_rows - starting_rows}")

        print(f"DataBento data complete for {symbol} {schema} data.")
        print(f"--------------------")

    return full_history_df


if __name__ == "__main__":

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    equities = ["AMZN", "AAPL"]

    for stock in equities:
        databento_pull_data(
            base_directory=DATA_DIR,
            symbol=stock,
            dataset="XNAS.ITCH",
            source="DataBento",
            asset_class="Equities",
            start_date=datetime(current_year - 2, current_month, current_day),
            schema="ohlcv-1m",
            force_existing_check=False,
            verbose=False,
            excel_export=True,
            pickle_export=True,
            parquet_export=True,
            output_confirmation=True,
        )

        databento_pull_data(
            base_directory=DATA_DIR,
            symbol=stock,
            dataset="XNAS.ITCH",
            source="DataBento",
            asset_class="Equities",
            start_date=datetime(current_year - 2, current_month, current_day),
            schema="ohlcv-1h",
            force_existing_check=False,
            verbose=False,
            excel_export=True,
            pickle_export=True,
            parquet_export=True,
            output_confirmation=True,
        )

        databento_pull_data(
            base_directory=DATA_DIR,
            symbol=stock,
            dataset="XNAS.ITCH",
            source="DataBento",
            asset_class="Equities",
            start_date=datetime(current_year - 2, current_month, current_day),
            schema="ohlcv-1d",
            force_existing_check=False,
            verbose=False,
            excel_export=True,
            pickle_export=True,
            parquet_export=True,
            output_confirmation=True,
        )
