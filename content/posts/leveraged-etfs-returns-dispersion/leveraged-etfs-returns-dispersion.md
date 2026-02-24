 # How do the long-term returns of leveraged ETFs diverge from their underlying index?

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
import pandas_datareader.data as web

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
    5: /home/jared/python-virtual-envs/general-venv-p313/lib/python3.13/site-packages/setuptools/_vendor
    6: /home/jared/Cloud_Storage/Dropbox/Websites/jaredszajkowski.github.io_congo/src


 ## Track Index Dependencies


```python
# Create file to track markdown dependencies
dep_file = Path("index_dep.txt")
dep_file.write_text("")

```




    0



 ## Python Functions


```python
from build_index import build_index
from df_info import df_info
from df_info_markdown import df_info_markdown
from export_track_md_deps import export_track_md_deps
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_histogram import plot_histogram
from plot_scatter import plot_scatter
from plot_timeseries import plot_timeseries
from run_linear_regression import run_linear_regression
from sm_ols_summary_markdown import sm_ols_summary_markdown
from summary_stats import summary_stats
from yf_pull_data import yf_pull_data

```


```python
# Set decimal places
pandas_set_decimal_places(2)
```

 ## Data Overview

## QQQ & TQQQ

 ### Acquire & Plot Data (QQQ)


```python
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

```

    [*********************100%***********************]  1 of 1 completed

    


    The first and last date of data for QQQ is: 



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1999-03-10</th>
      <td>43.13</td>
      <td>43.21</td>
      <td>42.47</td>
      <td>43.18</td>
      <td>5232000</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2026-02-04</th>
      <td>605.75</td>
      <td>615.10</td>
      <td>600.47</td>
      <td>615.02</td>
      <td>81850700</td>
    </tr>
  </tbody>
</table>
</div>


    Yahoo Finance data complete for QQQ
    --------------------



```python
plot_timeseries(
    price_df=qqq,
    plot_start_date=qqq.index.min(),
    plot_end_date=qqq.index.max(),
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

```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_14_0.png)
    



```python
# Copy this <!-- INSERT_01_QQQ_Price_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="01_QQQ_Price.md", 
    content=df_info_markdown(df=qqq, decimal_places=2),
    output_type="markdown",
)

```

    ✅ Exported and tracked: 01_QQQ_Price.md


 ### Acquire & Plot Data (TQQQ)


```python
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

```

    [*********************100%***********************]  1 of 1 completed

    


    The first and last date of data for TQQQ is: 



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2010-02-11</th>
      <td>0.21</td>
      <td>0.21</td>
      <td>0.19</td>
      <td>0.19</td>
      <td>6912000</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2026-02-04</th>
      <td>49.76</td>
      <td>52.15</td>
      <td>48.43</td>
      <td>52.14</td>
      <td>142536200</td>
    </tr>
  </tbody>
</table>
</div>


    Yahoo Finance data complete for TQQQ
    --------------------



```python
plot_timeseries(
    price_df=tqqq,
    plot_start_date=tqqq.index.min(),
    plot_end_date=tqqq.index.max(),
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

```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_18_0.png)
    



```python
# Copy this <!-- INSERT_02_TQQQ_Price_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="02_TQQQ_Price.md", 
    content=df_info_markdown(df=qqq, decimal_places=2),
    output_type="markdown",
)

```

    ✅ Exported and tracked: 02_TQQQ_Price.md


 ### Calculate & Plot Cumulative Returns, Rolling Returns, and Drawdowns (QQQ & TQQQ)


```python
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
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        qqq_tqqq_aligned[f"{etf}_Rolling_Return_{period_name}"] = (
            qqq_tqqq_aligned[f"{etf}_Close"].pct_change(periods=window)
        )

```


```python
# Copy this <!-- INSERT_03_QQQ_TQQQ_Aligned_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="03_QQQ_TQQQ_Aligned.md", 
    content=df_info_markdown(df=qqq_tqqq_aligned, decimal_places=2),
    output_type="markdown",
)

```

    ✅ Exported and tracked: 03_QQQ_TQQQ_Aligned.md



```python
plot_timeseries(
    price_df=qqq_tqqq_aligned,
    plot_start_date=qqq_tqqq_aligned.index.min(),
    plot_end_date=qqq_tqqq_aligned.index.max(),
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

```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_23_0.png)
    



```python
plot_timeseries(
    price_df=qqq_tqqq_aligned,
    plot_start_date=qqq_tqqq_aligned.index.min(),
    plot_end_date=qqq_tqqq_aligned.index.max(),
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

```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_24_0.png)
    


### Summary Statistics (QQQ & TQQQ)



```python
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

```


```python
# Copy this <!-- INSERT_03_QQQ_TQQQ_Summary_Stats_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="03_QQQ_TQQQ_Summary_Stats.md", 
    content=sum_stats.to_markdown(floatfmt=".3f"),
    output_type="markdown",
)

```

    ✅ Exported and tracked: 03_QQQ_TQQQ_Summary_Stats.md


### Plot Returns & Verify Beta (QQQ & TQQQ)


```python
plot_scatter(
    df=qqq_tqqq_aligned,
    x_plot_column="QQQ_Return",
    y_plot_column="TQQQ_Return",
    title="QQQ & TQQQ Returns",
    x_label="QQQ Return",
    x_format="Decimal",
    x_format_decimal_places=2,
    x_tick_spacing="Auto",
    x_tick_rotation=45,
    y_label="TQQQ Return",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    plot_OLS_regression_line=True,
    plot_Ridge_regression_line=True,
    plot_RidgeCV_regression_line=True,
    regression_constant=True,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name=f"03_QQQ_TQQQ_Returns_Scatter",
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_29_0.png)
    



```python
model = run_linear_regression(
    df=qqq_tqqq_aligned,
    x_plot_column="QQQ_Return",
    y_plot_column="TQQQ_Return",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)
```


```python
# Copy this <!-- INSERT_03_QQQ_TQQQ_Regression_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="03_QQQ_TQQQ_Regression.md", 
    content=sm_ols_summary_markdown(result=model, file_path="03_QQQ_TQQQ_Regression.md"),
    output_type="text",
)
```

    ✅ Exported and tracked: 03_QQQ_TQQQ_Regression.md


### Plot Rolling Returns (QQQ & TQQQ)


```python
# Create a dataframe to hold rolling returns stats
rolling_returns_stats = pd.DataFrame()

for period_name, window in rolling_windows.items():
    plot_histogram(
        df=qqq_tqqq_aligned,
        plot_columns=[f"QQQ_Rolling_Return_{period_name}", f"TQQQ_Rolling_Return_{period_name}"],
        title=f"QQQ & TQQQ {period_name} Rolling Returns Histogram",
        x_label="Rolling Return",
        x_tick_spacing="Auto",
        x_tick_rotation=45,
        y_label="# Of Datapoints",
        y_tick_spacing="Auto",
        grid=True,
        legend=True,
        export_plot=True,
        plot_file_name=f"04_Rolling_Returns_{period_name}_Histogram",
    )

    plot_scatter(
        df=qqq_tqqq_aligned,
        x_plot_column=f"QQQ_Rolling_Return_{period_name}",
        y_plot_column=f"TQQQ_Rolling_Return_{period_name}",
        title=f"QQQ & TQQQ {period_name} Rolling Returns Scatter",
        x_label="QQQ Rolling Return",
        x_format="Decimal",
        x_format_decimal_places=2,
        x_tick_spacing="Auto",
        x_tick_rotation=45,
        y_label="TQQQ Rolling Return",
        y_format="Decimal",
        y_format_decimal_places=2,
        y_tick_spacing="Auto",
        plot_OLS_regression_line=True,
        plot_Ridge_regression_line=False,
        plot_RidgeCV_regression_line=True,
        regression_constant=True,
        grid=True,
        legend=True,
        export_plot=True,
        plot_file_name=f"04_Rolling_Returns_{period_name}_Scatter",
    )

    # Run OLS regression with statsmodels
    model = run_linear_regression(
        df=qqq_tqqq_aligned,
        x_plot_column=f"QQQ_Rolling_Return_{period_name}",
        y_plot_column=f"TQQQ_Rolling_Return_{period_name}",
        regression_model="OLS-statsmodels",
        regression_constant=True,
    )

    # Copy this <!-- INSERT_04_Rolling_Returns_{period_name}_Regression_HERE --> to index_temp.md
    export_track_md_deps(
        dep_file=dep_file, 
        md_filename=f"04_Rolling_Returns_{period_name}_Regression.md", 
        content=sm_ols_summary_markdown(result=model, file_path=f"04_Rolling_Returns_{period_name}_Regression.md"),
        output_type="text",
    )

    # Add the regression results to the rolling returns stats dataframe
    intercept = model.params[0]
    slope = model.params[1]
    r_squared = model.rsquared
    rolling_returns_slope_int = pd.DataFrame({"Period": period_name, "Intercept": [intercept], "Slope": [slope], "R_Squared": [r_squared]})
    rolling_returns_stats = pd.concat([rolling_returns_stats, rolling_returns_slope_int])
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_0.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_1.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_1d_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_3.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_4.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_1w_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_6.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_7.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_1m_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_9.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_10.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_3m_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_12.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_13.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_6m_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_15.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_16.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_1y_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_18.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_19.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_2y_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_21.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_22.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_3y_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_24.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_25.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_4y_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_27.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_33_28.png)
    


    ✅ Exported and tracked: 04_Rolling_Returns_5y_Regression.md


### Rolling Returns Deviation (QQQ & TQQQ)


```python
rolling_returns_stats["Return_Deviation_From_3x"] = rolling_returns_stats["Slope"] - 3.0
```


```python
# Copy this <!-- INSERT_04_Rolling_Returns_Stats_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="04_Rolling_Returns_Stats.md", 
    content=rolling_returns_stats.set_index("Period").to_markdown(floatfmt=".3f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 04_Rolling_Returns_Stats.md



```python
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_column="Return_Deviation_From_3x",
    title="TQQQ Deviation from Perfect 3x Leverage by Time Period",
    x_label="Rolling Return Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_rotation=0,
    y_label="Deviation from 3x Leverage",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    plot_OLS_regression_line=False,
    plot_Ridge_regression_line=False,
    plot_RidgeCV_regression_line=False,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="04_Rolling_Returns_Deviation_from_3x",
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_37_0.png)
    


### Rolling Returns Following Drawdowns (QQQ & TQQQ)


```python
# Copy DataFrame
qqq_tqqq_aligned_future = qqq_tqqq_aligned.copy()

# Create a list of drawdown levels to analyze
# drawdown_levels = [-0.10, -0.20, -0.30, -0.40, -0.50, -0.60, -0.70, -0.80]
drawdown_levels = [-0.10, -0.50]

# Shift the rolling return columns by the number of days in the rolling window to get the returns following the drawdown
for etf in etfs:
    for period_name, window in rolling_windows.items():
        qqq_tqqq_aligned_future[f"{etf}_Rolling_Future_Return_{period_name}"] = qqq_tqqq_aligned_future[f"{etf}_Rolling_Return_{period_name}"].shift(-window)
```


```python
# Create a dataframe to hold rolling returns stats
rolling_returns_stats = pd.DataFrame()

for drawdown in drawdown_levels:

    for period_name, window in rolling_windows.items():

        plot_histogram(
            df=qqq_tqqq_aligned_future[qqq_tqqq_aligned_future["TQQQ_Drawdown"] <= drawdown],
            plot_columns=[f"QQQ_Rolling_Future_Return_{period_name}", f"TQQQ_Rolling_Future_Return_{period_name}"],
            title=f"QQQ & TQQQ {period_name} Rolling Future Returns Post {drawdown} Drawdown Histogram",
            x_label="Rolling Return",
            x_tick_spacing="Auto",
            x_tick_rotation=45,
            y_label="# Of Datapoints",
            y_tick_spacing="Auto",
            grid=True,
            legend=True,
            export_plot=True,
            plot_file_name=f"05_Rolling_Future_Returns_{period_name}_Post_{drawdown}_Drawdown_Histogram",
        )

        plot_scatter(
            df=qqq_tqqq_aligned_future[qqq_tqqq_aligned_future["TQQQ_Drawdown"] <= drawdown],
            x_plot_column=f"QQQ_Rolling_Future_Return_{period_name}",
            y_plot_column=f"TQQQ_Rolling_Future_Return_{period_name}",
            title=f"QQQ & TQQQ {period_name} Rolling Future Returns Post {drawdown} Drawdown Scatter",
            x_label="QQQ Rolling Return",
            x_format="Decimal",
            x_format_decimal_places=2,
            x_tick_spacing="Auto",
            x_tick_rotation=45,
            y_label="TQQQ Rolling Return",
            y_format="Decimal",
            y_format_decimal_places=2,
            y_tick_spacing="Auto",
            plot_OLS_regression_line=True,
            plot_Ridge_regression_line=False,
            plot_RidgeCV_regression_line=True,
            regression_constant=True,
            grid=True,
            legend=True,
            export_plot=True,
            plot_file_name=f"05_Rolling_Future_Returns_{period_name}_Post_{drawdown}_Drawdown_Scatter",
        )

        # Run OLS regression with statsmodels
        model = run_linear_regression(
            df=qqq_tqqq_aligned_future[qqq_tqqq_aligned_future["TQQQ_Drawdown"] <= drawdown],
            x_plot_column=f"QQQ_Rolling_Future_Return_{period_name}",
            y_plot_column=f"TQQQ_Rolling_Future_Return_{period_name}",
            regression_model="OLS-statsmodels",
            regression_constant=True,
        )

        # Copy this <!-- INSERT_05_Rolling_Future_Returns_{period_name}_Regression_HERE --> to index_temp.md
        export_track_md_deps(
            dep_file=dep_file, 
            md_filename=f"05_Rolling_Future_Returns_{period_name}_Post_{drawdown}_Drawdown_Regression.md", 
            content=sm_ols_summary_markdown(result=model, file_path=f"05_Rolling_Future_Returns_{period_name}_Post_{drawdown}_Drawdown_Regression.md"),
            output_type="text",
        )

        # Add the regression results to the rolling returns stats dataframe
        intercept = model.params[0]
        slope = model.params[1]
        r_squared = model.rsquared
        rolling_returns_slope_int = pd.DataFrame({"Drawdown": drawdown,"Period": period_name, "Intercept": [intercept], "Slope": [slope], "R_Squared": [r_squared]})
        rolling_returns_stats = pd.concat([rolling_returns_stats, rolling_returns_slope_int])
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_0.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_1.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_1d_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_3.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_4.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_1w_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_6.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_7.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_1m_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_9.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_10.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_3m_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_12.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_13.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_6m_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_15.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_16.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_1y_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_18.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_19.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_2y_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_21.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_22.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_3y_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_24.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_25.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_4y_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_27.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_28.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_5y_Post_-0.1_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_30.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_31.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_1d_Post_-0.5_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_33.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_34.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_1w_Post_-0.5_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_36.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_37.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_1m_Post_-0.5_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_39.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_40.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_3m_Post_-0.5_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_42.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_43.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_6m_Post_-0.5_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_45.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_46.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_1y_Post_-0.5_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_48.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_49.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_2y_Post_-0.5_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_51.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_52.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_3y_Post_-0.5_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_54.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_55.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_4y_Post_-0.5_Drawdown_Regression.md



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_57.png)
    



    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_40_58.png)
    


    ✅ Exported and tracked: 05_Rolling_Future_Returns_5y_Post_-0.5_Drawdown_Regression.md


### Rolling Returns Following Drawdowns Deviation (QQQ & TQQQ)


```python
rolling_returns_stats["Return_Deviation_From_3x"] = rolling_returns_stats["Slope"] - 3.0
```


```python
# Copy this <!-- INSERT_04_Rolling_Returns_Stats_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="04_Rolling_Returns_Stats.md", 
    content=rolling_returns_stats.set_index("Period").to_markdown(floatfmt=".3f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: 04_Rolling_Returns_Stats.md



```python
plot_scatter(
    df=rolling_returns_stats,
    x_plot_column="Period",
    y_plot_column="Return_Deviation_From_3x",
    title="TQQQ Deviation from Perfect 3x Leverage by Time Period",
    x_label="Rolling Return Time Period",
    x_format="String",
    x_format_decimal_places=0,
    x_tick_spacing=1,
    x_tick_rotation=0,
    y_label="Deviation from 3x Leverage",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    plot_OLS_regression_line=False,
    plot_Ridge_regression_line=False,
    plot_RidgeCV_regression_line=False,
    regression_constant=False,
    grid=True,
    legend=True,
    export_plot=True,
    plot_file_name="04_Rolling_Returns_Deviation_from_3x",
)
```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_44_0.png)
    



```python

```


```python

```

## SPY & UPRO

 ### Acquire & Plot Data (SPY)


```python
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="SPY",
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)

spy = load_data(
    base_directory=DATA_DIR,
    ticker="SPY",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "SPY_Close", etc.
spy = spy.rename(columns={
    "Close": "SPY_Close", 
    "High": "SPY_High", 
    "Low": "SPY_Low", 
    "Open": "SPY_Open", 
    "Volume": "SPY_Volume"
})

```

    [*********************100%***********************]  1 of 1 completed

    


    The first and last date of data for SPY is: 



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1993-01-29</th>
      <td>24.24</td>
      <td>24.26</td>
      <td>24.14</td>
      <td>24.26</td>
      <td>1003200</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2026-02-05</th>
      <td>677.62</td>
      <td>683.69</td>
      <td>675.79</td>
      <td>680.94</td>
      <td>113140100</td>
    </tr>
  </tbody>
</table>
</div>


    Yahoo Finance data complete for SPY
    --------------------



```python
plot_timeseries(
    price_df=spy,
    plot_start_date=spy.index.min(),
    plot_end_date=spy.index.max(),
    plot_columns=["SPY_Close"],
    title="SPY Close Price",
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
    plot_file_name="05_SPY_Price",
)

```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_50_0.png)
    



```python
# Copy this <!-- INSERT_05_SPY_Price_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file,
    md_filename="05_SPY_Price.md", 
    content=df_info_markdown(df=spy, decimal_places=2),
    output_type="markdown",
)

```

    ✅ Exported and tracked: 05_SPY_Price.md


### Acquire & Plot Data (UPRO)



```python
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="UPRO",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds", 
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)

upro = load_data(
    base_directory=DATA_DIR,
    ticker="UPRO",
    source="Yahoo_Finance", 
    asset_class="Exchange_Traded_Funds",
    timeframe="Daily",
    file_format="pickle",
)

# Rename columns to "UPRO_Close", etc.
upro = upro.rename(columns={
    "Close": "UPRO_Close", 
    "High": "UPRO_High", 
    "Low": "UPRO_Low", 
    "Open": "UPRO_Open", 
    "Volume": "UPRO_Volume"
})

```

    [*********************100%***********************]  1 of 1 completed

    


    The first and last date of data for UPRO is: 



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2009-06-25</th>
      <td>1.13</td>
      <td>1.14</td>
      <td>1.06</td>
      <td>1.06</td>
      <td>2577600</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Close</th>
      <th>High</th>
      <th>Low</th>
      <th>Open</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2026-02-05</th>
      <td>112.03</td>
      <td>115.19</td>
      <td>111.20</td>
      <td>113.79</td>
      <td>8115300</td>
    </tr>
  </tbody>
</table>
</div>


    Yahoo Finance data complete for UPRO
    --------------------



```python
plot_timeseries(
    price_df=upro,
    plot_start_date=upro.index.min(),
    plot_end_date=upro.index.max(),
    plot_columns=["UPRO_Close"],
    title="UPRO Close Price",
    x_label="Date",
    x_format="Year",
    x_tick_rotation=45,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing=10,
    grid=True,
    legend=False,
    export_plot=True,
    plot_file_name="06_UPRO_Price",
)

```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_54_0.png)
    



```python
# Copy this <!-- INSERT_06_UPRO_Price_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="06_UPRO_Price.md", 
    content=df_info_markdown(df=upro, decimal_places=2),
    output_type="markdown",
)

```

    ✅ Exported and tracked: 06_UPRO_Price.md


 ### Calculate & Plot Cumulative Returns, Rolling Returns, and Drawdowns (SPY & UPRO)


```python
etfs = ["SPY", "UPRO"]

# Merge dataframes and drop rows with missing values
spy_upro_aligned = upro.merge(spy, left_index=True, right_index=True, how='left')
spy_upro_aligned = spy_upro_aligned.dropna()

# Calculate cumulative returns
for etf in etfs:
    spy_upro_aligned[f"{etf}_Return"] = spy_upro_aligned[f"{etf}_Close"].pct_change()
    spy_upro_aligned[f"{etf}_Cumulative_Return"] = (1 + spy_upro_aligned[f"{etf}_Return"]).cumprod() - 1
    spy_upro_aligned[f"{etf}_Cumulative_Return_Plus_One"] = 1 + spy_upro_aligned[f"{etf}_Cumulative_Return"]
    spy_upro_aligned[f"{etf}_Rolling_Max"] = spy_upro_aligned[f"{etf}_Cumulative_Return_Plus_One"].cummax()
    spy_upro_aligned[f"{etf}_Drawdown"] = spy_upro_aligned[f"{etf}_Cumulative_Return_Plus_One"] / spy_upro_aligned[f"{etf}_Rolling_Max"] - 1
    spy_upro_aligned.drop(columns=[f"{etf}_Cumulative_Return_Plus_One", f"{etf}_Rolling_Max"], inplace=True)

# Define rolling windows in trading days
rolling_windows = {
    '1d': 1,      # 1 day
    '1w': 5,      # 1 week (5 trading days)
    '1m': 21,     # 1 month (~21 trading days)
    '3m': 63,     # 3 months (~63 trading days)
    '6m': 126,    # 6 months (~126 trading days)
    '1y': 252,    # 1 year (~252 trading days)
    '2y': 504,    # 2 years (~504 trading days)
    '3y': 756,    # 3 years (~756 trading days)
    '4y': 1008,   # 4 years (~1008 trading days)
    '5y': 1260,   # 5 years (~1260 trading days)
}

# Calculate rolling returns for each ETF and each window
for etf in etfs:
    for period_name, window in rolling_windows.items():
        spy_upro_aligned[f"{etf}_Rolling_Return_{period_name}"] = (
            spy_upro_aligned[f"{etf}_Close"].pct_change(periods=window)
        )

```


```python
# Copy this <!-- INSERT_07_SPY_UPRO_Aligned_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="07_SPY_UPRO_Aligned.md", 
    content=df_info_markdown(df=spy_upro_aligned, decimal_places=2),
    output_type="markdown",
)

```

    ✅ Exported and tracked: 07_SPY_UPRO_Aligned.md



```python
plot_timeseries(
    price_df=spy_upro_aligned,
    plot_start_date=spy_upro_aligned.index.min(),
    plot_end_date=spy_upro_aligned.index.max(),
    plot_columns=["SPY_Cumulative_Return", "UPRO_Cumulative_Return"],
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
    plot_file_name="07_Cumulative_Returns",
)

```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_59_0.png)
    



```python
plot_timeseries(
    price_df=spy_upro_aligned,
    plot_start_date=spy_upro_aligned.index.min(),
    plot_end_date=spy_upro_aligned.index.max(),
    plot_columns=["SPY_Drawdown", "UPRO_Drawdown"],
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
    plot_file_name="07_Drawdowns",
)

```


    
![png](leveraged-etfs-returns-dispersion_files/leveraged-etfs-returns-dispersion_60_0.png)
    


### Summary Statistics (SPY & UPRO)



```python
spy_sum_stats = summary_stats(
    fund_list=["SPY"],
    df=spy_upro_aligned[["SPY_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

upro_sum_stats = summary_stats(
    fund_list=["UPRO"],
    df=spy_upro_aligned[["UPRO_Return"]],
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

sum_stats = pd.concat([spy_sum_stats, upro_sum_stats])

```


```python
# Copy this <!-- INSERT_07_SPY_UPRO_Summary_Stats_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file,
    md_filename="07_SPY_UPRO_Summary_Stats.md", 
    content=sum_stats.to_markdown(floatfmt=".3f"),
    output_type="markdown",
)

```

    ✅ Exported and tracked: 07_SPY_UPRO_Summary_Stats.md

