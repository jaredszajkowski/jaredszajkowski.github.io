import os
import pandas as pd


def databento_month_end(
    base_directory,
    symbol: str,
    source: str,
    asset_class: str,
    schema: str,
    excel_export: bool,
    pickle_export: bool,
    parquet_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    """
    Read daily data from an existing pickle file and export month-end close prices.

    Parameters:
    -----------
    base_directory : str
        Root path to store downloaded data.
    symbol : str
        Symbol to download (e.g., "AAPL").
    source : str
        Name of the data source (e.g., "DataBento").
    asset_class : str
        Asset class name (e.g., "Equities").
    schema : str
        Schema used when fetching daily data (should be "ohlcv-1d").
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
    df_month_end : pd.DataFrame
        DataFrame containing month-end close prices.
    """

    location = f"{base_directory}/{source}/{asset_class}/{schema}/{symbol}.pkl"

    df = pd.read_pickle(location)

    if "Date" not in df.columns:
        df = df.reset_index()

    df = df[["Date", "close"]]
    df = df.set_index("Date")

    df_month_end = df.resample("ME").last()

    directory = f"{base_directory}/{source}/{asset_class}/Month_End"
    os.makedirs(directory, exist_ok=True)

    if excel_export:
        df_month_end.to_excel(f"{directory}/{symbol}_ME.xlsx", sheet_name="data")

    if pickle_export:
        df_month_end.to_pickle(f"{directory}/{symbol}_ME.pkl")

    if parquet_export:
        df_month_end.to_parquet(f"{directory}/{symbol}_ME.parquet")

    if output_confirmation:
        print(f"Month end data complete for {symbol}")
        print(f"--------------------")

    return df_month_end
