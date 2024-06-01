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
    plt.subplot(2, 3, position)
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
    # 12.7529 | S = e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
    #         | λ: 0.0022
    #         | α: 0.4632, β: 0.5902, γ: 0.2493
    lambd = 0.0022
    alpha, beta, gamma = 0.4632, 0.5902, 0.2493
    y   = data['experimental_S']
    gas = data['rot_S'] + data['trans_S'] + data['vib_S']
    gas_corr = gas + data['correctionS']
    predictions = (np.exp(-lambd*data['epsilon'])*(alpha*data['rot_S'] + beta*data['trans_S'] +
                                                   data['vib_S']*data['rot_S']/gas +
                                                   gamma*data['vib_S']*data['trans_S']/gas) +
                   data['vib_S'])
    mae = 12.7529
    plt.figure(figsize=(18, 12))
    plot_subplot(1, 'Best Model Predictions vs. Experimental Entropy', 'Experimental Entropy',
                 'Best Model Predicted Entropy', y, predictions,
                 r'$S = e^{-\lambda\varepsilon} [\alpha S_{\text{rot}} + \beta S_{\text{trans}} + \frac{S_{\text{vib}}S_{\text{rot}}}{S_{\text{gas}}} + \gamma \frac{S_{\text{vib}}S_{\text{tra}}}{S_{\text{gas}}}] + S_{\text{vib}}$',
                 [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                  r'$\gamma = {:.2f}$'.format(gamma), r'$\lambda = {:.4f}$'.format(lambd),
                  r'$MAE = {:.4f}$'.format(mae)], ybox=0.72)
    # Gas phase
    plt.subplot(2, 3, 2)
    plt.scatter(y, gas_corr, alpha=0.5, label='Gas Phase + Correction')
    plt.scatter(y, gas, alpha=0.5, label='Gas Phase')
    plt.scatter(y, data['trans_S'], alpha=0.5, label='Translational')
    plt.scatter(y, data['rot_S'], alpha=0.5, label='Rotational')
    plt.scatter(y, data['vib_S'], alpha=0.5, label='Vibrational')
    plt.title('Sum of Contributions vs. Experimental Entropy')
    plt.xlabel('Experimental Entropy')
    plt.ylabel('Sum of Contributions')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.legend()
    plt.grid(True)
    # 13.6673 | S = α*S_r + β*S_t + S_v + γ*S_vt/S_gas + S_vr/S_gas
    #         | α: 0.6507, β: 0.4361, γ: 0.2621
    alpha, beta, gamma = 0.6507, 0.4361, 0.2621
    mae = 13.6673
    predictions = alpha*data['rot_S'] + beta*data['trans_S'] + data['vib_S'] + gamma*data['vib_S']*data['trans_S']/gas + data['vib_S']*data['rot_S']/gas
    plot_subplot(3, 'Second Terms vs. Experimental Entropy', 'Experimental Entropy',
                 'Second Terms', y, predictions,
                 r'$S = \alpha S_{\text{rot}} + \beta S_{\text{tra}} + S_{\text{vib}} + \gamma \frac{S_{\text{vib}}S_{\text{tra}}}{S_{gas}} + \frac{S_{\text{vib}}S_{\text{rot}}}{S_{gas}}$',
                 [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                  r'$\gamma = {:.2f}$'.format(gamma), r'$MAE = {:.4f}$'.format(mae)])
    # 13.1803 | S = e^(-λ*ε)[α*(S_r + S_t) + S_v + β*S_v(S_r + S_t)/S_gas]
    #         | λ: 0.0026
    #         | α: 0.5466, β: 0.5574
    lambd = 0.0026
    alpha, beta = 0.5466, 0.5574
    mae = 13.1803
    predictions = np.exp(-lambd*data['epsilon'])*(alpha*(data['rot_S'] + data['trans_S']) + data['vib_S'] + beta*data['vib_S']*(data['rot_S'] + data['trans_S'])/gas)
    plot_subplot(4, 'Simple Exponential vs. Experimental Entropy', 'Experimental Entropy',
                 'Simple Exponential', y, predictions,
                 r'$S = e^{-\lambda\varepsilon} [\alpha(S_{\text{rot}} + S_{\text{tra}}) + S_{\text{vib}} + \beta \frac{S_{\text{vib}}(S_{\text{rot}} + S_{\text{tra}})}{S_{\text{gas}}}]$',
                 [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                  r'$\lambda = {:.4f}$'.format(lambd), r'$MAE = {:.4f}$'.format(mae)])
    # 12.9275 | S = e^(-λ*ε)[α*S_r + β*S_t + S_v + S_vr/S_gas + δ*S_vt/S_gas]
    #         | λ: 0.0026
    #         | α: 0.4307, β: 0.6229, δ: 0.2556
    lambd = 0.0026
    alpha, beta, delta = 0.4307, 0.6229, 0.2556
    mae = 12.9275
    predictions = (np.exp(-lambd*data['epsilon'])*(alpha*data['rot_S'] + beta*data['trans_S'] + data['vib_S'] +
                                                   data['vib_S']*data['rot_S']/gas + delta*data['vib_S']*data['trans_S']/gas))
    plot_subplot(5, 'Model Predictions vs. Experimental Entropy', 'Experimental Entropy',
                 'Model Predicted Entropy', y, predictions,
                 r'$S = e^{-\lambda\varepsilon} [\alpha S_{\text{rot}} + \beta S_{\text{trans}} + S_{\text{vib}} + \frac{S_{\text{vib}}S_{\text{rot}}}{S_{\text{gas}}} + \delta \frac{S_{\text{vib}}S_{\text{tra}}}{S_{\text{gas}}}]$',
                 [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                  r'$\delta = {:.2f}$'.format(delta), r'$\lambda = {:.4f}$'.format(lambd),
                  r'$MAE = {:.4f}$'.format(mae)], ybox=0.75)
    # 23.59  | S = 2/3*(S_r + S_t) + S_v
    mae = 23.59
    predictions = (2/3)*(data['rot_S'] + data['trans_S']) + data['vib_S']
    plot_subplot(6, 'Tow Thirds Model vs. Experimental Entropy', 'Experimental Entropy',
                 'Two Thirds Model', y, predictions,
                 r'$S = \frac{2}{3}(S_{\text{rot}} + S_{\text{tra}}) + S_{\text{vib}}$',
                 [r'$MAE = {:.4f}$'.format(mae)], ybox=0.85)
    plt.tight_layout()
    plt.savefig('best_regressions.pdf')
    # plt.show()

if __name__ == '__main__':
    ploting()
