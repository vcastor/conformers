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
          AND experimental_N > 10
          AND (comment IS NULL OR comment != 'exclude')
    ''')
    params = cursor.fetchall()
    
    cursor.close()
    return params

def region(dbpath):
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
        if data[-1] == '1':
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

    # if msc:
    #     return electrofuge_msc, nucleofuge_msc, homo_msc, exp_n, exp_sn
    # else:
    return electrofuge, nucleofuge, homo, exp_n, exp_sn

# -------------------------
# Objective functions
# -------------------------

def pred_N(electrofuge, nucleofuge, distances, q_qtaim):
    """ Equation: N = α/electrofuge - β*nucleofuge - γ*Σe^(-δd)q_qtaim - ε"""
    alpha, beta, gamma = 109.1573, 3.8812, 1.0377
    delta, epsilon = 0.4198, 2.6426
    # alpha, beta, gamma = 81.2974, 0.9780, 0.6958
    # delta, epsilon = 0.5216, 0.2826

    prediction = []

    for ele, nuc, distance, q in zip(electrofuge, nucleofuge, distances, q_qtaim):
        delta_dis = np.exp(-delta*distance**2)
        sum_q     = np.dot(delta_dis, q)
        prediction.append(alpha/ele - beta*nuc - gamma*sum_q - epsilon)

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
        electrofuge, nucleofuge, homo, exp_n, exp_sn = region(dbpath)
        distances, q_qtaim, clr, elep, pop = data_pond(pout, exp_n, exp_sn)

        if (len(exp_n) < 2):
            continue
        else:
            print(f"Number of data: {len(exp_n)}")

        pred = pred_N(electrofuge, nucleofuge, distances, q_qtaim)
        mae = np.mean(np.abs(pred - exp_n))
        r2  = r2 = 1 - np.sum((exp_n - pred)**2)/np.sum((exp_n - np.mean(pred))**2)

        plt.plot([pred.min(), pred.max()], [pred.min(), pred.max()], 'k--', lw=2)
        plt.scatter(exp_n, pred, label=f'MAE={mae:.2f}, R²={r2:.2f}', alpha=0.6)
        plt.legend()
        plt.xlabel('Experimental N')
        plt.ylabel('Predicted N')
        plt.show()

