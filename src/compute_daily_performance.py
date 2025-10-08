import pandas as pd

def compute_daily_performance(
    tickers: list,
    data: pd.DataFrame,
    trades: pd.DataFrame,
    initial_capital: int,
) -> pd.DataFrame:
    
    """
    Computes daily portfolio equity, return, etc. from trades dataframe.

    Parameters:
    -----------
    tickers : list
        List of crypto tickers, e.g., ["BTC-USD", "ETH-USD", "SOL-USD"].
    data : pd.DataFrame
        DataFrame containing merged price data for all tickers.
    trades : pd.DataFrame
        DataFrame of trades from backtest_rsi_multi_asset_strategy.
    initial_capital : int
        Initial capital for the portfolio.

    Returns:
    --------
    pd.DataFrame
        DataFrame containing daily data for the portfolio with equity, cash, 
        returns, positions, drawdowns, and prices.
    """

    # Copy the data dataframe
    df = data.copy().set_index("Date")

    # Filter the entry trades
    entry_trades_df = trades.copy()
    entry_trades_df = entry_trades_df[['asset', 'entry_time', 'entry_price', 'quantity', 'entry_fee']]
    entry_trades_df['cash'] = (entry_trades_df['entry_price'] * entry_trades_df['quantity'] * -1) - entry_trades_df['entry_fee']
    entry_trades_df['crypto_value'] = entry_trades_df['quantity'] * entry_trades_df['entry_price']
    entry_trades_df.rename(columns={'entry_time': 'Date'}, inplace=True)

    # Filter the exit trades
    exit_trades_df = trades.copy()
    exit_trades_df = exit_trades_df[['asset', 'exit_time', 'exit_price', 'quantity', 'exit_fee']]
    exit_trades_df['cash'] = (exit_trades_df['exit_price'] * exit_trades_df['quantity']) - exit_trades_df['exit_fee']
    exit_trades_df['quantity'] = exit_trades_df['quantity'] * -1  # Convert quantity to negative for exit
    exit_trades_df['crypto_value'] = exit_trades_df['quantity'] * exit_trades_df['exit_price']
    exit_trades_df.rename(columns={'exit_time': 'Date'}, inplace=True)

    # Combine entry and exit trades into a single DataFrame
    ledger_events_df = pd.concat([entry_trades_df, exit_trades_df], ignore_index=True)
    ledger_events_df = ledger_events_df.sort_values('Date')

    # Create pivot table for quantity held by date per asset
    quantity_df = ledger_events_df.pivot_table(
        index='Date',
        columns='asset',
        values='quantity',
        aggfunc='sum',
    ).fillna(0)

    quantity_df.columns = [f"{col}_qty" for col in quantity_df.columns]

    # Cash flow dataframe
    cash_df = ledger_events_df.groupby('Date')['cash'].sum().to_frame()

    # Combine quantity and cash dataframes into the ledger
    ledger_qtys_df = pd.concat([quantity_df, cash_df], axis=1).fillna(0)
    ledger_qtys_df = ledger_qtys_df.sort_index()

    # Isolate the daily close prices for each asset
    price_cols = [f"{ticker}_close" for ticker in tickers]
    price_df = df[price_cols].copy()

    # Merge the daily close prices DataFrame into the ledger
    ledger_qtys_prices_df = ledger_qtys_df.join(price_df, how="outer")

    # Replace all NaN values with 0
    ledger_qtys_prices_df.fillna(0, inplace=True)

    # Add columns for each asset's cumulative quantity
    quantity_cols = [col for col in ledger_qtys_prices_df.columns if col.endswith("_qty")]
    for col in quantity_cols:
        ledger_qtys_prices_df[col] = ledger_qtys_prices_df[col].cumsum()

    # Cumulative cash column
    ledger_qtys_prices_df['cash'] = ledger_qtys_prices_df['cash'].cumsum()

    # Add initial capital amount to cash to represent initial capital
    ledger_qtys_prices_df['cash'] += initial_capital

    # Establish position columns for each asset
    ledger_qtys_prices_pos_df = ledger_qtys_prices_df.copy()
    for col in quantity_cols:
        asset_symbol = col.replace("_qty", "")
        ledger_qtys_prices_pos_df[f"{asset_symbol}_position"] = ledger_qtys_prices_pos_df[col] * ledger_qtys_prices_pos_df[f"{asset_symbol}_close"]

    # Re-arrange the columns to have date, cash, then quantities, prices, positions grouped by asset
    asset_symbols = []
    for col in quantity_cols:
        asset_symbol = col.replace("_qty", "")
        asset_symbols.append(asset_symbol)

    cols = (['cash'] + [col for ticker in asset_symbols for col in ledger_qtys_prices_pos_df.columns if col.startswith(ticker)])
    ledger_qtys_prices_pos_df = ledger_qtys_prices_pos_df[cols]

    # Calculate total portfolio value
    ledger_qtys_prices_pos_df['equity'] = ledger_qtys_prices_pos_df['cash'] + ledger_qtys_prices_pos_df[[col for col in ledger_qtys_prices_pos_df.columns if col.endswith('_position')]].sum(axis=1)

    # Reindex ledger to daily using last price for the day
    daily_ledger_qtys_prices_pos_df = ledger_qtys_prices_pos_df.copy()
    daily_ledger_qtys_prices_pos_df = daily_ledger_qtys_prices_pos_df.resample("D").last()

    # Drop the columns where any of the crypto asset prices = 0
    price_cols = [col for col in daily_ledger_qtys_prices_pos_df.columns if col.endswith("_close")]
    complete_ledger = daily_ledger_qtys_prices_pos_df[~(daily_ledger_qtys_prices_pos_df[price_cols] == 0).any(axis=1)]

    # Calculate crypto daily return, cumulative return, and drawdown
    for col in asset_symbols:
        complete_ledger[f"{col}_return"] = complete_ledger[f"{col}_close"].pct_change()
        complete_ledger[f"{col}_cum_return"] = (1 + complete_ledger[f"{col}_return"]).cumprod() - 1
        complete_ledger[f"{col}_drawdown"] = (complete_ledger[f"{col}_close"] - complete_ledger[f"{col}_close"].cummax()) / complete_ledger[f"{col}_close"].cummax()

    # Calculate portfolio daily return and cumulative return
    complete_ledger['Return'] = complete_ledger['equity'].pct_change()
    complete_ledger['Cum_Return'] = (1 + complete_ledger['Return']).cumprod() - 1

    # Calculate drawdown
    complete_ledger["Drawdown"] = (complete_ledger["equity"] - complete_ledger["equity"].cummax()) / complete_ledger["equity"].cummax()

    # Fill NaN values with 0 to return a complete DataFrame
    complete_ledger.fillna(0, inplace=True)

    return complete_ledger