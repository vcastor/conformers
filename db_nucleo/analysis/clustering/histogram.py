#!/usr/bin/python3
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture

# Connect to the database
conn = sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db')
cursor = conn.cursor()

query = f'SELECT experimental_N FROM parameters WHERE nconformers > 0 AND experimental_N > 0'

cursor.execute(query)
data = cursor.fetchall()

N_values = np.array([x[0] for x in data]).reshape(-1, 1)

cursor.close()

# K-means (Elbow Method)
intertia = []; k_range = range(1,4)
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(N_values)
    intertia.append(kmeans.inertia_)

# Plot the Elbow Method
plt.plot(k_range, intertia, marker='o', linestyle='--')
plt.xlabel('Number of clusters')
plt.ylabel('Inertia')
plt.title('Elbow Method')
plt.show()

# Gaussian Mixture Model
bic_scores = []
for k in k_range:
    gmm = GaussianMixture(n_components=k, random_state=42)
    gmm.fit(N_values)
    bic_scores.append(gmm.bic(N_values))

# Plot the BIC scores
plt.plot(k_range, bic_scores, marker='o', linestyle='--')
plt.xlabel('Number of clusters')
plt.ylabel('BIC score')
plt.title('BIC for Gaussian Mixture Model')
plt.show()

# Suggested number of clusters
optimal_k = k_range[np.argmin(bic_scores)]
print(f'Optimal number of clusters: {optimal_k}')

# Histogram
plt.hist(N_values, bins=24, edgecolor='black')
plt.xlabel('N')
plt.ylabel('Frequency')
plt.title('Histogram of N values')
plt.show()

