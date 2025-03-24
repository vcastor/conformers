#!/usr/bin/python3
import numpy as np
from matplotlib import pyplot as plt
from reader import read_data

def model_n(distances_list, q_list, electrofuge, coff):
    alpha, beta, gamma, delta = coff

    q_contrib = []
    for distances, q in zip(distances_list, q_list):
        beta_exp = np.exp(-beta*(distances**2))
        q_contrib.append(np.dot(beta_exp, q))

    q_contrib = np.array(q_contrib)

    pred = alpha*q_contrib + gamma/electrofuge + delta

    return pred

# -------------------------
# 🚀
# -------------------------

if __name__ == "__main__":

    # Read the reactive data [ALL CONFORMERS]
    valuefile = 'reactive.pout'
    data = read_data(valuefile)

    # One value per system
    natoms = np.array(data["natoms"])
    N_exp  = np.array(data["expN"])
    Sn_exp = np.array(data["expSn"])
    electrofuge = np.array(data["electrofuge"])

    # One array per system
    distances_list = [np.array(d) for d in data["distances"]]
    q_list    = [np.array(q) for q in data["q_qtaim"]]
    clr_list  = [np.array(c) for c in data["clr"]]
    elep_list = [np.array(e) for e in data["electrostatic_potential"]]

    # Optimised values 
    # coff = [-2.70582936, 0.76420001, 113.73834686, -3.14600968] # linear
    coff = [-3.02679059, 0.57601411, 114.06462994, -3.21989228]

    # Model
    pred = model_n(distances_list, q_list, electrofuge, coff)
    st_dev = np.std(N_exp - pred)
    r2 = np.corrcoef(N_exp, pred)[0,1]**2

    # Plot predicted vs experimental, one plot
    plt.figure(figsize=(6,6))
    plt.plot([pred.min(), pred.max()], [pred.min(), pred.max()], 'k--', lw=2)
    plt.scatter(N_exp, pred, alpha=0.7)
    plt.xlabel('Experimental N')
    plt.ylabel('Predicted N')
    plt.title(f'N: R²={r2:.2f}, σ={st_dev:.2f}')
    plt.show()


