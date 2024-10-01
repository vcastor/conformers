#!/usr/bin/python3 
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S, correctionS FROM PBE0', conn)

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
    plt.figure(figsize=(12, 6))
    # Average Contributions
    plt.subplot(1, 2, 2)
    plt.scatter(y, strans, alpha=0.5, label='Translational')
    plt.scatter(y, srot, alpha=0.5, label='Rotational')
    plt.scatter(y, svib, alpha=0.5, label='Vibrational')
    plt.xlabel(r'Experimental Entropy $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'Average Contributions $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # Delta S 
    plt.subplot(1, 2, 1)
    plt.scatter(svib, corr, alpha=0.5)
    plt.xlabel(r'$\mathrm{S_{v}^{h}}$ $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'$\mathrm{\overline{\Delta S}_{v}^{G}}$ $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('anharmonic_contributions.pdf')
    # plt.show()

if __name__ == '__main__':
    ploting()

