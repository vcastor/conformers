# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from scipy.ndimage import label
from sklearn.preprocessing import LabelEncoder

# Pretty axis labels for known descriptors. Anything not listed here falls
# back to its raw column name.
FEATURE_LABELS = {
    'q_qtaim':                   r'$q_{\mathrm{QTAIM}}$',
    'q_hirshfeld':               r'$q_{\mathrm{Hirshfeld}}$',
    'condensed_linear_response': r'$\chi$',
    'electrostatic_potential':   r'$V_{\mathrm{ESP}}$',
    'fminus':                    r'$f^{-}$',
    'fplus':                     r'$f^{+}$',
    'fzero':                     r'$f^{0}$',
    'eigenchi':                  r'$\chi_{\mathrm{eig}}$',
}


def plot_cluster(df_scaled, df_noscaled, ndim, nclusters, comb, use_svc=True,
                 xlim=None, ylim=None, accuracy_text=None,
                 xlabel=None, ylabel=None, title='Reactive Regions'):
    """
    2D visualisation of an SVM (or k-means) classifier for the chosen feature
    pair `comb`.  The plot is rendered in the *original* (un-standardised)
    feature space, so `xlim` and `ylim` can be passed in physically meaningful
    units.

    Parameters
    ----------
    xlim, ylim : (lo, hi) tuple in original space.  If None, padded data range.
    accuracy_text : string shown in the badge.  If None, in-sample accuracy is
        computed and displayed (e.g. '92.2%').  Pass something like
        '91.8 $\\pm$ 2.0 %' to surface the cross-validated value instead.
    xlabel, ylabel : axis labels.  If None, looked up in FEATURE_LABELS.
    """
    class_true = df_scaled['category'].values

    X_scaled = df_scaled[list(comb)].values
    X_orig = df_noscaled[list(comb)].values

    if use_svc:
        le = LabelEncoder()
        class_true = le.fit_transform(class_true)
        model = SVC(kernel='rbf', random_state=42)
        model.fit(X_scaled, class_true)
        pred = model.predict(X_scaled)
    else:
        model = KMeans(n_clusters=nclusters, random_state=42)
        pred = model.fit_predict(X_scaled)

    # ------------------------------------------------------------------
    # Plot extents in original space (caller can override)
    # ------------------------------------------------------------------
    if xlim is None:
        x_pad = 0.1 * (X_orig[:, 0].max() - X_orig[:, 0].min())
        x_min, x_max = X_orig[:, 0].min() - x_pad, X_orig[:, 0].max() + x_pad
    else:
        x_min, x_max = xlim
    if ylim is None:
        y_pad = 0.1 * (X_orig[:, 1].max() - X_orig[:, 1].min())
        y_min, y_max = X_orig[:, 1].min() - y_pad, X_orig[:, 1].max() + y_pad
    else:
        y_min, y_max = ylim

    # Linear map between original and scaled coordinates per feature
    # (StandardScaler: scaled = (orig - mean) / std).
    mean_x, std_x = X_orig[:, 0].mean(), X_orig[:, 0].std()
    mean_y, std_y = X_orig[:, 1].mean(), X_orig[:, 1].std()

    step = max(x_max - x_min, y_max - y_min) / 400
    xx, yy = np.meshgrid(np.arange(x_min, x_max + step, step),
                         np.arange(y_min, y_max + step, step))

    # Predict on the mesh after mapping each point back to scaled space
    xx_s = (xx - mean_x) / std_x
    yy_s = (yy - mean_y) / std_y
    Z = model.predict(np.c_[xx_s.ravel(), yy_s.ravel()]).reshape(xx.shape)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    plt.figure(figsize=(12, 8))
    plt.contourf(xx, yy, Z, alpha=0.4, extend='both', cmap='viridis')
    plt.scatter(X_orig[:, 0], X_orig[:, 1], c=class_true, s=60, edgecolor='k')

    misclassified = pred != class_true
    plt.scatter(X_orig[misclassified, 0], X_orig[misclassified, 1],
                c='black', marker='x', s=150, label='Misclassified', linewidth=3)

    plt.xlabel(xlabel if xlabel is not None
               else FEATURE_LABELS.get(comb[0], comb[0]), fontsize=36)
    plt.ylabel(ylabel if ylabel is not None
               else FEATURE_LABELS.get(comb[1], comb[1]), fontsize=36)
    plt.title(title, fontsize=40)
    plt.xticks(fontsize=26)
    plt.yticks(fontsize=26)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    # Annotate contiguous decision regions
    structure = np.ones((3, 3))
    labeled_regions, num_regions = label(Z, structure=structure)

    region_assignments = []
    for orig_pt in X_orig:
        ix = np.argmin((xx[0] - orig_pt[0])**2)
        iy = np.argmin((yy[:, 0] - orig_pt[1])**2)
        region_id = labeled_regions[iy, ix]
        region_assignments.append(region_id if region_id > 0 else 'No Reactive Region')
    df_scaled['Region'] = region_assignments

    region_centers = []
    for label_id in range(1, num_regions + 1):
        mask = labeled_regions == label_id
        if not np.any(mask):
            continue
        y_coords, x_coords = np.where(mask)
        cx = x_min + x_coords.mean() * step
        cy = y_min + y_coords.mean() * step
        if x_min <= cx <= x_max and y_min <= cy <= y_max:
            region_centers.append((cx, cy))

    for idx, (cx, cy) in enumerate(region_centers, start=1):
        plt.text(cx, cy, f'Region {idx}', fontsize=22, color='black',
                 weight='bold', ha='center', va='center',
                 bbox=dict(facecolor='yellow', edgecolor='black',
                           boxstyle='round,pad=0.3', alpha=0.6))

    # Accuracy badge — caller-supplied string takes precedence over in-sample
    if accuracy_text is None:
        accuracy_text = f'{(pred == class_true).sum() / len(class_true) * 100:.1f}%'
    label_text = f'$\\times$ Misclassified\nAccuracy: {accuracy_text}'
    plt.text(x_max - 0.02 * (x_max - x_min), y_max - 0.02 * (y_max - y_min),
             label_text, fontsize=22, color='black', ha='right', va='top',
             bbox=dict(facecolor='white', edgecolor='black',
                       boxstyle='round,pad=0.4', alpha=0.8))

    plt.tight_layout()
    plt.show()
