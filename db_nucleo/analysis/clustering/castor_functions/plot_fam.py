# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from scipy.ndimage import label
from sklearn.preprocessing import LabelEncoder

from .plot_clusters import FEATURE_LABELS


def plot_fam(df_scaled, df_noscaled, ndim, nclusters, fam, comb,
             xlim=None, ylim=None, accuracy_text=None,
             xlabel=None, ylabel=None, title=None):
    """
    2D family classification plot in the original (un-standardised) feature
    space.  Limits, axis labels, title and accuracy badge are caller-supplied.

    Parameters
    ----------
    fam   : family key, used as the default title when `title` is None.
    comb  : 2-tuple of feature names to plot (x, y).
    xlim, ylim : (lo, hi) tuples in original space.  If None, padded data range.
    accuracy_text : string to render in the badge (e.g. '92.1 $\\pm$ 4 %').
    xlabel, ylabel : axis labels.  If None, looked up in FEATURE_LABELS.
    """
    class_true = df_scaled['category'].values

    X_scaled = df_scaled[list(comb)].values
    X_orig = df_noscaled[list(comb)].values

    le = LabelEncoder()
    class_true = le.fit_transform(class_true)
    # RBF matches the kernel used in kmeans_fam, so the in-sample boundary
    # tracks the cross-validated performance reported in the badge.
    model = SVC(kernel='rbf', random_state=42)
    model.fit(X_scaled, class_true)
    pred = model.predict(X_scaled)

    # ------------------------------------------------------------------
    # Plot extents (in original space; caller may override)
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

    # Per-feature linear map between scaled and original coordinates.
    mean_x, std_x = X_orig[:, 0].mean(), X_orig[:, 0].std()
    mean_y, std_y = X_orig[:, 1].mean(), X_orig[:, 1].std()

    step = max(x_max - x_min, y_max - y_min) / 400
    xx, yy = np.meshgrid(np.arange(x_min, x_max + step, step),
                         np.arange(y_min, y_max + step, step))

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

    if title is None:
        title = {
            'aliphatic_amines':         'Aliphatic Amines',
            'pyridines_quinolines_etc': 'Pyridines, Quinolines',
            'azoles_and_azole_anions':  'Azoles',
        }.get(fam, fam)
    plt.title(title, fontsize=40)
    plt.xticks(fontsize=26)
    plt.yticks(fontsize=26)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    if accuracy_text is None:
        accuracy_text = f'{(pred == class_true).sum() / len(class_true) * 100:.1f}%'
    label_text = f'$\\times$ Misclassified\nAccuracy: {accuracy_text}'
    plt.text(x_min + 0.03 * (x_max - x_min), y_max - 0.03 * (y_max - y_min),
             label_text, fontsize=22, color='black', ha='left', va='top',
             bbox=dict(facecolor='white', edgecolor='black',
                       boxstyle='round,pad=0.4', alpha=0.8))

    plt.tight_layout()
    plt.show()
