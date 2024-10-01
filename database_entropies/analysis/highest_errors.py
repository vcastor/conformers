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
    print(f'{pw:17.2f} & {ew:20.2f} & {dw:16.2f} & Worst Case')
    print(f'{ps:17.2f} & {es:20.2f} & {ds:16.2f} & Smallest Entropy')
    print(f'{ph:17.2f} & {eh:20.2f} & {dh:16.2f} & Highest Entropy')
    print(f'                  |                      |')


def models(data, functional):
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    s_exp, epsilon = data['experimental_S'], data['epsilon']
    sgas = srot + strans + svib
    model_dic = {
            'linear': {'PBE': [0.7009, 0.5327, 1.0000], 'PBE0': [1.0000, 0.3286, 0.9993]},
            'cross_terms': {'PBE': [0.5590, 0.3972, 1.0000], 'PBE0': [0.5666, 0.3880, 1.0000]},
            'exp_agrouped': {'PBE': [0.5974, 0.3085, 1.0000, 0.0025], 'PBE0': [0.6043, 0.3004, 1.0000, 0.0027]},
            'exp_separated': {'PBE': [0.8999, 0.4318, 0.5242, 0.0000, 1.0000, 0.0024], 'PBE0': [1.0000, 0.3690, 0.5271, 0.0000, 1.0000, 0.0020]},
            'splited': {'PBE': [0.4068, 0.7256, 0.0000, 1.0000, 0.6190, 0.0023], 'PBE0': [0.8178, 0.4699, 0.4721, 1.0000, 0.3978, 0.0016]}
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
