from sklearn.linear_model import Ridge
import numpy as np

# Generate some data with noise
X = np.random.randn(100, 1)
y = 5 * X.ravel() + np.random.randn(100) * 0.5  # True slope = 5

# Try different alphas
for alpha in [0.01, 0.1, 1.0, 10.0, 100.0]:
    model = Ridge(alpha=alpha)
    model.fit(X, y)
    print(f"α = {alpha:6.2f}  →  coefficient = {model.coef_[0]:.3f}")

# Output might look like:
# α =   0.01  →  coefficient = 4.987
# α =   0.10  →  coefficient = 4.891
# α =   1.00  →  coefficient = 4.523
# α =  10.00  →  coefficient = 2.841
# α = 100.00  →  coefficient = 0.543