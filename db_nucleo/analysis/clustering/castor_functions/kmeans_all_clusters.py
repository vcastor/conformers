# -*- coding: UTF-8 -*-
from itertools import combinations
from sklearn.cluster import KMeans
from sklearn.svm import SVC

# Accuracy
def accuracy_cluster(y_true, y_pred):
    import numpy as np
    return np.sum(y_true == y_pred)/len(y_true)

# ==============================
# Researcher over combinations
def kmeans_all_clusters(df, cols, ndim, n_clusters):
    class_true = df['category'].values
    best_accuracy = -1
    best_feats = None

    combs = combinations(cols, ndim)

    results = []

    for comb in combs:
        X = df[list(comb)].values

        # kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        # pred = kmeans.fit_predict(X)

        poli_svc = SVC(kernel='rbf', random_state=42)
        pred = poli_svc.fit(X, class_true).predict(X)

        accuracy = accuracy_cluster(class_true, pred)
        results.append((accuracy, comb))

    top_results = sorted(results, key=lambda x: x[0], reverse=True)[:5]

    return top_results

