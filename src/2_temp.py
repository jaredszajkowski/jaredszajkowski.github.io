import matplotlib.pyplot as plt
import pandas as pd

from load_data import load_data
from settings import config

# Get the data directory from the configuration
DATA_DIR = config("DATA_DIR")

TICKERS = ["BTC-USD", "ETH-USD", "SOL-USD"]
MA_DAYS = [28]
START_DATE = "2024-06-01"
END_DATE = "2024-06-30"

def load_crypto_data(
    tickers: list,
    base_directory,
    start_date: str,
    end_date: str,
) -> dict:
    """
    Loads minute-level data for multiple crypto tickers from Coinbase source.

    Parameters:
    - tickers: list of strings, e.g., ["BTC-USD", "ETH-USD", "SOL-USD"]
    - base_directory: path to your data directory (from config)
    - start_date: optional string, e.g., "2023-01-01"
    - end_date: optional string, e.g., "2023-12-31"

    Returns:
    - dict of DataFrames keyed by ticker
    """
    data = {}
    for ticker in tickers:
        df = load_data(
            base_directory=base_directory,
            ticker=ticker,
            source="Coinbase",
            asset_class="Cryptocurrencies",
            timeframe="Minute",
            file_format="pickle",
        )
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Apply date filtering if specified
        if start_date:
            df = df[df.index >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df.index <= pd.to_datetime(end_date)]

        data[ticker] = df

    return data


crypto_data = load_crypto_data(
    tickers=TICKERS,
    base_directory=DATA_DIR,
    start_date=START_DATE,
    end_date=END_DATE,
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

def prepare_crypto_indicators(
    data: dict,
    rsi_period: int = 14,
    ma_days: list = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70]
) -> dict:
    """
    Adds RSI and daily moving averages to each crypto DataFrame.

    Parameters:
    - data: dict of DataFrames keyed by ticker
    - rsi_period: RSI lookback (default=14)
    - ma_days: list of MA durations (in days) for trend allocation

    Returns:
    - dict of enriched DataFrames with 'RSI' and MA columns
    """
    enriched_data = {}

    for ticker, df in data.items():
        df = df.copy()
        df["RSI"] = calculate_rsi(df["close"], period=rsi_period)

        for day in ma_days:
            window = 1440 * day  # 1440 minutes in a day
            df[f"MA_{day}d"] = df["close"].rolling(window=window, min_periods=1).mean()

        enriched_data[ticker] = df

    return enriched_data

enriched_data = prepare_crypto_indicators(
    data=crypto_data,
    rsi_period=14,
    ma_days=MA_DAYS,
)

def backtest_rsi_multi_asset_strategy(
    data: dict,
    initial_capital: float,
    rsi_threshold: float,
    trailing_stop_pct: float,
    ma_days: list,
) -> pd.DataFrame:
    """
    Multi-asset backtest using RSI threshold + MA filter + trailing stop.
    
    Capital is shared across all assets. Each asset trades independently.

    Parameters:
    - data: dict of enriched DataFrames keyed by asset symbol (must have RSI and MA columns)
    - initial_capital: starting cash
    - rsi_threshold: RSI entry trigger (e.g., 30)
    - trailing_stop_pct: trailing stop trigger (e.g., 0.02)
    - ma_days: list of moving average day lengths

    Returns:
    - DataFrame of all trades across assets
    """
    # Merge index across all assets
    all_timestamps = sorted(set().union(*[df.index for df in data.values()]))
    
    # Initialize tracking variables
    cash = initial_capital
    trades = []
    positions = {symbol: None for symbol in data}
    
    # Prep asset DataFrames
    for df in data.values():
        df.sort_index(inplace=True)

    for timestamp in all_timestamps:
        for symbol, df in data.items():
            if timestamp not in df.index:
                continue

            row = df.loc[timestamp]

            # Current position state
            position = positions[symbol]

            # --- ENTRY ---
            if position is None:
                # Need previous RSI point to trigger
                i = df.index.get_loc(timestamp)
                if i == 0:
                    continue
                prev_rsi = df.iloc[i - 1]["RSI"]

                if prev_rsi < rsi_threshold:
                    ma_passes = sum(row["close"] > row[f"MA_{day}d"] for day in ma_days)
                    allocation_pct = ma_passes * (1 / len(ma_days))
                    if allocation_pct == 0:
                        continue

                    capital_to_use = cash * allocation_pct
                    entry_price = row["open"]
                    quantity = capital_to_use / entry_price

                    positions[symbol] = {
                        "entry_time": timestamp,
                        "entry_price": entry_price,
                        "peak_price": entry_price,
                        "quantity": quantity,
                        "allocation_pct": allocation_pct,
                    }

                    cash -= quantity * entry_price

            # --- EXIT ---
            elif position is not None:
                peak_price = max(position["peak_price"], row["high"])
                stop_price = peak_price * (1 - trailing_stop_pct)

                if row["low"] <= stop_price:
                    exit_price = stop_price
                    quantity = position["quantity"]
                    pnl = quantity * (exit_price - position["entry_price"])
                    return_pct = (exit_price - position["entry_price"]) / position["entry_price"]

                    cash += quantity * exit_price

                    trades.append({
                        "asset": symbol,
                        "entry_time": position["entry_time"],
                        "exit_time": timestamp,
                        "entry_price": position["entry_price"],
                        "exit_price": exit_price,
                        "quantity": quantity,
                        "allocation_pct": position["allocation_pct"],
                        "pnl": pnl,
                        "return_pct": return_pct * 100,
                        "cash": cash,
                    })

                    positions[symbol] = None
                else:
                    positions[symbol]["peak_price"] = peak_price

    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        trades_df["cumulative_pnl"] = trades_df["pnl"].cumsum()
        trades_df["equity"] = trades_df["cumulative_pnl"] + initial_capital
        trades_df["cumulative_return"] = trades_df["equity"] / initial_capital - 1

    # Export trades DataFrame
    trades_df.to_csv("multi_asset_trades.csv", index=False)

    return trades_df

trades = backtest_rsi_multi_asset_strategy(
    data=enriched_data,
    initial_capital=100_000,
    rsi_threshold=30,
    trailing_stop_pct=0.02,
    ma_days=MA_DAYS,
)

# def compute_daily_performance(
#     trades: pd.DataFrame,
#     data: dict,
# ) -> pd.DataFrame:
#     """
#     Computes daily portfolio equity and return from multi-asset trades and prices.

#     Parameters:
#     - trades: DataFrame of trades from backtest_rsi_multi_asset_strategy
#     - data: dict of price DataFrames per asset (with 'close'), indexed by datetime

#     Returns:
#     - DataFrame indexed by date with:
#         - equity
#         - cash
#         - daily_return
#         - cumulative_return
#         - [position_{asset}]
#         - [price_{asset}]
#     """
#     if trades.empty:
#         return pd.DataFrame()

#     # Resample asset prices to daily
#     price_df = pd.DataFrame()
#     for symbol, df in data.items():
#         daily_prices = df["close"].resample("D").last().rename(f"price_{symbol}")
#         price_df = pd.concat([price_df, daily_prices], axis=1)

#     # Time range
#     start = trades["entry_time"].min().normalize()
#     end = trades["exit_time"].max().normalize()
#     dates = pd.date_range(start, end, freq="D")

#     # Initialize performance frame
#     perf_df = pd.DataFrame(index=dates)
#     perf_df = perf_df.merge(price_df, left_index=True, right_index=True, how="left")
#     perf_df.fillna(method="ffill", inplace=True)

#     # Initialize state
#     cash = trades.iloc[0]["cash"] - trades.iloc[0]["pnl"]
#     equity = cash
#     positions = {symbol: 0.0 for symbol in data}
#     trade_idx = 0

#     for date in perf_df.index:
#         # Apply trades that happen on this day
#         while trade_idx < len(trades):
#             trade = trades.iloc[trade_idx]
#             asset = trade["asset"]
#             entry_day = pd.to_datetime(trade["entry_time"]).normalize()
#             exit_day = pd.to_datetime(trade["exit_time"]).normalize()

#             if entry_day == date:
#                 positions[asset] += trade["quantity"]
#                 cash -= trade["quantity"] * trade["entry_price"]
#             if exit_day == date:
#                 positions[asset] -= trade["quantity"]
#                 cash += trade["quantity"] * trade["exit_price"]
#                 trade_idx += 1
#                 continue
#             break

#         # Compute position value + equity
#         position_value = 0.0
#         for symbol, qty in positions.items():
#             price = perf_df.loc[date, f"price_{symbol}"]
#             perf_df.loc[date, f"position_{symbol}"] = qty
#             position_value += qty * price

#         equity = cash + position_value
#         perf_df.loc[date, "cash"] = cash
#         perf_df.loc[date, "equity"] = equity

#     # Calculate performance metrics
#     perf_df["daily_return"] = perf_df["equity"].pct_change().fillna(0)
#     perf_df["cumulative_return"] = (perf_df["equity"] / perf_df["equity"].iloc[0]) - 1

#     return perf_df

# daily_perf = compute_daily_performance(
#     trades=trades,
#     data=enriched_data,
# )

# def compute_daily_performance_multi_asset(trades: pd.DataFrame, prices: dict) -> pd.DataFrame:
#     """
#     Computes daily cash, equity, and position value across multiple crypto assets.

#     Parameters:
#     - trades: DataFrame with trade logs including asset, entry/exit times, quantity, prices, and cash
#     - prices: dict of DataFrames with DateTime index and 'close' column, one per asset

#     Returns:
#     - daily performance DataFrame with columns:
#       ['equity', 'cash', 'position_value', 'daily_return', 'cumulative_return']
#     """
#     if trades.empty:
#         return pd.DataFrame()

#     # Create master date index
#     all_dates = pd.date_range(
#         start=trades["entry_time"].min().normalize(),
#         end=trades["exit_time"].max().normalize(),
#         freq="D",
#     )

#     perf_df = pd.DataFrame(index=all_dates)
#     asset_list = trades["asset"].unique()

#     # Initialize position and cash trackers
#     cash = trades.iloc[0]["cash"] - trades.iloc[0]["pnl"]
#     asset_positions = {symbol: 0.0 for symbol in asset_list}

#     # Merge daily prices
#     daily_prices = {}
#     for asset, df in prices.items():
#         df = df.copy()
#         df.index = pd.to_datetime(df.index)
#         df = df.sort_index()
#         daily_prices[asset] = df["close"].resample("D").last().ffill()

#     # Process daily values
#     for date in perf_df.index:
#         # For each asset, update open positions
#         for asset in asset_list:
#             open_trades = trades[
#                 (trades["asset"] == asset)
#                 & (trades["entry_time"] <= date)
#                 & (trades["exit_time"] > date)
#             ]
#             asset_positions[asset] = open_trades["quantity"].sum()

#         # Update cash if any trades exited today
#         exited_today = trades[trades["exit_time"].dt.normalize() == date]
#         for _, trade in exited_today.iterrows():
#             cash += trade["pnl"]

#         # Compute position value
#         position_value = 0.0
#         for asset, qty in asset_positions.items():
#             price = daily_prices[asset].get(date, pd.NA)
#             if pd.notna(price):
#                 position_value += qty * price

#         equity = cash + position_value

#         perf_df.loc[date, "cash"] = cash
#         perf_df.loc[date, "position_value"] = position_value
#         perf_df.loc[date, "equity"] = equity

#     perf_df["daily_return"] = perf_df["equity"].pct_change().fillna(0)
#     perf_df["cumulative_return"] = (perf_df["equity"] / perf_df["equity"].iloc[0]) - 1

#     return perf_df

# daily_perf = compute_daily_performance_multi_asset(
#     trades=trades,
#     prices=enriched_data,
# )

import pandas as pd

def build_position_ledger(trades: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a daily ledger of crypto quantities and cash based on trade entries and exits.

    Parameters:
    - trades: DataFrame with columns ['asset', 'entry_time', 'exit_time', 'entry_price', 'exit_price', 'quantity', 'pnl']

    Returns:
    - DataFrame indexed by date with columns: cash, <asset>_qty for each asset
    """
    if trades.empty:
        return pd.DataFrame()

    # Normalize times and get full date range
    trades = trades.copy()
    trades["entry_time"] = pd.to_datetime(trades["entry_time"])
    trades["exit_time"] = pd.to_datetime(trades["exit_time"])

    start_date = trades["entry_time"].min().normalize()
    end_date = trades["exit_time"].max().normalize()
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    # Initialize ledger
    assets = trades["asset"].unique()
    ledger = pd.DataFrame(index=dates)
    for asset in assets:
        ledger[f"{asset}_qty"] = 0.0
    ledger["cash"] = 0.0

    # Apply entry and exit impacts
    for _, row in trades.iterrows():
        entry_date = row["entry_time"].normalize()
        exit_date = row["exit_time"].normalize()
        asset = row["asset"]
        qty = row["quantity"]
        entry_cost = qty * row["entry_price"]
        exit_value = qty * row["exit_price"]

        # Subtract entry cost from cash, add quantity
        if entry_date in ledger.index:
            ledger.at[entry_date, "cash"] -= entry_cost
            ledger.at[entry_date, f"{asset}_qty"] += qty

        # Add exit value to cash, remove quantity
        if exit_date in ledger.index:
            ledger.at[exit_date, "cash"] += exit_value
            ledger.at[exit_date, f"{asset}_qty"] -= qty

    return ledger

position_ledger = build_position_ledger(trades)

print(position_ledger)



# def plot_multi_asset_equity_and_drawdown(
#     perf_df: pd.DataFrame,
#     trades: pd.DataFrame,
#     data: dict,
#     title: str = "Multi-Asset Strategy Performance"
# ) -> None:
#     """
#     Plots:
#     - Total equity, cash, and per-asset position values
#     - Cumulative returns (strategy and crypto assets)
#     - Drawdowns (strategy and crypto assets)
#     - Price series and trade markers for BTC, ETH, SOL
#     """
#     if perf_df.empty or trades.empty or "equity" not in perf_df.columns:
#         print("Missing performance or trade data.")
#         return

#     perf_df = perf_df.copy()
#     trades = trades.copy()

#     # Compute portfolio drawdown
#     perf_df["drawdown"] = (perf_df["equity"] - perf_df["equity"].cummax()) / perf_df["equity"].cummax() * 100

#     # Identify asset symbols
#     position_cols = [col for col in perf_df.columns if col.startswith("position_")]
#     asset_symbols = [col.replace("position_", "") for col in position_cols]

#     # Compute position values and crypto drawdowns
#     colors = ["orange", "purple", "brown", "cyan", "magenta"]
#     for symbol in asset_symbols:
#         perf_df[f"value_{symbol}"] = perf_df[f"position_{symbol}"] * perf_df[f"price_{symbol}"]
#         perf_df[f"{symbol}_cum_return"] = (perf_df[f"price_{symbol}"] / perf_df[f"price_{symbol}"].iloc[0]) - 1
#         perf_df[f"{symbol}_drawdown"] = (
#             (perf_df[f"price_{symbol}"] - perf_df[f"price_{symbol}"].cummax()) / perf_df[f"price_{symbol}"].cummax()
#         ) * 100

#     # Compute strategy cumulative return
#     perf_df["strategy_cum_return"] = (perf_df["equity"] / perf_df["equity"].iloc[0]) - 1

#     # Setup plot
#     fig, (ax1, axr, ax2, ax3, ax4, ax5) = plt.subplots(
#         6, 1, figsize=(14, 16), sharex=True, gridspec_kw={"height_ratios": [1, 1, 1, 1, 1, 1]}
#     )

#     # --- ax1: Equity + Cash + Position Values ---
#     ax1.plot(perf_df.index, perf_df["equity"], color="blue", label="Equity")
#     ax1.plot(perf_df.index, perf_df["cash"], color="green", linestyle="--", label="Cash")
#     for i, symbol in enumerate(asset_symbols):
#         ax1.plot(perf_df.index, perf_df[f"value_{symbol}"], linestyle="--", color=colors[i % len(colors)], label=f"{symbol} Value")
#     ax1.set_title(f"{title} - Equity, Cash, Position Values")
#     ax1.set_ylabel("Account Value ($)")
#     ax1.legend()
#     ax1.grid(True)

#     # --- axr: Cumulative Returns ---
#     axr.plot(perf_df.index, perf_df["strategy_cum_return"] * 100, color="blue", label="Strategy Return (%)")
#     for i, symbol in enumerate(asset_symbols):
#         axr.plot(perf_df.index, perf_df[f"{symbol}_cum_return"] * 100, linestyle="--", color=colors[i % len(colors)], label=f"{symbol} Return (%)")
#     axr.set_title("Cumulative Returns")
#     axr.set_ylabel("Return (%)")
#     axr.legend()
#     axr.grid(True)

#     # --- ax2: Drawdowns ---
#     ax2.plot(perf_df.index, perf_df["drawdown"], color="red", linestyle="--", label="Strategy Drawdown")
#     for i, symbol in enumerate(asset_symbols):
#         ax2.plot(perf_df.index, perf_df[f"{symbol}_drawdown"], linestyle="--", color=colors[i % len(colors)], label=f"{symbol} Drawdown")
#     ax2.set_title("Drawdowns (%)")
#     ax2.set_ylabel("Drawdown (%)")
#     ax2.legend()
#     ax2.grid(True)

#     # --- ax3-ax5: Price plots with trade markers ---
#     price_axes = [ax3, ax4, ax5]
#     for i, symbol in enumerate(asset_symbols):
#         df = data[symbol].copy()
#         df.index = pd.to_datetime(df.index)
#         plot_df = df[df.index >= trades["entry_time"].min()]
#         ax = price_axes[i]
#         ax.plot(plot_df.index, plot_df["close"], color="gray", label=f"{symbol} Price")

#         # Mark trades
#         asset_trades = trades[trades["asset"] == symbol]
#         for _, trade in asset_trades.iterrows():
#             entry_time = trade["entry_time"]
#             exit_time = trade["exit_time"]
#             if entry_time in plot_df.index:
#                 ax.plot(entry_time, plot_df.loc[entry_time, "close"], marker="^", color="green", label="Entry" if "Entry" not in ax.get_legend_handles_labels()[1] else "")
#             if exit_time in plot_df.index:
#                 ax.plot(exit_time, plot_df.loc[exit_time, "close"], marker="v", color="red", label="Exit" if "Exit" not in ax.get_legend_handles_labels()[1] else "")
#         ax.set_title(f"{symbol} Price with Trades")
#         ax.set_ylabel("Price ($)")
#         ax.legend()
#         ax.grid(True)

#     plt.tight_layout()
#     plt.show()





print(trades)
print(daily_perf)
print("\nTotal Trades:", len(trades))
print("Average Return: {:.2f}%".format(trades["return_pct"].mean()))
print("Win Rate: {:.2f}%".format((trades["return_pct"] > 0).mean() * 100))
print("Total PnL: ${:.2f}".format(trades["pnl"].sum()))
print("Average PnL: ${:.2f}".format(trades["pnl"].mean()))
print("Max Gain Pnl: ${:.2f}".format(trades["pnl"].max()))
print("Max Loss Pnl: ${:.2f}".format(trades["pnl"].min()))

# plot_multi_asset_equity_and_drawdown(
#     perf_df=daily_perf,
#     trades=trades,
#     data=enriched_data,
#     title="Multi-Asset Strategy: BTC, ETH, SOL"
# )