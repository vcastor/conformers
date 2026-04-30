import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, r2_score

LIGHT_GRID = {
    'n_estimators': [300, 500, 800],
    'max_depth': [None, 30, 50],
    'min_samples_split': [2, 4],
    'min_samples_leaf': [1, 2],
    'max_features': ['sqrt', 'log2', None],
    'bootstrap': [True, False],
}

ROBUST_GRID = {
    'n_estimators': [200, 400, 600, 800, 1200, 1600, 2000, 3000],
    'max_depth': [None, 10, 20, 30, 50, 70, 100],
    'min_samples_split': [2, 3, 4, 5, 8, 10],
    'min_samples_leaf': [1, 2, 3, 4, 6, 8],
    'max_features': ['sqrt', 'log2', 0.3, 0.5, 0.7, None],
    'bootstrap': [True, False],
    'criterion': ['squared_error', 'absolute_error', 'friedman_mse'],
}

def _find_best(X, y, robust, search_seed=42):
    X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.2, random_state=search_seed)
    base = RandomForestRegressor(random_state=42)
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
    print(f'Random Forest best params: {best_params}')

    y_tests, y_preds, maes, r2s, importances = [], [], [], [], []
    for seed in range(n_splits):
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)
        m = RandomForestRegressor(random_state=42, n_jobs=-1, **best_params)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        y_tests.append(np.asarray(y_te))
        y_preds.append(y_pred)
        maes.append(mean_absolute_error(y_te, y_pred))
        r2s.append(r2_score(y_te, y_pred))
        importances.append(m.feature_importances_)

    if feature_names is not None:
        imp = np.array(importances)
        mean_imp = imp.mean(axis=0)
        std_imp  = imp.std(axis=0)
        order    = np.argsort(mean_imp)[::-1]

        plt.figure(figsize=(12, 7))
        plt.title(f'RF Feature Importances ({n_splits} splits)', fontsize=20)
        plt.bar(range(len(mean_imp)), mean_imp[order],
                yerr=std_imp[order], align='center', capsize=4)
        plt.xticks(range(len(mean_imp)),
                   [feature_names[i] for i in order], rotation=90, fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()
        plt.savefig(f'importances_{"robust" if robust else "light"}.pdf')
        plt.close()

    return y_tests, y_preds, maes, r2s, 'Random Forest'

