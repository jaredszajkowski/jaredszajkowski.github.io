import pandas as pd
import requests

def coinbase_fetch_available_products(
    base_currency: str=None,
    quote_currency: str=None,
    status: str=None,
) -> pd.DataFrame:

    """
    Fetch available products from Coinbase Exchange API.
    
    Parameters:
    -----------
    base_currency : str, optional
        Filter products by base currency (e.g., 'BTC').
    quote_currency : str, optional
        Filter products by quote currency (e.g., 'USD').
    status : str, optional
        Filter products by status (e.g., 'online', 'offline').

    Returns:
    --------
    pd.DataFrame
        DataFrame containing available products with their details.
    """

    url = 'https://api.exchange.coinbase.com/products'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        products = response.json()

        # Convert the list of products into a pandas DataFrame
        df = pd.DataFrame(products)
        
        # Filter by base_currency if provided
        if base_currency:
            df = df[df['base_currency'] == base_currency]
        
        # Filter by quote_currency if provided
        if quote_currency:
            df = df[df['quote_currency'] == quote_currency]

        # Filter by status if provided
        if status:
            df = df[df['status'] == status]
        
        return df
    
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Oops: Something Else {err}")

if __name__ == "__main__":
    # Example usage
    df = coinbase_fetch_available_products(base_currency='BTC', quote_currency='USD', status='online')
    if df is not None:
        print(df.head())
    else:
        print("No data returned.")