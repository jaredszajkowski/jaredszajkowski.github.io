# # Original function

# def backtest_rsi_multi_asset_strategy(
#     tickers: list,
#     prices: pd.DataFrame,
#     signals: pd.DataFrame,
#     initial_capital: float,
#     rsi_threshold: float,
#     trailing_stop_pct: float,
#     ma_days: list,
# ) -> pd.DataFrame:
    
#     """
#     Multi-asset backtest using RSI threshold + MA filter + trailing stop.
    
#     Capital is shared across all assets. Each asset trades independently.

#     Parameters:
#     - data: dict of enriched DataFrames keyed by asset symbol (must have RSI and MA columns)
#     - initial_capital: starting cash
#     - rsi_threshold: RSI entry trigger (e.g., 30)
#     - trailing_stop_pct: trailing stop trigger (e.g., 0.02)
#     - ma_days: list of moving average day lengths

#     Returns:
#     - DataFrame of all trades across assets
#     """
          
#     # Copy prices Dataframe and find timestamps
#     prices_df = prices.copy()
#     prices_df = prices_df.set_index('Date')
#     prices_ts = prices_df.index.unique()
    
#     # Copy signals DataFrame and find timestamps
#     signals_df = signals.copy()
#     signals_map = {ts: grp for ts, grp in signals_df.groupby("Date")}

#     # Initialize tracking variables
#     cash = initial_capital

#     # Create list for trades
#     trades = []

#     # Create dictionary to hold positions
#     positions = {ticker: None for ticker in tickers}

#     # Iterate through prices_df
#     for timestamp in prices_ts:

#         # Check if timestamp is in signals_map
#         if timestamp in signals_map:

#             # Get the group of signal rows for this timestamp
#             signal_rows = signals_map[timestamp]

#             # Iterate over each asset in the signal rows
#             for _, signal_row in signal_rows.iterrows():

#                 # Get the ticker
#                 ticker = signal_row['asset']

#                 # Get position
#                 position = positions.get(ticker)

#                 if position is not None:
#                     continue

#                 # -------- ENTRY (assuming no existing position) --------

#                 # Get allocation_pct
#                 allocation_pct = signal_row['allocation_pct']

#                 # Calculate capital based on number of assets and allocation_pct
#                 capital_to_use = cash / len(tickers) * allocation_pct

#                 # -- Alternate to use all available cash --
#                 # active = len(srows)  # number of signals at this timestamp
#                 # capital_to_use = (cash / max(1, active)) * allocation_pct

#                 # Get entry price
#                 entry_price = signal_row["open"]  # execute at current open

#                 # Calculate quantity to buy
#                 quantity = capital_to_use / entry_price

#                 # Store position details
#                 positions[ticker] = {
#                     "entry_time": timestamp,
#                     "entry_price": entry_price,
#                     "peak_price": entry_price,
#                     "quantity": quantity,
#                     "allocation_pct": allocation_pct,
#                 }

#                 cash -= quantity * entry_price

#         # Iterate through tickers
#         for ticker in tickers:

#             # Get position
#             position = positions.get(ticker)

#             if position is None:
#                 continue

#             # Get current row in prices_df
#             row = prices_df.loc[timestamp]

#             # Get prices
#             high_price = row[f"{ticker}_high"]
#             low_price  = row[f"{ticker}_low"]
#             open_price = row[f"{ticker}_open"]

#             # Update peak price with current bar high
#             peak_price = max(position["peak_price"], high_price)

#             # Update trailing stop price
#             stop_price = peak_price * (1 - trailing_stop_pct)

#             # -------- EXIT (assuming existing position) --------

#             # Breach check (intra-bar)
#             if low_price <= stop_price:
#                 # Gap handling: if open < stop, you're filled at open; otherwise at stop
#                 if open_price < stop_price:
#                     exit_price = open_price
#                 else:
#                     exit_price = stop_price

#                 quantity = position["quantity"]
#                 entry_price = position["entry_price"]

#                 pnl = quantity * (exit_price - entry_price)
#                 return_dec = (exit_price - entry_price) / entry_price

#                 cash += quantity * exit_price

#                 trades.append(
#                     {
#                         "asset": ticker,
#                         "entry_time": position["entry_time"],
#                         "exit_time": timestamp,
#                         "entry_price": entry_price,
#                         "exit_price": exit_price,
#                         "quantity": quantity,
#                         "allocation_pct": position["allocation_pct"],
#                         "pnl": pnl,
#                         "return_dec": return_dec,
#                         "cash": cash,
#                     }
#                 )

#                 # Set position back to None after exit
#                 positions[ticker] = None

#             else:
#                 # carry forward higher peak
#                 positions[ticker]["peak_price"] = peak_price

#     # Create new dataframe for trades
#     trades_df = pd.DataFrame(trades)

#     # If there are entries, calc cumulative pnl, equity, cumulative return
#     if not trades_df.empty:
#         trades_df["cumulative_pnl"] = trades_df["pnl"].cumsum()
#         trades_df["equity"] = trades_df["cumulative_pnl"] + initial_capital
#         trades_df["cumulative_return"] = trades_df["equity"] / initial_capital - 1

#     return trades_df

# # Revised function using DataFrames

# def backtest_rsi_multi_asset_strategy(
#     tickers: list,
#     prices: pd.DataFrame,
#     signals: pd.DataFrame,
#     initial_capital: float,
#     rsi_threshold: float,
#     trailing_stop_pct: float,
#     ma_days: list,
# ) -> pd.DataFrame:
    
#     """
#     Multi-asset backtest using RSI threshold + MA filter + trailing stop.
    
#     Capital is shared across all assets. Each asset trades independently.

#     Parameters:
#     - data: dict of enriched DataFrames keyed by asset symbol (must have RSI and MA columns)
#     - initial_capital: starting cash
#     - rsi_threshold: RSI entry trigger (e.g., 30)
#     - trailing_stop_pct: trailing stop trigger (e.g., 0.02)
#     - ma_days: list of moving average day lengths

#     Returns:
#     - DataFrame of all trades across assets
#     """
          
#     # Copy prices Dataframe and find timestamps
#     prices_df = prices.copy()
    
#     # Copy signals DataFrame and find timestamps
#     signals_df = signals.copy()
#     signals_map = {ts: grp for ts, grp in signals_df.groupby("Date")}

#     # Initialize tracking variables
#     cash = initial_capital

#     # Create list for trades
#     trades = []

#     # Start with the first timestamp
#     next_timestamp = prices_df['Date'].iloc[0]

#     # Iterate through signals_df
#     for timestamp in signals_map:

#         if timestamp <= next_timestamp:
#             continue

#         # Get the group of signal rows for this timestamp
#         signal_rows = signals_map[timestamp]

#         # Iterate over each asset in the signal rows
#         for _, signal_row in signal_rows.iterrows():

#             # Get the ticker
#             ticker = signal_row['asset']

#             # -------- ENTRY --------

#             # Set entry timestamp
#             entry_timestamp = timestamp

#             # Get allocation_pct
#             allocation_pct = signal_row['allocation_pct']

#             # Calculate capital based on number of assets and allocation_pct
#             capital_to_use = cash / len(tickers) * allocation_pct

#             # -- Alternate to use all available cash --
#             # active = len(srows)  # number of signals at this timestamp
#             # capital_to_use = (cash / max(1, active)) * allocation_pct

#             # Get entry price
#             entry_price = signal_row["open"]  # execute at current open

#             # Calculate quantity to buy
#             quantity = capital_to_use / entry_price

#             # Update cash position
#             cash -= quantity * entry_price

#             # -------- EXIT --------

#             # Filter by date >= timestamp
#             temp_prices_df = prices_df[prices_df['Date'] >= entry_timestamp].copy()

#             # Update peak price with current bar high
#             temp_prices_df[f"{ticker}_high_cummax"] = temp_prices_df[f"{ticker}_high"].cummax()
#             temp_prices_df[f"{ticker}_peak_price"] = np.where(temp_prices_df[f"{ticker}_high_cummax"] > entry_price, temp_prices_df[f"{ticker}_high_cummax"], entry_price)

#             # Update trailing stop price
#             temp_prices_df[f"{ticker}_stop_price"] = temp_prices_df[f"{ticker}_peak_price"] * (1 - trailing_stop_pct)

#             # Breach check (intra-bar)
#             temp_prices_df[f"{ticker}_exit_price"] = np.select(
#                 condlist = [(temp_prices_df[f"{ticker}_low"] <= temp_prices_df[f"{ticker}_stop_price"]) & (temp_prices_df[f"{ticker}_open"] <= temp_prices_df[f"{ticker}_stop_price"]), temp_prices_df[f"{ticker}_low"] <= temp_prices_df[f"{ticker}_stop_price"]],
#                 choicelist = [temp_prices_df[f"{ticker}_open"], temp_prices_df[f"{ticker}_stop_price"]],
#             )

#             # Get exit price
#             try:
#                 exit_price = temp_prices_df.loc[temp_prices_df[f"{ticker}_exit_price"] > 0, f"{ticker}_exit_price"].iloc[0]
#             except:
#                 continue

#             # Set exit timestamp
#             exit_timestamp = temp_prices_df.loc[temp_prices_df[f"{ticker}_exit_price"] > 0, "Date"].iloc[0]

#             # Calc pnl, return
#             pnl = quantity * (exit_price - entry_price)
#             return_dec = (exit_price - entry_price) / entry_price

#             # Update cash position
#             cash += quantity * exit_price

#             # Add to trades
#             trades.append(
#                 {
#                     "asset": ticker,
#                     "entry_time": entry_timestamp,
#                     "exit_time": exit_timestamp,
#                     "entry_price": entry_price,
#                     "exit_price": exit_price,
#                     "quantity": quantity,
#                     "allocation_pct": allocation_pct,
#                     "pnl": pnl,
#                     "return_dec": return_dec,
#                     "cash": cash,
#                 }
#             )

#             # Update next_timestamp
#             next_timestamp = exit_timestamp

#     # Create new dataframe for trades
#     trades_df = pd.DataFrame(trades)

#     # If there are entries, calc cumulative pnl, equity, cumulative return
#     if not trades_df.empty:
#         trades_df["cumulative_pnl"] = trades_df["pnl"].cumsum()
#         trades_df["equity"] = trades_df["cumulative_pnl"] + initial_capital
#         trades_df["cumulative_return"] = trades_df["equity"] / initial_capital - 1

#     return trades_df

# Last revision using numpy arrays

import numpy as np
import pandas as pd


def backtest_rsi_multi_asset_strategy(
    tickers: list,
    prices: pd.DataFrame,
    signals: pd.DataFrame,
    initial_capital: float,
    rsi_threshold: float,          # kept for signature compatibility (unused here)
    trailing_stop_pct: float,
    ma_days: list,                 # kept for signature compatibility (unused here)
    order_entry: str,
    trading_fees: bool,
    trade_taker_fee: float, # market order fee
    trade_maker_fee: float, # limit order fee
) -> pd.DataFrame:
    """
    Optimized backtest with legacy 'no-exit leaves cash stuck' behavior:
    - If no exit is found from entry to the end of data, cash is NOT refunded and the
      trade remains open (matching your original implementation).
    - Avoids copying prices_df inside the loop; uses NumPy views for speed.
    """

    # Stable sort; shallow (meta-only) copy to avoid duplicating data
    prices_df = prices.copy(deep=False).sort_values(by="Date", kind="mergesort")
    date_idx = prices_df["Date"].to_numpy()

    # Create dictionary of prices as numpy arrays
    prices_dict = {}
    for t in tickers:
        prices_dict[t] = (
            prices_df[f"{t}_open"].to_numpy(),
            prices_df[f"{t}_high"].to_numpy(),
            prices_df[f"{t}_low"].to_numpy(),
        )

    # Chronological signals; shallow copy to keep memory low
    signals_sorted_df = signals.copy(deep=False).sort_values(by="Date", kind="mergesort")
    signals_grouped_df = signals_sorted_df.groupby("Date", sort=True)

    # Initialize tracking variables
    cash = initial_capital

    # Initialize trading fee
    trade_entry_fee_dec = 0.0
    trade_exit_fee_dec = 0.0

    # Create list for trades
    trades = []

    # Start with the first timestamp
    next_timestamp = prices_df['Date'].iloc[0]

    # Iterate through signals DataFrame
    for timestamp, signal_rows in signals_grouped_df:
        
        # Check if signal was during a previous trade
        if timestamp <= next_timestamp:
            continue

        # Iterate over each asset
        for signal in signal_rows.itertuples(index=False):
            
            # -------- ENTRY --------

            # Get the ticker
            ticker = getattr(signal, "asset")

            # Set the entry timestamp
            entry_timestamp = timestamp
            
            # Get the allocation
            allocation_pct = getattr(signal, "allocation_pct")

            # Calc capital based on number of assets and allocation_pct
            capital_to_use = cash / len(tickers) * allocation_pct

            # # Shared capital, scaled by allocation
            # capital_to_use = (cash / max(1, len(tickers))) * allocation_pct
            # if capital_to_use <= 0:
            #     continue

            # Get entry price and trade entry fee percentage
            # Entry on open for a market order
            if order_entry == "market":
                entry_price = getattr(signal, "open")
                if trading_fees:
                    trade_entry_fee_dec = trade_taker_fee
            # Entry on a limit order set at previous candle close
            elif order_entry == "limit":
                close_prev = getattr(signal, "close_prev")
                high = getattr(signal, "high")
                low = getattr(signal, "low")

                if close_prev >= low and close_prev <= high:
                    entry_price = getattr(signal, "close_prev")
                    if trading_fees:
                        trade_entry_fee_dec = trade_maker_fee
                else:
                    continue

            # Calc entry value and entry fee
            entry_value = capital_to_use / (1.0 + trade_entry_fee_dec)
            entry_fee = capital_to_use - entry_value

            # Calc quantity to buy
            quantity = entry_value / entry_price
            
            # Update cash position based on entry
            cash -= entry_value
            cash -= entry_fee
            
            # -------- EXIT --------

            # Extract numpy arrays
            open_nparray, high_nparray, low_nparray = prices_dict[ticker]

            # Find signal timestamp in prices date index, start is index value
            start = np.searchsorted(date_idx, np.datetime64(entry_timestamp), side="left")
            if start >= len(date_idx):
                # No bars remain; legacy behavior: keep cash debited, position stays open
                continue

            # Slices from the price numpy arrays
            o_sub = open_nparray[start:]
            h_sub = high_nparray[start:]
            l_sub = low_nparray[start:]
            d_sub = date_idx[start:]

            # Running peak (never below entry price)
            peak_price = np.maximum.accumulate(np.maximum(h_sub, entry_price))
            stop_price = peak_price * (1.0 - trailing_stop_pct)

            # Gap-breach first: open <= stop and low <= stop -> exit at open
            gap_idx = np.flatnonzero((l_sub <= stop_price) & (o_sub <= stop_price))

            # Regular breach: low <= stop -> exit at stop price
            br_idx = np.flatnonzero(l_sub <= stop_price)

            i_gap = int(gap_idx[0]) if gap_idx.size else np.inf
            i_br  = int(br_idx[0])  if br_idx.size  else np.inf

            if np.isinf(min(i_gap, i_br)):
                # ---- LEGACY QUIRK: no exit to end of data -> keep cash debited, stay open
                continue

            if i_gap <= i_br:
                # Gap-breach is earlier (or same bar) -> exit at open
                i = i_gap
                exit_timestamp = pd.Timestamp(d_sub[i].astype("datetime64[ns]"))
                exit_price = float(o_sub[i])
                order_exit = "exit at open (gap)"
            else:
                # Regular breach is earlier -> exit at stop level of that bar
                i = i_br
                exit_timestamp = pd.Timestamp(d_sub[i].astype("datetime64[ns]"))
                exit_price = float(stop_price[i])
                order_exit = "trailing stop"

            # Get trade exit fee percentage
            if trading_fees:
                trade_exit_fee_dec = trade_taker_fee

            # Calc exit value and exit fee
            exit_value = quantity * exit_price
            exit_fee = exit_value * trade_exit_fee_dec

            # Update cash position based on exit
            cash += exit_value
            cash -= exit_fee

            # Calc pnl, return
            pnl = (exit_value - exit_fee) - (entry_value + entry_fee)
            return_dec = pnl / capital_to_use
            
            # Add to trades list
            trades.append(
                {
                    "asset": ticker,
                    "entry_time": entry_timestamp,
                    "entry_type": order_entry,
                    "entry_price": entry_price,
                    "exit_time": exit_timestamp,
                    "exit_type": order_exit,
                    "exit_price": exit_price,
                    "quantity": quantity,
                    "allocation_pct": allocation_pct,
                    "pnl": pnl,
                    "return": return_dec,
                    "cash": cash,
                    "entry_fee": entry_fee,
                    "exit_fee": exit_fee,
                }
            )

            # Update next_timestamp
            next_timestamp = exit_timestamp

    # Create new dataframe for trades
    trades_df = pd.DataFrame(trades)

    # If there are entries, calc cumulative pnl, equity, cumulative return
    if not trades_df.empty:
        trades_df["cumulative_pnl"] = trades_df["pnl"].cumsum()
        trades_df["equity"] = trades_df["cumulative_pnl"] + initial_capital
        trades_df["cumulative_return"] = trades_df["equity"] / initial_capital - 1

    return trades_df
