#!/usr/bin/python3
import numpy as np
import pandas as pd
from castor_functions import *
from sklearn.preprocessing import StandardScaler

# ==============================
# Experimental parameters and properties
families = ['aliphatic_amines', 'pyridines_quinolines_etc', 'azoles_and_azole_anions']

cols = [
    'fminus', 
    'q_qtaim', 
    'condensed_linear_response', 
]

# cols = [
#     'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
#     'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
#     'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
#     'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
#     'condensed_linear_response', 'P', 'Pf2'
# ]

# ==============================
# Here the main code starts
print('*****************************************')
print('Calssification: reactive and non-reactive')
print('*****************************************')
# for case in ['msc', 'conformers']:
for fam in families:
    df = connect_fam(cols)

    # Standardize the data
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[cols] = scaler.fit_transform(df_scaled[cols])

    # Clustering
    spliter = 'family'; ndim = 2; nclusters = 2
    dfclass = family_classifier(df_scaled, fam)
    results = kmeans_fam(dfclass, cols, ndim, nclusters)

    print('==============================')
    print(f'Classification for {fam} family')
    for res in results:
        accuracy, std, feats = res
        print(f'Accuracy: {accuracy:.4f}')
        print(f'Standard Deviation: {std:.4f}')
        print(f'Features: {feats}')

    # plot the best two clustering
    # plot_fam(dfclass, df, ndim, nclusters, fam, results[0][1])
    # for res in results:
    #     plot_cluster(dfclass, df_clustering, ndim, nclusters, res[1])

