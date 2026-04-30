#!/usr/bin/python3
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def parameters(dbpath):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    key = ['smiles', 'solvent', 'atom_analysed', 'experimental_Sn']
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
    smiles_list, solvents, atoms, exp_sn = zip(*parameters(dbpath))

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

    exp_sn = np.array(exp_sn)

    return q_qtaim, homo, exp_sn

# -------------------------
# Predict Sn
# -------------------------

def pred_sn(homo, q_qtaim):
    """ N = α*homo + β*q_qtaim + γ"""
    alpha, beta, gamma = 0.2480, 0.0197, 0.3444
    prediction = -alpha*homo - beta*q_qtaim + gamma
    return prediction

def plot_pred(exp_sn, sn_pred, mae, r2):
    plt.scatter(exp_sn, sn_pred, alpha=0.5)
    plt.plot([exp_sn.min(), exp_sn.max()], [exp_sn.min(), exp_sn.max()], 'k--', lw=2)
    plt.title('Experimental Sn value vs Predicted')
    plt.xlabel('Experimental Sn')
    plt.ylabel('Predicted Sn')
    textstr = '\n'.join((
        r'$MAE=%.3f$' % mae,
        r'$R^2=%.3f$' % r2,
        r'$S_n = \alpha HOMO + \beta q_{QTAIM} + \gamma$'
    ))
    plt.text(0.05, 0.95, textstr, transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top')
    plt.legend()
    plt.grid(True)
    plt.show()


# -------------------------
# Main script 🚀
# -------------------------

if __name__ == "__main__":

    # Load the data
    dbpath = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db"
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    homo, q_qtaim, exp_sn = q_homo_vals(dbpath)
    sn_pred = pred_sn(homo, q_qtaim)

    mae = np.mean(np.abs(exp_sn - sn_pred))
    r2 = 1 - np.sum((exp_sn - sn_pred)**2)/np.sum((exp_sn - np.mean(exp_sn))**2)

    plot_pred(exp_sn, sn_pred, mae, r2)

