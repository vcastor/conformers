#!/usr/bin/python3
from data_loader import load_data
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (
    RBF, DotProduct, RationalQuadratic, ExpSineSquared, Matern, WhiteKernel,
    ConstantKernel as C
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

def run_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    kernels = {
        'RBF': C(1.0)*RBF(length_scale=1.0),
        'DotProduct': C(1.0)*DotProduct(sigma_0=1.0),
        'RationalQuadratic': C(1.0)*RationalQuadratic(alpha=1.0, length_scale=1.0),
        'Matern_3/2': C(1.0)*Matern(length_scale=1.0, nu=1.5),
        'Matern_5/2': C(1.0)*Matern(length_scale=1.0, nu=2.5),
        'ExpSineSquared': C(1.0)*ExpSineSquared(length_scale=1.0, periodicity=3.0),
        'RBF+White': C(1.0)*RBF(length_scale=1.0) + WhiteKernel()
    }
    best_score = float('inf')
    best_model = None
    best_kernel = ''

    for name, kernel in kernels.items():
        model = GaussianProcessRegressor(kernel=kernel, random_state=42)
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)

            if mae < best_score:
                best_score = mae
                best_model = model
                best_kernel = name
        except Exception as e:
            continue

    y_pred = best_model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    label = f'Gaussion Process'
    print(f'Gaussian Process with {best_kernel} kernel')

    return y_test, y_pred, best_score, r2, label

