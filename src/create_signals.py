import pandas as pd

def create_signals(
    tickers: list,
    data: pd.DataFrame,
    # --- RSI settings ---
    use_rsi: bool,
    rsi_threshold: int,
    # --- MA settings ---
    use_ma: bool,
    ma_days: list,
    # --- Bollinger settings ---
    use_bbands: bool,
    bb_rule: str = "touch_lower",  # {"touch_lower", "cross_up_from_below", "below_lower"}
) -> pd.DataFrame:
    """
    Generate entry signals combining RSI, optional MA filter, and optional Bollinger Bands.

    Notes:
    - Bollinger bands are computed on *_close_prev so the signal at time t only uses info up to t-1.
    - BB rules:
        * "touch_lower": close_prev <= lower_prev  (default)
        * "below_lower": close_prev  < lower_prev  (strict)
        * "cross_up_from_below": close_prev crosses from < lower_prev to >= lower_prev (uses previous bar of prev-close)
    """

    # Copy the data dataframe
    df = data.copy()

    signals = []
    for ticker in tickers:
        # --- RSI mask ---
        if use_rsi:
            rsi_mask = df.get(f"{ticker}_RSI_prev", pd.Series(index=df.index, dtype="float64")).lt(rsi_threshold).fillna(False)
        else:
            rsi_mask = pd.Series(True, index=df.index, dtype="bool")

        # --- MA mask ---
        if use_ma:
            if ma_days:
                ma_cols = [f"{ticker}_MA_{day}d_prev" for day in ma_days if f"{ticker}_MA_{day}d_prev" in df.columns]
                if not ma_cols:
                    # MA periods requested but none present → this ticker yields no signals
                    continue

                ma_pass_df = pd.concat(
                    [(df[f"{ticker}_close"] > df[col]).rename(col) for col in ma_cols],
                    axis=1
                ).fillna(False)

                ma_passes = ma_pass_df.sum(axis=1)
                allocation_pct = ma_passes / len(ma_days)
                ma_mask = ma_passes.ge(1)
            else:
                ma_passes = pd.Series(0, index=df.index, dtype="int64")
                allocation_pct = pd.Series(1.0, index=df.index, dtype="float64")  # full allocation if no MAs
                ma_mask = pd.Series(True, index=df.index, dtype="bool")

        # --- Bollinger Bands mask ---
        if use_bbands:
            # close_prev = df.get(f"{ticker}_close_prev")
            # if close_prev is None:
            #     # If we don't have *_close_prev, skip BB logic safely
            #     bb_mask = pd.Series(True, index=df.index, dtype="bool")  # don't block RSI/MA if missing
            #     bb_mid_prev = bb_up_prev = bb_low_prev = pd.Series(pd.NA, index=df.index)
            #     bb_z_prev = pd.Series(pd.NA, index=df.index)
            # else:
            #     rolling = close_prev.rolling(window=bb_window, min_periods=bb_window)
            #     mid_prev = rolling.mean()
            #     std_prev = rolling.std(ddof=0)
            #     up_prev = mid_prev + bb_num_std * std_prev
            #     low_prev = mid_prev - bb_num_std * std_prev

            #     # Band position (z-score) using prev values
            #     bb_z_prev = (close_prev - mid_prev) / std_prev

                close_prev = df.get(f"{ticker}_close_prev")
                low_prev = df.get(f"{ticker}_BB_LOWER_prev")
                mid_prev = df.get(f"{ticker}_BB_MID_prev")
                up_prev = df.get(f"{ticker}_BB_UPPER_prev")
                bb_z_prev = df.get(f"{ticker}_BB_Z_prev")

                # Choose BB rule
                if bb_rule == "below_lower":
                    bb_mask = close_prev.lt(low_prev)
                elif bb_rule == "cross_up_from_below":
                    prev_below = close_prev.shift(1).lt(low_prev.shift(1))
                    now_at_or_above = close_prev.ge(low_prev)
                    bb_mask = prev_below & now_at_or_above
                else:  # "touch_lower"
                    bb_mask = close_prev.le(low_prev)

                bb_mask = bb_mask.fillna(False)
                bb_mid_prev, bb_up_prev, bb_low_prev = mid_prev, up_prev, low_prev
        else:
            # BB disabled
            bb_mask = pd.Series(True, index=df.index, dtype="bool")
            bb_mid_prev = bb_up_prev = bb_low_prev = pd.Series(pd.NA, index=df.index)
            bb_z_prev = pd.Series(pd.NA, index=df.index)

        # --- Combined entry rule ---
        mask = rsi_mask & ma_mask & bb_mask
        if not mask.any():
            continue

        # Collect signal rows
        cols = [
            "Date",
            f"{ticker}_open", f"{ticker}_high",
            f"{ticker}_low",  f"{ticker}_close",
            f"{ticker}_close_prev",
        ]

        # pick only columns that exist (avoids KeyError if some are missing)
        available_cols = [c for c in cols if c in df.columns]
        s = df.loc[mask, available_cols].copy()

        # Add metadata
        s["asset"] = ticker
        s["ma_passes"] = ma_passes.loc[mask].astype(int)
        s["allocation_pct"] = allocation_pct.loc[mask]
        s["bb_rule"] = bb_rule if use_bbands else pd.NA
        s["bb_mid_prev"] = bb_mid_prev.loc[mask]
        s["bb_up_prev"] = bb_up_prev.loc[mask]
        s["bb_low_prev"] = bb_low_prev.loc[mask]
        s["bb_z_prev"] = bb_z_prev.loc[mask]  # negative means below mid; ~-2 at/below lower band

        # Standardize column names
        rename_map = {
            f"{ticker}_open": "open",
            f"{ticker}_high": "high",
            f"{ticker}_low": "low",
            f"{ticker}_close": "close",
            f"{ticker}_close_prev": "close_prev",
        }
        s.rename(columns={k: v for k, v in rename_map.items() if k in s.columns}, inplace=True)

        signals.append(s)

    signals_df = (
        pd.concat(signals, ignore_index=True)
        if signals else
        pd.DataFrame(columns=[
            "Date", "open", "high", "low", "close", "asset",
            "ma_passes", "allocation_pct",
            "bb_rule", "bb_mid_prev", "bb_up_prev", "bb_low_prev", "bb_z_prev",
            "close_prev",
        ])
    )

    # Sort and de-dup (1 per asset per timestamp)
    if not signals_df.empty:
        signals_df = signals_df.sort_values(by="Date")
        signals_df = signals_df.drop_duplicates(subset=["Date", "asset"])

    return signals_df
