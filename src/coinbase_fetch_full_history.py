import pandas as pd
import time

from coinbase_fetch_historical_candles import coinbase_fetch_historical_candles
from datetime import datetime, timedelta


def coinbase_fetch_full_history(
    product_id: str,
    start: datetime,
    end: datetime,
    granularity: int,
) -> pd.DataFrame:
    """
    Fetch full historical data for a given product from Coinbase Exchange API.

    Parameters:
    -----------
    product_id : str
        The trading pair (e.g., 'BTC-USD').
    start : datetime
        Start time in UTC.
    end : datetime
        End time in UTC.
    granularity : int
        Time slice in seconds (e.g., 3600 for hourly candles).

    Returns:
    --------
    pd.DataFrame
        DataFrame containing time, low, high, open, close, volume.
    """

    all_data = []
    current_start = start
    window = timedelta(seconds=granularity * 300)  # Fetch max 300 candles per request

    while current_start < end:
        current_end = min(current_start + window, end)
        df = coinbase_fetch_historical_candles(
            product_id, current_start, current_end, granularity
        )

        if df.empty:
            # No candles in this window. Step over it rather than stopping: a
            # gap in the data longer than the window would otherwise truncate
            # the history at that point. This matters most at minute
            # granularity, where a window spans only 5 hours
            current_start = current_end
        else:
            all_data.append(df)
            current_start = df["time"].iloc[-1] + timedelta(seconds=granularity)

        time.sleep(0.2)  # Small delay to respect rate limits

    if all_data:
        full_df = pd.concat(all_data).reset_index(drop=True)
        return full_df
    else:
        return pd.DataFrame()


if __name__ == "__main__":

    # Example usage
    df = coinbase_fetch_full_history(
        product_id="BTC-USD",
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 31),
        granularity=86_400,
    )

    if df is not None:
        print(df)
    else:
        print("No data returned.")
