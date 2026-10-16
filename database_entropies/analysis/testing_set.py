#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
def fetch_data(db_file_path, training=False, basisset=''):
    if basisset == 'pbe0':
        with sqlite3.connect(db_file_path) as conn:
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM pbe0', conn)
    if training:
        with sqlite3.connect(db_file_path) as conn:
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM molecules', conn)
    else:
        with sqlite3.connect(db_file_path) as conn:
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM test_molecules', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def generate_bounds(num_coeffs):
    return [(0, 1)] * num_coeffs

def print_coeffs(coeffs):
    greek_letters = ['α', 'β', 'γ', 'δ', 'ζ', 'η', 'θ', 'ι', 'κ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
    formatted_coeffs = ', '.join([f'{greek_letters[i]}: {coef:.4f}' for i, coef in enumerate(coeffs)])
    print(f'          | {formatted_coeffs}')

def model1(data):
    # 12.7529 | S = e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
    #         | λ: 0.0022
    #         | α: 0.4632, β: 0.5902, γ: 0.2493
    lambd = 0.0022
    alpha, beta, gamma = 0.4632, 0.5902, 0.2493
    gas = data['rot_S'] + data['trans_S'] + data['vib_S']
    return (np.exp(-lambd*data['epsilon'])*(alpha*data['rot_S'] + beta*data['trans_S'] +
                                                  data['vib_S']*data['rot_S']/gas +
                                                  gamma*data['vib_S']*data['trans_S']/gas) + data['vib_S'])

def model2(data):
    # 13.6673 | S = α*S_r + β*S_t + S_v + γ*S_vt/S_gas + S_vr/S_gas
    #         | α: 0.6507, β: 0.4361, γ: 0.2621
    alpha, beta, gamma = 0.6507, 0.4361, 0.2621
    gas = data['rot_S'] + data['trans_S'] + data['vib_S']
    return (alpha*data['rot_S'] + beta*data['trans_S'] + data['vib_S'] +
            gamma*data['vib_S']*data['trans_S']/gas + data['vib_S']*data['rot_S']/gas)

def model3(data):
    # 13.1803 | S = e^(-λ*ε)[α*(S_r + S_t) + S_v + β*S_v(S_r + S_t)/S_gas]
    #         | λ: 0.0026
    #         | α: 0.5466, β: 0.5574
    lambd = 0.0026
    alpha, beta = 0.5466, 0.5574
    gas = data['rot_S'] + data['trans_S'] + data['vib_S']
    return (np.exp(-lambd*data['epsilon'])*(alpha*(data['rot_S'] + data['trans_S']) + data['vib_S'] +
                                                  beta*data['vib_S']*(data['rot_S'] + data['trans_S'])/gas))

def model4(data):
    # 12.9275 | S = e^(-λ*ε)[α*S_r + β*S_t + S_v + S_vr/S_gas + δ*S_vt/S_gas]
    #         | λ: 0.0026
    #         | α: 0.4307, β: 0.6229, δ: 0.2556
    lambd = 0.0026
    alpha, beta, delta = 0.4307, 0.6229, 0.2556
    gas = data['rot_S'] + data['trans_S'] + data['vib_S']
    return (np.exp(-lambd*data['epsilon'])*(alpha*data['rot_S'] + beta*data['trans_S'] + data['vib_S'] +
                                                  data['vib_S']*data['rot_S']/gas +
                                            delta*data['vib_S']*data['trans_S']/gas))

def models(data):
    # Model 1
    prediction = model1(data)
    predpbe0 = fetch_data('../entropiesCOSMO.db', training=False, basisset='pbe0')
    predpbe0 = prepare_data(predpbe0)
    mae = np.abs(data['experimental_S'] - prediction)
    mae_pbe0 = np.abs(predpbe0['experimental_S'] - model1(predpbe0))
    print('          | S = e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v')
    print('          | λ: 0.0022')
    alpha, beta, gamma = 0.4632, 0.5902, 0.2493
    print_coeffs([alpha, beta, gamma])
    print(f' {mae.mean():.4f}  | Testing mae')
    print(f' {mae_pbe0.mean():.4f}  | PBE0 mae')
    print(' 12.7529  | Training mae')
    print('          | ')
    # Model 2
    prediction = model2(data)
    mae = np.abs(data['experimental_S'] - prediction)
    mae_pbe0 = np.abs(predpbe0['experimental_S'] - model2(predpbe0))
    print('          | S = α*S_r + β*S_t + S_v + γ*S_vt/S_gas + S_vr/S_gas')
    alpha, beta, gamma = 0.6507, 0.4361, 0.2621
    print_coeffs([alpha, beta, gamma])
    print(f' {mae.mean():.4f}  | Testing mae')
    print(f' {mae_pbe0.mean():.4f}  | PBE0 mae')
    print(' 13.6673  | Training mae')
    print('          | ')
    # Model 3
    prediction = model3(data)
    mae = np.abs(data['experimental_S'] - prediction)
    mae_pbe0 = np.abs(predpbe0['experimental_S'] - model3(predpbe0))
    print('          | S = e^(-λ*ε)[α*(S_r + S_t) + S_v + β*S_v(S_r + S_t)/S_gas]')
    print('          | λ: 0.0026')
    alpha, beta = 0.5466, 0.5574
    print_coeffs([alpha, beta])
    print(f' {mae.mean():.4f}  | Testing mae')
    print(f' {mae_pbe0.mean():.4f}  | PBE0 mae')
    print(' 13.1803  | Training mae')
    print('          | ')
    # Model 4
    prediction = model4(data)
    mae = np.abs(data['experimental_S'] - prediction)
    mae_pbe0 = np.abs(predpbe0['experimental_S'] - model4(predpbe0))
    print('          | S = e^(-λ*ε)[α*S_r + β*S_t + S_v + S_vr/S_gas + δ*S_vt/S_gas]')
    print('          | λ: 0.0026')
    alpha, beta, delta = 0.4307, 0.6229, 0.2556
    print_coeffs([alpha, beta, delta])
    print(f' {mae.mean():.4f}  | Testing mae')
    print(f' {mae_pbe0.mean():.4f}  | PBE0 mae')
    print(' 12.9275  | Training mae')
    print('          | ')

def plotting():
    plt.figure(figsize=(12, 12))
    # Model 1
    plt.subplot(2, 2, 1)
    data = fetch_data('../entropiesCOSMO.db', training=True)
    data = prepare_data(data)
    prediction = model1(data)
    plt.scatter(data['experimental_S'], prediction, label='Trainig data')
    plt.plot([prediction.min(), prediction.max()], [prediction.min(), prediction.max()], 'k--', lw=2)
    pbe0 = fetch_data('../entropiesCOSMO.db', basisset='pbe0')
    pbe0 = prepare_data(pbe0)
    pred_pbe0 = model1(pbe0)
    plt.scatter(pbe0['experimental_S'], pred_pbe0, label='PBE0 data')
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    prediction = model1(data)
    plt.scatter(data['experimental_S'], prediction, label='Testing data')
    plt.title(r'$S=e^{-\lambda\epsilon}[\alpha S_r +\beta S_t + \frac{S_{vr}}{S_{gas}} + \gamma\frac{S_{vt}}{S_{gas}}] + S_v$')
    plt.xlabel('Experimental S')
    plt.ylabel('Predicted S')
    plt.legend()
    plt.grid(True)
    # Model 2
    plt.subplot(2, 2, 2)
    data = fetch_data('../entropiesCOSMO.db', training=True)
    data = prepare_data(data)
    prediction = model2(data)
    plt.scatter(data['experimental_S'], prediction, label='Trainig data')
    plt.plot([prediction.min(), prediction.max()], [prediction.min(), prediction.max()], 'k--', lw=2)
    pbe0 = prepare_data(pbe0)
    pred_pbe0 = model2(pbe0)
    plt.scatter(pbe0['experimental_S'], pred_pbe0, label='PBE0 data')
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    prediction = model2(data)
    plt.scatter(data['experimental_S'], prediction, label='Testing data')
    plt.title(r'$S=\alpha S_r + \beta S_t + S_v + \gamma\frac{S_{vt}}{S_{gas}} + \frac{S_{vr}}{S_{gas}}$')
    plt.xlabel('Experimental S')
    plt.ylabel('Predicted S')
    plt.legend()
    plt.grid(True)
    # Model 3
    plt.subplot(2, 2, 3)
    data = fetch_data('../entropiesCOSMO.db', training=True)
    data = prepare_data(data)
    prediction = model3(data)
    plt.scatter(data['experimental_S'], prediction, label='Trainig data')
    plt.plot([prediction.min(), prediction.max()], [prediction.min(), prediction.max()], 'k--', lw=2)
    pbe0 = prepare_data(pbe0)
    pred_pbe0 = model3(pbe0)
    plt.scatter(pbe0['experimental_S'], pred_pbe0, label='PBE0 data')
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    prediction = model3(data)
    plt.scatter(data['experimental_S'], prediction, label='Testing data')
    plt.title(r'$S=e^{-\lambda\epsilon}[\alpha(S_r + S_t) + S_v + \beta\frac{S_v(S_r + S_t)}{S_{gas}}]$')
    plt.xlabel('Experimental S')
    plt.ylabel('Predicted S')
    plt.legend()
    plt.grid(True)
    # Model 4
    plt.subplot(2, 2, 4)
    data = fetch_data('../entropiesCOSMO.db', training=True)
    data = prepare_data(data)
    prediction = model4(data)
    plt.scatter(data['experimental_S'], prediction, label='Trainig data')
    plt.plot([prediction.min(), prediction.max()], [prediction.min(), prediction.max()], 'k--', lw=2)
    pbe0 = prepare_data(pbe0)
    pred_pbe0 = model4(pbe0)
    plt.scatter(pbe0['experimental_S'], pred_pbe0, label='PBE0 data')
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    prediction = model4(data)
    plt.scatter(data['experimental_S'], prediction, label='Testing data')
    plt.title(r'$S=e^{-\lambda\epsilon}[\alpha S_r + \beta S_t + S_v + \frac{S_{vr}}{S_{gas}} + \delta\frac{S_{vt}}{S_{gas}}]$')
    plt.xlabel('Experimental S')
    plt.ylabel('Predicted S')
    plt.legend()
    plt.grid(True)
    # Show the plot
    # plt.savefig('testing_set.pdf')
    plt.show()

def main():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    # Run it, for the cases
    print('    MAE   |  Model')
    print('----------+--------------------------')
    models(data)

if __name__ == '__main__':
    main()
    plotting()
    quit()

