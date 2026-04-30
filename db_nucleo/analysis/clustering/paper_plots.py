#!/usr/bin/python3
import numpy as np
import pandas as pd
from castor_functions import *
from sklearn.preprocessing import StandardScaler

families = ['aliphatic_amines', 'pyridines_quinolines_etc', 'azoles_and_azole_anions']
cols = ['fminus', 'muplusfplus', 'q_qtaim', 'condensed_linear_response']

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
        accuracy, feats = res
        print(f'Accuracy: {accuracy:.4f}')
        print(f'Features: {feats}')

    # plot the best two clustering
    plot_cluster(dfclass, df, ndim, nclusters, results[0][1])
    # for res in results:
    #     plot_cluster(dfclass, df_clustering, ndim, nclusters, res[1])



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
    kernels = ['linear', 'rbf', 'poly', 'sigmoid']
    for kernel in kernels:
        print(f'Using kernel: {kernel}')
        results = kmeans_all_clusters(dfclass, cols, ndim, nclusters, kernel=kernel)

        # print('==============================')
        # print(f'Classification for {case} data')
        for res in results:
            accuracy, feats = res
            print(f'Accuracy: {accuracy:.4f}')
            print(f'Features: {feats}')

