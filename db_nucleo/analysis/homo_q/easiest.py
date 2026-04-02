#!/usr/bin/python3
import sqlite3
import numpy as np
from scipy.optimize import minimize
from sklearn.metrics import r2_score

def parameters(dbpath):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    key = ['smiles', 'solvent', 'atom_analysed', 'experimental_N', 'experimental_Sn']
    cursor.execute(f'''
        SELECT {', '.join(key)}
        FROM parameters
        WHERE table_name = 'reactive'
          AND (comment IS NULL OR comment != 'exclude')
    ''')
    params = cursor.fetchall()
    
    cursor.close()
    return params

def q_homo_vals(dbpath):
    smiles_list, solvents, atoms, exp_n, exp_sn = zip(*parameters(dbpath))

    features = ['q_qtaim', 'HOMO']
    q_qtaim, homo = [], []

    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    for i, (smiles, solvent, atom) in enumerate(zip(smiles_list, solvents, atoms)):
        cursor.execute(f'''
            SELECT {', '.join(features)}
              FROM reactive_msc
              WHERE smiles = '{smiles}'
                AND solvent = '{solvent}'
                AND atom_analysed = {atom}
        ''')
        data = cursor.fetchone()
        q_qtaim.append(data[0])
        homo.append(data[1])

    cursor.close()

    q_qtaim = np.array(q_qtaim)
    homo    = np.array(homo)

    exp_n  = np.array(exp_n)
    exp_sn = np.array(exp_sn)

    return q_qtaim, homo, exp_n, exp_sn

# -------------------------
# Objective functions
# -------------------------

def obj_charge(coeff, homo, q_qtaim, exp):
    """ N = α*homo + β*q_qtaim + γ"""
    alpha, beta, gamma = coeff
    prediction = alpha*homo + beta*q_qtaim + gamma
    return np.sum((exp - prediction)**2)

# -------------------------
# Objective functions
# -------------------------

def opt_model(homo, q_qtaim, exp, bounds):
    best_score, best_result = np.inf, None

    for _ in range(50):
        initial_guess = [
            l + np.random.rand()*(h-l)
            for (l,h) in bounds
        ]
        result = minimize(
            obj_charge,
            x0=initial_guess,
            args=(homo, q_qtaim, exp),
            bounds=bounds,
            method='L-BFGS-B'
        )
        if result.success and result.fun < best_score:
            best_score, best_result = result.fun, result
    
    return best_result

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ',
                     'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ',
                     'φ', 'χ', 'ψ', 'ω']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f' {formatted_coeffs}')

# -------------------------
# Main script 🚀
# -------------------------

if __name__ == "__main__":

    # Load the data
    dbpath = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db"
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    bounds = [(-200,200), (-200,200), (-200,200)]

    homo, q_qtaim, exp_n, exp_sn = q_homo_vals(dbpath)
    exp_name = ['N', 'Sn']

    print("N = α/homo + β*q_qtaim + γ")
    for i, exp in enumerate([exp_n, exp_sn]):
        results = opt_model(homo, q_qtaim, exp, bounds)
        print(f"modeling for {exp_name[i]}")
        print_coeffs(results.x)
        pred_val = homo*results.x[0] + q_qtaim*results.x[1] + results.x[2]
        mae = np.mean(np.abs(exp - pred_val))
        r2 = r2_score(exp, pred_val)
        print(f"MAE: {mae:.4f}")
        print(f"R2: {r2:.2f}")

