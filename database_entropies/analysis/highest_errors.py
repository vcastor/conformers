#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

# Load the data
def fetch_data(db_file_path, table_name='all_molecules'):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql(f'SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM {table_name}', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def worst_case_predictions(pred, exp):
    w_idx = np.argmax(np.abs(exp - pred))
    s_idx = np.argmin(exp.values)
    h_idx = np.argmax(exp.values)
    pw, ew = pred.values[w_idx], exp.values[w_idx]
    ps, es = pred.values[s_idx], exp.values[s_idx]
    ph, eh = pred.values[h_idx], exp.values[h_idx]
    dw, ds, dh = pw - ew, ps - es, ph - eh
    print(f'{pw:17.2f} | {ew:20.2f} | {dw:16.2f} | Worst Case')
    print(f'{ps:17.2f} | {es:20.2f} | {ds:16.2f} | Smallest Entropy')
    print(f'{ph:17.2f} | {eh:20.2f} | {dh:16.2f} | Highest Entropy')
    print(f'                  |                      |')


def models(data, functional):
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    s_exp, epsilon = data['experimental_S'], data['epsilon']
    sgas = srot + strans + svib
    model_dic = {
            'linear': {'PBE': [1.0000, 0.4016, 1.0000], 'PBE0': [0.9900, 0.4171, 1.0000]},
            'cross_terms': {'PBE': [0.5216, 1.0000, 0.6257], 'PBE0': [0.5229, 1.0000, 0.6852]},
            'exp_agrouped': {'PBE': [0.5568, 1.0000, 0.5301, 0.0025], 'PBE0': [0.5467, 0.7938, 0.9843, 0.0027]},
            'exp_separated': {'PBE': [0.0000, 0.9383, 1.0000, 1.0000, 0.3616, 0.0041], 'PBE0': [0.3440, 0.7091, 1.0000, 1.0000, 0.3454, 0.0034]},
            'splited': {'PBE': [0.8683, 0.3499, 0.6249, 0.5311, 0.9380, 0.0027], 'PBE0': [0.3044, 0.7366, 1.0000, 0.3157, 1.0000, 0.0038]}
            }
    for model, info in model_dic.items():
        if model == 'linear':
            predictions = info[functional][0]*srot + info[functional][1]*strans + info[functional][2]*svib
        elif model == 'cross_terms':
            predictions = info[functional][0]*(srot + strans) + info[functional][1]*svib + info[functional][2]*svib*(srot + strans)/sgas
        elif model == 'exp_agrouped':
            predictions = np.exp(-info[functional][-1]*epsilon)*(info[functional][0]*(srot + strans) +
                                                                 info[functional][1]*svib +
                                                                 info[functional][2]*svib*(srot + strans)/sgas)
        elif model == 'exp_separated':
            predictions = np.exp(-info[functional][-1]*epsilon)*(info[functional][0]*srot +
                                                                 info[functional][1]*strans +
                                                                 info[functional][2]*svib +
                                                                 info[functional][3]*svib*srot/sgas +
                                                                 info[functional][4]*svib*strans/sgas)
        elif model == 'splited':
            predictions = (np.exp(-info[functional][-1]*epsilon)*(info[functional][0]*srot +
                                                                 info[functional][1]*strans +
                                                                 info[functional][2]*svib*srot/sgas +
                                                                 info[functional][3]*svib*strans/sgas) +
                           info[functional][4]*svib)
        # print(f'                 |                  |                  | Model: {model} ; MAE : {mean_absolute_error(s_exp, predictions):.2f}')
        print(f' Functional: {functional:<4} | Model: {model:<13} |     MAE: {mean_absolute_error(s_exp, predictions):.2f}')
        worst_case_predictions(predictions, s_exp)

def main():
    functionals = ['PBE', 'PBE0']
    print(f'    Predictions   |      Experimental    |    Difference    |   Description')
    print(f'------------------+----------------------+------------------+-----------------')
    for functional in functionals:
        data = fetch_data('../entropiesCOSMO.db', table_name=functional)
        data = prepare_data(data)
        models(data, functional)
        print(f'                  |                      |')

if __name__ == '__main__':
    main()
