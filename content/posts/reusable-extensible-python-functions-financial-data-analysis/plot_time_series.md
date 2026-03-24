```python
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from matplotlib.ticker import (
    FuncFormatter,
    MultipleLocator,
    PercentFormatter,
)


def round_to_nice_value(value):
    """Round a value to a 'nice' number for tick spacing (1, 2, 5 x 10^n)."""
    if value <= 0:
        return value

    # Find order of magnitude
    exp = math.floor(math.log10(value))
    magnitude = 10**exp

    # Get mantissa (value normalized to [1, 10))
    mantissa = value / magnitude

    # Round mantissa to 1, 2, or 5
    if mantissa <= 1:
        nice_mantissa = 0.1
    elif mantissa <= 1.5:
        nice_mantissa = 1
    elif mantissa <= 3:
        nice_mantissa = 2
    elif mantissa <= 7:
        nice_mantissa = 5
    else:
        nice_mantissa = 10

    return nice_mantissa * magnitude


def plot_time_series(
    df: pd.DataFrame,
    plot_start_date: str,
    plot_end_date: str,
    plot_columns: str | list[str],
    title: str,
    x_label: str,
    x_format: str,
    x_tick_spacing: int,
    x_tick_rotation: int,
    y_label: str,
    y_format: str,
    y_format_decimal_places: int,
    y_tick_spacing: int,
    y_tick_rotation: int,
    grid: bool,
    legend: bool,
    export_plot: bool,
    plot_file_name: str,
) -> None:
    """
    Plot the time series data from a DataFrame for a specified date range and columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the time series data to plot.
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
    x_tick_spacing : int
        Spacing for the x-axis ticks.
    x_tick_rotation : int
        Rotation angle for the x-axis tick labels.
    y_label : str
        Label for the y-axis.
    y_format : str
        Format for the y-axis labels.
    y_format_decimal_places : int
        Number of decimal places for y-axis labels.
    y_tick_spacing : int
        Spacing for the y-axis ticks.
    y_tick_rotation : int
        Rotation angle for the y-axis tick labels.
    grid : bool
        Whether to display a grid on the plot.
    legend : bool
        Whether to display a legend on the plot.
    export_plot : bool
        Whether to save the figure as a PNG file.
    plot_file_name : str
        File name for saving the figure (if save_fig is True).


    Returns
    -------
    None
    """

    # If start date and end date are None, use the entire DataFrame
    if plot_start_date is None and plot_end_date is None:
        df_filtered = df.copy()

    # If only end date is specified, filter by end date
    elif plot_start_date is None and plot_end_date is not None:
        df_filtered = df[(df.index <= plot_end_date)].copy()

    # If only start date is specified, filter by start date
    elif plot_start_date is not None and plot_end_date is None:
        df_filtered = df[(df.index >= plot_start_date)].copy()

    # If both start date and end date are specified, filter by both
    else:
        df_filtered = df[
            (df.index >= plot_start_date) & (df.index <= plot_end_date)
        ].copy()

    # Set plot figure size and background color
    plt.figure(figsize=(10, 6))

    # Plot data
    if plot_columns == "All":
        for col in df_filtered.columns:
            plt.plot(
                df_filtered.index,
                df_filtered[col],
                label=col,
                linestyle="-",
                linewidth=1.5,
                alpha=0.7,
            )
    else:
        for col in plot_columns:
            plt.plot(
                df_filtered.index,
                df_filtered[col],
                label=col,
                linestyle="-",
                linewidth=1.5,
                alpha=0.7,
            )

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
        plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=x_tick_spacing))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    else:
        raise ValueError(
            f"Unrecognized x_format: {x_format}. Use 'Day', 'Week', 'Month', or 'Year'."
        )

    plt.xlabel(x_label)
    plt.xticks(rotation=x_tick_rotation)

    # Format Y axis
    if y_format == "Decimal":
        plt.gca().yaxis.set_major_formatter(
            FuncFormatter(lambda x, _: f"{x:,.{y_format_decimal_places}f}")
        )
    elif y_format == "Percentage":
        plt.gca().yaxis.set_major_formatter(
            PercentFormatter(xmax=1, decimals=y_format_decimal_places)
        )
    elif y_format == "Scientific":
        plt.gca().yaxis.set_major_formatter(
            FuncFormatter(lambda x, _: f"{x:.{y_format_decimal_places}e}")
        )
    elif y_format == "Log":
        plt.yscale("log")
    else:
        raise ValueError(
            f"Unrecognized y_format: {y_format}. Use 'Decimal', 'Percentage', 'Scientific', or 'Log'."
        )

    if y_tick_spacing == "Auto":
        max = 0
        min = 1
        for col in plot_columns:
            if df[col].max() > max:
                max = df[col].max()

            if df[col].min() < min:
                min = df[col].min()

        raw_y_spacing = (max - min) / 10
        y_tick_spacing = round_to_nice_value(raw_y_spacing)
    else:
        y_tick_spacing = y_tick_spacing

    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel(y_label)
    plt.yticks(rotation=y_tick_rotation)

    # Format title, layout, grid, and legend
    plt.title(title)
    plt.tight_layout()

    # Grid
    if grid == True:
        plt.grid(True, linestyle="--", alpha=0.7)

    # Legend
    if legend == True:
        plt.legend()

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None

```