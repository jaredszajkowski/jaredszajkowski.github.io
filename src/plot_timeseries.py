import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import pandas as pd

from matplotlib.ticker import FormatStrFormatter, MultipleLocator

def plot_timeseries(
    price_df: pd.DataFrame,
    plot_start_date: str,
    plot_end_date: str,
    plot_columns,
    title: str,
    x_label: str,
    x_format: str,
    y_label: str,
    y_format: str,
    y_format_decimal_places: int,
    y_tick_spacing: int,
    grid: bool,
    legend: bool,
    export_plot: bool,
    plot_file_name: str,
) -> None:

    """
    Plot the price data from a DataFrame for a specified date range and columns.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the price data to plot.
    plot_start_date : str
        Start date for the plot in 'YYYY-MM-DD' format.
    plot_end_date : str
        End date for the plot in 'YYYY-MM-DD' format.
    plot_columns : str OR list
        List of columns to plot from the DataFrame. If none, all columns will be plotted.
    title : str
        Title of the plot.
    x_label : str
        Label for the x-axis.
    x_format : str
        Format for the x-axis date labels.
    y_label : str
        Label for the y-axis.
    y_format : str
        Format for the y-axis labels.
    y_format_decimal_places : int
        Number of decimal places for y-axis labels.
    y_tick_spacing : int
        Spacing for the y-axis ticks.
    grid : bool
        Whether to display a grid on the plot.
    legend : bool
        Whether to display a legend on the plot.
    export_plot : bool
        Whether to save the figure as a PNG file.
    plot_file_name : str
        File name for saving the figure (if save_fig is True).
    

    Returns:
    --------
    None
    """

    # If start date and end date are None, use the entire DataFrame
    if plot_start_date is None and plot_end_date is None:
        df_filtered = price_df

    # If only end date is specified, filter by end date
    elif plot_start_date is None and plot_end_date is not None:
        df_filtered = price_df[(price_df.index <= plot_end_date)]

    # If only start date is specified, filter by start date
    elif plot_start_date is not None and plot_end_date is None:
        df_filtered = price_df[(price_df.index >= plot_start_date)]

    # If both start date and end date are specified, filter by both
    else:
        df_filtered = price_df[(price_df.index >= plot_start_date) & (price_df.index <= plot_end_date)]

    # Set plot figure size and background color
    plt.figure(figsize=(12, 6), facecolor="#F5F5F5")

    # Plot data
    if plot_columns =="All":
        for col in df_filtered.columns:
            plt.plot(df_filtered.index, df_filtered[col], label=col, linestyle='-', linewidth=1.5)
    else:
        for col in plot_columns:
            plt.plot(df_filtered.index, df_filtered[col], label=col, linestyle='-', linewidth=1.5)

    # Format X axis
    if x_format == "Day":
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    elif x_format == "Week":
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    elif x_format == "Month":
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    elif x_format == "Year":
        plt.gca().xaxis.set_major_locator(mdates.YearLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    else:
        raise ValueError(f"Unrecognized x_format: {x_format}. Use 'Day', 'Week', 'Month', or 'Year'.")

    plt.xlabel(x_label, fontsize=10)
    plt.xticks(rotation=45, fontsize=8)

    # Format Y axis
    if y_format == "Decimal":
        plt.gca().yaxis.set_major_formatter(FormatStrFormatter(f"%.{y_format_decimal_places}f"))
    elif y_format == "Percentage":
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=y_format_decimal_places))
    elif y_format == "Scientific":
        plt.gca().yaxis.set_major_formatter(FormatStrFormatter(f"%.{y_format_decimal_places}e"))
    elif y_format == "Log":
        plt.yscale("log")
    else:
        raise ValueError(f"Unrecognized y_format: {y_format}. Use 'Decimal', 'Percentage', or 'Scientific'.")
    
    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel(y_label, fontsize=10)
    plt.yticks(fontsize=8)

    # Format title, layout, grid, and legend
    plt.title(title, fontsize=12)
    plt.tight_layout()

    if grid == True:
        plt.grid(True, linestyle='--', alpha=0.7)

    if legend == True:
        plt.legend(fontsize=9)

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None