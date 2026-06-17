import databento as db
import pandas as pd

from datetime import datetime, timedelta
from settings import config

# Load API key from the environment variables
DATABENTO_KEY = config("DATABENTO_KEY")

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# DataBento fixed-point price scale: 1 unit = 1e-9 USD
PRICE_SCALE = 1_000_000_000


def databento_fetch_full_history(
    client,
    dataset: str,
    symbol: str,
    schema: str,
    existing_history_df: pd.DataFrame,
    current_start: datetime,
    verbose: bool,
) -> pd.DataFrame:
    """
    Fetch full historical OHLCV data for a given symbol from DataBento.

    Parameters:
    -----------
    client
        DataBento Historical client instance.
    dataset : str
        DataBento dataset identifier (e.g., "XNAS.ITCH", "DBEQ.BASIC", "GLBX.MDP3").
    symbol : str
        Symbol to download (e.g., "AAPL", "ESM4").
    schema : str
        DataBento schema (e.g., "ohlcv-1m", "ohlcv-1h", "ohlcv-1d").
    existing_history_df : pd.DataFrame
        DataFrame containing the existing historical data.
    current_start : datetime
        Date for which to start pulling data in datetime format.
    verbose : bool
        If True, print detailed information about the data being processed.

    Returns:
    --------
    full_history_df : pd.DataFrame
        DataFrame containing the data.
    """

    full_history_df = existing_history_df.copy()

    if schema == "ohlcv-1m":
        time_delta = 15
        time_overlap = 1
    elif schema == "ohlcv-1h":
        time_delta = 15
        time_overlap = 1
    elif schema == "ohlcv-1d":
        time_delta = 180
        time_overlap = 1
    else:
        raise ValueError(
            f"Invalid schema: {schema}. Acceptable schemas are: ohlcv-1m, ohlcv-1h, ohlcv-1d."
        )

    new_data_last_date = None
    new_date_last_date_check = None

    while current_start < datetime.now():

        # DataBento end is exclusive, so add 1 day to include current_end's data
        current_end = current_start + timedelta(days=time_delta)

        if verbose:
            print(
                f"Pulling {schema} data for {current_start} thru {current_end} for {symbol}...\n"
            )

        try:
            store = client.timeseries.get_range(
                dataset=dataset,
                symbols=[symbol],
                schema=schema,
                start=current_start,
                end=current_end,
                stype_in="raw_symbol",
            )

            new_data = store.to_df()

            if new_data.empty:
                print(
                    f"No data available for {symbol} from {current_start} thru {current_end}."
                )
                new_data_last_date = current_end
                if current_end > datetime.now():
                    break
                current_start = current_end - timedelta(days=time_overlap)
                new_date_last_date_check = new_data_last_date
                continue

            # Reset index to get ts_event as a column
            new_data = new_data.reset_index()

            # Rename ts_event to Date and strip timezone info
            new_data = new_data.rename(columns={"ts_event": "Date"})
            new_data["Date"] = pd.to_datetime(new_data["Date"]).dt.tz_localize(None)

            # Convert fixed-point prices to float if needed (1 unit = 1e-9 USD)
            price_cols = ["open", "high", "low", "close"]
            for col in price_cols:
                if new_data[col].dtype == "int64":
                    new_data[col] = new_data[col] / PRICE_SCALE

            # Keep only OHLCV columns
            new_data = new_data[["Date", "open", "high", "low", "close", "volume"]]
            new_data = new_data.sort_values(by="Date", ascending=True)

            # Enforce dtypes to match full_history_df
            new_data = new_data.astype(full_history_df.dtypes.to_dict())

            new_data_last_date = new_data["Date"].max()

            if verbose:
                print("New data:")
                print(new_data)

            if not full_history_df.empty:
                overlap = full_history_df.merge(new_data, on=price_cols, how="inner")
                if overlap.empty:
                    raise Exception(
                        "New data does not overlap with existing data (price data check)."
                    )

            full_history_df = pd.concat([full_history_df, new_data])
            full_history_df = full_history_df.drop_duplicates(
                subset="Date", keep="last"
            )
            full_history_df = full_history_df.sort_values(by="Date", ascending=True)
            full_history_df = full_history_df.reset_index(drop=True)

            if verbose:
                print("Combined data:")
                print(full_history_df)

        except Exception as e:
            print(
                f"Failed to pull {schema} data for {current_start} thru {current_end} for {symbol}: {e}"
            )
            raise

        if current_end > datetime.now():
            break
        else:
            if new_date_last_date_check == new_data_last_date:
                current_start = current_end - timedelta(days=time_overlap)
            else:
                current_start = new_data_last_date - timedelta(days=time_overlap)

            new_date_last_date_check = new_data_last_date

    return full_history_df


if __name__ == "__main__":

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    client = db.Historical(key=DATABENTO_KEY)

    # Create an empty DataFrame
    df = pd.DataFrame(
        {
            "Date": pd.Series(dtype="datetime64[ns]"),
            "open": pd.Series(dtype="float64"),
            "high": pd.Series(dtype="float64"),
            "low": pd.Series(dtype="float64"),
            "close": pd.Series(dtype="float64"),
            "volume": pd.Series(dtype="int64"),
        }
    )

    df = databento_fetch_full_history(
        client=client,
        dataset="XNAS.ITCH",
        symbol="AAPL",
        schema="ohlcv-1d",
        existing_history_df=df,
        current_start=datetime(current_year - 2, current_month, current_day),
        verbose=True,
    )

    print(df)
