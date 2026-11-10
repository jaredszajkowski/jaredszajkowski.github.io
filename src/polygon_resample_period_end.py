import os
import pandas as pd


def polygon_resample_period_end(
    base_directory,
    ticker: str,
    source: str,
    asset_class: str,
    timespan: str,
    period: str,
    excel_export: bool,
    pickle_export: bool,
    parquet_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    """
    Read data from an existing pickle file and export month-end or quarter-end
    close prices (and dividend-adjusted close prices, if present).

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    ticker : str
        Ticker symbol to resample.
    source : str
        Name of the data source (e.g., 'Polygon').
    asset_class : str
        Asset class name (e.g., 'Equities').
    timespan : str
        Time span of the existing data to read (e.g., "day").
    period : str
        Period to resample to, either "month" (month-end) or "quarter" (quarter-end).
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    parquet_export : bool
        If True, export data to Parquet format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns:
    --------
    df_period_end : pd.DataFrame
        DataFrame indexed by period-end date containing the close column, plus
        adj_close if it exists in the source data.
    """

    # Resample frequency, output directory, and file suffix for each period
    period_settings = {
        "month": {"freq": "ME", "directory": "Month_End", "suffix": "ME"},
        "quarter": {"freq": "QE", "directory": "Quarter_End", "suffix": "QE"},
    }
    if period not in period_settings:
        raise Exception(
            f"Invalid period: {period}. Acceptable periods are: {list(period_settings)}."
        )
    settings = period_settings[period]

    # Set location from where to read existing pickle file
    location = f"{base_directory}/{source}/{asset_class}/{timespan}/{ticker}.pkl"

    # Read data from pickle
    df = pd.read_pickle(location)

    # Reset index if 'Date' is column is the index
    if "Date" not in df.columns:
        df = df.reset_index()

    # Keep only required columns
    keep_cols = ["Date", "close"] + (["adj_close"] if "adj_close" in df.columns else [])
    df = df[keep_cols]

    # Set index to date column
    df = df.set_index("Date")

    # Resample data to period end
    df_period_end = df.resample(settings["freq"]).last()

    # Create directory
    directory = f"{base_directory}/{source}/{asset_class}/{settings['directory']}"
    os.makedirs(directory, exist_ok=True)

    file_stem = f"{directory}/{ticker}_{settings['suffix']}"

    # Export to Excel
    if excel_export == True:
        df_period_end.to_excel(f"{file_stem}.xlsx", sheet_name="data")

    # Export to Pickle
    if pickle_export == True:
        df_period_end.to_pickle(f"{file_stem}.pkl")

    # Export to Parquet
    if parquet_export == True:
        df_period_end.to_parquet(f"{file_stem}.parquet")

    # Output confirmation
    if output_confirmation == True:
        print(f"{period.capitalize()} end data complete for {ticker}")
        print(f"--------------------")

    return df_period_end
