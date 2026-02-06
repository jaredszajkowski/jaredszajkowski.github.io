```python
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib.ticker import MultipleLocator, PercentFormatter, FormatStrFormatter

from run_linear_regression import run_linear_regression

def round_to_nice_value(value):
    """Round a value to a 'nice' number for tick spacing (1, 2, 5 × 10^n)."""
    if value <= 0:
        return value

    # Find order of magnitude
    exp = math.floor(math.log10(value))
    magnitude = 10 ** exp

    # Get mantissa (value normalized to [1, 10))
    mantissa = value / magnitude

    # Round mantissa to 1, 2, or 5
    if mantissa <= 1.5:
        nice_mantissa = 1
    elif mantissa <= 3:
        nice_mantissa = 2
    elif mantissa <= 7:
        nice_mantissa = 5
    else:
        nice_mantissa = 10

    return nice_mantissa * magnitude


def plot_scatter(
    df: pd.DataFrame,
    x_plot_column: str,
    y_plot_column: str,
    title: str,
    x_label: str,
    x_format: str,
    x_format_decimal_places: int,
    x_tick_spacing: int,
    x_tick_rotation: int,
    y_label: str,
    y_format: str,
    y_format_decimal_places: int,
    y_tick_spacing: int,
    plot_OLS_regression_line: bool,
    plot_Ridge_regression_line: bool,
    plot_RidgeCV_regression_line: bool,
    regression_constant: bool,
    grid: bool,
    legend: bool,
    export_plot: bool,
    plot_file_name: str,
) -> None:
    """
    Plot the price data from a DataFrame for a specified date range and columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the price data to plot.
    x_plot_column : str
        Column to plot on the x-axis from the DataFrame.
    y_plot_column : str
        Column to plot on the y-axis from the DataFrame.
    title : str
        Title of the plot.
    x_label : str
        Label for the x-axis.
    x_format : str
        Format for the x-axis date labels.
    x_tick_spacing : int
        Spacing for the x-axis ticks.
    x_tick_rotation : int, optional
        Rotation angle for the x-axis tick labels (default: 0).
    y_label : str
        Label for the y-axis.
    y_format : str
        Format for the y-axis labels.
    y_format_decimal_places : int
        Number of decimal places for y-axis labels.
    y_tick_spacing : int
        Spacing for the y-axis ticks.
    plot_OLS_regression_line : bool
        Whether to plot an OLS regression line on the scatter plot.
    plot_Ridge_regression_line : bool
        Whether to plot a Ridge regression line on the scatter plot.
    plot_RidgeCV_regression_line : bool
        Whether to plot a RidgeCV regression line on the scatter plot.
    regression_constant : bool
        Whether to include a constant term in the regression models.
    grid : bool
        Whether to display a grid on the plot.
    legend : bool
        Whether to display a legend on the plot.
    export_plot : bool
        Whether to save the figure as a PNG file.
    plot_file_name : str
        File name for saving the figure (if save_fig is True).
    
    Returns
    -------
    None
    """

    # Set plot figure size and background color
    plt.figure(figsize=(10, 6))

    # Plot data
    plt.scatter(df[x_plot_column], df[y_plot_column])

    # Format X axis
    if x_format == "Decimal":
        plt.gca().xaxis.set_major_formatter(FormatStrFormatter(f"%.{x_format_decimal_places}f"))
    elif x_format == "Percentage":
        plt.gca().xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=x_format_decimal_places))
    elif x_format == "Scientific":
        plt.gca().xaxis.set_major_formatter(FormatStrFormatter(f"%.{x_format_decimal_places}e"))
    elif x_format == "Log":
        plt.xscale("log")
    elif x_format == "String":
        pass  # No special formatting for string x-axis
    else:
        raise ValueError(f"Unrecognized x_format: {x_format}. Use 'Decimal', 'Percentage', or 'Scientific'.")
    
    if x_tick_spacing == "Auto":
        raw_x_spacing = (df[x_plot_column].max() - df[x_plot_column].min()) / 20
        x_tick_spacing = round_to_nice_value(raw_x_spacing)
    else:
        x_tick_spacing = x_tick_spacing

    plt.gca().xaxis.set_major_locator(MultipleLocator(x_tick_spacing))
    plt.xlabel(x_label, fontsize=14)
    plt.xticks(rotation=x_tick_rotation, fontsize=12)

    # Format Y axis
    if y_format == "Decimal":
        plt.gca().yaxis.set_major_formatter(FormatStrFormatter(f"%.{y_format_decimal_places}f"))
    elif y_format == "Percentage":
        plt.gca().yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=y_format_decimal_places))
    elif y_format == "Scientific":
        plt.gca().yaxis.set_major_formatter(FormatStrFormatter(f"%.{y_format_decimal_places}e"))
    elif y_format == "Log":
        plt.yscale("log")
    else:
        raise ValueError(f"Unrecognized y_format: {y_format}. Use 'Decimal', 'Percentage', or 'Scientific'.")
    
    if y_tick_spacing == "Auto":
        raw_y_spacing = (df[y_plot_column].max() - df[y_plot_column].min()) / 10
        y_tick_spacing = round_to_nice_value(raw_y_spacing)
    else:
        y_tick_spacing = y_tick_spacing

    plt.gca().yaxis.set_major_locator(MultipleLocator(y_tick_spacing))
    plt.ylabel(y_label, fontsize=14)
    plt.yticks(fontsize=12)

    if plot_OLS_regression_line == True:

        model = run_linear_regression(
            df=df,
            x_plot_column=x_plot_column,
            y_plot_column=y_plot_column,
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
        plt.plot(X_vals, Y_vals, color="red", linestyle="--", 
                 label=f"OLS Fit: y = {intercept:.1f} + {slope:.2f}x")

    if plot_Ridge_regression_line == True:

        model = run_linear_regression(
            df=df,
            x_plot_column=x_plot_column,
            y_plot_column=y_plot_column,
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
        alpha_value = model.alpha_ if hasattr(model, 'alpha_') else 1.0 
        plt.plot(X_vals, Y_vals, color="blue", linestyle="--", 
             label=f"Ridge Fit (α={alpha_value:.2f}): y = {intercept:.1f} + {slope:.2f}x")
        
    if plot_RidgeCV_regression_line == True:

        model = run_linear_regression(
            df=df,
            x_plot_column=x_plot_column,
            y_plot_column=y_plot_column,
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
        alpha_value = model.alpha_ if hasattr(model, 'alpha_') else 1.0
        plt.plot(X_vals, Y_vals, color="green", linestyle="--", 
             label=f"RidgeCV Fit (α={alpha_value:.2f}): y = {intercept:.1f} + {slope:.2f}x")
  
    # Format title, layout, grid, and legend
    plt.title(title, fontsize=16)
    plt.tight_layout()

    if grid == True:
        plt.grid(True, linestyle='--', alpha=0.7)
    
    if legend == True:
        plt.legend(fontsize=9)

    # Save figure and display plot
    if export_plot == True:
        plt.savefig(f"{plot_file_name}.png", dpi=300, bbox_inches="tight")

    # Display the plot
    plt.show()

    return None
```