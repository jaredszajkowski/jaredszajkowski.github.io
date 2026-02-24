# Data Pipelining With Polygon

## Python Imports


```python
# Standard Library
import datetime
import io
import os
import random
import sys
import time
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
from polygon_fetch_full_history import polygon_fetch_full_history
from polygon_pull_data import polygon_pull_data
```

## Function Usage

### Polygon Fetch Full History


```python
from load_api_keys import load_api_keys
from massive import RESTClient

# Load API keys from the environment
api_keys = load_api_keys()

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Open client connection
client = RESTClient(api_key=api_keys["POLYGON_KEY"])

# Create an empty DataFrame
df = pd.DataFrame({
    'Date': pd.Series(dtype="datetime64[ns]"),
    'open': pd.Series(dtype="float64"),
    'high': pd.Series(dtype="float64"),
    'low': pd.Series(dtype="float64"),
    'close': pd.Series(dtype="float64"),
    'volume': pd.Series(dtype="float64"),
    'vwap': pd.Series(dtype="float64"),
    'transactions': pd.Series(dtype="int64"),
    'otc': pd.Series(dtype="object")
})

# Example usage - minute
df = polygon_fetch_full_history(
    client=client,
    ticker="AMZN",
    timespan="day",
    multiplier=1,
    adjusted=True,
    existing_history_df=df,
    current_start=datetime(2025, 1, 1),
    free_tier=True,
    verbose=True,
)

time.sleep(12)  # Sleep for 2 seconds to avoid hitting rate limits
```

    Pulling day data for 2025-01-01 00:00:00 thru 2025-06-30 00:00:00 for AMZN...
    


    New data:
                       Date     open     high      low   close       volume  \
    0   2025-01-02 05:00:00  222.030  225.150  218.190  220.22   33956579.0   
    1   2025-01-03 05:00:00  222.505  225.360  221.620  224.19   27515606.0   
    2   2025-01-06 05:00:00  226.780  228.835  224.840  227.61   31849831.0   
    3   2025-01-07 05:00:00  227.900  228.381  221.460  222.11   28084164.0   
    4   2025-01-08 05:00:00  223.185  223.520  220.200  222.13   25033292.0   
    ..                  ...      ...      ...      ...     ...          ...   
    117 2025-06-24 04:00:00  212.135  214.340  211.045  212.77   38378757.0   
    118 2025-06-25 04:00:00  214.615  216.030  211.110  211.99   31755698.0   
    119 2025-06-26 04:00:00  213.120  218.035  212.010  217.12   50480814.0   
    120 2025-06-27 04:00:00  219.920  223.300  216.740  223.30  119217138.0   
    121 2025-06-30 04:00:00  223.520  223.820  219.120  219.39   58887780.0   
    
             vwap  transactions   otc  
    0    221.2745        449631  None  
    1    223.7050        346976  None  
    2    227.0921        410686  None  
    3    223.4033        379570  None  
    4    222.0414        325539  None  
    ..        ...           ...   ...  
    117  213.1129        459901  None  
    118  212.8066        417565  None  
    119  216.0944        572822  None  
    120  221.7267        750603  None  
    121  220.6316        673189  None  
    
    [122 rows x 9 columns]
    Combined data:
                       Date     open     high      low   close       volume  \
    0   2025-01-02 05:00:00  222.030  225.150  218.190  220.22   33956579.0   
    1   2025-01-03 05:00:00  222.505  225.360  221.620  224.19   27515606.0   
    2   2025-01-06 05:00:00  226.780  228.835  224.840  227.61   31849831.0   
    3   2025-01-07 05:00:00  227.900  228.381  221.460  222.11   28084164.0   
    4   2025-01-08 05:00:00  223.185  223.520  220.200  222.13   25033292.0   
    ..                  ...      ...      ...      ...     ...          ...   
    117 2025-06-24 04:00:00  212.135  214.340  211.045  212.77   38378757.0   
    118 2025-06-25 04:00:00  214.615  216.030  211.110  211.99   31755698.0   
    119 2025-06-26 04:00:00  213.120  218.035  212.010  217.12   50480814.0   
    120 2025-06-27 04:00:00  219.920  223.300  216.740  223.30  119217138.0   
    121 2025-06-30 04:00:00  223.520  223.820  219.120  219.39   58887780.0   
    
             vwap  transactions   otc  
    0    221.2745        449631  None  
    1    223.7050        346976  None  
    2    227.0921        410686  None  
    3    223.4033        379570  None  
    4    222.0414        325539  None  
    ..        ...           ...   ...  
    117  213.1129        459901  None  
    118  212.8066        417565  None  
    119  216.0944        572822  None  
    120  221.7267        750603  None  
    121  220.6316        673189  None  
    
    [122 rows x 9 columns]
    Sleeping for 12 seconds to avoid hitting API rate limits...
    


    Pulling day data for 2025-06-29 04:00:00 thru 2025-12-26 04:00:00 for AMZN...
    
    New data:
                       Date     open     high     low   close      volume  \
    0   2025-06-30 04:00:00  223.520  223.820  219.12  219.39  58887780.0   
    1   2025-07-01 04:00:00  219.500  221.875  217.93  220.46  39256830.0   
    2   2025-07-02 04:00:00  219.730  221.600  219.06  219.92  30894178.0   
    3   2025-07-03 04:00:00  221.820  224.010  221.36  223.41  29632353.0   
    4   2025-07-07 04:00:00  223.000  224.290  222.37  223.47  36604139.0   
    ..                  ...      ...      ...     ...     ...         ...   
    120 2025-12-18 05:00:00  225.705  229.225  224.41  226.76  50272419.0   
    121 2025-12-19 05:00:00  226.760  229.125  225.58  227.35  85544374.0   
    122 2025-12-22 05:00:00  228.610  229.480  226.71  228.43  32261329.0   
    123 2025-12-23 05:00:00  229.055  232.445  228.73  232.14  29230233.0   
    124 2025-12-24 05:00:00  232.130  232.950  231.33  232.38  11420543.0   
    
             vwap  transactions   otc  
    0    220.6316        673189  None  
    1    220.1508        544150  None  
    2    220.2103        429633  None  
    3    222.8867        364422  None  
    4    223.4121        513469  None  
    ..        ...           ...   ...  
    120  226.8047        511173  None  
    121  227.4217        474053  None  
    122  228.1120        466788  None  
    123  231.3567        435724  None  
    124  232.3354        193852  None  
    
    [125 rows x 9 columns]
    Combined data:
                       Date     open     high     low   close      volume  \
    0   2025-01-02 05:00:00  222.030  225.150  218.19  220.22  33956579.0   
    1   2025-01-03 05:00:00  222.505  225.360  221.62  224.19  27515606.0   
    2   2025-01-06 05:00:00  226.780  228.835  224.84  227.61  31849831.0   
    3   2025-01-07 05:00:00  227.900  228.381  221.46  222.11  28084164.0   
    4   2025-01-08 05:00:00  223.185  223.520  220.20  222.13  25033292.0   
    ..                  ...      ...      ...     ...     ...         ...   
    241 2025-12-18 05:00:00  225.705  229.225  224.41  226.76  50272419.0   
    242 2025-12-19 05:00:00  226.760  229.125  225.58  227.35  85544374.0   
    243 2025-12-22 05:00:00  228.610  229.480  226.71  228.43  32261329.0   
    244 2025-12-23 05:00:00  229.055  232.445  228.73  232.14  29230233.0   
    245 2025-12-24 05:00:00  232.130  232.950  231.33  232.38  11420543.0   
    
             vwap  transactions   otc  
    0    221.2745        449631  None  
    1    223.7050        346976  None  
    2    227.0921        410686  None  
    3    223.4033        379570  None  
    4    222.0414        325539  None  
    ..        ...           ...   ...  
    241  226.8047        511173  None  
    242  227.4217        474053  None  
    243  228.1120        466788  None  
    244  231.3567        435724  None  
    245  232.3354        193852  None  
    
    [246 rows x 9 columns]
    Sleeping for 12 seconds to avoid hitting API rate limits...
    


    Pulling day data for 2025-12-23 05:00:00 thru 2026-06-21 05:00:00 for AMZN...
    
    New data:
                      Date     open     high     low   close      volume  \
    0  2025-12-23 05:00:00  229.055  232.445  228.73  232.14  29230233.0   
    1  2025-12-24 05:00:00  232.130  232.950  231.33  232.38  11420543.0   
    2  2025-12-26 05:00:00  232.035  232.990  231.18  232.52  15994726.0   
    3  2025-12-29 05:00:00  231.940  232.600  230.77  232.07  19797909.0   
    4  2025-12-30 05:00:00  231.205  232.770  230.20  232.53  21910453.0   
    5  2025-12-31 05:00:00  232.905  232.990  230.12  230.82  24383749.0   
    6  2026-01-02 05:00:00  231.340  235.458  224.70  226.50  51456229.0   
    7  2026-01-05 05:00:00  228.840  234.000  227.18  233.06  49733348.0   
    8  2026-01-06 05:00:00  232.100  243.180  232.07  240.93  53764677.0   
    9  2026-01-07 05:00:00  239.610  245.290  239.52  241.56  42236531.0   
    10 2026-01-08 05:00:00  243.060  246.410  241.88  246.29  39509844.0   
    11 2026-01-09 05:00:00  244.568  247.860  242.24  247.38  34559961.0   
    12 2026-01-12 05:00:00  246.730  248.940  245.96  246.47  35867770.0   
    13 2026-01-13 05:00:00  246.530  247.660  240.25  242.60  38371778.0   
    14 2026-01-14 05:00:00  241.150  241.280  236.22  236.65  41410578.0   
    15 2026-01-15 05:00:00  239.310  240.650  236.63  238.18  43003571.0   
    16 2026-01-16 05:00:00  239.085  239.570  236.41  239.12  45888283.0   
    17 2026-01-20 05:00:00  233.760  235.090  229.34  231.00  47737854.0   
    18 2026-01-21 05:00:00  231.085  232.300  226.88  231.31  47276090.0   
    19 2026-01-22 05:00:00  234.045  235.720  230.90  234.34  31913325.0   
    20 2026-01-23 05:00:00  234.955  240.450  234.57  239.16  33778478.0   
    
            vwap  transactions   otc  
    0   231.3567        435724  None  
    1   232.3354        193852  None  
    2   232.4647        278360  None  
    3   231.8925        352880  None  
    4   231.7815        322423  None  
    5   231.2767        322950  None  
    6   228.0134        750788  None  
    7   232.1786        678867  None  
    8   239.6475        767759  None  
    9   242.9662        623031  None  
    10  245.1880        537907  None  
    11  246.0666        487691  None  
    12  247.2996        520852  None  
    13  243.3866        559247  None  
    14  237.6446        582230  None  
    15  238.3037        567069  None  
    16  238.4963        424842  None  
    17  231.9376        749010  None  
    18  230.2750        654920  None  
    19  234.0045        447829  None  
    20  238.6065        482481  None  
    Combined data:
                       Date     open     high     low   close      volume  \
    0   2025-01-02 05:00:00  222.030  225.150  218.19  220.22  33956579.0   
    1   2025-01-03 05:00:00  222.505  225.360  221.62  224.19  27515606.0   
    2   2025-01-06 05:00:00  226.780  228.835  224.84  227.61  31849831.0   
    3   2025-01-07 05:00:00  227.900  228.381  221.46  222.11  28084164.0   
    4   2025-01-08 05:00:00  223.185  223.520  220.20  222.13  25033292.0   
    ..                  ...      ...      ...     ...     ...         ...   
    260 2026-01-16 05:00:00  239.085  239.570  236.41  239.12  45888283.0   
    261 2026-01-20 05:00:00  233.760  235.090  229.34  231.00  47737854.0   
    262 2026-01-21 05:00:00  231.085  232.300  226.88  231.31  47276090.0   
    263 2026-01-22 05:00:00  234.045  235.720  230.90  234.34  31913325.0   
    264 2026-01-23 05:00:00  234.955  240.450  234.57  239.16  33778478.0   
    
             vwap  transactions   otc  
    0    221.2745        449631  None  
    1    223.7050        346976  None  
    2    227.0921        410686  None  
    3    223.4033        379570  None  
    4    222.0414        325539  None  
    ..        ...           ...   ...  
    260  238.4963        424842  None  
    261  231.9376        749010  None  
    262  230.2750        654920  None  
    263  234.0045        447829  None  
    264  238.6065        482481  None  
    
    [265 rows x 9 columns]



```python
# Copy this <!-- INSERT_polygon_fetch_full_history_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="polygon_fetch_full_history.md", 
    content=df.head().to_markdown(floatfmt=".5f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: polygon_fetch_full_history.md


### Polygon Pull Data


```python
current_year = datetime.now().year
current_month = datetime.now().month
current_day = datetime.now().day

# Example usage - daily
df = polygon_pull_data(
    base_directory=DATA_DIR,
    ticker="AMZN",
    source="Polygon",
    asset_class="Equities",
    start_date=datetime(current_year - 2, current_month, current_day),
    timespan="day",
    multiplier=1,
    adjusted=True,
    force_existing_check=True,
    free_tier=True,
    verbose=True,
    excel_export=True,
    pickle_export=True,
    output_confirmation=True,
)

time.sleep(12)  # Sleep for 2 seconds to avoid hitting rate limits
```

    File found...updating the AMZN day data.
    Existing data:
                       Date     open    high       low   close      volume  \
    0   2023-07-28 04:00:00  129.690  133.01  129.3300  132.21  46269781.0   
    1   2023-07-31 04:00:00  133.200  133.87  132.3800  133.68  41901516.0   
    2   2023-08-01 04:00:00  133.550  133.69  131.6199  131.69  42250989.0   
    3   2023-08-02 04:00:00  130.154  130.23  126.8200  128.21  50988614.0   
    4   2023-08-03 04:00:00  127.480  129.84  126.4100  128.91  90855736.0   
    ..                  ...      ...     ...       ...     ...         ...   
    620 2026-01-16 05:00:00  239.085  239.57  236.4100  239.12  45888283.0   
    621 2026-01-20 05:00:00  233.760  235.09  229.3400  231.00  47737854.0   
    622 2026-01-21 05:00:00  231.085  232.30  226.8800  231.31  47276090.0   
    623 2026-01-22 05:00:00  234.045  235.72  230.9000  234.34  31913325.0   
    624 2026-01-23 05:00:00  234.955  240.45  234.5700  239.16  33778478.0   
    
             vwap  transactions   otc  
    0    131.8837        413438  None  
    1    133.3410        406644  None  
    2    132.2470        385743  None  
    3    128.3973        532942  None  
    4    131.4941        746639  None  
    ..        ...           ...   ...  
    620  238.4963        424842  None  
    621  231.9376        749010  None  
    622  230.2750        654920  None  
    623  234.0045        447829  None  
    624  238.6065        482481  None  
    
    [625 rows x 9 columns]
    Last date in existing data: 2026-01-23 05:00:00
    Number of rows in existing data: 625
    Forcing check of existing data...
    Pulling day data for 2024-01-26 00:00:00 thru 2024-07-24 00:00:00 for AMZN...
    
    New data:
                       Date    open    high      low   close       volume  \
    0   2024-01-29 05:00:00  159.34  161.29  158.900  161.26   45270385.0   
    1   2024-01-30 05:00:00  160.70  161.73  158.490  159.00   45207430.0   
    2   2024-01-31 05:00:00  157.00  159.01  154.810  155.20   50284371.0   
    3   2024-02-01 05:00:00  155.87  159.76  155.620  159.28   76542419.0   
    4   2024-02-02 05:00:00  169.19  172.50  167.330  171.81  117218313.0   
    ..                  ...     ...     ...      ...     ...          ...   
    118 2024-07-18 04:00:00  189.59  189.68  181.448  183.75   51043626.0   
    119 2024-07-19 04:00:00  181.14  184.93  180.110  183.13   43081829.0   
    120 2024-07-22 04:00:00  185.00  185.06  182.480  182.55   39931923.0   
    121 2024-07-23 04:00:00  184.10  189.39  183.560  186.41   47537670.0   
    122 2024-07-24 04:00:00  183.20  185.45  180.410  180.83   41532360.0   
    
             vwap  transactions   otc  
    0    160.2769        447373  None  
    1    159.4989        458714  None  
    2    156.2692        532783  None  
    3    160.6891        742980  None  
    4    170.9357       1134751  None  
    ..        ...           ...   ...  
    118  184.4092        672039  None  
    119  182.8750        482540  None  
    120  183.3798        448824  None  
    121  187.1186        489929  None  
    122  182.2157        506965  None  
    
    [123 rows x 9 columns]
    Combined data:
                       Date     open    high       low   close      volume  \
    0   2023-07-28 04:00:00  129.690  133.01  129.3300  132.21  46269781.0   
    1   2023-07-31 04:00:00  133.200  133.87  132.3800  133.68  41901516.0   
    2   2023-08-01 04:00:00  133.550  133.69  131.6199  131.69  42250989.0   
    3   2023-08-02 04:00:00  130.154  130.23  126.8200  128.21  50988614.0   
    4   2023-08-03 04:00:00  127.480  129.84  126.4100  128.91  90855736.0   
    ..                  ...      ...     ...       ...     ...         ...   
    620 2026-01-16 05:00:00  239.085  239.57  236.4100  239.12  45888283.0   
    621 2026-01-20 05:00:00  233.760  235.09  229.3400  231.00  47737854.0   
    622 2026-01-21 05:00:00  231.085  232.30  226.8800  231.31  47276090.0   
    623 2026-01-22 05:00:00  234.045  235.72  230.9000  234.34  31913325.0   
    624 2026-01-23 05:00:00  234.955  240.45  234.5700  239.16  33778478.0   
    
             vwap  transactions   otc  
    0    131.8837        413438  None  
    1    133.3410        406644  None  
    2    132.2470        385743  None  
    3    128.3973        532942  None  
    4    131.4941        746639  None  
    ..        ...           ...   ...  
    620  238.4963        424842  None  
    621  231.9376        749010  None  
    622  230.2750        654920  None  
    623  234.0045        447829  None  
    624  238.6065        482481  None  
    
    [625 rows x 9 columns]
    Sleeping for 12 seconds to avoid hitting API rate limits...
    


    Pulling day data for 2024-07-23 04:00:00 thru 2025-01-19 04:00:00 for AMZN...
    
    New data:
                       Date    open      high     low   close      volume  \
    0   2024-07-23 04:00:00  184.10  189.3900  183.56  186.41  47537670.0   
    1   2024-07-24 04:00:00  183.20  185.4500  180.41  180.83  41532360.0   
    2   2024-07-25 04:00:00  182.91  183.8958  176.80  179.85  44464163.0   
    3   2024-07-26 04:00:00  180.39  183.1900  180.24  182.50  29505964.0   
    4   2024-07-29 04:00:00  183.84  184.7500  182.38  183.20  33270123.0   
    ..                  ...     ...       ...     ...     ...         ...   
    119 2025-01-13 05:00:00  218.06  219.4000  216.47  218.46  27262655.0   
    120 2025-01-14 05:00:00  220.44  221.8200  216.20  217.76  24711650.0   
    121 2025-01-15 05:00:00  222.83  223.5700  220.75  223.35  31291257.0   
    122 2025-01-16 05:00:00  224.42  224.6500  220.31  220.66  24757276.0   
    123 2025-01-17 05:00:00  225.84  226.5100  223.08  225.94  42370123.0   
    
             vwap  transactions   otc  
    0    187.1186        489929  None  
    1    182.2157        506965  None  
    2    180.8787        548308  None  
    3    181.9844        375650  None  
    4    183.4509        350828  None  
    ..        ...           ...   ...  
    119  218.1426        373519  None  
    120  218.6245        332022  None  
    121  222.6690        353985  None  
    122  221.8942        313323  None  
    123  225.3927        385914  None  
    
    [124 rows x 9 columns]
    Combined data:
                       Date     open    high       low   close      volume  \
    0   2023-07-28 04:00:00  129.690  133.01  129.3300  132.21  46269781.0   
    1   2023-07-31 04:00:00  133.200  133.87  132.3800  133.68  41901516.0   
    2   2023-08-01 04:00:00  133.550  133.69  131.6199  131.69  42250989.0   
    3   2023-08-02 04:00:00  130.154  130.23  126.8200  128.21  50988614.0   
    4   2023-08-03 04:00:00  127.480  129.84  126.4100  128.91  90855736.0   
    ..                  ...      ...     ...       ...     ...         ...   
    620 2026-01-16 05:00:00  239.085  239.57  236.4100  239.12  45888283.0   
    621 2026-01-20 05:00:00  233.760  235.09  229.3400  231.00  47737854.0   
    622 2026-01-21 05:00:00  231.085  232.30  226.8800  231.31  47276090.0   
    623 2026-01-22 05:00:00  234.045  235.72  230.9000  234.34  31913325.0   
    624 2026-01-23 05:00:00  234.955  240.45  234.5700  239.16  33778478.0   
    
             vwap  transactions   otc  
    0    131.8837        413438  None  
    1    133.3410        406644  None  
    2    132.2470        385743  None  
    3    128.3973        532942  None  
    4    131.4941        746639  None  
    ..        ...           ...   ...  
    620  238.4963        424842  None  
    621  231.9376        749010  None  
    622  230.2750        654920  None  
    623  234.0045        447829  None  
    624  238.6065        482481  None  
    
    [625 rows x 9 columns]
    Sleeping for 12 seconds to avoid hitting API rate limits...
    


    Pulling day data for 2025-01-16 05:00:00 thru 2025-07-15 05:00:00 for AMZN...
    
    New data:
                       Date    open      high      low   close      volume  \
    0   2025-01-16 05:00:00  224.42  224.6500  220.310  220.66  24757276.0   
    1   2025-01-17 05:00:00  225.84  226.5100  223.080  225.94  42370123.0   
    2   2025-01-21 05:00:00  228.90  231.7800  226.940  230.71  39951456.0   
    3   2025-01-22 05:00:00  232.02  235.4400  231.190  235.01  41448217.0   
    4   2025-01-23 05:00:00  234.10  235.5200  231.510  235.42  26404364.0   
    ..                  ...     ...       ...      ...     ...         ...   
    118 2025-07-09 04:00:00  221.07  224.2900  220.470  222.54  38155121.0   
    119 2025-07-10 04:00:00  221.55  222.7900  219.700  222.26  30370591.0   
    120 2025-07-11 04:00:00  223.58  226.6799  222.370  225.02  50518307.0   
    121 2025-07-14 04:00:00  225.07  226.6600  224.240  225.69  35702597.0   
    122 2025-07-15 04:00:00  226.20  227.2700  225.455  226.35  34907294.0   
    
             vwap  transactions   otc  
    0    221.8942        313323  None  
    1    225.3927        385914  None  
    2    230.0901        552447  None  
    3    234.0950        512233  None  
    4    234.2435        365153  None  
    ..        ...           ...   ...  
    118  222.4555        493756  None  
    119  221.7055        451223  None  
    120  224.8908        661385  None  
    121  225.6173        460428  None  
    122  226.4985        507705  None  
    
    [123 rows x 9 columns]
    Combined data:
                       Date     open    high       low   close      volume  \
    0   2023-07-28 04:00:00  129.690  133.01  129.3300  132.21  46269781.0   
    1   2023-07-31 04:00:00  133.200  133.87  132.3800  133.68  41901516.0   
    2   2023-08-01 04:00:00  133.550  133.69  131.6199  131.69  42250989.0   
    3   2023-08-02 04:00:00  130.154  130.23  126.8200  128.21  50988614.0   
    4   2023-08-03 04:00:00  127.480  129.84  126.4100  128.91  90855736.0   
    ..                  ...      ...     ...       ...     ...         ...   
    620 2026-01-16 05:00:00  239.085  239.57  236.4100  239.12  45888283.0   
    621 2026-01-20 05:00:00  233.760  235.09  229.3400  231.00  47737854.0   
    622 2026-01-21 05:00:00  231.085  232.30  226.8800  231.31  47276090.0   
    623 2026-01-22 05:00:00  234.045  235.72  230.9000  234.34  31913325.0   
    624 2026-01-23 05:00:00  234.955  240.45  234.5700  239.16  33778478.0   
    
             vwap  transactions   otc  
    0    131.8837        413438  None  
    1    133.3410        406644  None  
    2    132.2470        385743  None  
    3    128.3973        532942  None  
    4    131.4941        746639  None  
    ..        ...           ...   ...  
    620  238.4963        424842  None  
    621  231.9376        749010  None  
    622  230.2750        654920  None  
    623  234.0045        447829  None  
    624  238.6065        482481  None  
    
    [625 rows x 9 columns]
    Sleeping for 12 seconds to avoid hitting API rate limits...
    


    Pulling day data for 2025-07-14 04:00:00 thru 2026-01-10 04:00:00 for AMZN...
    
    New data:
                       Date     open    high      low   close      volume  \
    0   2025-07-14 04:00:00  225.070  226.66  224.240  225.69  35702597.0   
    1   2025-07-15 04:00:00  226.200  227.27  225.455  226.35  34907294.0   
    2   2025-07-16 04:00:00  225.875  226.10  222.180  223.19  39535926.0   
    3   2025-07-17 04:00:00  223.320  224.50  222.510  223.88  31855831.0   
    4   2025-07-18 04:00:00  225.140  226.40  222.980  226.13  37833807.0   
    ..                  ...      ...     ...      ...     ...         ...   
    121 2026-01-05 05:00:00  228.840  234.00  227.180  233.06  49733348.0   
    122 2026-01-06 05:00:00  232.100  243.18  232.070  240.93  53764677.0   
    123 2026-01-07 05:00:00  239.610  245.29  239.520  241.56  42236531.0   
    124 2026-01-08 05:00:00  243.060  246.41  241.880  246.29  39509844.0   
    125 2026-01-09 05:00:00  244.568  247.86  242.240  247.38  34559961.0   
    
             vwap  transactions   otc  
    0    225.6173        460428  None  
    1    226.4985        507705  None  
    2    223.7872        556155  None  
    3    223.6948        445580  None  
    4    225.2906        454003  None  
    ..        ...           ...   ...  
    121  232.1786        678867  None  
    122  239.6475        767759  None  
    123  242.9662        623031  None  
    124  245.1880        537907  None  
    125  246.0666        487691  None  
    
    [126 rows x 9 columns]
    Combined data:
                       Date     open    high       low   close      volume  \
    0   2023-07-28 04:00:00  129.690  133.01  129.3300  132.21  46269781.0   
    1   2023-07-31 04:00:00  133.200  133.87  132.3800  133.68  41901516.0   
    2   2023-08-01 04:00:00  133.550  133.69  131.6199  131.69  42250989.0   
    3   2023-08-02 04:00:00  130.154  130.23  126.8200  128.21  50988614.0   
    4   2023-08-03 04:00:00  127.480  129.84  126.4100  128.91  90855736.0   
    ..                  ...      ...     ...       ...     ...         ...   
    620 2026-01-16 05:00:00  239.085  239.57  236.4100  239.12  45888283.0   
    621 2026-01-20 05:00:00  233.760  235.09  229.3400  231.00  47737854.0   
    622 2026-01-21 05:00:00  231.085  232.30  226.8800  231.31  47276090.0   
    623 2026-01-22 05:00:00  234.045  235.72  230.9000  234.34  31913325.0   
    624 2026-01-23 05:00:00  234.955  240.45  234.5700  239.16  33778478.0   
    
             vwap  transactions   otc  
    0    131.8837        413438  None  
    1    133.3410        406644  None  
    2    132.2470        385743  None  
    3    128.3973        532942  None  
    4    131.4941        746639  None  
    ..        ...           ...   ...  
    620  238.4963        424842  None  
    621  231.9376        749010  None  
    622  230.2750        654920  None  
    623  234.0045        447829  None  
    624  238.6065        482481  None  
    
    [625 rows x 9 columns]
    Sleeping for 12 seconds to avoid hitting API rate limits...
    


    Pulling day data for 2026-01-08 05:00:00 thru 2026-07-07 05:00:00 for AMZN...
    
    New data:
                      Date     open    high     low   close      volume      vwap  \
    0  2026-01-08 05:00:00  243.060  246.41  241.88  246.29  39509844.0  245.1880   
    1  2026-01-09 05:00:00  244.568  247.86  242.24  247.38  34559961.0  246.0666   
    2  2026-01-12 05:00:00  246.730  248.94  245.96  246.47  35867770.0  247.2996   
    3  2026-01-13 05:00:00  246.530  247.66  240.25  242.60  38371778.0  243.3866   
    4  2026-01-14 05:00:00  241.150  241.28  236.22  236.65  41410578.0  237.6446   
    5  2026-01-15 05:00:00  239.310  240.65  236.63  238.18  43003571.0  238.3037   
    6  2026-01-16 05:00:00  239.085  239.57  236.41  239.12  45888283.0  238.4963   
    7  2026-01-20 05:00:00  233.760  235.09  229.34  231.00  47737854.0  231.9376   
    8  2026-01-21 05:00:00  231.085  232.30  226.88  231.31  47276090.0  230.2750   
    9  2026-01-22 05:00:00  234.045  235.72  230.90  234.34  31913325.0  234.0045   
    10 2026-01-23 05:00:00  234.955  240.45  234.57  239.16  33778478.0  238.6065   
    
        transactions   otc  
    0         537907  None  
    1         487691  None  
    2         520852  None  
    3         559247  None  
    4         582230  None  
    5         567069  None  
    6         424842  None  
    7         749010  None  
    8         654920  None  
    9         447829  None  
    10        482481  None  
    Combined data:
                       Date     open    high       low   close      volume  \
    0   2023-07-28 04:00:00  129.690  133.01  129.3300  132.21  46269781.0   
    1   2023-07-31 04:00:00  133.200  133.87  132.3800  133.68  41901516.0   
    2   2023-08-01 04:00:00  133.550  133.69  131.6199  131.69  42250989.0   
    3   2023-08-02 04:00:00  130.154  130.23  126.8200  128.21  50988614.0   
    4   2023-08-03 04:00:00  127.480  129.84  126.4100  128.91  90855736.0   
    ..                  ...      ...     ...       ...     ...         ...   
    620 2026-01-16 05:00:00  239.085  239.57  236.4100  239.12  45888283.0   
    621 2026-01-20 05:00:00  233.760  235.09  229.3400  231.00  47737854.0   
    622 2026-01-21 05:00:00  231.085  232.30  226.8800  231.31  47276090.0   
    623 2026-01-22 05:00:00  234.045  235.72  230.9000  234.34  31913325.0   
    624 2026-01-23 05:00:00  234.955  240.45  234.5700  239.16  33778478.0   
    
             vwap  transactions   otc  
    0    131.8837        413438  None  
    1    133.3410        406644  None  
    2    132.2470        385743  None  
    3    128.3973        532942  None  
    4    131.4941        746639  None  
    ..        ...           ...   ...  
    620  238.4963        424842  None  
    621  231.9376        749010  None  
    622  230.2750        654920  None  
    623  234.0045        447829  None  
    624  238.6065        482481  None  
    
    [625 rows x 9 columns]
    Exporting AMZN day data to Excel...


    Exporting AMZN day data to Pickle...
    The first and last date of day data for AMZN is: 



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
      <th>Date</th>
      <th>open</th>
      <th>high</th>
      <th>low</th>
      <th>close</th>
      <th>volume</th>
      <th>vwap</th>
      <th>transactions</th>
      <th>otc</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-07-28 04:00:00</td>
      <td>129.69</td>
      <td>133.01</td>
      <td>129.33</td>
      <td>132.21</td>
      <td>46269781.0</td>
      <td>131.8837</td>
      <td>413438</td>
      <td>None</td>
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
      <th>Date</th>
      <th>open</th>
      <th>high</th>
      <th>low</th>
      <th>close</th>
      <th>volume</th>
      <th>vwap</th>
      <th>transactions</th>
      <th>otc</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>624</th>
      <td>2026-01-23 05:00:00</td>
      <td>234.955</td>
      <td>240.45</td>
      <td>234.57</td>
      <td>239.16</td>
      <td>33778478.0</td>
      <td>238.6065</td>
      <td>482481</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>


    Number of rows after data update: 625
    Number of rows added during update: 0
    Polygon data complete for AMZN day data.
    --------------------



```python
# Copy this <!-- INSERT_polygon_pull_data_HERE --> to index_temp.md
export_track_md_deps(
    dep_file=dep_file, 
    md_filename="polygon_pull_data.md", 
    content=df.head().to_markdown(floatfmt=".5f"),
    output_type="markdown",
)
```

    ✅ Exported and tracked: polygon_pull_data.md

