#!/usr/bin/python3
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3
from sklearn.metrics import mean_absolute_error

# MAE Calculation
def calculate_mae(model, data, casefrom):
    prediction = model(data, casefrom)
    return mean_absolute_error(data['experimental_S'], prediction)

def fetch_data(db_file_path, casedb):
    with sqlite3.connect(db_file_path) as conn:
        if casedb == 'pbe0':
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS, gamma, eta FROM pbe0', conn)
        elif casedb == 'training':
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS, gamma, eta FROM molecules', conn)
        elif casedb == 'testing':
            return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS, gamma, eta FROM test_molecules', conn)

def model1(data, case='training'):
    #  9.71  | α*Sr + β*St + (δ*Sv + ζ*epsilon)*e^(-θ*gamma)
    #        | α: 0.5425, β: 0.6639, δ: 0.7824, ζ: -0.3979, θ: -1.9725
    # 11.60  | α: 0.3901, β: 0.7498, δ: 1.0000, ζ: -0.5074, θ: -0.9118
    if case == 'training' or case == 'testing':
        α, β, δ, ζ, θ = 0.5425, 0.6639, 0.7824, -0.3979, -1.9725
    elif case == 'pbe0':
        α, β, δ, ζ, θ = 0.3901, 0.7498, 1.0000, -0.5074, -0.9118
    return α*data['rot_S'] + β*data['trans_S'] + (δ*data['vib_S'] + ζ*data['epsilon'])*np.exp(-θ*data['gamma'])

def modelNO(data):
    # MUY DEPENDIENTE DEL FUNCIONAL DFT (PBE, PBE0) CAMBIAN MUCHO LOS PARAMETROS
    # 9.87  | α*St + β*Sv*e^(γ*eta^3) + δ*eta*epsilon
    #       | α: 1.0000, β: 1.0000, γ: 18.2477, δ: -3.2656
    α, β, γ, δ = 1.0, 1.0, 18.2478, -3.2656
    return α*data['trans_S'] + β*data['vib_S']*np.exp(γ*data['eta']**3) + δ*data['eta']*data['epsilon']

def modelNO(data):
    # MUY DEPENDIENTE DEL FUNCIONAL DFT (PBE, PBE0) CAMBIAN MUCHO LOS PARAMETROS
    # 9.45  | α*Sr + β*St + γ*Sv*e^(δ*eta^3) + ζ*eta*epsilon
    #       | α: 0.4643, β: 0.7121, γ: 0.9138, δ: 20.8624, ζ: -2.7363
    α, β, γ, δ, ζ = 0.4643, 0.7121, 0.9138, 20.8624, -2.7363
    return α*data['rot_S'] + β*data['trans_S'] + γ*data['vib_S']*np.exp(δ*data['eta']**3) + ζ*data['eta']*data['epsilon']

def model2(data, case='training'):
    # 11.55  | α*(Sr + St)*exp(-δ*eta) + β*Sv*exp(ζ*gamma)
    #        | α: 0.5827, β: 0.9019, δ: 0.0965, ζ: 1.5777
    #        | α: 0.6404, β: 1.0000, δ: 0.4378, ζ: 1.0436
    if case == 'training' or case == 'testing':
        α, β, δ, ζ = 0.5827, 0.9019, 0.0965, 1.5777
    elif case == 'pbe0':
        α, β, δ, ζ = 0.6404, 1.0000, 0.4378, 1.0436
    return α*(data['rot_S'] + data['trans_S'])*np.exp(-δ*data['eta']) + β*data['vib_S']*np.exp(ζ*data['gamma'])

def model3(data, case='training'):
    # 9.50  | (α*Sr + β*St)*exp(-θ*epsilon) + (δ*Sv + ζ*epsilon)*exp(ι*gamma)
    #       | α: 0.2657, β: 0.8252, δ: 1.0709, ζ: -1.7112, θ: -0.0077, ι: 0.7422
    #       | α: 0.3507, β: 0.7623, θ: 0.0076, δ: 0.9216, ζ: 0.2847, ι: 1.2514
    if case == 'training' or case == 'testing':
        α, β, δ, ζ, θ, ι = 0.2657, 0.8252, 1.0709, -1.7112, -0.0077, 0.7422
    elif case == 'pbe0':
        α, β, δ, ζ, θ, ι = 0.3507, 0.7623, 0.9216, 0.2847, 0.0076, 1.2514
    return (α*data['rot_S'] + β*data['trans_S'])*np.exp(-θ*data['epsilon']) + (δ*data['vib_S'] + ζ*data['epsilon'])*np.exp(ι*data['gamma'])

def modelnocdft(data, case='training'):
    # 12.7529 | S = e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
    #         | λ: 0.0022
    #         | α: 0.4632, β: 0.5902, γ: 0.2493
    α, β, γ, λ = 0.4632, 0.5902, 0.2493, 0.0022
    sgas = data['rot_S'] + data['trans_S'] + data['vib_S']
    return np.exp(-λ*data['epsilon'])*(α*data['rot_S'] + β*data['trans_S'] + data['vib_S']*data['rot_S']/sgas + γ*data['vib_S']*data['trans_S']/sgas) + data['vib_S']

def print_mae(casefrom):
    db_path = '../entropiesCOSMO.db'
    cases  = ['training', 'testing', 'pbe0']
    models = [model1, model2, model3, modelnocdft]
    model_names = ['Model 1', 'Model 2', 'Model 3', 'Model No CDFT']
    maes = {name: [] for name in model_names}
    for case in cases:
        data = fetch_data(db_path, case)
        for model, name in zip(models, model_names):
            maes[name].append(calculate_mae(model, data, casefrom))
    mae_df = pd.DataFrame(maes, index=cases)
    print(mae_df)

#
# Plotting

def plot_subplot(position, title, model, ybox=0.77):
    plt.subplot(2, 2, position)
    for case in ['training', 'testing', 'pbe0']:
        d = fetch_data('../entropiesCOSMO.db', casedb=case)
        # for val in ['training', 'pbe0']:
        for val in ['pbe0']:
            pred = model(d, val)
            plt.scatter(d['experimental_S'], pred, alpha=0.3, label=f'{case.capitalize()} data')
    plt.title(title, fontsize=9)#, pad=20)
    plt.xlabel('Experimental S', fontsize=9, labelpad=-1)
    plt.ylabel('Predicted S', fontsize=9)
    plt.plot([d['experimental_S'].min(), d['experimental_S'].max()], [d['experimental_S'].min(), d['experimental_S'].max()], 'k--', lw=2)
    plt.tick_params(axis='both', which='major', labelsize=7)
    plt.legend()
    plt.grid(True)

def plotting():
    plt.figure(figsize=(8, 8))
    plot_subplot(1, r'$\alpha S_r + \beta S_t + (\delta S_v + \zeta\epsilon)*e^{-\theta\gamma}$', model1)
    plot_subplot(2, r'$\alpha(S_r + S_t)e^{-\delta\eta} + \beta S_v e^{\zeta\gamma}$', model2)
    plot_subplot(3, r'$(\alpha S_r + \beta S_t)e^{-\theta\epsilon} + (\delta S_v + \zeta\epsilon)e^{\iota\gamma}$', model3)
    plot_subplot(4, r'$e^{-\lambda\epsilon}[\alpha S_r + \beta S_t + S_vS^{-1}_{gas} + \gamma S_tS^{-1}_{gas}] + S_v$', modelnocdft)
    plt.savefig('cdft_models.pdf')
    plt.show()

print('''
 Model 1 | α*Sr + β*St + (γ*Sv + δ*epsilon)*e^(-ζ*gamma)
 Model 2 | α*(Sr + St)*exp(-γ*eta) + β*Sv*exp(δ*gamma)
 Model 3 | (α*Sr + β*St)*exp(-ζ*epsilon) + (γ*Sv + δ*epsilon)*exp(η*gamma)
 No CDFT | e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
      ''')
print_mae('training')
print_mae('pbe0')
plotting()

