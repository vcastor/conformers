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
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0, linewidths=0.5)
plt.title("Correlation Matrix Heatmap")
# plt.show()

