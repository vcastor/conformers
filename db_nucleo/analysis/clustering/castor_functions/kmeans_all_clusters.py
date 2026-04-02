# -*- coding: UTF-8 -*-
from itertools import combinations
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np

# Accuracy
def accuracy_cluster(y_true, y_pred):
    return np.sum(y_true == y_pred)/len(y_true)

# ==============================
# Researcher over combinations
def kmeans_all_clusters(df, cols, ndim, nclusters, use_svc=True, kernel='linear'):
    class_true = df['category'].values
    results = []

    random_states = [0, 1, 7, 21, 99]
    combs = combinations(cols, ndim)

    for comb in combs:
        X = df[list(comb)].values

        accs = []
        for rs in random_states:
            X_train, X_test, y_train, y_test = train_test_split(
                X, class_true, test_size=0.3, random_state=rs)
            model = SVC(kernel=kernel, random_state=rs)
            pred = model.fit(X_train, y_train).predict(X_test)
            acc  = accuracy_cluster(y_test, pred)
            accs.append(acc)

        accs = np.array(accs)
        results.append((
            accs.mean(),
            accs.std(),
            comb))

    return sorted(results, key=lambda x: x[0], reverse=True)[:1]

