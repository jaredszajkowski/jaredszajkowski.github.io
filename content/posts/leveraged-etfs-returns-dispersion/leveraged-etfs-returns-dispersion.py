# %% [markdown]
# # How do the long-term returns of leveraged ETFs diverge from their underlying index?

# %% [markdown]
# ## Python Imports

# %%
# Standard Library
import datetime
import io
import os
import random
import sys
import warnings

from datetime import datetime, timedelta
from pathlib import Path

# Data Handling
import numpy as np
import pandas as pd

# Data Visualization
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from matplotlib.ticker import FormatStrFormatter, FuncFormatter, MultipleLocator

# Data Sources
import yfinance as yf
import pandas_datareader.data as web

# Statistical Analysis
import statsmodels.api as sm

# Machine Learning
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Suppress warnings
warnings.filterwarnings("ignore")

# %% [markdown]
# ## Add Directories To Path

# %%
# Add the source subdirectory to the system path to allow import config from settings.py
current_directory = Path(os.getcwd())
website_base_directory = current_directory.parent.parent.parent
src_directory = website_base_directory / "src"
sys.path.append(str(src_directory)) if str(src_directory) not in sys.path else None

# Import settings.py
from settings import config

# Add configured directories from config to path
SOURCE_DIR = config("SOURCE_DIR")
sys.path.append(str(Path(SOURCE_DIR))) if str(Path(SOURCE_DIR)) not in sys.path else None

# Add other configured directories
BASE_DIR = config("BASE_DIR")
CONTENT_DIR = config("CONTENT_DIR")
POSTS_DIR = config("POSTS_DIR")
PAGES_DIR = config("PAGES_DIR")
PUBLIC_DIR = config("PUBLIC_DIR")
SOURCE_DIR = config("SOURCE_DIR")
DATA_DIR = config("DATA_DIR")
DATA_MANUAL_DIR = config("DATA_MANUAL_DIR")

# Print system path
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")

# %% [markdown]
# ## Track Index Dependencies

# %%
# Create file to track markdown dependencies
dep_file = Path("index_dep.txt")
dep_file.write_text("")

# %% [markdown]
# ## Python Functions

# %%
from build_index import build_index
from df_info import df_info
from df_info_markdown import df_info_markdown
from export_track_md_deps import export_track_md_deps
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_timeseries import plot_timeseries
from summary_stats import summary_stats
from yf_pull_data import yf_pull_data

# %%
# Set decimal places
pandas_set_decimal_places(2)

# %% [markdown]
# ## Data Overview

# %% [markdown]
# ### Acquire & Plot Data (QQQ)

# %%
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="QQQ",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)

qqq = load_data(
    base_directory=DATA_DIR,
    ticker="QQQ",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "QQQ_Close", etc.
qqq = qqq.rename(columns={
    "Close": "QQQ_Close", 
    "High": "QQQ_High", 
    "Low": "QQQ_Low", 
    "Open": "QQQ_Open", 
    "Volume": "QQQ_Volume"
})

# %%
plot_timeseries(
    price_df=qqq,
    plot_start_date="1999-03-10",
    plot_end_date="2025-12-31",
    plot_columns=["QQQ_Close"],
    title="QQQ Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_rotation=45,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=50,
    grid=True,
    legend=False,
    export_plot=True,
    plot_file_name="01_QQQ_Price",
)

# %%
# Copy this <!-- INSERT_01_QQQ_Price_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_QQQ_Price.md", 
    content=df_info_markdown(df=qqq, decimal_places=2),
    output_type="markdown",
)

# %% [markdown]
# ### Acquire & Plot Data (TQQQ)

# %%
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="TQQQ",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)

tqqq = load_data(
    base_directory=DATA_DIR,
    ticker="TQQQ",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "TQQQ_Close", etc.
tqqq = tqqq.rename(columns={
    "Close": "TQQQ_Close", 
    "High": "TQQQ_High", 
    "Low": "TQQQ_Low", 
    "Open": "TQQQ_Open", 
    "Volume": "TQQQ_Volume"
})


# %%
plot_timeseries(
    price_df=tqqq,
    plot_start_date="2010-02-11",
    plot_end_date="2025-12-31",
    plot_columns=["TQQQ_Close"],
    title="TQQQ Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_rotation=45,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=5,
    grid=True,
    legend=False,
    export_plot=True,
    plot_file_name="02_TQQQ_Price",
)

# %%
# Copy this <!-- INSERT_02_TQQQ_Price_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="02_TQQQ_Price.md", 
    content=df_info_markdown(df=qqq, decimal_places=2),
    output_type="markdown",
)

# %% [markdown]
# ### Calculate Cumulative Returns, Rolling Returns, and Drawdowns (QQQ & TQQQ)

# %%
etfs = ["QQQ", "TQQQ"]

# Merge dataframes and drop rows with missing values
qqq_tqqq_aligned = tqqq.merge(qqq, left_index=True, right_index=True, how='left')
qqq_tqqq_aligned = qqq_tqqq_aligned.dropna()

# Calculate cumulative returns
for etf in etfs:
    qqq_tqqq_aligned[f"{etf}_Return"] = qqq_tqqq_aligned[f"{etf}_Close"].pct_change()
    qqq_tqqq_aligned[f"{etf}_Cumulative_Return"] = (1 + qqq_tqqq_aligned[f"{etf}_Return"]).cumprod() - 1
    qqq_tqqq_aligned[f"{etf}_Cumulative_Return_Plus_One"] = 1 + qqq_tqqq_aligned[f"{etf}_Cumulative_Return"]
    qqq_tqqq_aligned[f"{etf}_Rolling_Max"] = qqq_tqqq_aligned[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    qqq_tqqq_aligned[f"{etf}_Drawdown"] = qqq_tqqq_aligned[f"{etf}_Cumulative_Return_Plus_One"] / qqq_tqqq_aligned[f"{etf}_Rolling_Max"] - 1
    qqq_tqqq_aligned.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)

# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        qqq_tqqq_aligned[f"{etf}_Rolling_Return_{period_name}"] = (
            qqq_tqqq_aligned[f"{etf}_Close"].pct_change(periods=window)
        )

# %%
# Copy this <!-- INSERT_03_QQQ_TQQQ_Aligned_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="03_QQQ_TQQQ_Aligned.md", 
    content=df_info_markdown(df=qqq_tqqq_aligned, decimal_places=2),
    output_type="markdown",
)

# %% [markdown]
# #### Plot Cumulative Returns


# %%
qqq_tqqq_aligned

# %%
plot_timeseries(
    price_df=qqq_tqqq_aligned,
    plot_start_date="2010-02-11",
    plot_end_date="2025-12-31",
    plot_columns=["QQQ_Cumulative_Return", "TQQQ_Cumulative_Return"],
    title="Cumulative Returns",
    x_label="Date",
    x_format="Year",
    x_tick_rotation=45,
    y_label="Cumulative Return",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=25,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="03_Cumulative_Returns",
)

# %%
plot_timeseries(
    price_df=qqq_tqqq_aligned,
    plot_start_date="2010-02-11",
    plot_end_date="2025-12-31",
    plot_columns=["QQQ_Drawdown", "TQQQ_Drawdown"],
    title="Drawdowns",
    x_label="Date",
    x_format="Year",
    x_tick_rotation=45,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing=0.10,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="03_Drawdowns",
)

# %%
qqq_sum_stats = summary_stats(
    fund_list=["QQQ"],
    df=qqq_tqqq_aligned[["QQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

tqqq_sum_stats = summary_stats(
    fund_list=["TQQQ"],
    df=qqq_tqqq_aligned[["TQQQ_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([qqq_sum_stats, tqqq_sum_stats])

# %%
sum_stats

# %% [markdown]
# ### Calculate Rolling Returns (QQQ & TQQQ)

# %%



# %%
# # Copy this <!-- INSERT_05_Portfolio_Stats_DF_HERE --> to index_temp.md
# export_track_md_deps(dep_file=dep_file, md_filename="05_Portfolio_Stats_DF.md", content=sum_stats.to_markdown(floatfmt=".3f"))

