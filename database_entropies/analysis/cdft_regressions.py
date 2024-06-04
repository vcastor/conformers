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
        return pd.read_sql('SELECT mu, eta, gamma, epsilon, experimental_S, correctionS FROM molecules', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def generate_bounds(num_coeffs):
    return [(0, 1)] * num_coeffs

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ζ', 'η', 'θ', 'ι', 'κ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f'          | {formatted_coeffs}')

def obj_linear_model(coeffs, mu, eta, gamma, s_exp, model_name):
    if model_name == 'model0':
        predictions = coeffs[0] - 1/(coeffs[1] - eta)
    return np.sum((s_exp - predictions) ** 2)

def optimise_linear_model(mu, eta, gamma, s_exp, model_name, num_coeffs):
    best_score, best_result = np.inf, None
    for _ in range(40):
        initial_guess = np.random.rand(num_coeffs)
        result = minimize(obj_linear_model, initial_guess, args=(mu, eta, gamma, s_exp, model_name), method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def linear_models(data):
    # 245.53801 - 1/(0.24949844 - x1)
    mu, eta, gamma = data['mu'], data['eta'], data['gamma']
    s_exp = data['experimental_S']
    models = {
        'model0': {'num_coeffs': 2,
                   'formula': 'α - 1/(β - η)'},
        # 'model4': {'num_coeffs': 4,
        #            'formula': 'α*S_r + β*S_t + S_v + γ*S_vct/S^c_gas + δ*S_vcr/S^c_gas'}
    }
    for model_name, model_info in models.items():
        result = optimise_linear_model(mu, eta, gamma, s_exp, model_name, model_info['num_coeffs'])
        if result is not None:
            coeffs = result.x
            if model_name == 'model0':
                predictions = coeffs[0] - 1/(coeffs[1] - eta)
            mae = np.mean(np.abs(s_exp - predictions))
            print(f'          |')
            print(f'  {mae:6.4f} | S = {model_info["formula"]}')
            print_coeffs(coeffs)

def no_opt_models(data):
    # 245.53801 - 1/(0.24949844 - x1)
    predic = 245.53801 - 1/(0.24949844 - data['eta'])
    print(f"  {np.mean(np.abs(data['experimental_S'] - predic)):6.2f}  | S = 245.53801 - 1/(0.24949844 - η)")
    
def set_correctionS_to_zero(data):
    data.loc[data['correctionS'] > 0, 'correctionS'] = 0
    return data

def main():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    # Run it, for the cases
    print('    MAE   |  Model')
    print('----------+--------------------------')
    linear_models(data)

if __name__ == '__main__':
    main()
    quit()

