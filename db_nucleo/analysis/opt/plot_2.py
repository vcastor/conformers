#!/usr/bin/python3
import sqlite3
import numpy as np
from matplotlib import pyplot as plt

def parameters(dbpath):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    key = ['smiles', 'solvent', 'atom_analysed', 'experimental_N', 'experimental_Sn']
    cursor.execute(f'''
        SELECT {', '.join(key)}
        FROM parameters WHERE table_name = 'reactive'
        AND (comment IS NULL OR comment != 'exclude')
    ''')
    params = cursor.fetchall()
    
    cursor.close()
    return params

def region(dbpath, region):
    smiles_list, solvents, atoms, exp_n, exp_sn = zip(*parameters(dbpath))

    features = ['electrofuge', 'nucleofuge', 'q_qtaim', 'region']
    electrofuge, nucleofuge, q_qtaim = [], [], []
    idx = []

    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    for i, (smiles, solvent, atom) in enumerate(zip(smiles_list, solvents, atoms)):
        cursor.execute(f'''
            SELECT {', '.join(features)}
            FROM reactive
            WHERE smiles = '{smiles}' AND solvent = '{solvent}' AND atom_analysed = {atom}
        ''')
        data = cursor.fetchone()
        electrofuge.append(data[0])
        nucleofuge.append(data[1])
        q_qtaim.append(data[2])
        if data[-1] == region:
            idx.append(i)

    cursor.close()

    electrofuge = np.array(electrofuge)[idx]
    nucleofuge = np.array(nucleofuge)[idx]
    q_qtaim = np.array(q_qtaim)[idx]

    exp_n = np.array(exp_n)[idx]
    exp_sn = np.array(exp_sn)[idx]

    return electrofuge, nucleofuge, q_qtaim, exp_n, exp_sn

# -------------------------
# 🚀
# -------------------------
if __name__ == "__main__":

    # Load the data
    dbpath = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db"
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    # Cluster, Region 1
    electrofuge, nucleofuge, q_qtaim, exp_n, exp_sn = region(dbpath, '2')

    # Equations
    n_inv = 94.4001/electrofuge 
    n_charge = 79.7440/electrofuge + 1.5418*nucleofuge + 2.3189*q_qtaim - 3.5977
    n_betap = (79.5572 + 0.6820*exp_sn)/electrofuge + 1.4762

    # R2 and MAE
    r2_inv = np.corrcoef(n_inv, exp_n)[0,1]**2
    r2_charge = np.corrcoef(n_charge, exp_n)[0,1]**2
    r2_betap = np.corrcoef(n_betap, exp_n)[0,1]**2
    mae_inv = np.mean(np.abs(n_inv - exp_n))
    mae_charge = np.mean(np.abs(n_charge - exp_n))
    mae_betap = np.mean(np.abs(n_betap - exp_n))

    # Plot
    plt.plot(n_inv, exp_n, 'o', label='Inv, R2 = {:.2f}, MAE = {:.2f}'.format(r2_inv, mae_inv))
    # plt.plot(n_charge, exp_n, 'o', label='Charge, R2 = {:.2f}, MAE = {:.2f}'.format(r2_charge, mae_charge))
    plt.plot(n_betap, exp_n, 'o', label='Beta+, R2 = {:.2f}, MAE = {:.2f}'.format(r2_betap, mae_betap))
    plt.plot([min(exp_n), max(exp_n)], [min(exp_n), max(exp_n)], 'k--')
    plt.xlabel('Predicted N')
    plt.ylabel('Experimental N')
    plt.legend()
    plt.show()

