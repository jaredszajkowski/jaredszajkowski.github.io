import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np
import pandas as pd

from matplotlib.ticker import MultipleLocator, PercentFormatter, FormatStrFormatter
from run_regression import run_regression

from round_to_nice_value import round_to_nice_value


def plot_scatter(
    df: pd.DataFrame,
    x_plot_column: str,
    y_plot_columns: list,
    title: str,
    x_label: str,
    x_format: str,
    x_format_decimal_places: int,
    x_tick_spacing: int,
    x_tick_start: str,
    x_tick_rotation: int,
    y_label: str,
    y_format: str,
    y_format_decimal_places: int,
    y_tick_spacing: int,
    y_tick_rotation: int,
    plot_OLS_regression_line: bool = False,
    OLS_column: str = None,
    plot_Ridge_regression_line: bool = False,
    Ridge_column: str = None,
    plot_RidgeCV_regression_line: bool = False,
    RidgeCV_column: str = None,
    regression_constant: bool = True,
    grid: bool = True,
    legend: bool = True,
    export_plot: bool = False,
    plot_file_name: str = None,
) -> None:
    """
    Plot the data from a DataFrame for a specified date range and columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the price data to plot.
    x_plot_column : str
        Column to plot on the x-axis from the DataFrame.
    y_plot_columns : list
        Columns to plot on the y-axis from the DataFrame.
    title : str
        Title of the plot.
    x_label : str
        Label for the x-axis.
    x_format : str
        Format for the x-axis date labels.
    x_tick_spacing : int
        Spacing for the x-axis ticks.
    x_tick_start : str
        Start date for the x-axis ticks.
    x_tick_rotation : int
        Rotation angle for the x-axis tick labels.
    y_label : str
        Label for the y-axis.
    y_format : str
        Format for the y-axis labels.
    y_format_decimal_places : int
        Number of decimal places for y-axis labels.
    y_tick_spacing : int
        Spacing for the y-axis ticks.
    y_tick_rotation : int
        Rotation angle for the y-axis tick labels.
    plot_OLS_regression_line : bool, optional
        Whether to plot an OLS regression line on the scatter plot (default: False).
    OLS_column : str, optional
        Column name for the OLS regression line (default: None).
    plot_Ridge_regression_line : bool, optional
        Whether to plot a Ridge regression line on the scatter plot (default: False).
    Ridge_column : str, optional
        Column name for the Ridge regression line (default: None).
    plot_RidgeCV_regression_line : bool, optional
        Whether to plot a RidgeCV regression line on the scatter plot (default: False).
    RidgeCV_column : str, optional
        Column name for the RidgeCV regression line (default: None).
    regression_constant : bool, optional
        Whether to include a constant term in the regression models (default: True).
    grid : bool, optional
        Whether to display a grid on the plot (default is True).
    legend : bool, optional
        Whether to display a legend on the plot (default is True).
    export_plot : bool, optional
        Whether to save the figure as a PNG file (default is False).
    plot_file_name : str, optional
        File name for saving the figure (if export_plot is True, default is None).

    Returns
    -------
    None
    """

    # Set plot figure size and background color
    plt.figure(figsize=(10, 6))

    # Plot data
    for col in y_plot_columns:
        plt.scatter(df[x_plot_column], df[col], label=col, marker="o", alpha=0.5)

    # Resolve "Auto" x-tick spacing for numeric x-axes only
    # (date-based formats use mdates locators and ignore x_tick_spacing as a numeric value)
    numeric_x_formats = ("Decimal", "Percentage", "Scientific", "Log")
    if x_tick_spacing == "Auto":
        if x_format in numeric_x_formats:
            raw_x_spacing = (df[x_plot_column].max() - df[x_plot_column].min()) / 20
            x_tick_spacing = round_to_nice_value(raw_x_spacing)
        else:
            # Date-based or string x-axis: "Auto" is not meaningful; pick a safe default
            # so downstream code that may reference x_tick_spacing doesn't fail.
            x_tick_spacing = 1

    # Format X axis
    if x_format == "Decimal":
        plt.gca().xaxis.set_major_formatter(
            FormatStrFormatter(f"%.{x_format_decimal_places}f")
        )
    elif x_format == "Percentage":
        plt.gca().xaxis.set_major_formatter(
            PercentFormatter(xmax=1, decimals=x_format_decimal_places)
        )
    elif x_format == "Scientific":
        plt.gca().xaxis.set_major_formatter(
            FormatStrFormatter(f"%.{x_format_decimal_places}e")
        )
    elif x_format == "Log":
        plt.xscale("log")
    elif x_format == "Second":
        if x_tick_start is not None:
            ticks = pd.date_range(
                start=pd.Timestamp(x_tick_start).tz_convert(df[x_plot_column].dt.tz),
                end=df[x_plot_column].max() + pd.tseries.offsets.Second(x_tick_spacing),
                freq=pd.tseries.offsets.Second(x_tick_spacing),
            )
            plt.gca().set_xticks(ticks)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        else:
            plt.gca().xaxis.set_major_locator(
                mdates.SecondLocator(interval=x_tick_spacing)
            )
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    elif x_format == "Minute":
        if x_tick_start is not None:
            ticks = pd.date_range(
                start=pd.Timestamp(x_tick_start).tz_convert(df[x_plot_column].dt.tz),
                end=df[x_plot_column].max() + pd.tseries.offsets.Minute(x_tick_spacing),
                freq=pd.tseries.offsets.Minute(x_tick_spacing),
            )
            plt.gca().set_xticks(ticks)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:
            plt.gca().xaxis.set_major_locator(
                mdates.MinuteLocator(interval=x_tick_spacing)
            )
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    elif x_format == "Hour":
        if x_tick_start is not None:
            ticks = pd.date_range(
                start=pd.Timestamp(x_tick_start).tz_convert(df[x_plot_column].dt.tz),
                end=df[x_plot_column].max() + pd.tseries.offsets.Hour(x_tick_spacing),
                freq=pd.tseries.offsets.Hour(x_tick_spacing),
            )
            plt.gca().set_xticks(ticks)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:
            plt.gca().xaxis.set_major_locator(
                mdates.HourLocator(interval=x_tick_spacing)
            )
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    elif x_format == "Day":
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=x_tick_spacing))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    elif x_format == "Week":
        plt.gca().xaxis.set_major_locator(
            mdates.WeekdayLocator(interval=x_tick_spacing)
        )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    elif x_format == "Month":
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=x_tick_spacing))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    elif x_format == "Year":
        plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=x_tick_spacing))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    elif x_format == "String":
        pass  # No special formatting for string x-axis
    else:
        raise ValueError(
            f"Unrecognized x_format: {x_format}. Use 'Decimal', 'Percentage', 'Scientific', 'Second', 'Minute', 'Hour', 'Day', 'Week', 'Month', 'Year', or 'String'."
        )

    if x_format not in (
        "Second",
        "Minute",
        "Hour",
        "Day",
        "Week",
        "Month",
        "Year",
        "String",
    ):
        plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
    plt.xlabel(x_label)

    if x_tick_rotation != 0:
        # Line up the x-ticks with the labels when rotated
        plt.xticks(rotation=x_tick_rotation, ha="right")
    else:
        plt.xticks(rotation=x_tick_rotation)

    # Format Y axis
    if y_format == "Decimal":
        plt.gca().yaxis.set_major_formatter(
            FormatStrFormatter(f"%.{y_format_decimal_places}f")
        )
    elif y_format == "Percentage":
        plt.gca().yaxis.set_major_formatter(
            PercentFormatter(xmax=1, decimals=y_format_decimal_places)
        )
    elif y_format == "Scientific":
        plt.gca().yaxis.set_major_formatter(
            FormatStrFormatter(f"%.{y_format_decimal_places}e")
        )
    elif y_format == "Log":
        plt.yscale("log")
    else:
        raise ValueError(
            f"Unrecognized y_format: {y_format}. Use 'Decimal', 'Percentage', 'Scientific', or 'Log'."
        )

    if y_tick_spacing == "Auto":
        max_value = 0
        min_value = 1_000_000
        for col in y_plot_columns:
            if df[col].max() > max_value:
                max_value = df[col].max()

            if df[col].min() < min_value:
                min_value = df[col].min()

        raw_y_spacing = (max_value - min_value) / 10
        y_tick_spacing = round_to_nice_value(raw_y_spacing)
    else:
        y_tick_spacing = y_tick_spacing

    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel(y_label)
    plt.yticks(rotation=y_tick_rotation)

    if plot_OLS_regression_line == True:

        model = run_regression(
            df=df,
            x_plot_column=x_plot_column,
            y_plot_column=OLS_column,
            regression_model="OLS-sklearn",
            regression_constant=regression_constant,
        )

        # Calc X and Y values for regression line
        X_vals = np.linspace(df[x_plot_column].min(), df[x_plot_column].max(), 100)
        X_vals_2d = X_vals.reshape(-1, 1)  # sklearn needs 2D input
        Y_vals = model.predict(X_vals_2d)

        # Plot regression line
        intercept = model.intercept_
        slope = model.coef_[0]
        plt.plot(
            X_vals,
            Y_vals,
            color="red",
            linestyle="--",
            label=f"OLS Fit: y = {intercept:.1f} + {slope:.2f}x",
        )

    if plot_Ridge_regression_line == True:

        model = run_regression(
            df=df,
            x_plot_column=x_plot_column,
            y_plot_column=Ridge_column,
            regression_model="Ridge",
            regression_constant=regression_constant,
            ridge_alpha=1.0,
        )

        # Calc X and Y values for regression line
        X_vals = np.linspace(df[x_plot_column].min(), df[x_plot_column].max(), 100)
        X_vals_2d = X_vals.reshape(-1, 1)  # sklearn needs 2D input
        Y_vals = model.predict(X_vals_2d)

        # Plot regression line
        intercept = model.intercept_
        slope = model.coef_[0]
        alpha_value = model.alpha_ if hasattr(model, "alpha_") else 1.0
        plt.plot(
            X_vals,
            Y_vals,
            color="blue",
            linestyle="--",
            label=f"Ridge Fit (α={alpha_value:.2f}): y = {intercept:.1f} + {slope:.2f}x",
        )

    if plot_RidgeCV_regression_line == True:

        model = run_regression(
            df=df,
            x_plot_column=x_plot_column,
            y_plot_column=RidgeCV_column,
            regression_model="RidgeCV",
            regression_constant=regression_constant,
        )

        # Calc X and Y values for regression line
        X_vals = np.linspace(df[x_plot_column].min(), df[x_plot_column].max(), 100)
        X_vals_2d = X_vals.reshape(-1, 1)  # sklearn needs 2D input
        Y_vals = model.predict(X_vals_2d)

        # Plot regression line
        intercept = model.intercept_
        slope = model.coef_[0]
        alpha_value = model.alpha_ if hasattr(model, "alpha_") else 1.0
        plt.plot(
            X_vals,
            Y_vals,
            color="green",
            linestyle="--",
            label=f"RidgeCV Fit (α={alpha_value:.2f}): y = {intercept:.1f} + {slope:.2f}x",
        )

    # Format title, layout, grid, and legend
    plt.title(title)
    plt.tight_layout()

    # Grid
    if grid == True:
        plt.grid(True, linestyle="--", alpha=0.5)

    # Legend
    if legend == True:
        plt.legend()

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None
