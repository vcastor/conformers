import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (
    RBF, DotProduct, RationalQuadratic, Matern, WhiteKernel,
    ConstantKernel as C,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

LIGHT_KERNELS = {
    'RBF':         C(1.0)*RBF(length_scale=1.0),
    'Matern_3/2':  C(1.0)*Matern(length_scale=1.0, nu=1.5),
    'Matern_5/2':  C(1.0)*Matern(length_scale=1.0, nu=2.5),
    'RBF+White':   C(1.0)*RBF(length_scale=1.0)+WhiteKernel(),
}

def _robust_kernels(n_features):
    # anisotropic = per-feature length scales optimised by GPR's marginal-likelihood
    ls = np.ones(n_features)
    return {
        'RBF_aniso':                C(1.0)*RBF(length_scale=ls),
        'RBF_aniso+White':          C(1.0)*RBF(length_scale=ls)+WhiteKernel(),
        'Matern_3/2_aniso':         C(1.0)*Matern(length_scale=ls, nu=1.5),
        'Matern_5/2_aniso':         C(1.0)*Matern(length_scale=ls, nu=2.5),
        'Matern_3/2_aniso+White':   C(1.0)*Matern(length_scale=ls, nu=1.5)+WhiteKernel(),
        'Matern_5/2_aniso+White':   C(1.0)*Matern(length_scale=ls, nu=2.5)+WhiteKernel(),
        'RationalQuadratic':        C(1.0)*RationalQuadratic(alpha=1.0, length_scale=1.0),
        'RQ+White':                 C(1.0)*RationalQuadratic(alpha=1.0, length_scale=1.0)+WhiteKernel(),
        'DotProduct':               C(1.0)*DotProduct(sigma_0=1.0),
        'RBF_aniso*Dot':            C(1.0)*RBF(length_scale=ls)*DotProduct(sigma_0=1.0),
        'Matern52_aniso*Dot+White': C(1.0)*Matern(length_scale=ls, nu=2.5)*DotProduct(sigma_0=1.0)+WhiteKernel(),
        'RBF_aniso+Matern52_aniso': C(1.0)*RBF(length_scale=ls)+C(1.0)*Matern(length_scale=ls, nu=2.5),
    }

def _build(kernel, n_restarts):
    return make_pipeline(
        StandardScaler(),
        GaussianProcessRegressor(
            kernel=kernel, alpha=1e-6, normalize_y=True,
            n_restarts_optimizer=n_restarts, random_state=42,
        ),
    )

def _find_best(X, y, robust, search_seed=42):
    n_features = X.shape[1]
    kernels    = _robust_kernels(n_features) if robust else LIGHT_KERNELS
    n_restarts = 15 if robust else 3
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=search_seed)
    best_name, best_kernel, best_mae = None, None, np.inf
    for name, kern in kernels.items():
        m = _build(kern, n_restarts)
        m.fit(X_tr, y_tr)
        mae = mean_absolute_error(y_te, m.predict(X_te))
        if mae < best_mae:
            best_mae, best_name, best_kernel = mae, name, kern
    return best_name, best_kernel, n_restarts

def run_model(X, y, n_splits=30, robust=False, feature_names=None, tag=''):
    best_name, best_kernel, n_restarts = _find_best(X, y, robust)
    print(f'GPR best kernel: {best_name}')

    indices = np.arange(len(X))
    y_tests, y_preds, test_idxs, maes, r2s = [], [], [], [], []
    for seed in range(n_splits):
        tr, te = train_test_split(indices, test_size=0.2, random_state=seed)
        X_tr, X_te = X.iloc[tr], X.iloc[te]
        y_tr, y_te = y.iloc[tr], y.iloc[te]
        m = _build(best_kernel, n_restarts)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        y_tests.append(np.asarray(y_te))
        y_preds.append(y_pred)
        test_idxs.append(np.asarray(te))
        maes.append(mean_absolute_error(y_te, y_pred))
        r2s.append(r2_score(y_te, y_pred))

    return y_tests, y_preds, test_idxs, maes, r2s, 'GPR'
