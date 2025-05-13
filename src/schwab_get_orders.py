import requests

# Replace these with your actual values
ACCESS_TOKEN = 'your_access_token_here'
ACCOUNT_ID = 'your_account_id_here'

# Schwab API base URL
BASE_URL = 'https://api.schwabapi.com/trader/v1/accounts'

# Endpoint to get orders for the account
orders_url = f"{BASE_URL}/{ACCOUNT_ID}/orders"

# Set up headers with your bearer token
headers = {
    'Authorization': f"Bearer {ACCESS_TOKEN}",
    'Accept': 'application/json'
}

# Make the request
response = requests.get(orders_url, headers=headers)

# Check and display the response
if response.status_code == 200:
    orders = response.json()
    for order in orders:
        print(order)
else:
    print(f"Failed to fetch orders: {response.status_code}")
    print(response.text)
