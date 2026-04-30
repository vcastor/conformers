#!/usr/bin/python3
import numpy as np
import pandas as pd
from castor_functions import *
from sklearn.preprocessing import StandardScaler

# # ==============================
# # Experimental parameters and properties
# families = {
#     # 'aliphatic_amines': ['q_qtaim', 'condensed_linear_response'],
#     'pyridines_quinolines_etc': ['fminus', 'condensed_linear_response'],
#     # 'azoles_and_azole_anions': ['muplusfplus', 'condensed_linear_response'],
#     # 'azoles_and_azole_anions': ['P', 'condensed_linear_response'],
#     # 'azoles_and_azole_anions': ['q_qtaim', 'condensed_linear_response']
# }

# Linear kernel
families = {
    'aliphatic_amines': ['q_qtaim', 'condensed_linear_response'],
    # 'pyridines_quinolines_etc': ['q_qtaim', 'muplusfplus'],
    # 'azoles_and_azole_anions': ['sfzero', 'fplus']
}

for fam, comb in families.items():
    df = connect_fam(comb)

    # Standardize the data
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[comb] = scaler.fit_transform(df_scaled[comb])

    # Clustering
    spliter = 'family'; ndim = 2; nclusters = 2
    dfclass = family_classifier(df_scaled, fam)

    # plot the best two clustering
    plot_fam(dfclass, df, ndim, nclusters, fam, comb)

