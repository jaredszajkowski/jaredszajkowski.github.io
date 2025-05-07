```text
The columns, shape, and data types are:

<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 8479 entries, 1990-01-02 to 2023-12-29
Data columns (total 4 columns):
 #   Column        Non-Null Count  Dtype  
---  ------        --------------  -----  
 0   Stocks_Close  8479 non-null   float64
 1   Bonds_Close   8479 non-null   float64
 2   Gold_Close    8479 non-null   float64
 3   Cash_Close    8479 non-null   int64  
dtypes: float64(3), int64(1)
memory usage: 331.2 KB

```

The first 5 rows are:

| Date                |   Stocks_Close |   Bonds_Close |   Gold_Close |   Cash_Close |
|:--------------------|---------------:|--------------:|-------------:|-------------:|
| 1990-01-02 00:00:00 |         386.16 |         99.97 |       399.00 |         1.00 |
| 1990-01-03 00:00:00 |         385.17 |         99.73 |       395.00 |         1.00 |
| 1990-01-04 00:00:00 |         382.02 |         99.81 |       396.50 |         1.00 |
| 1990-01-05 00:00:00 |         378.30 |         99.77 |       405.00 |         1.00 |
| 1990-01-08 00:00:00 |         380.04 |         99.68 |       404.60 |         1.00 |

The last 5 rows are:

| Date                |   Stocks_Close |   Bonds_Close |   Gold_Close |   Cash_Close |
|:--------------------|---------------:|--------------:|-------------:|-------------:|
| 2023-12-22 00:00:00 |       10292.37 |        604.17 |      2053.08 |         1.00 |
| 2023-12-26 00:00:00 |       10335.98 |        604.55 |      2067.81 |         1.00 |
| 2023-12-27 00:00:00 |       10351.60 |        609.36 |      2077.49 |         1.00 |
| 2023-12-28 00:00:00 |       10356.59 |        606.83 |      2065.61 |         1.00 |
| 2023-12-29 00:00:00 |       10327.83 |        606.18 |      2062.98 |         1.00 |