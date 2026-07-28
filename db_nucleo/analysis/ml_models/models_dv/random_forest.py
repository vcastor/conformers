import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
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

def _optuna_search(X_tr, y_tr, n_trials=300):
    from sklearn.model_selection import cross_val_score
    def objective(trial):
        max_d = trial.suggest_categorical('max_depth', [None, 5, 10, 20, 40, 80])
        mf    = trial.suggest_categorical('max_features', ['sqrt', 'log2', 0.3, 0.5, 0.7, None])
        crit  = trial.suggest_categorical('criterion',
                    ['squared_error', 'absolute_error', 'friedman_mse'])
        params = {
            'n_estimators':      trial.suggest_int('n_estimators', 100, 4000),
            'max_depth':         max_d,
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
            'min_samples_leaf':  trial.suggest_int('min_samples_leaf', 1, 15),
            'max_features':      mf,
            'criterion':         crit,
            'bootstrap':         trial.suggest_categorical('bootstrap', [True, False]),
        }
        m = RandomForestRegressor(random_state=42, n_jobs=1, **params)
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

    base = RandomForestRegressor(random_state=42)
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
    best_params = _find_best(X, y, robust)
    print(f'Random Forest best params: {best_params}')

    indices = np.arange(len(X))
    y_tests, y_preds, test_idxs, maes, r2s, importances = [], [], [], [], [], []
    for seed in range(n_splits):
        tr, te = train_test_split(indices, test_size=0.2, random_state=seed)
        X_tr, X_te = X.iloc[tr], X.iloc[te]
        y_tr, y_te = y.iloc[tr], y.iloc[te]
        m = RandomForestRegressor(random_state=42, n_jobs=10, **best_params)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        y_tests.append(np.asarray(y_te))
        y_preds.append(y_pred)
        test_idxs.append(np.asarray(te))
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
        plt.savefig(f'importances_{tag}.pdf')
        plt.close()

    return y_tests, y_preds, test_idxs, maes, r2s, 'Random Forest'
