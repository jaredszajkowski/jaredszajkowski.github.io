```python
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.ticker import MultipleLocator

def plot_vix_with_trades(
    vix_price_df: pd.DataFrame,
    trades_df: pd.DataFrame,
    plot_start_date: str,
    plot_end_date: str,
    x_tick_spacing: int,
    y_tick_spacing: int,
    index_number: str,
    export_plot: bool,
) -> pd.DataFrame:
    
    """
    Plot the VIX daily high and low prices, along with the VIX spikes, and trades.

    Parameters:
    -----------
    vix_price_df : pd.DataFrame
        Dataframe containing the VIX price data to plot.
    trades_df: pd.DataFrame
        Dataframe containing the trades data.
    plot_start_date : str
        Start date for the plot in 'YYYY-MM-DD' format.
    plot_end_date : str
        End date for the plot in 'YYYY-MM-DD' format.
    index_number : str
        Index number to be used in the file name of the plot export.
    export_plot : bool
        Whether to save the figure as a PNG file.

    Returns:
    --------
    vix_data : pd.DataFrame
        Dataframe containing the VIX price data for the specified timeframe.
    """

    # Create temporary dataframe for the specified date range
    vix_data = vix_price_df[(vix_price_df.index >= plot_start_date) & (vix_price_df.index <= plot_end_date)]

    # Set plot figure size and background color
    plt.figure(figsize=(12, 6), facecolor="#F5F5F5")

    # Plot data
    plt.plot(vix_data.index, vix_data['High'], label='High', linestyle='-', color='steelblue', linewidth=1)
    plt.plot(vix_data.index, vix_data['Low'], label='Low', linestyle='-', color='brown', linewidth=1)
    plt.scatter(vix_data[vix_data['Spike_SMA'] == True].index, vix_data[vix_data['Spike_SMA'] == True]['High'], label='Spike (High > 1.25 * 10 Day High SMA)', color='black', s=20)
    plt.scatter(trades_df['Trade_Date'], trades_df['Approx_VIX_Level'], label='Trades', color='red', s=20)

    # Annotate each point in trades_df with the corresponding Action_Symbol
    for _, row in trades_df.iterrows():
        plt.text(
            row['Trade_Date'] + pd.Timedelta(days=1),
            row['Approx_VIX_Level'] + 0.1,
            row['TradeDate_Action_Symbol_VIX'],
            fontsize=9
        )

    # Format X axis
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=x_tick_spacing))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xlabel("Date", fontsize=10)
    plt.xticks(rotation=45, fontsize=8)

    # Format Y axis
    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel("VIX", fontsize=10)
    plt.yticks(fontsize=8)

    # Format title, layout, grid, and legend
    plt.title(f"CBOE Volatility Index (VIX), VIX Spikes, Trades, {plot_start_date} - {plot_end_date}", fontsize=12)
    plt.tight_layout()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=9)

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{index_number}_VIX_Spike_Trades_{plot_start_date}_{plot_end_date}.png", dpi=300, bbox_inches="tight")
    
    # Display the plot
    plt.show()

    return vix_data
```