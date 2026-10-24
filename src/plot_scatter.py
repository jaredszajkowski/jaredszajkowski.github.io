import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np
import pandas as pd

from matplotlib.ticker import FuncFormatter, MultipleLocator, PercentFormatter
from run_regression import run_regression

from round_to_nice_value import round_to_nice_value


def plot_scatter(
    df: pd.DataFrame,
    x_plot_column: str,
    y_plot_columns: list,
    title: str,
    x_label: str,
    x_format: str,
    x_format_decimal_places: int | str,
    x_tick_spacing: int | float | str,
    x_tick_start: str,
    x_tick_rotation: int,
    y_label: str,
    y_format: str,
    y_format_decimal_places: int | str,
    y_tick_spacing: int | float | str,
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
    legend_location: str = "best",
    legend_anchor: tuple = None,
    export_plot: bool = False,
    plot_file_name: str = None,
    caption: str = None,
) -> None:
    """
    Plot one or more columns of a DataFrame against another column as a scatter
    plot, with optional regression lines.

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
        Format for the x-axis labels: "Decimal", "Percentage", "Scientific", or
        "Log" for numeric data; "Second", "Minute", "Hour", "Day", "Week",
        "Month", or "Year" for dates; or "String" for no formatting.
    x_format_decimal_places : int OR str
        Number of decimal places for x-axis labels, or "Auto" to infer it from
        the x-axis tick spacing. Used only by the numeric formats.
    x_tick_spacing : int OR float OR str
        Spacing for the x-axis ticks, or "Auto" to derive it from the range of
        the x-axis data. "Auto" applies to "Decimal", "Percentage", and
        "Scientific" only; date formats need an explicit interval. Ignored
        when x_format is "Log" or "String".
    x_tick_start : str
        Start date for the x-axis ticks.
    x_tick_rotation : int
        Rotation angle for the x-axis tick labels.
    y_label : str
        Label for the y-axis.
    y_format : str
        Format for the y-axis labels: "Decimal", "Percentage", "Scientific", or
        "Log".
    y_format_decimal_places : int OR str
        Number of decimal places for y-axis labels, or "Auto" to infer it from
        the y-axis tick spacing.
    y_tick_spacing : int OR float OR str
        Spacing for the y-axis ticks, or "Auto" to derive it from the range of
        the plotted data. Ignored when y_format is "Log".
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
    legend_location : str, optional
        Location of the legend on the plot (default is "best").
    legend_anchor : tuple, optional
        Anchor point (x, y) for placing the legend relative to the axes,
        e.g. (1, 1) to move it outside the plot (default is None).
    export_plot : bool, optional
        Whether to save the figure as a PNG file (default is False).
    plot_file_name : str, optional
        File name for saving the figure (if export_plot is True, default is None).
    caption : str, optional
        Caption drawn centered below the figure, e.g. "Figure 1" (default is
        None).

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

    if x_format_decimal_places == "Auto":
        if isinstance(x_tick_spacing, float):
            x_tick_spacing_decimal_places = max(
                0, -int(math.floor(math.log10(abs(x_tick_spacing))))
            )
        else:
            x_tick_spacing_decimal_places = 0

        # PercentFormatter shows the value x 100, which needs 2 fewer decimals
        if x_format == "Percentage":
            x_tick_spacing_decimal_places = max(0, x_tick_spacing_decimal_places - 2)

        x_format_decimal_places = x_tick_spacing_decimal_places

    # Format X axis
    if x_format == "Decimal":
        plt.gca().xaxis.set_major_formatter(
            FuncFormatter(lambda x, _: f"{x:,.{x_format_decimal_places}f}")
        )
    elif x_format == "Percentage":
        plt.gca().xaxis.set_major_formatter(
            PercentFormatter(xmax=1, decimals=x_format_decimal_places)
        )
    elif x_format == "Scientific":
        plt.gca().xaxis.set_major_formatter(
            FuncFormatter(lambda x, _: f"{x:.{x_format_decimal_places}e}")
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

    # Date formats set their own locators above, and linear tick spacing would
    # override the log locator
    if x_format in ("Decimal", "Percentage", "Scientific"):
        plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
    plt.xlabel(x_label)

    if x_tick_rotation != 0:
        # Line up the x-ticks with the labels when rotated
        plt.xticks(rotation=x_tick_rotation, ha="right")
    else:
        plt.xticks(rotation=x_tick_rotation)

    # Format Y axis
    if y_tick_spacing == "Auto":
        max_value = -math.inf
        min_value = math.inf
        for col in y_plot_columns:
            if df[col].max() > max_value:
                max_value = df[col].max()

            if df[col].min() < min_value:
                min_value = df[col].min()

        raw_y_spacing = (max_value - min_value) / 10
        y_tick_spacing = round_to_nice_value(raw_y_spacing)

    if y_format_decimal_places == "Auto":
        if isinstance(y_tick_spacing, float):
            y_tick_spacing_decimal_places = max(
                0, -int(math.floor(math.log10(abs(y_tick_spacing))))
            )
        else:
            y_tick_spacing_decimal_places = 0

        # PercentFormatter shows the value x 100, which needs 2 fewer decimals
        if y_format == "Percentage":
            y_tick_spacing_decimal_places = max(0, y_tick_spacing_decimal_places - 2)

        y_format_decimal_places = y_tick_spacing_decimal_places

    if y_format == "Decimal":
        plt.gca().yaxis.set_major_formatter(
            FuncFormatter(lambda x, _: f"{x:,.{y_format_decimal_places}f}")
        )
    elif y_format == "Percentage":
        plt.gca().yaxis.set_major_formatter(
            PercentFormatter(xmax=1, decimals=y_format_decimal_places)
        )
    elif y_format == "Scientific":
        plt.gca().yaxis.set_major_formatter(
            FuncFormatter(lambda x, _: f"{x:.{y_format_decimal_places}e}")
        )
    elif y_format == "Log":
        plt.yscale("log")
    else:
        raise ValueError(
            f"Unrecognized y_format: {y_format}. Use 'Decimal', 'Percentage', 'Scientific', or 'Log'."
        )

    # Linear tick spacing would override the log locator
    if y_format != "Log":
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
        # Score on the same rows the model was fit on (run_regression drops NaN)
        scored = df[[x_plot_column, OLS_column]].dropna()
        r_squared = model.score(scored[[x_plot_column]], scored[OLS_column])
        plt.plot(
            X_vals,
            Y_vals,
            color="red",
            linestyle="--",
            label=f"OLS Fit: y = {intercept:.1f} + {slope:.2f}x (R² = {r_squared:.2f})",
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
        # Score on the same rows the model was fit on (run_regression drops NaN)
        scored = df[[x_plot_column, Ridge_column]].dropna()
        r_squared = model.score(scored[[x_plot_column]], scored[Ridge_column])
        plt.plot(
            X_vals,
            Y_vals,
            color="blue",
            linestyle="--",
            label=f"Ridge Fit (α={alpha_value:.2f}): y = {intercept:.1f} + {slope:.2f}x (R² = {r_squared:.2f})",
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
        # Score on the same rows the model was fit on (run_regression drops NaN)
        scored = df[[x_plot_column, RidgeCV_column]].dropna()
        r_squared = model.score(scored[[x_plot_column]], scored[RidgeCV_column])
        plt.plot(
            X_vals,
            Y_vals,
            color="green",
            linestyle="--",
            label=f"RidgeCV Fit (α={alpha_value:.2f}): y = {intercept:.1f} + {slope:.2f}x (R² = {r_squared:.2f})",
        )

    # Format title, layout, grid, and legend
    plt.title(title)
    plt.tight_layout()

    # Grid
    if grid == True:
        plt.grid(True, linestyle="--", alpha=0.5)

    # Legend
    if legend == True:
        if legend_anchor is not None:
            plt.legend(loc=legend_location, bbox_to_anchor=legend_anchor)
        else:
            plt.legend(loc=legend_location)

    # Caption
    if caption is not None:
        plt.gcf().text(0.5, 0, caption, ha="center", va="top", fontsize=9)

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None
