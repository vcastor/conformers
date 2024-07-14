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
    # unitaryOp = ["square", "inv(x)=1/x", "exp", "log", "sqrt", "sin", "cos", "tan", "abs"]#, "asin", "acos", "atan", "sinh", "cosh", "tanh"]
    # unitaryOp = ["square", "inv(x)=1/x", "exp", "log", "sqrt", "sin", "cos", "tan", "abs", "asin", "acos", "atan", "sinh", "cosh", "tanh"]
    unitaryOp = ["square", "inv(x)=1/x", "exp", "log", "sqrt", "abs", "cube", "sinh", "cosh", "tanh"]
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
    """
    Just DRY for readability.
    """
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
db_file_path = '../entropiesCOSMO.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute('SELECT trans_S, rot_S, vib_S, mu, eta, gamma, epsilon, experimental_S FROM molecules')
data = cursor.fetchall()
# Commit the changes and close the connection
conn.commit()
conn.close()

#
# Not compleated data!
filtered_data = [val for val in data if None not in val]

# Data for linear regression
s_exp = np.array([val[7] for val in filtered_data])

# Best model for entropy without CDFT
# 12.7529 | S = e^(-λ*ε)[α*S_r + β*S_t + S_vr/S_gas + γ*S_vt/S_gas] + S_v
#         | λ: 0.0022
#         | α: 0.4632, β: 0.5902, γ: 0.2493
eps = np.array([val[6] for val in filtered_data])
srot = np.array([val[0] for val in filtered_data])
strans = np.array([val[1] for val in filtered_data])
svib = np.array([val[2] for val in filtered_data])
gas = srot + strans + svib
s_vr = svib*srot/gas
s_vt = svib*strans/gas
pred = np.exp(-0.0022*eps)*(0.4632*srot + 0.5902*strans + s_vr + 0.2493*s_vt) + svib

# X = np.array([[val[3], val[4], val[5], val[6]] for val in filtered_data])
# missing = s_exp - pred

# X = np.array([[val[0], val[1], val[2]] for val in filtered_data])
# strans, srot, svib, eps = X[:,0], X[:,1], X[:,2], X[:,3] # Editable variables

X = np.array([[val[0], val[1], val[2], val[3], val[4], val[5], val[6]] for val in filtered_data])

#-----------------------------------------------------------------------
#   Create the models for all predictions
model = create_pysr_model()

# She run, run, run [Radiohead - Creep]
# model.fit(X, missing)
model.fit(X, s_exp)

#-----------------------------------------------------------------------
# Best models
print('Best model:\n')
print(model.sympy())
quit()






