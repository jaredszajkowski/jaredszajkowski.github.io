import pandas as pd


def create_ma_trend_signals(
    fund_list: list[str],
    price_df: pd.DataFrame,
    ma_list: list[int],
    ma_type: str,
    price_column: str,
    signal_lag: int,
    output_confirmation: bool,
    fund_weights: list[float] | None = None,
) -> pd.DataFrame:
    """
    Generate multi-asset trend following target weights from a grid of moving averages.

    For every fund, a moving average is calculated for each span in ``ma_list``.
    Each average casts one vote: the vote is 1 when the fund's price is above that
    average and 0 otherwise. The fraction of votes in favor becomes the fund's
    signal strength, a value between 0 (price below every average) and 1 (price
    above every average).

    Signal strength is then scaled by the fund's share of ``fund_weights``, taken
    across the funds carrying valid price data on that row, so that a fully
    invested portfolio sums to a target weight of 1 and the unallocated remainder
    is held in cash. By default every fund carries equal weight and so tops out at
    1/N; passing ``[2, 1, 1]`` for three funds lets the first reach 0.5 and the
    other two 0.25. Funds without price data on a given row receive a target
    weight of 0 and are left out of the normalization, which lets the portfolio
    work with funds whose histories begin at different dates.

    Target weights are finally shifted forward by ``signal_lag`` rows so that a
    portfolio acting on this frame only ever trades on information that was
    already observable. With the default of 1, the weight applied on day t is the
    one implied by the close of day t-1.

    Notes
    -----
    A fund is only given a signal on rows where every span in the grid has a
    value. A simple moving average needs its full window before it reports
    anything, so a fund holds a target weight of 0 for the first ``max(ma_list)``
    rows of its own history. An exponential moving average is seeded on the first
    observation and reports immediately, which means its early values still carry
    the memory of that seed; allowing roughly one full span of warm-up before
    trading an EMA grid is prudent, but the caller must arrange that by choosing a
    later start date, since the EMA itself gives no signal that it is unready.

    Parameters
    ----------
    fund_list : list[str]
        List of funds to generate signals for, e.g. ``["IVV", "EFA", "EEM"]``.
    price_df : pd.DataFrame
        Date-indexed DataFrame containing a price column per fund, named
        ``f"{fund}_{price_column}"``.
    ma_list : list[int]
        List of moving average spans in rows (trading days for daily data), e.g.
        ``[20, 40, 60]``. Longer lists produce a smoother allocation.
    ma_type : str
        Type of moving average to use, either ``"EMA"`` for exponential or
        ``"SMA"`` for simple. Case insensitive. An EMA weights recent prices more
        heavily and turns faster; an SMA weights every observation in its window
        equally and turns more slowly.
    price_column : str
        Suffix of the price column to build signals from, e.g. ``"Adj_Close"``.
    signal_lag : int
        Number of rows to shift the target weights forward. Use 1 for daily data
        to trade on the prior close's signal. Use 0 only to inspect the
        unlagged signal; a backtest built on it will look ahead.
    output_confirmation : bool
        If True, print confirmation message.
    fund_weights : list[float] | None, optional
        Relative allocation ceiling per fund, in the same order as ``fund_list``.
        Values are normalized, so ``[2, 1, 1]`` and ``[0.5, 0.25, 0.25]`` describe
        the same portfolio. Because the normalization is taken over the funds
        active on each row, a fund's ceiling rises while its peers are still
        outside their price history. A weight of 0 holds a fund out of the
        portfolio while leaving its moving averages and signal strength in the
        returned frame. Defaults to None, which weights every fund equally.

    Returns
    -------
    pd.DataFrame
        Date-indexed DataFrame containing, for each fund, the moving average
        columns (``f"{fund}_{ma_type}_{span}"``), the signal strength
        (``f"{fund}_Signal_Strength"``), and the lagged target weight
        (``f"{fund}_Target_Weight"``), plus ``Total_Target_Weight`` and
        ``Cash_Weight``.

    Raises
    ------
    ValueError
        If ``ma_type`` is not "EMA" or "SMA", ``ma_list`` is empty, ``signal_lag``
        is negative, a required price column is missing from ``price_df``, or
        ``fund_weights`` is the wrong length, negative, non-finite, or all zero.
    """

    ma_type = ma_type.strip().upper()

    if ma_type not in ("EMA", "SMA"):
        raise ValueError(f"❌ ma_type must be 'EMA' or 'SMA', got {ma_type}.")

    if not ma_list:
        raise ValueError("❌ ma_list must contain at least one moving average span.")

    if signal_lag < 0:
        raise ValueError(f"❌ signal_lag must be >= 0, got {signal_lag}.")

    missing = [
        f"{fund}_{price_column}"
        for fund in fund_list
        if f"{fund}_{price_column}" not in price_df.columns
    ]
    if missing:
        raise ValueError(f"❌ price_df is missing required columns: {missing}")

    if fund_weights is None:
        weights = pd.Series(1.0, index=fund_list, dtype=float)
    else:
        if len(fund_weights) != len(fund_list):
            raise ValueError(
                f"❌ fund_weights must have one entry per fund, got "
                f"{len(fund_weights)} weights for {len(fund_list)} funds."
            )

        weights = pd.Series(
            [float(weight) for weight in fund_weights], index=fund_list, dtype=float
        )

        if weights.isna().any() or (weights == float("inf")).any():
            raise ValueError(f"❌ fund_weights must be finite, got {fund_weights}.")

        if (weights < 0).any():
            raise ValueError(
                f"❌ fund_weights must be non-negative, got {fund_weights}."
            )

        if weights.sum() <= 0:
            raise ValueError(
                "❌ fund_weights must contain at least one positive weight."
            )

    df = price_df.copy()

    # Total weight carried by the funds with valid price data on each row. Taking
    # the sum per row rather than once up front lets a fund's ceiling grow while
    # its peers are still outside their price history. Rows where no fund has data
    # are held as NaN so the division below does not blow up to infinity.
    active_funds = df[[f"{fund}_{price_column}" for fund in fund_list]].notna()
    active_funds.columns = fund_list
    active_weight = active_funds.mul(weights, axis=1).sum(axis=1)
    active_weight = active_weight.where(active_weight > 0)

    for fund in fund_list:
        price = df[f"{fund}_{price_column}"]

        # Calculate an average per span and record whether price sits above it
        votes = []
        for span in ma_list:
            if ma_type == "EMA":
                ma = price.ewm(span=int(span), adjust=False).mean()
            else:
                ma = price.rolling(window=int(span), min_periods=int(span)).mean()

            df[f"{fund}_{ma_type}_{span}"] = ma

            # A missing price or an average that has not filled its window yet
            # is recorded as no opinion rather than as a vote against
            votes.append((price > ma).astype(float).where(price.notna() & ma.notna()))

        # Signal strength is the fraction of averages the price is trading above.
        # skipna=False so a partially warmed up grid yields no signal at all,
        # rather than silently reporting on whichever spans happen to be ready.
        signal_strength = pd.concat(votes, axis=1).mean(axis=1, skipna=False)
        df[f"{fund}_Signal_Strength"] = signal_strength

        # Split the allocation across the funds that are active on that row in
        # proportion to their weight, then lag so the weight is only acted on
        # once it was observable
        target_weight = (signal_strength * weights[fund] / active_weight).fillna(0)
        df[f"{fund}_Target_Weight"] = target_weight.shift(signal_lag).fillna(0)

    # Portfolio level weights
    df["Total_Target_Weight"] = df[[f"{fund}_Target_Weight" for fund in fund_list]].sum(
        axis=1
    )
    df["Cash_Weight"] = 1 - df["Total_Target_Weight"]

    # Output confirmation
    if output_confirmation == True:
        plan_name = "_".join(fund_list)
        print(
            f"Trend signals complete for {plan_name} "
            f"across {len(ma_list)} {ma_type} spans with a {signal_lag} row lag"
        )
    else:
        pass

    return df
