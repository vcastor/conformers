#!/usr/bin/python3
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score

def run_model(X, y):
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    param_grid = {
        'n_estimators': [300, 500, 1000],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 5, 10, 15],
        'min_samples_split': [2, 5, 8],
        'min_samples_leaf': [1, 2, 4],
        'subsample': [0.7, 0.85, 1,0],
        'max_features': ['sqrt', 'log2', None]
    }
    grid = GridSearchCV(
        GradientBoostingRegressor(random_state=42),
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
    label = f'GBR'
    print(f'Gradient Boosting Regressor {grid.best_params_}')

    return y_test, y_pred, mae, r2, label

