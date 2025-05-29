import json
import pandas as pd
import requests

from load_api_keys import load_api_keys
from pathlib import Path
from settings import config

# Load API keys from the environment
api_keys = load_api_keys()

# Add configured directories
SOURCE_DIR = config("SOURCE_DIR")

def schwab_order_history(
    max_results: int,
    from_entered_time: str,
    to_entered_time: str,
    account_id: str,
) -> pd.DataFrame:
    
    """
    Fetches order history from Schwab API and returns it as a pandas DataFrame.
    
    Parameters:
    -----------
    max_results : int
        Maximum number of results to return.
    from_entered_time : str
        Start date for the order history in ISO 8601 format. (e.g., "2024-04-29T00:00:00.000Z")
    to_entered_time : str
        End date for the order history in ISO 8601 format. (e.g., "2025-03-28T23:59:59.000Z")
    account_id : str
        Schwab account ID to fetch order history for.
        
    Returns:
    --------
    df : pd.DataFrame
        DataFrame containing the order history.
    """

    def load_access_token_from_file(token_file="token.json"):
        with open(token_file, "r") as f:
            tokens = json.load(f)
        return tokens["access_token"]

    # Load current access token from file
    access_token = load_access_token_from_file(token_file=SOURCE_DIR / "token.json")

    # Schwab order history endpoint
    if account_id:
        url = f"https://api.schwabapi.com/trader/v1/accounts/{account_id}/orders"
    else:
        url = f"https://api.schwabapi.com/trader/v1/orders"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    params = {
        "maxResults": max_results,
        "fromEnteredTime": from_entered_time,
        "toEnteredTime": to_entered_time,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"API Error {response.status_code}: {response.text}")

    orders = response.json()
    # for order in orders:
    #         print(order)

    # Extract relevant data
    records = []
    for order in orders:
        legs = order.get("orderLegCollection", [])
        if not legs:
            continue

        symbol = legs[0]["instrument"].get("symbol")
        instruction = legs[0].get("instruction")

        for activity in order.get("orderActivityCollection", []):
            for exec_leg in activity.get("executionLegs", []):
                records.append({
                    "order_id": order.get("orderId"),
                    "execution_time": exec_leg.get("time"),
                    "instruction": instruction,
                    "symbol": symbol,
                    # "execution_legId": exec_leg.get("legId"),
                    "execution_quantity": exec_leg.get("quantity"),
                    "execution_price": exec_leg.get("price"),
                })

    return pd.DataFrame(records)

if __name__ == "__main__":
    df = schwab_order_history(
        max_results=50,
        from_entered_time="2024-05-29T00:00:00.000Z",
        to_entered_time="2025-05-13T23:59:59.000Z",
        account_id=None,
    )
    print(df.head())
