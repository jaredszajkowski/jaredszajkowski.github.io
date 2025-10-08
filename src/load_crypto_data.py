import pandas as pd

from load_data import load_data

def load_crypto_data(
    tickers: list,
    base_directory,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    
    """
    Loads minute-level data for multiple crypto tickers from Coinbase source.


    Parameters:
    -----------
    tickers : list
        List of crypto tickers, e.g., ["BTC-USD", "ETH-USD", "SOL-USD"].
    base_directory
        Base directory where data files are stored.
    start_date : str
        Optional start date for filtering data, e.g., "2023-01-01".
    end_date : str
        Optional end date for filtering data, e.g., "2023-12-31".

    Returns:
    --------
    pd.DataFrame
        DataFrame containing merged price data for all tickers.
    """

    # Create empty DataFrame
    df = pd.DataFrame()
    
    for ticker in tickers:
        # Load data
        temp_df = load_data(
            base_directory=base_directory,
            ticker=ticker,
            source="Coinbase",
            asset_class="Cryptocurrencies",
            timeframe="Minute",
            file_format="pickle",
        )
        temp_df.index = pd.to_datetime(temp_df.index)
        temp_df = temp_df.sort_index()

        # Rename columns
        temp_df = temp_df.rename(columns={
            "open": f"{ticker}_open",
            "high": f"{ticker}_high",
            "low": f"{ticker}_low",
            "close": f"{ticker}_close",
            "volume": f"{ticker}_volume",
        })

        # Merge the data
        df = pd.merge(df, temp_df, how="outer", left_index=True, right_index=True)

    # Apply date filtering if specified
    if start_date:
        df = df[df.index >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df.index <= pd.to_datetime(end_date)]

    # Reset index
    df = df.reset_index()

    return df