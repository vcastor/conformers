#!/opt/homebrew/bin/python3.9
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# # The optimized form of the function
# def optimized_model(X, alpha, beta, gamma, delta):
#     x2, x7, x20 = X
#     return alpha*x2 + beta/(gamma*x20 + delta*x7)

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
sn_exp = np.array([val[1] for val in filtered_data])
X = np.array([val[2:] for val in filtered_data])
x26 = X[:,26]

# Predictions with the optimized model
# = y = abs(x₂₆) ^ 0.24247     
pred_optimized = np.absolute(x26)**0.24247

# Calculate and print MAE for the optimized model
mae_optimized = np.absolute(pred_optimized - sn_exp).mean()
print(f'Optimized MAE: {mae_optimized}')

# Plot Experimental vs. Predicted values
plt.scatter(sn_exp, pred_optimized, label="Predicted vs. Experimental", color="blue")
plt.plot([min(sn_exp), max(sn_exp)], [min(sn_exp), max(sn_exp)], color='red', label="y=x")
plt.xlabel('Experimental SN')
plt.ylabel('Predicted SN')
plt.legend()
plt.title('Experimental vs. Predicted SN')
plt.show()

