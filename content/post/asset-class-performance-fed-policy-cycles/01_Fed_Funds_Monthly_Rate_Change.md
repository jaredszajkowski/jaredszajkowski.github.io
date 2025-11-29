```text
The columns, shape, and data types are:

<class 'pandas.core.frame.DataFrame'>
DatetimeIndex: 252 entries, 2004-11-30 to 2025-10-31
Freq: ME
Data columns (total 2 columns):
 #   Column           Non-Null Count  Dtype  
---  ------           --------------  -----  
 0   FEDFUNDS         252 non-null    float64
 1   FedFunds_Change  251 non-null    float64
dtypes: float64(2)
memory usage: 5.9 KB

```

The first 5 rows are:

| DATE                |   FEDFUNDS |   FedFunds_Change |
|:--------------------|-----------:|------------------:|
| 2004-11-30 00:00:00 |     0.0193 |          nan      |
| 2004-12-31 00:00:00 |     0.0216 |            0.0023 |
| 2005-01-31 00:00:00 |     0.0228 |            0.0012 |
| 2005-02-28 00:00:00 |     0.0250 |            0.0022 |
| 2005-03-31 00:00:00 |     0.0263 |            0.0013 |

The last 5 rows are:

| DATE                |   FEDFUNDS |   FedFunds_Change |
|:--------------------|-----------:|------------------:|
| 2025-06-30 00:00:00 |     0.0433 |            0.0000 |
| 2025-07-31 00:00:00 |     0.0433 |            0.0000 |
| 2025-08-31 00:00:00 |     0.0433 |            0.0000 |
| 2025-09-30 00:00:00 |     0.0422 |           -0.0011 |
| 2025-10-31 00:00:00 |     0.0409 |           -0.0013 |