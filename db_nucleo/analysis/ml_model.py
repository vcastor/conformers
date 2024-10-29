#!/opt/homebrew/bin/python3.9
# -*- coding: UTF-8 -*-
########################################################################
#   This python script was written con el poder de las plantitas 🌱    #
#                                                                      #
#                                       ✨ Victoria Castor, 2023 ✨    #
########################################################################
import csv
import pysr
import sympy
import sqlite3
import itertools
import numpy as np
from pysr import PySRRegressor
from matplotlib import pyplot as plt

#-----------------------------------------------------------------------
#   functions
def get_mae_values(interaction_type):
    print(f'{interaction_type}')
    mae1 = int(input('Extra equation 1: '))
    mae2 = int(input('Extra equation 2: '))

    mae1 = 1 if mae1 < 0 else mae1
    mae2 = 2 if mae2 < 0 else mae2

    return mae1, mae2

def create_pysr_model():
    """
    This function returns the PySRRegressor model with complex equations.
    """
    # Operations allowed (same for all predictions)
    binaryOp  = ["plus", "mult", "-", "/", "pow"]
    unitaryOp = ["square", "inv(x)=1/x", "exp", "log", "sqrt", "sin", "cos", "tan", "abs"]#, "asin", "acos", "atan", "sinh", "cosh", "tanh"]
    # unitaryOp = ["square", "inv(x)=1/x", "exp", "log", "sqrt", "sin", "cos", "tan", "abs", "asin", "acos", "atan", "sinh", "cosh", "tanh"]
    # unitaryOp = ["square", "inv(x)=1/x", "exp", "log", "sqrt", "abs", "cube", "sinh", "cosh", "tanh"]
    # unitaryOp = ["square", "exp", "log", "asin", "acos", "atan"]#, "sin", "cos", "tan"]
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
        extra_sympy_mappings={"inv": lambda x: 1/x},
        **default_pysr_params
    )

def print_other_model_equations(model, description, num_equations=4):
    print(description)
    for i in range(1, num_equations + 1):
        print(i, model.sympy(i))
    print()

def print_and_return_mae(model, X, y, mae_indices, interaction_type):
    """
    It returns the y predictions, and also print the difference between
    the data and the prediction.
    """
    print(f'{interaction_type}\n')
    y_predict0 = model.predict(X)
    print("Best model:", np.absolute(y_predict0 - y).mean())

    y_predict1, y_predict2 = None, None

    if len(mae_indices) > 0 and mae_indices[0] > 0:
        y_predict1 = model.predict(X, mae_indices[0])
        print(f"Manual selection MAE for index {mae_indices[0]}:", np.absolute(y_predict1 - y).mean())

    if len(mae_indices) > 1 and mae_indices[1] > 0:
        y_predict2 = model.predict(X, mae_indices[1])
        print(f"Manual selection MAE for index {mae_indices[1]}:", np.absolute(y_predict2 - y).mean())

    return y_predict0, y_predict1, y_predict2

#-----------------------------------------------------------------------
#   the data
db_file_path = '../nucleo_data.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute('''SELECT DISTINCT family FROM main WHERE atom_analysed > 0 AND nconformers not null''')
families = cursor.fetchall()
cursor.execute('''SELECT 
                    experimental_N, experimental_Sn,
                    mu, eta, softness, hyperhardness, omega, nucleofuge, electrofuge, electrodonating, electroaccepting,
                    fplus, fminus, fzero, f2, sfplus, sfminus, sfzero, s2,
                    muplusfplus, muminusfminus, wfplus, wf2, Sf2, s2f2, electro, nucleo,
                    q_qtaim, q_hirshfeld
                  FROM main WHERE atom_analysed > 0 AND nconformers not null''')
rawdata = cursor.fetchall()
# Commit the changes and close the connection
conn.commit()
conn.close()

# Converte families to a list
families = [f[0] for f in families]

# Split
data_f = {}
for family in families:
    data_f[family] = [row for row in rawdata if row[0] == family]

#
# Not compleated data?
filtered_data = [val for val in data if None not in val]
# Data for regression
n_exp = np.array([val[0] for val in filtered_data])
sn_exp = np.array([val[1] for val in filtered_data])

#-----------------------------------------------------------------------
#   Create the models for all predictions
X = np.array([[val[2], val[3], val[4], val[5], val[6], val[7], val[8],
               val[9], val[10], val[11], val[12], val[13], val[14],
               val[15], val[16], val[17], val[18], val[19], val[20],
               val[21], val[22], val[23], val[24], val[25], val[26],
               val[27], val[28]] for val in filtered_data])
model = create_pysr_model()

# She run, run, run [Radiohead - Creep]
# model.fit(X, missing)
model.fit(X, n_exp)

#-----------------------------------------------------------------------
# Best models
print('Best model:\n')
print(model.sympy())

pred = model.predict(X)
mae = np.absolute(pred - n_exp).mean()
print(f'MAE: {mae}\n')


