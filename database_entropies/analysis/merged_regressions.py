#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
from scipy.optimize import minimize

# Load the data
def fetch_data(db_file_path, with_correction=False):
    with sqlite3.connect(db_file_path) as conn:
        if with_correction:
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM molecules', conn)
        else:
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S FROM molecules', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

# Objective functions
def obj_model(coeffs, srot, strans, svib, s_exp, model, scorr=None):
    if model == 'model1':
        predictions = coeffs[0]*(srot + strans) + coeffs[1]*(svib if scorr is None else svib + scorr)
    elif model == 'model2':
        predictions = coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + (coeffs[3]*scorr if scorr is not None else 0)
    elif model == 'model3':
        predictions = (coeffs[0]*(strans + srot) + coeffs[1]*(svib if scorr is None else svib + scorr) + 
                       coeffs[2]*(strans*(svib if scorr is None else svib + scorr) + srot*(svib if scorr is None else svib + scorr))/(strans + srot + svib + (scorr if scorr is not None else 0)))
    elif model == 'model4':
        predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + (coeffs[3]*scorr if scorr is not None else 0) +
                       coeffs[4]*(strans*(svib if scorr is None else svib + scorr))/(strans + srot + svib + (scorr if scorr is not None else 0)) +
                       coeffs[5]*(srot*(svib if scorr is None else svib + scorr))/(strans + srot + svib + (scorr if scorr is not None else 0)))
    elif model == 'model5':
        predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + (coeffs[3]*scorr if scorr is not None else 0) +
                       coeffs[4]*(strans*(svib if scorr is None else svib + scorr) + srot*(svib if scorr is None else svib + scorr) + srot*strans)/(strans + srot + svib + (scorr if scorr is not None else 0)))
    elif model == 'model6':
        predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + (coeffs[3]*scorr if scorr is not None else 0) +
                       coeffs[4]*(strans*(svib if scorr is None else svib + scorr) + srot*(svib if scorr is None else svib + scorr) + srot*strans)/(strans + srot + svib + (scorr if scorr is not None else 0)) +
                       coeffs[5]*(strans*(svib if scorr is None else svib + scorr))/(strans + srot + svib + (scorr if scorr is not None else 0)) +
                       coeffs[6]*(srot*(svib if scorr is None else svib + scorr))/(strans + srot + svib + (scorr if scorr is not None else 0)) +
                       coeffs[7]*(srot*strans)/(strans + srot + svib + (scorr if scorr is not None else 0)))
    return np.sum((s_exp - predictions) ** 2)

def optimize_model(srot, strans, svib, s_exp, model, bounds, num_coeffs, scorr=None):
    best_score, best_result = np.inf, None
    for _ in range(20):
        initial_guess = np.random.rand(num_coeffs)
        # result = minimize(obj_model, initial_guess, args=(srot, strans, svib, s_exp, model, scorr), bounds=bounds, method='SLSQP')
        if scorr is not None:
            result = minimize(obj_model, initial_guess, args=(srot, strans, svib, s_exp, model, scorr), bounds=bounds, method='SLSQP')
        else:
            result = minimize(obj_model, initial_guess, args=(srot, strans, svib, s_exp, model), bounds=bounds, method='SLSQP')
        if result.success and result.fun < best_score:
            best_score = result.fun
            best_result = result
    return best_result

def evaluate_models(data, with_correction=False):
    srot, strans, svib, s_exp = data['rot_S'], data['trans_S'], data['vib_S'], data['experimental_S']
    scorr = data['correctionS'] if with_correction else None
    
    models = {
        'model1': {'bounds': [(0, 1), (0, 1)], 'num_coeffs': 2, 'formula': 'α*(S_r + S_t) + β*(S_v + S_corr)' if with_correction else 'α*(S_r + S_t) + β*S_v'},
        'model2': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 4 if with_correction else 3, 'formula': 'α*S_t + β*S_r + γ*S_v + δ*S_corr' if with_correction else 'α*S_t + β*S_r + γ*S_v'},
        'model3': {'bounds': [(0, 1), (0, 1), (0, 1)], 'num_coeffs': 3, 'formula': 'α*(S_t + S_r) + β*(S_v + S_corr) + γ*(S_tvc + S_rvc)/S_gas' if with_correction else 'α*(S_t + S_r) + β*S_v + γ*(S_tv + S_rv)/S_gas'},
        'model4': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 6 if with_correction else 5, 'formula': 'α*S_t + β*S_r + γ*S_v + δ*S_vc + ε*(S_tvc/S_gas) + ζ*(S_rv/S_gas)' if with_correction else 'α*S_t + β*S_r + γ*S_v + δ*(S_tv/S_gas) + ε*(S_rv/S_gas)'},
        'model5': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 5 if with_correction else 4, 'formula': 'α*S_t + β*S_r + γ*S_v + δ*S_vc ε*(S_tvc + S_rvc + S_tr)/S_gas' if with_correction else 'α*S_t + β*S_r + γ*S_v + δ*(S_tv + S_rv + S_tr)/S_gas'},
        'model6': {'bounds': [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], 'num_coeffs': 8 if with_correction else 7, 'formula': 'α*S_t + β*S_r + γ*S_v + δ*S_vc + ε*(S_tvc + S_rvc + S_tr)/S_gas + ζ*(S_tvc/S_gas) + η*(S_rvc/S_gas) + θ*(S_tr/S_gas)' if with_correction else 'α*S_t + β*S_r + γ*S_v + δ*(S_tv + S_rv + S_tr)/S_gas + ε*(S_tv/S_gas) + ζ*(S_rv/S_gas) + η*(S_tr/S_gas)'}
    }
    
    results = []
    for model_name, model_info in models.items():
        if not with_correction:
            if model_name == 'model2':
                model_info['bounds'] = [(0, 1), (0, 1), (0, 1)]
            elif model_name == 'model6':
                model_info['bounds'] = [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)]
        
        # result = optimize_model(srot, strans, svib, s_exp, model_name, model_info['bounds'], model_info['num_coeffs'], scorr)
        if with_correction:
            result = optimize_model(srot, strans, svib, s_exp, model_name, model_info['bounds'], model_info['num_coeffs'], scorr)
        else:
            result = optimize_model(srot, strans, svib, s_exp, model_name, model_info['bounds'], model_info['num_coeffs'])
        if result is not None:
            coeffs = result.x
            if model_name == 'model1':
                predictions = coeffs[0]*(srot + strans) + coeffs[1]*(svib if scorr is None else svib + scorr)
            elif model_name == 'model2':
                predictions = coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + (coeffs[3]*scorr if scorr is not None else 0)
            elif model_name == 'model3':
                predictions = coeffs[0]*(strans + srot) + coeffs[1]*(svib if scorr is None else svib + scorr) + coeffs[2]*(strans*svib + srot*svib)/(strans + srot + svib + (scorr if scorr is not None else 0))
            elif model_name == 'model4':
                predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + (coeffs[3]*scorr if scorr is not None else 0) +
                               coeffs[4]*(strans*(svib if scorr is None else svib + scorr))/(strans + srot + svib + (scorr if scorr is not None else 0)) + coeffs[5]*(srot*(svib if scorr is None else svib + scorr))/(strans + srot + svib + (scorr if scorr is not None else 0)))
            elif model_name == 'model5':
                predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + (coeffs[3]*scorr if scorr is not None else 0) +
                               coeffs[4]*(strans*(svib if scorr is None else svib + scorr) + srot*(svib if scorr is None else svib + scorr) + srot*strans)/(strans + srot + svib + (scorr if scorr is not None else 0)))
            elif model_name == 'model6':
                predictions = (coeffs[0]*strans + coeffs[1]*srot + coeffs[2]*svib + (coeffs[3]*scorr if scorr is not None else 0) +
                               coeffs[4]*(strans*(svib if scorr is None else svib + scorr) + srot*(svib if scorr is None else svib + scorr) + srot*strans)/(strans + srot + svib + (scorr if scorr is not None else 0)) + 
                               coeffs[5]*(strans*(svib if scorr is None else svib + scorr))/(strans + srot + svib + (scorr if scorr is not None else 0)) + coeffs[6]*(srot*(svib if scorr is None else svib + scorr))/(strans + srot + svib + (scorr if scorr is not None else 0)) + 
                               coeffs[7]*(srot*strans)/(strans + srot + svib + (scorr if scorr is not None else 0)))
            mae = np.mean(np.abs(s_exp - predictions))
            results.append((mae, f'S = {model_info["formula"]}'))
    
    return results

def main():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    results = []
    # Linear optimization
    results.extend(evaluate_models(data))
    # With correction factor
    data_with_corr = fetch_data('../entropiesCOSMO.db', with_correction=True)
    data_with_corr = prepare_data(data_with_corr)
    results.extend(evaluate_models(data_with_corr, with_correction=True))
    
    # Output results as a table
    df_results = pd.DataFrame(results, columns=['MAE', 'Model'])
    print(df_results)

if __name__ == '__main__':
    main()
    quit()

