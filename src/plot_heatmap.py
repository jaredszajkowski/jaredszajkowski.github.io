import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_heatmap(
    df: pd.DataFrame,
    title: str,
) -> None:
    """
    Plot a heatmap from a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data to plot.
    title : str
        Title of the plot.

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
    sns.heatmap(df, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)

    # Format X axis
    plt.xticks(rotation=30, ha="right")

    # Format Y axis
    plt.yticks(rotation=0)

    # Format title, layout, grid, and legend
    plt.title(title)
    plt.tight_layout()

    # Display the plot
    plt.show()

    return None
