import os
import pandas as pd
import time

from datetime import datetime, timedelta, timezone
from IPython.display import display
from massive import RESTClient
from settings import config

# Load API key from the environment variables
POLYGON_KEY = config("POLYGON_KEY")

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")


def polygon_fetch_futures_full_history(
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
    Fetch full historical data for a given futures contract from the Polygon
    (Massive) futures aggregates endpoint.

    Futures aggregates carry a session end date and, on daily bars, a settlement
    price. Contracts are not split- or dividend-adjusted.

    Daily bars are dated by session_end_date, the trading day the session belongs
    to. The API's window_start for a daily bar is the prior calendar day (a Sunday
    for a Monday session). Hourly and minute bars are dated by window_start.

    Parameters:
    -----------
    client
        Polygon API client instance.
    ticker : str
        Futures contract ticker to download (e.g., "ESZ6").
    timespan : str
        Time span for the data (e.g., "minute", "hour", "day").
    multiplier : int
        Multiplier for the time span (e.g., 1 for daily data).
    existing_history_df : pd.DataFrame
        DataFrame containing the existing historical data.
    current_start : datetime
        Date for which to start pulling data in datetime format, as naive UTC.
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

    # Set resolution based on the multiplier
    window_resolution = {
        "minute": f"{multiplier}min",
        "hour": f"{multiplier}hour",
        "day": f"{multiplier}day",
    }
    if timespan not in window_resolution:
        raise Exception(f"Invalid {timespan}.")
    resolution = window_resolution[timespan]

    # Set the number of overlapping days to check for revisions in the data
    time_overlap = 1

    # List of columns to check for overlapping data
    price_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "dollar_volume",
        "transactions",
        "settlement_price",
        "session_end_date",
    ]

    # Set current_end to the start of the window
    current_end = current_start

    # Bars are stored as naive UTC, so compare against the current UTC time
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    while current_start < now:

        # Move the end of the window forward by time_delta
        current_end = current_end + timedelta(days=time_delta)

        if verbose == True:
            print(
                f"Pulling {timespan} data for {current_start} thru {current_end} for {ticker}...\n"
            )

        try:
            # Pull new data, with the window bounds as UTC nanoseconds
            aggs = list(
                client.list_futures_aggregates(
                    ticker=ticker,
                    resolution=resolution,
                    window_start_gte=pd.Timestamp(current_start, tz="UTC").value,
                    window_start_lte=pd.Timestamp(current_end, tz="UTC").value,
                    sort="window_start.asc",
                    limit=5000,
                )
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
                new_data["session_end_date"] = pd.to_datetime(
                    new_data["session_end_date"]
                )

                if timespan == "day":
                    new_data["Date"] = new_data["session_end_date"]
                else:
                    new_data["Date"] = pd.to_datetime(
                        new_data["window_start"], unit="ns"
                    )

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
                # and reset index
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

        # Exception handling for failed data pull
        except Exception as e:
            print(
                f"Failed to pull {timespan} data for {current_start} thru {current_end} for {ticker}: {e}"
            )
            raise  # Re-raise the original exception

        # Break out of while loop if current_end is beyond the present date
        if current_end >= now:
            break
        else:
            current_end = current_start

        # Check for free tier and if so then pause for 12 seconds to avoid hitting
        # API rate limits
        if free_tier == True:
            if verbose == True:
                print(f"Sleeping for 12 seconds to avoid hitting API rate limits...\n")
            time.sleep(12)

    # Return the DataFrame containing the full history
    return full_history_df


def polygon_pull_futures_data(
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
    Read existing data file, download futures contract price data from Polygon
    (Massive), and export data.

    Each ticker is a single dated contract (e.g., "ESZ6"), so no continuous series
    is built and no roll adjustment is applied.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    ticker : str
        Futures contract ticker to download (e.g., "ESZ6").
    source : str
        Name of the data source (e.g., 'Polygon').
    asset_class : str
        Asset class name (e.g., 'Futures').
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
        DataFrame containing the updated price data.
    """

    # Open client connection
    client = RESTClient(api_key=POLYGON_KEY)

    # Set file location based on parameters
    directory = f"{base_directory}/{source}/{asset_class}/{timespan}"
    file_location = f"{directory}/{ticker}.pkl"

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

        print(f"File found...updating the {ticker} {timespan} data.")

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
        print(f"File not found...downloading the {ticker} {timespan} data.")

        # Create an empty DataFrame
        existing_history_df = pd.DataFrame(
            {
                "Date": pd.Series(dtype="datetime64[ns]"),
                "open": pd.Series(dtype="float64"),
                "high": pd.Series(dtype="float64"),
                "low": pd.Series(dtype="float64"),
                "close": pd.Series(dtype="float64"),
                "volume": pd.Series(dtype="float64"),
                "dollar_volume": pd.Series(dtype="float64"),
                "transactions": pd.Series(dtype="int64"),
                "settlement_price": pd.Series(dtype="float64"),
                "session_end_date": pd.Series(dtype="datetime64[ns]"),
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

    full_history_df = polygon_fetch_futures_full_history(
        client=client,
        ticker=ticker,
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
        print(f"Exporting {ticker} {timespan} data to Excel...")
        full_history_df.to_excel(f"{directory}/{ticker}.xlsx", sheet_name="data")

    # Export to Pickle
    if pickle_export == True:
        print(f"Exporting {ticker} {timespan} data to Pickle...")
        full_history_df.to_pickle(f"{directory}/{ticker}.pkl")

    # Export to Parquet
    if parquet_export == True:
        print(f"Exporting {ticker} {timespan} data to Parquet...")
        full_history_df.to_parquet(f"{directory}/{ticker}.parquet")

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

    # Set global variables. The futures endpoints returned 429 errors when called
    # without a pause, so pace requests at 12 seconds apart.
    GLOBAL_FREE_TIER = True

    # Futures contracts
    contracts = ["ESZ6"]

    # Timespans
    timespans = ["day", "hour", "minute"]

    # Iterate through each contract
    for contract in contracts:
        for timespan in timespans:
            polygon_pull_futures_data(
                base_directory=DATA_DIR,
                ticker=contract,
                source="Polygon",
                asset_class="Futures",
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
