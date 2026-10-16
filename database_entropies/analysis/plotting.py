#!/usr/bin/python3 
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM PBE WHERE nconformers IS NOT NULL', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def plot_subplot(position, title, ylabel, y, predictions, equation_text, params_texts, ybox=0.77):
    plt.subplot(1, 3, position)
    plt.scatter(y, predictions, alpha=0.5)
    # plt.title(title)
    plt.xlabel('Experimental Entropy', fontsize=14)
    plt.ylabel('Model Predictions', fontsize=14)
    # plt.ylabel(ylabel)
    textstr = equation_text + '\n' + ', '.join(params_texts[:-1]) + '\n' + params_texts[-1]
    plt.text(0.05, ybox, textstr, fontsize=9, transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.grid(True)

def ploting():
    plt.figure(figsize=(18, 6))
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    epsilon, y = data['epsilon'], data['experimental_S']
    s_gas = srot + strans + svib
    s_gas_corr = s_gas + data['correctionS']
    #
    # Contributions
    # plt.subplot(2, 3, 1)
    # plt.scatter(y, s_gas_corr, alpha=0.5, label='All Contributions and Correction')
    # plt.scatter(y, s_gas, alpha=0.5, label='All Contributions')
    # plt.scatter(y, strans, alpha=0.5, label='Translational')
    # plt.scatter(y, srot, alpha=0.5, label='Rotational')
    # plt.scatter(y, svib, alpha=0.5, label='Vibrational')
    # plt.title('Sum of Contributions vs. Experimental Entropy')
    # plt.xlabel('Experimental Entropy')
    # plt.ylabel('Sum of Contributions')
    # plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    # plt.legend()
    # plt.grid(True)
    # Linear Model
    # 10.8598 | S = α*S_r + β*S_t + γ*S_v
    #         | α: 1.0000, β: 0.3286, γ: 0.9993
    alpha, beta, gamma = 1.0000, 0.3286, 0.9993
    mae = 10.8598
    predictions = alpha*srot + beta*strans + gamma*svib
    plot_subplot(1, 'Linear Model vs. Experimental Entropy', 
                 'Linear Model', y, predictions,
                 r'$S = \alpha S_{\text{rot}} + \beta S_{\text{trans}} + \gamma S_{\text{vib}}$',
                 [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                  r'$\gamma = {:.2f}$'.format(gamma), 
                  r'$MAE = {:.4f}$'.format(mae)], ybox=0.82)
    # # Cross Terms
    # # 10.9215 | S = α*(S_r + S_t) + β*S_v + γ*S_v(S_r + S_t)/S_gas
    # #         | α: 0.5666, β: 0.3880, γ: 1.0000
    # alpha, beta, gamma = 0.5666, 0.3880, 1.0000
    # mae = 10.9215
    # predictions = alpha*(srot + strans) + beta*svib + gamma*svib*(srot + strans)/s_gas
    # plot_subplot(3, 'Cross Terms vs. Experimental Entropy',
    #              'Cross Terms', y, predictions,
    #              r'$S = \alpha (S_{\text{rot}} + S_{\text{trans}}) + \beta S_{\text{vib}} + \gamma\frac{S_{\text{vib}}(S_{\text{rot}} + S_{\text{trans}})}{S_{\text{gas}}}$',
    #              [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
    #               r'$\gamma = {:.2f}$'.format(gamma), r'$MAE = {:.4f}$'.format(mae)],
    #              ybox=0.82)
    # # Exponential Agrouped Model
    # # 10.3237 | S = e^(-λ*ε)[α*(S_r + S_t) + β*S_v + γ*S_v*(S_r + S_t)/S_gas]
    # #         | λ: 0.0027
    # #         | α: 0.6043, β: 0.3004, γ: 1.0000
    # lambd = 0.0027
    # alpha, beta, gamma = 0.6043, 0.3004, 1.0000
    # mae = 10.3237
    # predictions = np.exp(-lambd*epsilon)*(alpha*(srot + strans) + beta*svib + gamma*svib*(srot + strans)/s_gas)
    # plot_subplot(4, 'Simple Exponential vs. Experimental Entropy', 
    #              'Exponential Agrouped', y, predictions,
    #              r'$S = e^{-\lambda\varepsilon} [\alpha(S_{\text{rot}} + S_{\text{trans}}) + \beta S_{\text{vib}} + \gamma\frac{S_{\text{vib}}(S_{\text{rot}} + S_{trans})}{S_{\text{gas}}}]$',
    #              [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta), r'$\gamma = {:.2f}$'.format(gamma),
    #               r'$\lambda = {:.4f}$'.format(lambd), r'$MAE = {:.4f}$'.format(mae)],
    #              ybox=0.82)
    # Exponential Separated Model
    # 10.5310 | S = e^(-λ*ε)[α*S_r + β*S_t + γ*S_v + δ*S_v*S_r/S_gas + ζ*S_v*S_t/S_gas]
    #         | λ: 0.0020
    #         | α: 1.0000, β: 0.3690, γ: 0.5271, δ: 0.0000, ζ: 1.0000
    lambd = 0.0020
    alpha, beta, gamma, delta, zeta = 1.0000, 0.3690, 0.5271, 0.0000, 1.0000
    mae = 10.5310
    predictions = np.exp(-lambd*epsilon)*(alpha*srot + beta*strans + gamma*svib + delta*svib*srot/s_gas + zeta*svib*strans/s_gas)
    plot_subplot(2, 'Model Predictions vs. Experimental Entropy', 
                 'Exponential Separated', y, predictions,
                 r'$S = e^{-\lambda\varepsilon} [\alpha S_{\text{rot}} + \beta S_{\text{trans}} + \gamma S_{\text{vib}} + \delta\frac{S_{\text{vib}}S_{\text{rot}}}{S_{\text{gas}}} + \zeta\frac{S_{\text{vib}}S_{\text{trans}}}{S_{\text{gas}}}]$',
                 [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                  r'$\delta = {:.2f}$'.format(delta), r'$\zeta = {:.2f}$'.format(zeta),
                  r'$\lambda = {:.4f}$'.format(lambd),
                  r'$MAE = {:.4f}$'.format(mae)], ybox=0.82)
    # Exponential Split Model
    # 10.1949 | S = e^(-λ*ε)[α*S_r + β*S_t + γ*S_v*S_r/S_gas + δ*S_v*S_t/S_gas] + ζ*S_v
    #         | λ: 0.0016
    #         | α: 0.8178, β: 0.4699, γ: 0.4721, δ: 1.0000, ζ: 0.3978
    lambd = 0.0016
    alpha, beta, gamma, delta, zeta = 0.8178, 0.4699, 0.4721, 1.0000, 0.3978
    mae = 10.1949
    predictions = np.exp(-lambd*epsilon)*(alpha*srot + beta*strans + gamma*svib*srot/s_gas + delta*svib*strans/s_gas) + zeta*svib
    plot_subplot(3, 'Exponential Split vs. Experimental Entropy', 
                 'Exponential', y, predictions,
                 r'$S = e^{-\lambda\varepsilon} [\alpha S_{\text{rot}} + \beta S_{\text{trans}} + \gamma\frac{S_{\text{vib}}S_{\text{rot}}}{S_{\text{gas}}} + \delta\frac{S_{\text{vib}}S_{\text{trans}}}{S_{\text{gas}}}] + \zeta S_{\text{vib}}$',
                 [r'$\alpha = {:.2f}$'.format(alpha), r'$\beta = {:.2f}$'.format(beta),
                  r'$\gamma = {:.2f}$'.format(gamma), r'$\delta = {:.2f}$'.format(delta),
                  r'$\zeta = {:.2f}$'.format(zeta), r'$\lambda = {:.4f}$'.format(lambd),
                  r'$MAE = {:.4f}$'.format(mae)], ybox=0.82)
    plt.tight_layout()
    # plt.savefig('final_regressions.pdf')
    plt.show()

if __name__ == '__main__':
    ploting()

