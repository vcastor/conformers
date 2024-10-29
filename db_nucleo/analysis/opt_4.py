#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
from scipy.optimize import minimize

# Load the data
def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('''SELECT experimental_N, experimental_Sn,
                                     mu, eta, softness, hyperhardness, omega,
                                     nucleofuge, electrofuge, electrodonating, electroaccepting, fplus, fminus, fzero,
                                     f2, sfplus, sfminus, sfzero, s2, muplusfplus, muminusfminus, wfplus, wf2,
                                     Sf2, s2f2, electro, nucleo, q_qtaim, q_hirshfeld
                              FROM main WHERE atom_analysed > 0 AND nconformers not null''', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ε']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f'          | {formatted_coeffs}')

# Objective functions
def obj_model_sn(coeffs, X, s_exp, model):
    if model == 'model1':
        predictions = coeffs[0]*X[:,8] + coeffs[1]*X[:,26] + coeffs[2]
    elif model == 'model2':
        predictions = coeffs[0]*X[:,8] + coeffs[1]
    elif model == 'model3':
        predictions = coeffs[0]*X[:,4] + coeffs[1]*X[:,0] + coeffs[2]
    return np.sum((s_exp - predictions)**2)

def obj_model_n(coeffs, X, s_exp, model):
    if model == 'model1':
        predictions = coeffs[0]*X[:,6] + coeffs[1]
    elif model == 'model2':
        predictions = coeffs[0]/X[:,7] + coeffs[1]*X[:,2] + coeffs[2]
    elif model == 'model3':
        predictions = (coeffs[0]/X[:,7] + coeffs[1]/X[:,20] + coeffs[2]*X[:,2] +
                       coeffs[3]*X[:,25] + coeffs[4])
    return np.sum((s_exp - predictions)**2)

def optimize_model(X, s_exp, model, obj_func, num_coeffs):
    best_score, best_result = np.inf, None
    for _ in range(20):
        initial_guess = np.random.rand(num_coeffs)
        result = minimize(obj_func, initial_guess, args=(X, s_exp, model), method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def evaluate_models(data):
    X = data.iloc[:, 2:].values
    s_exp_sn, s_exp_n = data['experimental_Sn'], data['experimental_N']

    models_Sn = {
        'model1': {'num_coeffs': 3, 'formula': 'α*X8 + β*X26 + γ'},
        'model2': {'num_coeffs': 2, 'formula': 'α*X8 + β'},
        'model3': {'num_coeffs': 3, 'formula': 'α*X4 + β*X0 + γ'}
    }
    models_N = {
        'model1': {'num_coeffs': 2, 'formula': 'α*X6 + β'},
        'model2': {'num_coeffs': 3, 'formula': 'α/X7 + β*X2 + γ'},
        'model3': {'num_coeffs': 5, 'formula': 'α/X7 + β/X20 + γ*X2 + δ*X25 + ε'}
    }

    # Evaluate for Sn models
    for model_name, model_info in models_Sn.items():
        result = optimize_model(X, s_exp_sn, model_name, obj_model_sn, model_info['num_coeffs'])
        if result is not None:
            mae = np.mean(np.abs(s_exp_sn - result.fun))
            print()
            print(f'  {mae:.4f} | Sn = {model_info["formula"]}')
            print_coeffs(result.x)

    # Evaluate for N models
    for model_name, model_info in models_N.items():
        result = optimize_model(X, s_exp_n, model_name, obj_model_n, model_info['num_coeffs'])
        if result is not None:
            mae = np.mean(np.abs(s_exp_n - result.fun))
            print()
            print(f'  {mae:.4f} | N = {model_info["formula"]}')
            print_coeffs(result.x)

def main():
    data = fetch_data('../nucleo_data.db')
    data = prepare_data(data)

    # Evaluate models
    print('   MAE    |    Model')
    evaluate_models(data)

if __name__ == '__main__':
    main()

