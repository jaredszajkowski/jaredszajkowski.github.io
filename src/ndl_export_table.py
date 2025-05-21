import datetime
import nasdaqdatalink as quandl
import os
import pandas as pd

from env_vars import load_api_keys
from pathlib import Path
from settings import config

# Load API keys from the environment
api_keys = load_api_keys()

# Get the data directory from the configuration
DATA_DIR = config("DATA_DIR")

# Credit to Professor Brian Boonstra for much of the code below in the "grab_quandl_table" and "fetch_quandl_table" functions
def grab_quandl_table(
    table_path: str,
    avoid_download: bool=False,
    replace_existing: bool=False,
    date_override=None,
    allow_old_file: bool=False,
    **kwargs,
):      
    
    root_data_dir = Path(DATA_DIR / "Nasdaq_Data_Link")
    
    data_symlink = os.path.join(root_data_dir, f"{table_path}_latest.zip")
    
    if avoid_download and os.path.exists(data_symlink):
        print(f"Skipping any possible download of {table_path}")
        return data_symlink
    
    table_dir = os.path.dirname(data_symlink)
    if not os.path.isdir(table_dir):
        print(f"Creating new data dir {table_dir}")
        os.makedirs(table_dir, exist_ok=True)

    if date_override is None:
        my_date = datetime.datetime.now().strftime("%Y%m%d")
    else:
        my_date = date_override

    data_file = os.path.join(root_data_dir, f"{table_path}_{my_date}.zip")

    if os.path.exists(data_file):
        file_size = os.stat(data_file).st_size
        if replace_existing or not file_size > 0:
            print(f"Removing old file {data_file} size {file_size}")
        else:
            print(f"Data file {data_file} size {file_size} exists already, no need to download")
            return data_file

    dl = quandl.export_table(table_path, filename=data_file, api_key=api_keys["NASDAQ_DATA_LINK_KEY"], **kwargs)

    file_size = os.stat(data_file).st_size
    
    if os.path.exists(data_file) and file_size > 0:
        print(f"Download finished: {file_size} bytes")
        if not date_override:
            if os.path.exists(data_symlink):
                print(f"Removing old symlink")
                os.unlink(data_symlink)
            print(f"Creating symlink: {data_file} -> {data_symlink}")
            os.symlink(
                data_file, data_symlink,
            )
    else:
        print(f"Data file {data_file} failed download")
        return
    return data_symlink if (date_override is None or allow_old_file) else "NoFileAvailable"


def fetch_quandl_table(table_path, avoid_download=True, **kwargs):
    return pd.read_csv(grab_quandl_table(table_path, avoid_download=avoid_download, **kwargs))

if __name__ == "__main__":
    table_paths = [
        # 'EDI/ASAP',
        'EDI/ASAF',
        'EDI/CUR',
        'QUOTEMEDIA/PRICES',
        'QUOTEMEDIA/TICKERS',
        'QUOTEMEDIA/DAILYPRICES',
        'AR/IVM',
        'AR/IVS',
        'ZACKS/FC',
        'ZACKS/FR',
        'ZACKS/MT',
        'ZACKS/MKTV',
        'ZACKS/SHRS',
        'ZACKS/HDM',
        'NDAQ/USEDH',
        'NDAQ/USEDHADJ',
    ]

    for table in table_paths:
        try:
            print(f"Fetching: {table}")
            fetch_quandl_table(table)
        except Exception as e:
            print(f"❌ Error fetching {table}: {e}")