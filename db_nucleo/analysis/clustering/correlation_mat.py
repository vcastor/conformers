#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from castor_functions import *

exp  = ['experimental_N', 'experimental_Sn']
cols = [ 
    'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
    'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
    'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
    'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
    'condensed_linear_response', 'P', 'Pf2'
]
label_map = {
    'mu':       r'$\mu$',
    'eta':      r'$\eta$',
    'softness': r'$S$',
    'hyperhardness': r'$\gamma$',
    'omega':         r'$\omega$',
    'nucleofuge':    'nucleofuge',
    'electrofuge':   'e fuge',
    'electrodonating': 'e donating',
    'electroaccepting': 'e accepting',
    'fplus': r'$f^+$',
    'fminus': r'$f^-$',
    'fzero': r'$f^0$',
    'f2': r'$f^2$',
    'sfplus': r'$sf^+$',
    'sfminus': r'$sf^-$',
    'sfzero': r'$sf^0$',
    's2': r'$s^2$',
    'muplusfplus': r'$\mu^+ f^+$',
    'muminusfminus': r'$\mu^- f^-$',
    'wfplus': r'$w^+$',
    'wf2': r'$w^2$',
    'Sf2': r'$S^2$',
    's2f2': r'$S^2 f^2$',
    'nucleo': 'nucleophilicity',
    'q_qtaim': r'$q_{QTAIM}$',
    'q_hirshfeld': r'$q_{Hirshfeld}$',
    'electrostatic_potential': 'e potential',
    'condensed_linear_response': r'$\chi(N)$',
    'P': r'$P$',
    'Pf2': r'$Pf^2$',
    'experimental_N': r'$N_{Mayr}$',
    'experimental_Sn': r'$Sn_{Mayr}$'
}

df = connect_db(exp, cols)
# df = df.drop('experimental_N', axis=1)
# df = df.drop('experimental_Sn', axis=1)
df = df.drop('smiles', axis=1)
df = df.drop('solvent', axis=1)
df = df.drop('atom_analysed', axis=1)
df = df.drop('source', axis=1)

# Compute the correlation matrix
corr_matrix = df.corr()

# corr_matrix_abs = corr_matrix.abs()
# np.fill_diagonal(corr_matrix_abs.values, np.nan)

# Get the top 5 most correlated pairs
for expval in exp:
    top_correlations = (
        corr_matrix[expval]
        .dropna()
        .sort_values(ascending=False)
        .head(5)
    )

    print("Top 5 Most Correlated Feature Pairs:")
    print(top_correlations)


# Plot the heatmap
plt.figure()
corr_matrix.rename(index=label_map, columns=label_map, inplace=True)
sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0, linewidths=0.5)
plt.xticks(fontsize=30)
plt.yticks(fontsize=30)
plt.title("Correlation Matrix Heatmap", fontsize=42)
plt.tight_layout()
# plt.savefig('heatmap.pdf')
plt.show()

