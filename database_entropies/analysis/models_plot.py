#!/usr/bin/python3 
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS, rad FROM PBE', conn)
        # return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS, rad FROM PBE WHERE nconformers = 1', conn)

def prepare_data(data):
    data.dropna(inplace=True)
    return data

def plot_subplot(position, title, ylabel, y, predictions, equation_text, params_texts, ybox=0.77):
    plt.subplot(2, 3, position)
    plt.scatter(y, predictions, alpha=0.5)
    plt.title(title)
    plt.xlabel('Experimental Entropy')
    plt.ylabel(ylabel)
    textstr = equation_text + '\n' + ', '.join(params_texts[:-1]) + '\n' + params_texts[-1]
    plt.text(0.05, ybox, textstr, fontsize=9, transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.grid(True)

def ploting():
    data = fetch_data('../entropiesCOSMO.db')
    data = prepare_data(data)
    srot, strans, svib = data['rot_S'], data['trans_S'], data['vib_S']
    epsilon, y, corr = data['epsilon'], data['experimental_S'], data['correctionS']
    rad = data['rad']
    plt.figure(figsize=(12, 6))
    #
    s1 = srot + strans + svib
    s23 = (2/3)*(srot + strans) + svib
    s2nl =  0.578*(srot + strans) + svib + 0.403*(svib*srot/(srot+svib+strans) + svib*strans/(srot+svib+strans))
    s3nlv =  0.582*(srot + strans) + svib + 0.238*(svib*srot/(srot+svib+strans) + svib*strans/(srot+svib+strans))
    fgamma = 1 +0.4*np.arctan(np.tanh(0.131*rad))
    gdelta = 5.4*np.log(5.82/epsilon)
    s4nlv =  0.582*(srot + strans) + fgamma*svib + 0.238*(svib*srot/(srot+svib+strans) + svib*strans/(srot+svib+strans)) + gdelta
    s3eps = svib**1.05 - epsilon + 166
    # Average Contributions
    plt.subplot(1, 2, 1)
    plt.scatter(y, s1, alpha=0.5, label=r'$S_1^l$ $\alpha=1$ ')
    plt.scatter(y, s23, alpha=0.5, label=r'$S_1^l$ $\alpha=2/3$ ')
    plt.scatter(y, s2nl, alpha=0.5, label=r'$S_2^{nl}$')
    plt.xlabel(r'Standard Exp. Entropy $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'S$^{\mathrm{pred}}$', size=16)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # Delta S 
    plt.subplot(1, 2, 2)
    plt.scatter(y, s3nlv, alpha=0.5, label=r'$S_3^{nl,v-only}$')
    plt.scatter(y, s4nlv, alpha=0.5, label=r'$S_4^{nlv}$')
    plt.scatter(y, s3eps, alpha=0.5, label=r'$S_3^{eps}$')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.xlabel(r'Standard Exp. Entropy $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'S$^{\mathrm{pred}}$', size=16)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('models.pdf')
    # plt.show()

if __name__ == '__main__':
    ploting()

