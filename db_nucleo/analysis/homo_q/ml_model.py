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
#   functions
def create_pysr_model():
    """
    This function returns the PySRRegressor model with complex equations.
    """
    # Operations allowed (same for all predictions)
    binaryOp  = ["plus", "mult", "-", "/", "pow"]
    unitaryOp = ["square", "inv(x)=1/x", "exp", "log", "sqrt", "abs"]
    # Let the values for the regressor
    default_pysr_params = dict(
        populations=70,
        model_selection='best',
    )
    return PySRRegressor(
        niterations=300,
        maxdepth=9,
        binary_operators=binaryOp,
        unary_operators=unitaryOp,
        select_k_features=len(features), # All features
        extra_sympy_mappings={"inv": lambda x: 1/x},
        **default_pysr_params
    )

#-----------------------------------------------------------------------

db_file_path = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

key = ['smiles', 'solvent', 'atom_analysed', 'experimental_N', 'experimental_Sn']
cursor.execute(f'''
    SELECT {', '.join(key)}
    FROM parameters WHERE table_name = 'reactive'
    AND (comment IS NULL OR comment != 'exclude')
''')
#    AND family = 'aliphatic_amines'
#    AND family != 'pyridines_quinolines_etc'
#    AND family != 'azoles_and_azole_anions'
params = cursor.fetchall()

smiles_list, solvents, atoms, n_exp, sn_exp = zip(*params)
nsn = np.array(n_exp)*np.array(sn_exp)

# Be sure of the order, we run in a loop to get the data
features = ['q_qtaim', 'HOMO', 'region']

q_qtaim, elep, electrofuge = [], [], []
eta, nucleofuge, populations = [], [], []
p, homo = [], []
valid_idx = []

for i, (smiles, solvent, atom) in enumerate(zip(smiles_list, solvents, atoms)):
    cursor.execute(f'''
        SELECT {', '.join(features)}
        FROM reactive
        WHERE smiles = '{smiles}' AND solvent = '{solvent}' AND atom_analysed = {atom}
    ''')
    data = cursor.fetchone()
    q_qtaim.append(data[0])
    homo.append(data[1])
    if data[-1] in ['2']:
        valid_idx.append(i)

conn.close()

if len(q_qtaim) < 2:
    quit

q_qtaim = np.array(q_qtaim)[valid_idx]
homo = np.array(homo)[valid_idx]
n_exp = np.array(n_exp)[valid_idx]
sn_exp = np.array(sn_exp)[valid_idx]

#-----------------------------------------------------------------------
#   Create the models for all predictions
# X = np.array([q_qtaim, elep, electrofuge, eta,
#               nucleofuge, populations, p, homo, elep_per_pop]).T
X = np.array([q_qtaim, homo]).T

model = create_pysr_model()
model.fit(X, sn_exp)

# with open('modelNexp.pkl', 'wb') as f:
#     pickle.dump(model, f)

#-----------------------------------------------------------------------
# Best models
pred = model.predict(X)
mae = np.mean(np.abs(n_exp - pred))
print('Best model:\n')
print(model.sympy())
print(f'MAE: {mae}')

print('Top models:\n')
for i, eq in enumerate(model.equations_):
    print(i, model.sympy(i))

print('fetures used')
print(features)
