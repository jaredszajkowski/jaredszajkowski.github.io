import pandas as pd

from calculate_rsi import calculate_rsi

def add_rsi_ma_bb(
    tickers: list,
    data: pd.DataFrame,
    rsi_period: int,
    ma_days: list,
    bb_window: int,
    bb_num_std: float,
) -> pd.DataFrame:
    
    """
    Adds RSI, moving averages,and Bollinger bands for each crypto asset.

    Parameters:
    -----------
    tickers : list
        List of crypto tickers, e.g., ["BTC-USD", "ETH-USD", "SOL-USD"].
    data : pd.DataFrame
        DataFrame containing merged price data for all tickers.
    rsi_period : int
        RSI lookback period.
    ma_days : list
        List of moving average durations in days.

    Returns:
    --------
    pd.DataFrame
        DataFrame containing merged data for all tickers with RSI, moving averages, 
        and bollinger bands.
    """

    # Copy the data dataframe
    df = data.copy()

    for ticker in tickers:
        # Shift close by 1 row
        df[f"{ticker}_close_prev"] = df[f"{ticker}_close"].shift(1)

        # ----- RSI -----

        # Calc RSI and shift by 1 row
        df[f"{ticker}_RSI"] = calculate_rsi(df[f"{ticker}_close"], period=rsi_period)
        df[f"{ticker}_RSI_prev"] = df[f"{ticker}_RSI"].shift(1)

        # ----- Moving Averages -----

        # Calc moving averages and shift by 1 row
        for day in ma_days:
            window = 1440 * day  # 1440 minutes in a day
            df[f"{ticker}_MA_{day}d"] = df[f"{ticker}_close"].rolling(window=window, min_periods=1).mean()
            df[f"{ticker}_MA_{day}d_prev"] = df[f"{ticker}_MA_{day}d"].shift(1)

        # ----- Bollinger Bands -----
        rolling = df[f"{ticker}_close_prev"].rolling(window=bb_window, min_periods=bb_window)
        df[f"{ticker}_BB_MID_prev"] = rolling.mean()
        df[f"{ticker}_BB_STD_prev"] = rolling.std()
        df[f"{ticker}_BB_UPPER_prev"] = df[f"{ticker}_BB_MID_prev"] + (bb_num_std * df[f"{ticker}_BB_STD_prev"])
        df[f"{ticker}_BB_LOWER_prev"] = df[f"{ticker}_BB_MID_prev"] - (bb_num_std * df[f"{ticker}_BB_STD_prev"])
        df[f"{ticker}_BB_Z_prev"] = (df[f"{ticker}_close_prev"] - df[f"{ticker}_BB_MID_prev"]) / df[f"{ticker}_BB_STD_prev"]

    return df