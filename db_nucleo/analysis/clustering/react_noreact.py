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
    'condensed_linear_response', 'P', 'Pf2'#, 'eigenchi'
]

# ==============================
# Auxiliary function to check for NaNs
def nan_in_df(df):
    """
    Checks for NaN values in the DataFrame and prints the rows containing NaNs.
    If NaNs are found, the function will raise an error.
    """
    nan_rows = df[df.isna().any(axis=1)]
    if not nan_rows.empty:
        print("DataFrame rows containing NaN values:")
        print(nan_rows)
        raise ValueError("DataFrame contains NaN values. Fix them before proceeding.")

# ==============================
# Here the main code starts
print('*****************************************')
print('Calssification: reactive and non-reactive')
print('*****************************************')
# for case in ['msc', 'conformers']:
for case in ['conformers']:
    df = connect_db(exp, cols, case)

    # Standardize the data
    scaler = StandardScaler()
    df_clustering = df[df['source'] != 'peculiar'].copy()
    df_scaled = df_clustering.copy()
    df_scaled[cols] = scaler.fit_transform(df_clustering[cols])

    # Clustering
    spliter = 'reactive/no-reactive'; ndim = 2; nclusters = 2
    dfclass = reactivity_classifier(df_scaled, exp[0], spliter)
    nan_in_df(dfclass)
    # kernels = ['linear', 'rbf', 'poly', 'sigmoid']
    kernels = ['rbf']
    for kernel in kernels:
        print(f'Using kernel: {kernel}')
        results = kmeans_all_clusters(dfclass, cols, ndim, nclusters, kernel=kernel)

        # print('==============================')
        # print(f'Classification for {case} data')
        for res in results:
            accuracy, std, feats = res
            print(f'Accuracy: {accuracy:.4f}')
            print(f'Standard Deviation: {std:.4f}')
            print(f'Features: {feats}')

    # plot_cluster(dfclass, df_clustering, ndim, nclusters, results[0][1])

    # Split the two regions of reactivity
    # regions_reactivity(dfclass, ndim, nclusters, results[0][1])

