#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# Load data from the SQLite database
db_file_path = '../entropiesCOSMO.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute('SELECT mu, eta, gamma, epsilon, experimental_S FROM molecules')
data = cursor.fetchall()
conn.close()

# Filter out rows with None values
filtered_data = [val for val in data if None not in val]

# Prepare data for regression
s_exp = np.array([val[4] for val in filtered_data])
X = np.array([[val[0], val[1], val[2]] for val in filtered_data])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, s_exp, test_size=0.2, random_state=42)

# Initialize models
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    # "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=400, random_state=84)
}

# Train models and store results
results = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    results[name] = {"model": model, "MAE": mae, "R2": r2}

# Print evaluation metrics for each model
for name, result in results.items():
    print(f"{name}:")
    print(f"  Mean Absolute Error: {result['MAE']}")
    print(f"  R-squared: {result['R2']}")
    print()

# Select the best model
best_model_name = max(results, key=lambda name: results[name]["R2"])
best_model = results[best_model_name]["model"]

print(f"Best model: {best_model_name}")

# # Example prediction
# new_data = np.array([[value_mu, value_eta, value_gamma]])  # Replace with actual values
# predicted_S = best_model.predict(new_data)
# print(f"Predicted S: {predicted_S[0]}")

