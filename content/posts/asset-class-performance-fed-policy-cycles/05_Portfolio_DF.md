```text
The columns, shape, and data types are:

<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 252 entries, 2004-11-30 to 2025-10-31
Freq: ME
Data columns (total 9 columns):
 #   Column                       Non-Null Count  Dtype  
---  ------                       --------------  -----  
 0   Portfolio_Monthly_Return     251 non-null    float64
 1   Portfolio_Cumulative_Return  251 non-null    float64
 2   Portfolio_Drawdown           251 non-null    float64
 3   SPY_Monthly_Return           251 non-null    float64
 4   SPY_Cumulative_Return        251 non-null    float64
 5   SPY_Drawdown                 251 non-null    float64
 6   TLT_Monthly_Return           251 non-null    float64
 7   TLT_Cumulative_Return        251 non-null    float64
 8   TLT_Drawdown                 251 non-null    float64
dtypes: float64(9)
memory usage: 19.7 KB

```

The first 5 rows are:

| Date                |   Portfolio_Monthly_Return |   Portfolio_Cumulative_Return |   Portfolio_Drawdown |   SPY_Monthly_Return |   SPY_Cumulative_Return |   SPY_Drawdown |   TLT_Monthly_Return |   TLT_Cumulative_Return |   TLT_Drawdown |
|:--------------------|---------------------------:|------------------------------:|---------------------:|---------------------:|------------------------:|---------------:|---------------------:|------------------------:|---------------:|
| 2004-11-30 00:00:00 |                    nan     |                       nan     |              nan     |              nan     |                 nan     |        nan     |              nan     |                 nan     |        nan     |
| 2004-12-31 00:00:00 |                      0.030 |                         0.030 |                0.000 |                0.030 |                   0.030 |          0.000 |                0.027 |                   0.027 |          0.000 |
| 2005-01-31 00:00:00 |                     -0.022 |                         0.007 |               -0.022 |               -0.022 |                   0.007 |         -0.022 |                0.036 |                   0.063 |          0.000 |
| 2005-02-28 00:00:00 |                      0.021 |                         0.028 |               -0.002 |                0.021 |                   0.028 |         -0.002 |               -0.015 |                   0.048 |         -0.015 |
| 2005-03-31 00:00:00 |                     -0.018 |                         0.009 |               -0.020 |               -0.018 |                   0.009 |         -0.020 |               -0.005 |                   0.043 |         -0.019 |

The last 5 rows are:

| Date                |   Portfolio_Monthly_Return |   Portfolio_Cumulative_Return |   Portfolio_Drawdown |   SPY_Monthly_Return |   SPY_Cumulative_Return |   SPY_Drawdown |   TLT_Monthly_Return |   TLT_Cumulative_Return |   TLT_Drawdown |
|:--------------------|---------------------------:|------------------------------:|---------------------:|---------------------:|------------------------:|---------------:|---------------------:|------------------------:|---------------:|
| 2025-06-30 00:00:00 |                      0.027 |                        19.004 |               -0.072 |                0.051 |                   6.718 |          0.000 |                0.027 |                   0.963 |         -0.408 |
| 2025-07-31 00:00:00 |                     -0.011 |                        18.776 |               -0.082 |                0.023 |                   6.896 |          0.000 |               -0.011 |                   0.941 |         -0.415 |
| 2025-08-31 00:00:00 |                      0.000 |                        18.778 |               -0.082 |                0.021 |                   7.058 |          0.000 |                0.000 |                   0.941 |         -0.415 |
| 2025-09-30 00:00:00 |                      0.036 |                        19.489 |               -0.049 |                0.036 |                   7.345 |          0.000 |                0.036 |                   1.011 |         -0.394 |
| 2025-10-31 00:00:00 |                      0.014 |                        19.772 |               -0.036 |                0.024 |                   7.544 |          0.000 |                0.014 |                   1.039 |         -0.385 |