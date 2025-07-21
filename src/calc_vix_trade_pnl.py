import pandas as pd

def calc_vix_trade_pnl(
    transaction_df: pd.DataFrame,
    exp_start_date: str,
    exp_end_date: str,
    trade_start_date: str,
    trade_end_date: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, str, str, str]:
    
    """
    Calculate the profit and loss (PnL) of trades based on transaction data.

    Parameters:
    -----------
    transaction_df : pd.DataFrame
        DataFrame containing transaction data.
    exp_start_date : str
        Start date for filtering transactions in 'YYYY-MM-DD' format. This is the start of the range for the option expiration date.
    exp_end_date : str
        End date for filtering transactions in 'YYYY-MM-DD' format. This is the end of the range for the option expiration date.
    trade_start_date : str
        Start date for filtering transactions in 'YYYY-MM-DD' format. This is the start of the range for the trade date.
    trade_end_date : str
        End date for filtering transactions in 'YYYY-MM-DD' format. This is the end of the range for the trade date.

    Returns:
    --------
    transactions_data : pd.DataFrame
        Dataframe containing the transactions for the specified timeframe.
    closed_trades : pd.DataFrame
        DataFrame containing the closed trades with realized PnL and percent PnL.
    open_trades : pd.DataFrame
        DataFrame containing the open trades.
    net_PnL_percent_str : str
        String representation of the net profit percentage.
    net_PnL_str : str
        String representation of the net profit and loss in dollars.
    """

    # If start and end dates for trades and expirations are None, use the entire DataFrame
    if exp_start_date is None and exp_end_date is None and trade_start_date is None and trade_end_date is None:
        transactions_data = transaction_df
    
    # If both start and end dates for trades and expirations are provided then filter by both
    else:
        transactions_data = transaction_df[
            (transaction_df['Exp_Date'] >= exp_start_date) & (transaction_df['Exp_Date'] <= exp_end_date) &
            (transaction_df['Trade_Date'] >= trade_start_date) & (transaction_df['Trade_Date'] <= trade_end_date)
        ]

    # Combine the 'Action' and 'Symbol' columns to create a unique identifier for each transaction
    transactions_data['TradeDate_Action_Symbol_VIX'] = (
        transactions_data['Trade_Date'].astype(str) + 
        ", " + 
        transactions_data['Action'] + 
        ", " + 
        transactions_data['Symbol'] + 
        ", VIX = " + 
        transactions_data['Approx_VIX_Level'].astype(str)
    )

    # Split buys and sells and sum the notional amounts
    transactions_sells = transactions_data[transactions_data['Action'] == 'Sell to Close']
    transactions_sells = transactions_sells.groupby(['Symbol', 'Exp_Date'], as_index=False)[['Amount', 'Quantity']].sum()

    transactions_buys = transactions_data[transactions_data['Action'] == 'Buy to Open']
    transactions_buys = transactions_buys.groupby(['Symbol', 'Exp_Date'], as_index=False)[['Amount', 'Quantity']].sum()

    # Merge buys and sells dataframes back together
    merged_transactions = pd.merge(transactions_buys, transactions_sells, on=['Symbol', 'Exp_Date'], how='outer', suffixes=('_Buy', '_Sell'))
    merged_transactions = merged_transactions.sort_values(by=['Exp_Date'], ascending=[True])
    merged_transactions = merged_transactions.reset_index(drop=True)

    # Identify the closed positions
    merged_transactions['Closed'] = (~merged_transactions['Amount_Sell'].isna()) & (~merged_transactions['Amount_Buy'].isna()) & (merged_transactions['Quantity_Buy'] == merged_transactions['Quantity_Sell'])

    # Create a new dataframe for closed positions
    closed_trades = merged_transactions[merged_transactions['Closed']]
    closed_trades = closed_trades.reset_index(drop=True)
    closed_trades['Realized_PnL'] = closed_trades['Amount_Sell'] - closed_trades['Amount_Buy']
    closed_trades['Percent_PnL'] = closed_trades['Realized_PnL'] / closed_trades['Amount_Buy']
    closed_trades.drop(columns={'Closed', 'Exp_Date'}, inplace=True)
    closed_trades['Quantity_Sell'] = closed_trades['Quantity_Sell'].astype(int)

    # Calculate the net % PnL
    net_PnL_percent = closed_trades['Realized_PnL'].sum() / closed_trades['Amount_Buy'].sum()
    net_PnL_percent_str = f"{round(net_PnL_percent * 100, 2)}%"

    # Calculate the net $ PnL
    net_PnL = closed_trades['Realized_PnL'].sum()
    net_PnL_str = f"${net_PnL:,.2f}"

    # Create a new dataframe for open positions
    open_trades = merged_transactions[~merged_transactions['Closed']]
    open_trades = open_trades.reset_index(drop=True)
    open_trades.drop(columns={'Closed', 'Amount_Sell', 'Quantity_Sell', 'Exp_Date'}, inplace=True)

    # Calculate the total market value of opened positions
    # If start and end dates for trades and expirations are None, use only the closed positions
    if exp_start_date is None and exp_end_date is None and trade_start_date is None and trade_end_date is None:
        total_opened_pos_mkt_val = closed_trades['Amount_Buy'].sum()
    else:
        total_opened_pos_mkt_val = closed_trades['Amount_Buy'].sum() + open_trades['Amount_Buy'].sum()
    total_opened_pos_mkt_val_str = f"${total_opened_pos_mkt_val:,.2f}"

    # Calculate the total market value of closed positions
    total_closed_pos_mkt_val = closed_trades['Amount_Sell'].sum()
    total_closed_pos_mkt_val_str = f"${total_closed_pos_mkt_val:,.2f}"

    return transactions_data, closed_trades, open_trades, net_PnL_percent_str, net_PnL_str, total_opened_pos_mkt_val_str, total_closed_pos_mkt_val_str