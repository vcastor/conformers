#!/usr/bin/python3
import numpy as np
from scipy.optimize import least_squares
from .reader import read_data

def compute_predicted_N(params, distances_list, q_list, clr_list, elep_list, electrofuge):
    """
    Given the parameters (alpha, beta, gamma, delta, epsilon, zeta),
    and the full dataset (list of distance matrices, q/clr/ele arrays),
    return a 1D array of predicted N for *all* atoms in *all* systems.
    """
    alpha, beta, gamma, delta, epsilon, zeta, eta, theta = params
    
    predicted = []
    
    # Loop over all systems; target N or Sn
    for dist_vals, q_vals, clr_vals, elep_vals in zip(distances_list, q_list, clr_list, elep_list):
        
        exp_beta_dist  = np.exp(beta*dist_vals)
        exp_delta_dist = np.exp(delta*dist_vals)
        exp_zeta_dist  = np.exp(zeta*dist_vals)
            
        sum_q    = np.dot(exp_beta_dist, q_vals)
        sum_clr  = np.dot(exp_delta_dist,clr_vals)
        sum_elep = np.dot(exp_zeta_dist, elep_vals)
        elefuge  = eta*electrofuge
            
        # Nj = α Σ e^(β d_ij) q_i + γ Σ e^(δ d_ij) clr_i + ε Σ e^(ζ d_ij) elep_i
        #    + η electrofuge + θ
        N_j = (alpha*sum_q) + (gamma*sum_clr) + (epsilon*sum_elep) + elefuge + theta
            
        predicted.append(N_j)
    
    return np.array(predicted)


def residual(params, distances_list, q_list, clr_list, elep_list, electrofuge, N_exp):
    """
    Residual function = Predicted - Experimental, 
    for atoms across systems.
    """
    # Compute the model predictions for the entire dataset
    N_pred = compute_predicted_N(params, distances_list, q_list, clr_list, elep_list, electrofuge)
    N_pred = np.array(N_pred)
    return np.mean((N_pred - N_exp)**2)


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

    exp_vals = {
        'N_exp': N_exp,
        'Sn_exp': Sn_exp
    }

    # Initial guess for parameters: α, β, γ, δ, ε, ζ, η, θ
    p0 = [1.0, -0.1, 1.0, -0.1, 1.0, -0.1, 1.0, 1.0]


    print("α Σ e^(β d_ij) q_i + γ Σ e^(δ d_ij) clr_i + ε Σ e^(ζ d_ij) elep_i + η electrofuge + θ")
    print("Optimized parameters [alpha, beta, gamma, delta, epsilon, zeta, eta, theta]:")
    # Run the optimization
    for key, exp_val in exp_vals.items():
        result = least_squares(
            fun=residual,
            x0=p0,
            args=(distances_list, q_list, clr_list, elep_list, electrofuge, exp_val),
        )
        # Print the optimized parameters
        print(f"Results for {key}")
        print(" Optimized parameters:", result.x)
        print(" Residual:", result.cost)
        print(" Number of function evaluations:", result.nfev)
        print("")

