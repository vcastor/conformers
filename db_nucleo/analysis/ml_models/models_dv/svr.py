import numpy as np
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, r2_score

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

def _find_best(X, y, robust, search_seed=42):
    X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.2, random_state=search_seed)
    if robust:
        search = RandomizedSearchCV(
            _build(), ROBUST_GRID, n_iter=500, cv=5,
            scoring='neg_mean_absolute_error', n_jobs=-1,
            random_state=42, verbose=0,
        )
    else:
        search = GridSearchCV(
            _build(), LIGHT_GRID, cv=5,
            scoring='neg_mean_absolute_error', n_jobs=-1, verbose=0,
        )
    search.fit(X_tr, y_tr)
    return search.best_params_

def run_model(X, y, n_splits=30, robust=False, feature_names=None):
    best_params = _find_best(X, y, robust)
    print(f'SVR best params: {best_params}')

    y_tests, y_preds, maes, r2s = [], [], [], []
    for seed in range(n_splits):
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)
        m = _build()
        m.set_params(**best_params)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        y_tests.append(np.asarray(y_te))
        y_preds.append(y_pred)
        maes.append(mean_absolute_error(y_te, y_pred))
        r2s.append(r2_score(y_te, y_pred))

    return y_tests, y_preds, maes, r2s, 'SVR'

