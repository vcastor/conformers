import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import (
    train_test_split, GridSearchCV, RandomizedSearchCV, KFold, RepeatedKFold,
)
from sklearn.metrics import mean_absolute_error, r2_score

LIGHT_GRID = [
    {
        'mlpregressor__solver': ['adam'],
        'mlpregressor__hidden_layer_sizes': [(100,), (200,), (200,100), (300,200,100)],
        'mlpregressor__activation': ['relu', 'tanh'],
        'mlpregressor__alpha': [1e-4, 1e-3, 1e-2],
        'mlpregressor__learning_rate_init': [1e-3, 5e-3],
    },
    {
        'mlpregressor__solver': ['lbfgs'],
        'mlpregressor__hidden_layer_sizes': [(100,), (200,), (200,100), (300,200,100)],
        'mlpregressor__activation': ['relu', 'tanh'],
        'mlpregressor__alpha': [1e-4, 1e-3, 1e-2],
    },
]

ROBUST_GRID = {
    'mlpregressor__solver': ['adam', 'lbfgs'],
    'mlpregressor__hidden_layer_sizes': [
        (50,), (100,), (200,), (300,), (500,), (800,),
        (200,100), (300,200), (500,200), (500,300),
        (300,200,100), (500,300,100), (500,300,200,100),
        (300,300,300), (200,200,200,200),
    ],
    'mlpregressor__activation': ['relu', 'tanh', 'logistic'],
    'mlpregressor__alpha': [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
    'mlpregressor__learning_rate_init': [1e-4, 5e-4, 1e-3, 5e-3, 1e-2],
    'mlpregressor__batch_size': [16, 32, 64, 'auto'],
    'mlpregressor__beta_1': [0.85, 0.9, 0.95],
    'mlpregressor__beta_2': [0.99, 0.999, 0.9999],
}

def _build():
    return make_pipeline(
        StandardScaler(),
        MLPRegressor(max_iter=20000, random_state=42,
                     early_stopping=True, n_iter_no_change=25,
                     validation_fraction=0.1),
    )

def _find_best(X, y, robust, search_seed=42):
    X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.2, random_state=search_seed)
    if robust:
        cv = RepeatedKFold(n_splits=5, n_repeats=2, random_state=42)
        search = RandomizedSearchCV(
            _build(), ROBUST_GRID, n_iter=800, cv=cv,
            scoring='neg_mean_absolute_error', n_jobs=-1,
            random_state=42, verbose=0,
        )
    else:
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        search = GridSearchCV(
            _build(), LIGHT_GRID, cv=cv,
            scoring='neg_mean_absolute_error', n_jobs=-1, verbose=0,
        )
    search.fit(X_tr, y_tr)
    return search.best_params_

def run_model(X, y, n_splits=30, robust=False, feature_names=None, tag=''):
    best_params = _find_best(X, y, robust)
    print(f'MLP best params: {best_params}')

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

    return y_tests, y_preds, test_idxs, maes, r2s, 'MLP NN'
