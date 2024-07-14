#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sqlite3
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error

# Load the data
def fetch_data(db_file_path, table_name='all_molecules'):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql(f'SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM {table_name}', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ζ', 'η', 'θ', 'ι', 'κ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f'          | {formatted_coeffs}')

def obj_model(coeffs, srot, strans, svib, s_exp, epsilon, model_name):
    sgas = srot + strans + svib
    if model_name == 'linear':
        predictions = coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib
    elif model_name == 'cross_terms':
        predictions = coeffs[0]*(srot + strans) + coeffs[1]*svib + coeffs[2]*svib*(srot + strans)/sgas
    elif model_name == 'exp_agrouped':
        predictions = np.exp(-coeffs[-1]*epsilon)*(coeffs[0]*(srot + strans) +
                                                   coeffs[1]*svib +
                                                   coeffs[2]*svib*(srot + strans)/sgas)
    elif model_name == 'exp_separated':
        predictions = np.exp(-coeffs[-1]*epsilon)*(coeffs[0]*srot +
                                                   coeffs[1]*strans +
                                                   coeffs[2]*svib +
                                                   coeffs[3]*svib*srot/sgas +
                                                   coeffs[4]*svib*strans/sgas)
    elif model_name == 'splited':
        predictions = (np.exp(-coeffs[-1]*epsilon)*(coeffs[0]*srot +
                                                    coeffs[1]*strans +
                                                    coeffs[2]*svib*srot/sgas +
                                                    coeffs[3]*svib*strans/sgas) +
                       coeffs[4]*svib)
    return np.sum((s_exp - predictions)**2)

def opt_model(srot, strans, svib, s_exp, epsilon, model_name, nlin_coeffs, nexp_coeffs=0):
    bounds = [(0, 1)]*nlin_coeffs + [(0, 0.05)]*nexp_coeffs
    best_score, best_result = np.inf, None
    for _ in range(40):
        initial_guess = np.concatenate([np.random.uniform(0, 1, nlin_coeffs), np.random.uniform(0, 0.005, nexp_coeffs)])
        result = minimize(obj_model, initial_guess, args=(srot, strans, svib, s_exp, epsilon, model_name), bounds=bounds, method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def run_models(data):
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    epsilon, s_exp = data['epsilon'], data['experimental_S']
    models = {
        'linear': {'nlin_coeffs': 3, 'nexp_coeffs': 0,
                   'formula': 'α*S_r + β*S_t + γ*S_v'},
        'cross_terms': {'nlin_coeffs': 3, 'nexp_coeffs': 0,
                   'formula': 'α*(S_r + S_t) + β*S_v + γ*S_v(S_r + S_t)/S_gas'},
        'exp_agrouped': {'nlin_coeffs': 3, 'nexp_coeffs': 1,
                   'formula': 'e^(-λ*ε)[α*(S_r + S_t) + β*S_v + γ*S_v*(S_r + S_t)/S_gas]'},
        'exp_separated': {'nlin_coeffs': 5, 'nexp_coeffs': 1,
                   'formula': 'e^(-λ*ε)[α*S_r + β*S_t + γ*S_v + δ*S_v*S_r/S_gas + ζ*S_v*S_t/S_gas]'},
        'splited': {'nlin_coeffs': 5, 'nexp_coeffs': 1,
                   'formula': 'e^(-λ*ε)[α*S_r + β*S_t + γ*S_v*S_r/S_gas + δ*S_v*S_t/S_gas] + ζ*S_v'}
    }
    kf = KFold(n_splits=10, shuffle=True)
    for model_name, model_info in models.items():
        maes = []
        for train_index, test_index in kf.split(data):
            srot_train, strans_train, svib_train = srot[train_index], strans[train_index], svib[train_index]
            epsilon_train, s_exp_train = epsilon[train_index], s_exp[train_index]
            srot_test, strans_test, svib_test = srot[test_index], strans[test_index], svib[test_index]
            epsilon_test, s_exp_test = epsilon[test_index], s_exp[test_index]
            # Run the optimization
            result = opt_model(srot_train, strans_train, svib_train, s_exp_train, epsilon_train, model_name, model_info['nlin_coeffs'], model_info['nexp_coeffs'])
            if result is not None:
                coeffs = result.x
                sgas = srot_test + strans_test + svib_test
                if model_name == 'linear':
                    predictions = coeffs[0]*srot_test + coeffs[1]*strans_test + coeffs[2]*svib_test
                elif model_name == 'cross_terms':
                    predictions = (coeffs[0]*(srot_test + strans_test) + coeffs[1]*svib_test +
                                   coeffs[2]*svib_test*(srot_test + strans_test)/sgas)
                elif model_name == 'exp_agrouped':
                    predictions = np.exp(-coeffs[-1]*epsilon_test)*(coeffs[0]*(srot_test + strans_test) +
                                                                    coeffs[1]*svib_test +
                                                                    coeffs[2]*svib_test*(srot_test + strans_test)/sgas)
                elif model_name == 'exp_separated':
                    predictions = np.exp(-coeffs[-1]*epsilon_test)*(coeffs[0]*srot_test +
                                                                    coeffs[1]*strans_test +
                                                                    coeffs[2]*svib_test +
                                                                    coeffs[3]*svib_test*srot_test/sgas +
                                                                    coeffs[4]*svib_test*strans_test/sgas)
                elif model_name == 'splited':
                    predictions = (np.exp(-coeffs[-1]*epsilon_test)*(coeffs[0]*srot_test +
                                                                     coeffs[1]*strans_test +
                                                                     coeffs[2]*svib_test*srot_test/sgas +
                                                                     coeffs[3]*svib_test*strans_test/sgas) +
                                   coeffs[4]*svib_test)
                maes.append(mean_absolute_error(s_exp_test, predictions))
        avg_mae = np.mean(maes)
        print(f'          |')
        print(f'  {avg_mae:6.4f} | S = {model_info["formula"]}')
        if model_info['nexp_coeffs'] > 0:
            print(f'          | λ: {coeffs[-1]:.4f}')
        print_coeffs(coeffs[:model_info['nlin_coeffs']])

def no_opt_models(data):
    gas_phase = data['rot_S'] + data['trans_S'] + data['vib_S']
    twothirds = 2/3*data['rot_S'] + 2/3*data['trans_S'] + data['vib_S']
    gas_phase_corr = gas_phase + data['correctionS']
    print(f"  {np.mean(np.abs(data['experimental_S'] - gas_phase)):6.2f}  | S = S_r + S_t + S_v")
    print(f'          |')
    print(f"  {np.mean(np.abs(data['experimental_S'] - gas_phase_corr)):6.2f}  | S = S_r + S_t + S_v + ΔS_corr")
    print(f'          |')
    print(f"  {np.mean(np.abs(data['experimental_S'] - twothirds)):6.2f}  | S = 2/3*(S_r + S_t) + S_v")
    print(f'          |')
    
def main():
    functionals = ['PBE', 'PBE0']
    for functional in functionals:
        data = fetch_data('../entropiesCOSMO.db', table_name=functional)
        data = prepare_data(data)
        print(f'Functional: {functional}')
        print('    MAE   |  Model')
        print('----------+--------------------------')
        no_opt_models(data)
        run_models(data)

if __name__ == '__main__':
    main()

