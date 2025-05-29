---
title: Reusable And Extensible Python Functions For Financial Data Analysis
description: A list of common functions used for data acquisition, cleaning, analysis, etc.
slug: reusable-extensible-python-functions-financial-data-analysis
date: 2025-02-02 00:00:01+0000
lastmod: 2025-05-28 00:00:01+0000
image: cover.jpg
draft: false
categories:
    - Tutorials
    - Tech
tags:
    - Bloomberg
    - Nasdaq Data Link
    - pandas
    - Python
    - Yahoo Finance
# weight: 1       # You can add weight to some posts to override the default sorting (date descending)
---

<!-- ## Post Updates

Update 4/8/2025: Added plot for signals for each year. VIX data through 4/7/25.</br>
Update 4/9/2025: VIX data through 4/8/25.</br>
Update 4/12/2025: VIX data through 4/10/25.</br>
Update 4/22/2025: VIX data through 4/18/25.</br>
Update 4/23/2025: VIX data through 4/22/25.</br>
Update 4/25/2025: VIX data through 4/23/25. Added section for trade history, including open and closed positions.</br>
Update 4/28/2025: VIX data through 4/25/25.</br>
Update 5/6/2025: Data through 5/5/25. Added section for the VVIX.</br>
Update 5/7/2025: Data through 5/6/25.</br>
Update 5/21/2025: Data through 5/20/25.</br> -->

## Introduction

This post intends to provide the code for all of the python functions that I use in my analysis. The goal here is that when writing another post I will simply be able to link to the functions below as opposed to providing the function code in each post.

## Function Index

[bb_clean_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#bb_clean_data): Takes an Excel export from Bloomberg, removes the miscellaneous headings/rows, and returns a DataFrame.</br>
[build_index](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#build_index): Reads the `index_temp.md` markdown file, inserts the markdown dependencies where indicated, and then saves the file as `index.md`.</br>
[calc_vix_trade_pnl](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#calc_vix_trade_pnl): Calculates the profit/loss from VIX options trades.</br>
[df_info](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#df_info): A simple function to display the information about a DataFrame and the first five rows and last five rows.</br>
[df_info_markdown](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#df_info_markdown): Similar to the `df_info` function above, except that it coverts the output to markdown.</br>
[export_track_md_deps](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#export_track_md_deps): Exports various text outputs to markdown files, which are included in the `index.md` file created when building the site with Hugo.</br>
[load_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.</br>
[pandas_set_decimal_places](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.</br>
[plot_price](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#plot_price): Plot the price data from a DataFrame for a specified date range and columns.</br>
[plot_vix_with_trades](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#plot_vix_with_trades): Plot the VIX daily high and low prices, along with the VIX spikes, and trades.</br>
[yf_pull_data](/2025/02/02/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.

## Python Functions

### bb_clean_data

<!-- INSERT_bb_clean_data_HERE -->

### build_index

<!-- INSERT_build_index_HERE -->

### calc_vix_trade_pnl

<!-- INSERT_calc_vix_trade_pnl_HERE -->

### df_info

<!-- INSERT_df_info_HERE -->

### df_info_markdown

<!-- INSERT_df_info_markdown_HERE -->

### export_track_md_deps

<!-- INSERT_export_track_md_deps_HERE -->

### load_api_keys

<!-- INSERT_load_api_keys_HERE -->

### load_data

<!-- INSERT_load_data_HERE -->

### pandas_set_decimal_places

<!-- INSERT_pandas_set_decimal_places_HERE -->

### plot_price

<!-- INSERT_plot_price_HERE -->

### plot_vix_with_trades

<!-- INSERT_plot_vix_with_trades_HERE -->

### yf_pull_data

<!-- INSERT_yf_pull_data_HERE -->

## References

None

## Code

The jupyter notebook with the functions and all other code is available [here](reusable-extensible-python-functions-financial-data-analysis.ipynb).</br>
The html export of the jupyter notebook is available [here](reusable-extensible-python-functions-financial-data-analysis.html).</br>
The pdf export of the jupyter notebook is available [here](reusable-extensible-python-functions-financial-data-analysis.pdf).