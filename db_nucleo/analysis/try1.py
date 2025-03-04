#!/usr/bin/python3
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from itertools import combinations
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D

# Connect to the database
conn = sqlite3.connect('../nucleo_data.db')
cursor = conn.cursor()

# Properties to fetch
exp = ['experimental_N', 'experimental_Sn']
cols = [
    'mu', 'eta', 'softness', 'hyperhardness',
    'omega', 'nucleofuge', 'electrofuge', 'electrodonating', 'electroaccepting',
    'fplus', 'fminus', 'fzero', 'f2', 'sfplus', 'sfminus', 'sfzero', 's2',
    'muplusfplus', 'muminusfminus', 'wfplus', 'wf2', 'Sf2', 's2f2',
    'electro', 'nucleo', 'q_qtaim', 'q_hirshfeld',
    'electrostatic_potential', 'condensed_liner_response',
    'epsilon', 'rad'
]

# Fetch
queryMain = f'SELECT {", ".join(exp)}, {", ".join(cols)} FROM main WHERE nconformers IS NOT NULL'
queryNoReac = f'SELECT {", ".join(cols)} FROM non_reactive_N'

cursor.execute(queryMain)
reactive_data = cursor.fetchall()

cursor.execute(queryNoReac)
non_reactive_data = cursor.fetchall()

conn.close()

# Organize data into a DataFrame [add zeros for non-reactive data]
reactive_df = pd.DataFrame(reactive_data, columns=exp+cols)
noreactive_df = pd.DataFrame(non_reactive_data, columns=cols)
for col in exp:
    noreactive_df[col] = 0
df = pd.concat([reactive_df, noreactive_df], ignore_index=True)
df['no_reactive_N'] = (df['experimental_N'] == 0) & (df['experimental_Sn'] == 0)

# Define feature space for clustering
features = ['experimental_N', 'experimental_Sn', 'q_qtaim', 'softness', 'eta', 'electrostatic_potential', 'rad', 'epsilon', 'fzero', 'omega']
X = df[features].fillna(0)

# Artificial limit for nucleophile classification (middle of experimental values)
exp_n_mean = X['experimental_N'].mean()
df['good_nucleophile'] = (X['experimental_N'] > exp_n_mean)
df['bad_nucleophile'] = (X['experimental_N'] <= exp_n_mean)

# Assign categories based on criteria
df['category'] = np.where(df['no_reactive_N'], 'No Reactive Nitrogen',
                          np.where(df['good_nucleophile'], 'Good Nucleophile', 'Bad Nucleophile'))

# K-Means clustering for optional visualization
kmeans = KMeans(n_clusters=3, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

# 2D Visualization
plt.figure(figsize=(8, 6))
scatter = plt.scatter(X['experimental_N'], X['experimental_Sn'], c=kmeans.labels_, cmap='viridis')
plt.xlabel('Experimental N')
plt.ylabel('Experimental Sn')
plt.title('Clustering of Molecules')
plt.legend(*scatter.legend_elements(), title="Clusters")
plt.colorbar(scatter, label='Cluster')
plt.show()

# Save results
# df.to_csv('clustered_molecules.csv', index=False)

