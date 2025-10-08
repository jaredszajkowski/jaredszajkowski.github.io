import pandas as pd

def analyze_trades(
    trades_df: pd.DataFrame,
    daily_perf_df: pd.DataFrame,
    print_summary: bool,
) -> tuple[int, float, float, float, float, float, float, float, float, float, float]:

    # Filter trades to only those that traded an actual position
    filtered_trades = trades_df[trades_df['quantity'] > 0.01]

    total_trades = len(filtered_trades)
    win_rate = len(filtered_trades[filtered_trades['return'] > 0]) / len(filtered_trades)
    total_return = daily_perf_df['Cum_Return'].iloc[-1]
    average_return_per_trade = filtered_trades['return'].mean()
    max_trade_gain_return = filtered_trades['return'].max()
    max_trade_loss_return = filtered_trades['return'].min()
    total_pnl = filtered_trades['pnl'].sum()
    average_pnl_per_trade = filtered_trades['pnl'].mean()
    max_trade_gain_pnl = filtered_trades['pnl'].max()
    max_trade_loss_pnl = filtered_trades['pnl'].min()
    max_drawdown = daily_perf_df['Drawdown'].min() * 100

    if print_summary:
        print("\nTrade Summary:")
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate (%): {win_rate * 100:.2f}%")
        print(f"Total Return (%): {total_return * 100:.2f}%")
        print(f"Average Return Per Trade: {average_return_per_trade * 100:.2f}%")
        print(f"Max Trade Gain (%): {max_trade_gain_return * 100:.2f}%")
        print(f"Max Trade Loss (%): {max_trade_loss_return * 100:.2f}%")
        print(f"Total PnL ($): ${total_pnl:,.2f}")
        print(f"Average PnL Per Trade ($): ${average_pnl_per_trade:,.2f}")
        print(f"Max Trade Gain ($): ${max_trade_gain_pnl:,.2f}")
        print(f"Max Trade Loss ($): ${max_trade_loss_pnl:,.2f}")
        print(f"Max Drawdown (%): {max_drawdown:.2f}%")

    # Return all metrics as a tuple
    return total_trades, win_rate, total_return, average_return_per_trade, max_trade_gain_return, max_trade_loss_return, total_pnl, average_pnl_per_trade, max_trade_gain_pnl, max_trade_loss_pnl, max_drawdown