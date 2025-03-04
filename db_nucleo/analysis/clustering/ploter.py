#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from castor_functions import *

# Properties to fetch
exp  = ['experimental_N', 'experimental_Sn']
cols = [
    'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
    'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
    'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
    'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
    'condensed_liner_response'
]

df = connect_db(exp, cols)

df = reactivity_classifier(df, 'experimental_N', 2)

# ==============================
# Plotting Features: ('softness', 's2', 'electrostatic_potential')

# Colours for categories
color_map = {
    0: 'r',
    1: 'k'
}
labels = {
    0: 'Non-reactive',
    1: 'Reactive'
}

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for category, colour in color_map.items():
    mask = df['category'] == category
    ax.scatter(
        df.loc[mask, 'softness'],
        df.loc[mask, 's2'],
        df.loc[mask, 'electrostatic_potential'],
        c=colour,
        label=labels[category]
    )

ax.set_xlabel('softness')
ax.set_ylabel('s2')
ax.set_zlabel('electrostatic_potential')
ax.legend()
plt.show()

