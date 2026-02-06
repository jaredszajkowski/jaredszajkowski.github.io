import numpy as np
import pandas as pd
import statsmodels.api as sm

from sklearn.linear_model import LinearRegression, Ridge, RidgeCV

def run_linear_regression(
    df: pd.DataFrame,
    x_plot_column: str,
    y_plot_column: str,
    regression_model: str,
    regression_constant: bool,
    ridge_alpha: float = None,
) -> LinearRegression | Ridge | RidgeCV | sm.regression.linear_model.RegressionResultsWrapper:
    """
    Run a linear regression on the specified DataFrame columns, model, and constant.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the price data to plot.
    x_plot_column : str
        Column to plot on the x-axis from the DataFrame.
    y_plot_column : str
        Column to plot on the y-axis from the DataFrame.
    regression_model : str
        Type of regression model to use ("OLS-statsmodels", "OLS-sklearn", "Ridge", or "RidgeCV").
    regression_constant : bool
        Whether to include a constant term in the regression model.
    ridge_alpha : float, optional
        Alpha value for Ridge regression. Required if regression_model is "Ridge".
    
    Returns
    -------
    model : LinearRegression | Ridge | RidgeCV | RegressionResultsWrapper
        The fitted regression model.
    """

    # Align X and y (common to both models)
    data = df[[x_plot_column, y_plot_column]].dropna()
    X = data[[x_plot_column]]
    y = data[y_plot_column]

    if regression_model == "OLS-statsmodels":
        # Add constant if requested
        if regression_constant:
            X_sm = sm.add_constant(X)
        else:
            X_sm = X
        
        # Fit OLS regression model
        model = sm.OLS(y, X_sm).fit()
    
    elif regression_model == "OLS-sklearn":
        # Fit OLS regression model
        model = LinearRegression(fit_intercept=regression_constant)
        model.fit(X, y)

    elif regression_model == "Ridge":
        # Fit Ridge regression model with fixed alpha
        model = Ridge(alpha=ridge_alpha, fit_intercept=regression_constant)
        model.fit(X, y)
    
    elif regression_model == "RidgeCV":
        # Fit Ridge regression model with automatic alpha selection via CV
        alphas = np.logspace(-2, 1, 50)  # 50 values, 0.01 to 10
        model = RidgeCV(alphas=alphas, cv=5, fit_intercept=regression_constant)
        model.fit(X, y)

    else:
        raise ValueError(
            f"Unrecognized regression_model: {regression_model}. "
            "Currently, only 'OLS-statsmodels', 'OLS-sklearn', 'Ridge', and 'RidgeCV' are supported."
        )

    return model