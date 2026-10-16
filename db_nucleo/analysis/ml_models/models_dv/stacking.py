import numpy as np
from sklearn.ensemble import (
    StackingRegressor, RandomForestRegressor, ExtraTreesRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.svm import SVR
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


def _build_base_models():
    estimators = [
        ('rf',   RandomForestRegressor(
                     n_estimators=600, max_features='sqrt',
                     random_state=42, n_jobs=1)),
        ('et',   ExtraTreesRegressor(
                     n_estimators=600, max_features='sqrt',
                     random_state=42, n_jobs=1)),
        ('hgbr', HistGradientBoostingRegressor(
                     max_iter=600, learning_rate=0.05,
                     max_leaf_nodes=63, random_state=42)),
        ('svr',  make_pipeline(StandardScaler(),
                               SVR(C=20, epsilon=0.05, kernel='rbf'))),
    ]
    try:
        import xgboost as xgb
        estimators.append(
            ('xgb', xgb.XGBRegressor(
                n_estimators=600, learning_rate=0.05, max_depth=5,
                subsample=0.8, colsample_bytree=0.8,
                random_state=42, n_jobs=1, verbosity=0))
        )
    except ImportError:
        pass
    try:
        import lightgbm as lgb
        estimators.append(
            ('lgbm', lgb.LGBMRegressor(
                n_estimators=600, learning_rate=0.05, num_leaves=31,
                random_state=42, n_jobs=1, verbose=-1))
        )
    except ImportError:
        pass
    return estimators


def _find_best_alpha(X, y, robust, search_seed=42):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=search_seed)
    alphas = [0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0] if robust else [0.1, 1.0, 10.0]
    cv_inner = 10 if robust else 5
    best_alpha, best_mae = 1.0, np.inf
    for alpha in alphas:
        stack = StackingRegressor(
            estimators=_build_base_models(),
            final_estimator=Ridge(alpha=alpha),
            cv=cv_inner, n_jobs=-1, passthrough=False,
        )
        stack.fit(X_tr, y_tr)
        mae = mean_absolute_error(y_te, stack.predict(X_te))
        if mae < best_mae:
            best_mae, best_alpha = mae, alpha
    return best_alpha


def run_model(X, y, n_splits=30, robust=False, feature_names=None, tag=''):
    base_names = [name for name, _ in _build_base_models()]
    print(f'Stacking base models: {base_names}')

    best_alpha = _find_best_alpha(X, y, robust)
    print(f'Stacking best Ridge alpha: {best_alpha}')

    cv_stacking = 10 if robust else 5
    indices = np.arange(len(X))
    y_tests, y_preds, test_idxs, maes, r2s = [], [], [], [], []
    for seed in range(n_splits):
        tr, te = train_test_split(indices, test_size=0.2, random_state=seed)
        X_tr, X_te = X.iloc[tr], X.iloc[te]
        y_tr, y_te = y.iloc[tr], y.iloc[te]
        m = StackingRegressor(
            estimators=_build_base_models(),
            final_estimator=Ridge(alpha=best_alpha),
            cv=cv_stacking, n_jobs=-1, passthrough=False,
        )
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        y_tests.append(np.asarray(y_te))
        y_preds.append(y_pred)
        test_idxs.append(np.asarray(te))
        maes.append(mean_absolute_error(y_te, y_pred))
        r2s.append(r2_score(y_te, y_pred))

    return y_tests, y_preds, test_idxs, maes, r2s, 'Stacking'
