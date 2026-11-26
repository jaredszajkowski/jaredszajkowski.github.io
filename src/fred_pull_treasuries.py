import os
import pandas as pd

from IPython.display import display
from settings import config

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# FRED's public CSV endpoint (no API key required)
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

# Daily Treasury constant maturity yields (percent), shortest to longest
TREASURY_SERIES = {
    "DGS1MO": "1M",
    "DGS3MO": "3M",
    "DGS6MO": "6M",
    "DGS1": "1Y",
    "DGS2": "2Y",
    "DGS3": "3Y",
    "DGS5": "5Y",
    "DGS7": "7Y",
    "DGS10": "10Y",
    "DGS20": "20Y",
    "DGS30": "30Y",
}


def fred_pull_treasuries(
    base_directory: str,
    series: dict,
    source: str,
    asset_class: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    """
    Download daily Treasury constant maturity yields from FRED, combine them
    into a single DataFrame, and export it.

    Parameters:
    -----------
    base_directory : str
        Root path to store downloaded data.
    series : dict
        Mapping of FRED series IDs to column names (e.g., {'DGS10': '10Y'}).
    source : str
        Name of the data source (e.g., 'FRED').
    asset_class : str
        Asset class name (e.g., 'Treasuries').
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    df : pd.DataFrame
        DataFrame of decimal yields, indexed by date, one column per
        maturity. Days with no observations for any maturity are dropped.
    """

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/Daily"
    os.makedirs(directory, exist_ok=True)

    # Download each series; FRED marks missing observations with "."
    frames = []
    for series_id, column_name in series.items():
        df_series = pd.read_csv(
            FRED_CSV_URL.format(series_id=series_id),
            index_col=0,
            parse_dates=True,
            na_values=".",
        )
        df_series.columns = [column_name]

        # Name the index and drop holidays with no observation
        df_series.index.name = "Date"
        df_series = df_series.dropna()

        # Convert from percent to decimal
        df_series[column_name] = df_series[column_name] / 100

        frames.append(df_series)

    # Combine on date, keeping the full history of every maturity
    df = pd.concat(frames, axis=1, join="outer").sort_index()

    # Normalize to nanosecond resolution
    df.index = df.index.astype("datetime64[ns]")

    # Export to excel
    if excel_export == True:
        df.to_excel(f"{directory}/Treasury_Yields.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df.to_pickle(f"{directory}/Treasury_Yields.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        print(f"The first and last date of data for Treasury_Yields is: ")
        display(df[:1])
        display(df[-1:])
        print(f"FRED data complete for Treasury_Yields")
        print(f"--------------------")
    else:
        pass

    return df


if __name__ == "__main__":

    fred_pull_treasuries(
        base_directory=DATA_DIR,
        series=TREASURY_SERIES,
        source="FRED",
        asset_class="Treasuries",
        excel_export=True,
        pickle_export=True,
        output_confirmation=True,
    )
