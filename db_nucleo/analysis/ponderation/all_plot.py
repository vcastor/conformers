#!/usr/bin/python3
import sqlite3
import numpy as np
from reader import data_pond
from matplotlib import pyplot as plt

DB_PATH = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db"
POUTBASE = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/analysis/ponderation/reactive.pout"

def get_parameters(dbpath, where_clause):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT smiles, solvent, atom_analysed, experimental_N, experimental_Sn
        FROM parameters
        WHERE table_name = 'reactive' AND (comment IS NULL OR comment != 'exclude') {where_clause}
    ''')
    data = cursor.fetchall()
    cursor.close()
    return data

def extract_features(dbpath, params, required_keys, region_code=None):
    smiles_list, solvents, atoms, exp_n, exp_sn = zip(*params)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    data = {key: [] for key in required_keys}
    valid_idx = []

    for i, (smi, solv, at) in enumerate(zip(smiles_list, solvents, atoms)):
        cursor.execute(f'''
            SELECT {', '.join(required_keys)}, region
            FROM reactive
            WHERE smiles = ? AND solvent = ? AND atom_analysed = ?
        ''', (smi, solv, at))
        row = cursor.fetchone()
        if region_code is not None and row[-1] != region_code:
            continue
        for k, v in zip(required_keys, row[:-1]):
            data[k].append(v)
        valid_idx.append(i)

    cursor.close()
    arr = {k: np.array(v) for k, v in data.items()}
    exp_n = np.array(exp_n)[valid_idx]
    exp_sn = np.array(exp_sn)[valid_idx]
    return arr, exp_n, exp_sn

# -------------------------
# Prediction Models
# -------------------------

def all_region1(e, n, d, q):
    """N = α/electrofuge - β*nucleofuge - γ*Σe^(-δd)q_qtaim - ε"""
    alpha, beta, gamma = 109.1573, 3.8812, 1.0377
    delta, epsilon = 0.4198, 2.6426
    preds = []
    for ele, nuc, dist, qval in zip(e, n, d, q):
        w = np.exp(-delta*dist**2)
        preds.append(alpha/ele - beta*nuc - gamma*np.dot(w, qval) - epsilon)
    return np.array(preds)

def model_no_pyridines(e, d, q, c, el, p, h):
    """N = α/electrofuge - β*Σe^(-γd)q_qtaim + δ*Σe^(-εd)clr + ζ*Σe^(-ηd)*elp/pop + θ/HOMO + ι"""
    alpha, beta, gamma = 23.1054, 8.9104, 0.1153
    delta, epsilon, zeta = 0.2404, 0.0381, 0.2989
    eta, theta, iot = 0.0167, -59.0422, -2.9176
    preds = []
    for ele, dist, qv, cv, elv, popv, hom in zip(e, d, q, c, el, p, h):
        wq = np.exp(-gamma * dist**2)
        wc = np.exp(-epsilon * dist**2)
        we = np.exp(-eta * dist**2)
        sum_q = np.dot(wq, qv)
        sum_clr = np.dot(wc, cv)
        sum_elp = np.dot(we, elv/popv)
        preds.append(alpha/ele - beta*sum_q + delta*sum_clr + zeta*sum_elp + theta/hom + iot)
    return np.array(preds)

def model_aliphatic(h):
    """N = -α/HOMO - β"""
    alpha, beta = 137.7566, 9.7247
    return -beta/h - gamma

# -------------------------
# Plotting
# -------------------------

def plot_predictions():
    plt.figure()

    # 1. All region 1
    p_all = get_parameters(DB_PATH, "AND experimental_N > 10")
    feat_all, exp_n_all, exp_sn_all = extract_features(DB_PATH, p_all, ['electrofuge', 'nucleofuge'], region_code='1')
    dist1, q1, _, _, _ = data_pond(POUTBASE, exp_n_all, exp_sn_all)
    pred1 = all_region1(feat_all['electrofuge'], feat_all['nucleofuge'], dist1, q1)
    mae = np.mean(np.abs(exp_n_all - pred1))
    texteq = r"$N = \frac{\alpha}{\text{electrofuge}} - \beta\text{nucleofuge} - \gamma\sum e^{-\delta d^2}q_{\text{qtaim}} - \epsilon$"
    plt.scatter(exp_n_all, pred1, alpha=0.6, label=f"Region 1 (all) MAE={mae:.2f}\n{texteq}")

    # 2. Region 1 without pyridines
    p_r1wo = get_parameters(DB_PATH, "AND family != 'pyridines_quinolines_etc'")
    feat_r1wo, exp_n_r1wo, exp_sn_r1wo = extract_features(DB_PATH, p_r1wo, ['electrofuge', 'nucleofuge', 'HOMO'], region_code='1')
    dist2, q2, clr2, elp2, pop2 = data_pond(POUTBASE, exp_n_r1wo, exp_sn_r1wo)
    pred2 = model_no_pyridines(feat_r1wo['electrofuge'], dist2, q2, clr2, elp2, pop2, feat_r1wo['HOMO'])
    mae = np.mean(np.abs(exp_n_r1wo - pred2))
    texteq = r"$N = \frac{\alpha}{\text{electrofuge}} - \beta\sum e^{-\gamma d^2}clr + \zeta\sum e^{-\eta d^2}\frac{elp}{pop} + \frac{\theta}{HOMO} + \iot$"
    plt.scatter(exp_n_r1wo, pred2, alpha=0.6, label='Region 1 (no pyridines) MAE={mae:.2f}\n{texteq}')

    # 3. Aliphatic amines region 2
    p_r2 = get_parameters(DB_PATH, "AND family = 'aliphatic_amines' AND experimental_N > 10 AND experimental_N < 20")
    feat_r2, exp_n_r2, exp_sn_r2 = extract_features(DB_PATH, p_r2, ['nucleofuge', 'HOMO', 'q_qtaim'], region_code='2')
    pred3 = model_aliphatic(feat_r2['nucleofuge'], feat_r2['HOMO'], feat_r2['q_qtaim'])
    mae = np.mean(np.abs(exp_n_r2 - pred3))
    texteq = r"$N = -\frac{\alpha}{\text{HOMO}} - \beta$"
    plt.scatter(exp_n_r2, pred3, alpha=0.6, label='Aliphatic MAE={mae:.2f}\n{texteq}')

    # Identity line
    all_preds = np.concatenate([pred1, pred2, pred3])
    all_exp   = np.concatenate([exp_n_all, exp_n_r1wo, exp_n_r2])
    lims = [all_exp.min(), all_exp.max()]
    plt.plot(lims, lims, 'k--', lw=2)

    # Labels and legend
    plt.xlabel("Experimental N")
    plt.ylabel("Predicted N")
    plt.legend()
    plt.title("Comparison of N Predictions Across Regions")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_predictions()

