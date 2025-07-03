---
title: Cleaning A Bloomberg Data Excel Export
description: A python function to clean and format an excel data export from Bloomberg.
slug: cleaning-bloomberg-excel-export
date: 2023-11-15 00:00:01+0000
lastmod: 2023-12-26 00:00:00+0000
image: cover.jpg
draft: false
categories:
    - Bloomberg
    - Pandas
    - Python
# tags:
#     - Python
#     - Bloomberg
#     - pandas
#     - OpenPyXL
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

## Introduction

In this tutorial, we will write a python function that imports an excel export from Bloomberg, removes ancillary rows and columns, and leaves the data in a format where it can then be used in time series analysis.

## Example of a Bloomberg excel export

We will use the SPX index data in this example. Exporting the data from Bloomberg using the excel Bloomberg add-on yields data in the following format:

![Format of data in excel export from Bloomberg](Format_of_data_in_excel_export_from_Bloomberg.png)

## Data modifications

The above format isn't horrible, but we want to perform the following modifications:

1. Remove the first six rows of the data
2. Convert the 7th row to become column headings
3. Rename column 2 to "Close" to represent the closing price
4. Remove column 3, as we are not concerned about volume
5. Export to excel and make the name of the excel worksheet "data"

## Assumptions

The remainder of this tutorial assumes the following:

* Your excel file is named "SPX_Index.xlsx"
* The worksheet in the excel file is named "Worksheet"
* You have the [pandas](https://pandas.pydata.org/) library installed
* You have the [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/) library installed

## Python function to modify the data

The following function will perform the modifications mentioned above:

```python
# This function takes an excel export from Bloomberg and 
# removes all excess data leaving date and close columns

# Imports
import pandas as pd

# Function definition
def bb_data_updater(fund):

    # File name variable
    file = fund + "_Index.xlsx"
    
    # Import data from file as a pandas dataframe
    df = pd.read_excel(file, sheet_name = 'Worksheet', engine='openpyxl')
    
    # Set the column headings from row 5 (which is physically row 6)
    df.columns = df.iloc[5]
    
    # Set the column heading for the index to be "None"
    df.rename_axis(None, axis=1, inplace = True)
    
    # Drop the first 6 rows, 0 - 5
    df.drop(df.index[0:6], inplace=True)
    
    # Set the date column as the index
    df.set_index('Date', inplace = True)
    
    # Drop the volume column
    try:
        df.drop(columns = {'PX_VOLUME'}, inplace = True)
    except KeyError:
        pass
        
    # Rename column
    df.rename(columns = {'PX_LAST':'Close'}, inplace = True)
    
    # Sort by date
    df.sort_values(by=['Date'], inplace = True)
    
    # Export data to excel
    file = fund + ".xlsx"
    df.to_excel(file, sheet_name='data')
    
    # Output confirmation
    print(f"The last date of data for {fund} is: ")
    print(df[-1:])
    print(f"Bloomberg data conversion complete for {fund} data")
    return print(f"--------------------")
```

Let's break this down line by line.

## Imports

First, we need to import pandas:

```python
import pandas as pd
```

## Import excel data file

Then import the excel file as a pandas dataframe:

```python
# File name variable
file = fund + "_Index.xlsx"

# Import data from file as a pandas dataframe
df = pd.read_excel(file, sheet_name = 'Worksheet', engine='openpyxl')
```

Running:

    df.head(10)

Gives us:

![Dataframe excel import](Dataframe_excel_import.png)

## Set column headings

Next, set the column heading:

```python
# Set the column headings from row 5 (which is physically row 6)
df.columns = df.iloc[5]
```

Now, running:

    df.head(10)

Gives us:

![Set column headings](Set_column_headings.png)

## Remove index heading

Next, remove the column heading from the index column:

```python
# Set the column heading for the index to be "None"
df.rename_axis(None, axis=1, inplace = True)
```

Note: The `axis=1` argument here specifies the column index.

Now, running:

    df.head(10)

Gives us:

![Remove index heading](Remove_index_heading.png)

## Drop rows

Next, we want to remove the first 6 rows that have unneeded data:

```python
# Drop the first 6 rows, 0 - 5
df.drop(df.index[0:6], inplace=True)
```

Note: When dropping rows, the range to drop begins with row 0 and continues up to - but not including - row 6.

Now, running:

    df.head(10)

Gives us:

![Remove rows](Remove_rows.png)

## Set index

Next, we want to set the date column as the index:

```python
# Set the date column as the index
df.set_index('Date', inplace = True)
```

Now, running:

    df.head(10)

Gives us:

![Set index](Set_index.png)

## Drop the "PX_VOLUME" column

Next, we want to drop the volume column:

```python
# Drop the volume column
try:
    df.drop(columns = {'PX_VOLUME'}, inplace = True)
except KeyError:
    pass
```

For some data records, the volume column does not exist. Therefore, we `try`, and if it fails with a `KeyError`, then we assume the "PX_VOLUME" column does not exist, and just `pass` to move on.

Now, running:

    df.head(10)

Gives us:

![Drop volume](Drop_volume.png)

## Rename the "PX_LAST" column

Next, we want to rename the "PX_LAST" column as "Close":

```python
# Rename column
df.rename(columns = {'PX_LAST':'Close'}, inplace = True)
```

Now, running:

    df.head(10)

Gives us:

![Rename column](Rename_column.png)

## Sort data

Next, we want to sort the data starting with the oldest date:

```python
# Sort by date
df.sort_values(by=['Date'], inplace = True)
```

Now, running:

    df.head(10)

Gives us:

![Sort by date](Sort_by_date.png)

## Export data

Next, we want to export the data to an excel file, for easy viewing and reference later:

```python
# Export data to excel
file = fund + ".xlsx"
df.to_excel(file, sheet_name='data')
```

And verify the output is as expected:

![Excel export](Excel_export.png)

## Output confirmation

Finally, we want to print a confirmation that the process succeeded along withe last date we have for data:

```python
# Output confirmation
print(f"The last date of data for {fund} is: ")
print(df[-1:])
print(f"Bloomberg data conversion complete for {fund} data")
print(f"--------------------")
```

And confirming the output:

![Output confirmation](Output_confirmation.png)

## References

https://www.bloomberg.com/professional/support/software-updates/