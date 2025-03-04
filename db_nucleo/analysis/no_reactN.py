#!/usr/bin/python3
import sqlite3
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from itertools import combinations

# Connect to the database and retrieve all necessary data
conn = sqlite3.connect('../nucleo_data.db')
cursor = conn.cursor()

# Fetch data from the main table
cursor.execute('''SELECT
                    experimental_N, experimental_Sn,
                    mu, eta, softness, hyperhardness, omega, nucleofuge, electrofuge,
                    electrodonating, electroaccepting, fplus, fminus, fzero, f2,
                    sfplus, sfminus, sfzero, s2, muplusfplus, muminusfminus, wfplus, wf2,
                    Sf2, s2f2, electro, nucleo, q_qtaim, q_hirshfeld
                  FROM main
                  WHERE atom_analysed > 0 AND nconformers IS NOT NULL''')
data_main = cursor.fetchall()

# Fetch data from no_reactive_N table
cursor.execute('''SELECT
                    mu, eta, softness, hyperhardness, omega, nucleofuge, electrofuge,
                    electrodonating, electroaccepting, fplus, fminus, fzero, f2,
                    sfplus, sfminus, sfzero, s2, muplusfplus, muminusfminus, wfplus, wf2,
                    Sf2, s2f2, electro, nucleo, q_qtaim, q_hirshfeld
                  FROM non_reactive_N
                  WHERE atom_analysed > 0 AND nconformers IS NOT NULL AND atom_analysed IS NOT NULL''')
data_no_reactive = cursor.fetchall()
conn.close()

# Define column names
cols_main = [
    'experimental_N', 'experimental_Sn', 'mu', 'eta', 'softness', 'hyperhardness',
    'omega', 'nucleofuge', 'electrofuge', 'electrodonating', 'electroaccepting',
    'fplus', 'fminus', 'fzero', 'f2', 'sfplus', 'sfminus', 'sfzero', 's2',
    'muplusfplus', 'muminusfminus', 'wfplus', 'wf2', 'Sf2', 's2f2',
    'electro', 'nucleo', 'q_qtaim', 'q_hirshfeld'
]
cols_no_reactive = cols_main[2:]  # No 'experimental_N' and 'experimental_Sn'

# Organize data into DataFrames and clean null values
df_main = pd.DataFrame(data_main, columns=cols_main).dropna()
df_no_reactive = pd.DataFrame(data_no_reactive, columns=cols_no_reactive).dropna()

# Iterate over all combinations of three descriptors for XYZ axes
for x, y, z in combinations(cols_main[2:], 3):  # Exclude 'experimental_N' and 'experimental_Sn' from XYZ
    # 3D plot colored by experimental_Sn
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(df_main[x], df_main[y], df_main[z], c=df_main['experimental_Sn'], cmap='viridis', alpha=0.7)
    ax.scatter(df_no_reactive[x], df_no_reactive[y], df_no_reactive[z], c='black', alpha=0.5, label='no_reactive_N')
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_zlabel(z)
    ax.set_title(f'{x} vs {y} vs {z} (colored by Sn)')
    cbar = plt.colorbar(sc, ax=ax, pad=0.1)
    cbar.set_label('Experimental Sn')
    ax.legend()
    plt.show()

    # 3D plot colored by experimental_N
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(df_main[x], df_main[y], df_main[z], c=df_main['experimental_N'], cmap='plasma', alpha=0.7)
    ax.scatter(df_no_reactive[x], df_no_reactive[y], df_no_reactive[z], c='black', alpha=0.5, label='no_reactive_N')
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_zlabel(z)
    ax.set_title(f'{x} vs {y} vs {z} (colored by N)')
    cbar = plt.colorbar(sc, ax=ax, pad=0.1)
    cbar.set_label('Experimental N')
    ax.legend()
    plt.show()

