#!/usr/bin/python3
from data_loader import load_data
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from scipy.interpolate import RBFInterpolator
import numpy as np

db_path = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db'
X, y = load_data(db_path)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# RBFInterpolator expects numpy arrays
rbf = RBFInterpolator(X_train.values, y_train.values, neighbors=40)
# rbf = RBFInterpolator(X_train.values, y_train.values, neighbors=10)
y_pred = rbf(X_test.values)

print(f'RBF MAE: {mean_absolute_error(y_test, y_pred):.3f}')
print(f'RBF R²: {r2_score(y_test, y_pred):.3f}')

