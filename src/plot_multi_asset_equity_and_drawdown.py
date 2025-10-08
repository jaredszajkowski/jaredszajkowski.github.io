import matplotlib.pyplot as plt
import pandas as pd

from label_start_end_min_max import label_start_end_min_max
from matplotlib.ticker import StrMethodFormatter
from pathlib import Path

def plot_multi_asset_equity_and_drawdown(
    tickers: list[str],
    daily_perf: pd.DataFrame,
    trades: pd.DataFrame,
    data: pd.DataFrame,
    title: str,
    show_plot: bool,
    export_plot: bool,
    export_dir: Path | str = None,   # <-- new optional parameter
) -> None:

    """
    Plots:
    - Total equity, cash, and per-asset position values
    - Cumulative returns (strategy and crypto assets)
    - Drawdowns (strategy and crypto assets)
    - Price series and trade markers for BTC, ETH, SOL

    Parameters:
    -----------
    tickers : list
        List of crypto tickers, e.g., ["BTC-USD", "ETH-USD", "SOL-USD"].
    daily_perf : pd.DataFrame
        DataFrame containing daily performance metrics from compute_daily_performance.
    trades : pd.DataFrame
        DataFrame of trades from backtest_rsi_multi_asset_strategy.
    data : pd.DataFrame
        DataFrame containing merged price data for all tickers.
    title : str
        Title for the overall plot.
    show_plot : bool
        Whether to display the plot.
    export_plot : bool
        Whether to save the plot as a PNG file.
    export_dir : Path | str, optional
        Directory to save the plot if export_plot is True. Defaults to current directory.

    Returns:
    --------
    None
    """
    
    # Copy the data dataframe
    prices_df = data.copy().set_index("Date")

    # Drop NaN rows
    perf_df = daily_perf.copy().dropna()

    # Compute position values and crypto drawdowns
    colors = ["blue", "red", "purple", "orange", "yellow"]

    # Determine number of subplots
    n_fixed = 3  # ax1, ax2, ax3
    n_tickers = len(tickers)
    total_axes = n_fixed + n_tickers

    # Setup plot
    fig, axes = plt.subplots(
        total_axes, 1,
        figsize=(14, 4 * total_axes),
        sharex=True,
        gridspec_kw={"height_ratios": [1] * total_axes}
    )

    # Unpack fixed axes
    ax1, ax2, ax3 = axes[:3]

    # Assign price axes
    price_axes = axes[3:]

    # ax1: Equity, Cash, and Position Values
    ax1.plot(perf_df.index, perf_df["equity"], color="black", label="Strategy Equity")
    label_start_end_min_max(ax1, perf_df.index, perf_df["equity"], fmt="{:,.0f}", fontsize=10)
    ax1.plot(perf_df.index, perf_df["cash"], color="green", alpha=0.6, linestyle="--", label="Strategy Cash")
    for i, symbol in enumerate(tickers):
        ax1.plot(perf_df.index, perf_df[f"{symbol}_position"], alpha=0.6, linestyle="--", color=colors[i % len(colors)], label=f"{symbol} Strategy Position Value")
    ax1.set_title("Equity, Cash, and Position Values (Daily Data)", fontsize=12)
    ax1.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax1.set_ylabel("Account Value ($)")
    ax1.legend()
    ax1.grid(True)

    # ax2: Cumulative Returns
    ax2.plot(perf_df.index, perf_df["Cum_Return"] * 100, color="black", label="Strategy Return")
    label_start_end_min_max(ax2, perf_df.index, perf_df["Cum_Return"] * 100, fmt="{:.1f}%", fontsize=10)
    for i, symbol in enumerate(tickers):
        ax2.plot(perf_df.index, perf_df[f"{symbol}_cum_return"] * 100, linestyle="--", color=colors[i % len(colors)], label=f"{symbol} Buy-Hold Return")
        label_start_end_min_max(ax2, perf_df.index, perf_df[f"{symbol}_cum_return"] * 100, fmt="{:.1f}%", fontsize=10)
    ax2.set_title("Cumulative Return (Daily Data)", fontsize=12)
    ax2.set_ylabel("Return (%)")
    ax2.legend()
    ax2.grid(True)

    # ax3: Drawdowns
    ax3.plot(perf_df.index, perf_df["Drawdown"] * 100, color="black", label="Strategy Drawdown")
    label_start_end_min_max(ax3, perf_df.index, perf_df["Drawdown"] * 100, fmt="{:.1f}%", fontsize=10)
    for i, symbol in enumerate(tickers):
        ax3.plot(perf_df.index, perf_df[f"{symbol}_drawdown"] * 100, linestyle="--", color=colors[i % len(colors)], label=f"{symbol} Buy-Hold Drawdown")
        label_start_end_min_max(ax3, perf_df.index, y = perf_df[f"{symbol}_drawdown"] * 100, fmt="{:.1f}%", fontsize=10)
    ax3.set_title("Drawdown (Daily Data)", fontsize=12)
    ax3.set_ylabel("Drawdown (%)")
    ax3.legend()
    ax3.grid(True)

    # ax4, ax5, ax6... : Price plots with trade markers are dynamically created based on the number of crypto assets
    for i, symbol in enumerate(tickers):
        df = prices_df[[f"{symbol}_close"]].copy()
        df.index = pd.to_datetime(df.index)
        # plot_df = df[df.index >= trades["entry_time"].min()]
        plot_df = df.copy()
        ax = price_axes[i]
        ax.plot(plot_df.index, plot_df[f"{symbol}_close"], color="gray", label=f"{symbol} Price")
        label_start_end_min_max(ax, plot_df.index, plot_df[f"{symbol}_close"], fmt="{:,.0f}", fontsize=10)

        # Mark trades
        asset_trades = trades[trades["asset"] == symbol]
        for _, trade in asset_trades.iterrows():
            if trade['quantity'] > 0:
                entry_time = trade["entry_time"]
                exit_time = trade["exit_time"]
                if entry_time in plot_df.index:
                    ax.plot(entry_time, plot_df.loc[entry_time, f"{symbol}_close"], marker="^", color="green", label="Entry" if "Entry" not in ax.get_legend_handles_labels()[1] else "")
                if exit_time in plot_df.index:
                    ax.plot(exit_time, plot_df.loc[exit_time, f"{symbol}_close"], marker="v", color="red", label="Exit" if "Exit" not in ax.get_legend_handles_labels()[1] else "")
            else:
                entry_time = trade["entry_time"]
                exit_time = trade["exit_time"]
                if entry_time in plot_df.index:
                    ax.plot(entry_time, plot_df.loc[entry_time, f"{symbol}_close"], marker="^", color="lightgreen", label="Entry (No trade due to position conflict)" if "Entry (No trade due to position conflict)" not in ax.get_legend_handles_labels()[1] else "")
                if exit_time in plot_df.index:
                    ax.plot(exit_time, plot_df.loc[exit_time, f"{symbol}_close"], marker="v", color="pink", label="Exit (No trade due to position conflict)" if "Exit (No trade due to position conflict)" not in ax.get_legend_handles_labels()[1] else "")
        ax.set_title(f"{symbol} Price History With Trades (Minute Data)", fontsize=12)
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.set_ylabel("Price ($)")
        ax.legend()
        ax.grid(True)

    # Set global title and layout
    fig.suptitle(title, fontsize=16, y=0.99)
    plt.tight_layout()

    # Export plot as PNG
    if export_plot:
        export_dir = Path(export_dir) if export_dir else Path.cwd()
        export_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(export_dir / "multi_asset_strategy.png")

    # Show the plot
    if show_plot == True:
        plt.show()
    else:
        plt.close(fig)

    return None