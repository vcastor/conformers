import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, r2_score

LIGHT_GRID = {
    'n_estimators': [300, 500, 800],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [3, 5, 8],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2],
    'subsample': [0.8, 1.0],
    'max_features': ['sqrt', 'log2', None],
}

ROBUST_GRID = {
    'n_estimators': [200, 400, 600, 1000, 1500, 2500, 4000],
    'learning_rate': [0.005, 0.01, 0.02, 0.05, 0.1, 0.2],
    'max_depth': [2, 3, 4, 5, 7, 10, 15],
    'min_samples_split': [2, 4, 6, 10, 20],
    'min_samples_leaf': [1, 2, 4, 6, 10],
    'subsample': [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    'max_features': ['sqrt', 'log2', 0.5, 0.7, None],
    'loss': ['squared_error', 'huber', 'absolute_error'],
}

def _find_best(X, y, robust, search_seed=42):
    X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.2, random_state=search_seed)
    base = GradientBoostingRegressor(random_state=42)
    if robust:
        search = RandomizedSearchCV(
            base, ROBUST_GRID, n_iter=500, cv=5,
            scoring='neg_mean_absolute_error', n_jobs=-1,
            random_state=42, verbose=0,
        )
    else:
        search = GridSearchCV(
            base, LIGHT_GRID, cv=5,
            scoring='neg_mean_absolute_error', n_jobs=-1, verbose=0,
        )
    search.fit(X_tr, y_tr)
    return search.best_params_

def run_model(X, y, n_splits=30, robust=False, feature_names=None):
    best_params = _find_best(X, y, robust)
    print(f'GBR best params: {best_params}')

    y_tests, y_preds, maes, r2s = [], [], [], []
    for seed in range(n_splits):
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)
        m = GradientBoostingRegressor(random_state=42, **best_params)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        y_tests.append(np.asarray(y_te))
        y_preds.append(y_pred)
        maes.append(mean_absolute_error(y_te, y_pred))
        r2s.append(r2_score(y_te, y_pred))

    return y_tests, y_preds, maes, r2s, 'GBR'

