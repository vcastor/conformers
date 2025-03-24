#!/usr/bin/python3
import numpy as np
from matplotlib import pyplot as plt

def read_data(filename):
    data = {
        "natoms": [],
        "expN": [],
        "expSn": [],
        "distances": [],
        "q_qtaim": [],
        "clr": [],
        "electrostatic_potential": [],
        "electrofuge": []
    }
    with open(filename, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            data["natoms"].append(int(lines[i].strip()))
            i += 1

            expN, expSn = map(float, lines[i].split())
            data["expN"].append(expN)
            data["expSn"].append(expSn)
            i += 1

            data["distances"].append(list(map(float, lines[i].split())))
            i += 1

            data["q_qtaim"].append(list(map(float, lines[i].split())))
            i += 1

            data["clr"].append(list(map(float, lines[i].split())))
            i += 1

            data["electrostatic_potential"].append(list(map(float, lines[i].split())))
            i += 1

            data["electrofuge"].append(float(lines[i].strip()))
            i += 1

    return data

def model_nsn(sn_cont, distances_lst, q_lst, clr_lst, elep_lst, electrofuge_lst):
    alpha, beta, gamma, delta, epsilon, zeta, eta, theta = sn_cont
    # reference;
    # ['q_qtaim', 'condensed_linear_response', 'electrofuge']
    # invele = q_qtaim + 90.80866/electrofuge

    pred = []
    for distances, q, clr, elep, electrofuge in zip(distances_list, q_list, clr_list, elep_list, electrofuge_lst):
        exp_beta  = np.exp(beta*distances)
        exp_delta = np.exp(delta*distances)
        exp_zeta  = np.exp(zeta*distances)

        sum_q    = np.dot(exp_beta, q)
        sum_clr  = np.dot(exp_delta, clr)
        sum_elep = np.dot(exp_zeta, elep)
        elefuge  = eta*electrofuge

        # nj = alpha*sum_q + gamma*sum_clr + epsilon*sum_elep + elefuge + theta
        nj = q[0] + 90.80866/electrofuge
        pred.append(nj)

    return np.array(pred)

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
    sn_cont = [0.99779505, -0.09522693, 0.22968717, -1.12669661, 0.02784221, -0.69939571, 0.0642452, 0.88250183]
    n_cont  = [0.99667521, -0.06944356, -0.1528218,  -0.95266161,  0.03575661, -0.65171434, 1.37795562,  1.31294067]

    # Model
    # α Σ e^(β d_ij) q_i + γ Σ e^(δ d_ij) clr_i + ε Σ e^(ζ d_ij) elep_i + η electrofuge + θ
    # pred = model_nsn(sn_cont, distances_list, q_list, clr_list, elep_list, electrofuge)
    pred = model_nsn(n_cont, distances_list, q_list, clr_list, elep_list, electrofuge)

    invele = 90.80866/electrofuge

    # Plot predicted vs experimental, one plot
    plt.figure(figsize=(6,6))
    plt.plot([pred.min(), pred.max()], [pred.min(), pred.max()], 'k--', lw=2)
    plt.scatter(N_exp, pred, alpha=0.7)
    plt.scatter(N_exp, invele, alpha=0.7)
    plt.xlabel('Experimental N')
    plt.ylabel('Predicted N')
    plt.title('N')
    plt.show()


