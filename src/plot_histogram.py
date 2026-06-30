import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.ticker import MultipleLocator

from round_to_nice_value import round_to_nice_value


def plot_histogram(
    df: pd.DataFrame,
    plot_columns: str | list[str],
    title: str,
    x_label: str,
    x_tick_spacing: int,
    x_tick_rotation: int,
    y_label: str,
    y_tick_spacing: int,
    y_tick_rotation: int,
    grid: bool = True,
    legend: bool = True,
    legend_location: str = "best",
    legend_anchor: tuple = None,
    export_plot: bool = False,
    plot_file_name: str = None,
) -> None:
    """
    Plot the histogram for a dataset from a DataFrame for a specified date range and columns.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the data to plot.
    plot_columns : str OR list
        List of columns to plot from the DataFrame. If none, all columns will be plotted.
    title : str
        Title of the plot.
    x_label : str
        Label for the x-axis.
    x_tick_spacing : int
        Spacing for the x-axis ticks.
    x_tick_rotation : int
        Rotation angle for the x-axis tick labels.
    y_label : str
        Label for the y-axis.
    y_tick_spacing : int
        Spacing for the y-axis ticks.
    y_tick_rotation : int
        Rotation angle for the y-axis tick labels.
    grid : bool, optional
        Whether to display a grid on the plot.
    legend : bool, optional
        Whether to display a legend on the plot.
    legend_location : str, optional
        Location of the legend on the plot (default is "best").
    legend_anchor : tuple, optional
        Anchor point (x, y) for placing the legend relative to the axes,
        e.g. (1, 1) to move it outside the plot (default is None).
    export_plot : bool, optional
        Whether to save the figure as a PNG file.
    plot_file_name : str, optional
        File name for saving the figure (if save_fig is True).

    Returns:
    --------
    None
    """

    # Set plot figure size and background color
    plt.figure(figsize=(10, 6))

    # Plot data
    cols = df.columns if plot_columns == "All" else plot_columns
    for col in cols:
        mean = df[col].mean()
        std = df[col].std()
        # Create histogram first to get its color
        n, bins, patches = plt.hist(
            df[col], label=col, bins=200, edgecolor="black", alpha=0.5
        )
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
        raw_x_spacing = (bins[-1] - bins[0]) / 20
        x_tick_spacing = round_to_nice_value(raw_x_spacing)
    else:
        x_tick_spacing = x_tick_spacing

    plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
    plt.xlabel(x_label)

    if x_tick_rotation != 0:
        # Line up the x-ticks with the labels when rotated
        plt.xticks(rotation=x_tick_rotation, ha="right")
    else:
        plt.xticks(rotation=x_tick_rotation)

    # Format Y axis
    if y_tick_spacing == "Auto":
        raw_y_spacing = (n.max() - n.min()) / 10
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
        plt.grid(True, linestyle="--", alpha=0.5)

    # Legend
    if legend == True:
        if legend_anchor is not None:
            plt.legend(loc=legend_location, bbox_to_anchor=legend_anchor)
        else:
            plt.legend(loc=legend_location)

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None
