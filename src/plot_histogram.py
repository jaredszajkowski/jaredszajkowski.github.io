import math
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.ticker import MultipleLocator

from round_to_nice_value import round_to_nice_value


def plot_histogram(
    df: pd.DataFrame,
    plot_columns: str | list[str],
    title: str,
    x_label: str,
    x_tick_spacing: int | float | str,
    x_tick_rotation: int,
    y_label: str,
    y_tick_spacing: int | float | str,
    y_tick_rotation: int,
    grid: bool = True,
    legend: bool = True,
    legend_location: str = "best",
    legend_anchor: tuple = None,
    export_plot: bool = False,
    plot_file_name: str = None,
    caption: str = None,
) -> None:
    """
    Plot a histogram of one or more columns from a DataFrame, with lines marking
    the mean and +/- 1 and 2 standard deviations of each.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data to plot.
    plot_columns : str OR list
        Column or list of columns to plot from the DataFrame, or "All" to plot
        every column.
    title : str
        Title of the plot.
    x_label : str
        Label for the x-axis.
    x_tick_spacing : int OR float OR str
        Spacing for the x-axis ticks, or "Auto" to derive it from the range of
        the histogram bins across all plotted columns.
    x_tick_rotation : int
        Rotation angle for the x-axis tick labels.
    y_label : str
        Label for the y-axis.
    y_tick_spacing : int OR float OR str
        Spacing for the y-axis ticks, or "Auto" to derive it from the tallest
        bar across all plotted columns (at least 1, since counts are whole
        numbers).
    y_tick_rotation : int
        Rotation angle for the y-axis tick labels.
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

    # Set plot figure size and background color
    plt.figure(figsize=(10, 6))

    # Plot data
    cols = df.columns if plot_columns == "All" else plot_columns

    # Track the extent across all columns so "Auto" spacing fits every histogram
    max_count = 0
    bins_min = math.inf
    bins_max = -math.inf

    for col in cols:
        mean = df[col].mean()
        std = df[col].std()
        # Create histogram first to get its color
        n, bins, patches = plt.hist(
            df[col], label=col, bins=200, edgecolor="black", alpha=0.5
        )
        max_count = max(max_count, n.max())
        bins_min = min(bins_min, bins[0])
        bins_max = max(bins_max, bins[-1])

        hist_color = patches[0].get_facecolor()
        # Use histogram color for vertical lines
        plt.axvline(
            mean,
            color=hist_color,
            linestyle="dashed",
            linewidth=1,
            label=f"Mean: {mean:.3f}",
        )
        plt.axvline(
            mean + std,
            color=hist_color,
            linestyle="dashed",
            linewidth=1,
            label=f"Mean + 1 std: {mean + std:.3f}",
        )
        plt.axvline(
            mean - std,
            color=hist_color,
            linestyle="dashed",
            linewidth=1,
            label=f"Mean - 1 std: {mean - std:.3f}",
        )
        plt.axvline(
            mean + 2 * std,
            color=hist_color,
            linestyle="dashed",
            linewidth=1,
            label=f"Mean + 2 std: {mean + 2 * std:.3f}",
        )
        plt.axvline(
            mean - 2 * std,
            color=hist_color,
            linestyle="dashed",
            linewidth=1,
            label=f"Mean - 2 std: {mean - 2 * std:.3f}",
        )

    # Format X axis
    if x_tick_spacing == "Auto":
        raw_x_spacing = (bins_max - bins_min) / 10
        x_tick_spacing = round_to_nice_value(raw_x_spacing)

    plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
    plt.xlabel(x_label)

    if x_tick_rotation != 0:
        # Line up the x-ticks with the labels when rotated
        plt.xticks(rotation=x_tick_rotation, ha="right")
    else:
        plt.xticks(rotation=x_tick_rotation)

    # Format Y axis
    if y_tick_spacing == "Auto":
        # Bars are drawn from 0, and counts are whole numbers
        raw_y_spacing = max_count / 10
        y_tick_spacing = max(1, round_to_nice_value(raw_y_spacing))

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
