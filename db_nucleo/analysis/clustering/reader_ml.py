#!/opt/homebrew/bin/python3.9
import csv
import pysr
import sympy
import sqlite3
import itertools
import pickle
import numpy as np
from pysr import PySRRegressor
# from matplotlib import pyplot as plt

#-----------------------------------------------------------------------
#   Read the model data
with open('modelNexp.pkl', 'rb') as f:
    model = pickle.load(f)

#-----------------------------------------------------------------------
#   Database connection
db_file_path = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

key = ['smiles', 'solvent', 'atom_analysed', 'experimental_N']
cursor.execute(f'''
    SELECT {', '.join(key)}
    FROM parameters WHERE table_name = 'reactive'
''')
params = cursor.fetchall()

smiles_list, solvents, atoms, n_exp = zip(*params)

features = ['sfplus', 'q_hirshfeld', 'electrostatic_potential']
cursor.execute(f'''
    SELECT {', '.join(features)}
    FROM reactive
''')
data = cursor.fetchall()
conn.close()

# Data for regression
sfplus = np.array([val[0] for val in data])
q_hirshfeld = np.array([val[1] for val in data])
electrostatic_potential = np.array([val[2] for val in data])
X = np.array([[val[0], val[1], val[2]] for val in data])

#-----------------------------------------------------------------------
# Best models
pred = model.predict(X)
mae = np.mean(np.abs(n_exp - pred))
print('Best model:\n')
print(model.sympy())
print(f'MAE: {mae}')

print('Top models:\n')
for i, eq in enumerate(model.equations):
    eq_sympy = model.latex(i)
    print(eq_sympy)

