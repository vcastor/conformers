# -*- coding: UTF-8 -*-
#!/opt/homebrew/bin/python3.9
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
    This function returns the PySRRegressor model.
    """
    # Operations allowed (same for all predictions)
    binaryOp  = ["plus", "mult", "-", "/"]
    unitaryOp = ["square" , "inv(x) = 1/x", "exp", "log"]
    # Let the values for the regressor
    default_pysr_params = dict(
        populations = 30,
        model_selection = 'best',
    )
    return PySRRegressor(
        niterations=100,
        maxdepth=5,
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

def setup_and_plot(ax, y_predicted, y_data, model, ymin, ymax, plot_label, extra_preds=None, markers=None):
    """
    Just DRY for readability about plots.
    """
    # Plot's limit
    data_range = ymax - ymin
    extra_space = data_range * 0.01
    ymin_plot = ymin - extra_space
    ymax_plot = ymax + extra_space
    ax.plot([ymin_plot, ymax_plot], [ymin_plot, ymax_plot], 'k-')

    marker_cycle = itertools.cycle(markers) if markers else itertools.cycle(['o'])

    # Scatter plot for the best prediction
    ax.scatter(y_predicted, y_data, label=f"Best: ${model.latex(0)}$", marker=next(marker_cycle), facecolor="None", edgecolor="darkcyan")

    # Extra predictions [Optional]
    if extra_preds:
        #for value, label, colour in extra_preds:
        for value, colour in extra_preds:
            if value > 0:
                ax.scatter(y_predicted, y_data, label=f"Alternative: ${model.latex(value)}$", marker=next(marker_cycle), facecolor="None", edgecolor=colour)

    # Labels and legend
    ax.set_xlabel(plot_label[0])
    ax.set_ylabel(plot_label[1])
    ax.legend()

#-----------------------------------------------------------------------
#   the data
db_file_path = '../entropiesCOSMO.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute('SELECT trans_S, rot_S, vib_S, epsilon, experimental_S FROM molecules')
data = cursor.fetchall()
# Commit the changes and close the connection
conn.commit()
conn.close()

#
# Not compleated data!
filtered_data = [val for val in data if None not in val]

# Data for linear regression
s_exp = np.array([val[4] for val in filtered_data])
X = np.array([[val[0], val[1], val[2]] for val in filtered_data])
# X = np.array([[val[0], val[1], val[2], val[3]] for val in filtered_data])
# strans, srot, svib, eps = X[:,0], X[:,1], X[:,2], X[:,3] # Editable variables


#new transformation
# yexp = s_exp/(np.exp(-eps))

#-----------------------------------------------------------------------
#   Create the models for all predictions
model = create_pysr_model()

# She run, run, run [Radiohead - Creep]
model.fit(X, s_exp)

#-----------------------------------------------------------------------
# Best models
print('Best model:\n')
print(model.sympy())
quit()

# Other models
print('Other models:\n')
print_other_model_equations(model_cou, 'Coulomb interaction')
print_other_model_equations(model_xc, 'Exchange-Correlation interaction')
print_other_model_equations(model_th, 'Kinetic Energy (Hydrogen)')

#-----------------------------------------------------------------------
#   Ask to the user which other equations are wanted for the plots
print('Select another two equations for the plot,\nif you don\'t want them just type zeros \
       or negative values to use the second and 3rd better options')
mae_cou1, mae_cou2 = get_mae_values('Coulomb interaction')
mae_xc1, mae_xc2 = get_mae_values('Exchange-Correlation interaction')
mae_th1, mae_th2 = get_mae_values('Kinetic Energy (Hydrogen)')

#-----------------------------------------------------------------------
#   Printing values predicted
print('Difference between prediction(s) and data\n')
yp0_cou, yp1_cou, yp2_cou = print_and_return_mae(model_cou, X, ycou, [mae_cou1, mae_cou2], 'Coulomb Interaction')
yp0_xc, yp1_xc, yp2_xc = print_and_return_mae(model_xc, X, yxc, [mae_xc1, mae_xc2], 'Exchange-Correlation Interaction')
yp0_th, yp1_th, yp2_th = print_and_return_mae(model_th, X, yth, [mae_th1, mae_th2], 'Kinetic Energy (Hydrogen)')

#-----------------------------------------------------------------------
#   Plots
fig_cou, ax_cou = plt.subplots()
fig_xc, ax_xc = plt.subplots()
fig_th, ax_th = plt.subplots()
# Plot's limit and markers
ycoumin, ycoumax = np.amin(ycou), np.amax(ycou)
yxcmin, yxcmax = np.amin(yxc), np.amax(yxc)
ythmin, ythmax = np.amin(yth), np.amax(yth)
markers = ['^', 'v']
# Call for the plots
setup_and_plot(ax_cou, yp0_cou, ycou, model_cou, ycoumin, ycoumax,
               ["Predicted $E^{int}_{Coul}$", "Reference $E^{int}_{Coul}$"], 
               [(mae_cou1, "orange"), (mae_cou2, "darkmagenta")], markers=markers)
setup_and_plot(ax_xc, yp0_xc, yxc, model_xc, yxcmin, yxcmax,
               ["Predicted $E^{int}_{XC}$", "Reference $E^{int}_{XC}$"], 
               [(mae_xc1, "orange"), (mae_xc2, "darkmagenta")], markers=markers)
setup_and_plot(ax_th, yp0_th, yth, model_th, ythmin, ythmax,
               ["Predicted $T^H$", "Reference $T^H$"], 
               [(mae_th1, "orange"), (mae_th2, "darkmagenta")], markers=markers)

plt.figure(fig_cou.number)
plt.figure(fig_xc.number)
plt.figure(fig_th.number)
plt.show()

