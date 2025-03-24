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
        FROM parameters WHERE table_name = 'reactive'
        AND (comment IS NULL OR comment != 'exclude')
    ''')
    params = cursor.fetchall()
    
    cursor.close()
    return params

def region(dbpath, region):
    smiles_list, solvents, atoms, exp_n, exp_sn = zip(*parameters(dbpath))

    features = ['electrofuge', 'nucleofuge', 'q_qtaim', 'region']
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
        if data[-1] == region:
            idx.append(i)

    cursor.close()

    electrofuge = np.array(electrofuge)[idx]
    nucleofuge  = np.array(nucleofuge)[idx]
    q_qtaim = np.array(q_qtaim)[idx]

    exp_n  = np.array(exp_n)[idx]
    exp_sn = np.array(exp_sn)[idx]

    return electrofuge, nucleofuge, q_qtaim, exp_n, exp_sn

def with_max_diff(dbpath, max_diff, exp_n, exp_sn):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    smiles_list, solvents = [], []
    key = ['smiles', 'solvent']
    for idx in max_diff:
        cursor.execute(f'''
            SELECT {', '.join(key)}
              FROM parameters
              WHERE experimental_N = {exp_n[idx]}
                AND experimental_Sn = {exp_sn[idx]}
              ''')
        chem = cursor.fetchall()
        for che in chem:
            smiles_list.append(che[0])
            solvents.append(che[1])

    cursor.close()
    return smiles_list, solvents

def prediction(electrofuge, nucleofuge, q_qtaim):
    """ N = α/electrofuge + β*nucleofuge + γ*q_qtaim + δ"""
    prediction = 93.4616/electrofuge - 4.5164*nucleofuge - 20.4578*q_qtaim - 20.6436
    return prediction

# -------------------------
# Main script 🚀
# -------------------------

if __name__ == "__main__":

    # Load the data
    dbpath = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db"
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    # Loop for Regions
    for regionval in ['1', '2']:
        print(f"===Region: {regionval}===")
        electrofuge, nucleofuge, q_qtaim, exp_n, exp_sn = region(dbpath, regionval)

        predN = prediction(electrofuge, nucleofuge, q_qtaim)
        idx_mx_diff = np.argsort(np.abs(predN - exp_n))[-5:]

        smiles_list, solvents = with_max_diff(dbpath, idx_mx_diff, exp_n, exp_sn)

        for i in range(5):
            print(f"{predN[idx_mx_diff[i]] - exp_n[idx_mx_diff[i]]}: {smiles_list[i]} {solvents[i]}")


