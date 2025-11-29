import numpy as np
import pandas as pd

def calc_fed_cycle_asset_performance(
    fed_cycles: list,
    cycle_labels: list,
    fed_changes: list,
    monthly_df: pd.DataFrame,
) -> pd.DataFrame:

    results = []

    for (start, end), label in zip(fed_cycles, cycle_labels):
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        # Filter TLT returns for the cycle period
        returns = monthly_df.loc[start:end, "Monthly_Return"]

        if len(returns) == 0:
            continue

        cumulative_return = (1 + returns).prod() - 1
        average_return = returns.mean()
        volatility = returns.std()

        results.append({
            "Cycle": label,
            "Start": start.date(),
            "End": end.date(),
            "Months": len(returns),
            "CumulativeReturn": cumulative_return,
            "AverageMonthlyReturn": average_return,
            "Volatility": volatility,
        })

    # Convert to DataFrame
    cycle_df = pd.DataFrame(results)
    cycle_df["CumulativeReturnPct"] = 100 * cycle_df["CumulativeReturn"]
    cycle_df["AverageMonthlyReturnPct"] = 100 * cycle_df["AverageMonthlyReturn"]
    cycle_df["AnnualizedReturn"] = (1 + cycle_df["CumulativeReturn"]) ** (12 / cycle_df["Months"]) - 1
    cycle_df["AnnualizedReturnPct"] = 100 * cycle_df["AnnualizedReturn"]

    # Correct the volatility calculation to annualized volatility
    cycle_df["Volatility"] = cycle_df["Volatility"] * np.sqrt(12)

    # Re-order columns
    cycle_df = cycle_df[[
        "Cycle", "Start", "End", "Months", "CumulativeReturn", "CumulativeReturnPct",  
        "AverageMonthlyReturn", "AverageMonthlyReturnPct", "AnnualizedReturn", "AnnualizedReturnPct", "Volatility", 
    ]]

    # Merge Fed changes into cycle_df
    cycle_df["FedFundsChange"] = fed_changes
    cycle_df["FedFundsChange_bps"] = cycle_df["FedFundsChange"] * 10000  # in basis

    # Add annualized change in FFR in basis points
    cycle_df["FFR_AnnualizedChange"] = (cycle_df["FedFundsChange"] / cycle_df["Months"]) * 12
    cycle_df["FFR_AnnualizedChange_bps"] = cycle_df["FFR_AnnualizedChange"] * 10000  # Convert to basis points

    cycle_df["Label"] = cycle_df.apply(
        lambda row: f"{row['Cycle']}, {row['Start']} to {row['End']}", axis=1
    )

    return cycle_df