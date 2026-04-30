#!/usr/bin/python3
import sqlite3
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def all_sn(dbpath):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT experimental_Sn
        FROM parameters
        WHERE table_name = 'reactive'
          AND (comment IS NULL OR comment != 'exclude')
    ''')
    sn = cursor.fetchall()
    cursor.close()
    return [val[0] for val in sn]

def parameters(dbpath, case):
    key = ['smiles', 'solvent', 'atom_analysed', 'experimental_N', 'experimental_Sn']
    query = f'''
        SELECT {', '.join(key)}
        FROM parameters
        WHERE table_name = 'reactive'
          AND (comment IS NULL OR comment != 'exclude')
    '''
    exclusions = {
        'aliphatic_amines':         "family = 'aliphatic_amines'",
        'pyridines_quinolines_etc': "family = 'pyridines_quinolines_etc'",
        'region1': "family != 'pyridines_quinolines_etc'",
        'region2': "family != 'aliphatic_amines'"
    }

    if case in exclusions:
        query += f" AND {exclusions[case]}"

    with sqlite3.connect(dbpath) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

def region(dbpath, case):
    data = parameters(dbpath, case)
    smiles_list, solvents, atoms, exp_n, exp_sn = zip(*data)

    descriptors = ['electrofuge', 'nucleofuge', 'P', 'region']
    electrofuge, nucleofuge, p, region = [], [], [], []

    with sqlite3.connect(dbpath) as conn:
        cursor = conn.cursor()
        for smiles, solvent, atom in zip(smiles_list, solvents, atoms):
            cursor.execute(f'''
                SELECT {', '.join(descriptors)}
                  FROM reactive
                  WHERE smiles = '{smiles}'
                    AND solvent = '{solvent}'
                    AND atom_analysed = {atom}
            ''')
            result = cursor.fetchone()
            electrofuge.append(result[0])
            nucleofuge.append(result[1])
            p.append(result[2])
            region.append(result[3])

    electrofuge = np.array(electrofuge)
    nucleofuge  = np.array(nucleofuge)
    p      = np.array(p)
    exp_n  = np.array(exp_n)
    exp_sn = np.array(exp_sn)

    if case == 'region1':
        mask = np.array(region) == '1'
    elif case == 'region2':
        mask = np.array(region) == '2'
    else:
        mask = slice(None)

    return (
        electrofuge[mask], nucleofuge[mask], p[mask],
        exp_n[mask], exp_sn[mask]
    )

def prediction(electrofuge, nucleofuge, p, case):
    # electrofuge = np.array(electrofuge, dtype=float)
    # nucleofuge  = np.array(nucleofuge, dtype=float)
    # p = np.array(p, dtype=float)
    if case == 'aliphatic_amines':
        # alpha, beta, gamma = 0.2979, 0.1505, 0.3027
        # pred = alpha**(nucleofuge**beta) + gamma
        pred = (np.log(0.0052325465/nucleofuge)**2)**(-0.15129869)
        return pred
    if case == 'pyridines_quinolines_etc':
        alpha, beta = 1.8610, 0.9479
        return -alpha/electrofuge + beta
    if case == 'region1':
        alpha, beta = 0.6596, 0.6619
        return alpha/p + beta
    if case == 'region2':
        alpha, beta, gamma = 17.0478, 0.0014, -16.4415
        pred = alpha/(nucleofuge**beta) + gamma
        return pred

# -------------------------
# Main script 🚀
# -------------------------

# Load the data
dbpath = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db"
conn = sqlite3.connect(dbpath)
cursor = conn.cursor()

all_exp_sn = np.array(all_sn(dbpath))
plt.plot([all_exp_sn.min(), all_exp_sn.max()], [all_exp_sn.min(), all_exp_sn.max()], 'k--', lw=2)
plt.xlabel('Experimental Sn')
plt.ylabel('Predicted Sn')
plt.title('Comparison between experimental and predicted Sn')

cases = ['aliphatic_amines', 'pyridines_quinolines_etc', 'region1', 'region2']

for case in cases:
    electrofuge, nucleofuge, p, exp_n, exp_sn = region(dbpath, case)
    pred = prediction(electrofuge, nucleofuge, p, case)
    mae = np.mean(np.abs(exp_sn - pred))
    r2 = 1 - np.sum((exp_sn - pred)**2)/np.sum((exp_sn - np.mean(exp_sn))**2)
    plt.scatter(exp_sn, pred, label=f'{case} (MAE={mae:.2f}, R²={r2:.2f})')
plt.legend()
plt.show()





