#!/usr/bin/python3
import sqlite3
import numpy as np
from scipy.optimize import minimize

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
    # AND family != 'pyridines_quinolines_etc'
    # AND family != 'aliphatic_amines'
    params = cursor.fetchall()
    
    cursor.close()
    return params

def region(dbpath, region):
    smiles_list, solvents, atoms, exp_n, exp_sn = zip(*parameters(dbpath))

    features = ['electrofuge', 'nucleofuge', 'q_qtaim', 'P', 'region']
    electrofuge, nucleofuge, q_qtaim, p = [], [], [], []
    idx = []

    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    for i, (smiles, solvent, atom) in enumerate(zip(smiles_list, solvents, atoms)):
        cursor.execute(f'''
            SELECT {', '.join(features)}
              FROM reactive
              WHERE smiles = '{smiles}'
                AND solvent = '{solvent}'
                AND atom_analysed = {atom}
        ''')
        data = cursor.fetchone()
        electrofuge.append(data[0])
        nucleofuge.append(data[1])
        q_qtaim.append(data[2])
        p.append(data[3])
        if data[-1] == region:
            idx.append(i)

    cursor.close()

    electrofuge = np.array(electrofuge)[idx]
    nucleofuge  = np.array(nucleofuge)[idx]
    q_qtaim = np.array(q_qtaim)[idx]
    p       = np.array(p)[idx]

    exp_n  = np.array(exp_n)[idx]
    exp_sn = np.array(exp_sn)[idx]

    return electrofuge, nucleofuge, q_qtaim, p, exp_n, exp_sn

# -------------------------
# Objective functions
# -------------------------

def obj_inverse(coeff, electrofuge, nucleofuge, q_qtaim, p, exp_n):
    """ N = α/electrofuge """
    alpha = coeff[0]
    prediction = alpha/electrofuge
    return np.sum((exp_n - prediction)**2)

def obj_charge(coeff, electrofuge, nucleofuge, q_qtaim, p, exp_n):
    """ N = α/electrofuge + β*nucleofuge + γ*q_qtaim + δ"""
    alpha, beta, gamma, delta = coeff
    prediction = alpha/electrofuge + beta*nucleofuge + gamma*q_qtaim + delta
    return np.sum((exp_n - prediction)**2)

def obj_betap(coeff, electrofuge, nucleofuge, q_qtaim, p, exp_n):
    """ N = (α + β*P)/electrofuge + γ"""
    alpha, beta, gamma = coeff
    prediction = (alpha + beta*p)/electrofuge + gamma
    return np.sum((exp_n - prediction)**2)

def obj_mult(coeff, electrofuge, nucleofuge, q_qtaim, p, exp_n):
    """ N = α/(electrofuge*q_qtaim) + β"""
    alpha, beta = coeff
    prediction = alpha/(electrofuge*q_qtaim) + beta
    return np.sum((exp_n - prediction)**2)

def obj_log(coeff, electrofuge, nucleofuge, q_qtaim, p, exp_n):
    """ N = (-log(abs(α*electrofuge + β)) + γ)/δ*q_qtaim"""
    alpha, beta, gamma, delta = coeff
    prediction = (-np.log(np.abs(alpha*electrofuge + beta)) + gamma)/(delta*q_qtaim)
    return np.sum((exp_n - prediction)**2)

# -------------------------
# Objective functions
# -------------------------

def opt_model(electrofuge, nucleofuge, q_qtaim, exp_n, model, bounds):
    best_score, best_result = np.inf, None

    if model == 'inverse':
        obj_model = obj_inverse
        print("N = α/electrofuge")
    elif model == 'charge':
        obj_model = obj_charge
        print("N = α/electrofuge + β*nucleofuge + γ*q_qtaim + δ")
    elif model == 'betap':
        obj_model = obj_betap
        print("N = (α + β*P)/electrofuge + γ")
    elif model == 'mult':
        obj_model = obj_mult
        print("N = α/(electrofuge*q_qtaim) + β")
    elif model == 'log':
        obj_model = obj_log
        print("N = (-log(abs(α*electrofuge + β)) + γ)/(δ*q_qtaim)")

    for _ in range(50):
        initial_guess = [
            l + np.random.rand()*(h-l)
            for (l,h) in bounds
        ]
        result = minimize(
            obj_model,
            x0=initial_guess,
            args=(electrofuge, nucleofuge, q_qtaim, p, exp_n),
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

    models = ['inverse', 'charge', 'betap', 'mult', 'log']
    bounds = [[(50,150)],
              [(50,150), (-10, 10), (-50,50), (-30,30)],
              [(50,150), (-10, 10), (-50,50)],
              [(50,150), (-20, 20)],
              [(-10,10), (-20, 20), (-50,50), (-30,30)]]

    """ N = (-log(abs(α*electrofuge + β)) + γ)/δ*q_qtaim"""

    # Loop for Regions
    for regionval in ['1', '2']:
        print(f"===Region: {regionval}===")
        electrofuge, nucleofuge, q_qtaim, p, exp_n, exp_sn = region(dbpath, regionval)
        if (len(electrofuge) < 2):
            continue

        # Loop for models
        for model, bound in zip(models, bounds):
            results = opt_model(electrofuge, nucleofuge, q_qtaim, exp_n, model, bound)

            print_coeffs(results.x)
            mae = results.fun/len(exp_n)
            print(f"MAE: {mae}")
            ss_tot = np.sum((exp_n - np.mean(exp_n))**2)
            r2 = 1 - results.fun/ss_tot
            print(f"R^2: {r2}\n")

