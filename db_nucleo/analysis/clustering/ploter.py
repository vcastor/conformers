#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from castor_functions import *
from sklearn.preprocessing import StandardScaler

# Properties to fetch
exp  = ['experimental_N', 'experimental_Sn']
# cols = ['q_qtaim', 'condensed_linear_response']
cols = ['f2', 'electrostatic_potential']

df = connect_db(exp, cols, 'conformers')

# Standardize the data
scaler = StandardScaler()
df_clustering = df[df['source'] != 'peculiar'].copy()
df_scaled = df_clustering.copy()
df_scaled[cols] = scaler.fit_transform(df_clustering[cols])

# Clustering
spliter = 'reactive/no-reactive'; ndim = 2; nclusters = 2
dfclass = reactivity_classifier(df_scaled, exp[0], spliter)
# results = kmeans_all_clusters(dfclass, cols, ndim, nclusters)

# plot_cluster(dfclass, df_clustering, ndim, nclusters, cols)
plot_cluster_kernel(dfclass, df_clustering, ndim, nclusters, cols)


