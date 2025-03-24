#!/usr/bin/python3
import numpy as np
import pandas as pd
from castor_functions import *
from sklearn.preprocessing import StandardScaler

# ==============================
# Experimental parameters and properties
exp  = ['experimental_N', 'experimental_Sn']
cols = [
    'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
    'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
    'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
    'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
    'condensed_linear_response', 'P', 'Pf2'
]

# ==============================
# Here the main code starts
print('*****************************************')
print('Calssification: good and bad nucleophiles')
print('*****************************************')
for case in ['conformers']:
    for exp_val in exp:
        df = connect_db(exp, cols, case)

        # Standardize the data
        scaler = StandardScaler()
        df_clustering = df[df['source'] != 'peculiar'].copy()
        df_scaled = df_clustering.copy()
        df_scaled[cols] = scaler.fit_transform(df_clustering[cols])

        # Clustering
        spliter = 'good/bad'; ndim = 3; nclusters = 2
        dfclass = reactivity_classifier(df_scaled, exp_val, spliter)
        results = kmeans_all_clusters(dfclass, cols, ndim, nclusters)

        print('==============================')
        print(f'Classification for {case} data and {exp_val} parameter')
        for res in results:
            accuracy, feats = res
            print(f'Accuracy: {accuracy:.4f}')
            print(f'Features: {feats}')

        plot_cluster(dfclass, ndim, nclusters, results[0][1])

