#!/usr/bin/python3
import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from sklearn.linear_model import LinearRegression

# Objective function: sum of squared residuals
def objective(coeffs):
    alpha, beta, gamma, delta, epsilon, zeta = coeffs
    predictions = alpha * x0 + beta * x1 + gamma * x2 + delta * x3 + epsilon * x4 + zeta * x5
    return np.sum((y - predictions) ** 2)

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

# Data for linear regression
y = np.array([val[3] for val in filtered_valdata])
X = np.array([[val[0], val[1], val[2]] for val in filtered_valdata])
x0, x1, x2 = X[:,0], X[:,1], X[:,2] # Editable variables

# Add cross terms
sums = x0 + x1 + x2
x3 = (x0 * x1) / sums
x4 = (x0 * x2) / sums
x5 = (x1 * x2) / sums

# Scipy optimization
bounds = [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)]
best_score, best_result = np.inf, None
for _ in range(20):
    # Random initial guess for the coefficients
    initial_guess = np.random.rand(6)
    # Constraint: no intercept, coefficients between 0 and 1
    result = minimize(objective, initial_guess, bounds=bounds, method='SLSQP')
    # Check if this result is better
    if result.success and result.fun < best_score:
        best_score = result.fun
        best_result = result

# Minimization result
print('Optimization result:')
if best_result is not None:
    alpha, beta, gamma, delta, epsilon, zeta = best_result.x
    predictions = alpha * x0 + beta * x1 + gamma * x2 + delta * x3 + epsilon * x4 + zeta * x5
    sum_contributions = np.sum(X, axis=1)
    print(f"Optimal coefficients found: alpha={alpha:.4f}, beta={beta:.4f}, gamma={gamma:.4f}")
    print(f"Optimal coefficients found: delta={delta:.4f}, epsilon={epsilon:.4f}, zeta={zeta:.4f}")
    print("for the equation: S_exp = alpha translational + beta rotational + gamma vibrational")
    print("for the equation:       + delta translational*rotational + epsilon translational*vibrational + zeta rotational*vibrational")
    # Calculate R^2
    r_squared = 1 - (np.sum((y - (alpha * x0 + beta * x1 + gamma * x2)) ** 2) / np.sum((y - np.mean(y)) ** 2))
    print(f"R^2: {r_squared:.4f}")
    # Text for the plot
    equation_text = r'$S_{\text{exp}} = \alpha S_{\text{trans}} + \beta S_{\text{rot}} + \gamma S_{\text{vib}} + \delta S_{\text{trans}} S_{\text{rot}} + \epsilon S_{\text{rot}}S_{\text{vib}} + \zeta S_{\text{trans}}S_{\text{vib}}$'
    alpha_text = r'$\alpha = {:.4f}$'.format(alpha)
    beta_text = r'$\beta = {:.1f}$'.format(beta)
    gamma_text = r'$\gamma = {:.1f}$'.format(gamma)
    r_squared_text = r'$r^2 = {:.4f}$'.format(r_squared)
else:
    print("No successful optimization found.")
    quit()

# Plotting
plt.figure(figsize=(12, 6))

# Plot for model predictions vs experimental
plt.subplot(1, 2, 1)
plt.scatter(y, predictions, alpha=0.5)
plt.title('Model Predictions vs. Experimental Entropy')
plt.xlabel('Experimental Entropy')
plt.ylabel('Model Predicted Entropy')
plt.text(0.05, 0.9, equation_text, fontsize=9, transform=plt.gca().transAxes)
plt.text(0.05, 0.85, alpha_text, fontsize=8, transform=plt.gca().transAxes)
plt.text(0.05, 0.8, beta_text, fontsize=8, transform=plt.gca().transAxes)
plt.text(0.05, 0.75, gamma_text, fontsize=8, transform=plt.gca().transAxes)
plt.text(0.05, 0.7, r_squared_text, fontsize=8, transform=plt.gca().transAxes)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)  # Line of perfect fit
plt.grid(True)

# Plot for sum of contributions vs experimental
plt.subplot(1, 2, 2)
plt.scatter(y, sum_contributions, alpha=0.5)
plt.scatter(y, X[:,0], alpha=0.5, label='Translational')
plt.scatter(y, X[:,1], alpha=0.5, label='Rotational')
plt.scatter(y, X[:,2], alpha=0.5, label='Vibrational')
plt.title('Sum of Contributions vs. Experimental Entropy')
plt.xlabel('Experimental Entropy')
plt.ylabel('Sum of Contributions')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)  # Line of perfect fit
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

