#!/usr/bin/python3
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score

def run_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = make_pipeline(StandardScaler(), MLPRegressor(max_iter=10000, random_state=42))

    param_grid = {
        'mlpregressor__hidden_layer_sizes': [
            (100,), (200, ), (300,), (200, 100), (300, 200, 100)
        ],
        'mlpregressor__activation': ['relu', 'tanh'],
        'mlpregressor__alpha': [0.0001, 0.001, 0.01],  # L2 regularization
        'mlpregressor__solver': ['adam', 'lbfgs'],  # Could try 'lbfgs' for small data
        'mlpregressor__learning_rate': ['constant', 'adaptive']
    }

    grid = GridSearchCV(
        pipeline,
        param_grid,
        cv=5,
        scoring='neg_mean_absolute_error',
        n_jobs=-1,
        verbose=0
    )
    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    label = f'MLP Neural Net'
    print(f'MLP Neural Net {grid.best_params_}')

    return y_test, y_pred, mae, r2, label

