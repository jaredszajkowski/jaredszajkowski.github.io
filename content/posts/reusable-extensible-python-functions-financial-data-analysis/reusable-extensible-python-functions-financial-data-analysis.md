# Reusable And Extensible Python Functions For Financial Data Analysis

## Python Imports


```python
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

# Statistical Analysis
import statsmodels.api as sm

# Machine Learning
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Suppress warnings
warnings.filterwarnings("ignore")
```

## Add Directories To Path


```python
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
```

    0: /usr/lib/python313.zip
    1: /usr/lib/python3.13
    2: /usr/lib/python3.13/lib-dynload
    3: 
    4: /home/jared/python-virtual-envs/general-venv-p313/lib/python3.13/site-packages
    5: /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io_congo/src


## Track Index Dependencies


```python
# Create file to track markdown dependencies
dep_file = Path("index_dep.txt")
dep_file.write_text("")
```




    0



## Python Functions


```python
from export_track_md_deps import export_track_md_deps
```


```python
from bb_clean_data import bb_clean_data
code = Path(SOURCE_DIR / "bb_clean_data.py").read_text()
# Copy this <!-- INSERT_bb_clean_data_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="bb_clean_data.md", content=code, output_type="python")
```

    ✅ Exported and tracked: bb_clean_data.md



```python
from build_index import build_index
code = Path(SOURCE_DIR / "build_index.py").read_text()
# Copy this <!-- INSERT_build_index_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="build_index.md", content=code, output_type="python")
```

    ✅ Exported and tracked: build_index.md



```python
from calc_fed_cycle_asset_performance import calc_fed_cycle_asset_performance
code = Path(SOURCE_DIR / "calc_fed_cycle_asset_performance.py").read_text()
# Copy this <!-- INSERT_calc_fed_cycle_asset_performance_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="calc_fed_cycle_asset_performance.md", content=code, output_type="python")
```

    ✅ Exported and tracked: calc_fed_cycle_asset_performance.md



```python
from calc_vix_trade_pnl import calc_vix_trade_pnl
code = Path(SOURCE_DIR / "calc_vix_trade_pnl.py").read_text()
# Copy this <!-- INSERT_calc_vix_trade_pnl_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="calc_vix_trade_pnl.md", content=code, output_type="python")
```

    ✅ Exported and tracked: calc_vix_trade_pnl.md



```python
from coinbase_fetch_available_products import coinbase_fetch_available_products
code = Path(SOURCE_DIR / "coinbase_fetch_available_products.py").read_text()
# Copy this <!-- INSERT_coinbase_fetch_available_products_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="coinbase_fetch_available_products.md", content=code, output_type="python")
```

    ✅ Exported and tracked: coinbase_fetch_available_products.md



```python
from coinbase_fetch_full_history import coinbase_fetch_full_history
code = Path(SOURCE_DIR / "coinbase_fetch_full_history.py").read_text()
# Copy this <!-- INSERT_coinbase_fetch_full_history_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="coinbase_fetch_full_history.md", content=code, output_type="python")
```

    ✅ Exported and tracked: coinbase_fetch_full_history.md



```python
from coinbase_fetch_historical_candles import coinbase_fetch_historical_candles
code = Path(SOURCE_DIR / "coinbase_fetch_historical_candles.py").read_text()
# Copy this <!-- INSERT_coinbase_fetch_historical_candles_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="coinbase_fetch_historical_candles.md", content=code, output_type="python")
```

    ✅ Exported and tracked: coinbase_fetch_historical_candles.md



```python
from coinbase_pull_data import coinbase_pull_data
code = Path(SOURCE_DIR / "coinbase_pull_data.py").read_text()
# Copy this <!-- INSERT_coinbase_pull_data_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="coinbase_pull_data.md", content=code, output_type="python")
```

    ✅ Exported and tracked: coinbase_pull_data.md



```python
from df_info import df_info
code = Path(SOURCE_DIR / "df_info.py").read_text()
# Copy this <!-- INSERT_df_info_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="df_info.md", content=code, output_type="python")
```

    ✅ Exported and tracked: df_info.md



```python
from df_info_markdown import df_info_markdown
code = Path(SOURCE_DIR / "df_info_markdown.py").read_text()
# Copy this <!-- INSERT_df_info_markdown_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="df_info_markdown.md", content=code, output_type="python")
```

    ✅ Exported and tracked: df_info_markdown.md



```python
from export_track_md_deps import export_track_md_deps
code = Path(SOURCE_DIR / "export_track_md_deps.py").read_text()
# Copy this <!-- INSERT_export_track_md_deps_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="export_track_md_deps.md", content=code, output_type="python")
```

    ✅ Exported and tracked: export_track_md_deps.md



```python
from load_api_keys import load_api_keys
code = Path(SOURCE_DIR / "load_api_keys.py").read_text()
# Copy this <!-- INSERT_load_api_keys_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="load_api_keys.md", content=code, output_type="python")
```

    ✅ Exported and tracked: load_api_keys.md



```python
from load_data import load_data
code = Path(SOURCE_DIR / "load_data.py").read_text()
# Copy this <!-- INSERT_load_data_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="load_data.md", content=code, output_type="python")
```

    ✅ Exported and tracked: load_data.md



```python
from pandas_set_decimal_places import pandas_set_decimal_places
code = Path(SOURCE_DIR / "pandas_set_decimal_places.py").read_text()
# Copy this <!-- INSERT_pandas_set_decimal_places_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="pandas_set_decimal_places.md", content=code, output_type="python")
```

    ✅ Exported and tracked: pandas_set_decimal_places.md



```python
from plot_bar_returns_ffr_change import plot_bar_returns_ffr_change
code = Path(SOURCE_DIR / "plot_bar_returns_ffr_change.py").read_text()
# Copy this <!-- INSERT_plot_bar_returns_ffr_change_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="plot_bar_returns_ffr_change.md", content=code, output_type="python")
```

    ✅ Exported and tracked: plot_bar_returns_ffr_change.md



```python
from plot_histogram import plot_histogram
code = Path(SOURCE_DIR / "plot_histogram.py").read_text()
# Copy this <!-- INSERT_plot_histogram_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="plot_histogram.md", content=code, output_type="python")
```

    ✅ Exported and tracked: plot_histogram.md



```python
from plot_scatter import plot_scatter
code = Path(SOURCE_DIR / "plot_scatter.py").read_text()
# Copy this <!-- INSERT_plot_scatter_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="plot_scatter.md", content=code, output_type="python")
```

    ✅ Exported and tracked: plot_scatter.md



```python
from plot_scatter_regression_ffr_vs_returns import plot_scatter_regression_ffr_vs_returns
code = Path(SOURCE_DIR / "plot_scatter_regression_ffr_vs_returns.py").read_text()
# Copy this <!-- INSERT_plot_scatter_regression_ffr_vs_returns_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="plot_scatter_regression_ffr_vs_returns.md", content=code, output_type="python")
```

    ✅ Exported and tracked: plot_scatter_regression_ffr_vs_returns.md



```python
from plot_stats import plot_stats
code = Path(SOURCE_DIR / "plot_stats.py").read_text()
# Copy this <!-- INSERT_plot_stats_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="plot_stats.md", content=code, output_type="python")
```

    ✅ Exported and tracked: plot_stats.md



```python
from plot_timeseries import plot_timeseries
code = Path(SOURCE_DIR / "plot_timeseries.py").read_text()
# Copy this <!-- INSERT_plot_timeseries_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="plot_timeseries.md", content=code, output_type="python")
```

    ✅ Exported and tracked: plot_timeseries.md



```python
from plot_vix_with_trades import plot_vix_with_trades
code = Path(SOURCE_DIR / "plot_vix_with_trades.py").read_text()
# Copy this <!-- INSERT_plot_vix_with_trades_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="plot_vix_with_trades.md", content=code, output_type="python")
```

    ✅ Exported and tracked: plot_vix_with_trades.md



```python
from polygon_fetch_full_history import polygon_fetch_full_history
code = Path(SOURCE_DIR / "polygon_fetch_full_history.py").read_text()
# Copy this <!-- INSERT_polygon_fetch_full_history_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="polygon_fetch_full_history.md", content=code, output_type="python")
```

    ✅ Exported and tracked: polygon_fetch_full_history.md



```python
from polygon_pull_data import polygon_pull_data
code = Path(SOURCE_DIR / "polygon_pull_data.py").read_text()
# Copy this <!-- INSERT_polygon_pull_data_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="polygon_pull_data.md", content=code, output_type="python")
```

    ✅ Exported and tracked: polygon_pull_data.md



```python
from run_linear_regression import run_linear_regression
code = Path(SOURCE_DIR / "run_linear_regression.py").read_text()
# Copy this <!-- INSERT_run_linear_regression_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="run_linear_regression.md", content=code, output_type="python")
```

    ✅ Exported and tracked: run_linear_regression.md



```python
from strategy_harry_brown_perm_port import strategy_harry_brown_perm_port
code = Path(SOURCE_DIR / "strategy_harry_brown_perm_port.py").read_text()
# Copy this <!-- INSERT_strategy_harry_brown_perm_port_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="strategy_harry_brown_perm_port.md", content=code, output_type="python")
```

    ✅ Exported and tracked: strategy_harry_brown_perm_port.md



```python
from summary_stats import summary_stats
code = Path(SOURCE_DIR / "summary_stats.py").read_text()
# Copy this <!-- INSERT_summary_stats_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="summary_stats.md", content=code, output_type="python")
```

    ✅ Exported and tracked: summary_stats.md



```python
from yf_pull_data import yf_pull_data
code = Path(SOURCE_DIR / "yf_pull_data.py").read_text()
# Copy this <!-- INSERT_yf_pull_data_HERE --> to index_temp.md
export_track_md_deps(dep_file=dep_file, md_filename="yf_pull_data.md", content=code, output_type="python")
```

    ✅ Exported and tracked: yf_pull_data.md

