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
    # AND family != 'aliphatic_amines'
    # AND family != 'pyridines_quinolines_etc'
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

def pred_N(electrofuge, distances, q_qtaim, clr, elep, population, homo):
    """ Equation: N = α/electrofuge - β*Σe^(-γd)q_qtaim + δ*Σe^(-εd)clr + ζ*Σe^(-ηd)*elp/pop + θ/HOMO + ι"""
    alpha, beta, gamma = 23.1054, 8.9104, 0.1153
    delta, epsilon, zeta = 0.2404, 0.0381, 0.2989
    eta, theta, iot = 0.0167, -59.0422, -2.9176

    prediction = []

    for ele, nuc, distance, q, clrv, elp, pop, hom in zip(electrofuge, nucleofuge, distances, q_qtaim, clr, elep, population, homo):
        delta_dis = np.exp(-gamma*distance**2)
        delta_clr = np.exp(-epsilon*distance**2)
        delta_elp = np.exp(-eta*distance**2)
        sum_q     = np.dot(delta_dis, q)
        sum_clr   = np.dot(delta_clr, clrv)
        sum_elp   = np.dot(delta_elp, elp/pop)
        prediction.append(alpha/ele - beta*sum_q + delta*sum_clr + zeta*sum_elp + theta/hom + iot)

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

        pred = pred_N(electrofuge, distances, q_qtaim, clr, elep, pop, homo)
        mae = np.mean(np.abs(pred - exp_n))
        r2  = r2 = 1 - np.sum((exp_n - pred)**2)/np.sum((exp_n - np.mean(pred))**2)

        plt.plot([pred.min(), pred.max()], [pred.min(), pred.max()], 'k--', lw=2)
        plt.scatter(exp_n, pred, label=f'MAE={mae:.2f}, R²={r2:.2f}', alpha=0.6, edgecolor='k')
        plt.legend(fontsize=14)
        plt.xlabel('Experimental N', fontsize=16)
        plt.ylabel('Predicted N', fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.title('Experimental vs Predicted N', fontsize=18)
        plt.show()

