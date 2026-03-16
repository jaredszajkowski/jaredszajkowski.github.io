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

    plt.figure(figsize=(10, 6))

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
    # plt.title(f"{asset_label} Annualized Return vs Annualized Change in Fed Funds Rate by Policy Cycle", fontsize=16)
    plt.title(f"{asset_label} Annualized Return vs Annualized Change in Fed Funds Rate by Policy Cycle")
    # plt.xlabel("Annualized Change In Fed Funds Rate (bps)", fontsize=14)
    plt.xlabel("Annualized Change In Fed Funds Rate (bps)")
    # plt.xticks(fontsize=12)
    plt.xticks()
    # plt.ylabel(f"{asset_label} Annualized Return (%)", fontsize=14)
    plt.ylabel(f"{asset_label} Annualized Return (%)")
    # plt.yticks(fontsize=12)
    plt.yticks()
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
```