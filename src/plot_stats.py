import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.ticker import MultipleLocator


def plot_stats(
    stats_df: pd.DataFrame,
    plot_columns,
    title: str,
    x_label: str,
    x_rotation: int,
    x_tick_spacing: int,
    y_label: str,
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
    stats_df : pd.DataFrame
        DataFrame containing the price data to plot.
    plot_columns : str OR list
        List of columns to plot from the DataFrame. If none, all columns will be plotted.
    title : str
        Title of the plot.
    x_label : str
        Label for the x-axis.
    x_rotation : int
        Rotation angle for the x-axis date labels.
    x_tick_spacing : int
        Spacing for the x-axis ticks.
    y_label : str
        Label for the y-axis.
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

    # Set plot figure size and background color
    plt.figure(figsize=(12, 6), facecolor="#F5F5F5")

    # Plot data
    if plot_columns == "All":
        for col in stats_df.columns:
            plt.scatter(
                stats_df.index, stats_df[col], label=col, linestyle="-", linewidth=1.5
            )
    else:
        for col in plot_columns:
            plt.scatter(
                stats_df.index, stats_df[col], label=col, linestyle="-", linewidth=1.5
            )

    # Format X axis
    plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
    plt.xlabel(x_label, fontsize=10)
    plt.xticks(rotation=x_rotation, fontsize=8)

    # Format Y axis
    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel(y_label, fontsize=10)
    plt.yticks(fontsize=8)

    # Format title, layout, grid, and legend
    plt.title(title, fontsize=12)
    plt.tight_layout()

    if grid == True:
        plt.grid(True, linestyle="--", alpha=0.7)

    if legend == True:
        plt.legend(fontsize=9)

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None
