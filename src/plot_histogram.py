import math
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.ticker import MultipleLocator


def round_to_nice_value(value):
    """Round a value to a 'nice' number for tick spacing (1, 2, 5 × 10^n)."""
    if value <= 0:
        return value

    # Find order of magnitude
    exp = math.floor(math.log10(value))
    magnitude = 10 ** exp

    # Get mantissa (value normalized to [1, 10))
    mantissa = value / magnitude

    # Round mantissa to 1, 2, or 5
    if mantissa <= 1.5:
        nice_mantissa = 1
    elif mantissa <= 3:
        nice_mantissa = 2
    elif mantissa <= 7:
        nice_mantissa = 5
    else:
        nice_mantissa = 10

    return nice_mantissa * magnitude


def plot_histogram(
    df: pd.DataFrame,
    plot_columns: str | list[str],
    title: str,
    x_label: str,
    x_tick_spacing: int,
    x_tick_rotation: int,
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
    df : pd.DataFrame
        DataFrame containing the price data to plot.
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
    plt.figure(figsize=(10, 6))

    # Plot data
    if plot_columns == "All":
        for col in df.columns:
            mean = df[col].mean()
            std = df[col].std()
            # Create histogram first to get its color
            n, bins, patches = plt.hist(df[col], label=col, bins=200, edgecolor='black', alpha=0.5)
            hist_color = patches[0].get_facecolor()
            # Use histogram color for vertical lines
            plt.axvline(mean, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean: {mean:.3f}')
            plt.axvline(mean + std, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean + 1 std: {mean + std:.3f}')
            plt.axvline(mean - std, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean - 1 std: {mean - std:.3f}')
            plt.axvline(mean + 2 * std, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean + 2 std: {mean + 2 * std:.3f}')
            plt.axvline(mean - 2 * std, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean - 2 std: {mean - 2 * std:.3f}')
    else:
        for col in plot_columns:
            mean = df[col].mean()
            std = df[col].std()
            # Create histogram first to get its color
            n, bins, patches = plt.hist(df[col], label=col, bins=200, edgecolor='black', alpha=0.5)
            hist_color = patches[0].get_facecolor()
            # Use histogram color for vertical lines
            plt.axvline(mean, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean: {mean:.3f}')
            plt.axvline(mean + std, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean + 1 std: {mean + std:.3f}')
            plt.axvline(mean - std, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean - 1 std: {mean - std:.3f}')
            plt.axvline(mean + 2 * std, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean + 2 std: {mean + 2 * std:.3f}')
            plt.axvline(mean - 2 * std, color=hist_color, linestyle='dashed', linewidth=1, label=f'Mean - 2 std: {mean - 2 * std:.3f}')

    # Format X axis
    if x_tick_spacing == "Auto":
        raw_x_spacing = (bins[-1] - bins[0]) / 20
        x_tick_spacing = round_to_nice_value(raw_x_spacing)
    else:
        x_tick_spacing = x_tick_spacing
    plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
    plt.xlabel(x_label, fontsize=14)
    plt.xticks(rotation=x_tick_rotation, fontsize=12)

    # Format Y axis
    if y_tick_spacing == "Auto":
        raw_y_spacing = (n.max() - n.min()) / 10
        y_tick_spacing = round_to_nice_value(raw_y_spacing)
    else:
        y_tick_spacing = y_tick_spacing
    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel(y_label, fontsize=14)
    plt.yticks(fontsize=12)

    # Format title, layout, grid, and legend
    plt.title(title, fontsize=16)
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