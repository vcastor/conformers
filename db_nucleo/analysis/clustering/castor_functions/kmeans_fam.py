# -*- coding: UTF-8 -*-
from itertools import combinations
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import numpy as np

# Accuracy
def accuracy_cluster(y_true, y_pred):
    return np.sum(y_true == y_pred)/len(y_true)

# ==============================
# Researcher over combinations
def kmeans_fam(df, cols, ndim, nclusters, use_svc=True):
    class_true = df['category'].values
    results = []

    # random_states = [0, 1, 7, 21, 99]
    # 20 random states
    random_states = list(range(20))
    le = LabelEncoder()
    class_true = le.fit_transform(class_true)

    combs = combinations(cols, ndim)
    for comb in combs:
        X = df[list(comb)].values

        accs = []
        # model = SVC(kernel='linear', random_state=42)
        for rs in random_states:
            X_train, X_test, y_train, y_test = train_test_split(
                    X, class_true, test_size=0.2, random_state=rs)
            model = SVC(kernel='rbf', random_state=rs)
            pred = model.fit(X_train, y_train).predict(X_test)
            acc = accuracy_cluster(y_test, pred)
            accs.append(acc)

        accs = np.array(accs)
        results.append((
            accs.mean(),
            accs.std(),
            comb))

    return sorted(results, key=lambda x: x[0], reverse=True)[:1]

