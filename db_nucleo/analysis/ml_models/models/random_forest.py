#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score

def run_model(X, y, feature_names):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    param_grid = {
        'n_estimators': [300, 500, 800, 1200, 1500],
        'max_depth': [None, 30, 50, 70],
        'min_samples_split': [2, 4, 6],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['auto', 'sqrt', 'log2', None],
        'bootstrap': [True, False]
    }

    grid = GridSearchCV(
        RandomForestRegressor(random_state=42),
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
    label = "Random Forest"
    print(f"Random Forest ({grid.best_params_})")

    # ---- Feature importance plot ----
    importances = best_model.feature_importances_
    indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(12, 7))
    plt.title("Feature Importances (Best Random Forest)", fontsize=20)
    plt.bar(range(len(importances)), importances[indices], align="center")
    plt.xticks(
        range(len(importances)),
        [feature_names[i] for i in indices],
        rotation=90,
        fontsize=12
    )
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig('imporances.pdf')
    plt.close()  # don’t display, just save
    # --------------------------------

    return y_test, y_pred, mae, r2, label

# def run_model(X, y):
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#     param_grid = {
#         'n_estimators': [300, 500, 800, 1200, 1500],
#         'max_depth': [None, 30, 50, 70],
#         'min_samples_split': [2, 4, 6],
#         'min_samples_leaf': [1, 2, 4],
#         'max_features': ['auto', 'sqrt', 'log2', None],
#         'bootstrap': [True, False]
#     }
#     grid = GridSearchCV(
#         RandomForestRegressor(random_state=42),
#         param_grid,
#         cv=5,
#         scoring='neg_mean_absolute_error',
#         n_jobs=-1,
#         verbose=0
#     )
#     grid.fit(X_train, y_train)

#     best_model = grid.best_estimator_
#     y_pred = best_model.predict(X_test)

#     mae = mean_absolute_error(y_test, y_pred)
#     r2 = r2_score(y_test, y_pred)
#     label = f'Random Forest'
#     print(f'Random Forest ({grid.best_params_})')

#     return y_test, y_pred, mae, r2, label

# def run_model(X, y):
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#     rf = RandomForestRegressor(n_estimators=500, random_state=42)
#     rf.fit(X_train, y_train)
#     y_pred = rf.predict(X_test)
#     mae = mean_absolute_error(y_test, y_pred)

#     return y_test, y_pred, mae, r2_score(y_test, y_pred), 'Random Forest'

# Cross-validation
# cv_scores = cross_val_score(rf, X, y, cv=5, scoring='r2')
# print(f'5-Fold CV R²: {np.mean(cv_scores):.3f} ± {np.std(cv_scores):.3f}')

# Feature importance
# importances = rf.feature_importances_
# indices = np.argsort(importances)[::-1]

# # Plot
# plt.figure(figsize=(10, 6))
# plt.title("Feature Importances (Random Forest)", fontsize=20)
# plt.bar(range(len(features)), importances[indices], align="center")
# plt.xticks(range(len(features)), [features[i] for i in indices], rotation=90, fontsize=16)
# plt.yticks(fontsize=16)
# plt.tight_layout()
# plt.show()

