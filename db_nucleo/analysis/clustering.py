#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D
from sklearn.model_selection import train_test_split

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

# Fetch data
queryMain = f'SELECT {", ".join(exp)}, {", ".join(cols)} FROM main WHERE nconformers IS NOT NULL'
queryNoReac = f'SELECT {", ".join(cols)} FROM non_reactive_N'

cursor.execute(queryMain)
reactive_data = cursor.fetchall()

cursor.execute(queryNoReac)
non_reactive_data = cursor.fetchall()

conn.close()

# Organize data into DataFrames
reactive_df = pd.DataFrame(reactive_data, columns=exp+cols)
noreactive_df = pd.DataFrame(non_reactive_data, columns=cols)

# For non-reactive, experimental values = 0
for col in exp:
    noreactive_df[col] = 0

df = pd.concat([reactive_df, noreactive_df], ignore_index=True)
df['no_reactive_N'] = (df['experimental_N'] == 0) & (df['experimental_Sn'] == 0)

# Define features for initial analysis
features = ['experimental_N', 'experimental_Sn', 'q_qtaim', 'softness', 'eta', 
            'electrostatic_potential', 'rad', 'epsilon', 'fzero', 'omega']

X = df[features].fillna(0)

# Define nucleophile categories
exp_n_mean = X['experimental_N'].mean()
df['good_nucleophile'] = (X['experimental_N'] > exp_n_mean)
df['bad_nucleophile'] = (X['experimental_N'] <= exp_n_mean)

df['category'] = np.where(df['no_reactive_N'], 'No Reactive Nitrogen',
                 np.where(df['good_nucleophile'], 'Good Nucleophile', 'Bad Nucleophile'))

# -------------------------------------------------------
# Physically inspired transformations for interpretability
# For example: (hyperhardness + mu)^2 and q_qtaim, eta
# -------------------------------------------------------
df['hyper_plus_mu_sq'] = (df['hyperhardness'] + df['mu'])**2

# Let's select a smaller, interpretable feature set for clustering
cluster_features = ['hyper_plus_mu_sq', 'q_qtaim', 'eta']
X_phys = df[cluster_features].fillna(0)

# -------------------------------------------------------
# Split data into train/val/test sets: 60%/20%/20%
# -------------------------------------------------------
X_train_val, X_test, y_train_val, y_test = train_test_split(X_phys, df['category'], test_size=0.2, random_state=42, stratify=df['category'])
X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.25, random_state=42, stratify=y_train_val)
# After this: X_train 60%, X_val 20%, X_test 20%

# -------------------------------------------------------
# K-Means Clustering on the training set only
# -------------------------------------------------------
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X_train)
train_clusters = kmeans.labels_

# Assign clusters to validation and test sets
val_clusters = kmeans.predict(X_val)
test_clusters = kmeans.predict(X_test)

# Add cluster info back to DataFrame for plotting (careful with indexing)
df.loc[X_train.index, 'cluster'] = train_clusters
df.loc[X_val.index, 'cluster'] = val_clusters
df.loc[X_test.index, 'cluster'] = test_clusters

# -------------------------------------------------------
# Interpretation:
# We can attempt to visualize the clusters in the transformed space
# and also overlay lines that might represent physical boundaries.
# For example, a surface where (hyperhardness+mu)^2 = q_qtaim.
# -------------------------------------------------------

fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')

# Plot training data
scatter = ax.scatter(df.loc[X_train.index, 'hyper_plus_mu_sq'],
                     df.loc[X_train.index, 'q_qtaim'],
                     df.loc[X_train.index, 'eta'],
                     c=df.loc[X_train.index, 'cluster'],
                     cmap='viridis', alpha=0.8, label='Train')

# Plot validation data (different marker)
ax.scatter(df.loc[X_val.index, 'hyper_plus_mu_sq'],
           df.loc[X_val.index, 'q_qtaim'],
           df.loc[X_val.index, 'eta'],
           c=df.loc[X_val.index, 'cluster'],
           cmap='viridis', marker='^', alpha=0.8, label='Validation')

# Plot test data (different marker)
ax.scatter(df.loc[X_test.index, 'hyper_plus_mu_sq'],
           df.loc[X_test.index, 'q_qtaim'],
           df.loc[X_test.index, 'eta'],
           c=df.loc[X_test.index, 'cluster'],
           cmap='viridis', marker='s', alpha=0.8, label='Test')

ax.set_xlabel('(hyperhardness + mu)^2')
ax.set_ylabel('q_qtaim')
ax.set_zlabel('eta')

plt.title('Clusters in Physically Interpretable Space')
plt.legend()

# -------------------------------------------------------
# Identify points in test set that are "near to fail":
# For simplicity, let's say we consider "failures" as test points
# that don't match the expected category or are outliers relative
# to cluster centers. One crude measure: distance to cluster center.
# -------------------------------------------------------
centers = kmeans.cluster_centers_
X_test_values = X_test.values
test_distances = np.min([np.linalg.norm(X_test_values - c, axis=1) for c in centers], axis=0)
threshold = np.percentile(test_distances, 95)  # top 5% furthest from any cluster center
fail_points = test_distances > threshold

# Mark these fail points on the plot with a red edge
ax.scatter(df.loc[X_test.index[fail_points], 'hyper_plus_mu_sq'],
           df.loc[X_test.index[fail_points], 'q_qtaim'],
           df.loc[X_test.index[fail_points], 'eta'],
           facecolors='none', edgecolors='r', s=100, label='Near Failure')

# Add a surface or line representing a physical boundary if needed
# For example, a surface where (hyperhardness+mu)^2 = q_qtaim:
# We'll just plot a line q_qtaim = (hyperhardness+mu)^2 at some fixed eta
# as a guide. Let's pick eta=mean(eta) for illustration.
eta_mean = df['eta'].mean()
h_vals = np.linspace(df['hyper_plus_mu_sq'].min(), df['hyper_plus_mu_sq'].max(), 100)
q_line = h_vals  # q_qtaim = hyper_plus_mu_sq
eta_line = np.full_like(h_vals, eta_mean)
ax.plot(h_vals, q_line, eta_line, 'r--', label='Example boundary: q_qtaim = (hyper+mu)^2 @ eta=mean')

plt.legend()
plt.show()

# -------------------------------------------------------
# In practice:
# - You can tune cluster_features for better physical meaning.
# - Adjust the "fail" criteria.
# - Add more domain-inspired lines or surfaces to interpret clusters.
# -------------------------------------------------------

