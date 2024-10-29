#!/opt/homebrew/bin/python3.9
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# The optimized form of the function
def optimized_model(X, alpha, beta, gamma, delta):
    x2, x7, x20 = X
    return alpha*x2 + beta/(gamma*x20 + delta*x7)

# Load data from SQLite database
db_file_path = '../nucleo_data.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute('''SELECT experimental_N, experimental_Sn, mu, eta, softness, hyperhardness, omega, 
                         nucleofuge, electrofuge, electrodonating, electroaccepting, fplus, fminus, fzero, 
                         f2, sfplus, sfminus, sfzero, s2, muplusfplus, muminusfminus, wfplus, wf2, 
                         Sf2, s2f2, electro, nucleo, q_qtaim, q_hirshfeld
                  FROM main WHERE atom_analysed > 0 AND nconformers = 1''')
data = cursor.fetchall()
conn.close()

# Filter out rows with missing data
filtered_data = [val for val in data if None not in val]

# Prepare data for regression
n_exp = np.array([val[0] for val in filtered_data])
X = np.array([val[2:] for val in filtered_data])
x2, x7, x20 = X[:,2], X[:,7], X[:,20]

X_opt = np.array([x2, x7, x20])
initial_guess = [1, 1, 1, 1]
params, covariance = curve_fit(optimized_model, X_opt, n_exp, initial_guess)
alpha, beta, gamma, delta = params
print(f"alpha: {alpha}, beta: {beta}, gamma: {gamma}, delta: {delta}")

# Predictions with the optimized model
pred_optimized = optimized_model(X_opt, alpha, beta, gamma, delta)

# Calculate and print MAE for the optimized model
mae_optimized = np.absolute(pred_optimized - n_exp).mean()
print(f'Optimized MAE: {mae_optimized}')

# # Plot Experimental vs. Predicted values
# plt.scatter(n_exp, pred, label="Predicted vs. Experimental", color="blue")
# plt.plot([min(n_exp), max(n_exp)], [min(n_exp), max(n_exp)], color='red', label="y=x")
# plt.xlabel('Experimental N')
# plt.ylabel('Predicted N')
# plt.legend()
# plt.title('Experimental vs. Predicted N')
# plt.show()

