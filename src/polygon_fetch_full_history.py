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
    existing_history_df: pd.DataFrame,
    current_start: datetime,
    free_tier: bool,
    verbose: bool,
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
    verbose : bool
        If True, print detailed information about the data being processed.

    Returns:
    --------
    full_history_df : pd.DataFrame
        DataFrame containing the data.
    """

    # Copy DataFrame
    full_history_df = existing_history_df.copy()

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
    
    new_data_last_date = None
    new_date_last_date_check = None

    while current_start < datetime.now():

        # Offset end date by time_delta
        current_end = current_start + timedelta(days=time_delta)

        if verbose == True:
            print(f"Pulling {timespan} data for {current_start} thru {current_end} for {ticker}...\n")

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

            # if len(aggs) == 0:
                # raise Exception(f"No data is available for {ticker} for {current_start} thru {current_end}. Please attempt different dates.")
            
            # Convert to DataFrame
            new_data = pd.DataFrame([bar.__dict__ for bar in aggs])
            new_data["timestamp"] = pd.to_datetime(new_data["timestamp"], unit="ms")
            new_data = new_data.rename(columns = {'timestamp':'Date'})
            new_data = new_data[['Date', 'open', 'high', 'low', 'close', 'volume', 'vwap', 'transactions', 'otc']]
            new_data = new_data.sort_values(by='Date', ascending=True)

            # Enforce dtypes to match full_history_df
            new_data = new_data.astype(full_history_df.dtypes.to_dict())

            # (Optional) reorder columns to match schema
            # new_data = new_data[full_history_df.columns]

            # Find last date in new_data
            new_data_last_date = new_data['Date'].max()

            if verbose == True:
                print("New data:")
                print(new_data)

            # No longer necessary to check for 5000 rows of data

            # Check if new data contains 5000 rows
            # if len(new_data) == 5000:
                # raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")

            # If full_history_df length is not 0, check to confirm that data overlaps to verify that there were not any splits in the data
            # if not full_history_df.empty:
                # if not full_history_df['Date'].isin(new_data['Date']).any():
                    # raise Exception(f"New data does not overlap with existing data.")

            if not full_history_df.empty:
                # Columns present in both frames
                common_cols = list(full_history_df.columns.intersection(new_data.columns))
                if not common_cols:
                    raise Exception("No common columns to compare.")

                # (Optional) de-duplicate to speed up the merge
                full_dedup = full_history_df[common_cols].drop_duplicates()
                new_dedup  = new_data[common_cols].drop_duplicates()

                # Inner join on every shared column = exact row matches
                overlap = full_dedup.merge(new_dedup, on=common_cols, how="inner")

                if overlap.empty:
                    raise Exception(f"New data does not overlap with existing data (full-row check).")

            # Combine existing data with recent data, drop duplicates, sort values, reset index
            full_history_df = pd.concat([full_history_df, new_data])
            full_history_df = full_history_df.drop_duplicates(subset="Date", keep="last")
            full_history_df = full_history_df.sort_values(by='Date',ascending=True)
            full_history_df = full_history_df.reset_index(drop=True)

            if verbose == True:
                print("Combined data:")
                print(full_history_df)

        except KeyError as e:
            print(f"No data is available for {ticker} from {current_start} thru {current_end}.")

            user_choice = input(
                f"Press Enter to continue, or type 'q' to quit: "
            )
            if user_choice.lower() == "q":
                print(f"Aborting operation to update {ticker} {timespan} data.")
                break  # break out of the while loop
            else:
                print(f"Trying next timeframe for {ticker} {timespan} data.")

                # Set last_data_date to current_end because we know data was not available
                # up until current_end
                new_data_last_date = current_end
                pass

        except Exception as e:
            print(f"Failed to pull {timespan} data for {current_start} thru {current_end} for {ticker}: {e}")
            raise  # Re-raise the original exception

        # Break out of loop if data is up-to-date (or close to being up-to-date because it is 
        # possible that entire range was not pulled due to the way API handles hour data
        # from minute data)
        if current_end > datetime.now():
            break
        else:
            # Edge case, if the last date for new_date is exactly time_overlap's duration
            # past current_start
            if new_date_last_date_check == new_data_last_date:
                current_start = current_end - timedelta(days=time_overlap)
                new_date_last_date_check = new_data_last_date
            else:
                current_start = new_data_last_date - timedelta(days=time_overlap)
                new_date_last_date_check = new_data_last_date

            # Code below is likely not necessary

            # # Overlap with existing data to capture all data but check to see if
            # # current_end is a Sunday and if so ensure overlap covers a trading day
            # if current_end.weekday() == 6:
            #     current_start = last_data_date - timedelta(days=(time_overlap+1))
            # else:
            #     current_start = last_data_date - timedelta(days=time_overlap)

        # Check for free tier and if so then pause for 12 seconds to avoid hitting API rate limits
        if free_tier == True:
            if verbose == True:
                print(f"Sleeping for 12 seconds to avoid hitting API rate limits...\n")
            time.sleep(12)

    # Return the DataFrame containing the full history
    return full_history_df

if __name__ == "__main__":

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

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
        ticker="SPY",
        timespan="hour",
        multiplier=1,
        adjusted=True,
        existing_history_df=df,
        current_start=datetime(current_year - 2, current_month, current_day),
        free_tier=True,
        verbose=True,
    )