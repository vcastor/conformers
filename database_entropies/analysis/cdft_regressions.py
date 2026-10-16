#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Load the data
def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT mu, eta, gamma, epsilon, rot_S, trans_S, vib_S, experimental_S, correctionS FROM all_molecules', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def generate_bounds(num_coeffs):
    return [(0, 1)] * num_coeffs

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ζ', 'η', 'θ', 'ι', 'κ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f'          | {formatted_coeffs}')

def obj_linear_model(coeffs, sr, st, sv, mu, eta, gamma, epsilon, missing, s_exp, model_name):
    if model_name == 'model0':
        predictions = coeffs[0]*(gamma - coeffs[1])**2 + np.log((mu + coeffs[2])**2)
    elif model_name == 'model1':
        predictions = np.exp(coeffs[0]*gamma) + np.log((mu + coeffs[1])**2)
    elif model_name == 'model2':
        predictions = 1/(coeffs[0] + 1/gamma)
    elif model_name == 'model3':
        predictions = np.log((mu + coeffs[0])**6/(gamma + coeffs[1])**12 + 1e-10)
    elif model_name == 'model4':
        predictions = (np.cosh(coeffs[0]*mu*eta) + coeffs[1])/epsilon
    elif model_name == 'model5':
        predictions = coeffs[0]*eta**coeffs[1]
    elif model_name == 'model6':
        predictions = st + (sv + coeffs[0]*epsilon)*np.exp(coeffs[1]*gamma)
        return np.sum((s_exp - predictions) ** 2)
    elif model_name == 'model7':
        predictions = coeffs[0]*sr + coeffs[1]*st + (coeffs[2]*sv + coeffs[3]*epsilon)*np.exp(-coeffs[4]*gamma)
        return np.sum((s_exp - predictions) ** 2)
    return np.sum((missing - predictions) ** 2)

def optimise_model(sr, st, sv, mu, eta, gamma, epsilon, missing, s_exp, model_name, num_coeffs):
    best_score, best_result = np.inf, None
    for _ in range(40):
        initial_guess = np.random.rand(num_coeffs)
        result = minimize(obj_linear_model, initial_guess, args=(sr, st, sv, mu, eta, gamma, epsilon, missing, s_exp, model_name), method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def models(data):
    # Just with Sr, St and Sv
    # 12.7529 | S = e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
    #         | λ: 0.0022
    #         | α: 0.4632, β: 0.5902, γ: 0.2493
    # Missing part 0:
    # S_exp - S_pred =
    # 1695.13300759205*(x2 - 0.1361452)**2 + log((x0 + 0.12201865)**2)
    # α*(gamma - β)**2 + log((mu + γ)**2)
    # Missing part 1:
    # S_exp - S_pred =
    # exp(12.106078*x2) + log((x0 + 0.121999994)**2)
    # Missing part 2:
    # S_exp - S_pred =
    # 1/(-3.6153426 + 1/x1)
    # 1/(α + 1/gamma)
    mu, eta, gamma = data['mu'], data['eta'], data['gamma']
    s_exp, epsilon = data['experimental_S'], data['epsilon']
    sr, st, sv = data['rot_S'], data['trans_S'], data['vib_S']
    gas = sr + st + sv
    pred = np.exp(-0.0022*epsilon)*(0.4632*sr + 0.5902*st + sv*sr/gas + 0.2493*sv*st/gas) + sv
    missing = s_exp - pred
    models = {
        'model0': {'num_coeffs': 3,
                   'formula': 'α(gamma - β)^2 + log((mu + γ)^2)'},
        'model1': {'num_coeffs': 2,
                   'formula': 'exp(α*gamma) + log((mu + β)^2)'},
        'model2': {'num_coeffs': 1,
                   'formula': '1/(α* + 1/gamma)'},
        'model3': {'num_coeffs': 2,
                   'formula': 'log((mu + α)^6/(gamma + β)^12)'},
        'model4': {'num_coeffs': 2,
                   'formula': '(cosh(α*mu*eta) - β)/epsilon'},
        'model5': {'num_coeffs': 2,
                   'formula': 'α*eta^β'},
        'model6': {'num_coeffs': 2,
                   'formula': 'St + (Sv + α*epsilon)*exp(β*gamma)'},
        'model7': {'num_coeffs': 5,
                   'formula': 'α*Sr + β*St + (γ*Sv + δ*epsilon)*e^(-ζ*gamma)'},
    }
    for model_name, model_info in models.items():
        result = optimise_model(sr, st, sv, mu, eta, gamma, epsilon, missing, s_exp, model_name, model_info['num_coeffs'])
        if result is not None:
            coeffs = result.x
            if model_name == 'model0':
                predictions = coeffs[0]*(gamma - coeffs[1])**2 + np.log((mu + coeffs[2])**2)
            elif model_name == 'model1':
                predictions = np.exp(coeffs[0]*gamma) + np.log((mu + coeffs[1])**2)
            elif model_name == 'model2':
                predictions = 1/(coeffs[0] + 1/gamma)
            elif model_name == 'model3':
                predictions = np.log((mu + coeffs[0])**6/(gamma + coeffs[1])**12 + 1e-10)
            elif model_name == 'model4':
                predictions = (np.cosh(coeffs[0]*mu*eta) + coeffs[1])/epsilon
            elif model_name == 'model5':
                predictions = coeffs[0]*eta**coeffs[1]
            elif model_name == 'model6':# S_exp
                predictions = st + (sv + coeffs[0]*epsilon)*np.exp(coeffs[1]*gamma)
                mae = np.mean(np.abs(s_exp - predictions))
                print(f'  {mae:6.2f}  | {model_info["formula"]}')
                print_coeffs(coeffs)
                # predictions += pred
            elif model_name == 'model7':
                predictions = coeffs[0]*sr + coeffs[1]*st + (coeffs[2]*sv + coeffs[3]*epsilon)*np.exp(-coeffs[4]*gamma)
                mae = np.mean(np.abs(s_exp - predictions))
                print(f'  {mae:6.2f}  | {model_info["formula"]}')
                print_coeffs(coeffs)
                # predictions += pred
            mae = np.mean(np.abs(missing - predictions))
            # print(f'  {mae:6.2f}  | {model_info["formula"]}')
            # print_coeffs(coeffs)

def no_opt_models(data):
    mu, eta, gamma = data['mu'], data['eta'], data['gamma']
    s_exp, epsilon = data['experimental_S'], data['epsilon']
    sr, st, sv = data['rot_S'], data['trans_S'], data['vib_S']
    gas = sr + st + sv
    pred = np.exp(-0.0022*epsilon)*(0.4632*sr + 0.5902*st + sv*sr/gas + 0.2493*sv*st/gas) + sv
    # | α(gamma - β)^2 + log((mu + γ)^2)
    # | α: 1686.3977, β: 0.1283, γ: 0.1220
    pred0 = pred + 1686.3977*(gamma - 0.1283)**2 + np.log((mu + 0.1220)**2 + 1e-10)
    print(f"  {np.mean(np.abs(s_exp - pred0)):6.2f}  | α(gamma - β)^2 + log((mu + γ)^2)")
    # | exp(α*gamma) + log((mu + β)^2)
    # | α: -8.0235, β: 19.8487
    pred1 = pred + np.exp(-8.0235*gamma) + np.log((mu + 19.8487)**2 + 1e-10)
    print(f"  {np.mean(np.abs(s_exp - pred1)):6.2f}  | exp(α*gamma) + log((mu + β)^2)")
    # | 1/(α + 1/gamma)
    # | α: -10.3329
    pred2 = pred + 1/(-10.3329 + 1/gamma)
    print(f"  {np.mean(np.abs(s_exp - pred2)):6.2f}  | 1/(α + 1/gamma)")
    # | log((mu + α)**6/(gamma - β)**12)
    # | α: 0.1223, β: -0.2872
    pred3 = pred + np.log((mu + 0.12594678)**6/(gamma - 0.2897794)**12 + 1e-10)
    print(f"  {np.mean(np.abs(s_exp - pred3)):6.2f}  | log((mu + α)**6/(gamma - β)**12)")
    # | (cosh(α*mu*eta) - β)/epsilon
    # | α: 142.0142, β: -41.8793
    pred4 = pred + (np.cosh(142.1042*mu*eta) - 41.8793)/epsilon
    print(f"  {np.mean(np.abs(s_exp - pred4)):6.2f}  | (cosh(α*mu*eta) + β)/epsilon")
    # | 15533537406.7985*x1**15.941084
    pred5 = pred + 15533537406.7985*eta**15.941084
    print(f"  {np.mean(np.abs(s_exp - pred5)):6.2f}  | 15533537406.7985*eta**15.941084")
    # | (exp(cosh(108.499913774279*x1**3)) - 26.519297)/x3
    #
    # trans_S, rot_S, vib_S, mu, eta, gamma, epsilon, experimental_S 
    # | x0 + (x2 - 0.58717936*x6)*exp(1.17290619530225*x5)
    pred6 = st + (sv - 0.58717936*epsilon)*np.exp(1.17290619530225*gamma)
    print(f"  {np.mean(np.abs(s_exp - pred6)):6.2f}  | x0 + (x2 - 0.58717936*x6)*exp(1.17290619530225*x5)")
    #
    # x0 + (x2 - 0.58717936*x6)*exp(1.17290619530225*x5)
    # pred7 = st + (sv - 0.58717936*epsilon)*np.exp(1.17290619530225*gamma)

    
def main():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    # plotter(data)
    # Run it, for the cases
    print('    MAE   |  Model')
    print('----------+--------------------------')
    models(data)
    # no_opt_models(data)

if __name__ == '__main__':
    main()

