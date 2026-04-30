#!/usr/bin/python3
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from sklearn.metrics import r2_score

def parameters(dbpath):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    key = ['smiles', 'solvent', 'atom_analysed', 'experimental_N']
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
    smiles_list, solvents, atoms, exp_n = zip(*parameters(dbpath))

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

    exp_n = np.array(exp_n)

    return q_qtaim, homo, exp_n

# -------------------------
# Predict Sn
# -------------------------

def pred_n(homo, q_qtaim):
    """ N = α/homo + β*q_qtaim + γ"""
    alpha, beta, gamma = 6.7881, 3.3477, 38.4893
    prediction = alpha/homo + beta*q_qtaim + gamma
    return prediction

def plot_pred(exp_n, n_pred, mae, r2):
    plt.scatter(exp_n, n_pred, alpha=0.5)
    plt.plot([exp_n.min(), exp_n.max()], [exp_n.min(), exp_n.max()], 'k--', lw=2)
    plt.title('Experimental N value vs Predicted')
    plt.xlabel('Experimental N')
    plt.ylabel('Predicted N')
    textstr = '\n'.join((
        r'$MAE=%.3f$' % mae,
        r'$R^2=%.3f$' % r2,
        r'$N = \frac{\alpha}{HOMO} + \beta q_{QTAIM} + \gamma$'
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

    homo, q_qtaim, exp_n = q_homo_vals(dbpath)
    n_pred = pred_n(homo, q_qtaim)

    mae = np.mean(np.abs(exp_n - n_pred))
    # r2 = 1 - np.sum((exp_n - n_pred)**2)/np.sum((exp_n - np.mean(exp_n))**2)
    r2 = r2_score(exp_n, n_pred)

    plot_pred(exp_n, n_pred, mae, r2)

