import pandas as pd
from pathlib import Path

def load_data(
    base_directory: str,
    ticker: str,
    source: str,
    asset_class: str,
    timeframe: str,
    file_format: str,
) -> pd.DataFrame:
    
    """
    Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.

    This function attempts to read a file first as a CSV, then as an Excel file 
    (specifically looking for a sheet named 'data' and using the 'calamine' engine).
    If both attempts fail, a ValueError is raised.

    Parameters:
    -----------
    base_directory : str
        Root path to read data file.
    ticker : str
        Ticker symbol to read.
    source : str
        Name of the data source (e.g., 'Yahoo').
    asset_class : str
        Asset class name (e.g., 'Equities').
    timeframe : str
        Timeframe for the data (e.g., 'Daily', 'Month_End').
    file_format : str
        Format of the file to load ('csv', 'excel', or 'pickle')

    Returns:
    --------
    pd.DataFrame
        The loaded data.

    Raises:
    -------
    ValueError
        If the file could not be loaded as either CSV or Excel.

    Example:
    --------
    >>> df = load_data(DATA_DIR, "^VIX", "Yahoo_Finance", "Indices")
    """

    if file_format == "csv":
        csv_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.csv"
        df = pd.read_csv(csv_path)
        return df
    
    elif file_format == "excel":
        xlsx_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.xlsx"
        df = pd.read_excel(xlsx_path, sheet_name="data", engine="calamine")
        return df

    elif file_format == "pickle":
        pickle_path = Path(base_directory) / source / asset_class / timeframe / f"{ticker}.pkl"
        df = pd.read_pickle(pickle_path)
        return df
    
    else:
        raise ValueError(f"❌ Unsupported file format: {file_format}. Please use 'csv', 'excel', or 'pickle'.")