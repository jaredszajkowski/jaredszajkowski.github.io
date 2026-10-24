import pandas as pd


def strategy_harry_brown_perm_port(
    fund_list: str,
    starting_cash: int,
    cash_contrib: int,
    close_prices_df: pd.DataFrame,
    rebal_month: int,
    rebal_day: int,
    rebal_per_high: float,
    rebal_per_low: float,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
    target_weights: dict = None,
) -> pd.DataFrame:
    """
    Execute the re-balance strategy based on specified criteria.

    Parameters:
    -----------
    fund_list (str):
        List of funds for data to be combined from. Funds are strings in the form "BTC-USD".
    starting_cash (int):
        Starting investment balance.
    cash_contrib (int):
        Cash contribution to be made daily.
    close_prices_df (pd.DataFrame):
        DataFrame containing date and close prices for all funds to be included.
    rebal_month (int):
        Month for annual rebalance.
    rebal_day (int):
        Day for annual rebalance.
    rebal_per_high (float):
        High rebalance band, as a multiple of each fund's target weight. A value of
        1.40 rebalances a fund once it exceeds 140% of its target, which for an
        evenly weighted four asset portfolio is Browne's 35% upper bound.
    rebal_per_low (float):
        Low rebalance band, as a multiple of each fund's target weight. A value of
        0.60 rebalances a fund once it falls below 60% of its target, which for an
        evenly weighted four asset portfolio is Browne's 15% lower bound.
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.
    target_weights (dict):
        Target portfolio weight for each fund, keyed by fund name, as decimals summing
        to 1.0 (for example {"Stocks": 0.30, "Bonds": 0.30, "Gold": 0.30, "Cash": 0.10}).
        If None, every fund is weighted equally, which is Browne's original 25% each.

    Returns:
    --------
    df (pd.DataFrame):
        DataFrame containing strategy data for all funds to be included. Also dumps the df to excel for reference later.
    """

    num_funds = len(fund_list)

    # Weight each fund evenly unless explicit target weights were provided
    if target_weights is None:
        target_weights = {fund: 1 / num_funds for fund in fund_list}
    else:
        missing = [fund for fund in fund_list if fund not in target_weights]
        if missing:
            raise KeyError(f"target_weights is missing a weight for: {missing}")

        weight_total = sum(target_weights[fund] for fund in fund_list)
        if abs(weight_total - 1) > 1e-9:
            raise ValueError(
                f"target_weights for {fund_list} sum to {weight_total}, expected 1.0"
            )

    df = close_prices_df.copy()
    df.reset_index(inplace=True)

    # Date to be used for annual rebalance
    target_month = rebal_month
    target_day = rebal_day

    # Create a dataframe with dates from the specific month
    rebal_date = df[df["Date"].dt.month == target_month]

    # Specify the date or the next closest
    rebal_date = rebal_date[rebal_date["Date"].dt.day >= target_day]

    # Group by year and take the first entry for each year
    rebal_dates_by_year = (
        rebal_date.groupby(rebal_date["Date"].dt.year).first().reset_index(drop=True)
    )

    """
    Column order for the dataframe:
    df[fund + "_BA_Shares"]
    df[fund + "_BA_$_Invested"]
    df[fund + "_BA_Port_%"]
    df['Total_BA_$_Invested']
    df['Contribution']
    df['Rebalance']
    df[fund + "_AA_Shares"]
    df[fund + "_AA_$_Invested"]
    df[fund + "_AA_Port_%"]
    df['Total_AA_$_Invested']
    """

    # Calculate the columns and initial values for before action (BA) shares, $ invested, and port %
    for fund in fund_list:
        df[fund + "_BA_Shares"] = (
            starting_cash * target_weights[fund] / df[fund + "_Close"]
        )
        df[fund + "_BA_$_Invested"] = df[fund + "_BA_Shares"] * df[fund + "_Close"]
        df[fund + "_BA_Port_%"] = target_weights[fund]

    # Set column values initially
    df["Total_BA_$_Invested"] = float(starting_cash)
    df["Contribution"] = cash_contrib
    df["Rebalance"] = "No"

    # Set columns and values initially for after action (AA) shares, $ invested, and port %
    for fund in fund_list:
        df[fund + "_AA_Shares"] = (
            starting_cash * target_weights[fund] / df[fund + "_Close"]
        )
        df[fund + "_AA_$_Invested"] = df[fund + "_AA_Shares"] * df[fund + "_Close"]
        df[fund + "_AA_Port_%"] = target_weights[fund]

    # Set column value for after action (AA) total $ invested
    df["Total_AA_$_Invested"] = float(starting_cash)

    # Iterate through the dataframe and execute the strategy
    for index, row in df.iterrows():

        # Ensure there's a previous row to reference by checking the index value
        if index > 0:

            # Initialize variable
            Total_BA_Invested = 0

            # Calculate before action (BA) shares and $ invested values
            for fund in fund_list:
                df.at[index, fund + "_BA_Shares"] = df.at[
                    index - 1, fund + "_AA_Shares"
                ]
                df.at[index, fund + "_BA_$_Invested"] = (
                    df.at[index, fund + "_BA_Shares"] * row[fund + "_Close"]
                )

                # Sum the asset values to find the total
                Total_BA_Invested = (
                    Total_BA_Invested + df.at[index, fund + "_BA_$_Invested"]
                )

            # Calculate before action (BA) port % values
            for fund in fund_list:
                df.at[index, fund + "_BA_Port_%"] = (
                    df.at[index, fund + "_BA_$_Invested"] / Total_BA_Invested
                )

            # Set column for before action (BA) total $ invested
            df.at[index, "Total_BA_$_Invested"] = Total_BA_Invested

            # Initialize variables
            rebalance = "No"
            date = row["Date"]

            # Check for a specific date annually
            # Simple if statement to check if date_to_check is in jan_28_or_after_each_year
            if date in rebal_dates_by_year["Date"].values:
                rebalance = "Yes"
            else:
                pass

            # Check to see if any asset has drifted outside its rebalance band, which is
            # set as a multiple of that asset's target weight, and if so set variable
            for fund in fund_list:
                if (
                    df.at[index, fund + "_BA_Port_%"]
                    > target_weights[fund] * rebal_per_high
                    or df.at[index, fund + "_BA_Port_%"]
                    < target_weights[fund] * rebal_per_low
                ):
                    rebalance = "Yes"
                else:
                    pass

            # If rebalance is required, rebalance back to each asset's target weight,
            # else just divide the contribution across assets by their target weights
            if rebalance == "Yes":
                df.at[index, "Rebalance"] = rebalance
                for fund in fund_list:
                    df.at[index, fund + "_AA_$_Invested"] = (
                        Total_BA_Invested + df.at[index, "Contribution"]
                    ) * target_weights[fund]
            else:
                df.at[index, "Rebalance"] = rebalance
                for fund in fund_list:
                    df.at[index, fund + "_AA_$_Invested"] = (
                        df.at[index, fund + "_BA_$_Invested"]
                        + df.at[index, "Contribution"] * target_weights[fund]
                    )

            # Initialize variable
            Total_AA_Invested = 0

            # Set column values for after action (AA) shares and port %
            for fund in fund_list:
                df.at[index, fund + "_AA_Shares"] = (
                    df.at[index, fund + "_AA_$_Invested"] / row[fund + "_Close"]
                )

                # Sum the asset values to find the total
                Total_AA_Invested = (
                    Total_AA_Invested + df.at[index, fund + "_AA_$_Invested"]
                )

            # Calculate after action (AA) port % values
            for fund in fund_list:
                df.at[index, fund + "_AA_Port_%"] = (
                    df.at[index, fund + "_AA_$_Invested"] / Total_AA_Invested
                )

            # Set column for after action (AA) total $ invested
            df.at[index, "Total_AA_$_Invested"] = Total_AA_Invested

        # If this is the first row
        else:
            pass

    df["Return"] = df["Total_AA_$_Invested"].pct_change()
    df["Cumulative_Return"] = (1 + df["Return"]).cumprod()

    plan_name = "_".join(fund_list)

    # Export to excel
    if excel_export == True:
        df.to_excel(f"{plan_name}_Strategy.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        df.to_pickle(f"{plan_name}_Strategy.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        print(f"Strategy complete for {plan_name}")
    else:
        pass

    return df
