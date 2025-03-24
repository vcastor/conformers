#!/usr/bin/python3
import sqlite3
import numpy as np
from reader import data_pond
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
    # AND family != 'aliphatic_amines'
    # AND family != 'pyridines_quinolines_etc'
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

def obj_charge(coeff, electrofuge, nucleofuge, distances, q_qtaim, clr, elep, population, homo, exp_n):
    """ N = α/electrofuge - β*nucleofuge - γ*Σe^(-δd)q_qtaim + ε*Σe^(-ζd)clr + η*Σe^(-θd)*elp/pop + ι + κ*HOMO"""""
    alpha, beta, gamma, delta, epsilon, zeta, eta, theta, iot, kappa = coeff

    prediction = []

    for ele, nuc, distance, q, clrv, elp, pop, hom in zip(electrofuge, nucleofuge, distances, q_qtaim, clr, elep, population, homo):
        delta_dis = np.exp(-delta*distance**2)
        delta_clr = np.exp(-zeta*distance**2)
        delta_elp = np.exp(-theta*distance**2)
        sum_q     = np.dot(delta_dis, q)
        sum_clr   = np.dot(delta_clr, clrv)
        sum_elp   = np.dot(delta_elp, elp/pop)
        prediction.append(alpha/ele - beta*nuc - gamma*sum_q + epsilon*sum_clr + eta*sum_elp + iot+ kappa/hom)

    prediction = np.array(prediction)
    return np.sum((exp_n - prediction)**2)

def opt_model(electrofuge, nucleofuge, distances, q_qtaim, clr, elep, pop, homo, exp_n, bounds):
    best_score, best_result = np.inf, None

    for _ in range(50):
        initial_guess = [
            l + np.random.rand()*(h-l)
            for (l,h) in bounds
        ]
        result = minimize(
            obj_charge,
            x0=initial_guess,
            args=(electrofuge, nucleofuge, distances, q_qtaim, clr, elep, pop, homo, exp_n),
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

    """ N = α/electrofuge - β*nucleofuge - γ*Σe^(-δd)q_qtaim + ε*Σe^(-ζd)clr + η*Σe^(-θd)*elp/pop + ι + κ*HOMO"""
    bounds = [(50,180), (0, 10), (0,2000), (0.00, 3.99), (-2000, 2000), (0.00, 3.99), (-2000, 2000), (0.00, 3.99), (-2000, 2000), (-200,200)]

    print('Equation: N = α/electrofuge - β*nucleofuge - γ*Σe^(-δd)q_qtaim + ε*Σe^(-ζd)clr + η*Σe^(-θd)*elp/pop + ι + κ/HOMO\n')
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
            distances, q_qtaim, clr, elep, pop = data_pond(pout, exp_n, exp_sn)
            if (len(exp_n) < 2):
                continue
            else:
                print(f"Number of data: {len(exp_n)}")

            results = opt_model(electrofuge, nucleofuge, distances, q_qtaim, clr, elep, pop, homo, exp_n, bounds)

            print_coeffs(results.x)
            mae = results.fun/len(exp_n)
            print(f"MAE: {mae}")
            ss_tot = np.sum((exp_n - np.mean(exp_n))**2)
            r2 = 1 - results.fun/ss_tot
            print(f"R^2: {r2}\n")

