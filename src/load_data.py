import pandas as pd
from pathlib import Path

def load_data(file: str | Path) -> pd.DataFrame:
    """
    Load data from a CSV or Excel file into a pandas DataFrame.

    This function attempts to read a file first as a CSV, then as an Excel file 
    (specifically looking for a sheet named 'data' and using the 'calamine' engine).
    If both attempts fail, a ValueError is raised.

    Parameters:
    -----------
    file : str or Path
        The path to the data file to be loaded.

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
    >>> df = load_data("my_data.csv")
    >>> df = load_data("my_excel_file.xlsx")
    """
    file = Path(file)
    df = None

    # Try CSV
    try:
        df = pd.read_csv(file)
        return df
    except Exception:
        pass

    # Try Excel
    try:
        df = pd.read_excel(file, sheet_name="data", engine="calamine")
        return df
    except Exception:
        pass

    raise ValueError(f"❌ Unable to load file: {file}. Ensure it's a valid CSV or Excel file with a 'data' sheet.")
