from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

# ==== Config ====
html_path = Path("stacks_bowers.html")
csv_path = Path("stacks_bowers.csv")

# ==== Time stamp for this scrape ====
current_time = pd.Timestamp.now()
col_time = current_time.strftime("%Y%m%d_%H%M%S")
bid_col = f"current_bid_{col_time}"

# ==== Parse HTML ====
with html_path.open(encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "lxml")

rows = []

for lot_div in soup.select("div.lot-v2"):

    # Lot number
    lot_id_attr = lot_div.get("id", "")
    if lot_id_attr.startswith("list-lot-"):
        lot_number = lot_id_attr.split("-")[-1]
    else:
        num_div = lot_div.select_one(".lot-number")
        lot_number = num_div.get_text(strip=True) if num_div else None

    # Link & short title
    link_tag = lot_div.select_one("a.block-link")
    href = link_tag["href"] if link_tag and link_tag.has_attr("href") else None
    short_title = link_tag.get_text(strip=True) if link_tag else None

    # Full title
    full_title_div = lot_div.select_one(".inner-details .title.lot-title")
    full_title = full_title_div.get_text(strip=True) if full_title_div else None

    # PCGS
    pcgs_span = lot_div.select_one(".lot-pcgs span")
    pcgs = pcgs_span.get_text(strip=True) if pcgs_span else None

    # Current bid
    current_bid_span = lot_div.select_one(".current-bid .bid-amount")
    current_bid = current_bid_span.get_text(strip=True) if current_bid_span else None

    rows.append(
        {
            "lot_number": lot_number,
            "href": href,
            "short_title": short_title,
            "full_title": full_title,
            "pcgs": pcgs,
            bid_col: current_bid,
        }
    )

# New scrape as DataFrame
new_df = pd.DataFrame(rows)

# ==== Merge with existing CSV (if any) ====
if csv_path.exists():
    old_df = pd.read_csv(csv_path, dtype={"lot_number": str})
    new_df["lot_number"] = new_df["lot_number"].astype(str)

    # Merge on lot_number, keeping all existing columns + new bid column
    df = old_df.merge(new_df[["lot_number", bid_col]], on="lot_number", how="outer")
else:
    df = new_df

print(df.head())
df.to_csv(csv_path, index=False)
