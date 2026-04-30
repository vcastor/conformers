#!/usr/bin/python3
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score

def run_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    pipline = make_pipeline(StandardScaler(), SVR())
    param_grid = {
        'svr__C': [0.1, 1, 10, 100, 300, 500],
        'svr__epsilon': [0.01, 0.05, 0.1, 0.2],
        'svr__kernel': ['rbf', 'poly', 'sigmoid'],
        'svr__degree': [2, 3, 4]
    }
    grid = GridSearchCV(
        pipline,
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
    label = f'SVR'
    print(f'SVR {grid.best_params_}')

    return y_test, y_pred, mae, r2, label

