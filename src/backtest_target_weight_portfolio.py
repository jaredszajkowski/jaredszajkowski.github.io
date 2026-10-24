import numpy as np
import pandas as pd


def backtest_target_weight_portfolio(
    fund_list: list[str],
    price_df: pd.DataFrame,
    weights_df: pd.DataFrame,
    price_column: str,
    starting_cash: float,
    cash_contrib: float,
    cash_yield: float | pd.Series,
    borrow_spread: float,
    leverage: float,
    rebal_interval: int | str,
    trans_cost_pct: float,
    start_date: str,
    excel_export: bool,
    pickle_export: bool,
    output_confirmation: bool,
) -> pd.DataFrame:
    """
    Backtest a portfolio that periodically rebalances toward target weights.

    The portfolio holds each fund at its target weight, with any unallocated
    remainder sitting in cash. Positions drift with prices between rebalances and
    are only traded back to target on the rows ``rebal_interval`` selects, either
    every N rows, counted from the first row on or after ``start_date`` so the
    rebalance calendar does not depend on how much price history precedes the
    backtest, or on the last trading day of each month.

    Supplied weights are scaled by ``leverage`` before being applied. A leverage
    above 1 does not force borrowing: it raises the ceiling on gross exposure, and
    whether the portfolio actually borrows depends on how much of that ceiling the
    weights use. A strategy whose weights sum to 0.6 levered at 1.25 targets 0.75
    of the portfolio and still holds a quarter of it in cash. The same strategy at
    a moment when its weights sum to 1.0 targets 1.25 and borrows a quarter of
    equity. Cash simply goes negative when it happens, and negative balances
    accrue at ``cash_yield`` plus ``borrow_spread`` rather than earning interest.

    Each row is recorded twice: before action (BA) values reflect the positions
    carried in from the prior row marked at today's prices, and after action (AA)
    values reflect the positions held once any rebalance trade has taken place. On
    a non-rebalance row the two are identical and no transaction costs accrue.

    The engine is agnostic about where the weights come from, so any strategy that
    can express itself as a per-fund target weight can be run through it.

    Notes
    -----
    Weights are consumed as supplied apart from the ``leverage`` scaling. Lagging
    them so that the backtest does not act on same-day information is the caller's
    responsibility; ``create_ma_trend_signals`` does this via its ``signal_lag``
    parameter.

    Margin is modeled only as a financing cost. There is no maintenance
    requirement, no margin call, and no forced liquidation, so a leverage high
    enough to be called in practice will run to the end of the sample here
    regardless. Treat results above roughly 2x as indicative rather than
    achievable.

    Parameters
    ----------
    fund_list : list[str]
        List of funds in the portfolio, e.g. ``["IVV", "EFA", "EEM"]``.
    price_df : pd.DataFrame
        Date-indexed DataFrame containing a price column per fund, named
        ``f"{fund}_{price_column}"``. When this is a total return series such as
        adjusted close, dividends are implicitly reinvested.
    weights_df : pd.DataFrame
        Date-indexed DataFrame containing a target weight per fund, named
        ``f"{fund}_Target_Weight"``, on the same index as ``price_df``. Weights
        are expressed as a fraction of total portfolio value.
    price_column : str
        Suffix of the price column to mark positions at, e.g. ``"Adj_Close"``.
    starting_cash : float
        Starting portfolio balance, held as cash before the first rebalance.
    cash_contrib : float
        Cash contribution added on every row. Contributions accumulate in cash
        and are deployed at the next rebalance.
    cash_yield : float | pd.Series
        Annual interest rate earned on the uninvested cash balance, in decimal
        form. Pass a float for a flat rate across the whole backtest, or a
        date-indexed Series of annual rates to track an actual short rate such as
        the 3 month Treasury bill. A Series is reindexed onto the backtest
        calendar and forward filled. Pass ``0.0`` for no interest. Interest
        accrues on the balance carried in from the prior row, over the actual
        calendar days elapsed on a 365 day basis, and is credited before the
        rebalance decision so it is available to invest.
    borrow_spread : float
        Annual markup over ``cash_yield`` charged on a negative cash balance, in
        decimal form. Broker margin is typically priced as a benchmark rate plus a
        spread, roughly 100 to 150 basis points for a retail account and far less
        institutionally. Pass ``0.0`` to borrow at the cash rate. Ignored while
        the cash balance stays positive.
    leverage : float
        Multiplier applied to every supplied target weight. ``1.0`` leaves the
        weights untouched and the portfolio can never borrow. Above 1.0 the
        portfolio borrows only on rows where the scaled weights exceed 1.0; below
        1.0 it deliberately underinvests.
    rebal_interval : int | str
        Rebalance calendar. An integer rebalances every N rows, counted from the
        first row of the backtest. ``"ME"`` instead rebalances on the last row of
        each month, which is the last trading day present in the data rather than
        the calendar month end, since that need not be a trading day. The first
        row of the backtest is always a rebalance under either setting, which is
        what deploys the starting cash. Under ``"ME"`` the final row of the
        backtest is never a rebalance: no row follows it for the trade to
        benefit, so it would pay transaction costs for nothing.
    trans_cost_pct : float
        Transaction cost as a fraction of traded notional, e.g. ``0.001`` for 10
        basis points. Applied to the absolute value of each fund's trade.
    start_date : str
        Start date for the backtest in ``"YYYY-MM-DD"`` format, or ``"All"`` to
        run from the first row of ``price_df``.
    excel_export : bool
        If True, export data to Excel format.
    pickle_export : bool
        If True, export data to Pickle format.
    output_confirmation : bool
        If True, print confirmation message.

    Returns
    -------
    pd.DataFrame
        Date-indexed DataFrame containing, per fund, the applied target weight
        (post-leverage, not as supplied), before action shares and dollars
        invested, after action shares, dollars invested, realized weight and
        traded notional, alongside the portfolio level ``Total_BA_$_Invested``,
        ``Cash_Interest``, ``Cash_BA``, ``Contribution``, ``Rebalance``,
        ``Total_AA_$_Invested``, ``Total_AA_%_Invested``,
        ``Total_Transaction_Costs``, ``Cash_AA``, ``Cash_%``, ``Borrowing``,
        ``Total_Value``, ``Return``, ``Cumulative_Return``,
        ``Cum_Total_Transaction_Costs`` and ``Cum_Cash_Interest``.

        ``Cash_Interest`` is signed: positive where the balance earned interest,
        negative where it was charged. ``Borrowing`` marks the rows where the
        portfolio was genuinely on margin.

    Raises
    ------
    ValueError
        If ``rebal_interval`` is neither a positive integer nor ``"ME"``,
        ``leverage`` is not positive, ``borrow_spread`` is negative, a required
        column is missing, or ``start_date`` falls beyond the end of the price
        data.
    """

    if isinstance(rebal_interval, str):
        if rebal_interval != "ME":
            raise ValueError(
                f'❌ rebal_interval must be a positive int or "ME", '
                f"got {rebal_interval!r}."
            )
    elif rebal_interval < 1:
        raise ValueError(f"❌ rebal_interval must be >= 1, got {rebal_interval}.")

    if leverage <= 0:
        raise ValueError(f"❌ leverage must be > 0, got {leverage}.")

    if borrow_spread < 0:
        raise ValueError(f"❌ borrow_spread must be >= 0, got {borrow_spread}.")

    missing_prices = [
        f"{fund}_{price_column}"
        for fund in fund_list
        if f"{fund}_{price_column}" not in price_df.columns
    ]
    if missing_prices:
        raise ValueError(f"❌ price_df is missing required columns: {missing_prices}")

    missing_weights = [
        f"{fund}_Target_Weight"
        for fund in fund_list
        if f"{fund}_Target_Weight" not in weights_df.columns
    ]
    if missing_weights:
        raise ValueError(
            f"❌ weights_df is missing required columns: {missing_weights}"
        )

    # Align the two frames and trim to the backtest window
    prices = price_df[[f"{fund}_{price_column}" for fund in fund_list]]
    weights = weights_df[[f"{fund}_Target_Weight" for fund in fund_list]]
    df = prices.join(weights, how="inner")

    if start_date != "All":
        df = df[df.index >= start_date]

    if df.empty:
        raise ValueError(
            f"❌ No rows remain for start_date {start_date}. "
            f"Price data ends {price_df.index.max()}."
        )

    num_rows = df.shape[0]
    num_funds = len(fund_list)

    # Work in NumPy so the sequential path below stays fast
    price_arr = df[[f"{fund}_{price_column}" for fund in fund_list]].to_numpy(
        dtype=float
    )
    # Scale the supplied weights. Gross exposure now runs up to leverage rather
    # than up to 1, and cash absorbs the difference in either direction.
    weight_arr = (
        df[[f"{fund}_Target_Weight" for fund in fund_list]].to_numpy(dtype=float)
        * leverage
    )

    # A fund only trades on rows where it has a price
    tradable = np.isfinite(price_arr)
    safe_price = np.where(tradable, price_arr, np.nan)

    # Rebalance calendar. An integer interval is counted from the first row of
    # the backtest; "ME" instead marks every row that its successor does not
    # share a month with, the last trading day of the month as the data has it.
    # That leaves the final row unflagged, which is deliberate: no row follows it
    # for the trade to benefit, so it would pay transaction costs for nothing.
    # Either way the first row rebalances, deploying the starting cash.
    if isinstance(rebal_interval, str):
        month = df.index.to_period("M")
        rebal_flags = np.append(month[:-1] != month[1:], False)
        rebal_flags[0] = True
    else:
        rebal_flags = np.arange(num_rows) % rebal_interval == 0

    # Annual cash rate per row, either flat or tracking a supplied short rate
    if isinstance(cash_yield, pd.Series):
        cash_rate = cash_yield.reindex(df.index).ffill().fillna(0).to_numpy(dtype=float)
    else:
        cash_rate = np.full(num_rows, float(cash_yield))

    # Interest accrues over the actual calendar days between rows. The first row
    # has no prior balance to accrue on, so its elapsed count is zero. A positive
    # balance earns the cash rate; a negative one is charged the cash rate plus
    # the borrow spread, so which factor applies is decided inside the loop.
    days_elapsed = df.index.to_series().diff().dt.days.fillna(0).to_numpy(dtype=float)
    lend_factor = cash_rate * days_elapsed / 365
    borrow_factor = (cash_rate + borrow_spread) * days_elapsed / 365

    # Output arrays
    ba_shares = np.zeros((num_rows, num_funds))
    ba_invested = np.zeros((num_rows, num_funds))
    aa_shares = np.zeros((num_rows, num_funds))
    aa_invested = np.zeros((num_rows, num_funds))
    notional = np.zeros((num_rows, num_funds))
    total_ba_invested = np.zeros(num_rows)
    cash_interest = np.zeros(num_rows)
    cash_ba = np.zeros(num_rows)
    cash_aa = np.zeros(num_rows)
    total_aa_invested = np.zeros(num_rows)
    total_costs = np.zeros(num_rows)
    total_value = np.zeros(num_rows)

    # Positions and cash carried into the current row
    prev_shares = np.zeros(num_funds)
    prev_cash = starting_cash

    for i in range(num_rows):
        # ----- Before action -----

        # Positions carried in from the prior row, marked at today's prices
        shares_in = prev_shares
        invested_in = np.where(tradable[i], shares_in * safe_price[i], 0.0)
        ba_shares[i] = shares_in
        ba_invested[i] = invested_in
        total_ba_invested[i] = invested_in.sum()

        # Interest on the balance carried in, then this row's contribution.
        # Negative when the portfolio is borrowing rather than lending.
        if prev_cash >= 0:
            interest = prev_cash * lend_factor[i]
        else:
            interest = prev_cash * borrow_factor[i]
        cash_interest[i] = interest
        cash_in = prev_cash + interest + cash_contrib
        cash_ba[i] = cash_in

        # ----- After action -----

        portfolio_value = total_ba_invested[i] + cash_in

        if rebal_flags[i]:
            # Trade back to target weights, holding untradable funds flat.
            # Costs are paid out of cash, so the amount available to deploy is
            # the portfolio net of them. Since the cost depends on the size of
            # the trade and the trade depends on the amount deployed, price the
            # trade once at gross value, then redeploy against value net of that
            # first estimate. The residual is on the order of the cost squared.
            gross_dollars = np.nan_to_num(
                np.where(tradable[i], weight_arr[i] * portfolio_value, invested_in),
                nan=0.0,
            )
            cost_estimate = trans_cost_pct * np.abs(gross_dollars - invested_in).sum()

            target_dollars = np.nan_to_num(
                np.where(
                    tradable[i],
                    weight_arr[i] * (portfolio_value - cost_estimate),
                    invested_in,
                ),
                nan=0.0,
            )
            traded = target_dollars - invested_in
            costs = trans_cost_pct * np.abs(traded).sum()

            # Divide only where a price exists, holding other funds' shares flat
            divisor = np.where(tradable[i], safe_price[i], 1.0)
            aa_invested[i] = target_dollars
            aa_shares[i] = np.where(tradable[i], target_dollars / divisor, shares_in)
            notional[i] = traded
        else:
            # No trade, so after action simply mirrors before action
            aa_invested[i] = invested_in
            aa_shares[i] = shares_in
            notional[i] = 0.0
            costs = 0.0

        total_aa_invested[i] = aa_invested[i].sum()
        total_costs[i] = costs

        # Whatever is not invested, less costs, remains in cash
        cash_aa[i] = portfolio_value - total_aa_invested[i] - costs
        total_value[i] = total_aa_invested[i] + cash_aa[i]

        prev_shares = aa_shares[i]
        prev_cash = cash_aa[i]

    # Assemble the output frame in the documented column order
    out = pd.DataFrame(index=df.index)

    for j, fund in enumerate(fund_list):
        out[f"{fund}_{price_column}"] = price_arr[:, j]
        out[f"{fund}_Target_Weight"] = weight_arr[:, j]
        out[f"{fund}_BA_Shares"] = ba_shares[:, j]
        out[f"{fund}_BA_$_Invested"] = ba_invested[:, j]

    out["Total_BA_$_Invested"] = total_ba_invested
    out["Cash_Interest"] = cash_interest
    out["Cash_BA"] = cash_ba
    out["Contribution"] = cash_contrib
    out["Rebalance"] = np.where(rebal_flags, "Yes", "No")

    for j, fund in enumerate(fund_list):
        out[f"{fund}_AA_Shares"] = aa_shares[:, j]
        out[f"{fund}_AA_$_Invested"] = aa_invested[:, j]
        out[f"{fund}_Notional"] = notional[:, j]

    out["Total_AA_$_Invested"] = total_aa_invested
    out["Total_Transaction_Costs"] = total_costs
    out["Cash_AA"] = cash_aa
    out["Total_Value"] = total_value

    # Realized weights, calculated once total value is known
    for j, fund in enumerate(fund_list):
        out[f"{fund}_AA_%_Invested"] = aa_invested[:, j] / total_value

    out["Total_AA_%_Invested"] = total_aa_invested / total_value
    out["Cash_%"] = cash_aa / total_value

    # Whether the portfolio was actually on margin. The two pass cost sizing can
    # leave cash a few billionths negative even at leverage 1.0, which is
    # rounding, not borrowing, so judge against a tolerance scaled to portfolio
    # size rather than against zero.
    out["Borrowing"] = out["Cash_AA"] < -1e-6 * out["Total_Value"].abs()

    # Performance
    out["Return"] = out["Total_Value"].pct_change()
    out["Cumulative_Return"] = (1 + out["Return"]).cumprod()
    out["Cum_Total_Transaction_Costs"] = out["Total_Transaction_Costs"].cumsum()
    out["Cum_Cash_Interest"] = out["Cash_Interest"].cumsum()

    plan_name = "_".join(fund_list)

    # Export to excel
    if excel_export == True:
        out.to_excel(f"{plan_name}_Strategy.xlsx", sheet_name="data")
    else:
        pass

    # Export to pickle
    if pickle_export == True:
        out.to_pickle(f"{plan_name}_Strategy.pkl")
    else:
        pass

    # Output confirmation
    if output_confirmation == True:
        borrowed_rows = out["Borrowing"].sum()
        print(
            f"Strategy complete for {plan_name} at {leverage}x leverage, "
            f"borrowing on {borrowed_rows} of {num_rows} rows"
        )
    else:
        pass

    return out
