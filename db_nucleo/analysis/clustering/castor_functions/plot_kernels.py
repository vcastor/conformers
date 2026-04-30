# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from scipy.ndimage import label
from sklearn.datasets import make_classification
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import LabelEncoder
from skimage import measure
from joblib import dump, load

# ==============================
# Researcher over combinations
def plot_cluster_kernel(df_scaled, df_noscaled, ndim, nclusters, comb):
    class_true = df_scaled['category'].values

    X_scaled = df_scaled[list(comb)].values
    X_original = df_noscaled[list(comb)].values

    le = LabelEncoder()
    class_true = le.fit_transform(class_true)
    model = SVC(kernel='linear', random_state=42)
    model.fit(X_scaled, class_true).predict(X_scaled)
    pred = model.predict(X_scaled)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.scatter(X_scaled[:, 0], X_scaled[:, 1], c=pred, cmap='viridis', s=50, edgecolors='k')
    ax.set_title('2D Kernel Plot')
    ax.set_xlabel(comb[0])
    ax.set_ylabel(comb[1])

    plt.show()

