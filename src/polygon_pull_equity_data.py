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


def polygon_fetch_full_history(
    client,
    ticker: str,
    timespan: str,
    multiplier: int,
    adjusted: bool,
    existing_history_df: pd.DataFrame,
    current_start: datetime,
    free_tier: bool,
    verbose: bool,
) -> pd.DataFrame:
    """
    Fetch full historical data for a given equity or ETF product from Polygon API.

    Parameters:
    -----------
    client
        Polygon API client instance.
    ticker : str
        Ticker symbol to download.
    timespan : str
        Time span for the data (e.g., "minute", "hour", "day", "week", "month", "quarter", "year").
    multiplier : int
        Multiplier for the time span (e.g., 1 for daily data).
    adjusted : bool
        If True, return adjusted data; if False, return raw data.
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
        "volume",
        "vwap",
        "transactions",
        "otc",
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
                adjusted=adjusted,
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

                # Combine existing data with new data, drop duplicates, sort values,
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
        if current_end >= datetime.now():
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


def polygon_fetch_dividend_factors(
    client,
    ticker: str,
    free_tier: bool,
    verbose: bool,
) -> pd.DataFrame:
    """
    Fetch the dividend history and cumulative dividend adjustment factors for a
    given ticker from the Polygon (Massive) dividends endpoint.

    Parameters:
    -----------
    client
        Polygon API client instance.
    ticker : str
        Ticker symbol to download.
    free_tier : bool
        If True, then pause to avoid API limits.
    verbose : bool
        If True, print detailed information about the data being processed.

    Returns:
    --------
    dividends_df : pd.DataFrame
        DataFrame with one row per ex-dividend date, sorted ascending, containing
        the columns ex_dividend_date, cash_amount, split_adjusted_cash_amount,
        distribution_type, and historical_adjustment_factor. Empty if the ticker
        has no dividend history.
    """

    columns = [
        "ex_dividend_date",
        "cash_amount",
        "split_adjusted_cash_amount",
        "distribution_type",
        "historical_adjustment_factor",
    ]

    # Check for free tier and if so then pause for 12 seconds to avoid hitting
    # API rate limits
    if free_tier == True:
        if verbose == True:
            print(f"Sleeping for 12 seconds to avoid hitting API rate limits...\n")
        time.sleep(12)

    print(f"Pulling dividend adjustment factors for {ticker}...")

    dividends = client.list_stocks_dividends(
        ticker=ticker,
        sort="ex_dividend_date.asc",
        limit=5000,
    )

    dividends_df = pd.DataFrame(
        [{col: getattr(div, col) for col in columns} for div in dividends],
        columns=columns,
    )

    # Drop records without an adjustment factor, then sort and de-duplicate by ex-date
    dividends_df = dividends_df.dropna(subset=["historical_adjustment_factor"])
    dividends_df["ex_dividend_date"] = pd.to_datetime(dividends_df["ex_dividend_date"])
    dividends_df["historical_adjustment_factor"] = dividends_df[
        "historical_adjustment_factor"
    ].astype("float64")
    dividends_df = dividends_df.sort_values(by="ex_dividend_date", ascending=True)
    dividends_df = dividends_df.drop_duplicates(subset="ex_dividend_date", keep="last")
    dividends_df = dividends_df.reset_index(drop=True)

    if verbose == True:
        print("Dividend data:")
        print(dividends_df)

    print(f"Number of dividends found for {ticker}: {len(dividends_df)}")

    return dividends_df


def apply_dividend_adjustment(
    df: pd.DataFrame,
    dividends_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply cumulative dividend adjustment factors to split-adjusted price data to
    create the adj_open, adj_high, adj_low, adj_close, and adj_vwap columns.
    Volume is left unadjusted, since a cash dividend does not change the share count.

    For a bar on trading date D, the factor used is the historical_adjustment_factor
    of the first dividend whose ex-dividend date falls after D. Bars on or after the
    most recent ex-dividend date receive a factor of 1.0.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing split-adjusted price data, with a "Date" column of
        naive UTC timestamps and open, high, low, close columns.
    dividends_df : pd.DataFrame
        DataFrame returned by polygon_fetch_dividend_factors.

    Returns:
    --------
    adjusted_df : pd.DataFrame
        Copy of df with the adj_open, adj_high, adj_low, adj_close, and adj_vwap columns added.
    """

    price_cols = ["open", "high", "low", "close", "vwap"]

    # Drop any existing adjusted columns so they can be recomputed from scratch
    adjusted_df = df.drop(
        columns=[f"adj_{col}" for col in price_cols], errors="ignore"
    ).copy()

    # Trading date in US/Eastern so extended-hours intraday bars land on the right session
    trade_date = (
        adjusted_df["Date"]
        .dt.tz_localize("UTC")
        .dt.tz_convert("America/New_York")
        .dt.tz_localize(None)
        .dt.normalize()
        .astype("datetime64[ns]")
    )

    if dividends_df.empty:
        factor = pd.Series(1.0, index=adjusted_df.index)
    else:
        left = pd.DataFrame(
            {"trade_date": trade_date, "row_order": range(len(adjusted_df))}
        ).sort_values(by="trade_date", kind="stable")

        right = dividends_df[["ex_dividend_date", "historical_adjustment_factor"]]
        right = right.assign(
            ex_dividend_date=right["ex_dividend_date"].astype("datetime64[ns]")
        )

        # First ex-dividend date strictly after each bar's trading date
        merged = pd.merge_asof(
            left,
            right,
            left_on="trade_date",
            right_on="ex_dividend_date",
            direction="forward",
            allow_exact_matches=False,
        )

        merged = merged.sort_values(by="row_order")
        factor = pd.Series(
            merged["historical_adjustment_factor"].fillna(1.0).to_numpy(),
            index=adjusted_df.index,
        )

    for col in price_cols:
        adjusted_df[f"adj_{col}"] = adjusted_df[col] * factor

    return adjusted_df


def polygon_pull_equity_data(
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
    parquet_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    """
    Read existing data file, download price data from Polygon, apply dividend
    adjustment factors, and export data.

    When adjusted is True, the split-adjusted open, high, low, and close are also
    multiplied by Polygon's cumulative dividend adjustment factors to create the
    adj_open, adj_high, adj_low, adj_close, and adj_vwap columns. These are recomputed over
    the full history on every run, since each new dividend changes all prior factors.

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
        If True, return split-adjusted data with dividend-adjusted adj_* columns;
        if False, return raw data without adj_* columns.
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

        # Drop dividend-adjusted columns; they are recomputed after the update
        existing_history_df = existing_history_df.drop(
            columns=["adj_open", "adj_high", "adj_low", "adj_close", "adj_vwap"],
            errors="ignore",
        )

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
                "vwap": pd.Series(dtype="float64"),
                "transactions": pd.Series(dtype="int64"),
                "otc": pd.Series(dtype="object"),
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

    # Do not export an empty file, since later runs would read it as existing data
    # and have no last date from which to resume
    if full_history_df.empty:
        print(f"No {timespan} data found for {ticker}, so nothing was exported.")
        return full_history_df

    # Apply dividend adjustment factors to the split-adjusted prices
    if adjusted == True:
        dividends_df = polygon_fetch_dividend_factors(
            client=client,
            ticker=ticker,
            free_tier=free_tier,
            verbose=verbose,
        )
        full_history_df = apply_dividend_adjustment(
            df=full_history_df,
            dividends_df=dividends_df,
        )
    else:
        print(
            f"adjusted=False: {ticker} prices are not split-adjusted, so dividend adjustment factors were not applied (no adj_* columns)."
        )

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

    # Set global variables
    GLOBAL_FREE_TIER = False

    # Stock Data
    equities = ["AAPL"]

    # Timespans
    timespans = ["day", "hour", "minute"]

    # Iterate through each stock
    for stock in equities:
        for timespan in timespans:
            polygon_pull_equity_data(
                base_directory=DATA_DIR,
                ticker=stock,
                source="Polygon",
                asset_class="Equities",
                start_date=datetime.now() - timedelta(days=5 * 365),
                timespan=timespan,
                multiplier=1,
                adjusted=True,
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
