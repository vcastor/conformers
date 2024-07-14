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
        return pd.read_sql('SELECT mu, eta, gamma, epsilon, rot_S, trans_S, vib_S, experimental_S, correctionS FROM pbe0', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def generate_bounds(num_coeffs):
    return [(0, 1)] * num_coeffs

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ζ', 'η', 'θ', 'ι', 'κ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f'          | {formatted_coeffs}')

def obj_linear_model(coeffs, sr, st, sv, mu, eta, gamma, epsilon, s_exp, model_name):
    if model_name == 'model0':
        predictions = coeffs[0]*st + (coeffs[1]*sv + coeffs[2]*epsilon)*np.exp(-coeffs[3]*gamma)
    elif model_name == 'model1':
        predictions = coeffs[0]*sr + coeffs[1]*st + (coeffs[2]*sv + coeffs[3]*epsilon)*np.exp(-coeffs[4]*gamma)
    elif model_name == 'model2':
        predictions = coeffs[0]*st + coeffs[1]*sv*np.exp(coeffs[2]*eta**3) + coeffs[3]*eta*epsilon
    elif model_name == 'model3':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*eta**3) + coeffs[4]*eta*epsilon
    elif model_name == 'model4':
        predictions = np.abs(coeffs[0]*sv + coeffs[1])/np.abs((coeffs[2]*gamma*epsilon**(np.sqrt(coeffs[3]*gamma)))**(coeffs[4]*eta))
    elif model_name == 'model5':
        predictions = np.abs(coeffs[0]*sv + coeffs[1])/np.abs((coeffs[2]*gamma*epsilon**(np.sqrt(np.abs(coeffs[3]*gamma))))**(coeffs[4]*eta))
    elif model_name == 'model6':
        predictions = (coeffs[0]*sr + coeffs[1]*sv)**np.cosh(coeffs[2]*gamma) + coeffs[3]
    elif model_name == 'model7':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*epsilon*np.exp(coeffs[3]*gamma) + coeffs[4]*sv*np.exp(coeffs[5]*gamma)
    elif model_name == 'model8':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*np.exp(coeffs[3]*gamma)*sv
    elif model_name == 'model9':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*gamma*sv*(1 + coeffs[3]*epsilon)
    elif model_name == 'model10':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv - coeffs[3]*epsilon*sv*np.exp(coeffs[4]*gamma)
    elif model_name == 'model11':
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv + coeffs[3]*sv**(coeffs[4]*eta)
    elif model_name == 'model12':
        sgas = sr + st + sv
        predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*eta**3) + coeffs[4]*eta*epsilon*sv*sr/sgas
    elif model_name == 'model13':
        predictions = (coeffs[0]*sr + coeffs[1]*st)*np.exp(-coeffs[4]*epsilon) + coeffs[2]*sv + coeffs[3]*epsilon*np.exp(-coeffs[5]*gamma)
    elif model_name == 'model14':
        predictions = (coeffs[0]*sr + coeffs[1]*st)*np.exp(-coeffs[2]*epsilon) + (coeffs[3]*sv + coeffs[4]*epsilon)*np.exp(coeffs[5]*gamma)
    elif model_name == 'model15':
        predictions = coeffs[0]*(sr + st)*np.exp(-coeffs[2]*gamma) + coeffs[1]*sv*np.exp(coeffs[3]*epsilon)
    elif model_name == 'model16':
        predictions = coeffs[0]*(sr + st)*np.exp(-coeffs[2]*eta) + coeffs[1]*sv*np.exp(coeffs[3]*gamma)
    return np.sum((s_exp - predictions) ** 2)

def optimise_model(sr, st, sv, mu, eta, gamma, epsilon, s_exp, model_name, num_coeffs, bounds):
    best_score, best_result = np.inf, None
    for _ in range(40):
        initial_guess = np.random.rand(num_coeffs)
        result = minimize(obj_linear_model, initial_guess, bounds=bounds, args=(sr, st, sv, mu, eta, gamma, epsilon, s_exp, model_name), method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def models(data):
    mu, eta, gamma = data['mu'], data['eta'], data['gamma']
    s_exp, epsilon = data['experimental_S'], data['epsilon']
    sr, st, sv = data['rot_S'], data['trans_S'], data['vib_S']
    gas = sr + st + sv
    models = {
        'model0': {'num_coeffs': 4,
                   'bounds': [(0, 1), (0, 1), (-1, 1), (-2, 2)],
                   'formula': 'α*St + (β*Sv + γ*epsilon)*exp(-δ*gamma)'},
        'model1': {'num_coeffs': 5,
                   'bounds': [(0, 1), (0, 1), (0, 1), (-1, 1), (-np.inf, np.inf)],
                   'formula': 'α*Sr + β*St + (γ*Sv + δ*epsilon)*e^(-ζ*gamma)'},
        'model2': {'num_coeffs': 4,
                   'bounds': [(0, 1), (0, 1), (-20, 20), (-5, 5)],
                   'formula': 'α*St + β*Sv*e^(γ*eta^3) + δ*eta*epsilon'},
        'model3': {'num_coeffs': 5,
                   'bounds': [(0, 1), (0, 1), (0, 1), (-np.inf, np.inf), (-9, 9)],
                   'formula': 'α*Sr + β*St + γ*Sv*e^(δ*eta^3) + ζ*eta*epsilon'},
        'model4': {'num_coeffs': 5,
                   'bounds': [(0, 1), (0, 1000), (0.1, 1), (-9, 9), (-9, 9)],
                   'formula': '|α*Sv + β|/|(γ*gamma*epsilon^(sqrt(δ*gamma)))^(ζ*eta)|'},
        'model5': {'num_coeffs': 5,
                   'bounds': [(0, 1), (0, 1000), (0.01, 1), (0, np.inf), (-np.inf, np.inf)],
                   'formula': '|α*Sv + β|/|(γ*gamma*epsilon**(sqrt(|δ*gamma|)))**(δ*eta)|'},
        'model6' : {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (-np.inf, np.inf), (-300, 300)],
                    'formula': '(α*Sr + β*Sv)^cosh(γ*gamma) + δ'},
        'model7' : {'num_coeffs': 6,
                    'bounds': [(0, 1), (0, 1), (-np.inf, np.inf), (-5, 5), (0, 5), (-5, 5)],
                    'formula': 'α*Sr + β*St + γ*epsilon*exp(δ*gamma) + ζ*Sv*exp(η*gamma)'},
        'model8' : {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (0, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*Sr + β*St + γ*exp(δ*gamma)*Sv'},
        'model9' : {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (0, 9), (-9, 9)],
                    'formula': 'α*Sr + β*St + γ*gamma*Sv*(1+δ*epsilon)'},
        'model10' : {'num_coeffs': 5,
                    'bounds': [(0, 1), (0, 1), (0, 1), (-np.inf, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*Sr + β*St + γ*Sv - δ*epsilon*Sv*e^(ζ*gamma)'},
        'model11' : {'num_coeffs': 5,
                    'bounds': [(0, 1), (0, 1), (0, 1), (-np.inf, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*Sr + β*St + γ*Sv + δ*Sv^(ζ*eta)'},
        'model12': {'num_coeffs': 5,
                    'bounds': [(0, 1), (0, 1), (0, 1), (-20, 20), (-np.inf, np.inf)],
                    'formula': 'α*Sr β*St + γ*Sv*e^(δ*eta^3) + ζ*eta*epsilon*sv^2/sgas'},
        # e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
        #            'formula': 'α*St + (β*Sv + γ*epsilon)*exp(-δ*gamma)'},
        'model13': {'num_coeffs': 6,
                    'bounds': [(0, 1), (0, 1), (0, 1), (-3, 3), (0, np.inf), (0, np.inf)],
                    'formula': '(α*Sr + β*St)*exp(-ζ*epsilon) + γ*Sv + δ*epsilon*exp(-η*gamma)'},
        'model14': {'num_coeffs': 6,
                    'bounds': [(0, 1), (0, 1), (0, 0.5), (-1, 1), (-100, 100), (-np.inf, np.inf)],
                    'formula': '(α*Sr + β*St)*exp(-γ*epsilon) + (δ*Sv + ζ*epsilon)*exp(η*gamma)'},
        'model15': {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (0, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*(Sr + St)*exp(-γ*gamma) + β*Sv*exp(δ*epsilon)'},
        'model16': {'num_coeffs': 4,
                    'bounds': [(0, 1), (0, 1), (0, np.inf), (-np.inf, np.inf)],
                    'formula': 'α*(Sr + St)*exp(-γ*eta) + β*Sv*exp(δ*gamma)'},
    }
    for model_name, model_info in models.items():
        result = optimise_model(sr, st, sv, mu, eta, gamma, epsilon, s_exp, model_name, model_info['num_coeffs'], model_info['bounds'])
        if result is not None:
            coeffs = result.x
            if model_name == 'model0':
                predictions = coeffs[0]*st + (coeffs[1]*sv + coeffs[2]*epsilon)*np.exp(-coeffs[3]*gamma)
            elif model_name == 'model1':
                predictions = coeffs[0]*sr + coeffs[1]*st + (coeffs[2]*sv + coeffs[3]*epsilon)*np.exp(-coeffs[4]*gamma)
            elif model_name == 'model2':
                predictions = coeffs[0]*st + coeffs[1]*sv*np.exp(coeffs[2]*eta**3) + coeffs[3]*eta*epsilon
            elif model_name == 'model3':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*eta**3) + coeffs[4]*eta*epsilon
            elif model_name == 'model4':
                predictions = np.abs(coeffs[0]*sv + coeffs[1])/np.abs((coeffs[2]*gamma*epsilon**(np.sqrt(coeffs[3]*gamma)))**(coeffs[4]*eta))
            elif model_name == 'model5':
                predictions = np.abs(coeffs[0]*sv + coeffs[1])/np.abs((coeffs[2]*gamma*epsilon**(np.sqrt(np.abs(coeffs[3]*gamma))))**(coeffs[4]*eta))
            elif model_name == 'model6':
                predictions = (coeffs[0]*sr + coeffs[1]*sv)**np.cosh(coeffs[2]*gamma) + coeffs[3]
            elif model_name == 'model7':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*gamma) + coeffs[4]*sv*np.exp(coeffs[5]*gamma)
            elif model_name == 'model8':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*np.exp(coeffs[3]*gamma)*sv
            elif model_name == 'model9':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*gamma*sv*(1 + coeffs[3]*epsilon)
            elif model_name == 'model10':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv - coeffs[3]*epsilon*sv*np.exp(coeffs[4]*gamma)
            elif model_name == 'model11':
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv + coeffs[3]*sv**(coeffs[4]*eta)
            elif model_name == 'model12':
                sgas = sr + st + sv
                predictions = coeffs[0]*sr + coeffs[1]*st + coeffs[2]*sv*np.exp(coeffs[3]*eta**3) + coeffs[4]*eta*epsilon*sv*sr/sgas
            elif model_name == 'model13':
                predictions = (coeffs[0]*sr + coeffs[1]*st)*np.exp(-coeffs[4]*epsilon) + coeffs[2]*sv + coeffs[3]*epsilon*np.exp(-coeffs[5]*gamma)
            elif model_name == 'model14':
                predictions = (coeffs[0]*sr + coeffs[1]*st)*np.exp(-coeffs[2]*epsilon) + (coeffs[3]*sv + coeffs[4]*epsilon)*np.exp(coeffs[5]*gamma)
            elif model_name == 'model15':
                predictions = coeffs[0]*(sr + st)*np.exp(-coeffs[2]*gamma) + coeffs[1]*sv*np.exp(coeffs[3]*epsilon)
            elif model_name == 'model16':
                predictions = coeffs[0]*(sr + st)*np.exp(-coeffs[2]*eta) + coeffs[1]*sv*np.exp(coeffs[3]*gamma)
            mae = np.mean(np.abs(s_exp - predictions))
            diff=np.abs(s_exp-predictions)
            max_diff=np.max(diff)
            max_idx=np.argmax(diff)
            # print(max_idx, max_diff, s_exp[max_idx], predictions[max_idx])
            print(f'  {mae:6.2f}  | {model_info["formula"]}')
            print_coeffs(coeffs)

def no_model(data):
    # Abs(x2 + 129.85002)/Abs((x5*x6**(sqrt(x5)))**x4)
    sr, st, sv = data['rot_S'], data['trans_S'], data['vib_S']
    mu, eta, gamma = data['mu'], data['eta'], data['gamma']
    s_exp, epsilon = data['experimental_S'], data['epsilon']
    pred = np.abs(sv + 129.85002)/np.abs((gamma*epsilon**(np.sqrt(gamma)))**eta)
    mae = np.mean(np.abs(s_exp - pred))
    print(f'  {mae:6.2f}  | Abs(Sv + 129.85002)/Abs((gamma*epsilon**(sqrt(gamma)))**eta)')
    # (x1 + x2)**cosh(x5) + 43.268063
    pred = (sr + sv)**np.cosh(gamma) + 43.268063
    mae = np.mean(np.abs(s_exp - pred))
    print(f'  {mae:6.2f}  | (Sr + Sv)**cosh(gamma) + 43.268063')

def main():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    # plotter(data)
    # Run it, for the cases
    print('    MAE   |  Model')
    print('----------+--------------------------')
    models(data)
    # no_model(data)

if __name__ == '__main__':
    main()

#     MAE   |  Model
# ----------+--------------------------
#    10.32  | α*St + (β*Sv + γ*epsilon)*exp(-δ*gamma)
#           | α: 1.0000, β: 0.9221, γ: -0.5335, δ: -1.5294
#     9.71  | α*Sr + β*St + (γ*Sv + δ*epsilon)*e^(-ζ*gamma)
#           | α: 0.5425, β: 0.6639, γ: 0.7824, δ: -0.3979, ζ: -1.9725
#     9.87  | |α*St + β*Sv*e^(γ*eta^3) + δ*eta*epsilon|
#           | α: 1.0000, β: 1.0000, γ: 18.2478, δ: -3.2653
#     9.18  | |α*Sr + β*St + γ*Sv*e^(δ*eta^ζ) + δ*eta*epsilon|
#           | α: 0.4684, β: 0.7080, γ: 0.9789, δ: 257.1982, ζ: 5.0000, η: -2.6843
