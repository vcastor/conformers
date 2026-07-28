import numpy as np
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
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
    'svr__C': [0.1, 1, 10, 100],
    'svr__epsilon': [0.01, 0.05, 0.1, 0.2],
    'svr__kernel': ['rbf', 'poly'],
    'svr__degree': [2, 3],
    'svr__gamma': ['scale', 'auto'],
}

ROBUST_GRID = {
    'svr__C': [0.05, 0.1, 0.5, 1, 5, 10, 50, 100, 300, 500, 1000, 3000],
    'svr__epsilon': [0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0],
    'svr__kernel': ['rbf', 'poly', 'sigmoid'],
    'svr__degree': [2, 3, 4, 5],
    'svr__gamma': ['scale', 'auto', 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0],
    'svr__coef0': [0.0, 0.1, 0.5, 1.0],
}

def _build():
    return make_pipeline(StandardScaler(), SVR(cache_size=500))


def _optuna_search(X_tr, y_tr, n_trials=300):
    from sklearn.model_selection import cross_val_score
    def objective(trial):
        kernel = trial.suggest_categorical('svr__kernel', ['rbf', 'poly', 'sigmoid'])
        params = {
            'svr__C':       trial.suggest_float('svr__C', 1e-2, 3000.0, log=True),
            'svr__epsilon': trial.suggest_float('svr__epsilon', 1e-4, 2.0, log=True),
            'svr__kernel':  kernel,
            'svr__gamma':   trial.suggest_categorical(
                                'svr__gamma', ['scale', 'auto', 1e-4, 1e-3, 1e-2, 0.1, 1.0]),
        }
        if kernel == 'poly':
            params['svr__degree'] = trial.suggest_int('svr__degree', 2, 5)
            params['svr__coef0']  = trial.suggest_float('svr__coef0', 0.0, 2.0)
        m = _build()
        m.set_params(**params)
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

    if robust:
        cv = RepeatedKFold(n_splits=5, n_repeats=2, random_state=42)
        search = RandomizedSearchCV(
            _build(), ROBUST_GRID, n_iter=800, cv=cv,
            scoring='neg_mean_absolute_error', n_jobs=10,
            random_state=42, verbose=0,
        )
    else:
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        search = GridSearchCV(
            _build(), LIGHT_GRID, cv=cv,
            scoring='neg_mean_absolute_error', n_jobs=10, verbose=0,
        )
    search.fit(X_tr, y_tr)
    return search.best_params_

def run_model(X, y, n_splits=30, robust=False, feature_names=None, tag=''):
    best_params = _find_best(X, y, robust)
    print(f'SVR best params: {best_params}')

    indices = np.arange(len(X))
    y_tests, y_preds, test_idxs, maes, r2s = [], [], [], [], []
    for seed in range(n_splits):
        tr, te = train_test_split(indices, test_size=0.2, random_state=seed)
        X_tr, X_te = X.iloc[tr], X.iloc[te]
        y_tr, y_te = y.iloc[tr], y.iloc[te]
        m = _build()
        m.set_params(**best_params)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        y_tests.append(np.asarray(y_te))
        y_preds.append(y_pred)
        test_idxs.append(np.asarray(te))
        maes.append(mean_absolute_error(y_te, y_pred))
        r2s.append(r2_score(y_te, y_pred))

    return y_tests, y_preds, test_idxs, maes, r2s, 'SVR'
