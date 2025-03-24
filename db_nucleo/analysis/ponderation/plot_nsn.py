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

    # Plot predicted vs experimental, one plot
    plt.figure(figsize=(6,6))
    # plt.plot([pred.min(), pred.max()], [pred.min(), pred.max()], 'k--', lw=2)
    plt.scatter(N_exp, Sn_exp, alpha=0.7)
    plt.xlabel('Experimental N')
    plt.ylabel('Experimental Sn')
    plt.show()


