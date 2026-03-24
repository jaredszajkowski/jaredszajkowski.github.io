```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm


def plot_scatter_regression_ffr_vs_returns(
    cycle_df: pd.DataFrame,
    asset_label: str,
    x_vals: np.ndarray,
    y_vals: np.ndarray,
    intercept: float,
    slope: float,
) -> None:
    """
    Plot a scatter plot of annualized returns vs annualized change in Fed Funds 
    Rate, with a regression line and annotations for each policy cycle.

    Parameters
    ----------
    cycle_df : pd.DataFrame
        DataFrame containing the policy cycle data with columns 'FFR_AnnualizedChange_bps', 'AnnualizedReturnPct', and 'Cycle'.
    asset_label : str
        Label for the asset being plotted (e.g., "S&P 500").
    x_vals : np.ndarray
        Array of x values for the regression line.
    y_vals : np.ndarray
        Array of y values for the regression line.
    intercept : float
        Intercept of the OLS regression line.
    slope : float
        Slope of the OLS regression line.

    Returns
    -------
    None
    """

    # Set plot figure size and background color
    plt.figure(figsize=(10, 6))

    # Plot data
    sns.scatterplot(
        data=cycle_df,
        x="FFR_AnnualizedChange_bps",
        y="AnnualizedReturnPct",
        s=100,
        color="blue"
    )

    # Annotate each point with the cycle number or date range, annualized returns and FFR
    for i, row in cycle_df.iterrows():
        plt.text(
            row["FFR_AnnualizedChange_bps"] + 5,  # small x-offset
            row["AnnualizedReturnPct"],
            row["Cycle"],
            # fontsize=10,
            color="black",
        )

    plt.plot(x_vals, y_vals, color="red", linestyle="--", label=f"OLS Fit: y = {intercept:.1f} + {slope:.2f}x")
    plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    plt.axvline(0, color="gray", linestyle="--", linewidth=0.8)
    
    # Format X axis
    plt.xlabel("Annualized Change In Fed Funds Rate (bps)")
    plt.xticks()

    # Format Y axis
    plt.ylabel(f"{asset_label} Annualized Return (%)")
    plt.yticks()

    # Format title, layout, grid, and legend
    plt.title(f"{asset_label} Annualized Return vs Annualized Change in Fed Funds Rate by Policy Cycle")
    plt.tight_layout()
    plt.grid(True)
    plt.legend()

    # Display the plot
    plt.show()

    return None
```