#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.cluster import contingency_matrix

# ==============================
# Researcher over combinations
def kmeans_combinations(df, cols, ndim):
    y_true = df['category'].values
    best_accuracy = -1
    best_feats = None
    best_model = None
    best_map = None

    combos = combinations(cols, ndim)

    for combo in combos:
        combo = list(combo)
        X = df[combo].values

        kmeans = KMeans(n_clusters=4, random_state=42)
        y_pred = kmeans.fit_predict(X)

        accuracy = accuracyf(y_true, y_pred)

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_feats = combo
            best_model = kmeans
            best_map = label_map(y_true, y_pred)

    return best_accuracy, best_feats, best_model, best_map

# ==============================
# Connect to the database
conn = sqlite3.connect('../../nucleo_data.db')
cursor = conn.cursor()

# Properties to fetch
exp  = ['experimental_N', 'experimental_Sn']
cols = [
    'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
    'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
    'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
    'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
    'condensed_liner_response'
]

# Queries:
queryReact = f'''
SELECT {", ".join(exp)}, {", ".join(cols)} 
FROM main
WHERE nconformers IS NOT NULL
AND (
  comment NOT LIKE "%&%"
  OR comment LIKE "%[&]"
)
'''

queryNoReac = f'SELECT {", ".join(cols)} FROM non_reactive_N'

queryPeculiar = f'''
SELECT {", ".join(exp)}, {", ".join(cols)} 
FROM main
WHERE nconformers IS NOT NULL
AND comment LIKE "%&%"
AND comment NOT LIKE "%[&]"
'''

cursor.execute(queryReact)
reactive_data = cursor.fetchall()

cursor.execute(queryPeculiar)
peculiar_data = cursor.fetchall()

cursor.execute(queryNoReac)
non_reactive_data = cursor.fetchall()

conn.close()

# ==============================
# Organize data into DataFrames
reactive_df = pd.DataFrame(reactive_data, columns=exp+cols)
peculiar_df = pd.DataFrame(peculiar_data, columns=exp+cols)
noreactive_df = pd.DataFrame(non_reactive_data, columns=cols)

# For non-reactive, define experimental values = 0
noreactive_df[exp] = 0

# Tag dataframes by source
reactive_df['source'] = 'reactive'
peculiar_df['source'] = 'peculiar'
noreactive_df['source'] = 'non_reactive'

# Combine all into one DataFrame
df = pd.concat([reactive_df, peculiar_df, noreactive_df], ignore_index=True)

# Identify no-reactive nitrogen cases
df['no_reactive_N'] = (df['experimental_N'] == 0) & (df['experimental_Sn'] == 0)

# Quantiles for experimental_N (only for those that are not zero and not peculiar)
mask_for_quantiles = (~df['no_reactive_N']) & (df['source'] != 'peculiar')
q1 = df.loc[mask_for_quantiles, 'experimental_N'].quantile(0.25)
q2 = df.loc[mask_for_quantiles, 'experimental_N'].quantile(0.75)

# descriptors not present in the database
# P = 1/γ; Pf2 = f2/γ; hyperhardness = γ
df['P'] = 1/df['hyperhardness']
df['Pf2'] = df['f2']/df['hyperhardness']

# Initialize category column
df['category'] = None

# Assign categories
df.loc[df['no_reactive_N'], 'category'] = 'No Reactive Nitrogen'
df.loc[(df['source'] == 'peculiar') & (df['category'].isnull()), 'category'] = 'Peculiar'

# For the remaining (reactive ones):
# for expparam in exp:
remaining_mask = df['category'].isnull()
df.loc[(remaining_mask) & (df['experimental_N'] <= q1), 'category'] = 'Bad Nucleophile'
df.loc[(remaining_mask) & (df['experimental_N'] > q1) & (df['experimental_N'] <= q2), 'category'] = 'Good Nucleophile'
df.loc[(remaining_mask) & (df['experimental_N'] > q2), 'category'] = 'Very Good Nucleophile'

# ==============================
# Standardize the data
df_clustering = df[df['category'] != 'Peculiar'].copy()
scaler = StandardScaler()
df_scaled = df_clustering.copy()
df_scaled[cols] = scaler.fit_transform(df_clustering[cols])

# keep the peculiar data, aside for plotting
df_peculiar = df[df['category'] == 'Peculiar']
df_peculiar_scaled = df_peculiar.copy()
df_peculiar_scaled[cols] = scaler.transform(df_peculiar[cols])

# Encode categories
cat_to_num = {
    'No Reactive Nitrogen': 0,
    'Bad Nucleophile': 1,
    'Good Nucleophile': 2,
    'Very Good Nucleophile': 3
}
df_scaled['category'] = df_scaled['category'].map(cat_to_num)

# ==============================
# Clustering
results = {}

for dims in [3, 4, 5]:
    score, feats, model, bmap = kmeans_combinations(df_scaled, cols, dims)
    results[dims] = {
        'score': score,
        'feats': feats,
        'model': model,
        'bmap': bmap
    }

