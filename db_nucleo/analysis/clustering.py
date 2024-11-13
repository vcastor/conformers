#!/usr/bin/python3
import sqlite3
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from itertools import combinations

# Connect to the database and retrieve all necessary data
conn = sqlite3.connect('../nucleo_data.db')
cursor = conn.cursor()

# Fetch all relevant columns
cursor.execute('''SELECT
                    experimental_N, experimental_Sn,
                    mu, eta, softness, hyperhardness, omega, nucleofuge, electrofuge,
                    electrodonating, electroaccepting, fplus, fminus, fzero, f2,
                    sfplus, sfminus, sfzero, s2, muplusfplus, muminusfminus, wfplus, wf2,
                    Sf2, s2f2, electro, nucleo, q_qtaim, q_hirshfeld,
                    electrostatic_potential, condensed_liner_response
                  FROM main
                  WHERE atom_analysed > 0 AND nconformers IS NOT NULL''')
data = cursor.fetchall()
conn.close()

# Define column names
cols = [
    'experimental_N', 'experimental_Sn', 'mu', 'eta', 'softness', 'hyperhardness',
    'omega', 'nucleofuge', 'electrofuge', 'electrodonating', 'electroaccepting',
    'fplus', 'fminus', 'fzero', 'f2', 'sfplus', 'sfminus', 'sfzero', 's2',
    'muplusfplus', 'muminusfminus', 'wfplus', 'wf2', 'Sf2', 's2f2',
    'electro', 'nucleo', 'q_qtaim', 'q_hirshfeld',
    'electrostatic_potential', 'condensed_liner_response'
]

# Organize data into a DataFrame
df = pd.DataFrame(data, columns=cols)

# Iterate over all combinations of three descriptors for XYZ axes
for x, y, z in combinations(cols[2:], 3):  # Exclude 'experimental_N' and 'experimental_Sn' from XYZ
    # 3D plot colored by experimental_Sn
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(df[x], df[y], df[z], c=df['experimental_Sn'], cmap='viridis', alpha=0.7)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_zlabel(z)
    ax.set_title(f'{x} vs {y} vs {z} (colored by Sn)')
    cbar = plt.colorbar(sc, ax=ax, pad=0.1)
    cbar.set_label('Experimental Sn')
    plt.show()

    # 3D plot colored by experimental_N
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(df[x], df[y], df[z], c=df['experimental_N'], cmap='plasma', alpha=0.7)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_zlabel(z)
    ax.set_title(f'{x} vs {y} vs {z} (colored by N)')
    cbar = plt.colorbar(sc, ax=ax, pad=0.1)
    cbar.set_label('Experimental N')
    plt.show()

