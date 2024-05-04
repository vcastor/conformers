#!/usr/bin/python3
import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Retrieve all molecule names from the database
cursor.execute('SELECT trans_S, rot_S, vib_S, experimental_S FROM molecules')
valdata = cursor.fetchall()

# Commit the changes and close the connection
conn.commit()
conn.close()

# Not compleated data!
filtered_valdata = [val for val in valdata if None not in val]

y = np.array([val[3] for val in filtered_valdata])
X = np.array([[val[0], val[1], val[2]] for val in filtered_valdata])

model = LinearRegression(fit_intercept=False)
model.fit(X, y)

predictions = model.predict(X)
sum_contributions = np.sum(X, axis=1)

print('Coefficients: ', model.coef_)
print('Intercept: ', model.intercept_)
print('R^2: ', model.score(X, y))

# Plotting

plt.figure(figsize=(12, 6))

# Plot for model predictions vs experimental
plt.subplot(1, 2, 1)
plt.scatter(y, predictions, alpha=0.5)
plt.title('Model Predictions vs. Experimental Entropy')
plt.xlabel('Experimental Entropy (experimental_S)')
plt.ylabel('Model Predicted Entropy')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)  # Line of perfect fit
plt.grid(True)

# Plot for sum of contributions vs experimental
plt.subplot(1, 2, 2)
plt.scatter(y, sum_contributions, alpha=0.5)
plt.scatter(y, X[:,0], alpha=0.5, label='Translational')
plt.scatter(y, X[:,1], alpha=0.5, label='Rotational')
plt.scatter(y, X[:,2], alpha=0.5, label='Vibrational')
plt.title('Sum of Contributions vs. Experimental Entropy')
plt.xlabel('Experimental Entropy (experimental_S)')
plt.ylabel('Sum of Contributions (trans_S + rot_S + vib_S)')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)  # Line of perfect fit
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()


