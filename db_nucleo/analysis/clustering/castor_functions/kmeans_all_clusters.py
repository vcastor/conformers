# -*- coding: UTF-8 -*-
from itertools import combinations
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

# Accuracy
def accuracy_cluster(y_true, y_pred):
    import numpy as np
    return np.sum(y_true == y_pred)/len(y_true)

# ==============================
# Researcher over combinations
def kmeans_all_clusters(df, cols, ndim, nclusters, use_svc=True):
    class_true = df['category'].values
    results = []

    if ndim == 3:
        fixed_cols = {'q_qtaim', 'condensed_linear_response'}
        combs = [comb for comb in combinations(cols, ndim) if fixed_cols.issubset(comb)]
    else:
        combs = combinations(cols, ndim)

    for comb in combs:
        X = df[list(comb)].values

        if use_svc:
            model = SVC(kernel='rbf', random_state=42)
            pred = model.fit(X, class_true).predict(X)
        else:
            kmeans = KMeans(n_clusters=nclusters, random_state=42)
            pred = kmeans.fit_predict(X)

        accuracy = accuracy_cluster(class_true, pred)
        results.append((accuracy, comb))

    return sorted(results, key=lambda x: x[0], reverse=True)[:5]

