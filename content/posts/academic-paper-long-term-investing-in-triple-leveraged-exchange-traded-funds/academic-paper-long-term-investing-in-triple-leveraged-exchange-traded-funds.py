# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Introduction

# %% [markdown]
# In late 2025, I ran across a paper by Lewis Glenn entitled "Long-Term Investing in Triple Leveraged Exchange Traded Funds." The paper explores the performance and risks associated with holding triple leveraged ETFs over extended periods, and proposes an investment strategy involving rebalancing two triple leveraged ETFs (abbreviated "TLETFs") on a bimonthly schedule. From the abstract:
#
# > "The phrase long-term investing in triple leveraged ETFs is somewhat of an anathema for investment academicians. As a result of daily rebalancing and so-called beta slippage or “the constant leverage trap” it is highly likely over the long term to significantly deviate from the targeted leverage and, in so doing, generate wipeout losses. In fact, the data show that many 3X leveraged ETFs have performed poorly over the long term in the period of their existence. However, there are some significant exceptions. The 3X leveraged Nasdaq ETF, TQQQ, for example has delivered a total return exceeding 10,000% (CAGR of 54.4%) over the 10+ years of its existence, more than 13 times the total return of its underlying ETF (QQQ). Similar, but less impressive numbers have been achieved with triple leveraged ETFs that target the S&P 500 and the Dow Industrials."
# >
# > "These results, however, are accompanied by excessive volatility and very large maximum end-of-month (EOM) draw downs, in excess of 49% for TQQQ, and with maximum daily drawdown of almost 70%. Many retail investors would be unwilling to sustain such (paper) losses. Here we propose a strategy to mitigate these large draw downs while still retaining much of the upside performance of triple leveraging. We show that by simply establishing a portfolio consisting of an equal dollar amount of TQQQ and TMF (the triple leveraged ETF linked to the 20+ year treasury bond), and performing bimonthly rebalancing, a total return, after transaction costs, in excess of 5,800% (CAGR of 44.9%) would have been achieved over the 10+ years of TQQQ existence, with the maximum EOM draw down less than 25%."
#
# The paper was published (or dated, at least) November 7, 2020. In this piece, we will attempt to reproduce the results of the investment strategy presented in the paper section by section, and examine whether the impressive performance in sample has continued.
#
# A note on the numbering of figures and tables: figures that reproduce a figure from the paper use the same number as the paper (for example, Figure 1), with a letter added when we split one of the paper's figures into several plots (for example, Figures 9a, 9b, and 9c). Figure 10 from the paper is reproduced as a table. Figure 6 is omitted due to data limitations, and figure 11 (a pseudo-code diagram) is discussed but not reproduced. All figures and tables that do not appear in the paper are numbered with an "E" prefix (for example, Figure E1 and Table E1).

# %% [markdown]
# ## Python Imports

# %%
# Standard Library
import os
import sys
import warnings

from pathlib import Path

# Data Handling
import pandas as pd

# Suppress warnings
warnings.filterwarnings("ignore")

# %%
# Add the source subdirectory to the system path to allow import config from settings.py
current_directory = Path(os.getcwd())
website_base_directory = current_directory.parent.parent.parent
src_directory = website_base_directory / "src"
sys.path.append(str(src_directory)) if str(src_directory) not in sys.path else None

# Import settings.py
from settings import config

# Add configured directories from config to path
SOURCE_DIR = config("SOURCE_DIR")
(
    sys.path.append(str(Path(SOURCE_DIR)))
    if str(Path(SOURCE_DIR)) not in sys.path
    else None
)

# Add other configured directories
BASE_DIR = config("BASE_DIR")
CONTENT_DIR = config("CONTENT_DIR")
POSTS_DIR = config("POSTS_DIR")
PAGES_DIR = config("PAGES_DIR")
PUBLIC_DIR = config("PUBLIC_DIR")
SOURCE_DIR = config("SOURCE_DIR")
DATA_DIR = config("DATA_DIR")
DATA_MANUAL_DIR = config("DATA_MANUAL_DIR")

# %% [markdown]
# ## Python Functions

# %% [markdown]
# Here are the functions needed for this project:
#
# * [load_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#load_data): Load data from a CSV, Excel, or Pickle file into a pandas DataFrame.
# * [pandas_set_decimal_places](/posts/reusable-extensible-python-functions-financial-data-analysis/#pandas_set_decimal_places): Set the number of decimal places displayed for floating-point numbers in pandas.
# * [plot_time_series](/posts/reusable-extensible-python-functions-financial-data-analysis/#plot_time_series): Plot the timeseries data from a DataFrame for a specified date range and columns.
# * [run_regression](/posts/reusable-extensible-python-functions-financial-data-analysis/#run_regression): Run a linear regression using statsmodels OLS and return the results.
# * [summary_stats](/posts/reusable-extensible-python-functions-financial-data-analysis/#summary_stats): Generate summary statistics for a series of returns.
# * [yf_pull_data](/posts/reusable-extensible-python-functions-financial-data-analysis/#yf_pull_data): Download daily price data from Yahoo Finance and export it.

# %%
from load_data import load_data
from pandas_set_decimal_places import pandas_set_decimal_places
from plot_time_series import plot_time_series
from run_regression import run_regression
from summary_stats import summary_stats
from yf_pull_data import yf_pull_data

# %% [markdown]
# ## Data Overview

# %% [markdown]
# For this exercise, we will use the following ETFs:
#
# * TQQQ - ProShares UltraPro QQQ
# * QQQ - Invesco QQQ Trust
# * UPRO - ProShares UltraPro S&P 500
# * SPY - SPDR S&P 500 ETF Trust
# * UDOW - ProShares UltraPro Dow30
# * DIA - SPDR Dow Jones Industrial Average ETF Trust
# * TNA - Direxion Daily Small Cap Bull 3X Shares
# * IWM - iShares Russell 2000 ETF
# * TMF - Direxion Daily 20+ Year Treasury Bull 3X Shares
# * TLT - iShares 20+ Year Treasury Bond ETF
# * EDC - Direxion Daily MSCI Emerging Markets Bull 3X Shares
# * EEM - iShares MSCI Emerging Markets ETF
# * IEF - iShares 7-10 Year Treasury Bond ETF (used for the "black swan" filter in section 3.2)
# * AGG - iShares Core U.S. Aggregate Bond ETF (used in extension 3)
#
# We'll use the adjusted close prices for each of these ETFs.
#
# The paper also used the following funds:
#
# * DZK - Direxion Daily MSCI Developed Markets Bull 3X Shares
# * EFA - iShares MSCI EAFE ETF
#
# But we will omit these due to DZK being delisted.

# %% [markdown]
# ## Acquire Data

# %% [markdown]
# First, let's get the data for these ETFs. If we already have the desired data, we can load it from a local pickle file. Otherwise, we can download it from Yahoo Finance using the `yf_pull_data` function.

# %%
pandas_set_decimal_places(2)

# Create a list of the ETF tickers
fund_list = [
    "TQQQ",
    "QQQ",
    "UPRO",
    "SPY",
    "UDOW",
    "DIA",
    "TNA",
    "IWM",
    "TMF",
    "TLT",
    "EDC",
    "EEM",
]

# %%
# Pull data for each ETF and cache it locally
for fund in fund_list:
    yf_pull_data(
        base_directory=DATA_DIR,
        ticker=fund,
        adjusted=False,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        excel_export=True,
        pickle_export=True,
        output_confirmation=False,
    )

# %% [markdown]
# ## Create Data Dictionary

# %% [markdown]
# Then, create a dictionary to hold the data for each ETF.

# %%
# Create an empty dictionary to hold the data for each ETF
fund_data = {}

# Load the data for each ETF, rename the columns to include the ticker, store it in the fund_data dictionary
for fund in fund_list:
    data = load_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        timeframe="Daily",
        file_format="pickle",
    )

    data = data.rename(
        columns={
            "Adj Close": f"{fund}_Adj_Close",
            "Close": f"{fund}_Close",
            "High": f"{fund}_High",
            "Low": f"{fund}_Low",
            "Open": f"{fund}_Open",
            "Volume": f"{fund}_Volume",
        }
    )

    fund_data[fund] = data


# %% [markdown]
# ## Section 2.0: Long-term Empirical behavior of Triple Leveraged Exchange Traded Funds

# %% [markdown]
# Section 2.0 of the paper establishes some baseline definitions, specifically CAGR (referenced in the paper as cumulative annualized growth rate, but more commonly as compound annual growth rate), DDD (daily drawdown, daily and maximum), and MDD (monthly drawdown, monthly and maximum).
#
# The following two helper functions will combine and normalize the fund prices, and calculate the summary statistics.


# %%
def combine_normalize(
    fund_data: dict,
    lev_etf: str,
    etf: str,
    start_date=None,
    end_date=None,
) -> pd.DataFrame:
    """
    Combine and normalize the data for a leveraged ETF and its corresponding non-leveraged ETF.

    Parameters
    ----------
    fund_data : dict
        Dictionary containing DataFrames for each fund.
    lev_etf : str
        The ticker symbol for the leveraged ETF.
    etf : str
        The ticker symbol for the non-leveraged ETF.
    start_date : optional,
        Start date for the data. If None, uses the earliest available date (default is None).
    end_date : optional
        End date for the data. If None, uses the latest available date (default is None).

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized values for both ETFs.
    """

    # Combine into a single DataFrame
    df = fund_data[lev_etf].merge(fund_data[etf], left_index=True, right_index=True)

    # Normalize values to start at 1
    df = df / df.iloc[0]

    # Set start and end dates
    if start_date is None:
        start_date = df.index.min()
    if end_date is None:
        end_date = df.index.max()

    df = df.loc[start_date:end_date]

    return df


# %%
def calculate_returns_stats(
    df: pd.DataFrame,
    lev_etf: str,
    etf: str,
    max_per_ratio_date=None,
) -> pd.DataFrame:
    """
    Calculate and display summary statistics for the returns of a leveraged ETF and its corresponding non-leveraged ETF.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the adjusted close prices of the ETFs.
    lev_etf : str
        Ticker symbol of the leveraged ETF.
    etf : str
        Ticker symbol of the non-leveraged ETF.
    max_per_ratio_date : optional
        Date of the maximum performance ratio. If provided, the CAGR is calculated through this date, while
        all other statistics use the full date range. If None, the CAGR uses the full date range (default is None).

    Returns
    -------
    pd.DataFrame
        DataFrame containing the summary statistics for both ETFs, including the maximum monthly drawdown
        calculated from end-of-month prices only.
    """

    df[f"{lev_etf}_Return"] = df[f"{lev_etf}_Adj_Close"].pct_change()
    df[f"{etf}_Return"] = df[f"{etf}_Adj_Close"].pct_change()

    # Create empty DataFrame for summary statistics
    sum_stats = pd.DataFrame()

    df_lev_stats = summary_stats(
        fund_list=[f"{lev_etf}"],
        df=df[[f"{lev_etf}_Return"]].dropna(),
        period="Daily",
        use_calendar_days=False,
        excel_export=False,
        pickle_export=False,
        output_confirmation=False,
    )

    sum_stats = pd.concat([sum_stats, df_lev_stats])

    df_etf_stats = summary_stats(
        fund_list=[f"{etf}"],
        df=df[[f"{etf}_Return"]].dropna(),
        period="Daily",
        use_calendar_days=False,
        excel_export=False,
        pickle_export=False,
        output_confirmation=False,
    )

    sum_stats = pd.concat([sum_stats, df_etf_stats])

    # Replace the CAGR with the CAGR through the maximum performance ratio date, if provided
    if max_per_ratio_date is not None:
        for fund in [lev_etf, etf]:
            df_cagr_stats = summary_stats(
                fund_list=[f"{fund}"],
                df=df.loc[:max_per_ratio_date, [f"{fund}_Return"]].dropna(),
                period="Daily",
                use_calendar_days=False,
                excel_export=False,
                pickle_export=False,
                output_confirmation=False,
            )

            sum_stats.loc[f"{fund}_Return", "CAGR (Geometric)"] = df_cagr_stats.loc[
                f"{fund}_Return", "CAGR (Geometric)"
            ]

    # Record the end date used for the CAGR
    sum_stats["CAGR End Date"] = (
        max_per_ratio_date
        if max_per_ratio_date is not None
        else df.index.max().strftime("%Y-%m-%d")
    )

    # Calculate the maximum monthly drawdown using end-of-month prices only
    for fund in [lev_etf, etf]:
        month_end_prices = df[f"{fund}_Adj_Close"].resample("ME").last()
        sum_stats.loc[f"{fund}_Return", "Max Monthly Drawdown"] = (
            month_end_prices / month_end_prices.cummax() - 1
        ).min()

    return sum_stats


# %% [markdown]
# ### Figure 1: Comparing the normalized value of TQQQ with its underlying index

# %% [markdown]
# First, we will plot TQQQ and QQQ to match figure 1. Note that the data from the paper is normalized to begin at 1, so we will follow that approach as well.

# %%
lev_etf = "TQQQ"
etf = "QQQ"
end_date = "2020-10-04"

df = combine_normalize(
    fund_data=fund_data,
    lev_etf=lev_etf,
    etf=etf,
    start_date=None,
    end_date=end_date,
)

print(f"Table E1: {lev_etf} & {etf} Normalized Data")
display(df)

# %%
# Create one empty dataframe for all summary statistics
all_sum_stats = pd.DataFrame()

# %%
max_per_ratio_date = "2020-09-02"

sum_stats = calculate_returns_stats(
    df=df,
    lev_etf=lev_etf,
    etf=etf,
    max_per_ratio_date=max_per_ratio_date,
)

all_sum_stats = pd.concat([all_sum_stats, sum_stats])

print("Table E2: Leveraged and Non-Leveraged ETF Summary Statistics")
display(all_sum_stats)

# %% [markdown]
# The paper lists a CAGR of 54.4% for TQQQ and 21.2% for QQQ. We find nearly the same values in our calculations, as can be seen above at 55% and 21%.
#
# For the DDD, the paper finds a maximum DDD of 69.2%, and we find 70%. For the MDD, the paper finds a maximum MDD of 49.1%, and we find 49%.
#
# Note that the paper calculates the CAGR and the drawdowns over different date ranges. The CAGR is calculated through the date of the maximum performance ratio, which is the normalized value of the leveraged ETF divided by the normalized value of its underlying ETF. For TQQQ and QQQ, the paper finds a maximum performance ratio of 13.1 (101.12/7.73) on 9/2/2020. The DDD and MDD, on the other hand, are calculated over the full period shown in the plots, which ends on 10/4/2020. We follow the same approach, calculating the CAGR through the maximum performance ratio date and all other statistics through 10/4/2020.
#
# Any slight differences can likely be attributed to our use of 252 trading days per year, vs the paper's use of 250 trading days per year.

# %%
plot_time_series(
    df=df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{lev_etf}_Adj_Close", f"{etf}_Adj_Close"],
    title=f"Figure 1: {lev_etf} & {etf} Adjusted Close Price (Normalized) as of {end_date}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# ### Figure 2: Comparing the normalized value of UPRO with its underlying index

# %% [markdown]
# Next, UPRO and SPY.

# %%
lev_etf = "UPRO"
etf = "SPY"
end_date = "2020-10-04"

df = combine_normalize(
    fund_data=fund_data,
    lev_etf=lev_etf,
    etf=etf,
    start_date=None,
    end_date=end_date,
)

print(f"Table E3: {lev_etf} & {etf} Normalized Data")
display(df)

# %%
max_per_ratio_date = "2020-02-19"

sum_stats = calculate_returns_stats(
    df=df,
    lev_etf=lev_etf,
    etf=etf,
    max_per_ratio_date=max_per_ratio_date,
)

all_sum_stats = pd.concat([all_sum_stats, sum_stats])

print("Table E4: Leveraged and Non-Leveraged ETF Summary Statistics")
display(all_sum_stats)

# %% [markdown]
# For UPRO and SPY, the paper finds a maximum performance ratio of 7.5 (34.13/4.53) on 2/19/2020, and lists a CAGR through that date of 39.0% for UPRO and 15.1% for SPY. We find 39% for UPRO and 15% for SPY. For the DDD, the paper finds a maximum DDD of 78.8% for UPRO, and we find 77%, so very close there. The paper's maximum MDD for UPRO is 60.4%, which matches our 60%.

# %%
plot_time_series(
    df=df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{lev_etf}_Adj_Close", f"{etf}_Adj_Close"],
    title=f"Figure 2: {lev_etf} & {etf} Adjusted Close Price (Normalized) as of {end_date}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# ### Figure 3: Comparing the normalized value of UDOW with its underlying index

# %% [markdown]
# Next, figure #3 plots UDOW and DIA.

# %%
lev_etf = "UDOW"
etf = "DIA"
end_date = "2020-10-04"

df = combine_normalize(
    fund_data=fund_data,
    lev_etf=lev_etf,
    etf=etf,
    start_date=None,
    end_date=end_date,
)

print(f"Table E5: {lev_etf} & {etf} Normalized Data")
display(df)

# %%
max_per_ratio_date = "2020-02-12"

sum_stats = calculate_returns_stats(
    df=df,
    lev_etf=lev_etf,
    etf=etf,
    max_per_ratio_date=max_per_ratio_date,
)

all_sum_stats = pd.concat([all_sum_stats, sum_stats])

print("Table E6: Leveraged and Non-Leveraged ETF Summary Statistics")
display(all_sum_stats)

# %% [markdown]
# For UDOW and DIA, the paper finds a maximum performance ratio of 5.9 (21.62/3.68) on 2/12/2020, and lists a CAGR through that date of 35.7% for UDOW and 13.8% for DIA. Our values are 36% and 14% respectively. The DDD values from the paper at 80.3% and 33.7% are reasonably close to ours at 80% and 37%. For the MDD, the paper lists 66.3% for UDOW, which matches our 66%, and 19.4% for DIA, compared with our 23%. Interestingly, 19.4% is exactly the maximum MDD we find for SPY, so this may be a transcription error in the paper.

# %%
plot_time_series(
    df=df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{lev_etf}_Adj_Close", f"{etf}_Adj_Close"],
    title=f"Figure 3: {lev_etf} & {etf} Adjusted Close Price (Normalized) as of {end_date}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# ### Figure 4: Comparing the normalized value of TNA with its underlying index

# %% [markdown]
# Figure #4 plots TNA and IWM.

# %%
lev_etf = "TNA"
etf = "IWM"
end_date = "2020-10-04"

df = combine_normalize(
    fund_data=fund_data,
    lev_etf=lev_etf,
    etf=etf,
    start_date=None,
    end_date=end_date,
)

print(f"Table E7: {lev_etf} & {etf} Normalized Data")
display(df)

# %%
max_per_ratio_date = "2018-08-29"

sum_stats = calculate_returns_stats(
    df=df,
    lev_etf=lev_etf,
    etf=etf,
    max_per_ratio_date=max_per_ratio_date,
)

all_sum_stats = pd.concat([all_sum_stats, sum_stats])

print("Table E8: Leveraged and Non-Leveraged ETF Summary Statistics")
display(all_sum_stats)

# %% [markdown]
# For TNA and IWM, the paper finds a maximum performance ratio of 3.8 (18.48/4.81) on 8/29/2018, well before the end of the period, and lists a CAGR through that date of 34.5% for TNA and 17.3% for IWM. Our values are 35% and 17% respectively. The DDD values from the paper at 88.1% and 41.1% are very close to ours at 88% and 41%. For the MDD, the paper lists 68.0% for TNA and 32.3% for IWM. Our IWM value of 32% matches, but our TNA value is 83%, measured from the end-of-month peak in August 2018 to the end-of-month trough in March 2020. We were not able to reproduce the paper's value for TNA.

# %%
plot_time_series(
    df=df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{lev_etf}_Adj_Close", f"{etf}_Adj_Close"],
    title=f"Figure 4: {lev_etf} & {etf} Adjusted Close Price (Normalized) as of {end_date}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# An interesting observation from the paper, from page 6:
#
# > "Note that, in this case, the normalized value of TNA at the end of the period actually briefly diminishes below that of IWM as a result of the financial crisis triggered by the COVID-19 pandemic, another illustration of the extreme volatility of the TLETFs compared with their underlying."

# %% [markdown]
# ### Figure 5: Comparing the normalized value of TMF with its underlying index

# %% [markdown]
# Next, figure #5 plots TMF and TLT.

# %%
lev_etf = "TMF"
etf = "TLT"
end_date = "2020-10-04"

df = combine_normalize(
    fund_data=fund_data,
    lev_etf=lev_etf,
    etf=etf,
    start_date=None,
    end_date=end_date,
)

print(f"Table E9: {lev_etf} & {etf} Normalized Data")
display(df)

# %%
max_per_ratio_date = "2020-03-09"

sum_stats = calculate_returns_stats(
    df=df,
    lev_etf=lev_etf,
    etf=etf,
    max_per_ratio_date=max_per_ratio_date,
)

all_sum_stats = pd.concat([all_sum_stats, sum_stats])

print("Table E10: Leveraged and Non-Leveraged ETF Summary Statistics")
display(all_sum_stats)

# %% [markdown]
# For TMF and TLT, the paper finds a maximum performance ratio of 1.9 (4.412/2.294) on 3/9/2020, and reports a CAGR through that date of 14.5% for TMF and 7.9% for TLT. Our values are 15% and 8% respectively. For the drawdowns, the paper reports 53.3% for TMF and 20.7% for TLT, whereas our values are 53% and 21%. For the MDD, the paper reports 49.7% for TMF and 18.2% for TLT, and we find 50% and 18%. So again, very close for both the CAGR and the drawdown metrics.

# %%
plot_time_series(
    df=df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{lev_etf}_Adj_Close", f"{etf}_Adj_Close"],
    title=f"Figure 5: {lev_etf} & {etf} Adjusted Close Price (Normalized) as of {end_date}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# ### Figure 7: Comparing the normalized value of EDC with its underlying index

# %% [markdown]
# As noted above, we will omit DZK and EFA, so we will jump to figure #7 which plots EDC and EEM.

# %%
lev_etf = "EDC"
etf = "EEM"
end_date = "2020-10-04"

df = combine_normalize(
    fund_data=fund_data,
    lev_etf=lev_etf,
    etf=etf,
    start_date=None,
    end_date=end_date,
)

print(f"Table E11: {lev_etf} & {etf} Normalized Data")
display(df)

# %%
max_per_ratio_date = None

sum_stats = calculate_returns_stats(
    df=df,
    lev_etf=lev_etf,
    etf=etf,
    max_per_ratio_date=max_per_ratio_date,
)

all_sum_stats = pd.concat([all_sum_stats, sum_stats])

print("Table E12: Leveraged and Non-Leveraged ETF Summary Statistics")
display(all_sum_stats)

# %% [markdown]
# Finally, the paper does not provide a maximum performance ratio or any CAGR values for EDC or EEM, so we calculate the CAGR over the full period, and find -1% for EDC and 7% for EEM. For the drawdowns, we observed 92% for EDC and 38% for EEM, which is in line with the values of 92.3% and 38.2% that were provided in the paper. The MDD values from the paper of 89.6% and 32.7% also match ours at 90% and 33%.

# %%
plot_time_series(
    df=df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{lev_etf}_Adj_Close", f"{etf}_Adj_Close"],
    title=f"Figure 7: {lev_etf} & {etf} Adjusted Close Price (Normalized) as of {end_date}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# ## Section 3.0: The Risk Mitigation Strategy

# %% [markdown]
# In section 3.0, the paper talks about using a portfolio composed of a combination of 2 TLETFs, rebalanced periodically to maintain a specific asset allocation. The section starts with the following claim:
#
# > "As mentioned earlier, it is easy to show that QQQ, SPY, and DIA are generally negatively correlated with TLT and the same can be said about their corresponding TLETFs."
#
# Before we move on to the portfolio and strategy, let's first look at the correlations between the above mentioned ETFs and the corresponding TLETFs.

# %%
corr_data = pd.DataFrame()

for fund in ["QQQ", "SPY", "DIA", "TLT"]:
    df = fund_data[fund]
    df[f"{fund}_Return"] = df[f"{fund}_Adj_Close"].pct_change()
    corr_data = pd.concat([corr_data, df[[f"{fund}_Return"]]], axis=1)

corr_data = corr_data.dropna()
corr_data = corr_data[corr_data.index >= "2010-02-11"]
corr_data = corr_data[corr_data.index <= "2020-10-04"]

print("Table E13: QQQ, SPY, DIA, and TLT Daily Returns")
display(corr_data)

print("Table E14: Correlation Matrix of QQQ, SPY, DIA, and TLT Daily Returns")
display(corr_data.corr())

# %% [markdown]
# The above table confirms the conjecture from the paper. The correlations amongst the equity and bond funds are in fact negative.
#
# Next, we will confirm the correlations for the leveraged ETFs.

# %%
lev_corr_data = pd.DataFrame()

for fund in ["TQQQ", "UPRO", "UDOW", "TMF"]:
    df = fund_data[fund]
    df[f"{fund}_Return"] = df[f"{fund}_Adj_Close"].pct_change()
    lev_corr_data = pd.concat([lev_corr_data, df[[f"{fund}_Return"]]], axis=1)

lev_corr_data = lev_corr_data.dropna()
lev_corr_data = lev_corr_data[lev_corr_data.index <= "2020-10-04"]

print("Table E15: TQQQ, UPRO, UDOW, and TMF Daily Returns")
display(lev_corr_data)

print("Table E16: Correlation Matrix of TQQQ, UPRO, UDOW, and TMF Daily Returns")
display(lev_corr_data.corr())

# %% [markdown]
# Here we have the same finding. The correlations between the leveraged equity ETFs and the leveraged bond ETF are also negative. They are also nearly identical to the correlations for the underlying non-leveraged ETFs over the same period. This is expected, since the daily return of a leveraged ETF is approximately 3 times the daily return of its underlying index, and scaling a return series does not change its correlation.
#
# Next, we'll look at the strategy. From the paper:
#
# > Strategies that exploit this feature have been shown to exceed the performance of both that of both TLT and the equity ETFs and with reduced risk6,7. Here we focus on the triple leveraged versions of QQQ (TQQQ) and TLT (TMF) and propose simply to purchase a portfolio consisting of equal dollar amounts of both TLETFs and attempt to maintain this percentage by rebalancing on the last day of the k th month, where k=1,2,3,…
#
# We'll use the following helper function to execute the strategy.


# %%
def rebalance_strategy(
    fund_data: dict,
    fund_1: str,
    fund_2: str,
    fund_1_weight: float = 0.5,
    rebalance_months: int = 2,
    transaction_fee: float = 0.0025,
    start_date=None,
    end_date=None,
) -> pd.DataFrame:
    """
    Simulate a two-fund portfolio that is periodically rebalanced back to a target allocation.

    Parameters
    ----------
    fund_data : dict
        Dictionary containing DataFrames for each fund.
    fund_1 : str
        The ticker symbol for the first fund.
    fund_2 : str
        The ticker symbol for the second fund.
    fund_1_weight : float, optional
        Target allocation to the first fund; the second fund receives the remainder (default is 0.5).
    rebalance_months : int, optional
        Rebalance on the last trading day of every k-th month, counting the start month as month 1 (default is 2).
    transaction_fee : float, optional
        Fee charged on the dollar amount of each buy or sell order at a rebalance (default is 0.0025).
    start_date : optional
        Start date for the data. If None, uses the earliest date both funds have data (default is None).
    end_date : optional
        End date for the data. If None, uses the latest available date (default is None).

    Returns
    -------
    pd.DataFrame
        DataFrame with the normalized fund prices, the value of each holding, the normalized
        strategy value, the strategy daily return, and the rebalance flag and fee paid on each day.
    """

    # Combine the adjusted close prices over the common date range
    df = fund_data[fund_1][[f"{fund_1}_Adj_Close"]].merge(
        fund_data[fund_2][[f"{fund_2}_Adj_Close"]], left_index=True, right_index=True
    )

    # Filter by date range
    df = df.loc[start_date:end_date]

    # Normalize prices to start at 1
    df = df / df.iloc[0]

    # Calculate the return series for each fund
    df[f"{fund_1}_Return"] = df[f"{fund_1}_Adj_Close"].pct_change()
    df[f"{fund_2}_Return"] = df[f"{fund_2}_Adj_Close"].pct_change()

    # Calculate the drawdowns for each fund
    df[f"{fund_1}_Drawdown"] = (
        df[f"{fund_1}_Adj_Close"] / df[f"{fund_1}_Adj_Close"].cummax() - 1
    )
    df[f"{fund_2}_Drawdown"] = (
        df[f"{fund_2}_Adj_Close"] / df[f"{fund_2}_Adj_Close"].cummax() - 1
    )
    df[f"{fund_1}_Drawdown_Daily_Max"] = df[f"{fund_1}_Drawdown"].cummin()
    df[f"{fund_2}_Drawdown_Daily_Max"] = df[f"{fund_2}_Drawdown"].cummin()

    # Flag the last trading day of each month, excluding the final row since that month may be incomplete
    month = pd.Series(df.index.to_period("M"), index=df.index)
    month_end = month != month.shift(-1)
    month_end.iloc[-1] = False

    # Rebalance on the last trading day of every k-th month
    month_number = (
        (df.index.year - df.index[0].year) * 12
        + (df.index.month - df.index[0].month)
        + 1
    )
    rebalance = month_end & (month_number % rebalance_months == 0)

    fund_2_weight = 1 - fund_1_weight

    # Initial purchase at the target allocation with a starting portfolio value of 1
    fund_1_shares = fund_1_weight / df[f"{fund_1}_Adj_Close"].iloc[0]
    fund_2_shares = fund_2_weight / df[f"{fund_2}_Adj_Close"].iloc[0]

    fund_1_values, fund_2_values, fees = [], [], []

    for date, row in df.iterrows():
        fund_1_value = fund_1_shares * row[f"{fund_1}_Adj_Close"]
        fund_2_value = fund_2_shares * row[f"{fund_2}_Adj_Close"]
        fee = 0.0

        if rebalance.loc[date]:
            total_value = fund_1_value + fund_2_value

            # Fee on the dollar amount traded in each fund to get back to the target allocation
            fee = transaction_fee * (
                abs(fund_1_weight * total_value - fund_1_value)
                + abs(fund_2_weight * total_value - fund_2_value)
            )
            total_value -= fee

            fund_1_value = fund_1_weight * total_value
            fund_2_value = fund_2_weight * total_value
            fund_1_shares = fund_1_value / row[f"{fund_1}_Adj_Close"]
            fund_2_shares = fund_2_value / row[f"{fund_2}_Adj_Close"]

        fund_1_values.append(fund_1_value)
        fund_2_values.append(fund_2_value)
        fees.append(fee)

    df[f"{fund_1}_Value"] = fund_1_values
    df[f"{fund_2}_Value"] = fund_2_values
    df["Strategy_Adj_Close"] = df[f"{fund_1}_Value"] + df[f"{fund_2}_Value"]
    df["Strategy_Return"] = df["Strategy_Adj_Close"].pct_change()

    # Calculate the drawdown for the strategy
    df["Strategy_Drawdown"] = (
        df["Strategy_Adj_Close"] / df["Strategy_Adj_Close"].cummax() - 1
    )
    df["Strategy_Drawdown_Daily_Max"] = df["Strategy_Drawdown"].cummin()

    df["Rebalance"] = rebalance
    df["Transaction_Fee"] = fees

    return df


# %% [markdown]
# Now, we'll execute the strategy for TQQQ and TMF, as the paper does with a start date of 2/11/2010 and an end date of 10/4/2020.

# %%
tqqq_tmf = rebalance_strategy(
    fund_data=fund_data,
    fund_1="TQQQ",
    fund_2="TMF",
    fund_1_weight=0.5,
    rebalance_months=2,
    transaction_fee=0.0025,  # 0.25% transaction fee
    start_date=None,
    end_date="2020-10-04",
)

print("Table E17: TQQQ/TMF Rebalance Strategy Data")
display(tqqq_tmf)

# %% [markdown]
# And then we can check the summary statistics to confirm that our implementation of the strategy matches the results reported in the paper.

# %%
# Create one empty dataframe for all summary statistics
all_strat_sum_stats = pd.DataFrame()

tqqq_tmf_sum_stats = summary_stats(
    fund_list=["TQQQ", "TMF"],
    df=tqqq_tmf[["Strategy_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
tqqq_tmf_sum_stats.index = ["TQQQ/TMF Strategy"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, tqqq_tmf_sum_stats])

tqqq_sum_stats = summary_stats(
    fund_list=["TQQQ", "TMF"],
    df=tqqq_tmf[["TQQQ_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
tqqq_sum_stats.index = ["TQQQ"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, tqqq_sum_stats])

tmf_sum_stats = summary_stats(
    fund_list=["TQQQ", "TMF"],
    df=tqqq_tmf[["TMF_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
tmf_sum_stats.index = ["TMF"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, tmf_sum_stats])

print("Table E18: Strategy Summary Statistics")
display(all_strat_sum_stats)

# %% [markdown]
# The paper reports a CAGR of 44.9%, and our implementation finds 42%. The discrepancy here is likely the end date. The paper references 10/4/2020, but it seems the data points it uses are actually from 9/2/2020.

# %% [markdown]
# ### Figure 8: Strategy Performance With Bimonthly Rebalancing

# %% [markdown]
# We can reproduce figure 8, which shows the performance of TQQQ, TMF, and the strategy over time.

# %%
plot_time_series(
    df=tqqq_tmf,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_Adj_Close", "TMF_Adj_Close", "Strategy_Adj_Close"],
    title="Figure 8: Rebalance Strategy, TQQQ, and TMF Adjusted Close Price (Normalized) as of 2020-10-04",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# ### Figure 9: Maximum end-of-month draw downs corresponding to fig. 8

# %% [markdown]
# Next, we can recreate figure 9, with the maximum DDD and MDD. First, the full daily drawdown plot.

# %%
plot_time_series(
    df=tqqq_tmf,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_Drawdown", "TMF_Drawdown", "Strategy_Drawdown"],
    title="Figure 9a: Rebalance Strategy, TQQQ, and TMF Daily Drawdowns as of 2020-10-04",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# Next, the maximum DDD.

# %%
plot_time_series(
    df=tqqq_tmf,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "TQQQ_Drawdown_Daily_Max",
        "TMF_Drawdown_Daily_Max",
        "Strategy_Drawdown_Daily_Max",
    ],
    title="Figure 9b: Rebalance Strategy, TQQQ, and TMF Maximum Daily Drawdowns as of 2020-10-04",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# Finally, the maximum MDD.

# %%
tqqq_tmf_monthly = tqqq_tmf.resample("ME").last()

# Calculate the monthly drawdowns using end-of-month prices only, then the running maximum monthly drawdown
for fund in ["TQQQ", "TMF", "Strategy"]:
    tqqq_tmf_monthly[f"{fund}_Drawdown_Monthly"] = (
        tqqq_tmf_monthly[f"{fund}_Adj_Close"]
        / tqqq_tmf_monthly[f"{fund}_Adj_Close"].cummax()
        - 1
    )
    tqqq_tmf_monthly[f"{fund}_Drawdown_Monthly_Max"] = tqqq_tmf_monthly[
        f"{fund}_Drawdown_Monthly"
    ].cummin()

plot_time_series(
    df=tqqq_tmf_monthly,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "TQQQ_Drawdown_Monthly_Max",
        "TMF_Drawdown_Monthly_Max",
        "Strategy_Drawdown_Monthly_Max",
    ],
    title="Figure 9c: Rebalance Strategy, TQQQ, and TMF Maximum Monthly Drawdowns as of 2020-10-04",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# Our plot above matches figure 9 from the paper. We find a maximum MDD of 49% for TQQQ, 50% for TMF, and 24% for the strategy, compared with 49.1% for TQQQ and 49.7% for TMF from section 2.0 of the paper, and 24.4% for the strategy from section 3.2.
#
# Note that the MDD uses end-of-month prices for both the drawdown and the prior peak, so a peak or trough within a month (such as TQQQ's peak on 2/19/2020) is not captured. This is why the MDD values are lower than the DDD values shown in the previous plot.

# %% [markdown]
# ## Section 3.1: Optimum Balance Interval for Risk Mitigation Strategy

# %% [markdown]
# ### Figure 10: Strategy performance on 9/2/20 as a function of rebalancing interval

# %% [markdown]
# Section 3.1 of the paper examines how the performance of the strategy on 9/2/2020 (the date of the peak normalized value) changes as the rebalancing interval is varied from one to six months, both with and without the 0.25% transaction fee. We can reproduce this by running the strategy for each rebalancing interval.

# %%
# Calculate the normalized value of the strategy on 9/2/2020 for rebalancing intervals of 1 to 6 months, with and without the transaction fee
rebalance_interval_results = pd.DataFrame(
    index=pd.Index(range(1, 7), name="Rebalance Interval (Months)")
)

for k in rebalance_interval_results.index:
    for fee, col in [(0.0, "No Transaction Fee"), (0.0025, "Transaction Fee = 0.25%")]:
        df_k = rebalance_strategy(
            fund_data=fund_data,
            fund_1="TQQQ",
            fund_2="TMF",
            fund_1_weight=0.5,
            rebalance_months=k,
            transaction_fee=fee,
            start_date=None,
            end_date="2020-09-02",
        )
        rebalance_interval_results.loc[k, col] = df_k["Strategy_Adj_Close"].iloc[-1]

print("Figure 10: Strategy performance on 9/2/20 as a function of rebalancing interval")
display(rebalance_interval_results)

# %% [markdown]
# ## Section 3.2: Risk Mitigation Strategy Modified to Account for “Black Swan” Events

# %% [markdown]
# In section 3.2, the paper proposes the idea of switching the allocation from the rebalance strategy to cash or a cash substitute, after a severe drop in the price of TQQQ. Specifically:
#
# > Such large one-day losses might cause even disciplined investors to panic sell. Here we propose a simple filter to overlay the risk mitigation strategy described above. The basic idea is to switch the simple strategy to cash, or a near-cash substitute (here we use the 7-10 year Treasury ETF, IEF) whenever an automated alert indicates that the daily return of TQQQ has dropped below a preset minimum. A return to the standard strategy is then only made when a second alert indicates that the daily adjusted close of TQQQ has returned to and exceeded the value it had when the switch was made.
#
# This is an interesting idea, and we will implement it next, but first we need to pull data for IEF.

# %%
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="IEF",
    adjusted=False,
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

# %% [markdown]
# Then append it to the existing dictionary.

# %%
fund_list.append("IEF")

# Load the data for each ETF, rename the columns to include the ticker, store it in the fund_data dictionary
for fund in fund_list:
    data = load_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        timeframe="Daily",
        file_format="pickle",
    )

    data = data.rename(
        columns={
            "Adj Close": f"{fund}_Adj_Close",
            "Close": f"{fund}_Close",
            "High": f"{fund}_High",
            "Low": f"{fund}_Low",
            "Open": f"{fund}_Open",
            "Volume": f"{fund}_Volume",
        }
    )

    fund_data[fund] = data


# %% [markdown]
# And we will use the following helper function. It implements the paper's filter with a threshold of 20% for the one-day drop in TQQQ (the paper's $\partial^{\ast}$) and IEF as the cash substitute. There are a few implementation details worth noting:
#
# * The paper's pseudo-code in figure 11 sets the switch-back price $v^{\ast}$ to the price of TQQQ on the day of the drop, $v(n)$. Implemented that way, TQQQ closes above $v^{\ast}$ the very next day (3/10/2020), and the filter switches in and out three times during March 2020. However, the paper states that the return to the standard strategy occurs on 5/18/2020, which is the first date that TQQQ closes above its price on the day *before* the drop, $v(n-1)$. This also matches the paper's description of TQQQ needing to return to "the value it had when the switch was made", so we use $v(n-1)$ for $v^{\ast}$.
# * While the strategy is holding IEF, the scheduled bimonthly rebalances are skipped.
# * Each switch into or out of IEF pays the 0.25% transaction fee on both the sell and the buy.


# %%
def rebalance_strategy_bs(
    fund_data: dict,
    fund_1: str,
    fund_2: str,
    cash_fund: str = "IEF",
    drop_threshold: float = 0.20,
    fund_1_weight: float = 0.5,
    rebalance_months: int = 2,
    transaction_fee: float = 0.0025,
    start_date=None,
    end_date=None,
) -> pd.DataFrame:
    """
    Simulate a two-fund portfolio that is periodically rebalanced back to a target allocation, with a
    "black swan" filter that switches the portfolio to a cash substitute after a large one-day drop in
    the first fund.

    When the daily return of the first fund falls below -drop_threshold, the entire portfolio is sold and
    moved into the cash fund at that day's close, and the first fund's price from the prior day's close
    (its value before the drop) is recorded. The portfolio stays in the cash fund, skipping any scheduled
    rebalances, until the first fund's price closes above the recorded price, at which point the cash fund
    is sold and the two-fund portfolio is bought back at the target allocation.

    Parameters
    ----------
    fund_data : dict
        Dictionary containing DataFrames for each fund.
    fund_1 : str
        The ticker symbol for the first fund. Its daily return triggers the switch to the cash fund.
    fund_2 : str
        The ticker symbol for the second fund.
    cash_fund : str, optional
        The ticker symbol for the cash substitute held after the filter is triggered (default is "IEF").
    drop_threshold : float, optional
        One-day decline in the first fund that triggers the switch to the cash fund (default is 0.20).
    fund_1_weight : float, optional
        Target allocation to the first fund; the second fund receives the remainder (default is 0.5).
    rebalance_months : int, optional
        Rebalance on the last trading day of every k-th month, counting the start month as month 1 (default is 2).
    transaction_fee : float, optional
        Fee charged on the dollar amount of each buy or sell order at a rebalance or switch (default is 0.0025).
    start_date : optional
        Start date for the data. If None, uses the earliest date all three funds have data (default is None).
    end_date : optional
        End date for the data. If None, uses the latest available date (default is None).

    Returns
    -------
    pd.DataFrame
        DataFrame with the normalized fund prices, the value of each holding, the normalized
        strategy value, the strategy daily return, the rebalance and switch flags, whether the
        portfolio is held in the cash fund, and the fee paid on each day.
    """

    # Combine the adjusted close prices over the common date range
    df = (
        fund_data[fund_1][[f"{fund_1}_Adj_Close"]]
        .merge(
            fund_data[fund_2][[f"{fund_2}_Adj_Close"]],
            left_index=True,
            right_index=True,
        )
        .merge(
            fund_data[cash_fund][[f"{cash_fund}_Adj_Close"]],
            left_index=True,
            right_index=True,
        )
    )

    # Filter by date range
    df = df.loc[start_date:end_date]

    # Normalize prices to start at 1
    df = df / df.iloc[0]

    # Calculate the return series for each fund
    df[f"{fund_1}_Return"] = df[f"{fund_1}_Adj_Close"].pct_change()
    df[f"{fund_2}_Return"] = df[f"{fund_2}_Adj_Close"].pct_change()

    # Calculate the drawdowns for each fund
    df[f"{fund_1}_Drawdown"] = (
        df[f"{fund_1}_Adj_Close"] / df[f"{fund_1}_Adj_Close"].cummax() - 1
    )
    df[f"{fund_2}_Drawdown"] = (
        df[f"{fund_2}_Adj_Close"] / df[f"{fund_2}_Adj_Close"].cummax() - 1
    )
    df[f"{fund_1}_Drawdown_Daily_Max"] = df[f"{fund_1}_Drawdown"].cummin()
    df[f"{fund_2}_Drawdown_Daily_Max"] = df[f"{fund_2}_Drawdown"].cummin()

    # Flag the last trading day of each month, excluding the final row since that month may be incomplete
    month = pd.Series(df.index.to_period("M"), index=df.index)
    month_end = month != month.shift(-1)
    month_end.iloc[-1] = False

    # Rebalance on the last trading day of every k-th month
    month_number = (
        (df.index.year - df.index[0].year) * 12
        + (df.index.month - df.index[0].month)
        + 1
    )
    rebalance = month_end & (month_number % rebalance_months == 0)

    fund_2_weight = 1 - fund_1_weight

    # Initial purchase at the target allocation with a starting portfolio value of 1
    fund_1_shares = fund_1_weight / df[f"{fund_1}_Adj_Close"].iloc[0]
    fund_2_shares = fund_2_weight / df[f"{fund_2}_Adj_Close"].iloc[0]
    cash_fund_shares = 0.0

    # Price of the first fund before the drop that triggered the switch to the cash fund (v* in the paper); 0 when
    # not in the cash fund. The paper's flowchart sets v* = v(n), but its switch back on 5/18/20 matches v* = v(n-1)
    switch_price = 0.0
    prior_close = df[f"{fund_1}_Adj_Close"].shift(1)

    fund_1_values, fund_2_values, cash_fund_values = [], [], []
    rebalanced, switched, in_cash_fund, fees = [], [], [], []

    for date, row in df.iterrows():
        fund_1_value = fund_1_shares * row[f"{fund_1}_Adj_Close"]
        fund_2_value = fund_2_shares * row[f"{fund_2}_Adj_Close"]
        cash_fund_value = cash_fund_shares * row[f"{cash_fund}_Adj_Close"]
        fee = 0.0
        rebalance_today = False
        switch_today = False

        if switch_price > 0:
            # Currently in the cash fund; switch back once the first fund closes above the switch price
            if row[f"{fund_1}_Adj_Close"] > switch_price:
                total_value = cash_fund_value

                # Fee on selling the cash fund and buying the two funds
                fee = transaction_fee * 2 * total_value
                total_value -= fee

                fund_1_value = fund_1_weight * total_value
                fund_2_value = fund_2_weight * total_value
                cash_fund_value = 0.0
                fund_1_shares = fund_1_value / row[f"{fund_1}_Adj_Close"]
                fund_2_shares = fund_2_value / row[f"{fund_2}_Adj_Close"]
                cash_fund_shares = 0.0

                switch_price = 0.0
                switch_today = True

        elif row[f"{fund_1}_Return"] < -drop_threshold:
            # One-day drop in the first fund exceeds the threshold; sell both funds and buy the cash fund
            total_value = fund_1_value + fund_2_value

            # Fee on selling the two funds and buying the cash fund
            fee = transaction_fee * 2 * total_value
            total_value -= fee

            cash_fund_value = total_value
            fund_1_value = 0.0
            fund_2_value = 0.0
            cash_fund_shares = cash_fund_value / row[f"{cash_fund}_Adj_Close"]
            fund_1_shares = 0.0
            fund_2_shares = 0.0

            switch_price = prior_close.loc[date]
            switch_today = True

        elif rebalance.loc[date]:
            total_value = fund_1_value + fund_2_value

            # Fee on the dollar amount traded in each fund to get back to the target allocation
            fee = transaction_fee * (
                abs(fund_1_weight * total_value - fund_1_value)
                + abs(fund_2_weight * total_value - fund_2_value)
            )
            total_value -= fee

            fund_1_value = fund_1_weight * total_value
            fund_2_value = fund_2_weight * total_value
            fund_1_shares = fund_1_value / row[f"{fund_1}_Adj_Close"]
            fund_2_shares = fund_2_value / row[f"{fund_2}_Adj_Close"]
            rebalance_today = True

        fund_1_values.append(fund_1_value)
        fund_2_values.append(fund_2_value)
        cash_fund_values.append(cash_fund_value)
        rebalanced.append(rebalance_today)
        switched.append(switch_today)
        in_cash_fund.append(switch_price > 0)
        fees.append(fee)

    df[f"{fund_1}_Value"] = fund_1_values
    df[f"{fund_2}_Value"] = fund_2_values
    df[f"{cash_fund}_Value"] = cash_fund_values
    df["Strategy_Adj_Close"] = (
        df[f"{fund_1}_Value"] + df[f"{fund_2}_Value"] + df[f"{cash_fund}_Value"]
    )
    df["Strategy_Return"] = df["Strategy_Adj_Close"].pct_change()

    # Calculate the drawdown for the strategy
    df["Strategy_Drawdown"] = (
        df["Strategy_Adj_Close"] / df["Strategy_Adj_Close"].cummax() - 1
    )
    df["Strategy_Drawdown_Daily_Max"] = df["Strategy_Drawdown"].cummin()

    df["Rebalance"] = rebalanced
    df["Switch"] = switched
    df[f"In_{cash_fund}"] = in_cash_fund
    df["Transaction_Fee"] = fees

    return df


# %% [markdown]
# Now, we'll execute the "black swan" strategy for TQQQ and TMF, as the paper does with a start date of 2/11/2010 and an end date of 10/4/2020.

# %%
tqqq_tmf_bs = rebalance_strategy_bs(
    fund_data=fund_data,
    fund_1="TQQQ",
    fund_2="TMF",
    cash_fund="IEF",
    drop_threshold=0.2,
    fund_1_weight=0.5,
    rebalance_months=2,
    transaction_fee=0.0025,  # 0.25% transaction fee
    start_date=None,
    end_date="2020-10-04",
)

print("Table E19: TQQQ/TMF Black Swan Strategy Data")
display(tqqq_tmf_bs)

# %% [markdown]
# And then we can check the summary statistics to confirm that our implementation of the strategy matches the results reported in the paper.

# %%
tqqq_tmf_bs_sum_stats = summary_stats(
    fund_list=["TQQQ", "TMF"],
    df=tqqq_tmf_bs[["Strategy_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
tqqq_tmf_bs_sum_stats.index = ["TQQQ/TMF BS"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, tqqq_tmf_bs_sum_stats])

print("Table E20: Strategy Summary Statistics")
display(all_strat_sum_stats)

# %% [markdown]
# ### Figure 12: Strategy performance with and without IEF filter

# %% [markdown]
# We can then plot figure 12, which compares the performance of the strategy with and without the black swan filter.

# %%
tqqq_tmf_both = tqqq_tmf.merge(
    tqqq_tmf_bs, on="Date", how="outer", suffixes=("", "_BS")
)

plot_time_series(
    df=tqqq_tmf_both,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "TQQQ_Adj_Close",
        "TMF_Adj_Close",
        "Strategy_Adj_Close",
        "Strategy_Adj_Close_BS",
    ],
    title="Figure 12a: Rebalance Strategy, Black Swan Strategy, TQQQ, and TMF Adjusted Close Price (Normalized) as of 2020-10-04",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# Zooming in on the data for 2020:

# %%
plot_time_series(
    df=tqqq_tmf_both[tqqq_tmf_both.index >= "2020-01-01"],
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["Strategy_Adj_Close", "Strategy_Adj_Close_BS"],
    title="Figure 12b: Rebalance Strategy and Black Swan Strategy Adjusted Close Price (Normalized), 2020-01-01 to 2020-10-04",
    x_label="Date",
    x_format="Month",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# Interestingly, the BS strategy misses much of the COVID crash in March of 2020, while retaining nearly all of the performance throughout the rest of the date range.

# %% [markdown]
# ### Figure 13: Maximum daily draw downs with IEF filter used for mitigation strategy

# %% [markdown]
# Finally, figure 13 shows the maximum DDD with the BS filter applied.

# %%
plot_time_series(
    df=tqqq_tmf_bs,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_Drawdown", "TMF_Drawdown", "Strategy_Drawdown"],
    title="Figure 13a: Black Swan Strategy, TQQQ, and TMF Daily Drawdowns as of 2020-10-04",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# Next, the maximum DDD.

# %%
plot_time_series(
    df=tqqq_tmf_bs,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "TQQQ_Drawdown_Daily_Max",
        "TMF_Drawdown_Daily_Max",
        "Strategy_Drawdown_Daily_Max",
    ],
    title="Figure 13b: Black Swan Strategy, TQQQ, and TMF Maximum Daily Drawdowns as of 2020-10-04",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# The above plot is the true replication of figure 13, and it does in fact appear to match. We see a maximum DDD of 30% for the BS strategy, and this does appear to match what is in the paper.

# %% [markdown]
# Finally, the maximum MDD.

# %%
tqqq_tmf_bs_monthly = tqqq_tmf_bs.resample("ME").last()

# Calculate the monthly drawdowns using end-of-month prices only, then the running maximum monthly drawdown
for fund in ["TQQQ", "TMF", "Strategy"]:
    tqqq_tmf_bs_monthly[f"{fund}_Drawdown_Monthly"] = (
        tqqq_tmf_bs_monthly[f"{fund}_Adj_Close"]
        / tqqq_tmf_bs_monthly[f"{fund}_Adj_Close"].cummax()
        - 1
    )
    tqqq_tmf_bs_monthly[f"{fund}_Drawdown_Monthly_Max"] = tqqq_tmf_bs_monthly[
        f"{fund}_Drawdown_Monthly"
    ].cummin()

plot_time_series(
    df=tqqq_tmf_bs_monthly,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "TQQQ_Drawdown_Monthly_Max",
        "TMF_Drawdown_Monthly_Max",
        "Strategy_Drawdown_Monthly_Max",
    ],
    title="Figure 13c: Black Swan Strategy, TQQQ, and TMF Maximum Monthly Drawdowns as of 2020-10-04",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# ## Extension 1: Expanding the date range for analysis

# %% [markdown]
# Above we saw that the rebalance strategy performed well during a time when the correlations between equity and bond funds were negative, which is the entirety of the range between 2010 and 2020. Now, let's expand the date range to present, and see if the results of the rebalance strategy hold up.

# %%
tqqq_tmf_full = rebalance_strategy(
    fund_data=fund_data,
    fund_1="TQQQ",
    fund_2="TMF",
    fund_1_weight=0.5,
    rebalance_months=2,
    transaction_fee=0.0025,  # 0.25% transaction fee
    start_date=None,
    end_date=None,
)

print("Table E21: TQQQ/TMF Rebalance Strategy Data (Full Period)")
display(tqqq_tmf_full)

# %%
tqqq_tmf_full_sum_stats = summary_stats(
    fund_list=["TQQQ", "TMF"],
    df=tqqq_tmf_full[["Strategy_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
tqqq_tmf_full_sum_stats.index = ["TQQQ/TMF Full Strategy"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, tqqq_tmf_full_sum_stats])

print("Table E22: Strategy Summary Statistics")
display(all_strat_sum_stats)

# %% [markdown]
# Here we can see that the performance has degraded over time, especially due to the significant drawdown in TMF. Next, we will look at the plots.

# %%
plot_time_series(
    df=tqqq_tmf_full,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_Adj_Close", "TMF_Adj_Close", "Strategy_Adj_Close"],
    title=f"Figure E1: Rebalance Strategy, TQQQ, and TMF Adjusted Close Price (Normalized) as of {tqqq_tmf_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# We can see that the strategy peaked in late 2021, and appears to have struggled since then. This could be due to the TQQQ performance, but since 2023 TQQQ has shown significant growth. Therefore, we suspect that TMF is actually the cause of the strategy underperformance, and we should look at its performance closely.

# %%
lev_etf = "TMF"
etf = "TLT"
end_date = None

df = combine_normalize(
    fund_data=fund_data,
    lev_etf=lev_etf,
    etf=etf,
    start_date=None,
    end_date=end_date,
)

print(f"Table E23: {lev_etf} & {etf} Normalized Data (Full Period)")
display(df)

# %%
plot_time_series(
    df=df,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[f"{lev_etf}_Adj_Close", f"{etf}_Adj_Close"],
    title=f"Figure E2: {lev_etf} & {etf} Adjusted Close Price (Normalized) as of {df.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# Here we have the answer. TMF has essentially collapsed since mid-2020, which explains the underperformance of the strategy despite the strong performance of TQQQ in recent years. Every time the strategy has been rebalancing, it has been selling TQQQ to buy TMF at depressed prices, which has hindered overall performance.
#
# Let's look at the drawdown plots to see how the strategy has been affected by the TMF collapse.

# %%
plot_time_series(
    df=tqqq_tmf_full,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_Drawdown", "TMF_Drawdown", "Strategy_Drawdown"],
    title=f"Figure E3: Rebalance Strategy, TQQQ, and TMF Daily Drawdowns as of {tqqq_tmf_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# Next, the maximum DDD.

# %%
plot_time_series(
    df=tqqq_tmf_full,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "TQQQ_Drawdown_Daily_Max",
        "TMF_Drawdown_Daily_Max",
        "Strategy_Drawdown_Daily_Max",
    ],
    title=f"Figure E4: Rebalance Strategy, TQQQ, and TMF Maximum Daily Drawdowns as of {tqqq_tmf_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# To confirm the change in regime, we can look at the correlation between the daily returns of TQQQ and TMF over time, first by calendar year, and then on a rolling 252 trading day (roughly one year) basis.

# %%
# Calculate the correlation between TQQQ and TMF daily returns for each calendar year
annual_corr = (
    tqqq_tmf_full.groupby(tqqq_tmf_full.index.year)
    .apply(lambda x: x["TQQQ_Return"].corr(x["TMF_Return"]))
    .to_frame(name="TQQQ_TMF_Correlation")
)
annual_corr.index.name = "Year"

print("Table E24: Annual Correlation of TQQQ and TMF Daily Returns")
display(annual_corr)

# %%
# Calculate the rolling 252 day correlation between TQQQ and TMF daily returns
tqqq_tmf_full["TQQQ_TMF_Rolling_Correlation"] = (
    tqqq_tmf_full["TQQQ_Return"].rolling(252).corr(tqqq_tmf_full["TMF_Return"])
)

plot_time_series(
    df=tqqq_tmf_full,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["TQQQ_TMF_Rolling_Correlation"],
    title=f"Figure E5: TQQQ & TMF 252-Day Rolling Correlation of Daily Returns as of {tqqq_tmf_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Correlation",
    y_format="Decimal",
    y_format_decimal_places=2,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# The correlation was negative in every year from 2010 through 2020, ranging from -0.16 to -0.62. Since 2021, it has been zero or positive in every year. The rolling correlation shows the same shift. Before 2021, it was positive for only a brief period in 2017, whereas since 2021 it has been positive for the vast majority of days.

# %% [markdown]
# What we find here is almost the worst case scenario for long-term investing in triple leveraged exchange traded funds. For years, we have a strategy that performs very well, with relatively low risk (Sharpe ratio of 1.4), but due to a regime change in markets, and a reversal of the historic equity/bond negative correlation, the strategy experiences significant drawdowns and underperformance, highlighting the challenges and risks associated with long-term investing in such leveraged instruments.

# %% [markdown]
# ## Extension 2: Expanding the date range for analysis (including "Black Swan")

# %% [markdown]
# We can also extend the date range for the BS strategy, to see if that impacted the overall performance at all.

# %%
tqqq_tmf_bs_full = rebalance_strategy_bs(
    fund_data=fund_data,
    fund_1="TQQQ",
    fund_2="TMF",
    cash_fund="IEF",
    drop_threshold=0.2,
    fund_1_weight=0.5,
    rebalance_months=2,
    transaction_fee=0.0025,  # 0.25% transaction fee
    start_date=None,
    end_date=None,
)

print("Table E25: TQQQ/TMF Black Swan Strategy Data (Full Period)")
display(tqqq_tmf_bs_full)

# %%
tqqq_tmf_bs_full_sum_stats = summary_stats(
    fund_list=["TQQQ", "TMF"],
    df=tqqq_tmf_bs_full[["Strategy_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
tqqq_tmf_bs_full_sum_stats.index = ["TQQQ/TMF Full BS"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, tqqq_tmf_bs_full_sum_stats])

print("Table E26: Strategy Summary Statistics")
display(all_strat_sum_stats)

# %%
tqqq_tmf_full_both = tqqq_tmf_full.merge(
    tqqq_tmf_bs_full, on="Date", how="outer", suffixes=("", "_BS")
)

plot_time_series(
    df=tqqq_tmf_full_both,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "TQQQ_Adj_Close",
        "TMF_Adj_Close",
        "Strategy_Adj_Close",
        "Strategy_Adj_Close_BS",
    ],
    title=f"Figure E6: Rebalance Strategy, Black Swan Strategy, TQQQ, and TMF Adjusted Close Price (Normalized) as of {tqqq_tmf_full_both.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# From the summary stats and the plot, we can see that the BS strategy did not materially change the performance. It might have had a risk-mitigation effect during COVID, but ultimately is not designed to handle nor is effective during long prolonged drawdowns.

# %% [markdown]
# ## Extension 3: Using UPRO and AGG

# %% [markdown]
# For our third extention, we'll examine the performance of a portfolio consisting of UPRO and AGG, to see how it compares to the previous strategies.
#
# One might say that UPRO is a more "well rounded" fund than TQQQ, in that it includes not only tech but other sectors of the market as well. This diversification could potentially reduce the overall volatility of the portfolio while still providing leveraged exposure to the broader market.
#
# Similarly, AGG (the iShares Core U.S. Aggregate Bond ETF) provides exposure to the bond market, which tends to have a low correlation with equities. Using a non-leveraged fund will likely reduce the performance, but it might also help stabilize the volatility and provide a smoother overall return profile.
#
# To compare with the TQQQ/TMF strategy over the same period, we'll use the same start date of 2/11/2010, even though UPRO has data back to June 2009.
#
# First, we need to pull data for AGG.

# %%
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="AGG",
    adjusted=False,
    source="Yahoo_Finance",
    asset_class="Exchange_Traded_Funds",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

# %% [markdown]
# Then append it to the existing dictionary.

# %%
fund_list.append("AGG")

# Load the data for each ETF, rename the columns to include the ticker, store it in the fund_data dictionary
for fund in fund_list:
    data = load_data(
        base_directory=DATA_DIR,
        ticker=fund,
        source="Yahoo_Finance",
        asset_class="Exchange_Traded_Funds",
        timeframe="Daily",
        file_format="pickle",
    )

    data = data.rename(
        columns={
            "Adj Close": f"{fund}_Adj_Close",
            "Close": f"{fund}_Close",
            "High": f"{fund}_High",
            "Low": f"{fund}_Low",
            "Open": f"{fund}_Open",
            "Volume": f"{fund}_Volume",
        }
    )

    fund_data[fund] = data

# %% [markdown]
# Now we can run the strategy.

# %%
upro_agg_full = rebalance_strategy(
    fund_data=fund_data,
    fund_1="UPRO",
    fund_2="AGG",
    fund_1_weight=0.5,
    rebalance_months=2,
    transaction_fee=0.0025,  # 0.25% transaction fee
    start_date="2010-02-11",
    end_date=None,
)

print("Table E27: UPRO/AGG Rebalance Strategy Data")
display(upro_agg_full)

# %%
upro_agg_full_sum_stats = summary_stats(
    fund_list=["UPRO", "AGG"],
    df=upro_agg_full[["Strategy_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
upro_agg_full_sum_stats.index = ["UPRO/AGG Full Strategy"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, upro_agg_full_sum_stats])

print("Table E28: Strategy Summary Statistics")
display(all_strat_sum_stats)

# %% [markdown]
# Comparing the last 3 lines from above gives us an interesting result. Our CAGR for the UPRO/AGG strategy is lower than that of the TQQQ/TMF strategy, but the volatility and drawdowns are both significantly reduced, leading to a more stable overall performance, and an improved MAR ratio.
#
# And now the plots for the UPRO/AGG strategy.

# %%
plot_time_series(
    df=upro_agg_full,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["UPRO_Adj_Close", "AGG_Adj_Close", "Strategy_Adj_Close"],
    title=f"Figure E7: Rebalance Strategy, UPRO, and AGG Adjusted Close Price (Normalized) as of {upro_agg_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=1,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %%
plot_time_series(
    df=upro_agg_full,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=["UPRO_Drawdown", "AGG_Drawdown", "Strategy_Drawdown"],
    title=f"Figure E8: Rebalance Strategy, UPRO, and AGG Daily Drawdowns as of {upro_agg_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %%
plot_time_series(
    df=upro_agg_full,
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "UPRO_Drawdown_Daily_Max",
        "AGG_Drawdown_Daily_Max",
        "Strategy_Drawdown_Daily_Max",
    ],
    title=f"Figure E9: Rebalance Strategy, UPRO, and AGG Maximum Daily Drawdowns as of {upro_agg_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=1,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# ## Extension 4: Extrapolating UPRO Back To 1993

# %% [markdown]
# UPRO only has data back to its inception on 6/25/2009, which means that all of the results above come from a period that excludes both the dot-com crash and the 2008 financial crisis. To see how the strategy might have performed through those periods, we will extrapolate the returns for UPRO back to the start of SPY in January 1993, using a regression of the daily returns of UPRO on those of SPY over the period where both funds have data. Before the inception of UPRO we use the extrapolated data, and after its inception we use the actual data.
#
# For the bond fund, we will use VBMFX (the Vanguard Total Bond Market Index Fund), which tracks the same index as AGG but has data back to 1986. We will then run the strategy on both UPRO/VBMFX and SPY/VBMFX from 1993 to present.
#
# First, we need to pull data for VBMFX.

# %%
yf_pull_data(
    base_directory=DATA_DIR,
    ticker="VBMFX",
    adjusted=False,
    source="Yahoo_Finance",
    asset_class="Mutual_Funds",
    excel_export=True,
    pickle_export=True,
    output_confirmation=False,
)

# %% [markdown]
# Then add it to the existing dictionary. Since VBMFX is a mutual fund rather than an ETF, we load it separately.

# %%
data = load_data(
    base_directory=DATA_DIR,
    ticker="VBMFX",
    source="Yahoo_Finance",
    asset_class="Mutual_Funds",
    timeframe="Daily",
    file_format="pickle",
)

data = data.rename(
    columns={
        "Adj Close": "VBMFX_Adj_Close",
        "Close": "VBMFX_Close",
        "High": "VBMFX_High",
        "Low": "VBMFX_Low",
        "Open": "VBMFX_Open",
        "Volume": "VBMFX_Volume",
    }
)

fund_data["VBMFX"] = data

# %% [markdown]
# Next, we run a regression of the daily returns of UPRO on the daily returns of SPY, over the period where both funds have data. The slope (beta) is the leverage that UPRO actually delivers, and the constant (alpha) captures the daily costs of the fund, including financing and fees.

# %%
# Merge UPRO and SPY over the period where both funds have data
upro_spy = fund_data["UPRO"][["UPRO_Adj_Close"]].merge(
    fund_data["SPY"][["SPY_Adj_Close"]], left_index=True, right_index=True
)
upro_spy["UPRO_Return"] = upro_spy["UPRO_Adj_Close"].pct_change()
upro_spy["SPY_Return"] = upro_spy["SPY_Adj_Close"].pct_change()
upro_spy = upro_spy.dropna()

upro_spy_model = run_regression(
    df=upro_spy,
    x_plot_column="SPY_Return",
    y_plot_column="UPRO_Return",
    regression_model="OLS-statsmodels",
    regression_constant=True,
)

alpha = upro_spy_model.params.iloc[0]
beta = upro_spy_model.params.iloc[1]

print("Table E29: Regression of UPRO Daily Returns on SPY Daily Returns")
display(upro_spy_model.summary())

# %% [markdown]
# Before extrapolating, we can check how well the regression fits the actual UPRO data. Over the period where both funds have data, we compare the CAGR of the actual UPRO returns with the CAGR of the returns constructed from SPY, using only the beta, and using both the alpha and the beta.

# %%
# Compare the actual UPRO returns with the returns constructed from SPY
fit_check = pd.DataFrame(
    {
        "Actual UPRO": upro_spy["UPRO_Return"],
        "Beta x SPY": beta * upro_spy["SPY_Return"],
        "Alpha + Beta x SPY": alpha + beta * upro_spy["SPY_Return"],
    }
)

years = len(fit_check) / 252
fit_check_cagr = ((1 + fit_check).prod() ** (1 / years) - 1).to_frame(name="CAGR")

print("Table E30: CAGR of Actual UPRO vs Returns Constructed From SPY")
display(fit_check_cagr)

# %% [markdown]
# The table above tells us that we have an adequate fit for the regression.
#
# Next, we use the alpha and beta to extrapolate the UPRO returns back to the start of SPY, and then walk the price backwards from the first actual price of UPRO. Here is the data around the inception of UPRO after the extrapolation:

# %%
# Merge SPY with UPRO over the full history of SPY
upro_extrap = fund_data["SPY"][["SPY_Adj_Close"]].merge(
    fund_data["UPRO"][["UPRO_Adj_Close"]], left_index=True, right_index=True, how="left"
)
upro_extrap["SPY_Return"] = upro_extrap["SPY_Adj_Close"].pct_change()
upro_extrap["UPRO_Return"] = upro_extrap["UPRO_Adj_Close"].pct_change()

# Before the inception of UPRO, fill the returns using the regression coefficients
upro_extrap["UPRO_Return"] = upro_extrap["UPRO_Return"].fillna(
    alpha + beta * upro_extrap["SPY_Return"]
)

# Walk backwards from the first actual price of UPRO: Price_{t} = Price_{t+1} / (1 + Return_{t+1})
first_valid_idx = upro_extrap["UPRO_Adj_Close"].first_valid_index()
splice_loc = upro_extrap.index.get_loc(first_valid_idx)
for i in range(splice_loc - 1, -1, -1):
    current_return = upro_extrap.iloc[i + 1]["UPRO_Return"]
    next_price = upro_extrap.iloc[i + 1]["UPRO_Adj_Close"]
    upro_extrap.loc[upro_extrap.index[i], "UPRO_Adj_Close"] = next_price / (
        1 + current_return
    )

# Store as a separate fund so the actual UPRO data is unchanged
fund_data["UPRO_Extrap"] = upro_extrap[["UPRO_Adj_Close"]].rename(
    columns={"UPRO_Adj_Close": "UPRO_Extrap_Adj_Close"}
)

print("Table E31: Extrapolated UPRO Data Around the Inception of UPRO")
display(upro_extrap.iloc[splice_loc - 3 : splice_loc + 3])

# %% [markdown]
# And now we can run the strategy for both UPRO/VBMFX and SPY/VBMFX, from 1993 to present.

# %%
upro_extrap_vbmfx_full = rebalance_strategy(
    fund_data=fund_data,
    fund_1="UPRO_Extrap",
    fund_2="VBMFX",
    fund_1_weight=0.5,
    rebalance_months=2,
    transaction_fee=0.0025,  # 0.25% transaction fee
    start_date=None,
    end_date=None,
)

print("Table E32: UPRO (Extrap)/VBMFX Rebalance Strategy Data")
display(upro_extrap_vbmfx_full)

spy_vbmfx_full = rebalance_strategy(
    fund_data=fund_data,
    fund_1="SPY",
    fund_2="VBMFX",
    fund_1_weight=0.5,
    rebalance_months=2,
    transaction_fee=0.0025,  # 0.25% transaction fee
    start_date=None,
    end_date=None,
)

print("Table E33: SPY/VBMFX Rebalance Strategy Data")
display(spy_vbmfx_full)

# %%
upro_extrap_vbmfx_full_sum_stats = summary_stats(
    fund_list=["UPRO (Extrap)/VBMFX"],
    df=upro_extrap_vbmfx_full[["Strategy_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
upro_extrap_vbmfx_full_sum_stats.index = ["UPRO (Extrap)/VBMFX Full Strategy"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, upro_extrap_vbmfx_full_sum_stats])

upro_extrap_sum_stats = summary_stats(
    fund_list=["UPRO (Extrap)/VBMFX"],
    df=upro_extrap_vbmfx_full[["UPRO_Extrap_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
upro_extrap_sum_stats.index = ["UPRO (Extrap)"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, upro_extrap_sum_stats])

spy_vbmfx_full_sum_stats = summary_stats(
    fund_list=["SPY/VBMFX"],
    df=spy_vbmfx_full[["Strategy_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
spy_vbmfx_full_sum_stats.index = ["SPY/VBMFX Full Strategy"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, spy_vbmfx_full_sum_stats])

spy_sum_stats = summary_stats(
    fund_list=["SPY"],
    df=spy_vbmfx_full[["SPY_Return"]].dropna(),
    period="Daily",
    use_calendar_days=False,
    excel_export=False,
    pickle_export=False,
    output_confirmation=False,
)

# Rename the index to indicate the strategy
spy_sum_stats.index = ["SPY"]

all_strat_sum_stats = pd.concat([all_strat_sum_stats, spy_sum_stats])

print("Table E34: Strategy Summary Statistics")
display(all_strat_sum_stats)

# %% [markdown]
# To make the comparison as easy as possible, we will plot both the UPRO (Extrap)/VBMFX strategy and the actual SPY/VBMFX strategy together, along with each of the individual components.

# %%
plot_time_series(
    df=upro_extrap_vbmfx_full.merge(
        spy_vbmfx_full,
        on="Date",
        how="outer",
        suffixes=("_UPRO_Extrap_VBMFX", "_SPY_VBMFX"),
    ).rename(columns={"VBMFX_Adj_Close_UPRO_Extrap_VBMFX": "VBMFX_Adj_Close"}),
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "UPRO_Extrap_Adj_Close",
        "SPY_Adj_Close",
        "VBMFX_Adj_Close",
        "Strategy_Adj_Close_UPRO_Extrap_VBMFX",
        "Strategy_Adj_Close_SPY_VBMFX",
    ],
    title=f"Figure E10: Rebalance Strategies, UPRO (Extrap), SPY, and VBMFX Adjusted Close Price (Normalized) as of {upro_extrap_vbmfx_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Price ($)",
    y_format="Decimal",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %%
plot_time_series(
    df=upro_extrap_vbmfx_full.merge(
        spy_vbmfx_full,
        on="Date",
        how="outer",
        suffixes=("_UPRO_Extrap_VBMFX", "_SPY_VBMFX"),
    ).rename(columns={"VBMFX_Drawdown_UPRO_Extrap_VBMFX": "VBMFX_Drawdown"}),
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "UPRO_Extrap_Drawdown",
        "SPY_Drawdown",
        "VBMFX_Drawdown",
        "Strategy_Drawdown_UPRO_Extrap_VBMFX",
        "Strategy_Drawdown_SPY_VBMFX",
    ],
    title=f"Figure E11: Rebalance Strategies, UPRO (Extrap), SPY, and VBMFX Daily Drawdowns as of {upro_extrap_vbmfx_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %%
plot_time_series(
    df=upro_extrap_vbmfx_full.merge(
        spy_vbmfx_full,
        on="Date",
        how="outer",
        suffixes=("_UPRO_Extrap_VBMFX", "_SPY_VBMFX"),
    ).rename(
        columns={
            "VBMFX_Drawdown_Daily_Max_UPRO_Extrap_VBMFX": "VBMFX_Drawdown_Daily_Max"
        }
    ),
    plot_start_date=None,
    plot_end_date=None,
    plot_columns=[
        "UPRO_Extrap_Drawdown_Daily_Max",
        "SPY_Drawdown_Daily_Max",
        "VBMFX_Drawdown_Daily_Max",
        "Strategy_Drawdown_Daily_Max_UPRO_Extrap_VBMFX",
        "Strategy_Drawdown_Daily_Max_SPY_VBMFX",
    ],
    title=f"Figure E12: Rebalance Strategies, UPRO (Extrap), SPY, and VBMFX Maximum Daily Drawdowns as of {upro_extrap_vbmfx_full.index[-1].date()}",
    x_label="Date",
    x_format="Year",
    x_tick_spacing=2,
    x_tick_start=None,
    x_tick_rotation=0,
    y_label="Drawdown",
    y_format="Percentage",
    y_format_decimal_places=0,
    y_tick_spacing="Auto",
    y_tick_rotation=0,
    caption="Data Source: Yahoo Finance, Analysis by the Author",
)

# %% [markdown]
# ## Conclusion

# %% [markdown]
# First, the way the paper handles the different dates for the CAGR, DDD, and MDD is quite unusual and requires careful consideration when attempting to reproduce the results accurately. Typically, one would expect a specific data range to be consistently applied across all metrics to ensure comparability and validity of the results. The unusual way that the paper handled the dates actually required quite a bit of extra effort to align the data correctly and update the summary stats tables with additional fields to accurately portray what was being calculated in the paper.
#
# Second, the pseudo-code for the "black swan" filter in figure 11 does not match the results reported in the paper. The pseudo-code sets the switch-back price $v^{\ast}$ to the price of TQQQ on the day of the drop, $v(n)$, but implemented that way, the filter switches back to the standard strategy the very next day and whipsaws in and out of IEF three times during March 2020. Using the price of TQQQ on the day before the drop, $v(n-1)$, instead reproduces both the 5/18/2020 switch-back date and the 30% maximum DDD reported in the paper. When the pseudo-code and the reported results disagree, the results (and the paper's written description of the method) are the better guide for a replication.

# %% [markdown]
# ## Future Investigation

# %% [markdown]
# Nothing here yet.

# %% [markdown]
# ## References

# %% [markdown]
# 1. Glenn, Lewis A., Long-Term Investing in Triple Leveraged Exchange Traded Funds (October 30, 2020). Available at SSRN: https://ssrn.com/abstract=3722318 or http://dx.doi.org/10.2139/ssrn.3722318

# %% [markdown]
#
