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
    'eigenchi'
]

# Per-family plotting configuration: feature pair to display, axis limits in
# original (un-standardised) space, axis labels and the cross-validated
# accuracy/std to surface in the badge.
fam_config = {
    'aliphatic_amines': dict(
        comb=('q_qtaim', 'condensed_linear_response'),
        xlim=(-1.24, -0.40),
        ylim=(-6.24, -1.12),
        xlabel=r'$q(N)$',
        ylabel=r'$\chi(N)$',
        accuracy_text=r'97.0 $\pm$ 1.9 %',
    ),
    'pyridines_quinolines_etc': dict(
        comb=('fminus', 'condensed_linear_response'),
        xlim=(0.00, 1.10),
        ylim=(-6.24, -1.12),
        xlabel=r'$f^{-}(N)$',
        ylabel=r'$\chi(N)$',
        accuracy_text=r'92.1 $\pm$ 4 %',
    ),
    'azoles_and_azole_anions': dict(
        comb=('q_qtaim', 'condensed_linear_response'),
        xlim=(-1.24, -0.40),
        ylim=(-6.24, -1.12),
        xlabel=r'$q(N)$',
        ylabel=r'$\chi(N)$',
        accuracy_text=r'96.9 $\pm$ 2.0 %',
    ),
}

# ==============================
# Here the main code starts
print('*****************************************')
print('Calssification: family vs. rest')
print('*****************************************')
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

    # Render the family plot using the manually chosen feature pair and
    # cross-validated accuracy band, not the optimizer's pick.
    cfg = fam_config[fam]
    plot_fam(dfclass, df, ndim, nclusters, fam, cfg['comb'],
             xlim=cfg['xlim'], ylim=cfg['ylim'],
             xlabel=cfg['xlabel'], ylabel=cfg['ylabel'],
             accuracy_text=cfg['accuracy_text'])
