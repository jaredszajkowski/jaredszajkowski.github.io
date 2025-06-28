---
title: "Investigating A VIX Trading Signal, Part 3: Trading"
description: A brief look at finding a trading signal based on moving averages of the VIX.
slug: investigating-a-vix-trading-signal-part-3-trading
date: 2025-03-03 00:00:01+0000
lastmod: 2025-06-10 00:00:01+0000
image: cover.jpg
draft: false
categories:
    - Financial Data
    - Trading
tags:
    - Python
    - Yahoo Finance
    - pandas
    - VIX
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Trading History

I have began trading based on the ideas from [part 2](/2025/03/02/investigating-a-vix-trading-signal-part-2-finding-a-signal/), opening positions during the VIX spikes and closing them as volatility comes back down. The executed trades, closed positions, and open positions listed below are all automated updates from the transaction history exports from Schwab. The exported CSV files are available in the GitHub repository.

### Trades Executed

Here are the trades executed to date, with any comments related to execution, market sentiment, reason for opening/closing position, VIX level, etc.

<!-- INSERT_10_Trades_Executed_HERE -->

#### Volatility In August 2024

Plot with VIX level, trade side, VIX option, and VIX level at trade date/time:

![VIX Level, Trades](11_VIX_Spike_Trades_2024-07-26_2024-12-07.png)

Closed positions:

<!-- INSERT_11_Closed_Positions_2024-09-18_2024-12-18_2024-08-05_2024-11-27_HERE -->

Open positions:

<!-- INSERT_11_Open_Positions_2024-09-18_2024-12-18_2024-08-05_2024-11-27_HERE -->

Percent profit/loss: <!-- INSERT_11_Percent_PnL_2024-09-18_2024-12-18_2024-08-05_2024-11-27_HERE -->

Net profit/loss: <!-- INSERT_11_PnL_2024-09-18_2024-12-18_2024-08-05_2024-11-27_HERE -->

#### Volatility In March 2025

Plot with VIX level, trade side, VIX option, and VIX level at trade date/time:

![VIX Level, Trades](12_VIX_Spike_Trades_2025-02-22_2025-04-03.png)

Closed positions:

<!-- INSERT_12_Closed_Positions_2025-04-16_2025-04-16_2025-03-04_2025-03-24_HERE -->

Open positions:

<!-- INSERT_12_Open_Positions_2025-04-16_2025-04-16_2025-03-04_2025-03-24_HERE -->

Percent profit/loss: <!-- INSERT_12_Percent_PnL_2025-04-16_2025-04-16_2025-03-04_2025-03-24_HERE -->

Net profit/loss: <!-- INSERT_12_PnL_2025-04-16_2025-04-16_2025-03-04_2025-03-24_HERE -->

#### Volatility In April 2025

Plot with VIX level, trade side, VIX option, and VIX level at trade date/time:

![VIX Level, Trades](13_VIX_Spike_Trades_2025-02-28_2025-05-23.png)

Closed positions:

<!-- INSERT_13_Closed_Positions_2025-05-21_2025-08-20_2025-03-10_2025-05-13_HERE -->

Open positions:

<!-- INSERT_13_Open_Positions_2025-05-21_2025-08-20_2025-03-10_2025-05-13_HERE -->

Percent profit/loss: <!-- INSERT_13_Percent_PnL_2025-05-21_2025-08-20_2025-03-10_2025-05-13_HERE -->

Net profit/loss: <!-- INSERT_13_PnL_2025-05-21_2025-08-20_2025-03-10_2025-05-13_HERE -->

#### Low Volatility In June 2025

Plot with VIX level, trade side, VIX option, and VIX level at trade date/time:

![VIX Level, Trades](14_VIX_Spike_Trades_2025-06-16_2025-10-06.png)

Closed positions:

<!-- INSERT_14_Closed_Positions_2025-09-17_2025-10-22_2025-06-26_2025-09-26_HERE -->

Open positions:

<!-- INSERT_14_Open_Positions_2025-09-17_2025-10-22_2025-06-26_2025-09-26_HERE -->

Percent profit/loss: <!-- INSERT_14_Percent_PnL_2025-09-17_2025-10-22_2025-06-26_2025-09-26_HERE -->

Net profit/loss: <!-- INSERT_14_PnL_2025-09-17_2025-10-22_2025-06-26_2025-09-26_HERE -->

#### Complete Trade History

Percent profit/loss: <!-- INSERT_99_Percent_PnL_None_None_None_None_HERE -->

Net profit/loss: <!-- INSERT_99_PnL_None_None_None_None_HERE -->

## References

1. https://www.cboe.com/tradable_products/vix/
2. https://github.com/ranaroussi/yfinance

## Code

Note: The files below are identical to those linked in [part 1](/2025/03/01/investigating-a-vix-trading-signal-part-1-vix-and-vvix/#code) and [part 2](/2025/03/02/investigating-a-vix-trading-signal-part-2-finding-a-signal/#code).

The jupyter notebook with the functions and all other code is available [here](investigating-a-vix-trading-signal-part-3-trading.ipynb).</br>
The html export of the jupyter notebook is available [here](investigating-a-vix-trading-signal-part-3-trading.html).</br>
The pdf export of the jupyter notebook is available [here](investigating-a-vix-trading-signal-part-3-trading.pdf).