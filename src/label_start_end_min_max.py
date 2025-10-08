import numpy as np

def label_start_end_min_max(
    ax,
    x,
    y,
    fmt: str = "{:.2f}",
    fontsize: int = 9,
):
    
    """
    Annotate start, end, min, and max points on a line plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis to annotate.
    x : array-like
        X values (e.g., dates).
    y : array-like
        Y values (numeric).
    fmt : str, optional
        Format string for labels.
    fontsize : int, optional
        Font size for annotation text.
    """

    # Ensure numpy arrays for indexing
    x = np.array(x)
    y = np.array(y)

    # Start and end
    ax.annotate(
        fmt.format(y[0]),
        (x[0], y[0]),
        textcoords="offset points",
        xytext=(5, 5),
        ha="left",
        color="black",
        fontsize=fontsize,
    )
    ax.annotate(
        fmt.format(y[-1]),
        (x[-1], y[-1]),
        textcoords="offset points",
        xytext=(5, 5),
        ha="left",
        color="black",
        fontsize=fontsize,
    )

    # Min and max
    min_idx = y.argmin()
    max_idx = y.argmax()
    ax.annotate(
        fmt.format(y[min_idx]),
        (x[min_idx], y[min_idx]),
        textcoords="offset points",
        xytext=(0, -15),
        ha="center",
        color="red",
        fontsize=fontsize,
    )
    ax.annotate(
        fmt.format(y[max_idx]),
        (x[max_idx], y[max_idx]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        color="green",
        fontsize=fontsize,
    )
