```python
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_bar_returns_ffr_change(
    cycle_df: pd.DataFrame,
    asset_label: str,
    annualized_or_cumulative: str,
) -> None:

    plt.figure(figsize=(10, 8))

    if annualized_or_cumulative == "Cumulative":

        # Create bar plot for cumulative returns
        barplot = sns.barplot(
            data=cycle_df,
            x="Label",
            y="CumulativeReturnPct",
            palette="coolwarm"
        )

        # Annotate each bar with cumulative return and Fed rate change
        for i, row in cycle_df.iterrows():
            barplot.text(
                i,
                row["CumulativeReturnPct"] + 1,
                f"{row['CumulativeReturnPct']:.1f}%\nΔFFR: {row['FedFundsChange_bps']:.0f}bps",
                color="black",
                ha="center",
                # fontsize=10,
            )

    elif annualized_or_cumulative == "Annualized":    
        
        # Create bar plot for annualized returns
        barplot = sns.barplot(
            data=cycle_df,
            x="Label",  # Date range labels from earlier
            y="AnnualizedReturnPct",
            palette="coolwarm"
        )

        # Annotate each bar with annualized return + annualized FFR change
        for i, row in cycle_df.iterrows():
            barplot.text(
                i,
                row["AnnualizedReturnPct"] + 1,
                f"{row['AnnualizedReturnPct']:.1f}%\nΔFFR: {row['FFR_AnnualizedChange_bps']:.0f}bps/yr",
                color="black",
                ha="center",
                # fontsize=10,
            )

    # plt.ylabel(f"{asset_label} {annualized_or_cumulative} Return (%)", fontsize=14)
    plt.ylabel(f"{asset_label} {annualized_or_cumulative} Return (%)")
    # plt.yticks(fontsize=12)
    plt.yticks()
    # plt.xlabel("Fed Policy Cycle (Date Range)", fontsize=14)
    plt.xlabel("Fed Policy Cycle (Date Range)")
    # plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    # plt.title(f"{asset_label} {annualized_or_cumulative} Return by Fed Policy Cycle With {annualized_or_cumulative} Change in Fed Funds Rate", fontsize=16)
    plt.title(f"{asset_label} {annualized_or_cumulative} Return by Fed Policy Cycle With {annualized_or_cumulative} Change in Fed Funds Rate")
    plt.tight_layout()
    plt.show()
```