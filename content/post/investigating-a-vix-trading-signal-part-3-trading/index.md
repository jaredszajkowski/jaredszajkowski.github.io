---
title: "Investigating A VIX Trading Signal, Part 3: Trading"
description: A brief look at finding a trading signal based on moving averages of the VIX.
slug: investigating-a-vix-trading-signal-part-3-trading
date: 2025-03-03 00:00:01+0000
lastmod: 2025-07-21 00:00:01+0000
image: cover.jpg
draft: false
categories:
    - Pandas
    - Python
    - Trading
    - VIX
    - Yahoo Finance
# tags:
#     - Python
#     - Yahoo Finance
#     - pandas
#     - VIX
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Trading History

I have recently started trading based on the ideas from [part 2](/2025/03/02/investigating-a-vix-trading-signal-part-2-finding-a-signal/), using the following as guidelines:

* Look for opportunities when the VIX is the 7 - 10th deciles to buy puts, opening positions during the VIX spikes and closing them as volatility comes back down
* Look for opportunities when the VIX is in the 1 - 4th deciles to buy calls during periods of lower volatility based on seasonality
* When volatility spikes, sell call spreads and buy puts
* When volatility is low, buy calls
* Open positions with 2, 3, and 4 months to expiration
* Close positions within 4 - 5 weeks of expiration to avoid theta drag

The executed trades, closed positions, and open positions listed below are all automated updates from the transaction history exports from Schwab. The exported CSV files are available in the GitHub repository.

### Trades Executed

Here are the trades executed to date, with any comments related to execution, market sentiment, reason for opening/closing position, VIX level, etc.

| Trade_Date          | Action        | Symbol                 |   Quantity |   Price |   Fees & Comm |   Amount |   Approx_VIX_Level | Comments                                                                                      |
|:--------------------|:--------------|:-----------------------|-----------:|--------:|--------------:|---------:|-------------------:|:----------------------------------------------------------------------------------------------|
| 2024-08-05 00:00:00 | Buy to Open   | VIX 09/18/2024 34.00 P |          1 |   10.95 |          1.08 |  1096.08 |              34.33 | nan                                                                                           |
| 2024-08-21 00:00:00 | Sell to Close | VIX 09/18/2024 34.00 P |          1 |   17.95 |          1.08 |  1793.92 |              16.50 | nan                                                                                           |
| 2024-08-05 00:00:00 | Buy to Open   | VIX 10/16/2024 40.00 P |          1 |   16.35 |          1.08 |  1636.08 |              42.71 | nan                                                                                           |
| 2024-09-18 00:00:00 | Sell to Close | VIX 10/16/2024 40.00 P |          1 |   21.54 |          1.08 |  2152.92 |              18.85 | nan                                                                                           |
| 2024-08-07 00:00:00 | Buy to Open   | VIX 11/20/2024 25.00 P |          2 |    5.90 |          2.16 |  1182.16 |              27.11 | nan                                                                                           |
| 2024-11-04 00:00:00 | Sell to Close | VIX 11/20/2024 25.00 P |          2 |    6.10 |          2.16 |  1217.84 |              22.43 | nan                                                                                           |
| 2024-08-06 00:00:00 | Buy to Open   | VIX 12/18/2024 30.00 P |          1 |   10.25 |          1.08 |  1026.08 |              32.27 | nan                                                                                           |
| 2024-11-27 00:00:00 | Sell to Close | VIX 12/18/2024 30.00 P |          1 |   14.95 |          1.08 |  1493.92 |              14.04 | nan                                                                                           |
| 2025-03-04 00:00:00 | Buy to Open   | VIX 04/16/2025 25.00 P |          5 |    5.65 |          5.40 |  2830.40 |              25.75 | nan                                                                                           |
| 2025-03-24 00:00:00 | Sell to Close | VIX 04/16/2025 25.00 P |          5 |    7.00 |          5.40 |  3494.60 |              18.01 | nan                                                                                           |
| 2025-03-10 00:00:00 | Buy to Open   | VIX 05/21/2025 26.00 P |          5 |    7.10 |          5.40 |  3555.40 |              27.54 | Missed opportunity to close position for 20% profit before vol spike in early April 2025      |
| 2025-04-04 00:00:00 | Buy to Open   | VIX 05/21/2025 26.00 P |         10 |    4.10 |         10.81 |  4110.81 |              38.88 | Averaged down on existing position                                                            |
| 2025-04-24 00:00:00 | Sell to Close | VIX 05/21/2025 26.00 P |          7 |    3.50 |          7.57 |  2442.43 |              27.37 | Sold half of position due to vol spike concerns and theta                                     |
| 2025-05-02 00:00:00 | Sell to Close | VIX 05/21/2025 26.00 P |          4 |    4.35 |          4.32 |  1735.68 |              22.73 | Sold half of remaining position due to vol spike concerns and theta                           |
| 2025-05-07 00:00:00 | Sell to Close | VIX 05/21/2025 26.00 P |          4 |    3.55 |          4.32 |  1415.68 |              24.49 | Closed position ahead of Fed’s (Powell’s) comments                                            |
| 2025-04-04 00:00:00 | Buy to Open   | VIX 05/21/2025 37.00 P |          3 |   13.20 |          3.24 |  3963.24 |              36.46 | nan                                                                                           |
| 2025-05-07 00:00:00 | Sell to Close | VIX 05/21/2025 37.00 P |          3 |   13.75 |          3.24 |  4121.76 |              24.51 | Closed position ahead of Fed’s (Powell’s) comments                                            |
| 2025-04-08 00:00:00 | Buy to Open   | VIX 05/21/2025 50.00 P |          2 |   21.15 |          2.16 |  4232.16 |             nan    | nan                                                                                           |
| 2025-04-24 00:00:00 | Sell to Close | VIX 05/21/2025 50.00 P |          1 |   25.30 |          1.08 |  2528.92 |             nan    | nan                                                                                           |
| 2025-04-25 00:00:00 | Sell to Close | VIX 05/21/2025 50.00 P |          1 |   25.65 |          1.08 |  2563.92 |             nan    | nan                                                                                           |
| 2025-04-03 00:00:00 | Buy to Open   | VIX 06/18/2025 27.00 P |          8 |    7.05 |          8.65 |  5648.65 |              27.62 | nan                                                                                           |
| 2025-04-08 00:00:00 | Buy to Open   | VIX 06/18/2025 27.00 P |          4 |    4.55 |          4.32 |  1824.32 |              55.44 | Averaged down on existing position                                                            |
| 2025-05-12 00:00:00 | Sell to Close | VIX 06/18/2025 27.00 P |          6 |    7.55 |          6.49 |  4523.51 |              19.05 | Market up on positive news of lowering tariffs with China; VIX down 15%, VVIX down 10%        |
| 2025-05-12 00:00:00 | Sell to Close | VIX 06/18/2025 27.00 P |          6 |    7.40 |          6.49 |  4433.51 |              19.47 | Market up on positive news of lowering tariffs with China; VIX down 15%, VVIX down 10%        |
| 2025-04-04 00:00:00 | Buy to Open   | VIX 06/18/2025 36.00 P |          3 |   13.40 |          3.24 |  4023.24 |              36.61 | nan                                                                                           |
| 2025-05-12 00:00:00 | Sell to Close | VIX 06/18/2025 36.00 P |          3 |   16.00 |          3.24 |  4796.76 |              19.14 | Market up on positive news of lowering tariffs with China; VIX down 15%, VVIX down 10%        |
| 2025-04-07 00:00:00 | Buy to Open   | VIX 06/18/2025 45.00 P |          2 |   18.85 |          2.16 |  3772.16 |              53.65 | nan                                                                                           |
| 2025-05-12 00:00:00 | Sell to Close | VIX 06/18/2025 45.00 P |          2 |   25.00 |          2.16 |  4997.84 |              19.24 | Market up on positive news of lowering tariffs with China; VIX down 15%, VVIX down 10%        |
| 2025-04-03 00:00:00 | Buy to Open   | VIX 07/16/2025 29.00 P |          5 |    8.55 |          5.40 |  4280.40 |              29.03 | nan                                                                                           |
| 2025-05-13 00:00:00 | Sell to Close | VIX 07/16/2025 29.00 P |          3 |   10.40 |          3.24 |  3116.76 |              17.72 | nan                                                                                           |
| 2025-05-13 00:00:00 | Sell to Close | VIX 07/16/2025 29.00 P |          2 |   10.30 |          2.16 |  2057.84 |              17.68 | nan                                                                                           |
| 2025-04-04 00:00:00 | Buy to Open   | VIX 07/16/2025 36.00 P |          3 |   13.80 |          3.24 |  4143.24 |              36.95 | nan                                                                                           |
| 2025-05-13 00:00:00 | Sell to Close | VIX 07/16/2025 36.00 P |          1 |   17.00 |          1.08 |  1698.92 |              17.79 | nan                                                                                           |
| 2025-05-13 00:00:00 | Sell to Close | VIX 07/16/2025 36.00 P |          2 |   16.90 |          2.16 |  3377.84 |              17.72 | nan                                                                                           |
| 2025-04-07 00:00:00 | Buy to Open   | VIX 07/16/2025 45.00 P |          2 |   21.55 |          2.16 |  4312.16 |              46.17 | nan                                                                                           |
| 2025-05-13 00:00:00 | Sell to Close | VIX 07/16/2025 45.00 P |          2 |   25.65 |          2.16 |  5127.84 |              17.96 | nan                                                                                           |
| 2025-04-07 00:00:00 | Buy to Open   | VIX 08/20/2025 45.00 P |          2 |   21.75 |          2.16 |  4352.16 |              49.07 | nan                                                                                           |
| 2025-05-13 00:00:00 | Sell to Close | VIX 08/20/2025 45.00 P |          2 |   25.40 |          2.16 |  5077.84 |              18.06 | nan                                                                                           |
| 2025-06-26 00:00:00 | Buy to Open   | VIX 09/17/2025 20.00 C |         10 |    3.00 |         10.81 |  3010.81 |              16.37 | Opened long dated call position; VIX level at 4th historical decile                           |
| 2025-08-01 00:00:00 | Sell to Close | VIX 09/17/2025 20.00 C |          5 |    3.05 |          5.40 |  1519.60 |              20.48 | Sold half of position due to theta drag, held remaining half for vol spike                    |
| 2025-08-12 00:00:00 | Buy to Open   | VIX 09/17/2025 20.00 C |         10 |    1.54 |          9.31 |  1549.31 |              14.87 | Doubled existing position to reduce cost basis                                                |
| 2025-08-22 00:00:00 | Buy to Open   | VIX 09/17/2025 20.00 C |         15 |    0.88 |         12.01 |  1332.01 |             nan    | nan                                                                                           |
| 2025-08-29 00:00:00 | Sell to Close | VIX 09/17/2025 20.00 C |         15 |    0.80 |         12.01 |  1187.99 |             nan    | nan                                                                                           |
| 2025-09-02 00:00:00 | Sell to Close | VIX 09/17/2025 20.00 C |         15 |    1.33 |         13.96 |  1981.04 |             nan    | nan                                                                                           |
| 2025-08-12 00:00:00 | Buy to Open   | VIX 10/22/2025 19.00 C |         10 |    3.05 |         10.81 |  3060.81 |              15.22 | nan                                                                                           |
| 2025-09-29 00:00:00 | Sell to Close | VIX 10/22/2025 19.00 C |         10 |    1.20 |          9.31 |  1190.69 |             nan    | nan                                                                                           |
| 2025-08-22 00:00:00 | Buy to Open   | VIX 10/22/2025 20.00 C |         10 |    2.12 |         10.81 |  2130.81 |             nan    | nan                                                                                           |
| 2025-09-02 00:00:00 | Sell to Close | VIX 10/22/2025 20.00 C |         10 |    2.65 |         10.81 |  2639.19 |             nan    | nan                                                                                           |
| 2025-07-23 00:00:00 | Buy to Open   | VIX 10/22/2025 21.00 C |         10 |    2.92 |         10.81 |  2930.81 |              15.40 | Continued low volatility, opened long dated call position; VIX level at 4th historical decile |
| 2025-09-29 00:00:00 | Sell to Close | VIX 10/22/2025 21.00 C |         10 |    0.91 |          8.01 |   901.99 |             nan    | nan                                                                                           |
| 2025-06-26 00:00:00 | Buy to Open   | VIX 10/22/2025 22.00 C |         10 |    2.94 |         10.81 |  2950.81 |              16.43 | Opened long dated call position; VIX level at 4th historical decile                           |
| 2025-09-15 00:00:00 | Sell to Close | VIX 10/22/2025 22.00 C |         10 |    1.08 |          9.31 |  1070.69 |             nan    | nan                                                                                           |
| 2025-07-17 00:00:00 | Buy to Open   | VIX 10/22/2025 23.00 C |         10 |    2.75 |         10.81 |  2760.81 |              16.86 | Continued low volatility, opened long dated call position; VIX level at 4th historical decile |
| 2025-09-15 00:00:00 | Sell to Close | VIX 10/22/2025 23.00 C |         10 |    0.98 |          8.01 |   971.99 |             nan    | nan                                                                                           |
| 2025-09-29 00:00:00 | Buy to Open   | VIX 11/19/2025 16.00 C |         10 |    3.65 |         10.81 |  3660.81 |             nan    | nan                                                                                           |
| 2025-10-10 00:00:00 | Sell to Close | VIX 11/19/2025 16.00 C |         10 |    4.80 |         10.81 |  4789.19 |             nan    | nan                                                                                           |
| 2025-08-22 00:00:00 | Buy to Open   | VIX 11/19/2025 19.00 C |         10 |    3.17 |         10.81 |  3180.81 |             nan    | nan                                                                                           |
| 2025-09-02 00:00:00 | Sell to Close | VIX 11/19/2025 19.00 C |         10 |    3.70 |         10.81 |  3689.19 |             nan    | nan                                                                                           |
| 2025-08-13 00:00:00 | Buy to Open   | VIX 11/19/2025 20.00 C |         10 |    3.26 |         10.81 |  3270.81 |              14.56 | VIX at ~0 decile based on the YTD VIX data                                                    |
| 2025-10-09 00:00:00 | Sell to Close | VIX 11/19/2025 20.00 C |         10 |    2.08 |         10.81 |  2069.19 |             nan    | nan                                                                                           |
| 2025-08-12 00:00:00 | Buy to Open   | VIX 11/19/2025 21.00 C |         10 |    3.00 |         10.81 |  3010.81 |              15.17 | nan                                                                                           |
| 2025-10-08 00:00:00 | Sell to Close | VIX 11/19/2025 21.00 C |         10 |    1.83 |          9.31 |  1820.69 |             nan    | nan                                                                                           |
| 2025-09-11 00:00:00 | Buy to Open   | VIX 12/17/2025 17.00 C |         10 |    3.90 |         10.81 |  3910.81 |             nan    | nan                                                                                           |
| 2025-10-10 00:00:00 | Sell to Close | VIX 12/17/2025 17.00 C |         10 |    4.60 |         10.81 |  4589.19 |             nan    | nan                                                                                           |

#### Volatility In August 2024

Plot with VIX high/low, trade side, VIX option, and VIX level at trade date/time:

![VIX Level, Trades](11_VIX_Spike_Trades.png)

Closed positions:

| Symbol                 |   Amount_Buy |   Quantity_Buy |   Amount_Sell |   Quantity_Sell |   Realized_PnL |   Percent_PnL |
|:-----------------------|-------------:|---------------:|--------------:|----------------:|---------------:|--------------:|
| VIX 09/18/2024 34.00 P |      1096.08 |              1 |       1793.92 |               1 |         697.84 |          0.64 |
| VIX 10/16/2024 40.00 P |      1636.08 |              1 |       2152.92 |               1 |         516.84 |          0.32 |
| VIX 11/20/2024 25.00 P |      1182.16 |              2 |       1217.84 |               2 |          35.68 |          0.03 |
| VIX 12/18/2024 30.00 P |      1026.08 |              1 |       1493.92 |               1 |         467.84 |          0.46 |

Open positions:

| Symbol   | Amount_Buy   | Quantity_Buy   |
|----------|--------------|----------------|

Total Opened Position Market Value: $4,940.40</br>
Total Closed Position Market Value: $6,658.60</br>
Net Profit/Loss: $1,718.20</br>
Percent Profit/Loss: 34.78%

#### Volatility In March 2025

Plot with VIX high/low, trade side, VIX option, and VIX level at trade date/time:

![VIX Level, Trades](12_VIX_Spike_Trades.png)

Closed positions:

| Symbol                 |   Amount_Buy |   Quantity_Buy |   Amount_Sell |   Quantity_Sell |   Realized_PnL |   Percent_PnL |
|:-----------------------|-------------:|---------------:|--------------:|----------------:|---------------:|--------------:|
| VIX 04/16/2025 25.00 P |      2830.40 |              5 |       3494.60 |               5 |         664.20 |          0.23 |

Open positions:

| Symbol   | Amount_Buy   | Quantity_Buy   |
|----------|--------------|----------------|

Total Opened Position Market Value: $2,830.40</br>
Total Closed Position Market Value: $3,494.60</br>
Net Profit/Loss: $664.20</br>
Percent Profit/Loss: 23.47%

#### Volatility In April 2025

Plot with VIX high/low, trade side, VIX option, and VIX level at trade date/time:

![VIX Level, Trades](13_VIX_Spike_Trades.png)

Closed positions:

| Symbol                 |   Amount_Buy |   Quantity_Buy |   Amount_Sell |   Quantity_Sell |   Realized_PnL |   Percent_PnL |
|:-----------------------|-------------:|---------------:|--------------:|----------------:|---------------:|--------------:|
| VIX 05/21/2025 26.00 P |      7666.21 |             15 |       5593.79 |              15 |       -2072.42 |         -0.27 |
| VIX 05/21/2025 37.00 P |      3963.24 |              3 |       4121.76 |               3 |         158.52 |          0.04 |
| VIX 05/21/2025 50.00 P |      4232.16 |              2 |       5092.84 |               2 |         860.68 |          0.20 |
| VIX 06/18/2025 27.00 P |      7472.97 |             12 |       8957.02 |              12 |        1484.05 |          0.20 |
| VIX 06/18/2025 36.00 P |      4023.24 |              3 |       4796.76 |               3 |         773.52 |          0.19 |
| VIX 06/18/2025 45.00 P |      3772.16 |              2 |       4997.84 |               2 |        1225.68 |          0.32 |
| VIX 07/16/2025 29.00 P |      4280.40 |              5 |       5174.60 |               5 |         894.20 |          0.21 |
| VIX 07/16/2025 36.00 P |      4143.24 |              3 |       5076.76 |               3 |         933.52 |          0.23 |
| VIX 07/16/2025 45.00 P |      4312.16 |              2 |       5127.84 |               2 |         815.68 |          0.19 |
| VIX 08/20/2025 45.00 P |      4352.16 |              2 |       5077.84 |               2 |         725.68 |          0.17 |

Open positions:

| Symbol   | Amount_Buy   | Quantity_Buy   |
|----------|--------------|----------------|

Total Opened Position Market Value: $48,217.94</br>
Total Closed Position Market Value: $54,017.05</br>
Net Profit/Loss: $5,799.11</br>
Percent Profit/Loss: 12.03%

#### Low Volatility In June, July, August 2025

Plot with VIX high/low, trade side, VIX option, and VIX level at trade date/time:

![VIX Level, Trades](14_VIX_Spike_Trades.png)

Closed positions:

| Symbol                 |   Amount_Buy |   Quantity_Buy |   Amount_Sell |   Quantity_Sell |   Realized_PnL |   Percent_PnL |
|:-----------------------|-------------:|---------------:|--------------:|----------------:|---------------:|--------------:|
| VIX 09/17/2025 20.00 C |      5892.13 |             35 |       4688.63 |              35 |       -1203.50 |         -0.20 |
| VIX 10/22/2025 19.00 C |      3060.81 |             10 |       1190.69 |              10 |       -1870.12 |         -0.61 |
| VIX 10/22/2025 20.00 C |      2130.81 |             10 |       2639.19 |              10 |         508.38 |          0.24 |
| VIX 10/22/2025 21.00 C |      2930.81 |             10 |        901.99 |              10 |       -2028.82 |         -0.69 |
| VIX 10/22/2025 22.00 C |      2950.81 |             10 |       1070.69 |              10 |       -1880.12 |         -0.64 |
| VIX 10/22/2025 23.00 C |      2760.81 |             10 |        971.99 |              10 |       -1788.82 |         -0.65 |
| VIX 11/19/2025 16.00 C |      3660.81 |             10 |       4789.19 |              10 |        1128.38 |          0.31 |
| VIX 11/19/2025 19.00 C |      3180.81 |             10 |       3689.19 |              10 |         508.38 |          0.16 |
| VIX 11/19/2025 20.00 C |      3270.81 |             10 |       2069.19 |              10 |       -1201.62 |         -0.37 |
| VIX 11/19/2025 21.00 C |      3010.81 |             10 |       1820.69 |              10 |       -1190.12 |         -0.40 |
| VIX 12/17/2025 17.00 C |      3910.81 |             10 |       4589.19 |              10 |         678.38 |          0.17 |

Open positions:

| Symbol   | Amount_Buy   | Quantity_Buy   |
|----------|--------------|----------------|

Total Opened Position Market Value: $36,760.23</br>
Total Closed Position Market Value: $28,420.63</br>
Net Profit/Loss: $-8,339.60</br>
Percent Profit/Loss: -22.69%

#### Complete Trade History (Closed Positions)

Total Opened Position Market Value: $92,748.97</br>
Total Closed Position Market Value: $92,590.88</br>
Net Profit/Loss: $-158.09</br>
Percent Profit/Loss: -0.17%

## References

1. https://www.cboe.com/tradable_products/vix/
2. https://github.com/ranaroussi/yfinance

## Code

Note: The files below are identical to those linked in [part 1](/2025/03/01/investigating-a-vix-trading-signal-part-1-vix-and-vvix/#code) and [part 2](/2025/03/02/investigating-a-vix-trading-signal-part-2-finding-a-signal/#code).

The jupyter notebook with the functions and all other code is available [here](investigating-a-vix-trading-signal-part-3-trading.ipynb).</br>
The html export of the jupyter notebook is available [here](investigating-a-vix-trading-signal-part-3-trading.html).</br>
The pdf export of the jupyter notebook is available [here](investigating-a-vix-trading-signal-part-3-trading.pdf).