# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from scipy.ndimage import label
from sklearn.datasets import make_classification
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import LabelEncoder

# ==============================
# Researcher over combinations
def plot_cluster(df_scaled, df_noscaled, ndim, nclusters, comb, use_svc=True):
    class_true = df_scaled['category'].values

    X_scaled = df_scaled[list(comb)].values
    X_original = df_noscaled[list(comb)].values

    if use_svc:
        le = LabelEncoder()
        class_true = le.fit_transform(class_true)
        model = SVC(kernel='rbf', random_state=42)
        model.fit(X_scaled, class_true).predict(X_scaled)
        pred = model.predict(X_scaled)
    else:
        kmeans = KMeans(n_clusters=nclusters, random_state=42)
        pred = kmeans.fit_predict(X)

    # Create the mesh **in scaled space** for plotting
    x_min, x_max = X_scaled[:, 0].min() - 1, X_scaled[:, 0].max() + 1
    y_min, y_max = X_scaled[:, 1].min() - 1, X_scaled[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                         np.arange(y_min, y_max, 0.02))

    # Predict on mesh (scaled)
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)    

    # Plot decision regions + scaled data points
    plt.contourf(xx, yy, Z, alpha=0.4)
    plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=class_true, s=20, edgecolor='k')

    # Label the axes by their original feature names (but the coordinates are scaled!)
    plt.xlabel(comb[0])
    plt.ylabel(comb[1])
    plt.xticks(np.linspace(x_min, x_max, num=5),
               [f'{val:.2f}' for val in np.linspace(X_original[:, 0].min(), X_original[:, 0].max(), num=5)])
    plt.yticks(np.linspace(y_min, y_max, num=5),
               [f'{val:.2f}' for val in np.linspace(X_original[:, 1].min(), X_original[:, 1].max(), num=5)])
    plt.title(f'Clusters with {ndim} dimensions (scaled plot)')
    plt.show()

    # Label contiguous regions in the Z "map"
    structure = np.ones((3, 3))
    labeled_regions, num_features = label(Z, structure=structure)

    # Region assignment must also use scaled coordinates
    region_assignments = []
    for i, scaled_pt in enumerate(X_scaled):
        # Find the nearest mesh indices in scaled space
        ix = np.argmin((xx[0] - scaled_pt[0])**2)
        iy = np.argmin((yy[:, 0] - scaled_pt[1])**2)
        region_id = labeled_regions[iy, ix]
        region_assignments.append(region_id if region_id > 0 else 'No Reactive Region')

    # Save region assignments in df_scaled (or df_noscaled if you prefer)
    # df_scaled['Region'] = region_assignments

