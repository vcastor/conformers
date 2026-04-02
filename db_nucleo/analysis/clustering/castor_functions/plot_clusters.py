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

    # Size of the Plot
    plt.figure(figsize=(12, 8))
    # Create the mesh **in scaled space** for plotting
    x_min, x_max = X_scaled[:, 0].min() - 1.5, X_scaled[:, 0].max() + 0.8
    y_min, y_max = X_scaled[:, 1].min() - 1, X_scaled[:, 1].max() + 2
    delta = 0.02 # just to avoid the border
    step = 0.01
    xx, yy = np.meshgrid(np.arange(x_min, x_max+delta, step),
                         np.arange(y_min, y_max+delta, step))

    # Predict on mesh (scaled)
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)    

    # Plot decision regions + scaled data points
    plt.contourf(xx, yy, Z, alpha=0.4, extend='both', cmap='viridis')
    plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=class_true, s=60, edgecolor='k')

    # Mark misclassified points
    misclassified = pred != class_true
    plt.scatter(X_scaled[misclassified, 0], X_scaled[misclassified, 1],
                c='black', marker='x', s=150, label='Misclassified', linewidth=3)

    # Re-scale the ticks to the original space
    x_factor = (X_original[:, 0].max() - X_original[:, 0].min())/(X_scaled[:, 0].max() - X_scaled[:, 0].min())
    y_factor = (X_original[:, 1].max() - X_original[:, 1].min())/(X_scaled[:, 1].max() - X_scaled[:, 1].min())
    x_offset = X_original[:, 0].min() - X_scaled[:, 0].min()*x_factor
    y_offset = X_original[:, 1].min() - X_scaled[:, 1].min()*y_factor
    x_start = x_min*x_factor + x_offset
    y_start = y_min*y_factor + y_offset
    x_end   = x_max*x_factor + x_offset
    y_end   = y_max*y_factor + y_offset
    xtickslables = [f'{val:.2f}' for val in np.linspace(x_start, x_end, num=5)]
    ytickslables = [f'{val:.2f}' for val in np.linspace(y_start, y_end, num=5)]

    # Label the axes by their original feature names (but the coordinates are scaled!)
    plt.xlabel(r"q(N)", fontsize=36) # comb[0]
    plt.ylabel(r"$\chi (N)$", fontsize=36) # comb[1]
    plt.xticks(np.linspace(x_min, x_max, num=5), xtickslables, fontsize=26)
    plt.yticks(np.linspace(y_min, y_max, num=5), ytickslables, fontsize=26)
    plt.title(f'Reactive Regions', fontsize=40)

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
    df_scaled['Region'] = region_assignments

    # Region centers
    region_centers = []
    for label_id in range(1, 3):
        mask = labeled_regions == label_id
        if np.sum(mask) == 0:
            continue
        y_coords, x_coords = np.where(mask)
        x_mean = x_coords.mean()
        y_mean = y_coords.mean()
        x_plot = x_min + x_mean * step
        y_plot = y_min + y_mean * step
        region_centers.append((x_plot, y_plot))

    # Accuracy and colour code
    handles, labels = plt.gca().get_legend_handles_labels()
    accuracy = (pred == class_true).sum()/len(class_true)
    label_text = (
        f'$\\times$ {labels[0]}\nAccuracy: {accuracy * 100:.1f}%'
    )
    plt.text(
    x_max - 3.5, y_max - 1.5, 
    label_text,
    fontsize=26, 
    color='black',
    bbox=dict(
        facecolor='white', 
        edgecolor='black', 
        boxstyle='round,pad=0.4', 
        alpha=0.8
        )
    )

    # You decide which label ID is which (e.g., based on majority class in that region)
    plt.text(region_centers[0][0]-1.2, region_centers[0][1]-1, 'Region 1',
             fontsize=24, color='black', weight='bold',
             bbox=dict(facecolor='yellow', edgecolor='black', boxstyle='round,pad=0.3', alpha=0.6))

    plt.text(region_centers[1][0]-0.5, region_centers[1][1]+0.5, 'Region 2',
             fontsize=24, color='black', weight='bold',
             bbox=dict(facecolor='yellow', edgecolor='black', boxstyle='round,pad=0.3', alpha=0.6))

    # plt.text(region_centers[2][0], region_centers[2][1], 'No React',
    #          fontsize=11, color='white', weight='bold',
    #          bbox=dict(facecolor='purple', edgecolor='black', boxstyle='round,pad=0.3', alpha=0.6))

    plt.tight_layout()
    plt.show()
    # plt.savefig('react_noreact.pdf')

    # Save the model
    # dump(model, 'rbf_svc_model.joblib')
    # to load:
    # model = load('rbf_svc_model.joblib')
    # model.predict(new_scaled_data)  # input must be scaled the same way!


    # # Access components of the decision function
    # support_vectors = model.support_vectors_
    # dual_coefs = model.dual_coef_[0]
    # intercept = model.intercept_[0]
    # gamma = model._gamma
    # print(f"Support Vectors: {support_vectors}")
    # print(f"Dual Coefficients: {dual_coefs}")
    # print(f"Intercept: {intercept}")
    # print(f"Gamma: {gamma}")
    # print("for f(x) = sum_i dual_coef_i * K(support_vector_i, x) + intercept")


