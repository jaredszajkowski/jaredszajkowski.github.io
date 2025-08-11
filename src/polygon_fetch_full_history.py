import pandas as pd
import time

from datetime import datetime, timedelta
from load_api_keys import load_api_keys
from polygon import RESTClient
from settings import config

# Load API keys from the environment
api_keys = load_api_keys()

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

def polygon_fetch_full_history(
    client,
    ticker: str,
    timespan: str,
    multiplier: int,
    adjusted: bool,
    full_history_df: pd.DataFrame,
    current_start: datetime,
    free_tier: bool,
) -> pd.DataFrame:

    """
    Fetch full historical data for a given product from Polygon API.

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
    full_history_df : pd.DataFrame
        DataFrame containing the data.
    current_start : datetime
        Date for which to start pulling data in datetime format.
    free_tier : bool
        If True, then pause to avoid API limits.

    Returns:
    --------
    full_history_df : pd.DataFrame
        DataFrame containing the data.
    """

    if timespan == "minute":
        time_delta = 5
    elif timespan == "hour":
        time_delta = 180
    elif timespan == "day":
        time_delta = 365
    else:
        raise Exception(f"Invalid {timespan}.")

    while current_start < datetime.now():

        # Offset end date by time_delta
        current_end = current_start + timedelta(days=time_delta)

        print(f"Pulling {timespan} data for {current_start} thru {current_end} for {ticker}...")
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

            # Convert to DataFrame
            new_data = pd.DataFrame([bar.__dict__ for bar in aggs])
            new_data["timestamp"] = pd.to_datetime(new_data["timestamp"], unit="ms")
            new_data = new_data.rename(columns = {'timestamp':'Date'})
            new_data = new_data[['Date', 'open', 'high', 'low', 'close', 'volume', 'vwap', 'transactions', 'otc']]
            new_data = new_data.sort_values(by='Date', ascending=True)
            print("New data:")
            print(new_data)

            # Check if new data contains 5000 rows
            if len(new_data) == 5000:
                raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
            else:
                pass

            # Combine existing data with recent data, sort values
            full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
            full_history_df = full_history_df.sort_values(by='Date',ascending=True)
            print("Combined data:")
            print(full_history_df)

            # Check for free tier and if so then pause for 12 seconds to avoid hitting API rate limits
            if free_tier == True:
                print(f"Sleeping for 12 seconds to avoid hitting API rate limits...\n")
                time.sleep(12)
            else:
                pass

        except Exception as e:
            print(f"Failed to pull {timespan} data for {current_start} thru {current_end} for {ticker}: {e}")

        # Break out of loop if data is up-to-date, otherwise pause if free tier
        if current_end > datetime.now():
            break
        else:
            current_start = current_end + timedelta(days=time_delta)

    return full_history_df

if __name__ == "__main__":

    # Open client connection
    client = RESTClient(api_key=api_keys["POLYGON_KEY"])

    # Create an empty DataFrame
    df = pd.DataFrame({
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

    # Example usage - minute
    df = polygon_fetch_full_history(
        client=client,
        ticker="AMZN",
        timespan="day",
        multiplier=1,
        adjusted=True,
        full_history_df=df,
        current_start=datetime(2025, 1, 1),
        free_tier=True,
    )