```python
import pandas as pd
import requests
import time

from datetime import datetime

def coinbase_fetch_historical_candles(
    product_id: str,
    start: datetime,
    end: datetime,
    granularity: int,
) -> pd.DataFrame:

    """
    Fetch historical candle data for a given product from Coinbase Exchange API.

    Parameters:
    -----------
    product_id : str
        The trading pair (e.g., 'BTC-USD').
    start : str
        Start time in UTC.
    end : str
        End time in UTC.
    granularity : int
        Time slice in seconds (e.g., 3600 for hourly candles).

    Returns:
    --------
    pd.DataFrame
        DataFrame containing time, low, high, open, close, volume.
    """

    url = f'https://api.exchange.coinbase.com/products/{product_id}/candles'
    params = {
        'start': start.isoformat(),
        'end': end.isoformat(),
        'granularity': granularity
    }

    max_retries = 5
    retry_delay = 1  # initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Coinbase Exchange API returns data in reverse chronological order
            data = data[::-1]

            # Convert to DataFrame
            df = pd.DataFrame(data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df

        except requests.exceptions.HTTPError as errh:
            if response.status_code == 429:
                print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"HTTP Error: {errh}")
                break
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
            time.sleep(retry_delay)
            retry_delay *= 2
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
            time.sleep(retry_delay)
            retry_delay *= 2
        except requests.exceptions.RequestException as err:
            print(f"OOps: Something Else {err}")
            break

    raise Exception("Failed to fetch data after multiple retries.")

if __name__ == "__main__":
    
    # Example usage
    df = coinbase_fetch_historical_candles(
        product_id="BTC-USD",
        start=datetime(2025, 1, 1),
        end=datetime(2025, 1, 1),
        granularity=86_400,
    )

    if df is not None:
        print(df)
    else:
        print("No data returned.")
```