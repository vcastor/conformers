#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
from scipy.optimize import minimize

# Load the data
def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM molecules', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    # data = data[data['correctionS'] < 0]
    return data

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f'          | {formatted_coeffs}')

# Objective functions
def obj_model(coeffs, srot, strans, svib, scorr, s_exp, model):
    if model == 'model1':
        predictions = coeffs[0]*(srot + strans) + coeffs[1]*(svib + scorr)
    elif model == 'model2':
        predictions = coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + coeffs[3]*scorr
    elif model == 'model3':
        predictions = (coeffs[0]*(strans + srot) + coeffs[1]*(svib + scorr) + 
                       coeffs[2]*(strans*(svib + scorr) + srot*(svib + scorr))/(strans + srot + svib + scorr))
    elif model == 'model4':
        predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + coeffs[3]*scorr +
                       coeffs[4]*(strans*(svib + scorr))/(strans + srot + svib + scorr) +
                       coeffs[5]*(srot*(svib + scorr))/(strans + srot + svib + scorr))
    elif model == 'model5':
        predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + coeffs[3]*scorr +
                       coeffs[4]*(strans*(svib + scorr) + srot*(svib + scorr) + srot*strans)/(strans + srot + svib + scorr))
    elif model == 'model6':
        predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + coeffs[3]*scorr +
                       coeffs[4]*(strans*(svib + scorr) + srot*(svib + scorr) + srot*strans)/(strans + srot + svib + scorr) +
                       coeffs[4]*(strans*(svib + scorr))/(strans + srot + svib + scorr) +
                       coeffs[5]*(srot*(svib + scorr))/(strans + srot + svib + scorr) +
                       coeffs[6]*(srot*strans)/(strans + srot + svib + scorr))
    elif model == 'model7':
        predictions = (coeffs[0]*(strans + srot) +
                       coeffs[1]*(svib + scorr) + coeffs[2]*(svib + scorr)*(srot + strans)/(srot + strans + svib + scorr))
    elif model == 'model8':
        predictions = (coeffs[0]*(strans + srot) +
                       coeffs[1]*svib + coeffs[2]*scorr + coeffs[3]*(svib + scorr)*(srot + strans)/(srot + strans + svib + scorr))
    return np.sum((s_exp - predictions) ** 2)

def optimize_model(srot, strans, svib, scorr, s_exp, model, bounds, num_coeffs):
    best_score, best_result = np.inf, None
    for _ in range(20):
        initial_guess = np.random.rand(num_coeffs)
        # result = minimize(obj_model, initial_guess, bounds=bounds, method='SLSQP')
        result = minimize(obj_model, initial_guess, args=(srot, strans, svib, scorr, s_exp, model), bounds=bounds, method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def evaluate_models(data):
    srot, strans, svib, scorr, s_exp = data['rot_S'], data['trans_S'], data['vib_S'], data['correctionS'], data['experimental_S']
    
    models = {
        'model1': {'bounds': [(0, 1), (0, 1)], 'num_coeffs': 2, 'formula': 'α*(S_r + S_t) + β*(S_v + S_corr)'},
        'model2': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 4, 'formula': 'α*S_t + β*S_r + γ*S_v + δ*S_corr'},
        'model3': {'bounds': [(0, 1), (0, 1), (0, 1)], 'num_coeffs': 3,
                   'formula': 'α*(S_t + S_r) + β*(S_v + S_corr) + γ*(S_tvc + S_rvc)/S_gas'},
        'model4': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 6,
                   'formula': 'α*S_t + β*S_r + γ*S_v + δ*S_vc + ε*(S_tvc/S_gas) + ζ*(S_rv/S_gas)'},
        'model5': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 5,
                   'formula': 'α*S_t + β*S_r + γ*S_v + δ*S_vc ε*(S_tvc + S_rvc + S_tr)/S_gas'},
        'model6': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 8,
                   'formula': 'α*S_t + β*S_r + γ*S_v + δ*S_vc + ε*(S_tvc + S_rvc + S_tr)/S_gas + ζ*(S_tvc/S_gas) + η*(S_rvc/S_gas) + θ*(S_tr/S_gas)'},
        'model7': {'bounds': [(0, 1), (0, 1), (0, 1)], 'num_coeffs': 3,
                  'formula': 'α*(S_t + S_r) + β*(S_vc) + γ*(S_vc*(S_r + S_t))/S_gas'},
        'model8': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 4,
                  'formula': 'α*(S_t + S_r) + β*S_v + γ*S_corr + δ*(S_vc*(S_r + S_t))/S_gas'},
    }
    
    for model_name, model_info in models.items():
        result = optimize_model(srot, strans, svib, scorr, s_exp, model_name, model_info['bounds'], model_info['num_coeffs'])
        if result is not None:
            coeffs = result.x
            if model_name == 'model1':
                predictions = coeffs[0]*(srot + strans) + coeffs[1]*(svib + scorr)
            elif model_name == 'model2':
                predictions = coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + coeffs[3]*scorr
            elif model_name == 'model3':
                predictions = coeffs[0]*(strans + srot) + coeffs[1]*(svib + scorr) + coeffs[2]*(strans*svib + srot*svib)/(strans + srot + svib + scorr)
            elif model_name == 'model4':
                predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + coeffs[3]*scorr +
                               coeffs[4]*(strans*(svib+scorr))/(strans + srot + svib + scorr) + coeffs[5]*(srot*(svib + scorr))/(strans + srot + svib + scorr))
            elif model_name == 'model5':
                predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + coeffs[3]*scorr +
                               coeffs[4]*(strans*(svib + scorr) + srot*(svib + scorr) + srot*strans)/(strans + srot + svib + scorr))
            elif model_name == 'model6':
                predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + coeffs[3]*scorr +
                               coeffs[4]*(strans*(svib + scorr) + srot*(svib + scorr) + srot*strans)/(strans + srot + svib + scorr) + 
                               coeffs[5]*(strans*(svib + scorr))/(strans + srot + svib + scorr) + coeffs[5]*(srot*(svib + scorr))/(strans + srot + svib + scorr) + 
                               coeffs[6]*(srot*strans)/(strans + srot + svib + scorr))
            elif model_name == 'model7':
                predictions = (coeffs[0]*(strans + srot) +
                               coeffs[1]*(svib + scorr) + coeffs[2]*(svib + scorr)*(srot + strans)/(srot + strans + svib + scorr))
            elif model_name == 'model8':
                predictions = (coeffs[0]*(strans + srot) +
                               coeffs[1]*svib + coeffs[2]*scorr + coeffs[3]*(svib + scorr)*(srot + strans)/(srot + strans + svib + scorr))
            mae = np.mean(np.abs(s_exp - predictions))
            print('')
            print(f'  {mae:.4f} | S = {model_info["formula"]}')
            print_coeffs(coeffs)

def obj_model_exp(coeffs, srot, strans, svib, scorr):
    predictions = coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib + coeffs[3]*scorr
    return np.sum((obj_model_exp.y - predictions) ** 2)

def obj_model_exp2(coeffs, srot, strans, svib, scorr):
    predictions = coeffs[0]*(strans + srot) + coeffs[1]*svib + coeffs[2]*scorr + coeffs[3]*(strans*(svib + scorr) + srot*(svib + scorr))/(strans + srot + svib + scorr)
    return np.sum((obj_model_exp2.y - predictions) ** 2)

def obj_model_exp3(coeffs, srot, strans, svib, scorr):
    predictions = coeffs[0]*(strans + srot) + coeffs[1]*(svib + scorr) + coeffs[2]*(strans*(svib + scorr) + srot*(svib + scorr) + srot*strans)/(strans + srot + svib + scorr)
    return np.sum((obj_model_exp3.y - predictions) ** 2)

def optimize_model_exp(srot, strans, svib, scorr, s_exp, eps, bounds, exp_model):
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
        elif exp_model == 'exp3':
            obj_model_exp3.y = y  # Set y as a static variable
            obj_func = obj_model_exp3
        for _ in range(20):
            initial_guess = np.random.rand(4) if exp_model == 'exp1' or exp_model == 'exp2' else np.random.rand(3)
            result = minimize(obj_func, initial_guess, args=(srot, strans, svib, scorr), bounds=bounds, method='SLSQP')
            if result.success and result.fun < best_score:
                best_score = result.fun
                best_result = result
                best_lamb = lamb
    return best_result, best_lamb

def exponential_optimization(data):
    srot, strans, svib, scorr, s_exp, eps = data['rot_S'], data['trans_S'], data['vib_S'], data['correctionS'], data['experimental_S'], data['epsilon']
    bounds = [(0, 1), (0, 1), (0, 1), (0, 1)]

    # First exponential model
    result, lambd = optimize_model_exp(srot, strans, svib, scorr, s_exp, eps, bounds, 'exp1')
    if result is not None:
        coeffs = result.x
        predictions = coeffs[0]*srot + coeffs[1]*strans + coeffs[2]*svib + coeffs[3]*scorr
        y = s_exp / np.exp(-lambd * eps)
        mae = np.mean(np.abs(y - predictions))
        print('')
        print(f'  {mae:.4f} | S = e^(-λ*ε) [α*S_r + β*S_t + γ*S_v + δ*S_corr]')
        print(f'          | λ: {lambd:.4f}')
        print_coeffs(coeffs)

    # Second exponential model
    result, lambd = optimize_model_exp(srot, strans, svib, scorr, s_exp, eps, bounds, 'exp2')
    if result is not None:
        coeffs = result.x
        predictions = (coeffs[0]*(strans + srot) + coeffs[1]*svib + coeffs[2]*scorr +
                       coeffs[3]*(strans*(svib + scorr) + srot*(svib + scorr))/(strans + srot + svib + scorr))
        y = s_exp/np.exp(-lambd*eps)
        mae = np.mean(np.abs(y - predictions))
        print('')
        print(f'  {mae:.4f} | S = e^(-λ*ε) [α*(S_t + S_r) + β*S_v + γ*S_vc + δ*(S_tvc + S_rvc)/(S_t + S_r + S_v + S_corr)]')
        print(f'          | λ: {lambd:.4f}')
        print_coeffs(coeffs)

    # Third exponential model [merged the vibration and correction terms]
    bounds = [(0, 1), (0, 1), (0, 1)]
    result, lambd = optimize_model_exp(srot, strans, svib, scorr, s_exp, eps, bounds, 'exp3')
    if result is not None:
        coeffs = result.x
        predictions = (coeffs[0]*(strans + srot) + coeffs[1]*(svib + scorr) +
                       coeffs[2]*(strans*(svib + scorr) + srot*(svib + scorr) + srot*strans)/(strans + srot + svib + scorr))
        y = s_exp/np.exp(-lambd*eps)
        mae = np.mean(np.abs(y - predictions))
        print('')
        print(f'  {mae:.4f} | S = e^(-λ*ε) [α*(S_t + S_r) + β*(S_v + S_corr) + γ*(S_tvc + S_rvc)/(S_t + S_r + S_v + S_corr)]')
        print(f'          | λ: {lambd:.4f}')
        print_coeffs(coeffs)

def obj_model_splited1(coeffs, srot, strans):
    predictions = coeffs[0]*(srot + strans)
    return np.sum((obj_model_splited1.y - predictions) ** 2)

def obj_model_splited2(coeffs, srot, strans):
    predictions = coeffs[0]*srot + coeffs[1]*strans
    return np.sum((obj_model_splited2.y - predictions) ** 2)

def optimize_model_splited(srot, strans, svib, scorr, s_exp, eps, bounds, exp_model):
    best_score, best_result, best_lamb = np.inf, None, None
    for _ in range(40):
        lamb = np.random.uniform(0, 0.05)
        y = (s_exp - svib - scorr)/np.exp(-lamb*eps)
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
    srot, strans, svib, scorr, s_exp, eps = data['rot_S'], data['trans_S'], data['vib_S'], data['correctionS'], data['experimental_S'], data['epsilon']
    # First splited model
    bounds = [(0, 1)]
    result, lambd = optimize_model_splited(srot, strans, svib, scorr, s_exp, eps, bounds, 'splited1')
    if result is not None:
        coeffs = result.x
        predictions = coeffs[0]*(srot + strans)
        y = (s_exp - svib - scorr)/np.exp(-lambd*eps)
        mae = np.mean(np.abs(y - predictions))
        print('')
        print(f'  {mae:.4f} | S = e^(-λ*ε) [α*(S_r + S_t)] + S_v + S_corr')
        print(f'          | λ: {lambd:.4f}')
        print_coeffs(coeffs)
    # Second splited model
    bounds = [(0, 1), (0, 1)]
    result, lambd = optimize_model_splited(srot, strans, svib, scorr, s_exp, eps, bounds, 'splited2')
    if result is not None:
        coeffs = result.x
        predictions = coeffs[0]*srot + coeffs[1]*strans
        y = (s_exp - svib - scorr)/np.exp(-lambd*eps)
        mae = np.mean(np.abs(y - predictions))
        print('')
        print(f'  {mae:.4f} | S = e^(-λ*ε) [α*S_r + β*S_t] + S_v + S_corr')
        print(f'          | λ: {lambd:.4f}')
        print_coeffs(coeffs)

def obj_new_model(coeffs, svib, scorr):
    predictions = coeffs[0]*svib + coeffs[1]*scorr
    return np.sum((obj_new_model.y - predictions) ** 2)

def optimise_new_split(srot, strans, svib, scorr, s_exp, eps, lambd, alpha, bounds):
    best_score, best_result = np.inf, None
    y = s_exp - np.exp(-lambd * eps) * alpha * (srot + strans)
    obj_new_model.y = y  # Set y as a static variable
    obj_func = obj_new_model
    for _ in range(20):
        initial_guess = np.random.rand(2)
        result = minimize(obj_func, initial_guess, args=(svib, scorr), bounds=bounds, method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def new_split(data):
    srot, strans, svib, scorr, s_exp, eps = data['rot_S'], data['trans_S'], data['vib_S'], data['correctionS'], data['experimental_S'], data['epsilon']
    bounds = [(0, 1), (0, 1)]
    lambd, alpha = 0.0022, 0.6029
    result = optimise_new_split(srot, strans, svib, scorr, s_exp, eps, lambd, alpha, bounds)
    if result is not None:
        coeffs = result.x
        predictions = coeffs[0] * svib + coeffs[1] * scorr
        y = s_exp - np.exp(-lambd * eps) * alpha * (srot + strans)
        mae = np.mean(np.abs(y - predictions))
        print('')
        print(f'  {mae:.4f} | S = e^(-λ*ε)α(S_r + S_t) + β*S_v + γ*S_corr')
        coeffs = [alpha] + coeffs.tolist()
        print_coeffs(coeffs)

def main():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    # reference values [not optimized]
    gas_phase = data['rot_S'] + data['trans_S'] + data['vib_S'] + data['correctionS']
    print('** Using the correction factor **')
    print('    MAE   |     Model')
    print(f"  {np.mean(np.abs(data['experimental_S'] - gas_phase)):.2f}  | gas phase")
    twothirds = 2/3*data['rot_S'] + 2/3*data['trans_S'] + data['vib_S'] + data['correctionS']
    print(f"  {np.mean(np.abs(data['experimental_S'] - twothirds)):.3f}  | 2/3")
    # linear optmization
    evaluate_models(data)
    # exponential optimization
    exponential_optimization(data)
    # splited S optimization
    splited_S(data)
    # new split optimization
    new_split(data)

    

if __name__ == '__main__':
    main()
    quit()

