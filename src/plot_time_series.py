import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from matplotlib.ticker import (
    FuncFormatter,
    MultipleLocator,
    PercentFormatter,
)

from round_to_nice_value import round_to_nice_value


def plot_time_series(
    df: pd.DataFrame,
    plot_start_date: str,
    plot_end_date: str,
    plot_columns: str | list[str],
    title: str,
    x_label: str,
    x_format: str,
    x_tick_spacing: int,
    x_tick_start: str,
    x_tick_rotation: int,
    y_label: str,
    y_format: str,
    y_format_decimal_places: int | str,
    y_tick_spacing: int | float | str,
    y_tick_rotation: int,
    emphasis_columns: str | list[str] = None,
    emphasis_linewidth: float = 3.0,
    emphasis_alpha: float = 1.0,
    grid: bool = True,
    legend: bool = True,
    legend_location: str = "best",
    legend_anchor: tuple = None,
    export_plot: bool = False,
    plot_file_name: str = None,
    caption: str = None,
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
        Column or list of columns to plot from the DataFrame, or "All" to plot
        every column.
    title : str
        Title of the plot.
    x_label : str
        Label for the x-axis.
    x_format : str
        Format for the x-axis date labels.
    x_tick_spacing : int
        Spacing for the x-axis ticks.
    x_tick_start : str
        Start date for the x-axis ticks.
    x_tick_rotation : int
        Rotation angle for the x-axis tick labels.
    y_label : str
        Label for the y-axis.
    y_format : str
        Format for the y-axis labels: "Decimal", "Percentage", "Scientific", or
        "Log".
    y_format_decimal_places : int OR str
        Number of decimal places for y-axis labels, or "Auto" to infer it from
        the y-axis tick spacing.
    y_tick_spacing : int OR float OR str
        Spacing for the y-axis ticks, or "Auto" to derive it from the range of
        the plotted data. Ignored when y_format is "Log".
    y_tick_rotation : int
        Rotation angle for the y-axis tick labels.
    emphasis_columns : str OR list, optional
        Column(s) to draw with emphasis: full opacity and drawn on top of the
        other series, plus a heavier line weight if emphasis_linewidth is
        raised. Colors are unchanged, and the non-emphasized series keep their
        normal styling (default is None).
    emphasis_linewidth : float, optional
        Line width used for emphasized columns (default is 3.0).
    emphasis_alpha : float, optional
        Opacity used for emphasized columns (default is 1.0).
    grid : bool, optional
        Whether to display a grid on the plot (default is True).
    legend : bool, optional
        Whether to display a legend on the plot (default is True).
    legend_location : str, optional
        Location of the legend on the plot (default is "best").
    legend_anchor : tuple, optional
        Anchor point (x, y) for placing the legend relative to the axes,
        e.g. (1, 1) to move it outside the plot (default is None).
    export_plot : bool, optional
        Whether to save the figure as a PNG file (default is False).
    plot_file_name : str, optional
        File name for saving the figure (if export_plot is True, default is None).
    caption : str, optional
        Caption drawn centered below the figure, e.g. "Figure 1" (default is
        None).

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
    cols = df_filtered.columns if plot_columns == "All" else plot_columns

    # Normalize emphasis columns to a set for membership testing
    if emphasis_columns is None:
        emphasis_cols = set()
    elif isinstance(emphasis_columns, str):
        emphasis_cols = {emphasis_columns}
    else:
        emphasis_cols = set(emphasis_columns)

    # Catch typos rather than silently plotting without emphasis
    unrecognized = emphasis_cols - set(cols)
    if unrecognized:
        raise ValueError(
            f"Unrecognized emphasis_columns: {sorted(unrecognized)}. "
            f"Columns being plotted: {sorted(cols)}."
        )

    for col in cols:
        emphasized = col in emphasis_cols
        plt.plot(
            df_filtered.index,
            df_filtered[col],
            label=col,
            linestyle="-",
            linewidth=emphasis_linewidth if emphasized else 1.5,
            alpha=emphasis_alpha if emphasized else 0.5,
            # Layer emphasized series on top without reordering the loop, which
            # would shift the color cycle and the legend order
            zorder=3 if emphasized else 2,
        )

    # Format X axis
    if x_format == "Second":
        if x_tick_start is not None:
            ticks = pd.date_range(
                start=pd.Timestamp(x_tick_start).tz_convert(df_filtered.index.tz),
                end=df_filtered.index.max() + pd.tseries.offsets.Second(x_tick_spacing),
                freq=pd.tseries.offsets.Second(x_tick_spacing),
            )
            plt.gca().set_xticks(ticks)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        else:
            plt.gca().xaxis.set_major_locator(
                mdates.SecondLocator(interval=x_tick_spacing)
            )
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    elif x_format == "Minute":
        if x_tick_start is not None:
            ticks = pd.date_range(
                start=pd.Timestamp(x_tick_start).tz_convert(df_filtered.index.tz),
                end=df_filtered.index.max() + pd.tseries.offsets.Minute(x_tick_spacing),
                freq=pd.tseries.offsets.Minute(x_tick_spacing),
            )
            plt.gca().set_xticks(ticks)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:
            plt.gca().xaxis.set_major_locator(
                mdates.MinuteLocator(interval=x_tick_spacing)
            )
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    elif x_format == "Hour":
        if x_tick_start is not None:
            ticks = pd.date_range(
                start=pd.Timestamp(x_tick_start).tz_convert(df_filtered.index.tz),
                end=df_filtered.index.max() + pd.tseries.offsets.Hour(x_tick_spacing),
                freq=pd.tseries.offsets.Hour(x_tick_spacing),
            )
            plt.gca().set_xticks(ticks)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:
            plt.gca().xaxis.set_major_locator(
                mdates.HourLocator(interval=x_tick_spacing)
            )
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    elif x_format == "Day":
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=x_tick_spacing))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    elif x_format == "Week":
        plt.gca().xaxis.set_major_locator(
            mdates.WeekdayLocator(interval=x_tick_spacing)
        )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    elif x_format == "Month":
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=x_tick_spacing))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    elif x_format == "Year":
        plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=x_tick_spacing))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    else:
        raise ValueError(
            f"Unrecognized x_format: {x_format}. Use 'Second', 'Minute', 'Hour', 'Day', 'Week', 'Month', or 'Year'."
        )

    plt.xlabel(x_label)

    if x_tick_rotation != 0:
        # Line up the x-ticks with the labels when rotated
        plt.xticks(rotation=x_tick_rotation, ha="right")
    else:
        plt.xticks(rotation=x_tick_rotation)

    # Format Y axis
    if y_tick_spacing == "Auto":
        max_value = -math.inf
        min_value = math.inf
        cols = df_filtered.columns if plot_columns == "All" else plot_columns
        for col in cols:
            if df_filtered[col].max() > max_value:
                max_value = df_filtered[col].max()

            if df_filtered[col].min() < min_value:
                min_value = df_filtered[col].min()

        raw_y_spacing = (max_value - min_value) / 10
        y_tick_spacing = round_to_nice_value(raw_y_spacing)

    if y_format_decimal_places == "Auto":
        if isinstance(y_tick_spacing, float):
            y_tick_spacing_decimal_places = max(
                0, -int(math.floor(math.log10(abs(y_tick_spacing))))
            )
        else:
            y_tick_spacing_decimal_places = 0

        # PercentFormatter shows the value x 100, which needs 2 fewer decimals
        if y_format == "Percentage":
            y_tick_spacing_decimal_places = max(0, y_tick_spacing_decimal_places - 2)

        y_format_decimal_places = y_tick_spacing_decimal_places

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

    # Linear tick spacing would override the log locator
    if y_format != "Log":
        plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))

    plt.ylabel(y_label)
    plt.yticks(rotation=y_tick_rotation)

    # Format title, layout, grid, and legend
    plt.title(title)
    plt.tight_layout()

    # Grid
    if grid == True:
        plt.grid(True, linestyle="--", alpha=0.5)

    # Legend
    if legend == True:
        if legend_anchor is not None:
            plt.legend(loc=legend_location, bbox_to_anchor=legend_anchor)
        else:
            plt.legend(loc=legend_location)

    # Caption
    if caption is not None:
        plt.gcf().text(0.5, 0, caption, ha="center", va="top", fontsize=9)

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None
