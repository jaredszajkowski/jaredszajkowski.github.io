import os
import pandas as pd
import time

from datetime import datetime, timedelta
from IPython.display import display
from massive import RESTClient
from settings import config

# Load API key from the environment variables
POLYGON_KEY = config("POLYGON_KEY")

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")


def normalize_index_ticker(ticker: str) -> dict:
    """
    Normalize an index ticker to the Polygon (Massive) "I:" format.

    Parameters:
    -----------
    ticker : str
        Index ticker, with or without the "I:" prefix (e.g., "I:SPX" or "SPX").

    Returns:
    --------
    dict
        Dictionary with the keys api_ticker (the ticker with the "I:" prefix, as
        required by the API) and file_ticker (the ticker without the prefix, safe
        for use in file names).
    """

    file_ticker = ticker.upper().removeprefix("I:")
    if not file_ticker:
        raise Exception(f"Invalid index ticker: {ticker}.")

    return {
        "api_ticker": f"I:{file_ticker}",
        "file_ticker": file_ticker,
    }


def polygon_fetch_index_full_history(
    client,
    ticker: str,
    timespan: str,
    multiplier: int,
    existing_history_df: pd.DataFrame,
    current_start: datetime,
    free_tier: bool,
    verbose: bool,
) -> pd.DataFrame:
    """
    Fetch full historical data for a given index from the Polygon (Massive) API.

    Index aggregates only carry open, high, low, and close values; there is no
    volume, VWAP, or transaction count, and indices are not split- or
    dividend-adjusted.

    Parameters:
    -----------
    client
        Polygon API client instance.
    ticker : str
        Index ticker to download, with the "I:" prefix (e.g., "I:SPX").
    timespan : str
        Time span for the data (e.g., "minute", "hour", "day").
    multiplier : int
        Multiplier for the time span (e.g., 1 for daily data).
    existing_history_df : pd.DataFrame
        DataFrame containing the existing historical data.
    current_start : datetime
        Date for which to start pulling data in datetime format.
    free_tier : bool
        If True, then pause to avoid API limits.
    verbose : bool
        If True, print detailed information about the data being processed.

    Returns:
    --------
    full_history_df : pd.DataFrame
        DataFrame containing the data.
    """

    # Copy DataFrame
    full_history_df = existing_history_df.copy()

    # Set time_delta based on the timespan
    window_days = {"minute": 15, "hour": 15, "day": 180}
    if timespan not in window_days:
        raise Exception(f"Invalid {timespan}.")
    time_delta = window_days[timespan]

    # Set the number of overlapping days to check for revisions in the data
    time_overlap = 1

    # List of columns to check for overlapping data
    price_cols = [
        "open",
        "high",
        "low",
        "close",
    ]

    # Set current_end to the start of the window
    current_end = current_start

    while current_start < datetime.now():

        # Move the end of the window forward by time_delta
        current_end = current_end + timedelta(days=time_delta)

        if verbose == True:
            print(
                f"Pulling {timespan} data for {current_start} thru {current_end} for {ticker}...\n"
            )

        try:
            # Pull new data
            aggs = client.get_aggs(
                ticker=ticker,
                timespan=timespan,
                multiplier=multiplier,
                from_=current_start,
                to=current_end,
                sort="asc",
                limit=5000,
            )

            # If no new data is returned, print a message indicating no data was found
            # Always prints regardless of the verbose setting
            if len(aggs) == 0:
                print(
                    f"No data for {ticker} from {current_start} thru {current_end}.\n"
                )

            else:
                # Convert to DataFrame
                new_data = pd.DataFrame([bar.__dict__ for bar in aggs])
                new_data["timestamp"] = pd.to_datetime(new_data["timestamp"], unit="ms")
                new_data = new_data.rename(columns={"timestamp": "Date"})
                new_data = new_data[["Date"] + price_cols]
                new_data = new_data.sort_values(by="Date", ascending=True)

                # Enforce dtypes to match full_history_df
                new_data = new_data.astype(full_history_df.dtypes.to_dict())

                if verbose == True:
                    print("New data:")
                    print(new_data)

                # If full_history_df is not empty, confirm that the new data overlaps
                # the existing data on price, as a check against revisions or gaps
                if not full_history_df.empty:
                    overlap = full_history_df.merge(
                        new_data, on=["Date"] + price_cols, how="inner"
                    )

                    if overlap.empty:
                        raise Exception(
                            f"New data does not overlap with existing data (price data check)."
                        )

                # Combine existing data with recent data, drop duplicates, sort values,
                # reset index
                full_history_df = pd.concat([full_history_df, new_data])
                full_history_df = full_history_df.drop_duplicates(
                    subset="Date", keep="last"
                )
                full_history_df = full_history_df.sort_values(by="Date", ascending=True)
                full_history_df = full_history_df.reset_index(drop=True)

                if verbose == True:
                    print("Combined data:")
                    print(full_history_df)

                # Start the next window before the last bar pulled, so that the bar
                # is included in the next overlap check
                current_start = new_data["Date"].max() - timedelta(days=time_overlap)
                current_end = current_start

        # Exception handling for failed data pull
        except Exception as e:
            print(
                f"Failed to pull {timespan} data for {current_start} thru {current_end} for {ticker}: {e}"
            )
            raise  # Re-raise the original exception

        # Break out of while loop if current_end is beyond the present date
        if current_end > datetime.now():
            break

        # Check for free tier and if so then pause for 12 seconds to avoid hitting
        # API rate limits
        if free_tier == True:
            if verbose == True:
                print(f"Sleeping for 12 seconds to avoid hitting API rate limits...\n")
            time.sleep(12)

    # Return the DataFrame containing the full history
    return full_history_df


def polygon_pull_index_data(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    start_date: datetime,
    timespan: str,
    multiplier: int,
    force_existing_check: bool,
    free_tier: bool,
    verbose: bool,
    excel_export: bool,
    pickle_export: bool,
    parquet_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    """
    Read existing data file, download index level data from Polygon, and export data.

    Files are named by the ticker without its "I:" prefix (e.g. SPX.pkl).

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    ticker : str
        Index ticker to download, with or without the "I:" prefix (e.g., "I:SPX").
    source : str
        Name of the data source (e.g., 'Polygon').
    asset_class : str
        Asset class name (e.g., 'Indices').
    start_date : datetime
        Start date for the data in datetime format.
    timespan : str
        Time span for the data (e.g., "minute", "hour", "day").
    multiplier : int
        Multiplier for the time span (e.g., 1 for daily data).
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
    parquet_export : bool
        If True, export data to Parquet format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    pd.DataFrame
        DataFrame containing the updated index data.
    """

    # Open client connection
    client = RESTClient(api_key=POLYGON_KEY)

    # Normalize the ticker for the API and for file names
    tickers = normalize_index_ticker(ticker)
    api_ticker = tickers["api_ticker"]
    file_ticker = tickers["file_ticker"]

    # Set file location based on parameters
    directory = f"{base_directory}/{source}/{asset_class}/{timespan}"
    file_location = f"{directory}/{file_ticker}.pkl"

    # Create list of acceptable timespans
    acceptable_timespans = ["minute", "hour", "day"]
    if timespan not in acceptable_timespans:
        raise Exception(
            f"Invalid timespan: {timespan}. Acceptable timespans are: {acceptable_timespans}."
        )

    try:
        # Attempt to read existing pickle data file
        existing_history_df = pd.read_pickle(file_location)

        # Reset index if 'Date' is column is the index
        if "Date" not in existing_history_df.columns:
            existing_history_df = existing_history_df.reset_index()

        print(f"File found...updating the {api_ticker} {timespan} data.")

        if verbose == True:
            print("Existing data:")
            print(existing_history_df)

        # Find last date in existing data
        last_data_date = existing_history_df["Date"].max()
        print(f"Last date in existing data: {last_data_date}")

        # Find the number of starting rows
        starting_rows = len(existing_history_df)
        print(f"Number of rows in existing data: {starting_rows}")

        # Overlap with existing data by enough to span a weekend, so that a session
        # still in progress at the last update is not the only bar being compared
        current_start = last_data_date - timedelta(days=7)

    except FileNotFoundError:
        # Print error
        print(f"File not found...downloading the {api_ticker} {timespan} data.")

        # Create an empty DataFrame
        existing_history_df = pd.DataFrame(
            {
                "Date": pd.Series(dtype="datetime64[ns]"),
                "open": pd.Series(dtype="float64"),
                "high": pd.Series(dtype="float64"),
                "low": pd.Series(dtype="float64"),
                "close": pd.Series(dtype="float64"),
            }
        )

        # Set the number of starting rows to be 0
        starting_rows = 0

        # Set current date to start date
        current_start = start_date

    # Check for force_existing_check flag
    if force_existing_check == True:
        print("Forcing check of existing data...")
        current_start = start_date

    full_history_df = polygon_fetch_index_full_history(
        client=client,
        ticker=api_ticker,
        timespan=timespan,
        multiplier=multiplier,
        existing_history_df=existing_history_df,
        current_start=current_start,
        free_tier=free_tier,
        verbose=verbose,
    )

    # Do not export an empty file, since later runs would read it as existing data
    # and have no last date from which to resume
    if full_history_df.empty:
        print(f"No {timespan} data found for {ticker}, so nothing was exported.")
        return full_history_df

    # Create directory
    os.makedirs(directory, exist_ok=True)

    # Export to Excel
    if excel_export == True:
        print(f"Exporting {api_ticker} {timespan} data to Excel...")
        full_history_df.to_excel(f"{directory}/{file_ticker}.xlsx", sheet_name="data")

    # Export to Pickle
    if pickle_export == True:
        print(f"Exporting {api_ticker} {timespan} data to Pickle...")
        full_history_df.to_pickle(f"{directory}/{file_ticker}.pkl")

    # Export to Parquet
    if parquet_export == True:
        print(f"Exporting {api_ticker} {timespan} data to Parquet...")
        full_history_df.to_parquet(f"{directory}/{file_ticker}.parquet")

    total_rows = len(full_history_df)

    # Output confirmation
    if output_confirmation == True:
        print(f"The first and last date of {timespan} data for {api_ticker} is: ")
        display(full_history_df[:1])
        display(full_history_df[-1:])
        print(f"Number of rows after data update: {total_rows}")

        if starting_rows:
            print(f"Number of rows added during update: {total_rows - starting_rows}")

        print(f"Polygon data complete for {api_ticker} {timespan} data.")
        print(f"--------------------")

    return full_history_df


def polygon_resample_index_period_end(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    timespan: str,
    period: str,
    excel_export: bool,
    pickle_export: bool,
    parquet_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    """
    Read index data from an existing pickle file and export month-end or
    quarter-end close values.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    ticker : str
        Index ticker to resample, with or without the "I:" prefix (e.g., "I:SPX").
    source : str
        Name of the data source (e.g., 'Polygon').
    asset_class : str
        Asset class name (e.g., 'Indices').
    timespan : str
        Time span of the existing data to read (e.g., "day").
    period : str
        Period to resample to, either "month" (month-end) or "quarter" (quarter-end).
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
    df_period_end : pd.DataFrame
        DataFrame indexed by period-end date containing the close column.
    """

    # Resample frequency, output directory, and file suffix for each period
    period_settings = {
        "month": {"freq": "ME", "directory": "Month_End", "suffix": "ME"},
        "quarter": {"freq": "QE", "directory": "Quarter_End", "suffix": "QE"},
    }
    if period not in period_settings:
        raise Exception(
            f"Invalid period: {period}. Acceptable periods are: {list(period_settings)}."
        )
    settings = period_settings[period]

    file_ticker = normalize_index_ticker(ticker)["file_ticker"]

    # Set location from where to read existing pickle file
    location = f"{base_directory}/{source}/{asset_class}/{timespan}/{file_ticker}.pkl"

    # Read data from pickle
    df = pd.read_pickle(location)

    # Reset index if 'Date' is column is the index
    if "Date" not in df.columns:
        df = df.reset_index()

    # Keep only required columns and set index to date column
    df = df[["Date", "close"]].set_index("Date")

    # Resample data to period end
    df_period_end = df.resample(settings["freq"]).last()

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/{settings['directory']}"
    os.makedirs(directory, exist_ok=True)

    file_stem = f"{directory}/{file_ticker}_{settings['suffix']}"

    # Export to Excel
    if excel_export == True:
        df_period_end.to_excel(f"{file_stem}.xlsx", sheet_name="data")

    # Export to Pickle
    if pickle_export == True:
        df_period_end.to_pickle(f"{file_stem}.pkl")

    # Export to Parquet
    if parquet_export == True:
        df_period_end.to_parquet(f"{file_stem}.parquet")

    # Output confirmation
    if output_confirmation == True:
        print(f"{period.capitalize()} end data complete for {file_ticker}")
        print(f"--------------------")

    return df_period_end


if __name__ == "__main__":

    # Set global variables
    GLOBAL_FREE_TIER = False

    # Index Data
    indices = ["I:SPX"]

    # Timespans
    timespans = ["day", "hour", "minute"]

    # Iterate through each index
    for index in indices:
        for timespan in timespans:
            polygon_pull_index_data(
                base_directory=DATA_DIR,
                ticker=index,
                source="Polygon",
                asset_class="Indices",
                start_date=datetime.now() - timedelta(days=2 * 365),
                timespan=timespan,
                multiplier=1,
                force_existing_check=False,
                free_tier=GLOBAL_FREE_TIER,
                verbose=True,
                excel_export=True,
                pickle_export=True,
                parquet_export=True,
                output_confirmation=True,
            )

            if GLOBAL_FREE_TIER == True:
                time.sleep(12)
