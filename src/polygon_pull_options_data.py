import os
import re
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

# OCC option symbol, e.g. O:SPY251219C00500000
#   underlying (1-6 chars), expiration (YYMMDD), type (C/P), strike x 1000 (8 digits)
OCC_PATTERN = re.compile(
    r"^O:(?P<underlying>[A-Z0-9.]{1,6})(?P<expiration>\d{6})(?P<contract_type>[CP])(?P<strike>\d{8})$"
)


def parse_option_ticker(
    ticker: str,
) -> dict:
    """
    Parse an OCC-format option ticker into its components.

    Parameters:
    -----------
    ticker : str
        Option ticker in Polygon (Massive) format, e.g. "O:SPY251219C00500000".

    Returns:
    --------
    dict
        Dictionary with the keys underlying_ticker (str), expiration_date (datetime),
        contract_type ("call" or "put"), strike_price (float), and file_ticker
        (the ticker without the "O:" prefix, safe for use in file names).
    """

    match = OCC_PATTERN.match(ticker)
    if match is None:
        raise Exception(
            f"Invalid option ticker: {ticker}. Expected OCC format such as O:SPY251219C00500000."
        )

    return {
        "underlying_ticker": match["underlying"],
        "expiration_date": datetime.strptime(match["expiration"], "%y%m%d"),
        "contract_type": "call" if match["contract_type"] == "C" else "put",
        "strike_price": int(match["strike"]) / 1000,
        "file_ticker": ticker.removeprefix("O:"),
    }


def polygon_fetch_options_contracts(
    client,
    underlying_ticker: str,
    contract_type: str | None,
    expiration_date_gte: datetime | None,
    expiration_date_lte: datetime | None,
    strike_price_gte: float | None,
    strike_price_lte: float | None,
    expired: bool,
    as_of: datetime | None,
    free_tier: bool,
    verbose: bool,
) -> pd.DataFrame:
    """
    Fetch the list of option contracts for an underlying ticker from the Polygon
    (Massive) options contracts reference endpoint.

    Parameters:
    -----------
    client
        Polygon API client instance.
    underlying_ticker : str
        Underlying ticker symbol (e.g., "SPY").
    contract_type : str | None
        "call", "put", or None for both.
    expiration_date_gte : datetime | None
        Only return contracts expiring on or after this date.
    expiration_date_lte : datetime | None
        Only return contracts expiring on or before this date.
    strike_price_gte : float | None
        Only return contracts with a strike price greater than or equal to this value.
    strike_price_lte : float | None
        Only return contracts with a strike price less than or equal to this value.
    expired : bool
        If True, return expired contracts; if False, return active contracts. The
        endpoint returns one or the other, not both.
    as_of : datetime | None
        Return contracts as they existed on this date. None uses today.
    free_tier : bool
        If True, then pause to avoid API limits.
    verbose : bool
        If True, print detailed information about the data being processed.

    Returns:
    --------
    contracts_df : pd.DataFrame
        DataFrame with one row per contract, sorted by expiration date, contract
        type, and strike price.
    """

    columns = [
        "ticker",
        "underlying_ticker",
        "contract_type",
        "exercise_style",
        "expiration_date",
        "strike_price",
        "shares_per_contract",
        "primary_exchange",
        "cfi",
    ]

    def fmt(d):
        return d.strftime("%Y-%m-%d") if d is not None else None

    # Check for free tier and if so then pause for 12 seconds to avoid hitting API rate limits
    if free_tier == True:
        if verbose == True:
            print(f"Sleeping for 12 seconds to avoid hitting API rate limits...\n")
        time.sleep(12)

    print(f"Pulling option contracts for {underlying_ticker}...")

    contracts = client.list_options_contracts(
        underlying_ticker=underlying_ticker,
        contract_type=contract_type,
        expiration_date_gte=fmt(expiration_date_gte),
        expiration_date_lte=fmt(expiration_date_lte),
        strike_price_gte=strike_price_gte,
        strike_price_lte=strike_price_lte,
        expired=expired,
        as_of=fmt(as_of),
        sort="expiration_date",
        order="asc",
        limit=1000,
    )

    contracts_df = pd.DataFrame(
        [{col: getattr(c, col) for col in columns} for c in contracts],
        columns=columns,
    )

    contracts_df["expiration_date"] = pd.to_datetime(contracts_df["expiration_date"])
    contracts_df["strike_price"] = contracts_df["strike_price"].astype("float64")
    contracts_df = contracts_df.drop_duplicates(subset="ticker", keep="last")
    contracts_df = contracts_df.sort_values(
        by=["expiration_date", "contract_type", "strike_price"], ascending=True
    )
    contracts_df = contracts_df.reset_index(drop=True)

    if verbose == True:
        print("Contract data:")
        print(contracts_df)

    print(f"Number of contracts found for {underlying_ticker}: {len(contracts_df)}")

    return contracts_df


def polygon_fetch_options_full_history(
    client,
    ticker: str,
    timespan: str,
    multiplier: int,
    existing_history_df: pd.DataFrame,
    current_start: datetime,
    end_date: datetime,
    free_tier: bool,
    verbose: bool,
) -> pd.DataFrame:
    """
    Fetch full historical aggregate data for an option contract from Polygon API.

    Differs from the equity version in two ways, because option contracts trade
    sparsely and have a finite life:
    - The pull stops at end_date (the day after expiration, or now if still active).
    - The start and end of each window move independently. The end moves forward
      by time_delta on every pass, and the start follows the last bar pulled minus
      time_overlap. Each window therefore contains the last pulled bar, even across
      a trading gap, so the overlap check always has a row to compare against.

    Parameters:
    -----------
    client
        Polygon API client instance.
    ticker : str
        Option ticker to download (e.g., "O:SPY251219C00500000").
    timespan : str
        Time span for the data ("minute", "hour", "day").
    multiplier : int
        Multiplier for the time span (e.g., 1 for daily data).
    existing_history_df : pd.DataFrame
        DataFrame containing the existing historical data.
    current_start : datetime
        Date for which to start pulling data in datetime format.
    end_date : datetime
        Date at which to stop pulling data in datetime format.
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

    price_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "vwap",
        "transactions",
    ]

    # Set current_end to the start of the window
    current_end = current_start

    while current_start < end_date:

        # Move the end of the window forward by time_delta, capped at end_date
        current_end = min(current_end + timedelta(days=time_delta), end_date)

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

        # Break out of while loop once the window has reached end_date
        if current_end >= end_date:
            break

        # Check for free tier and if so then pause for 12 seconds to avoid hitting
        # API rate limits
        if free_tier == True:
            if verbose == True:
                print(f"Sleeping for 12 seconds to avoid hitting API rate limits...\n")
            time.sleep(12)

    # Return the DataFrame containing the full history
    return full_history_df


def polygon_pull_options_data(
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
    Read existing data file, download aggregate price data for a single option
    contract from Polygon, and export data.

    Files are stored under {base_directory}/{source}/{asset_class}/{underlying}/{timespan}/
    and named by the ticker without its "O:" prefix (e.g. SPY251219C00500000.pkl).

    The contract's expiration date is parsed from the OCC ticker, and the pull stops
    the day after expiration. An expired contract whose existing data already runs
    to expiration therefore takes a single request, which confirms the overlap.
    With free_tier=True the pull also stops at midnight today, since the free tier
    has no same-day data and only about two years of history.

    Option aggregates are not dividend-adjusted, so no adj_* columns are created.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    ticker : str
        Option ticker to download, in OCC format (e.g., "O:SPY251219C00500000").
    source : str
        Name of the data source (e.g., 'Polygon').
    asset_class : str
        Asset class name (e.g., 'Options').
    start_date : datetime
        Start date for the data in datetime format.
    timespan : str
        Time span for the data ("minute", "hour", "day").
    multiplier : int
        Multiplier for the time span (e.g., 1 for daily data).
    force_existing_check : bool
        If True, re-pull from start_date to verify that there are not any gaps in the data.
    free_tier : bool
        If True, then pause to avoid API limits and stop the pull at midnight today.
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

    # Parse contract details from the ticker
    contract = parse_option_ticker(ticker)
    underlying = contract["underlying_ticker"]
    file_ticker = contract["file_ticker"]

    # Stop pulling the day after expiration, or now if the contract is still active.
    # The free tier only serves end-of-day data through the prior day, so a request
    # covering only today is rejected as NOT_AUTHORIZED; stop at midnight instead.
    if free_tier == True:
        data_cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        data_cutoff = datetime.now()
    end_date = min(contract["expiration_date"] + timedelta(days=1), data_cutoff)

    # Set file location based on parameters
    directory = f"{base_directory}/{source}/{asset_class}/{underlying}/{timespan}"
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

    full_history_df = polygon_fetch_options_full_history(
        client=client,
        ticker=ticker,
        timespan=timespan,
        multiplier=multiplier,
        existing_history_df=existing_history_df,
        current_start=current_start,
        end_date=end_date,
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
        full_history_df.to_excel(f"{directory}/{file_ticker}.xlsx", sheet_name="data")

    # Export to Pickle
    if pickle_export == True:
        print(f"Exporting {ticker} {timespan} data to Pickle...")
        full_history_df.to_pickle(f"{directory}/{file_ticker}.pkl")

    # Export to Parquet
    if parquet_export == True:
        print(f"Exporting {ticker} {timespan} data to Parquet...")
        full_history_df.to_parquet(f"{directory}/{file_ticker}.parquet")

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
    GLOBAL_FREE_TIER = True

    # Underlying tickers
    underlyings = ["SPY"]

    # Timespans
    timespans = ["day"]

    client = RESTClient(api_key=POLYGON_KEY)

    # Iterate through each underlying ticker
    for underlying in underlyings:

        # Active contracts expiring within the next 3 years
        contracts_df = polygon_fetch_options_contracts(
            client=client,
            underlying_ticker=underlying,
            contract_type=None,
            expiration_date_gte=datetime.now(),
            expiration_date_lte=datetime.now() + timedelta(days=1095),
            strike_price_gte=None,
            strike_price_lte=None,
            expired=False,
            as_of=None,
            free_tier=GLOBAL_FREE_TIER,
            verbose=False,
        )

        # Export contract list for that underlying ticker
        contracts_directory = f"{DATA_DIR}/Polygon/Options/{underlying}"
        os.makedirs(contracts_directory, exist_ok=True)
        contracts_df.to_pickle(f"{contracts_directory}/{underlying}_contracts.pkl")
        contracts_df.to_excel(
            f"{contracts_directory}/{underlying}_contracts.xlsx", sheet_name="data"
        )

        # Iterate through the list of contracts
        for option_ticker in contracts_df["ticker"].head(5):
            for timespan in timespans:
                polygon_pull_options_data(
                    base_directory=DATA_DIR,
                    ticker=option_ticker,
                    source="Polygon",
                    asset_class="Options",
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
