#!/usr/bin/python3
import numpy as np
import pandas as pd
from castor_functions import *
from sklearn.preprocessing import StandardScaler

# ==============================
# Experimental parameters and properties
fam = ['aliphatic_amines', 'pyridines_quinolines_etc', 'azoles_and_azole_anions']
cols = [
    'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
    'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
    'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
    'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
    'condensed_linear_response', 'P', 'Pf2', 'eigenchi'
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
for case in ['msc', 'conformers']:
    df = all_families(cols, case)

    # Standardize the data
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[cols] = scaler.fit_transform(df_scaled[cols])

    # Clustering
    spliter = 'families'; ndim = 2; nclusters = 2
    dfclass = family_classifier(df_scaled, spliter)
    nan_in_df(dfclass)
    results = kmeans_fam(dfclass, cols, ndim, nclusters)

    print('==============================')
    print(f'Classification for {case} case')
    for res in results:
        accuracy, feats = res
        print(f'Accuracy: {accuracy:.4f}')
        print(f'Features: {feats}')

    # plot the best two clustering
    # plot_cluster(dfclass, df, ndim, nclusters, results[0][1])
    # for res in results:
    #     plot_cluster(dfclass, df_clustering, ndim, nclusters, res[1])

    # Split the two regions of reactivity
    # regions_reactivity(dfclass, ndim, nclusters, results[0][1])

