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
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM molecules', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def generate_bounds(num_coeffs):
    return [(0, 1)] * num_coeffs

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ζ', 'η', 'θ', 'ι', 'κ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f'          | {formatted_coeffs}')

def obj_linear_model(coeffs, srot, strans, svib, scorr, s_exp, model_name):
    gas = srot + strans + svib
    gascor = srot + strans + svib + scorr
    if model_name == 'model0':
        predictions = coeffs[0]*srot + coeffs[1]*strans + svib
    elif model_name == 'model1':
        predictions = coeffs[0]*srot + coeffs[1]*strans + svib + coeffs[2]*svib*(srot + strans)/gas
    elif model_name == 'model2':
        predictions = coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib + coeffs[3]*scorr
    elif model_name == 'model3':
        predictions = (coeffs[0]*srot + coeffs[1]*strans + svib +
                       coeffs[2]*svib*strans/gas + coeffs[3]*svib*srot/gas)
    elif model_name == 'model4':
        predictions = (coeffs[0]*srot + coeffs[1]*strans + svib +
                       coeffs[2]*(svib + scorr)*srot/gascor + coeffs[3]*(svib + scorr)*strans/gascor)
    return np.sum((s_exp - predictions) ** 2)

def obj_exponential_model(coeffs, srot, strans, svib, scorr, s_exp, eps, model_name):
    gas = srot + strans + svib
    gascor = srot + strans + svib + scorr
    # y = s_exp/np.exp(-lambd*eps)
    if model_name == 'exp0':
        predictions = coeffs[0]*srot + coeffs[1]*strans + svib
    elif model_name == 'exp1':
        predictions = coeffs[0]*(srot + strans) + svib + coeffs[1]*svib*(srot + strans)/gas
    elif model_name == 'exp2':
        predictions = coeffs[0]*(srot + strans) + svib + coeffs[1]*(svib + scorr)*(srot + strans)/gascor
    elif model_name == 'exp3':
        predictions = coeffs[0]*srot + coeffs[1]*strans + svib + coeffs[2]*svib*srot/gas + coeffs[3]*svib*strans/gas
    elif model_name == 'exp4':
        predictions = (coeffs[0]*srot + coeffs[1]*strans + svib +
                       coeffs[2]*svib*srot/gas + coeffs[3]*svib*strans/gas + coeffs[4]*scorr)
    return np.sum((obj_exponential_model.y - predictions) ** 2)

def obj_splited_model(coeffs, srot, strans, svib, scorr, s_exp, eps, model_name):
    gas = srot + strans + svib
    gascor = srot + strans + svib + scorr
    if model_name == 'splited1':
        predictions = coeffs[0]*(srot + strans)
    elif model_name == 'splited2':
        predictions = coeffs[0]*srot + coeffs[1]*strans
    elif model_name == 'splited3':
        predictions = coeffs[0]*(srot + strans) + coeffs[1]*svib*(srot + strans)/gas
    elif model_name == 'splited4':
        predictions = coeffs[0]*(srot + strans) + coeffs[1]*(svib + scorr)*(srot + strans)/gascor
    elif model_name == 'splited5':
        predictions = coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib*srot/gas + coeffs[3]*svib*strans/gas
    elif model_name == 'splited6':
        predictions = (coeffs[0]*srot + coeffs[1]*strans +
                       coeffs[2]*(svib + scorr)*srot/gascor + coeffs[3]*(svib + scorr)*strans/gascor)
    return np.sum((obj_splited_model.y - predictions) ** 2)

def optimise_linear_model(srot, strans, svib, scorr, s_exp, model_name, num_coeffs):
    bounds = [(0, 1)]*num_coeffs
    best_score, best_result = np.inf, None
    for _ in range(40):
        initial_guess = np.random.rand(num_coeffs)
        result = minimize(obj_linear_model, initial_guess, args=(srot, strans, svib, scorr, s_exp, model_name), bounds=bounds, method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def optimise_exponential_model(srot, strans, svib, scorr, s_exp, eps, model_name, num_coeffs):
    bounds = [(0, 1)]*num_coeffs
    best_score, best_result = np.inf, None
    best_lamb = None
    for lamb in np.linspace(0, 0.05, 40):
        y = s_exp/np.exp(-lamb*eps)
        obj_exponential_model.y = y
        obj_func = obj_exponential_model
        for _ in range(40):
            initial_guess = np.random.rand(num_coeffs)
            result = minimize(obj_func, initial_guess, args=(srot, strans, svib, scorr, s_exp, eps, model_name), bounds=bounds, method='SLSQP')
            if result.success and result.fun < best_score:
                best_score = result.fun
                best_result = result
                best_lamb = lamb
    return best_result, best_lamb

def optimise_splited_model(srot, strans, svib, scorr, s_exp, eps, model_name, num_coeffs):
    bounds = [(0, 1)]*num_coeffs
    best_score, best_result = np.inf, None
    best_lamb = None
    for lamb in np.linspace(0, 0.05, 40):
        y = s_exp - svib - scorr if model_name == 'splited4' else s_exp - svib
        y /= np.exp(-lamb*eps)
        obj_splited_model.y = y
        obj_func = obj_splited_model
        for _ in range(40):
            initial_guess = np.random.rand(num_coeffs)
            result = minimize(obj_func, initial_guess, args=(srot, strans, svib, scorr, s_exp, eps, model_name), bounds=bounds, method='SLSQP')
            if result.success and result.fun < best_score:
                best_score = result.fun
                best_result = result
                best_lamb = lamb
    return best_result, best_lamb

def linear_models(data):
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    scorr, s_exp = data['correctionS'], data['experimental_S']
    models = {
        'model0': {'num_coeffs': 2,
                   'formula': 'α*S_r + β*S_t + S_v'},
        'model1': {'num_coeffs': 3,
                   'formula': 'α*S_r + β*S_t + S_v + γ*S_v(S_r + S_t)/S_gas'},
        'model2': {'num_coeffs': 4,
                   'formula': 'α*S_r + β*S_t + γ*S_v + δ*ΔS_corr'},
        # 'model2': {'num_coeffs': 5,
        #            'formula': 'α*S_r + β*S_t + S_v + γ*ΔS_v + δ*S_v(S_r + S_t)/S_gas + ζ*ΔS_v(S_r + S_t)/S^c_gas'},
        'model3': {'num_coeffs': 4,
                   'formula': 'α*S_r + β*S_t + S_v + γ*S_vt/S_gas + δ*S_vr/S_gas'}
        # 'model4': {'num_coeffs': 4,
        #            'formula': 'α*S_r + β*S_t + S_v + γ*S_vct/S^c_gas + δ*S_vcr/S^c_gas'}
    }
    for model_name, model_info in models.items():
        result = optimise_linear_model(srot, strans, svib, scorr, s_exp, model_name, model_info['num_coeffs'])
        if result is not None:
            coeffs = result.x
            gas = srot + strans + svib
            gascor = srot + strans + svib + scorr
            if model_name == 'model0':
                predictions = coeffs[0]*srot + coeffs[1]*strans + svib
            elif model_name == 'model1':
                predictions = coeffs[0]*srot + coeffs[1]*strans + svib + coeffs[2]*svib*(srot + strans)/gas
            elif model_name == 'model2':
                predictions = coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib + coeffs[3]*scorr
            elif model_name == 'model3':
                predictions = (coeffs[0]*srot + coeffs[1]*strans + svib +
                               coeffs[2]*svib*strans/gas + coeffs[3]*svib*srot/gas)
            elif model_name == 'model4':
                predictions = (coeffs[0]*srot + coeffs[1]*strans + svib +
                               coeffs[2]*(svib + scorr)*srot/gascor + coeffs[3]*(svib + scorr)*strans/gascor)
            mae = np.mean(np.abs(s_exp - predictions))
            print(f'          |')
            print(f'  {mae:6.4f} | S = {model_info["formula"]}')
            print_coeffs(coeffs)

def exponential_models(data):
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    scorr, s_exp, eps  = data['correctionS'], data['experimental_S'], data['epsilon']
    models = {
        # 'exp0': {'num_coeffs': 2, 'formula': 'e^(-λ*ε)[α*S_r + β*S_t + S_v]'},
        'exp1': {'num_coeffs': 2, 'formula': 'e^(-λ*ε)[α*(S_r + S_t) + S_v + β*S_v(S_r + S_t)/S_gas]'},
        'exp2': {'num_coeffs': 2, 'formula': 'e^(-λ*ε)[α*(S_r + S_t) + S_v + β*S_vc(S_r + S_t)/S^c_gas]'},
        # 'exp2': {'num_coeffs': 2, 'formula': 'e^(-λ*ε)[α*(S_r + S_t) + S_v + β*ΔS_corr(S_r + S_t)/S^c_gas]'},
        'exp3': {'num_coeffs': 4, 'formula': 'e^(-λ*ε)[α*S_r + β*S_t + S_v + γ*S_vr/S_gas + δ*S_vt/S_gas]'},
        'exp4': {'num_coeffs': 5, 'formula': 'e^(-λ*ε)[α*S_r + β*S_t + S_v + γ*S_vr/S_gas + δ*S_vt/S_gas + ζ*ΔS_corr]'}
    }
    for model_name, model_info in models.items():
        result, lambd = optimise_exponential_model(srot, strans, svib, scorr, s_exp, eps, model_name, model_info['num_coeffs'])
        if result is not None:
            coeffs = result.x
            y = s_exp/np.exp(-lambd*eps)
            gas = srot + strans + svib
            gascor = srot + strans + svib + scorr
            if model_name == 'exp0':
                predictions = coeffs[0]*srot + coeffs[1]*strans + svib
            elif model_name == 'exp1':
                predictions = coeffs[0]*(srot + strans) + svib + coeffs[1]*svib*(srot + strans)/gas
            elif model_name == 'exp2':
                predictions = (coeffs[0]*(srot + strans) + svib + coeffs[1]*(svib + scorr)*(srot + strans)/gascor)
            elif model_name == 'exp3':
                predictions = (coeffs[0]*srot + coeffs[1]*strans + svib +
                               coeffs[2]*svib*srot/gas + coeffs[3]*svib*strans/gas)
            elif model_name == 'exp4':
                predictions = (coeffs[0]*srot + coeffs[1]*strans + svib +
                               coeffs[2]*svib*srot/gas + coeffs[3]*svib*strans/gas + coeffs[4]*scorr)
            mae = np.mean(np.abs(y - predictions))
            print(f'          |')
            print(f'  {mae:6.4f} | S = {model_info["formula"]}')
            print(f'          | λ: {lambd:.4f}')
            print_coeffs(coeffs)

def split_models(data):
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    scorr, s_exp, eps  = data['correctionS'], data['experimental_S'], data['epsilon']
    models = {
        # 'splited1': {'num_coeffs': 1, 'formula': 'e^(-λ*ε)[α*(S_r + S_t)] + S_v'},
        # 'splited2': {'num_coeffs': 2, 'formula': 'e^(-λ*ε)[α*S_r + β*S_t] + S_v'},
        'splited3': {'num_coeffs': 2, 'formula': 'e^(-λ*ε)[α*(S_r + S_t) + β*S_v(S_r + S_t)/S_gas] + S_v'},
        'splited4': {'num_coeffs': 2, 'formula': 'e^(-λ*ε)[α*(S_r + S_t) + β*S_vc(S_r + S_t)/S_gas] + S_vc'},
        # 'splited4.5': {'num_coeffs': 2, 'formula': 'e^(-λ*ε)[α*(S_r + S_t) + β*ΔS_corr(S_r + S_t)/S^c_gas] + S_v'},
        'splited5': {'num_coeffs': 4, 'formula': 'e^(-λ*ε)[α*S_r + β*S_t + γ*S_vr/S_gas + δ*S_vt/S_gas] + S_v'}
    }
    for model_name, model_info in models.items():
        result, lambd = optimise_splited_model(srot, strans, svib, scorr, s_exp, eps, model_name, model_info['num_coeffs'])
        if result is not None:
            coeffs = result.x
            y = (s_exp - svib)/np.exp(-lambd*eps)
            gas = srot + strans + svib
            gascor = srot + strans + svib + scorr
            if model_name == 'splited1':
                predictions = coeffs[0]*(srot + strans)
            elif model_name == 'splited2':
                predictions = coeffs[0]*srot + coeffs[1]*strans
            elif model_name == 'splited3':
                predictions = coeffs[0]*(srot + strans) + coeffs[1]*svib*(srot + strans)/gas
            elif model_name == 'splited4':
                y = (s_exp - svib - scorr)/np.exp(-lambd*eps)
                predictions = coeffs[0]*(srot + strans) + coeffs[1]*(svib + scorr)*(srot + strans)/gascor
            elif model_name == 'splited5':
                predictions = (coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib*srot/gas + coeffs[3]*svib*strans/gas)
            elif model_name == 'splited6':
                predictions = (coeffs[0]*srot + coeffs[1]*strans +
                               coeffs[2]*svib*srot/gas + coeffs[3]*svib*strans/gas + coeffs[4]*scorr)
            mae = np.mean(np.abs(y - predictions))
            print(f'          |')
            print(f'  {mae:6.4f} | S = {model_info["formula"]}')
            print(f'          | λ: {lambd:.4f}')
            print_coeffs(coeffs)

def obj_extra_split_model(coeffs, srot, strans, svib, scorr, s_exp, eps, model_name):
    if model_name == 'extrasplited1':
        predictions = coeffs[0]*svib + coeffs[1]*scorr
    return np.sum((obj_extra_split_model.y - predictions) ** 2)

def optimise_extra_split_model(srot, strans, svib, scorr, s_exp, eps, model_name, num_coeffs, lambd, alpha, beta, gamma, delta):
    bounds = [(0, 1)]*num_coeffs
    best_score, best_result = np.inf, None
    sgas = srot + strans + svib
    y = s_exp - np.exp(-lambd*eps)*(alpha*srot + beta*strans + gamma*svib*srot/sgas + delta*svib*strans/sgas)
    obj_extra_split_model.y = y
    obj_func = obj_extra_split_model
    for _ in range(40):
        initial_guess = np.random.rand(num_coeffs)
        result = minimize(obj_func, initial_guess, args=(srot, strans, svib, scorr, s_exp, eps, model_name), bounds=bounds, method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def extra_split_models(data):
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    scorr, s_exp, eps  = data['correctionS'], data['experimental_S'], data['epsilon']
    lambd = 0.0022
    alpha, beta, gamma, delta = 0.4632, 0.5902, 1.0, 0.2493
    models = {
        'extrasplited1': {'num_coeffs': 2, 'formula': 'e^(-λ*ε)[α*S_r + β*S_t + γ*S_vr/S_gas + δ*S_vt/S_gas] + ζ*S_v + η*ΔS_corr'}
    }
    for model_name, model_info in models.items():
        result = optimise_extra_split_model(srot, strans, svib, scorr, s_exp, eps, model_name, model_info['num_coeffs'],
                                            lambd, alpha, beta, gamma, delta)
        if result is not None:
            coeffs = result.x
            sgas = srot + strans + svib
            y = s_exp - np.exp(-lambd*eps)*(alpha*srot + beta*strans + gamma*svib*srot/sgas + delta*svib*strans/sgas)
            if model_name == 'extrasplited1':
                predictions = coeffs[0]*svib + coeffs[1]*scorr
            mae = np.mean(np.abs(y - predictions))
            print(f'          |')
            print(f'  {mae:6.4f} | S = {model_info["formula"]}')
            print(f'          | λ: {lambd:.4f}')
            coeffs = np.concatenate(([alpha, beta, gamma, delta], coeffs))
            print_coeffs(coeffs)

def no_opt_models(data):
    gas_phase = data['rot_S'] + data['trans_S'] + data['vib_S']
    twothirds = 2/3*data['rot_S'] + 2/3*data['trans_S'] + data['vib_S']
    gas_phase_corr = gas_phase + data['correctionS']
    twothirds_corr = twothirds + data['correctionS']
    print(f"  {np.mean(np.abs(data['experimental_S'] - gas_phase)):6.2f}  | S = S_r + S_t + S_v")
    print(f"  {np.mean(np.abs(data['experimental_S'] - gas_phase_corr)):6.2f}  | S = S_r + S_t + S_v + ΔS_corr")
    print(f"  {np.mean(np.abs(data['experimental_S'] - twothirds)):6.2f}  | S = 2/3*(S_r + S_t) + S_v")
    print(f"  {np.mean(np.abs(data['experimental_S'] - twothirds_corr)):6.2f}  | S = 2/3*(S_r + S_t) + S_v + ΔS_corr")
    
def set_correctionS_to_zero(data):
    data.loc[data['correctionS'] > 0, 'correctionS'] = 0
    return data

def process_data_and_optimise(data, filter_condition=None):
    if filter_condition == 'positive':
        data = data[data['correctionS'] > 0]
    elif filter_condition == 'negative':
        data = data[data['correctionS'] < 0]
    elif filter_condition == 'new variable':
        data = set_correctionS_to_zero(data)
    linear_models(data)
    exponential_models(data)
    split_models(data)
    extra_split_models(data)

def main():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    # Run it, for the cases
    print('    MAE   |  Model')
    print('----------+--------------------------')
    no_opt_models(data)
    # process_data_and_optimise(data)
    # print('          |')
    # print('----------+ ΔS_corr = 0 if ΔS_corr > 0')
    # process_data_and_optimise(data, 'new variable')

if __name__ == '__main__':
    main()
    quit()

