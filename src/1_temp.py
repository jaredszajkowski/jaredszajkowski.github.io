import matplotlib.pyplot as plt
import pandas as pd

from load_data import load_data
from settings import config

# Get the data directory from the configuration
DATA_DIR = config("DATA_DIR")

crypto_ticker = "BTC-USD"

df = load_data(
    base_directory=DATA_DIR,
    ticker=crypto_ticker,
    source="Coinbase",
    asset_class="Cryptocurrencies",
    timeframe="Minute",
    file_format="pickle",
)

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculates the Relative Strength Index (RSI) for a price series."""
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def plot_price_and_rsi(df: pd.DataFrame, start_date: str, end_date: str, period: int = 14) -> None:
    """
    Plots price and RSI over a selected date range.
    
    Parameters:
    - df: DataFrame with a datetime index and a 'close' column.
    - start_date: string, e.g. "2023-01-01 00:00"
    - end_date: string, e.g. "2023-01-01 12:00"
    - period: RSI lookback period (default=14)
    """
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    df["RSI"] = calculate_rsi(df["close"], period=period)

    mask = (df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))
    df_slice = df.loc[mask]

    if df_slice.empty:
        print("No data in the specified date range.")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    # Price plot
    ax1.plot(df_slice.index, df_slice["close"], label="Price", color="blue")
    ax1.set_title(f"Price and RSI ({period}) from {start_date} to {end_date}")
    ax1.set_ylabel("Price")
    ax1.grid(True)
    ax1.legend()

    # RSI plot
    ax2.plot(df_slice.index, df_slice["RSI"], label="RSI", color="purple")
    ax2.axhline(70, color="red", linestyle="--", linewidth=1)
    ax2.axhline(30, color="green", linestyle="--", linewidth=1)
    ax2.set_ylabel("RSI")
    ax2.set_xlabel("Time")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()

def backtest_rsi_dynamic_allocation(
    df: pd.DataFrame,
    initial_capital: float = 100_000,
    rsi_col: str = "RSI",
    entry_rsi: float = 30,
    trailing_stop_pct: float = 0.02,
    ma_days: list = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70]
) -> pd.DataFrame:
    """
    Backtest with RSI < entry_rsi and dynamic position sizing based on price > multiple MAs.

    Capital is scaled by 10% per MA the price is above. Tracks cash, position size, equity.
    """
    df = df.copy()
    df = df.dropna(subset=[rsi_col])
    df.index = pd.to_datetime(df.index)

    # Compute moving averages
    for day in ma_days:
        window = 1440 * day
        df[f"MA_{day}d"] = df["close"].rolling(window=window, min_periods=1).mean()

    in_position = False
    trades = []
    cash = initial_capital
    entry_price = 0.0
    peak_price = 0.0
    position_crypto = 0.0
    entry_time = None

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i - 1]

        # --- ENTRY ---
        if not in_position and prev_row[rsi_col] < entry_rsi:
            # Count how many MAs price is above
            ma_passes = sum(row["close"] > row[f"MA_{day}d"] for day in ma_days)
            # allocation_pct = ma_passes * 0.10  # 10% per MA
            allocation_pct = ma_passes * (1 / len(ma_days)) # equal weight % per MA

            if allocation_pct == 0:
                continue  # no trade if price is below all MAs

            capital_to_use = cash * allocation_pct
            entry_price = row["open"]
            position_crypto = capital_to_use / entry_price
            peak_price = entry_price
            entry_time = row.name
            in_position = True
            continue

        # --- EXIT ---
        if in_position:
            peak_price = max(peak_price, row["high"])
            stop_price = peak_price * (1 - trailing_stop_pct)

            if row["low"] <= stop_price:
                exit_price = stop_price
                exit_time = row.name
                pnl = position_crypto * (exit_price - entry_price)
                return_pct = (exit_price - entry_price) / entry_price
                cash += pnl
                equity = cash

                trades.append({
                    "entry_time": entry_time,
                    "exit_time": exit_time,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "return_pct": return_pct * 100,
                    "pnl": pnl,
                    "crypto_position": position_crypto,
                    "allocation_pct": allocation_pct,
                    "cash": cash,
                    "equity": equity,
                })

                # Reset position
                in_position = False
                position_crypto = 0.0
                entry_price = 0.0
                peak_price = 0.0

    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        trades_df["cumulative_pnl"] = trades_df["pnl"].cumsum()
        trades_df["cumulative_return"] = (trades_df["equity"] / initial_capital) - 1

    return trades_df

def compute_daily_performance(trades: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes daily equity and return from trade logs and price data.

    Returns a daily DataFrame with:
    - equity
    - cash
    - crypto_position
    - crypto_price
    - daily_return
    """
    if trades.empty:
        return pd.DataFrame()

    df = df.copy()
    df.index = pd.to_datetime(df.index)
    crypto_daily = df["close"].resample("D").last().to_frame("crypto_price")

    # Create daily time range
    start = trades["entry_time"].min().normalize()
    end = trades["exit_time"].max().normalize()
    dates = pd.date_range(start, end, freq="D")
    perf_df = pd.DataFrame(index=dates)

    perf_df["crypto_price"] = crypto_daily["crypto_price"]
    perf_df["crypto_price"] = perf_df["crypto_price"].ffill()

    # Track state over time
    cash = trades.iloc[0]["cash"] - trades.iloc[0]["pnl"]
    equity = cash
    position = 0.0
    trade_idx = 0

    for date in perf_df.index:
        # Check for any trades on this date
        while trade_idx < len(trades):
            trade = trades.iloc[trade_idx]
            if pd.to_datetime(trade["entry_time"]).normalize() == date:
                position += trade["crypto_position"]
                cash -= trade["crypto_position"] * trade["entry_price"]
            if pd.to_datetime(trade["exit_time"]).normalize() == date:
                cash += trade["crypto_position"] * trade["exit_price"]
                position -= trade["crypto_position"]
                trade_idx += 1
                continue
            break

        # Calculate equity
        crypto_price = perf_df.loc[date, "crypto_price"]
        equity = cash + (position * crypto_price)

        perf_df.loc[date, "cash"] = cash
        perf_df.loc[date, "crypto_position"] = position
        perf_df.loc[date, "equity"] = equity

    # Daily returns
    perf_df["daily_return"] = perf_df["equity"].pct_change().fillna(0)
    perf_df["cumulative_return"] = (perf_df["equity"] / perf_df["equity"].iloc[0]) - 1

    return perf_df

def plot_equity_and_drawdown(trades: pd.DataFrame, df: pd.DataFrame, perf_df: pd.DataFrame, title: str = "Strategy Performance") -> None:
    """
    Plots:
    - Trade-based equity curve
    - Cumulative returns
    - Drawdowns (trade-based and daily)
    - Crypto price with entry/exit markers
    - Overlays daily equity/drawdown from perf_df if provided
    """
    if trades.empty:
        print("No trades to plot.")
        return

    trades = trades.copy().sort_values("exit_time").reset_index(drop=True)
    trades["entry_time"] = pd.to_datetime(trades["entry_time"])
    trades["exit_time"] = pd.to_datetime(trades["exit_time"])

    # Initial capital
    initial_capital = trades.loc[0, "cash"] - trades.loc[0, "pnl"]
    trades["cumulative_return"] = (trades["equity"] / initial_capital) - 1
    trades["peak"] = trades["equity"].cummax()
    trades["drawdown_pct"] = (trades["equity"] - trades["peak"]) / trades["peak"] * 100

    # Crypto prep
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    crypto_df = df.loc[trades["entry_time"].min():trades["exit_time"].max()].resample("1min").ffill()
    crypto_df["crypto_cum_return"] = (crypto_df["close"] / crypto_df["close"].iloc[0]) - 1

    # Interpolated strategy return series
    strategy_return_series = pd.Series(index=crypto_df.index, dtype=float)
    strategy_return_series.loc[trades["exit_time"]] = trades["cumulative_return"].values
    strategy_return_series = strategy_return_series.ffill().fillna(0)

    # Optional: daily drawdown and return overlays
    perf_df = perf_df.copy() if perf_df is not None and not perf_df.empty else None
    if perf_df is not None:
        perf_df["daily_drawdown"] = (perf_df["equity"] - perf_df["equity"].cummax()) / perf_df["equity"].cummax() * 100
        perf_df["daily_cum_return"] = (perf_df["equity"] / perf_df["equity"].iloc[0]) - 1

    # --- Plot layout ---
    fig, (ax1, axr, ax2, ax3) = plt.subplots(
        4, 1, figsize=(14, 12), sharex=True, gridspec_kw={"height_ratios": [1, 1, 1, 1]}
    )

    # Equity Curve (with cash and position overlays)
    ax1.plot(trades["exit_time"], trades["equity"], color="blue", label="Trade Equity")
    
    if perf_df is not None:
        # Dashed equity overlay
        ax1.plot(perf_df.index, perf_df["equity"], color="blue", linestyle="--", alpha=0.8, label="Daily Equity")
        
        # Cash (dashed)
        ax1.plot(perf_df.index, perf_df["cash"], color="green", linestyle="--", alpha=0.6, label="Daily Cash")
        
        # Position value = equity - cash
        position_value = perf_df["equity"] - perf_df["cash"]
        ax1.plot(perf_df.index, position_value, color="orange", linestyle="--", alpha=0.6, label="Daily Position Value")

    ax1.set_title(f"{title} - Equity Curve with Cash & Position Value")
    ax1.set_ylabel("Account Value ($)")
    ax1.grid(True)
    ax1.legend()


    # Cumulative returns
    axr.plot(crypto_df.index, crypto_df["crypto_cum_return"] * 100, color="gray", linestyle="--", label="Crypto Return (%)")
    axr.plot(strategy_return_series.index, strategy_return_series * 100, color="blue", label="Strategy Return (%)")
    axr.plot(perf_df.index, perf_df["daily_cum_return"] * 100, color="green", linestyle="--", alpha=0.7, label="Strategy Return (%) (Daily)")
    axr.set_title("Cumulative Returns")
    axr.set_ylabel("Return (%)")
    axr.grid(True)
    axr.legend()

    # Drawdown
    # Crypto drawdown
    crypto_df["crypto_peak"] = crypto_df["close"].cummax()
    crypto_df["crypto_drawdown_pct"] = (crypto_df["close"] - crypto_df["crypto_peak"]) / crypto_df["crypto_peak"] * 100

    # Plot both drawdowns
    ax2.plot(trades["exit_time"], trades["drawdown_pct"], color="red", label="Trade Drawdown")
    ax2.plot(crypto_df.index, crypto_df["crypto_drawdown_pct"], color="black", linestyle="--", label="Crypto Drawdown")

    if perf_df is not None:
        ax2.plot(perf_df.index, perf_df["daily_drawdown"], color="red", linestyle="--", alpha=0.7, label="Daily Drawdown")
    ax2.set_title("Drawdown (%)")
    ax2.set_ylabel("Drawdown (%)")
    ax2.grid(True)
    ax2.legend()

    # Crypto price with entry/exit markers
    ax3.plot(crypto_df.index, crypto_df["close"], color="gray", label="Crypto Price")

    for _, trade in trades.iterrows():
        if trade["entry_time"] in crypto_df.index:
            ax3.plot(trade["entry_time"], crypto_df.loc[trade["entry_time"], "close"], marker="^", color="green", label="Entry" if "Entry" not in ax3.get_legend_handles_labels()[1] else "")
        if trade["exit_time"] in crypto_df.index:
            ax3.plot(trade["exit_time"], crypto_df.loc[trade["exit_time"], "close"], marker="v", color="red", label="Exit" if "Exit" not in ax3.get_legend_handles_labels()[1] else "")

    ax3.set_title("Crypto Price with Trade Markers")
    ax3.set_ylabel("Price ($)")
    ax3.set_xlabel("Time")
    ax3.grid(True)
    ax3.legend()

    plt.tight_layout()
    plt.show()





# df = df[df.index >= "2022-01-01"]
# df = df[(df.index >= "2024-01-01") & (df.index <= "2024-12-31")]
# df = df[df.index >= "2024-07-24"]
# df = df[df.index >= "2025-01-01"]
# df = df[(df.index >= "2024-06-01") & (df.index <= "2024-08-31")]
df = df[(df.index >= "2025-01-01") & (df.index <= "2025-06-30")]

# plot_price_and_rsi(df, start_date="2025-06-24 19:00", end_date="2025-07-24 19:00", period=14)

df["RSI"] = calculate_rsi(df["close"], period=14)
# trades = backtest_rsi_trailing_stop(
#     df=df,
#     initial_capital=100_000,
#     rsi_col="RSI",
#     entry_rsi=30,
#     trailing_stop_pct=0.02,
# )
# trades = backtest_rsi_trailing_stop_with_ma_filter(
#     df,
#     initial_capital=100_000,
#     rsi_col="RSI",
#     entry_rsi=30,
#     trailing_stop_pct=0.02,
#     ma_days=28  # Only trade when price > X-day MA
# )
trades = backtest_rsi_dynamic_allocation(
    df=df,
    initial_capital=100_000,
    rsi_col="RSI",
    entry_rsi=30,
    trailing_stop_pct=0.02,
    ma_days=[28]  # Trade when price > multiple MAs
)
daily_perf = compute_daily_performance(
    trades=trades,
    df=df
)

# print(df)
print(trades)
print(daily_perf)
print(f"Trades Summary: {crypto_ticker}")
print("\nTotal Trades:", len(trades))
print("Average Return: {:.2f}%".format(trades["return_pct"].mean()))
print("Win Rate: {:.2f}%".format((len(trades[trades["return_pct"] > 0]) / len(trades) * 100)))
print("Total PnL: ${:.2f}".format(trades["pnl"].sum()))
print("Average PnL: ${:.2f}".format(trades["pnl"].mean()))
print("Max Gain Pnl: ${:.2f}".format(trades["pnl"].max()))
print("Max Loss Pnl: ${:.2f}".format(trades["pnl"].min()))
plot_equity_and_drawdown(
    trades=trades,
    df=df,
    perf_df=daily_perf,
    title="Crypto RSI < 30 + MA Filter + 2% Trailing Stop + Dynamic Allocation"
)