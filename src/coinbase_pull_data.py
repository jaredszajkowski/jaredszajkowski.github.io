import os
import pandas as pd

from coinbase_fetch_available_products import coinbase_fetch_available_products
from coinbase_fetch_full_history import coinbase_fetch_full_history
from datetime import datetime, timedelta
from IPython.display import display
from settings import config

# Get the data directory from the configuration
DATA_DIR = config("DATA_DIR")

# Supported granularities, in seconds, mapped to the subdirectory the data is
# stored in
GRANULARITY_DIRECTORIES = {
    60: "Minute",
    3600: "Hourly",
    86400: "Daily",
}


def _find_first_available_date(
    product_id: str,
    start_date: datetime,
    end_date: datetime,
) -> datetime:
    """
    Locate the first date with data for a product using daily candles.

    Pulling at daily granularity covers 300 days per request, so scanning a
    range of years costs only a handful of requests. Scanning the same range at
    minute granularity, where each request covers 5 hours, would take thousands.

    Parameters:
    -----------
    product_id : str
        The trading pair (e.g., 'BTC-USD').
    start_date : datetime
        Earliest date to consider.
    end_date : datetime
        Latest date to consider.

    Returns:
    --------
    datetime
        Date of the first available candle, or None if the product has no data.
    """

    daily_history_df = coinbase_fetch_full_history(
        product_id, start_date, end_date, 86400
    )

    if daily_history_df.empty:
        return None

    return daily_history_df["time"].min()


def coinbase_pull_data(
    base_directory,
    product_id: str,
    source: str,
    asset_class: str,
    granularity: int = 3600,  # 60=minute, 3600=hourly, 86400=daily
    start_date: datetime = datetime(2010, 1, 1),
    end_date: datetime = None,  # defaults to 1 day ago due to lag in data availability
    force_existing_check: bool = False,
    excel_export: bool = False,
    pickle_export: bool = True,
    parquet_export: bool = False,
    output_confirmation: bool = True,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Read existing data file, download price data from Coinbase, and export data.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    product_id : str
        The trading pair to download (e.g., 'BTC-USD').
    source : str
        Name of the data source (e.g., 'Coinbase').
    asset_class : str
        Asset class name (e.g., 'Cryptocurrencies').
    granularity : int
        Time slice in seconds (60=minute, 3600=hourly, 86400=daily).
    start_date : datetime
        Earliest date to consider. Only used when no existing record is found;
        where a record exists it is resumed from its last stored candle.
    end_date : datetime, optional
        End date in UTC. Defaults to 1 day ago due to lag in data availability.
    force_existing_check : bool
        If True, re-pull from start_date rather than resuming, to fill any gaps
        in an existing data file.
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    parquet_export : bool
        If True, export data to Parquet format.
    output_confirmation : bool
        If True, print confirmation message.
    verbose : bool
        If True, print detailed information about the data being processed.

    Returns:
    --------
    pd.DataFrame
        DataFrame containing the updated price data, indexed by Date.
    """

    # Resolved here rather than in the signature so that the default tracks the
    # current date instead of the moment this module was imported
    if end_date is None:
        end_date = datetime.now() - timedelta(days=1)

    if granularity not in GRANULARITY_DIRECTORIES:
        raise ValueError(
            f"Invalid granularity: {granularity}. Acceptable values are: {sorted(GRANULARITY_DIRECTORIES)}."
        )

    time_length = GRANULARITY_DIRECTORIES[granularity]

    # Set file location based on parameters
    directory = f"{base_directory}/{source}/{asset_class}/{time_length}"
    file_location = f"{directory}/{product_id}.pkl"

    try:
        # Attempt to read existing pickle data file
        existing_history_df = pd.read_pickle(file_location)

        # Reset index if 'Date' is the index
        if "Date" not in existing_history_df.columns:
            existing_history_df = existing_history_df.reset_index()

        print(f"File found...updating the {product_id} {time_length} data.")

        if verbose == True:
            print("Existing data:")
            print(existing_history_df)

        # Find last date in existing data
        last_data_date = existing_history_df["Date"].max()
        starting_rows = len(existing_history_df)
        print(f"Last date in existing data: {last_data_date}")
        print(f"Number of rows in existing data: {starting_rows}")

        # Resume from the last stored candle. It is re-fetched because the
        # period may still have been in progress when it was written
        current_start = last_data_date

    except FileNotFoundError:
        # Print error
        print(f"File not found...downloading the {product_id} {time_length} data.")

        # Create an empty DataFrame so that both paths converge on the same
        # fetch and merge below
        existing_history_df = pd.DataFrame(
            {
                "Date": pd.Series(dtype="datetime64[ns]"),
                "low": pd.Series(dtype="float64"),
                "high": pd.Series(dtype="float64"),
                "open": pd.Series(dtype="float64"),
                "close": pd.Series(dtype="float64"),
                "volume": pd.Series(dtype="float64"),
            }
        )

        # Set the number of starting rows to be 0
        starting_rows = 0

        # Find where the product's data actually begins rather than walking
        # forward from start_date at the requested granularity
        first_available_date = _find_first_available_date(
            product_id, start_date, end_date
        )

        if first_available_date is None:
            print(f"No data available for {product_id}.")
            return existing_history_df.set_index("Date")

        print(f"First available candle for {product_id}: {first_available_date}")
        current_start = first_available_date

    # Check for force_existing_check flag
    if force_existing_check == True:
        print("Forcing check of existing data...")
        current_start = start_date

    # Pull the data
    new_data = coinbase_fetch_full_history(
        product_id, current_start, end_date, granularity
    )

    if new_data.empty:
        # Nothing returned means the record is already current
        print(f"No new data returned...{product_id} {time_length} data is up to date.")
        full_history_df = existing_history_df.copy()

    else:
        new_data = new_data.rename(columns={"time": "Date"})

        if verbose == True:
            print("New data:")
            print(new_data)

        # Combine existing data with recent data, keeping the newly fetched row
        # where a date appears in both so that a partial candle is replaced by
        # its completed version
        full_history_df = pd.concat([existing_history_df, new_data])
        full_history_df = full_history_df.drop_duplicates(subset="Date", keep="last")
        full_history_df = full_history_df.sort_values(by="Date", ascending=True)
        full_history_df = full_history_df.reset_index(drop=True)

        if verbose == True:
            print("Combined data:")
            print(full_history_df)

    # Store with Date as the index, matching the existing data files
    full_history_df = full_history_df.set_index("Date")

    # Create directory
    os.makedirs(directory, exist_ok=True)

    # Export to Excel
    if excel_export == True:
        print(f"Exporting {product_id} {time_length} data to Excel...")
        full_history_df.to_excel(f"{directory}/{product_id}.xlsx", sheet_name="data")

    # Export to Pickle
    if pickle_export == True:
        print(f"Exporting {product_id} {time_length} data to Pickle...")
        full_history_df.to_pickle(f"{directory}/{product_id}.pkl")

    # Export to Parquet
    if parquet_export == True:
        print(f"Exporting {product_id} {time_length} data to Parquet...")
        full_history_df.to_parquet(f"{directory}/{product_id}.parquet")

    total_rows = len(full_history_df)

    # Output confirmation
    if output_confirmation == True:
        print(f"The first and last date of {time_length} data for {product_id} is: ")
        display(full_history_df[:1])
        display(full_history_df[-1:])
        print(f"Number of rows after data update: {total_rows}")

        if starting_rows:
            print(f"Number of rows added during update: {total_rows - starting_rows}")

        print(f"Coinbase data complete for {product_id} {time_length} data.")
        print(f"--------------------")

    return full_history_df


if __name__ == "__main__":

    # Stablecoins and wrapped coins are not useful for analysis
    excluded_products = [
        "DAI-USD",
        "GUSD-USD",
        "PAX-USD",
        "PYUSD-USD",
        "USDC-USD",
        "USDT-USD",
        "WAXL-USD",
        "WBTC-USD",
    ]

    # Identify the products to pull
    available_products = coinbase_fetch_available_products(
        base_currency=None,
        quote_currency="USD",
        status="online",
    )
    product_list = sorted(
        product
        for product in available_products["id"]
        if product not in excluded_products
    )

    # Limit to a subset of currencies for this example
    currencies = ["BTC", "ETH", "SOL", "XRP"]
    product_list = [
        product for product in product_list if product.split("-")[0] in currencies
    ]

    # Timespans
    granularities = [60, 3600, 86400]

    # Iterate through each product
    for product in product_list:
        for granularity in granularities:
            try:
                coinbase_pull_data(
                    base_directory=DATA_DIR,
                    product_id=product,
                    source="Coinbase",
                    asset_class="Cryptocurrencies",
                    granularity=granularity,
                    force_existing_check=False,
                    excel_export=granularity != 60,  # minute data is pickle only
                    pickle_export=True,
                    parquet_export=False,
                    output_confirmation=True,
                    verbose=False,
                )
            except Exception as e:
                print(f"Failed to pull {product} at granularity {granularity}: {e}")
