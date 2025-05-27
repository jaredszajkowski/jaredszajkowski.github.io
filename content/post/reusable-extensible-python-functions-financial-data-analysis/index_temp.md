---
title: Reusable And Extensible Python Functions For Financial Data Analysis
description: A list of common functions used for data acquisition, cleaning, analysis, etc.
slug: reusable-extensible-python-functions-financial-data-analysis
date: 2025-02-02 00:00:01+0000
lastmod: 2025-05-26 00:00:01+0000
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

### Functions For Assembling/Processing Posts

[build_index](#build_index): Reads the `index_temp.md` markdown file and inserts the markdown dependencies where indicated.</br>
[export_track_md_deps](#export_track_md_deps): exports various text outputs to markdown files, which are included in the index.md file created when building the site with Hugo.

### Bloomberg Functions

[bb_clean_data](#bb_clean_data): Takes an Excel export from Bloomberg, removes the miscellaneous headings/rows, and returns a DataFrame.

### Analysis Functions

[calc_vix_trade_pnl](#calc_vix_trade_pnl): Calculates the profit/loss from VIX options trades.

## Python Functions

### bb_clean_data

<!-- INSERT_bb_clean_data_HERE -->

### build_index

<!-- INSERT_build_index_HERE -->

### calc_vix_trade_pnl

<!-- INSERT_calc_vix_trade_pnl_HERE -->

### export_track_md_deps

<!-- INSERT_export_track_md_deps_HERE -->

## References

None

## Code

The jupyter notebook with the functions and all other code is available [here](reusable-extensible-python-functions-financial-data-analysis.ipynb).</br>
The html export of the jupyter notebook is available [here](reusable-extensible-python-functions-financial-data-analysis.html).</br>
The pdf export of the jupyter notebook is available [here](reusable-extensible-python-functions-financial-data-analysis.pdf).