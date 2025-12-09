import requests
import pandas as pd

API_URL = "https://auctions.stacksbowers.com/..."  # the URL you find

resp = requests.get(API_URL)
resp.raise_for_status()
data = resp.json()

rows = []
for lot in data["lots"]:  # or whatever the key is
    rows.append(
        {
            "lot_number": lot["lot_number"],
            "title": lot["title"],
            "current_bid": lot["timed_auction_bid"]["amount"],
        }
    )

df = pd.DataFrame(rows)
print(df)
