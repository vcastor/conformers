#!/usr/bin/python3
import numpy as np
from reader import read_data
from scipy.optimize import minimize

def obj_model(coeff, q, electrofuge, N_exp):
    alpha, beta = coeff

    prediction = alpha*q/electrofuge + beta

    return np.sum((N_exp - prediction)**2)

def opt_model(q, electrofuge, N_exp, bounds):
    best_score, best_result = np.inf, None

    for _ in range(30):
        initial_guess = [
            l + np.random.rand()*(h-l)
            for (l,h) in bounds
        ]
        result = minimize(
            obj_model,
            x0=initial_guess,
            args=(q, electrofuge, N_exp),
            bounds=bounds,
            method='L-BFGS-B'
        )
        if result.success and result.fun < best_score:
            best_score, best_result = result.fun, result
    
    return best_result

# -------------------------
# 🚀
# -------------------------
if __name__ == "__main__":

    # Read the reactive data [ALL CONFORMERS]
    valuefile = 'reactive.pout'
    data = read_data(valuefile)

    # One value per system
    natoms = np.array(data["natoms"])
    N_exp  = np.array(data["expN"])
    Sn_exp = np.array(data["expSn"])
    electrofuge = np.array(data["electrofuge"])

    # One array per system
    q = np.array([q[0] for q in data["q_qtaim"]])

    bounds = [(-200,200), (-200,200)]

    # Optimise the model
    results = opt_model(q, electrofuge, N_exp, bounds)

    if results:
        print(results.x)
        pred = results.x[0]*q/electrofuge + results.x[1]
        st_dv = np.std(N_exp - pred)
        print("Standard deviation: ", st_dv)
        r2 = 1 - np.sum((N_exp - pred)**2)/np.sum((N_exp - np.mean(N_exp))**2)
        print("R2: ", r2)

