import os
import pandas as pd
import time

from calendar import monthrange
from datetime import datetime
from IPython.display import display
from load_api_keys import load_api_keys
from polygon import RESTClient
from settings import config

# Load API keys from the environment
api_keys = load_api_keys()

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

def polygon_pull_data(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    start_date: datetime,
    timespan: str,
    multiplier: int,
    adjusted: bool,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    
    """
    Read existing data file, download price data from Polygon, and export data.

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
        If True, return adjusted data; if False, return raw data.
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    None
    """

    # Open client connection
    client = RESTClient(api_key=api_keys["POLYGON_KEY"])

    # Set file location based on parameters
    file_location = f"{base_directory}/{source}/{asset_class}/{timespan}/{ticker}.pkl"

    try:
        # Attempt to read existing pickle data file
        full_history_df = pd.read_pickle(file_location)

        # Reset index if 'Date' is column is the index
        if 'Date' not in full_history_df.columns:
            full_history_df = full_history_df.reset_index()

        print(f"File found...updating the {ticker} data")
        print("Existing data:")
        print(full_history_df)

        # Find last date in existing data
        last_date = full_history_df['Date'].max()
        last_year = last_date.year
        last_month = last_date.month
        print(f"Last date in existing data: {last_date}")

        # If the last date is the current month and year, pull data for the current month (some data may be pulled again)
        if last_year == current_year and last_month == current_month:
            # Pull data for minute
            if timespan == "minute":
                for start_day in [1, 6, 11, 16, 21, 26]:
                    end_day = min(start_day + 5, monthrange(current_year, current_month)[1])
                    print(f"Pulling data for {current_year}-{current_month:02d}-{start_day:02d} thru {current_year}-{current_month:02d}-{end_day:02d}...")
                    try:
                        # Pull new data
                        aggs = client.get_aggs(
                            ticker=ticker,
                            timespan=timespan,
                            multiplier=multiplier,
                            from_=datetime(current_year, current_month, start_day),
                            to=datetime(current_year, current_month, end_day),
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
                            # Raise exception
                            raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                        else:
                            pass

                        # Combine existing data with recent data, sort values
                        full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                        full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                        print("Combined data:")
                        print(full_history_df)

                    except Exception as e:
                        print(f"Failed to pull data for {current_year}-{current_month:02d}-{start_day:02d} thru {current_year}-{current_month:02d}-{end_day:02d}: {e}")

                    # Pause for 15 seconds to avoid hitting API rate limits
                    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                    time.sleep(15)

            # Pull data for hour
            elif timespan == "hour":
                for start_day in [1, 16]:
                    end_day = min(start_day + 15, monthrange(current_year, current_month)[1])
                    print(f"Pulling data for {current_year}-{current_month:02d}-{start_day:02d} thru {current_year}-{current_month:02d}-{end_day:02d}...")
                    try:
                        # Pull new data
                        aggs = client.get_aggs(
                            ticker=ticker,
                            timespan=timespan,
                            multiplier=multiplier,
                            from_=datetime(current_year, current_month, start_day),
                            to=datetime(current_year, current_month, end_day),
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
                            # Raise exception
                            raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                        else:
                            pass

                        # Combine existing data with recent data, sort values
                        full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                        full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                        print("Combined data:")
                        print(full_history_df)

                    except Exception as e:
                        print(f"Failed to pull data for {current_year}-{current_month:02d}-{start_day:02d} thru {current_year}-{current_month:02d}-{end_day:02d}: {e}")

                    # Pause for 15 seconds to avoid hitting API rate limits
                    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                    time.sleep(15)

            # Pull data for day
            elif timespan == "day":
                for start_day in [1]:
                    end_day = min(start_day + 30, monthrange(current_year, current_month)[1])
                    print(f"Pulling data for {current_year}-{current_month:02d}-{start_day:02d} thru {current_year}-{current_month:02d}-{end_day:02d}...")
                    try:
                        # Pull new data
                        aggs = client.get_aggs(
                            ticker=ticker,
                            timespan=timespan,
                            multiplier=multiplier,
                            from_=datetime(current_year, current_month, start_day),
                            to=datetime(current_year, current_month, end_day),
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
                            # Raise exception
                            raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                        else:
                            pass

                        # Combine existing data with recent data, sort values
                        full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                        full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                        print("Combined data:")
                        print(full_history_df)

                    except Exception as e:
                        print(f"Failed to pull data for {current_year}-{current_month:02d}-{start_day:02d} thru {current_year}-{current_month:02d}-{end_day:02d}: {e}")

                    # Pause for 15 seconds to avoid hitting API rate limits
                    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                    time.sleep(15)

        # Iterate through each year and month to pull data since the last date
        else:
            # Pull data for minute
            if timespan == "minute":
                for year in range(last_year, current_year + 1):
                    for month in range(1, 13):
                        for start_day in [1, 6, 11, 16, 21, 26]:
                            end_day = min(start_day + 5, monthrange(year, month)[1])
                            print(f"Pulling data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}...")
                            try:
                                # Pull new data
                                aggs = client.get_aggs(
                                    ticker=ticker,
                                    timespan=timespan,
                                    multiplier=multiplier,
                                    from_=datetime(year, month, start_day),
                                    to=datetime(year, month, end_day),
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
                                    # Raise exception
                                    raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                                else:
                                    pass

                                # Combine existing data with recent data, sort values
                                full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                                full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                                print("Combined data:")
                                print(full_history_df)

                            except Exception as e:
                                print(f"Failed to pull data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}: {e}")

                            # Pause for 15 seconds to avoid hitting API rate limits
                            print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                            time.sleep(15)

            # Pull data for hour
            elif timespan == "hour":
                for year in range(last_year, current_year + 1):
                    for month in range(1, 13):
                        for start_day in [1, 16]:
                            end_day = min(start_day + 15, monthrange(year, month)[1])
                            print(f"Pulling data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}...")
                            try:
                                # Pull new data
                                aggs = client.get_aggs(
                                    ticker=ticker,
                                    timespan=timespan,
                                    multiplier=multiplier,
                                    from_=datetime(year, month, start_day),
                                    to=datetime(year, month, end_day),
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
                                    # Raise exception
                                    raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                                else:
                                    pass

                                # Combine existing data with recent data, sort values
                                full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                                full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                                print("Combined data:")
                                print(full_history_df)

                            except Exception as e:
                                print(f"Failed to pull data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}: {e}")

                            # Pause for 15 seconds to avoid hitting API rate limits
                            print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                            time.sleep(15)

            # Pull data for day
            elif timespan == "day":
                for year in range(last_year, current_year + 1):
                    for month in range(1, 13):
                        for start_day in [1]:
                            end_day = min(start_day + 30, monthrange(year, month)[1])
                            print(f"Pulling data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}...")
                            try:
                                # Pull new data
                                aggs = client.get_aggs(
                                    ticker=ticker,
                                    timespan=timespan,
                                    multiplier=multiplier,
                                    from_=datetime(year, month, start_day),
                                    to=datetime(year, month, end_day),
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
                                    # Raise exception
                                    raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                                else:
                                    pass

                                # Combine existing data with recent data, sort values
                                full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                                full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                                print("Combined data:")
                                print(full_history_df)

                            except Exception as e:
                                print(f"Failed to pull data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}: {e}")

                            # Pause for 15 seconds to avoid hitting API rate limits
                            print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                            time.sleep(15)


    except FileNotFoundError:
        # Print error
        print(f"File not found...downloading the {ticker} data.")

        # Create an empty DataFrame
        full_history_df = pd.DataFrame({
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

        # Pull data for minute
        if timespan == "minute":
            for year in range(start_date.year, start_date.year + 1):
                for month in range(start_date.month, 13):
                    for start_day in [1, 6, 11, 16, 21, 26]:
                        end_day = min(start_day + 5, monthrange(year, month)[1])
                        print(f"Pulling data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}...")
                        try:
                            # Pull new data
                            aggs = client.get_aggs(
                                ticker=ticker,
                                timespan=timespan,
                                multiplier=multiplier,
                                from_=datetime(year, month, start_day),
                                to=datetime(year, month, end_day),
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
                                # Raise exception
                                raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                            else:
                                pass

                            # Combine existing data with recent data, sort values
                            full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                            full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                            print("Combined data:")
                            print(full_history_df) 

                        except Exception as e:
                            print(f"Failed to pull data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}: {e}")

                        # Pause for 15 seconds to avoid hitting API rate limits
                        print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                        time.sleep(15)
            
            # Continue pulling data for the next years and months
            for year in range(start_date.year + 1, datetime.now().year + 1):
                for month in range(1, datetime.now().month):
                    for start_day in [1, 6, 11, 16, 21, 26]:
                        end_day = min(start_day + 5, monthrange(year, month)[1])
                        print(f"Pulling data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}...")
                        try:
                            # Pull new data
                            aggs = client.get_aggs(
                                ticker=ticker,
                                timespan=timespan,
                                multiplier=multiplier,
                                from_=datetime(year, month, start_day),
                                to=datetime(year, month, end_day),
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
                                # Raise exception
                                raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                            else:
                                pass

                            # Combine existing data with recent data, sort values
                            full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                            full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                            print("Combined data:")
                            print(full_history_df) 

                        except Exception as e:
                            print(f"Failed to pull data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}: {e}")

                        # Pause for 15 seconds to avoid hitting API rate limits
                        print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                        time.sleep(15)
        
        # Pull data for hour
        elif timespan == "hour":
            for year in range(start_date.year, start_date.year + 1):
                for month in range(start_date.month, 13):
                    for start_day in [1, 16]:
                        end_day = min(start_day + 15, monthrange(year, month)[1])
                        print(f"Pulling data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}...")
                        try:
                            # Pull new data
                            aggs = client.get_aggs(
                                ticker=ticker,
                                timespan=timespan,
                                multiplier=multiplier,
                                from_=datetime(year, month, start_day),
                                to=datetime(year, month, end_day),
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
                                # Raise exception
                                raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                            else:
                                pass

                            # Combine existing data with recent data, sort values
                            full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                            full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                            print("Combined data:")
                            print(full_history_df) 

                        except Exception as e:
                            print(f"Failed to pull data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}: {e}")

                        # Pause for 15 seconds to avoid hitting API rate limits
                        print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                        time.sleep(15)

            # Continue pulling data for the next years and months
            for year in range(start_date.year + 1, datetime.now().year + 1):
                for month in range(1, datetime.now().month):
                    for start_day in [1, 16]:
                        end_day = min(start_day + 15, monthrange(year, month)[1])
                        print(f"Pulling data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}...")
                        try:
                            # Pull new data
                            aggs = client.get_aggs(
                                ticker=ticker,
                                timespan=timespan,
                                multiplier=multiplier,
                                from_=datetime(year, month, start_day),
                                to=datetime(year, month, end_day),
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
                                # Raise exception
                                raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                            else:
                                pass

                            # Combine existing data with recent data, sort values
                            full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                            full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                            print("Combined data:")
                            print(full_history_df)

                        except Exception as e:
                            print(f"Failed to pull data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}: {e}")

                        # Pause for 15 seconds to avoid hitting API rate limits
                        print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                        time.sleep(15)

        # Pull data for day
        elif timespan == "day":
            for year in range(start_date.year, start_date.year + 1):
                for month in range(start_date.month, 13):
                    for start_day in [1]:
                        end_day = min(start_day + 30, monthrange(year, month)[1])
                        print(f"Pulling data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}...")
                        try:
                            # Pull new data
                            aggs = client.get_aggs(
                                ticker=ticker,
                                timespan=timespan,
                                multiplier=multiplier,
                                from_=datetime(year, month, start_day),
                                to=datetime(year, month, end_day),
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
                                # Raise exception
                                raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                            else:
                                pass

                            # Combine existing data with recent data, sort values
                            full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                            full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                            print("Combined data:")
                            print(full_history_df)

                        except Exception as e:
                            print(f"Failed to pull data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}: {e}")

                        # Pause for 15 seconds to avoid hitting API rate limits
                        print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                        time.sleep(15)

            # Continue pulling data for the next years and months
            for year in range(start_date.year + 1, datetime.now().year + 1):
                for month in range(1, datetime.now().month):
                    for start_day in [1]:
                        end_day = min(start_day + 30, monthrange(year, month)[1])
                        print(f"Pulling data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}...")
                        try:
                            # Pull new data
                            aggs = client.get_aggs(
                                ticker=ticker,
                                timespan=timespan,
                                multiplier=multiplier,
                                from_=datetime(year, month, start_day),
                                to=datetime(year, month, end_day),
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
                                # Raise exception
                                raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
                            else:
                                pass

                            # Combine existing data with recent data, sort values
                            full_history_df = pd.concat([full_history_df,new_data[new_data['Date'].isin(full_history_df['Date']) == False]])
                            full_history_df = full_history_df.sort_values(by='Date',ascending=True)
                            print("Combined data:")
                            print(full_history_df)

                        except Exception as e:
                            print(f"Failed to pull data for {year}-{month:02d}-{start_day:02d} thru {year}-{month:02d}-{end_day:02d}: {e}")

                        # Pause for 15 seconds to avoid hitting API rate limits
                        print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                        time.sleep(15)

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/{timespan}"
    os.makedirs(directory, exist_ok=True)

    # Export to excel
    if excel_export == True:
        full_history_df.to_excel(f"{directory}/{ticker}.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        full_history_df.to_pickle(f"{directory}/{ticker}.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        print(f"The first and last date of data for {ticker} is: ")
        display(full_history_df[:1])
        display(full_history_df[-1:])
        print(f"Polygon data complete for {ticker}")
        print(f"--------------------")
    else:
        pass

    return full_history_df

if __name__ == "__main__":

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    # Stock Data
    equities = ["AMZN", "AAPL"]

    # Iterate through each stock
    for stock in equities:
        # Example usage - minute
        polygon_pull_data(
            base_directory=DATA_DIR,
            ticker=stock,
            source="Polygon",
            asset_class="Equities",
            start_date=datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day),
            timespan="minute",
            multiplier=1,
            adjusted=True,
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
        )

        # Example usage - hourly
        polygon_pull_data(
            base_directory=DATA_DIR,
            ticker=stock,
            source="Polygon",
            asset_class="Equities",
            start_date=datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day),
            timespan="hour",
            multiplier=1,
            adjusted=True,
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
        )

        # Example usage - daily
        polygon_pull_data(
            base_directory=DATA_DIR,
            ticker=stock,
            source="Polygon",
            asset_class="Equities",
            start_date=datetime(datetime.now().year - 2, datetime.now().month, datetime.now().day),
            timespan="day",
            multiplier=1,
            adjusted=True,
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
        )