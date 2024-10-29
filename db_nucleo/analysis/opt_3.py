#!/opt/homebrew/bin/python3.9
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Objetive models
def obj_model_sn(coef, exp, X, model):# For Sn
    if model == 1:
        pred = coef[0]*X[:,8] + coef[1]*X[:,26] + coef[2]
    elif model == 2:
        pred = coef[0]*X[:,8] + coef[1]
    elif model == 3:
        pred = coef[0]*X[:,4] + coef[1]*X[:,0] + coef[2]
    return np.absolute(pred - exp).mean()

def obj_model_n(coef, exp, X, model):# For N
    if model == 1:
        pred = coef[0]*X[:,6] + coef[1]
    elif model == 2:
        pred = coef[0]/X[:,7] + coef[1]*X[:,2] + coef[2]
    elif model == 3:
        pred = coef[0]/X[:,7] + coef[1]/X[:,20] + coef[2]*X[:,2] + coef[3]*X[:,25] + coef[4]
    return np.absolute(pred - exp).mean()

# Optimisation
def optimise_model(exp, X, model, obj_model, num_coeffs):
    best_score, best_result = np.inf, None
    for _ in range(20):
        initial_guess = np.random.rand(num_coeffs)
        result = minimize(obj_model, initial_guess, args=(exp, X, model))
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

# 
# Load data from SQLite database
db_file_path = '../nucleo_data.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute('''SELECT experimental_N, experimental_Sn,
                         mu, eta, softness, hyperhardness, omega, 
                         nucleofuge, electrofuge, electrodonating, electroaccepting, fplus, fminus, fzero, 
                         f2, sfplus, sfminus, sfzero, s2, muplusfplus, muminusfminus, wfplus, wf2, 
                         Sf2, s2f2, electro, nucleo, q_qtaim, q_hirshfeld
                  FROM main WHERE atom_analysed > 0 AND nconformers not null''')
data = cursor.fetchall()
conn.close()

# Filter out rows with missing data [?]
filtered_data = [val for val in data if None not in val]

# Prepare data for regression
n_exp = np.array([val[0] for val in filtered_data])
sn_exp = np.array([val[1] for val in filtered_data])
X = np.array([val[2:] for val in filtered_data])

# Optimise the models
models = [1, 2, 3]

# Plot
fig, ax = plt.subplots(1, 2, figsize=(12, 6))

# Sn optimisation and plot
for model in models:
    num_coeffs = 3 if model == 1 else 2
    res = optimise_model(sn_exp, X, model, obj_model_sn, num_coeffs)
    sn_pred = obj_model_sn(res.x, sn_exp, X, model)
    ax[0].scatter(sn_exp, sn_pred, label=f'Model {model} (Sn)')
ax[0].set_xlabel('Experimental Sn')
ax[0].legend()

# N optimisation and plot
for model in models:
    num_coeffs = 5 if model == 3 else (3 if model == 2 else 2)
    res = optimise_model(n_exp, X, model, obj_model_n, num_coeffs)
    n_pred = obj_model_n(res.x, n_exp, X, model)
    ax[1].scatter(n_exp, n_pred, label=f'Model {model} (N)')
ax[1].set_xlabel('Experimental N')
ax[1].legend()

plt.show()

