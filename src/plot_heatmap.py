import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_heatmap(
    df: pd.DataFrame,
    title: str,
    cmap: str = "coolwarm",
    vmin: float = -1,
    vmax: float = 1,
    center: float = None,
    fmt: str = ".2f",
    caption: str = None,
) -> None:
    """
    Plot a heatmap from a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data to plot.
    title : str
        Title of the plot.
    cmap : str, optional
        Matplotlib/seaborn colormap name. Default "coolwarm".
    vmin, vmax : float, optional
        Lower and upper bounds of the color scale. Default -1 and 1.
    center : float, optional
        Value at which to center a diverging colormap (e.g. 0 for a signed
        quantity, 0.5 for an accuracy relative to a coin flip). Default None.
    fmt : str, optional
        String format for the cell annotations. Default ".2f".
    caption : str, optional
        Caption drawn centered below the figure, e.g. "Figure 1". Default
        None.

    Returns
    -------
    None

    Example
    -------
    >>> import pandas as pd
    >>> data = {
    ...     "A": [1, 0.5, -0.5],
    ...     "B": [0.5, 1, -0.25],
    ...     "C": [-0.5, -0.25, 1]
    ... }
    >>> df = pd.DataFrame(data, index=["A", "B", "C"])
    >>> plot_heatmap(df, title="Correlation Heatmap")
    """

    # Set plot figure size and background color
    plt.figure(figsize=(12, 8))

    # Plot data
    sns.heatmap(df, annot=True, fmt=fmt, cmap=cmap, vmin=vmin, vmax=vmax, center=center)

    # Format X axis
    plt.xticks(rotation=30, ha="right")

    # Format Y axis
    plt.yticks(rotation=0)

    # Format title, layout, grid, and legend
    plt.title(title)
    plt.tight_layout()

    # Caption
    if caption is not None:
        plt.gcf().text(0.5, 0, caption, ha="center", va="top", fontsize=9)

    # Display the plot
    plt.show()

    return None
