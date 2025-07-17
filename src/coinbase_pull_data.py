import os
import pandas as pd

from coinbase_fetch_available_products import coinbase_fetch_available_products
from coinbase_fetch_full_history import coinbase_fetch_full_history
from datetime import datetime, timedelta
from settings import config

# Get the data directory from the configuration
DATA_DIR = config("DATA_DIR")

def coinbase_pull_data(
    base_directory: str,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
    base_currency: str,
    quote_currency: str,
    granularity: int=3600, # 60=minute, 3600=hourly, 86400=daily
    status: str='online', # default status is 'online'
    start_date: str = datetime(2025, 1, 1), # default start date
    end_date: str = datetime.now() - timedelta(days = 1), # updates data through 1 day ago
) -> pd.DataFrame:
    
    """
    Pull historical data for a given product from Coinbase Exchange API.

    Parameters:
    -----------
    base_directory : str
        Root path to store downloaded data.
    source : str
        Name of the data source (e.g., 'Nasdaq_Data_Link').
    asset_class : str
        Asset class name (e.g., 'Equities').
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.
    base_currency : str
        The base currency (e.g., 'BTC').
    quote_currency : str
        The quote currency (e.g., 'USD').
    status : str, optional
        Filter products by status (default is 'online').
    granularity : int
        Time slice in seconds (e.g., 3600 for hourly candles).
    start_date : str, optional
        Start date in UTC (ISO format).
    end_date : str, optional
        End date in UTC (ISO format).

    Returns:
    --------
    pd.DataFrame
        DataFrame containing time, low, high, open, close, volume.
    """

    # List of crypto assets
    filtered_products = coinbase_fetch_available_products(base_currency=base_currency, quote_currency=quote_currency, status=status)
    filtered_products_list = filtered_products['id'].tolist()
    filtered_products_list = sorted(filtered_products_list)

    if not filtered_products.empty:
        print(filtered_products[['id', 'base_currency', 'quote_currency', 'status']])
        print(filtered_products_list)
        print(len(filtered_products_list))

    else:
        print("No products found with the specified base and/or quote currencies.")

    missing_data = []
    omitted_data = []
    num_products = len(filtered_products_list)
    counter = 0

    # Loop for updates
    for product in filtered_products_list:
        
        counter+=1
        print(f"Updating product {counter} of {num_products}.")

        if granularity == 60:
            time_length = "Minute"
        elif granularity == 3600:
            time_length = "Hourly"
        elif granularity == 86400:
            time_length = "Daily"
        else:
            print("Error - please confirm timeframe.")
            break

        # Set file location based on parameters
        file_location = f"{base_directory}/{source}/{asset_class}/{time_length}/{product}.pkl"
    
        try:
            # Attempt to read existing pickle data file
            ex_data = pd.read_pickle(file_location)
            ex_data = ex_data.reset_index()
            print(f"File found...updating the {product} data")
            print("Existing data:")
            print(ex_data)

            # Pull recent data
            new_data = coinbase_fetch_full_history(product, start_date, end_date, granularity)
            new_data = new_data.rename(columns={'time':'Date'})
            new_data['Date'] = new_data['Date'].dt.tz_localize(None)
            print("New data:")
            print(new_data)

            # Combine existing data with recent data
            full_history_df = pd.concat([ex_data,new_data[new_data['Date'].isin(ex_data['Date']) == False]])
            full_history_df = full_history_df.sort_values(by='Date')
            full_history_df = full_history_df.set_index('Date')
            full_history_df.index = full_history_df.index.tz_localize(None)
            print("Combined data:")
            print(full_history_df)

            # Create directory
            directory = f"{base_directory}/{source}/{asset_class}/{time_length}"
            os.makedirs(directory, exist_ok=True)

            # Export to excel
            if excel_export == True:
                full_history_df.to_excel(f"{directory}/{product}.xlsx", sheet_name="data")
            else:
                pass

            # Export to pickle
            if pickle_export == True:
                full_history_df.to_pickle(f"{directory}/{product}.pkl")
            else:
                pass

            # Output confirmation
            if output_confirmation == True:
                print(f"Data update complete for {time_length} {product}.")
                print("--------------------")
            else:
                pass
            
        except FileNotFoundError:
            # Starting year for fetching initial data
            starting_year = 2025

            # Print error
            print(f"File not found...downloading the {product} data starting with {starting_year}.")

            def get_full_hist(year):
                try:
                    # Define the start and end dates
                    start_date = datetime(year, 1, 1) # Default start date
                    end_date = datetime.now() - timedelta(days = 1) # Updates data through 1 day ago

                    # Fetch and process the data
                    full_history_df = coinbase_fetch_full_history(product, start_date, end_date, granularity)
                    full_history_df = full_history_df.rename(columns={'time': 'Date'})
                    full_history_df = full_history_df.sort_values(by='Date')

                    # Iterate through rows to see if the value of the asset ever exceeds a specified threshold
                    # Default value for the price threshold is 0 USD
                    # If the price never exceeds this threshold, the asset is omitted from the final list
                    def find_first_close_above_threshold(full_history_df, threshold=0):
                        # Ensure 'Date' is the index before proceeding
                        if 'Date' in full_history_df.columns:
                            full_history_df.set_index('Date', inplace=True)
                        full_history_df.index = full_history_df.index.tz_localize(None)
                        
                        # Iterate through the DataFrame
                        for index, row in full_history_df.iterrows():
                            if row['close'] >= threshold:
                                print(f"First occurrence: {index}, close={row['close']}")

                                # Return the filtered DataFrame starting from this row
                                return full_history_df.loc[index:]
                        
                        # If no value meets the condition, return an empty DataFrame
                        print(f"Share price never exceeds {threshold} USD.")
                        omitted_data.append(product)
                        return None
                    
                    full_history_above_threshold_df = find_first_close_above_threshold(full_history_df, threshold=0)

                    return full_history_above_threshold_df

                except KeyError:
                    print(f"KeyError: No data available for {product} in {year}. Trying next year...")
                    next_year = year + 1

                    # Base case: Stop if the next year exceeds the current year
                    if next_year > datetime.now().year:
                        print("No more data available for any future years.")
                        missing_data.append(product)
                        return None

                    # Recursive call for the next year
                    return get_full_hist(next_year)

            # Fetch the full history starting from the given year
            full_history_df = get_full_hist(starting_year)

            if full_history_df is not None:

                # Create directory
                directory = f"{base_directory}/{source}/{asset_class}/{time_length}"
                os.makedirs(directory, exist_ok=True)

                # Export to excel
                if excel_export == True:
                    full_history_df.to_excel(f"{directory}/{product}.xlsx", sheet_name="data")
                else:
                    pass

                # Export to pickle
                if pickle_export == True:
                    full_history_df.to_pickle(f"{directory}/{product}.pkl")
                else:
                    pass

                # Output confirmation
                if output_confirmation == True:
                    print(f"Initial data fetching completed successfully for {time_length} {product}.")
                    print("--------------------")
                else:
                    pass

            else:
                print("No data could be fetched for the specified range.")
                
        except Exception as e:
            print(str(e))

    # Remove the cryptocurrencies with missing data from the final list
    missing_data = sorted(missing_data)
    print(f"Data missing for: {missing_data}")

    for asset in missing_data:
        try:
            print(f"Removing {asset} from the list because it is missing data.")
            filtered_products_list.remove(asset)
        except ValueError:
            print(f"{asset} not in list.")
            pass

    # Remove the cryptocurrencies with share prices that never exceed 1 USD from the final list
    omitted_data = sorted(omitted_data)
    print(f"Data omitted due to price for: {omitted_data}")

    for asset in omitted_data:
        try:
            print(f"Removing {asset} from the list because the share price never exceeds 1 USD.")
            filtered_products_list.remove(asset)
        except ValueError:
            print(f"{asset} not in list.")
            pass  
    
    # Remove stablecoins from the final list
    stablecoins_to_remove = ['USDT-USD', 'USDC-USD', 'PAX-USD', 'DAI-USD', 'PYUSD-USD', 'GUSD-USD']
    stablecoins_to_remove = sorted(stablecoins_to_remove)
    print(f"Data for stable coins not to be used: {stablecoins_to_remove}")
    
    for asset in stablecoins_to_remove:
        try:
            filtered_products_list.remove(asset)
            # print(f"Removing {asset} from the list because it is a stablecoin.")
        except ValueError:
            # print(f"{asset} not in list.")
            pass 

    # Remove the wrapped coins from the final list
    wrapped_coins_to_remove = ['WAXL-USD', 'WBTC-USD']
    wrapped_coins_to_remove = sorted(wrapped_coins_to_remove)
    print(f"Data for wrapped coins not to be used: {wrapped_coins_to_remove}")
    
    for asset in wrapped_coins_to_remove:
        try:
            filtered_products_list.remove(asset)
            # print(f"Removing {asset} from the list because it is a wrapped coin.")
        except ValueError:
            # print(f"{asset} not in list.")
            pass

    # Print the final list of token and the length of the list
    print(f"Final list of tokens: {filtered_products_list}")
    print(f"Length of final list of tokens: {len(filtered_products_list)}")

    return full_history_df

if __name__ == "__main__":
       
    # # Example usage to pull all data for each month from 2010 to 2024
    # for year in range(2010, 2025):
    #     for month in range(1, 13):
    #         print(f"Pulling data for {year}-{month:02d}...")
    #         for days in [31, 30, 29, 28]:
    #             try:
    #                 df = coinbase_pull_data(
    #                     base_directory=DATA_DIR,
    #                     source="Coinbase",
    #                     asset_class="Cryptocurrencies",
    #                     excel_export=False,
    #                     pickle_export=True,
    #                     output_confirmation=True,
    #                     base_currency="SOL",
    #                     quote_currency="USD",
    #                     granularity=86400, # 60=minute, 3600=hourly, 86400=daily
    #                     status='online',
    #                     start_date=datetime(year, month, 1),
    #                     end_date=datetime(year, month, days),
    #                 )
    #                 break  # success
    #             except Exception as e:
    #                 print(f"Error pulling data for {year}-{month:02d} with {days} days: {e}")
    #         else:
    #             print(f"All attempts failed for {year}-{month:02d}, skipping...")
    #             continue

    current_year = datetime.now().year
    current_month = datetime.now().month
    currencies = ["BTC", "ETH", "SOL"]

    for cur in currencies:

        # Example usage - minute
        df = coinbase_pull_data(
            base_directory=DATA_DIR,
            source="Coinbase",
            asset_class="Cryptocurrencies",
            excel_export=False,
            pickle_export=True,
            output_confirmation=True,
            base_currency=cur,
            quote_currency="USD",
            granularity=60, # 60=minute, 3600=hourly, 86400=daily
            status='online', # default status is 'online'
            start_date=datetime(current_year, current_month, 1), # default start date
            end_date=datetime.now() - timedelta(days = 1), # updates data through 1 day ago
        )

        # Example usage - hourly
        df = coinbase_pull_data(
            base_directory=DATA_DIR,
            source="Coinbase",
            asset_class="Cryptocurrencies",
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
            base_currency=cur,
            quote_currency="USD",
            granularity=3600, # 60=minute, 3600=hourly, 86400=daily
            status='online', # default status is 'online'
            start_date=datetime(current_year, current_month, 1), # default start date
            end_date=datetime.now() - timedelta(days = 1), # updates data through 1 day ago
        )

        # Example usage - daily
        df = coinbase_pull_data(
            base_directory=DATA_DIR,
            source="Coinbase",
            asset_class="Cryptocurrencies",
            excel_export=True,
            pickle_export=True,
            output_confirmation=True,
            base_currency=cur,
            quote_currency="USD",
            granularity=86400, # 60=minute, 3600=hourly, 86400=daily
            status='online', # default status is 'online'
            start_date=datetime(current_year, current_month, 1), # default start date
            end_date=datetime.now() - timedelta(days = 1), # updates data through 1 day ago
        )