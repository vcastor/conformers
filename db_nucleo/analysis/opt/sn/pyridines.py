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
          AND family = 'pyridines_quinolines_etc'
          AND (comment IS NULL OR comment != 'exclude')
    ''')
    params = cursor.fetchall()
    
    cursor.close()
    return params

def region(dbpath, region, msc=False):
    smiles_list, solvents, atoms, exp_n, exp_sn = zip(*parameters(dbpath))

    descriptors = ['electrofuge', 'nucleofuge', 'HOMO']
    features = descriptors + ['region']

    electrofuge, nucleofuge, homo = [], [], []
    electrofuge_msc, nucleofuge_msc, homo_msc = [], [], []
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
        cursor.execute(f'''
            SELECT {', '.join(descriptors)}
              FROM reactive_msc
              WHERE smiles = '{smiles}'
                AND solvent = '{solvent}'
                AND atom_analysed = {atom}
        ''')
        data_msc = cursor.fetchone()
        electrofuge.append(data[0])
        nucleofuge.append(data[1])
        homo.append(data[2])
        electrofuge_msc.append(data_msc[0])
        nucleofuge_msc.append(data_msc[1])
        homo_msc.append(data_msc[2])
        if data[-1] == region:
            idx.append(i)

    cursor.close()

    electrofuge = np.array(electrofuge)[idx]
    nucleofuge  = np.array(nucleofuge)[idx]
    homo        = np.array(homo)[idx]

    electrofuge_msc = np.array(electrofuge_msc)[idx]
    nucleofuge_msc  = np.array(nucleofuge_msc)[idx]
    homo_msc        = np.array(homo_msc)[idx]

    exp_n  = np.array(exp_n)[idx]
    exp_sn = np.array(exp_sn)[idx]

    if msc:
        return electrofuge_msc, nucleofuge_msc, homo_msc, exp_n, exp_sn
    else:
        return electrofuge, nucleofuge, homo, exp_n, exp_sn

# -------------------------
# Objective functions
# -------------------------

def obj_pyridines(coeff, electrofuge, nucleofuge, homo, exp_sn):
    """ Sn = α/electrofuge + β"""
    alpha, beta = coeff
    prediction = alpha/electrofuge + beta
    return np.sum((exp_sn - prediction)**2)

# def obj_log(coeff, electrofuge, nucleofuge, homo, exp_sn):
#     """ Sn = (α*HOMO - β*log(nucleofuge)^2)**-γ + δ """
#     alpha, beta, gamma, delta = coeff
#     prediction = (alpha*homo- beta*np.log(nucleofuge)**2)**(-gamma) + delta
#     return np.sum((exp_sn - prediction)**2)

def opt_model(electrofuge, nucleofuge, homo, exp_sn, bounds):
    best_score, best_result = np.inf, None

    for _ in range(50):
        initial_guess = [
            l + np.random.rand()*(h-l)
            for (l,h) in bounds
        ]
        result = minimize(
            obj_pyridines,
            x0=initial_guess,
            args=(electrofuge, nucleofuge, homo, exp_sn),
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
    poutbase = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/analysis/ponderation/"
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    """ Sn = α/electrofuge + β"""
    bounds = [(-10,10), (-10,10)]

    print('Sn = α/electrofuge + β')
    # Loop for Regions
    for regionval in ['1', '2']:
        print(f"===Region: {regionval}===")
        for msc in [True, False]:
            if msc:
                pout = poutbase + 'msc_pond.pout'
                print("Most Satble Conformer")
            else:
                pout = poutbase + 'reactive.pout'
                print("All conformers")
            electrofuge, nucleofuge, homo, exp_n, exp_sn = region(dbpath, regionval, msc)
            if (len(exp_n) < 2):
                continue
            else:
                print(f"Number of data: {len(exp_n)}")

            results = opt_model(electrofuge, nucleofuge, homo, exp_sn, bounds)

            print_coeffs(results.x)
            mae = results.fun/len(exp_n)
            print(f"MAE: {mae}")
            ss_tot = np.sum((exp_n - np.mean(exp_n))**2)
            r2 = 1 - results.fun/ss_tot
            print(f"R^2: {r2}\n")

