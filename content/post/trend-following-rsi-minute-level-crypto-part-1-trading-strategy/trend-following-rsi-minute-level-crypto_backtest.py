import itertools as it
import os
import pandas as pd
import sys
import time
import zipfile

from datetime import datetime, timedelta
from pathlib import Path
from tqdm import tqdm

# Add the source subdirectory to the system path to allow import config from settings.py
try:
    # Works for .py files
    current_directory = Path(__file__).resolve().parent
except NameError:
    # Fallback for notebooks / interactive shells
    current_directory = Path(os.getcwd()).resolve()

website_base_directory = current_directory.parent.parent.parent
src_directory = website_base_directory / "src"
sys.path.append(str(src_directory)) if str(src_directory) not in sys.path else None

# Import settings.py
from settings import config

# Add configured directories from config to path
SOURCE_DIR = config("SOURCE_DIR")
sys.path.append(str(Path(SOURCE_DIR))) if str(Path(SOURCE_DIR)) not in sys.path else None

# Add other configured directories
BASE_DIR = config("BASE_DIR")
CONTENT_DIR = config("CONTENT_DIR")
POSTS_DIR = config("POSTS_DIR")
PAGES_DIR = config("PAGES_DIR")
PUBLIC_DIR = config("PUBLIC_DIR")
SOURCE_DIR = config("SOURCE_DIR")
DATA_DIR = config("DATA_DIR")
DATA_MANUAL_DIR = config("DATA_MANUAL_DIR")

# Print system path
# for i, path in enumerate(sys.path):
#     print(f"{i}: {path}")

from add_rsi_ma_bb import add_rsi_ma_bb
from analyze_trades import analyze_trades
from backtest_rsi_multi_asset_strategy import backtest_rsi_multi_asset_strategy
from compute_daily_performance import compute_daily_performance
from create_signals import create_signals
from load_crypto_data import load_crypto_data
from plot_multi_asset_equity_and_drawdown import plot_multi_asset_equity_and_drawdown
from summary_stats import summary_stats

# Variables
INITIAL_CAPITAL = 10_000
START_DATE = "2019-01-01"
END_DATE = "2019-12-31"
# ORDER_ENTRY = "limit" # {"market", "limit"}
USE_RSI = True
USE_MA = True
# USE_BBANDS = True
# BB_WINDOW = 20
# BB_NUM_STD = 2.0
# BB_RULE = "touch_lower"  # {"touch_lower", "cross_up_from_below", "below_lower"}
# TRADING_FEES = True
TRADE_TAKER_FEE = 0.0020  # 0.20% or 20 bps
TRADE_MAKER_FEE = 0.0010  # 0.10% or 10 bps

# Parameter grid
param_grid = {
    "tickers": [["BTC-USD"]],
    # "tickers": [["BTC-USD"], ["ETH-USD"], ["SOL-USD"], ["BTC-USD", "ETH-USD"], ["BTC-USD", "ETH-USD", "SOL-USD"]],
    "ma_days": [
        [],
        [7],
        [14],
        [21],
        [28],
        [35],
        [42],
        [49],
    ],
    "rsi_period": [
        6,
        8,
        10,
        12,
        14,
        16,
        18,
        20,
        22,
        24,
    ],
    "rsi_threshold": [
        12,
        14,
        16, 
        18, 
        20, 
        22, 
        24, 
        26, 
        28, 
        30,
    ],
    "trailing_stop_pct": [
        0.010, 
        0.015, 
        0.020, 
        0.025, 
        0.030,
    ],
    "order_entry": [
        "market",
        "limit",
    ],
    "use_bbands": [
        True,
        False,
    ],
    "bb_window": [
        20,
    ],
    "bb_num_std": [
        2.0,
    ],
    "bb_rule": [
        "touch_lower",
        # "cross_up_from_below",
        # "below_lower",
    ],
    "trading_fees": [
        True,
        # False,
    ],
}

def _stringify_list(x):
    return ", ".join(map(str, x)) if isinstance(x, (list, tuple)) else str(x)

def _fmt_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"

# Build parameter combinations
keys = list(param_grid.keys())
combos = list(it.product(*[param_grid[k] for k in keys]))
total_combos = len(combos)

results_list = []
overall_start = time.time()

# Runtime tracking
ema_runtime = None  # all runs
alpha = 0.2
success_count = 0
success_elapsed = 0.0
success_ema_runtime = None

# Print details - no progress bar
# iterator = enumerate(combos, start=1)  # or tqdm(enumerate(...), total=total_combos)

# Progress bar
iterator = tqdm(enumerate(combos, start=1), total=total_combos, desc="Backtesting", ncols=100)

for idx, combo in iterator:
    combo_start_time = time.time()
    params = dict(zip(keys, combo))
    tickers         = params["tickers"]
    ma_days         = params["ma_days"]
    rsi_period      = params["rsi_period"]
    rsi_threshold   = params["rsi_threshold"]
    trailing_stop   = params["trailing_stop_pct"]
    order_entry     = params["order_entry"]
    use_bbands      = params["use_bbands"]
    bb_window       = params["bb_window"]
    bb_num_std      = params["bb_num_std"]
    bb_rule         = params["bb_rule"]
    trading_fees    = params["trading_fees"]

    # Print details - no progress bar
    # print(f"\n[{idx}/{total_combos}] TICKERS={tickers}, MA_DAYS={ma_days}, "
    #       f"RSI_PERIOD={rsi_period}, RSI_THRESHOLD={rsi_threshold}, STOP={trailing_stop}")

    signals_df = None
    trades_df = None
    daily_perf_df = None
    sum_stats_df = None
    error_msg = None
    success = True

    try:
        # Create MA_Days string for filename
        if ma_days == []:
            temp_ma_days = "[0]"
        else:
            temp_ma_days = ma_days

        # Create trailing stop string for filename
        temp_trailing_stop = f"{trailing_stop:.3f}"

        # Base title name
        base_title_name = f"{START_DATE}_{END_DATE}_{tickers}_MA-{temp_ma_days}_RP-{rsi_period}_RT-{rsi_threshold}_TS-{temp_trailing_stop}_{order_entry}"

        # Create title name
        if use_bbands == True:
            bb_part = f"BBR-{bb_rule}_BBW-{bb_window}_BBS-{bb_num_std}"
            if trading_fees == True:
                title_name = f"{base_title_name}_{bb_part}_TF"
            else:
                title_name = f"{base_title_name}_{bb_part}"
        else:
            if trading_fees == True:
                title_name = f"{base_title_name}_TF"
            else:
                title_name = f"{base_title_name}"

        
        
        # Create ZIP file name
        zip_name = f"{title_name}.zip"

        crypto_prices_df = load_crypto_data(
            tickers=tickers,
            base_directory=DATA_DIR,
            start_date=START_DATE,
            end_date=END_DATE,
        )

        crypto_prices_technical_df = add_rsi_ma_bb(
            tickers=tickers,
            data=crypto_prices_df,
            rsi_period=rsi_period,
            ma_days=ma_days,
            bb_window=bb_window,
            bb_num_std=bb_num_std,
        )

        signals_df = create_signals(
            tickers=tickers,
            data=crypto_prices_technical_df,
            use_rsi=USE_RSI,
            rsi_threshold=rsi_threshold,
            use_ma=USE_MA,
            ma_days=ma_days,
            use_bbands=use_bbands,
            bb_rule=bb_rule,
        )

        trades_df = backtest_rsi_multi_asset_strategy(
            tickers=tickers,
            prices=crypto_prices_technical_df,
            signals=signals_df,
            initial_capital=INITIAL_CAPITAL,
            rsi_threshold=rsi_threshold,
            trailing_stop_pct=trailing_stop,
            ma_days=ma_days,
            order_entry=order_entry,
            trading_fees=trading_fees,
            trade_taker_fee=TRADE_TAKER_FEE,
            trade_maker_fee=TRADE_MAKER_FEE,
        )

        daily_perf_df = compute_daily_performance(
            tickers=tickers,
            data=crypto_prices_technical_df,
            trades=trades_df,
            initial_capital=INITIAL_CAPITAL,
        )

        sum_stats_df = summary_stats(
            fund_list=tickers,
            df=daily_perf_df[['Return']],
            period="Daily",
            use_calendar_days=True,
            excel_export=False,
            pickle_export=False,
            output_confirmation=False,
        )

        plot_multi_asset_equity_and_drawdown(
            tickers=tickers,
            daily_perf=daily_perf_df,
            trades=trades_df,
            data=crypto_prices_technical_df,
            title=title_name,
            show_plot=False,
            export_plot=True,
            export_dir=current_directory,
        )

        (
            total_trades,
            win_rate,
            total_return,
            average_return_per_trade,
            max_trade_gain_return,
            max_trade_loss_return,
            total_pnl,
            average_pnl_per_trade,
            max_trade_gain_pnl,
            max_trade_loss_pnl,
            max_drawdown,
        ) = analyze_trades(
            trades_df=trades_df,
            daily_perf_df=daily_perf_df,
            print_summary=False,
        )

    except Exception as e:
        success = False
        error_msg = str(e)
        total_trades = win_rate = total_return = average_return_per_trade = None
        max_trade_gain_return = max_trade_loss_return = None
        total_pnl = average_pnl_per_trade = None
        max_trade_gain_pnl = max_trade_loss_pnl = None
        max_drawdown = None

    # Timing updates
    combo_runtime = time.time() - combo_start_time
    ema_runtime = combo_runtime if ema_runtime is None else alpha * combo_runtime + (1 - alpha) * ema_runtime
    elapsed = time.time() - overall_start
    avg_runtime_all = elapsed / idx

    # Update success-only metrics
    if success:
        success_count += 1
        success_elapsed += combo_runtime
        success_ema_runtime = (
            combo_runtime if success_ema_runtime is None
            else alpha * combo_runtime + (1 - alpha) * success_ema_runtime
        )

    # --- ETA calculation preferring success-only data ---
    remaining = total_combos - idx
    if success_count > 0:
        avg_success = success_elapsed / success_count
        # Prefer EMA of successful runs if we have multiple; else use simple mean
        basis = "EMA(success)" if success_count > 1 and success_ema_runtime is not None else "Avg(success)"
        eta_sec = remaining * (success_ema_runtime if basis.startswith("EMA") else avg_success)
    else:
        # Fallback to overall EMA/avg (includes errors)
        basis = "EMA(all)" if idx > 1 and ema_runtime is not None else "Avg(all)"
        eta_sec = remaining * (ema_runtime if basis.startswith("EMA") else avg_runtime_all)

    finish_time = datetime.now() + timedelta(seconds=eta_sec)

     # Progress bar
    iterator.set_postfix({
        # "last": _fmt_duration(combo_runtime),
        # "elapsed": _fmt_duration(elapsed),
        # "eta": _fmt_duration(eta_sec),
        # "basis": basis,
        "finish": finish_time.strftime("%H:%M:%S")
    })

    # Print details - no progress bar
    # print(
    #     f"   Elapsed: {_fmt_duration(elapsed)} | "
    #     f"Last: {_fmt_duration(combo_runtime)} | "
    #     f"ETA: {_fmt_duration(eta_sec)} via {basis} "
    #     f"(finish ~ {finish_time.strftime('%Y-%m-%d %H:%M:%S')})"
    # )

    # print(combo)

    # Store results
    results_list.append({
        # --- parameter fields ---
        "TICKERS": _stringify_list(tickers),
        "MA_DAYS": _stringify_list(ma_days),
        "INITIAL_CAPITAL": INITIAL_CAPITAL,
        "RSI_PERIOD": rsi_period,
        "RSI_THRESHOLD": rsi_threshold,
        "TRAILING_STOP_PCT": trailing_stop,
        "START_DATE": START_DATE,
        "END_DATE": END_DATE,
        "Total Trades": total_trades,
        "Win Rate": win_rate,
        "Total Return": total_return,
        "Average Return Per Trade": average_return_per_trade,
        "Max Trade Gain (%)": max_trade_gain_return,
        "Max Trade Loss (%)": max_trade_loss_return,
        "Total PnL": total_pnl,
        "Average PnL Per Trade": average_pnl_per_trade,
        "Max Trade Gain ($)": max_trade_gain_pnl,
        "Max Trade Loss ($)": max_trade_loss_pnl,

        # --- summary_stats fields (None if sum_stats_df is None) ---
        "Annualized Mean Return": sum_stats_df.loc['Return']['Annualized Mean'] if sum_stats_df is not None else None,
        "Annualized Volatility": sum_stats_df.loc['Return']['Annualized Volatility'] if sum_stats_df is not None else None,
        "Annualized Sharpe Ratio": sum_stats_df.loc['Return']['Annualized Sharpe Ratio'] if sum_stats_df is not None else None,
        "CAGR": sum_stats_df.loc['Return']['CAGR'] if sum_stats_df is not None else None,
        "Daily Max Return": sum_stats_df.loc['Return']['Daily Max Return'] if sum_stats_df is not None else None,
        "Daily Max Return Date": sum_stats_df.loc['Return']['Daily Max Return (Date)'] if sum_stats_df is not None else None,
        "Daily Min Return": sum_stats_df.loc['Return']['Daily Min Return'] if sum_stats_df is not None else None,
        "Daily Min Return Date": sum_stats_df.loc['Return']['Daily Min Return (Date)'] if sum_stats_df is not None else None,
        "Max Drawdown": sum_stats_df.loc['Return']['Max Drawdown'] if sum_stats_df is not None else None,
        "Peak": sum_stats_df.loc['Return']['Peak'] if sum_stats_df is not None else None,
        "Trough": sum_stats_df.loc['Return']['Trough'] if sum_stats_df is not None else None,
        "Recovery Date": sum_stats_df.loc['Return']['Recovery Date'] if sum_stats_df is not None else None,
        "Days to Recover": sum_stats_df.loc['Return']['Days to Recover'] if sum_stats_df is not None else None,
        "MAR Ratio": sum_stats_df.loc['Return']['MAR Ratio'] if sum_stats_df is not None else None,

        # --- runtime & metadata ---
        "Total Runtime (s)": round(elapsed, 2),
        "Average Runtime (s)": round(avg_runtime_all, 2),
        "Runtime (s)": round(combo_runtime, 2),
        "Runtime EMA (s)": round(ema_runtime, 2) if ema_runtime is not None else None,
        "Success-only Runtime EMA (s)": round(success_ema_runtime, 2) if success_ema_runtime is not None else None,
        "Success": success,
        "Error": error_msg,
        "Order Entry": order_entry,
        "BB Rule": bb_rule if use_bbands else None,
        "BB Window": bb_window if use_bbands else None,
        "BB Num Std": bb_num_std if use_bbands else None,
        "Trade Taker Fee": TRADE_TAKER_FEE if trading_fees else 0,
        "Trade Maker Fee": TRADE_MAKER_FEE if trading_fees else 0,
    })

    if signals_df is not None and trades_df is not None and daily_perf_df is not None and sum_stats_df is not None:

        # Export DataFrames to Pickles (save inside current_directory)
        signals_path      = current_directory / "signals_df.pkl"
        trades_path       = current_directory / "trades_df.pkl"
        daily_perf_path   = current_directory / "daily_perf_df.pkl"
        sum_stats_path    = current_directory / "sum_stats_df.pkl"
        plot_path         = current_directory / "multi_asset_strategy.png"

        signals_df.to_pickle(signals_path)
        trades_df.to_pickle(trades_path)
        daily_perf_df.to_pickle(daily_perf_path)
        sum_stats_df.to_pickle(sum_stats_path)

        # Ensure the Iterations and year directories exist
        iterations_dir = current_directory / "Iterations"
        year = datetime.strptime(END_DATE, "%Y-%m-%d").year
        year_dir = iterations_dir / str(year)
        ma = ma_days if ma_days != [] else [0]
        ma_dir = year_dir / f"MA-{_stringify_list(ma)}"
        os.makedirs(ma_dir, exist_ok=True)
        
        zip_path = ma_dir / zip_name

        # Create ZIP of DataFrames and plot
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(signals_path, arcname="signals_df.pkl")
            zf.write(trades_path, arcname="trades_df.pkl")
            zf.write(daily_perf_path, arcname="daily_perf_df.pkl")
            zf.write(sum_stats_path, arcname="sum_stats_df.pkl")
            zf.write(plot_path, arcname="multi_asset_strategy.png")

        # Delete pickle files after zipping
        for path in [signals_path, trades_path, daily_perf_path, sum_stats_path, plot_path]:
            try:
                # path.unlink()  # same as os.remove(path)
                os.remove(path)  # just to be sure
            except FileNotFoundError:
                pass  # already deleted or never created
        
    else:
        pass

    # Delete all DataFrames to free up memory
    del crypto_prices_df, crypto_prices_technical_df, signals_df, trades_df, daily_perf_df, sum_stats_df

    # print(f"Created {START_DATE}_{END_DATE}_{tickers}_{ma_days}_{rsi_period}_{rsi_threshold}_{trailing_stop}.zip")

# Final DataFrame of results
results_df = pd.DataFrame(results_list)
results_df["MA_DAYS"] = results_df["MA_DAYS"].fillna(0.0)

results_csv = current_directory / f"multi_asset_strategy_results_{START_DATE}_{END_DATE}.csv"
try:
    existing_results_df = pd.read_csv(results_csv)
    combined_df = pd.concat([existing_results_df, results_df], ignore_index=True)
    combined_df.to_csv(results_csv, index=False)
except FileNotFoundError:
    results_df.to_csv(results_csv, index=False)