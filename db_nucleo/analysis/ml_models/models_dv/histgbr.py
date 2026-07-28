import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import (
    train_test_split, GridSearchCV, RandomizedSearchCV, KFold, RepeatedKFold,
)
from sklearn.metrics import mean_absolute_error, r2_score

try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    HAS_OPTUNA = True
except ImportError:
    HAS_OPTUNA = False

LIGHT_GRID = {
    'max_iter': [200, 500, 1000],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [None, 5, 10],
    'max_leaf_nodes': [31, 63, 127],
    'min_samples_leaf': [10, 20, 40],
    'l2_regularization': [0.0, 0.01, 0.1],
}

ROBUST_GRID = {
    'max_iter': [200, 500, 1000, 2000, 5000],
    'learning_rate': [0.005, 0.01, 0.02, 0.05, 0.1, 0.2],
    'max_depth': [None, 3, 5, 8, 12, 20],
    'max_leaf_nodes': [15, 31, 63, 127, 255, 511],
    'min_samples_leaf': [5, 10, 20, 40, 80],
    'l2_regularization': [0.0, 0.001, 0.01, 0.1, 1.0, 5.0],
    'max_bins': [64, 128, 255],
}


def _optuna_search(X_tr, y_tr, n_trials=300):
    from sklearn.model_selection import cross_val_score
    def objective(trial):
        max_d  = trial.suggest_categorical('max_depth', [None, 3, 5, 8, 12, 20, 30])
        params = {
            'max_iter':          trial.suggest_int('max_iter', 50, 6000),
            'learning_rate':     trial.suggest_float('learning_rate', 1e-3, 0.5, log=True),
            'max_depth':         max_d,
            'max_leaf_nodes':    trial.suggest_int('max_leaf_nodes', 10, 600),
            'min_samples_leaf':  trial.suggest_int('min_samples_leaf', 2, 120),
            'l2_regularization': trial.suggest_float('l2_regularization', 0.0, 20.0),
            'max_bins':          trial.suggest_categorical('max_bins', [64, 128, 255]),
        }
        m = HistGradientBoostingRegressor(random_state=42, **params)
        cv = RepeatedKFold(n_splits=5, n_repeats=3, random_state=42)
        scores = cross_val_score(m, X_tr, y_tr, cv=cv,
                                 scoring='neg_mean_absolute_error', n_jobs=10)
        return -scores.mean()

    study = optuna.create_study(
        direction='minimize',
        sampler=optuna.samplers.TPESampler(seed=42),
    )
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return study.best_params


def _find_best(X, y, robust, search_seed=42):
    X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.2, random_state=search_seed)

    if robust and HAS_OPTUNA:
        return _optuna_search(X_tr, y_tr, n_trials=300)

    base = HistGradientBoostingRegressor(random_state=42)
    if robust:
        cv = RepeatedKFold(n_splits=5, n_repeats=2, random_state=42)
        search = RandomizedSearchCV(
            base, ROBUST_GRID, n_iter=600, cv=cv,
            scoring='neg_mean_absolute_error', n_jobs=10,
            random_state=42, verbose=0,
        )
    else:
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        search = GridSearchCV(
            base, LIGHT_GRID, cv=cv,
            scoring='neg_mean_absolute_error', n_jobs=10, verbose=0,
        )
    search.fit(X_tr, y_tr)
    return search.best_params_


def run_model(X, y, n_splits=30, robust=False, feature_names=None, tag=''):
    best_params = _find_best(X, y, robust)
    print(f'HistGBR best params: {best_params}')

    indices = np.arange(len(X))
    y_tests, y_preds, test_idxs, maes, r2s = [], [], [], [], []
    for seed in range(n_splits):
        tr, te = train_test_split(indices, test_size=0.2, random_state=seed)
        X_tr, X_te = X.iloc[tr], X.iloc[te]
        y_tr, y_te = y.iloc[tr], y.iloc[te]
        m = HistGradientBoostingRegressor(random_state=42, **best_params)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        y_tests.append(np.asarray(y_te))
        y_preds.append(y_pred)
        test_idxs.append(np.asarray(te))
        maes.append(mean_absolute_error(y_te, y_pred))
        r2s.append(r2_score(y_te, y_pred))

    return y_tests, y_preds, test_idxs, maes, r2s, 'HistGBR'
