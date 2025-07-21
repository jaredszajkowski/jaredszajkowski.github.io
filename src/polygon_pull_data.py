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
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    start_date: str,
    end_date: str,
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
    base_directory : str
        Root path to store downloaded data.
    ticker : str
        Ticker symbol to download.
    source : str
        Name of the data source (e.g., 'Polygon').
    asset_class : str
        Asset class name (e.g., 'Equities').
    start_date : str
        Start date for the data in 'YYYY-MM-DD' format.
    end_date : str
        End date for the data in 'YYYY-MM-DD' format.
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
    df : pd.DataFrame
        DataFrame containing the downloaded data.
    """

    # Open client connection
    client = RESTClient(api_key=api_keys["POLYGON_KEY"])

    # Set file location based on parameters
    file_location = f"{base_directory}/{source}/{asset_class}/{timespan}/{ticker}.pkl"

    try:
        # Attempt to read existing pickle data file
        ex_data = pd.read_pickle(file_location)
        ex_data = ex_data.reset_index()
        print(f"File found...updating the {ticker} data")
        print("Existing data:")
        print(ex_data)

        # Pull recent data
        aggs = client.get_aggs(
            ticker=ticker,
            timespan=timespan,
            multiplier=multiplier,
            from_=start_date,
            to=end_date,
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

        # Combine existing data with recent data, sort values, set index to date
        full_history_df = pd.concat([ex_data,new_data[new_data['Date'].isin(ex_data['Date']) == False]])
        full_history_df = full_history_df.sort_values(by='Date',ascending=True)
        full_history_df = full_history_df.set_index('Date')
        print("Combined data:")
        print(full_history_df)

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
            print(f"Data update complete for {timespan} {ticker}.")
            print("--------------------")
        else:
            pass
    
    except FileNotFoundError:
        # Print error
        print(f"File not found...downloading the {ticker} data.")

        # Pull recent data
        aggs = client.get_aggs(
            ticker=ticker,
            timespan=timespan,
            multiplier=multiplier,
            from_=start_date,
            to=end_date,
            adjusted=adjusted,
            sort="asc",
            limit=5000,
        )

        # Convert to DataFrame
        full_history_df = pd.DataFrame([bar.__dict__ for bar in aggs])
        full_history_df["timestamp"] = pd.to_datetime(full_history_df["timestamp"], unit="ms")
        full_history_df = full_history_df.rename(columns = {'timestamp':'Date'})
        full_history_df = full_history_df[['Date', 'open', 'high', 'low', 'close', 'volume', 'vwap', 'transactions', 'otc']]
        full_history_df = full_history_df.sort_values(by='Date', ascending=True)
        full_history_df = full_history_df.set_index('Date')
        print("New data:")
        print(full_history_df)

        # Check if new data contains 5000 rows
        if len(full_history_df) == 5000:
            # Raise exception
            raise Exception(f"New data for {ticker} contains 5000 rows, indicating potential issues with data completeness or API limits.")
        else:
            pass

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

    # Stock Data
    equities = ["AMZN", "AAPL"]

    # Iterate through each stock
    for stock in equities:
        for year in range(2025, current_year+1):
            for month in range(1, current_month-1):
                print(f"Pulling data for {year}-{month:02d}...")
                for start_day in [1, 6, 11, 16, 21, 26]:
                    end_day = min(start_day + 5, monthrange(year, month)[1])
                    
                    polygon_pull_data(
                        base_directory=DATA_DIR,
                        ticker=stock,
                        source="Polygon",
                        asset_class="Equities",
                        start_date=datetime(year, month, start_day),
                        end_date=datetime(year, month, end_day),
                        timespan="minute",
                        multiplier=1,
                        adjusted=True,
                        excel_export=True,
                        pickle_export=True,
                        output_confirmation=True,
                    )

                    # Pause for 15 seconds to avoid hitting API rate limits
                    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                    time.sleep(15)

    # Iterate through each stock
    for stock in equities:
        for year in range(2025, current_year+1):
            for month in range(1, current_month-1):
                print(f"Pulling data for {year}-{month:02d}...")
                for start_day in [1, 16]:
                    end_day = min(start_day + 15, monthrange(year, month)[1])
                    
                    polygon_pull_data(
                        base_directory=DATA_DIR,
                        ticker=stock,
                        source="Polygon",
                        asset_class="Equities",
                        start_date=datetime(year, month, start_day),
                        end_date=datetime(year, month, end_day),
                        timespan="hour",
                        multiplier=1,
                        adjusted=True,
                        excel_export=True,
                        pickle_export=True,
                        output_confirmation=True,
                    )

                    # Pause for 15 seconds to avoid hitting API rate limits
                    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                    time.sleep(15)

    # Iterate through each stock
    for stock in equities:
        for year in range(2025, current_year+1):
            for month in range(1, current_month-1):
                print(f"Pulling data for {year}-{month:02d}...")
                for start_day in [1]:
                    end_day = min(start_day + 30, monthrange(year, month)[1])
                    
                    polygon_pull_data(
                        base_directory=DATA_DIR,
                        ticker=stock,
                        source="Polygon",
                        asset_class="Equities",
                        start_date=datetime(year, month, start_day),
                        end_date=datetime(year, month, end_day),
                        timespan="day",
                        multiplier=1,
                        adjusted=True,
                        excel_export=True,
                        pickle_export=True,
                        output_confirmation=True,
                    )

                    # Pause for 15 seconds to avoid hitting API rate limits
                    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                    time.sleep(15)

    # Exchange Traded Fund Data
    etfs = [
        'SPY',
        'TQQQ', 'AGG', 
        'EDC', 'EBND',
        'MVV', 'SCHZ',
        'VB', 'VIOO', 'BND',
        'UPRO', 'SGOV',
        'DHY',
        'IDU', 'IYC', 'IYE', 'IYF', 'IYH', 'IYJ', 'IYK', 'IYM', 'IYR', 'IYW', 'IYZ',
        'DIG', 'LTL', 'ROM', 'RXL', 'UCC', 'UGE', 'UPW', 'URE', 'UXI', 'UYG', 'UYM',
        'XLB', 'XLC', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY',
        'IVV', 'EFA', 'EEM', 'IEF', 'IEI', 'TLT', 'GSG', 'IAU', 'IYR',
        'SSO', 'EFO', 'EET', 'UBT', 'UST', 'GSG', 'UGL', 'URE',
        'TMF',
        'IWM', 'URTY',
    ]

    # Iterate through each ETF
    for fund in etfs:
        for year in range(2025, current_year+1):
            for month in range(1, current_month-1):
                print(f"Pulling data for {year}-{month:02d}...")
                for start_day in [1, 6, 11, 16, 21, 26]:
                    end_day = min(start_day + 5, monthrange(year, month)[1])
                    
                    polygon_pull_data(
                        base_directory=DATA_DIR,
                        ticker=fund,
                        source="Polygon",
                        asset_class="Exchange_Traded_Funds",
                        start_date=datetime(year, month, start_day),
                        end_date=datetime(year, month, end_day),
                        timespan="minute",
                        multiplier=1,
                        adjusted=True,
                        excel_export=True,
                        pickle_export=True,
                        output_confirmation=True,
                    )

                    # Pause for 15 seconds to avoid hitting API rate limits
                    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                    time.sleep(15)

    # Iterate through each ETF
    for fund in etfs:
        for year in range(2025, current_year+1):
            for month in range(1, current_month-1):
                print(f"Pulling data for {year}-{month:02d}...")
                for start_day in [1, 16]:
                    end_day = min(start_day + 15, monthrange(year, month)[1])
                    
                    polygon_pull_data(
                        base_directory=DATA_DIR,
                        ticker=fund,
                        source="Polygon",
                        asset_class="Exchange_Traded_Funds",
                        start_date=datetime(year, month, start_day),
                        end_date=datetime(year, month, end_day),
                        timespan="hour",
                        multiplier=1,
                        adjusted=True,
                        excel_export=True,
                        pickle_export=True,
                        output_confirmation=True,
                    )

                    # Pause for 15 seconds to avoid hitting API rate limits
                    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                    time.sleep(15)

    # Iterate through each ETF
    for fund in etfs:
        for year in range(2025, current_year+1):
            for month in range(1, current_month-1):
                print(f"Pulling data for {year}-{month:02d}...")
                for start_day in [1]:
                    end_day = min(start_day + 30, monthrange(year, month)[1])
                    
                    polygon_pull_data(
                        base_directory=DATA_DIR,
                        ticker=fund,
                        source="Polygon",
                        asset_class="Exchange_Traded_Funds",
                        start_date=datetime(year, month, start_day),
                        end_date=datetime(year, month, end_day),
                        timespan="day",
                        multiplier=1,
                        adjusted=True,
                        excel_export=True,
                        pickle_export=True,
                        output_confirmation=True,
                    )

                    # Pause for 15 seconds to avoid hitting API rate limits
                    print(f"Sleeping for 15 seconds to avoid hitting API rate limits...")
                    time.sleep(15)