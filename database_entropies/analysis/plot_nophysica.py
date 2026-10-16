#!/usr/bin/python3 
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM molecules', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def plot_subplot(position, title, xlabel, ylabel, y, predictions, equation_text, params_texts, ybox=0.77):
    plt.subplot(1, 2, position)
    plt.scatter(y, predictions, alpha=0.5)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    textstr = '\n'.join([equation_text] + params_texts)
    plt.text(0.05, ybox, textstr, fontsize=9, transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.grid(True)

def ploting():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    # 13.2039 | S = α*S_r + β*S_t + γ*S_v + δ*ΔS_corr + ζ
    #         | α: 0.7758, β: 0.3995, γ: 1.3094, δ: -0.0080, ζ: -0.5312
    mae = 13.2039
    alpha, beta, gamma, delta, zeta = 0.7758, 0.3995, 1.3094, -0.0080, -0.5312
    y   = data['experimental_S']
    gas = data['rot_S'] + data['trans_S'] + data['vib_S']
    gas_corr = gas + data['correctionS']
    predictions = (alpha*data['rot_S'] + beta*data['trans_S'] +
                   gamma*data['vib_S'] + delta*data['correctionS'] + zeta)
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.scatter(y, predictions, alpha=0.5)
    txt = r'$\alpha S_r + \beta S_t + \gamma S_v + \delta \Delta S_{corr} + \zeta$'
    txt += '\n'
    txt += '\n'.join([f'{key}: {value:.4f}' for key, value in zip(['α', 'β', 'γ', 'δ', 'ζ'], [alpha, beta, gamma, delta, zeta])])
    txt += f'\nMAE: {mae:.4f}'
    plt.text(0.05, 0.77, txt, fontsize=9, transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8))
    plt.title('Linear regression vs. Experimental Entropy')
    plt.xlabel('Experimental Entropy')
    plt.ylabel('Linear Regression')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.grid(True)
    # 10.9280 | S = e^(-λ*ε)[α*S_r + β*S_t + γ*S_v + δ*S_vr/S_gas + ζ*S_vt/S_gas + η*S_rt/S_gas + θ]
    #         | λ: 0.0026
    #         | α: -5.0127, β: -0.9422, γ: 2.2030, δ: -3.5351, ζ: 6.2794, η: 13.7874, θ: -46.5170
    mae = 10.9280
    lambd = 0.0026
    alpha, beta, gamma, delta, zeta, eta, theta = -5.0127, -0.9422, 2.2030, -3.5351, 6.2794, 13.7874, -46.5170
    predictions = np.exp(-lambd*data['epsilon'])*(alpha*data['rot_S'] + beta*data['trans_S'] +
                                                  gamma*data['vib_S'] + delta*data['vib_S']*data['rot_S']/gas +
                                                  zeta*data['vib_S']*data['trans_S']/gas +
                                                  eta*data['rot_S']*data['trans_S']/gas + theta)
    plt.subplot(1, 2, 2)
    plt.scatter(y, predictions, alpha=0.5)
    txt = r'$e^{-\lambda\epsilon}[\alpha S_r +\beta S_t +\gamma S_v +\delta S_{vr}/S_{gas} +\zeta S_{vt}/S_{gas} +\eta S_{rt}/S_{gas} +\theta]$'
    txt += '\n'
    txt += '\n'.join([f'{key}: {value:.4f}' for key, value in zip(['λ', 'α', 'β', 'γ', 'δ', 'ζ', 'η', 'θ'], [lambd, alpha, beta, gamma, delta, zeta, eta, theta])])
    txt += f'\nMAE: {mae:.4f}'
    plt.text(0.05, 0.65, txt, fontsize=9, transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8))
    plt.title('Exponential regression vs. Experimental Entropy')
    plt.xlabel('Experimental Entropy')
    plt.ylabel('Exponential Regression')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('best_regressions.pdf')
    plt.show()

if __name__ == '__main__':
    ploting()
