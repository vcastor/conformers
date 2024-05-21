#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
from scipy.optimize import minimize

# Load the data
def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S FROM molecules', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

# Objective functions
def obj_model(coeffs, srot, strans, svib, s_exp, model):
    if model == 'model1':
        predictions = coeffs[0]*(srot + strans) + coeffs[1]*svib
    elif model == 'model2':
        predictions = coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib
    elif model == 'model3':
        predictions = (coeffs[0]*(strans + srot) + coeffs[1]*svib + 
                       coeffs[2]*(strans*svib + srot*svib)/(strans + srot + svib))
    elif model == 'model4':
        predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib +
                       coeffs[3]*(strans*svib)/(strans + srot + svib) +
                       coeffs[4]*(srot*svib)/(strans + srot + svib))
    elif model == 'model5':
        predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib +
                       coeffs[3]*(strans*svib + srot*svib + srot*strans)/(strans + srot + svib))
    elif model == 'model6':
        predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib +
                       coeffs[3]*(strans*svib + srot*svib + srot*strans)/(strans + srot + svib) +
                       coeffs[4]*(strans*svib)/(strans + srot + svib) +
                       coeffs[5]*(srot*svib)/(strans + srot + svib) +
                       coeffs[6]*(srot*strans)/(strans + srot + svib))
    return np.sum((s_exp - predictions) ** 2)

def optimize_model(srot, strans, svib, s_exp, model, bounds, num_coeffs):
    best_score, best_result = np.inf, None
    for _ in range(20):
        initial_guess = np.random.rand(num_coeffs)
        # result = minimize(obj_model, initial_guess, bounds=bounds, method='SLSQP')
        result = minimize(obj_model, initial_guess, args=(srot, strans, svib, s_exp, model), bounds=bounds, method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def evaluate_models(data):
    srot, strans, svib, s_exp = data['rot_S'], data['trans_S'], data['vib_S'], data['experimental_S']
    
    models = {
        'model1': {'bounds': [(0, 1), (0, 1)], 'num_coeffs': 2, 'formula': 'α*(S_r + S_t) + β*S_v'},
        'model2': {'bounds': [(0, 1), (0, 1), (0, 1)], 'num_coeffs': 3, 'formula': 'α*S_t + β*S_r + γ*S_v'},
        'model3': {'bounds': [(0, 1), (0, 1), (0, 1)], 'num_coeffs': 3,
                   'formula': 'α*(S_t + S_r) + β*S_v + γ*(S_tv + S_rv)/S_gas'},
        'model4': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 5,
                   'formula': 'α*S_t + β*S_r + γ*S_v + δ*(S_tv/S_gas) + ε*(S_rv/S_gas)'},
        'model5': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 4,
                   'formula': 'α*S_t + β*S_r + γ*S_v + δ*(S_tv + S_rv + S_tr)/S_gas'},
        'model6': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 7,
                   'formula': 'α*S_t + β*S_r + γ*S_v + δ*(S_tv + S_rv + S_tr)/S_gas + ε*(S_tv/S_gas) + ζ*(S_rv/S_gas) + η*(S_tr/S_gas)'}
    }
    
    for model_name, model_info in models.items():
        result = optimize_model(srot, strans, svib, s_exp, model_name, model_info['bounds'], model_info['num_coeffs'])
        if result is not None:
            coeffs = result.x
            if model_name == 'model1':
                predictions = coeffs[0]*(srot + strans) + coeffs[1]*svib
            elif model_name == 'model2':
                predictions = coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib
            elif model_name == 'model3':
                predictions = coeffs[0]*(strans + srot) + coeffs[1]*svib + coeffs[2]*(strans*svib + srot*svib)/(strans + srot + svib)
            elif model_name == 'model4':
                predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + 
                               coeffs[3]*(strans*svib)/(strans + srot + svib) + coeffs[4]*(srot * svib)/(strans + srot + svib))
            elif model_name == 'model5':
                predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + 
                               coeffs[3]*(strans*svib + srot*svib + srot*strans)/(strans + srot + svib))
            elif model_name == 'model6':
                predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + 
                               coeffs[3]*(strans*svib + srot*svib + srot*strans)/(strans + srot + svib) + 
                               coeffs[4]*(strans*svib)/(strans + srot + svib) + coeffs[5]*(srot*svib)/(strans + srot + svib) + 
                               coeffs[6]*(srot*strans)/(strans + srot + svib))
            mae = np.mean(np.abs(s_exp - predictions))
            print(f'\nModel: S = {model_info["formula"]}')
            print(f'MAE for {model_name}: {mae:.4f}')

def obj_model_exp(coeffs, srot, strans, svib):
    predictions = coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib
    return np.sum((obj_model_exp.y - predictions) ** 2)

def obj_model_exp2(coeffs, srot, strans, svib):
    predictions = coeffs[0]*(strans + srot) + coeffs[1]*svib + coeffs[2]*(strans*svib + srot*svib)/(strans + srot + svib)
    return np.sum((obj_model_exp2.y - predictions) ** 2)

def optimize_model_exp(srot, strans, svib, s_exp, eps, bounds, exp_model):
    best_score, best_result, best_lamb = np.inf, None, None
    for _ in range(40):
        lamb = np.random.uniform(0, 0.05)
        y = s_exp / np.exp(-lamb * eps)
        if exp_model == 'exp1':
            obj_model_exp.y = y  # Set y as a static variable
            obj_func = obj_model_exp
        elif exp_model == 'exp2':
            obj_model_exp2.y = y  # Set y as a static variable
            obj_func = obj_model_exp2
        for _ in range(20):
            initial_guess = np.random.rand(3)
            result = minimize(obj_func, initial_guess, args=(srot, strans, svib), bounds=bounds, method='SLSQP')
            if result.success and result.fun < best_score:
                best_score = result.fun
                best_result = result
                best_lamb = lamb
    return best_result, best_lamb

def exponential_optimization(data):
    srot, strans, svib, s_exp, eps = data['rot_S'], data['trans_S'], data['vib_S'], data['experimental_S'], data['epsilon']
    bounds = [(0, 1), (0, 1), (0, 1)]

    # First exponential model
    result, lambd = optimize_model_exp(srot, strans, svib, s_exp, eps, bounds, 'exp1')
    if result is not None:
        coeffs = result.x
        predictions = coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib
        y = s_exp / np.exp(-lambd * eps)
        mae = np.mean(np.abs(y - predictions))
        print(f'\nModel: S = e^(-λ*ε) [α*S_r + β*S_t + γ*S_v]')
        print(f'MAE for exponential model 1: {mae:.4f}')
        print(f'λ: {lambd:.4f}')

    # Second exponential model
    result, lambd = optimize_model_exp(srot, strans, svib, s_exp, eps, bounds, 'exp2')
    if result is not None:
        coeffs = result.x
        predictions = (coeffs[0]*(strans + srot) + coeffs[1]*svib +
                       coeffs[2]*(strans*svib + srot*svib)/(strans + srot + svib))
        y = s_exp/np.exp(-lambd*eps)
        mae = np.mean(np.abs(y - predictions))
        print(f'\nModel: S = e^(-λ*ε) [α*(S_t + S_r) + β*S_v + γ*(S_tv + S_rv)/(S_t + S_r + S_v)]')
        print(f'MAE for exponential model 2: {mae:.4f}')
        print(f'λ: {lambd:.4f}')

def obj_model_splited1(coeffs, srot, strans):
    predictions = coeffs[0]*(srot + strans)
    return np.sum((obj_model_splited1.y - predictions) ** 2)

def obj_model_splited2(coeffs, srot, strans):
    predictions = coeffs[0]*srot + coeffs[1]*strans
    return np.sum((obj_model_splited2.y - predictions) ** 2)

def optimize_model_splited(srot, strans, svib, s_exp, eps, bounds, exp_model):
    best_score, best_result, best_lamb = np.inf, None, None
    for _ in range(40):
        lamb = np.random.uniform(0, 0.05)
        y = (s_exp - svib)/np.exp(-lamb*eps)
        if exp_model == 'splited1':
            obj_model_splited1.y = y  # Set y as a static variable
            obj_func = obj_model_splited1
        elif exp_model == 'splited2':
            obj_model_splited2.y = y  # Set y as a static variable
            obj_func = obj_model_splited2
        for _ in range(20):
            initial_guess = np.random.rand(len(bounds))
            result = minimize(obj_func, initial_guess, args=(srot, strans), bounds=bounds, method='SLSQP')
            if result.success and result.fun < best_score:
                best_score = result.fun
                best_result = result
                best_lamb = lamb
    return best_result, best_lamb

def splited_S(data):
    srot, strans, svib, s_exp, eps = data['rot_S'], data['trans_S'], data['vib_S'], data['experimental_S'], data['epsilon']
    # First splited model
    bounds = [(0, 1)]
    result, lambd = optimize_model_splited(srot, strans, svib, s_exp, eps, bounds, 'splited1')
    if result is not None:
        coeffs = result.x
        predictions = coeffs[0]*(srot + strans)
        y = (s_exp - svib)/np.exp(-lambd*eps)
        mae = np.mean(np.abs(y - predictions))
        print(f'\nModel: S = e^(-λ*ε) [α*(S_r + S_t)] + S_v')
        print(f'MAE for splited model 1: {mae:.4f}')
        print(f'λ: {lambd:.4f}')
    # Second splited model
    bounds = [(0, 1), (0, 1)]
    result, lambd = optimize_model_splited(srot, strans, svib, s_exp, eps, bounds, 'splited2')
    if result is not None:
        coeffs = result.x
        predictions = coeffs[0]*srot + coeffs[1]*strans
        y = (s_exp - svib)/np.exp(-lambd*eps)
        mae = np.mean(np.abs(y - predictions))
        print(f'\nModel: S = e^(-λ*ε) [α*S_r + β*S_t] + S_v')
        print(f'MAE for splited model 2: {mae:.4f}')
        print(f'λ: {lambd:.4f}')

def main():
    data = fetch_data('entropiesCOSMO.db')
    data = prepare_data(data)
    # reference values [not optimized]
    gas_phase = data['rot_S'] + data['trans_S'] + data['vib_S']
    print('gas phase')
    print('MAE', np.mean(np.abs(data['experimental_S'] - gas_phase)))
    twothirds = 2/3*data['rot_S'] + 2/3*data['trans_S'] + data['vib_S']
    print('2/3')
    print('MAE', np.mean(np.abs(data['experimental_S'] - twothirds)))
    # linear optmization
    evaluate_models(data)
    # exponential optimization
    exponential_optimization(data)
    # splited S optimization
    splited_S(data)
    

if __name__ == '__main__':
    main()
    quit()

