# -*- coding: UTF-8 -*-
import sqlite3
import numpy as np
import pandas as pd
from sklearn.svm import SVC
from scipy.ndimage import label
from sklearn.datasets import make_classification

# ==============================
# Connect to the database
def regions_reactivity(df, ndim, nclusters, comb):
    """
    Connect to the database and retrieve data for each table
    adding a 'source column to indicate its origin.
    """
    class_true = df['category'].values

    X = df[list(comb)].values

    model = SVC(kernel='rbf', random_state=42)
    model.fit(X, class_true).predict(X)

    # Meshgrid
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02), np.arange(y_min, y_max, 0.02))

    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    structure = np.ones((3,3))
    labeled_regions, nfeatures = label(Z, structure=structure)

    # Assigne each point of X to a region
    region_assignment = []
    for i, point in enumerate(X):
        ix = np.argmin((xx[0] - point[0])**2)
        iy = np.argmin((yy[:,0] - point[1])**2)
        region_id = labeled_regions[iy, ix]
        region_assignment.append(region_id if region_id > 0 else 'no-reactivity')

    df['Region'] = region_assignment

    conn = sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db')
    cursor = conn.cursor()

    # Add the region to the database
    for i, row in df.iterrows():
        smiles = row['smiles']
        solvent = row['solvent']
        atom = row['atom_analysed']
        table = row['source']
        if table != 'reactive':
            continue

        cursor.execute(f'''
            UPDATE {table}
            SET region = '{row['Region']}'
            WHERE smiles = '{smiles}' AND solvent = '{solvent}' AND atom_analysed = '{atom}'
            '''
        )

    conn.commit()
    conn.close()

