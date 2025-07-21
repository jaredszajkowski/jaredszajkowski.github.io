import pandas as pd

from load_data import load_data
from settings import config

# Get the data directory from the configuration
DATA_DIR = config("DATA_DIR")

# This script checks for missing timestamps in a DataFrame loaded from a pickle file.

# Load the pickle file
df = load_data(
    base_directory=DATA_DIR,
    ticker="XRP-USD",
    source="Coinbase",
    asset_class="Cryptocurrencies",
    timeframe="Minute",
    file_format="pickle",
)

print(df)

# Reset the index
df = df.reset_index(drop=False)

# Ensure the timestamp is datetime type
df['Date'] = pd.to_datetime(df['Date'])

# Sort by time (important for detecting gaps)
df = df.sort_values(by='Date', ascending=True)

# Set expected frequency (adjust as needed:
# 'min' for minute
# 'h' for hourly
# 'D' for daily
expected_freq = 'min'

# Create a complete range
full_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq=expected_freq)

# Detect missing timestamps
missing = full_range.difference(df['Date'])

# Summary
print(f"Total expected timestamps: {len(full_range)}")
print(f"Total actual timestamps: {df.shape[0]}")
print(f"Missing timestamps: {len(missing)}")

# Convert to DataFrame for grouping
missing_df = pd.DataFrame({'missing_timestamp': missing})
missing_df['year'] = missing_df['missing_timestamp'].dt.year
missing_df['month'] = missing_df['missing_timestamp'].dt.month

# Count missing timestamps by year and month
missing_by_year_month = (
    missing_df.groupby(['year', 'month'])
    .size()
    .reset_index(name='missing_count')
)

# Generate all year-month combinations in your date range
years = range(df['Date'].min().year, df['Date'].max().year + 1)
months = range(1, 13)
all_combinations = pd.MultiIndex.from_product([years, months], names=['year', 'month'])

# Reindex to force inclusion
missing_by_year_month = missing_by_year_month.set_index(['year', 'month']).reindex(
    all_combinations, fill_value=0
).reset_index()

# Optional: pivot for nicer display
pivot_table = missing_by_year_month.pivot(index='year', columns='month', values='missing_count').fillna(0).astype(int)
print(pivot_table)