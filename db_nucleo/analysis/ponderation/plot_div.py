#!/usr/bin/python3
import numpy as np
from matplotlib import pyplot as plt
from reader import read_data

def model_n(q, electrofuge, coff):
    alpha, beta = coff

    pred = alpha*q/electrofuge + beta

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
    q_list    = np.array([q[0] for q in data["q_qtaim"]])

    # Optimised values 
    coff = [-2.87963046, 13.72101802]

    # Model
    pred = model_n(q_list, electrofuge, coff)
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


