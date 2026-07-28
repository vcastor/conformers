import numpy as np
from sklearn.model_selection import (
    train_test_split, GridSearchCV, RandomizedSearchCV, KFold, RepeatedKFold,
)
from sklearn.metrics import mean_absolute_error, r2_score

try:
    import xgboost as xgb_mod
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    HAS_OPTUNA = True
except ImportError:
    HAS_OPTUNA = False

LIGHT_GRID = {
    'n_estimators': [100, 300, 600],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'max_depth': [3, 5, 7],
    'subsample': [0.7, 1.0],
    'colsample_bytree': [0.7, 1.0],
    'reg_alpha': [0, 0.1, 1.0],
    'reg_lambda': [0.5, 1.0, 2.0],
}

ROBUST_GRID = {
    'n_estimators': [200, 500, 1000, 2000, 4000],
    'learning_rate': [0.005, 0.01, 0.02, 0.05, 0.1, 0.2],
    'max_depth': [2, 3, 4, 5, 7, 10],
    'subsample': [0.5, 0.6, 0.7, 0.8, 1.0],
    'colsample_bytree': [0.4, 0.5, 0.7, 0.8, 1.0],
    'colsample_bylevel': [0.4, 0.6, 0.8, 1.0],
    'min_child_weight': [1, 3, 5, 10, 20],
    'reg_alpha': [0.0, 0.01, 0.1, 1.0, 10.0],
    'reg_lambda': [0.1, 0.5, 1.0, 5.0, 10.0],
    'gamma': [0.0, 0.1, 0.5, 1.0, 2.0],
}


def _optuna_search(X_tr, y_tr, n_trials=300):
    from sklearn.model_selection import cross_val_score
    def objective(trial):
        params = {
            'n_estimators':      trial.suggest_int('n_estimators', 50, 5000),
            'learning_rate':     trial.suggest_float('learning_rate', 1e-3, 0.5, log=True),
            'max_depth':         trial.suggest_int('max_depth', 2, 12),
            'subsample':         trial.suggest_float('subsample', 0.4, 1.0),
            'colsample_bytree':  trial.suggest_float('colsample_bytree', 0.3, 1.0),
            'colsample_bylevel': trial.suggest_float('colsample_bylevel', 0.3, 1.0),
            'min_child_weight':  trial.suggest_int('min_child_weight', 1, 40),
            'reg_alpha':         trial.suggest_float('reg_alpha', 1e-8, 50.0, log=True),
            'reg_lambda':        trial.suggest_float('reg_lambda', 1e-8, 50.0, log=True),
            'gamma':             trial.suggest_float('gamma', 0.0, 10.0),
        }
        m = xgb_mod.XGBRegressor(random_state=42, n_jobs=1, verbosity=0, **params)
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

    base = xgb_mod.XGBRegressor(random_state=42, n_jobs=10, verbosity=0)
    if robust:
        cv = RepeatedKFold(n_splits=5, n_repeats=2, random_state=42)
        search = RandomizedSearchCV(
            base, ROBUST_GRID, n_iter=800, cv=cv,
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
    if not HAS_XGB:
        print('[XGBoost] package not installed — skipping.')
        return [], [], [], [np.inf], [0.0], 'XGBoost'

    best_params = _find_best(X, y, robust)
    print(f'XGBoost best params: {best_params}')

    indices = np.arange(len(X))
    y_tests, y_preds, test_idxs, maes, r2s = [], [], [], [], []
    for seed in range(n_splits):
        tr, te = train_test_split(indices, test_size=0.2, random_state=seed)
        X_tr, X_te = X.iloc[tr], X.iloc[te]
        y_tr, y_te = y.iloc[tr], y.iloc[te]
        m = xgb_mod.XGBRegressor(random_state=42, n_jobs=10, verbosity=0, **best_params)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        y_tests.append(np.asarray(y_te))
        y_preds.append(y_pred)
        test_idxs.append(np.asarray(te))
        maes.append(mean_absolute_error(y_te, y_pred))
        r2s.append(r2_score(y_te, y_pred))

    return y_tests, y_preds, test_idxs, maes, r2s, 'XGBoost'
