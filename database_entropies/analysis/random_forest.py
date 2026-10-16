#!/usr/bin/python3
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.tree import export_text

# Load the data
def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, rad, correctionS, mu, eta, gamma, omega, experimental_S FROM PBE', conn)

# Prepare the data
def prepare_data(data):
    data.dropna(inplace=True)
    return data

# Path to your SQLite database
db_file_path = '../entropiesCOSMO.db'

# Fetch and prepare the data
data = fetch_data(db_file_path)
data = prepare_data(data)

# Assume 'experimental_S' is the target and others are features
X = data[['trans_S', 'rot_S', 'vib_S', 'epsilon', 'rad', 'correctionS', 'mu', 'eta', 'gamma', 'omega']]
y = data['experimental_S']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create the Random Forest model
random_forest_model = RandomForestRegressor(n_estimators=200, random_state=42)

# Train the model
random_forest_model.fit(X_train, y_train)

# Predict using the trained model
y_pred = random_forest_model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
# print("Mean Squared Error:", mse)
print("Root Mean Squared Error:", np.sqrt(mse))

# Optionally, review the feature importance to understand which features are most influential
print("Feature Importances:", random_forest_model.feature_importances_)

# Pick one tree from the forest
tree = random_forest_model.estimators_[0]

# Display the decision tree rules
tree_rules = export_text(tree, feature_names=['trans_S', 'rot_S', 'vib_S', 'epsilon', 'rad', 'correctionS', 'mu', 'eta', 'gamma', 'omega'])
# print("Decision rules for one of the trees:\n", tree_rules)

