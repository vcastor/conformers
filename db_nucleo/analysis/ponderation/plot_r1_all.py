#!/usr/bin/python3
import sqlite3
import numpy as np
from reader import data_pond
from scipy.optimize import minimize
from matplotlib import pyplot as plt

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

def region(dbpath):
    smiles_list, solvents, atoms, exp_n, exp_sn = zip(*parameters(dbpath))

    descriptors = ['electrofuge', 'nucleofuge', 'q_qtaim']
    features = descriptors + ['region']

    electrofuge, nucleofuge, q_qtaim = [], [], []
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
        data_msc = cursor.fetchone()
        electrofuge.append(data[0])
        nucleofuge.append(data[1])
        q_qtaim.append(data[2])
        if data[-1] == '1':
            idx.append(i)

    cursor.close()

    electrofuge = np.array(electrofuge)[idx]
    nucleofuge  = np.array(nucleofuge)[idx]
    q_qtaim     = np.array(q_qtaim)[idx]

    exp_n  = np.array(exp_n)[idx]
    exp_sn = np.array(exp_sn)[idx]

    return electrofuge, nucleofuge, q_qtaim, exp_n, exp_sn

# -------------------------
# Objective functions
# -------------------------

def pred_N(electrofuge, nucleofuge, q_qtaim):
    """ Equation: N = α/electrofuge - β*nucleofuge + γ*q_qtaim - δ """
    alpha, beta, gamma, delta = 102.7217, 2.8491, 0.1050, 2.7297

    prediction = alpha/electrofuge - beta*nucleofuge + gamma*q_qtaim - delta

    return np.array(prediction)

# -------------------------
# Main script 🚀
# -------------------------

if __name__ == "__main__":

    # Load the data
    dbpath = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db"
    poutbase = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/analysis/ponderation/"
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    for msc in [False]:
        if msc:
            pout = poutbase + 'msc_pond.pout'
        else:
            pout = poutbase + 'reactive.pout'
        electrofuge, nucleofuge, q_qtaim, exp_n, exp_sn = region(dbpath)

        if (len(exp_n) < 2):
            continue
        else:
            print(f"Number of data: {len(exp_n)}")

        pred = pred_N(electrofuge, nucleofuge, q_qtaim)
        mae = np.mean(np.abs(pred - exp_n))
        r2  = r2 = 1 - np.sum((exp_n - pred)**2)/np.sum((exp_n - np.mean(pred))**2)

        plt.plot([pred.min(), pred.max()], [pred.min(), pred.max()], 'k--', lw=2)
        plt.scatter(exp_n, pred, label=f'MAE={mae:.2f}, R²={r2:.2f}', alpha=0.6)
        plt.legend()
        plt.xlabel('Experimental N')
        plt.ylabel('Predicted N')
        plt.show()

