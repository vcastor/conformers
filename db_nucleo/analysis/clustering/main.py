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
    'condensed_liner_response', 'P', 'Pf2'
]

dynamic = [False, True]
for dyn in dynamic:
    df = connect_db(exp, cols, dynamic=dyn)

    # Standardize the data
    scaler = StandardScaler()
    df_clustering = df[df['source'] != 'peculiar'].copy()
    df_scaled = df_clustering.copy()
    df_scaled[cols] = scaler.fit_transform(df_clustering[cols])

    # # keep the peculiar data, aside for plotting
    # df_peculiar = df[df['source'] == 'peculiar']
    # df_peculiar_scaled = df_peculiar.copy()
    # df_peculiar_scaled[cols] = scaler.transform(df_peculiar[cols])

    print('*****************************************')
    print('Calssification: reactive and non-reactive')
    print('*****************************************')
    spliter = 2 # 2 : Reactive / Non-reactive
    dfclass = reactivity_classifier(df_scaled, exp[0], spliter)
    ndim = 2
    results = kmeans_all_clusters(dfclass, cols, ndim, spliter)
    for res in results:
        accuracy, feats = res
        print('==============================')
        print(f'Accuracy for {ndim} features: {accuracy:.2f}')
        print(f'Features: {feats}')

