#!/usr/bin/python3
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from itertools import combinations, product

# Connect to the database
conn = sqlite3.connect('../nucleo_data.db')
cursor = conn.cursor()

# Properties to fetch
exp = ['experimental_N', 'experimental_Sn']
cols = [
    'mu', 'eta', 'softness', 'hyperhardness',
    'omega', 'nucleofuge', 'electrofuge', 'electrodonating', 'electroaccepting',
    'fplus', 'fminus', 'fzero', 'f2', 'sfplus', 'sfminus', 'sfzero', 's2',
    'muplusfplus', 'muminusfminus', 'wfplus', 'wf2', 'Sf2', 's2f2',
    'electro', 'nucleo', 'q_qtaim', 'q_hirshfeld',
    'electrostatic_potential', 'condensed_liner_response',
    'epsilon', 'rad'
]

# Fetch data
queryReact = f'''SELECT {", ".join(exp)}, {", ".join(cols)} FROM main
                WHERE nconformers IS NOT NULL AND comment NOT LIKE "%&%" OR comment LIKE "%[&]%"'''
queryNoReac = f'SELECT {", ".join(cols)} FROM non_reactive_N'
queryPeculiar = f'''SELECT {", ".join(exp)}, {", ".join(cols)} FROM main
                    WHERE nconformers LIKE "%&%" AND comment NOT LIKE "%[&]%"'''

cursor.execute(queryReact)
reactive_data = cursor.fetchall()

cursor.execute(queryNoReac)
non_reactive_data = cursor.fetchall()

cursor.execute(queryPeculiar)
peculiar_data = cursor.fetchall()

conn.close()

# Organize data into DataFrames
reactive_df = pd.DataFrame(reactive_data, columns=exp+cols)
peculiar_df = pd.DataFrame(peculiar_data, columns=exp+cols)
noreactive_df = pd.DataFrame(non_reactive_data, columns=cols)

# For non-reactive, experimental values = 0
for col in exp:
    noreactive_df[col] = 0

df = pd.concat([reactive_df, noreactive_df], ignore_index=True)
df['no_reactive_N'] = (df['experimental_N'] == 0) & (df['experimental_Sn'] == 0)

# Calculate the quantiles
q1 = df['experimental_N'].quantile(0.25)
q2 = df['experimental_N'].quantile(0.75)

# Categorize into 'bad', 'good', and 'very good'
df['category'] = pd.cut(df['experimental_N'],
                        bins = [-float('inf'), q1, q2, float('inf')],
                        labels = ['Bad Nucleophile', 'Good Nucleophile', 'Very Good Nucleophile'])

# Define sets of atomic and molecular descriptors (adjust as needed)
atomic_descriptors = ['mu', 'q_qtaim', 'fminus', 'fplus', 'rad']
molecular_descriptors = ['condensed_liner_response', 'electrostatic_potential', 'omega', 'eta', 'epsilon']

# Create all combinations: 2 atomic, 1 molecular
atomic_combos = combinations(atomic_descriptors, 2)  # two atomic features
molecular_combos = molecular_descriptors  # single molecular feature

combinations_to_plot = []
for (a1, a2) in atomic_combos:
    for m in molecular_combos:
        combinations_to_plot.append((a1, a2, m))

# Colors for categories
color_map = {
    'Bad Nucleophile': 'r',
    'Good Nucleophile': 'g',
    'Very Good Nucleophile': 'b',
    'Peculiar': 'y',
    'No Reactive Nitrogen': 'k'
}

# Fixed axes: X=fminus, Y=electrostatic_potential
x_feature = 'fminus'
y_feature = 'electrostatic_potential'

# Z-axis candidates: all features except the fixed ones
z_candidates = [col for col in cols if col not in {x_feature, y_feature}]

# Plot each combination with the third axis as Z
for z_feature in z_candidates:
    if z_feature not in df.columns:
        continue

    x = df[x_feature].fillna(0)
    y = df[y_feature].fillna(0)
    z = df[z_feature].fillna(0)
    categories = df['category']

    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Plot each category with a different color
    for cat in categories.unique():
        cat_mask = (categories == cat)
        ax.scatter(x[cat_mask], y[cat_mask], z[cat_mask], c=color_map[cat], label=cat, alpha=0.7)

    ax.set_xlabel(x_feature)
    ax.set_ylabel(y_feature)
    ax.set_zlabel(z_feature)
    ax.set_title(f'3D plot: {x_feature} vs {y_feature} vs {z_feature}')
    ax.legend()

    plt.tight_layout()
    plt.show()
quit()

# Plot each combination
for (feat_x, feat_y, feat_z) in combinations_to_plot:
    # Check that these features exist in df
    if feat_x not in df.columns or feat_y not in df.columns or feat_z not in df.columns:
        continue

    x = df[feat_x].fillna(0)
    y = df[feat_y].fillna(0)
    z = df[feat_z].fillna(0)
    categories = df['category']

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')

    # Plot each category with a different color
    for cat in categories.unique():
        cat_mask = (categories == cat)
        ax.scatter(x[cat_mask], y[cat_mask], z[cat_mask], c=color_map[cat], label=cat, alpha=0.7)

    ax.set_xlabel(feat_x)
    ax.set_ylabel(feat_y)
    ax.set_zlabel(feat_z)
    ax.set_title(f'3D plot: {feat_x} vs {feat_y} vs {feat_z}')
    ax.legend()

    plt.tight_layout()
    plt.show()
    # If you have many plots, consider saving:
    # plt.savefig(f'3Dplot_{feat_x}_{feat_y}_{feat_z}.png', dpi=150)
    # plt.close()

