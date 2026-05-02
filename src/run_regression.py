import numpy as np
import pandas as pd
import statsmodels.api as sm

from sklearn.linear_model import (
    LinearRegression, 
    LogisticRegression, 
    LogisticRegressionCV,
    Ridge, 
    RidgeCV,
)


def run_regression(
    df: pd.DataFrame,
    x_plot_column: str,
    y_plot_column: str,
    regression_model: str,
    regression_constant: bool,
    ridge_alpha: float = None,
    logistic_C: float = 1.0,
    logistic_max_iter: int = 1000,
    logistic_solver: str = "lbfgs",
    logistic_cv_Cs: int = 10,
) -> (
    LinearRegression
    | Ridge
    | RidgeCV
    | LogisticRegression
    | LogisticRegressionCV
    | sm.regression.linear_model.RegressionResultsWrapper
):
    """
    Run a linear regression on the specified DataFrame columns, model, 
    and constant.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data to fit.
    x_plot_column : str
        Column to use as the feature (X) from the DataFrame.
    y_plot_column : str
        Column to use as the target (y) from the DataFrame.
    regression_model : str
        Type of regression model to use. One of:
            "OLS-statsmodels", "OLS-sklearn", "Ridge", "RidgeCV",
            "Logistic", "LogisticCV".
    regression_constant : bool
        Whether to include a constant/intercept term in the model.
    ridge_alpha : float, optional
        Alpha value for Ridge regression. Required if regression_model is "Ridge".
    logistic_C : float, optional
        Inverse of regularization strength for LogisticRegression. Smaller
        values produce stronger regularization. Default is 1.0.
    logistic_max_iter : int, optional
        Maximum number of iterations for the solver. Default is 1000.
    logistic_solver : str, optional
        Solver algorithm for LogisticRegression and LogisticRegressionCV.
        Default is "lbfgs". Other options: "liblinear", "saga", "newton-cg".
    logistic_cv_Cs : int, optional
        Number of C values to try in LogisticRegressionCV, spaced
        logarithmically. Default is 10.

    Returns
    -------
    model : LinearRegression | Ridge | RidgeCV | LogisticRegression
            | LogisticRegressionCV | RegressionResultsWrapper
        The fitted regression model.

    Notes
    -----
    Logistic models expect a binary (0/1) or multiclass integer target column.
    They are classification models, not regression models, so the interpretation
    of coefficients differs from the linear models above.
    """

    # Align X and y (common to all models)
    data = df[[x_plot_column, y_plot_column]].dropna()
    X = data[[x_plot_column]]
    y = data[y_plot_column]

    if regression_model == "OLS-statsmodels":
        if regression_constant:
            X_sm = sm.add_constant(X)
        else:
            X_sm = X
        model = sm.OLS(y, X_sm).fit()

    elif regression_model == "OLS-sklearn":
        model = LinearRegression(fit_intercept=regression_constant)
        model.fit(X, y)

    elif regression_model == "Ridge":
        model = Ridge(alpha=ridge_alpha, fit_intercept=regression_constant)
        model.fit(X, y)

    elif regression_model == "RidgeCV":
        alphas = np.logspace(-2, 1, 50)  # 50 values, 0.01 to 10
        model = RidgeCV(alphas=alphas, cv=5, fit_intercept=regression_constant)
        model.fit(X, y)

    elif regression_model == "Logistic":
        model = LogisticRegression(
            C=logistic_C,
            fit_intercept=regression_constant,
            max_iter=logistic_max_iter,
            solver=logistic_solver,
        )
        model.fit(X, y)

    elif regression_model == "LogisticCV":
        # Cs can be an int (number of log-spaced values) or an explicit array;
        # passing the int is the idiomatic sklearn approach here.
        model = LogisticRegressionCV(
            Cs=logistic_cv_Cs,
            fit_intercept=regression_constant,
            max_iter=logistic_max_iter,
            solver=logistic_solver,
            cv=5,
        )
        model.fit(X, y)

    else:
        raise ValueError(
            f"Unrecognized regression_model: '{regression_model}'. "
            "Supported models: 'OLS-statsmodels', 'OLS-sklearn', 'Ridge', "
            "'RidgeCV', 'Logistic', 'LogisticCV'."
        )

    return model
