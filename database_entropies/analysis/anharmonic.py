#!/usr/bin/python3 
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

def fetch_data(db_file_path):
    with sqlite3.connect(db_file_path) as conn:
        return pd.read_sql('SELECT vib_S, correctionS FROM PBE0', conn)

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
    vib, corr = data['vib_S'], data['correctionS']
    #
    # Contributions
    # plt.gca().set_aspect('equal', adjustable='box')
    # plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.2)
    # plt.scatter(y, strans, alpha=0.5, label='Translational')
    # plt.scatter(y, srot, alpha=0.5, label='Rotational')
    # plt.scatter(y, svib, alpha=0.5, label='Vibrational')
    plt.scatter(vib,corr)
    plt.xlabel(r'$\mathrm{S_{v}^{h}}$ $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    plt.ylabel(r'$\mathrm{\Delta S_{v}^{G}}$ $[\mathrm{JK^{-1}mol^{-1}}]$', size=16)
    # plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
    # plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # plt.savefig('final_regressions.pdf')
    plt.show()

if __name__ == '__main__':
    ploting()

