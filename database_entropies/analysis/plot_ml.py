#!/usr/bin/python3 
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

#-----------------------------------------------------------------------
#   the data
db_file_path = '../entropiesCOSMO.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()
cursor.execute('SELECT trans_S, rot_S, vib_S, epsilon, rad, correctionS, mu, eta, gamma, omega, experimental_S FROM PBE')
data = cursor.fetchall()
# Commit the changes and close the connection
conn.commit()
conn.close()

#
# Not compleated data!
filtered_data = [val for val in data if None not in val]

# Data for linear regression
s_exp = np.array([val[-1] for val in filtered_data])

#-----------------------------------------------------------------------
#   Create the models for all predictions
X = np.array([[val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7], val[8], val[9]] for val in filtered_data])

# The curent best model
# x2**1.0574647 - x3 + 166.88306

pred1 = X[:, 2]**1.0574647 - X[:, 3] + 166.88306

# Second model
# x2 + x5 - tan(0.4191836/x9) + 282.24756 - 386.79474/x4

pred2 = X[:,2] + X[:,5] - np.tan(0.4191836/X[:,9]) + 282.24756 - 386.79474/X[:,4]

plt.figure(figsize=(8,6))

# # First model
# plt.scatter(s_exp, pred1, c='blue', edgecolors='k', alpha=0.7, label=r'$S = S_v^{1.05} - \varepsilon + 166$')
# plt.plot([s_exp.min(), s_exp.max()], [s_exp.min(), s_exp.max()], 'k--')
# plt.text(0.05, 0.95, r'$S = S_v^{1.05} - \varepsilon + 166$'+f'\nMAE = 13.21', transform=plt.gca().transAxes,
#          fontsize=10, verticalalignment='top',
#          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# # Second model
# pred2 = X[:,2] + X[:,5] - np.tan(0.4191836/X[:,9]) + 282.24756 - 386.79474/X[:,4]
# plt.scatter(s_exp, pred2, c='green', edgecolors='k', alpha=0.7, label=r'$S = S_v + \varepsilon - \tan(0.42/\omega) + 282 - 387/\epsilon$')
# plt.text(0.95, 0.05, r'$S = S_v + \varepsilon - \tan(0.42/\omega) + 282 - 387/\epsilon$'+f'\nMAE = 13.21', transform=plt.gca().transAxes,
#          fontsize=10, verticalalignment='bottom', horizontalalignment='right',
#          bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

# plt.xlabel('Experimental S', fontsize=12)
# plt.ylabel('Predicted S', fontsize=12)
# plt.title('Experimental vs Predicted S', fontsize=14)
# plt.grid(True, linestyle='--', alpha=0.5)
# # plt.legend()
# plt.tight_layout()
# plt.show()

# First model
plt.scatter(s_exp, pred1, c='blue', edgecolors='k', alpha=0.7)
plt.plot([s_exp.min(), s_exp.max()], [s_exp.min(), s_exp.max()], 'k--')
plt.text(0.95, 0.05, r'$S = S_v^{1.05} - \varepsilon + 166$'+f'\nMAE = 13.21', transform=plt.gca().transAxes,
         fontsize=10, verticalalignment='bottom', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

# Second model
pred2 = X[:,2] + X[:,5] - np.tan(0.4191836/X[:,9]) + 282.24756 - 386.79474/X[:,4]
plt.scatter(s_exp, pred2, c='green', edgecolors='k', alpha=0.7)
plt.text(0.05, 0.95, r'$S = S_v + \varepsilon - \tan(0.42/\omega) + 282 - 387/\epsilon$'+f'\nMAE = 13.21', transform=plt.gca().transAxes,
         fontsize=10, verticalalignment='top', horizontalalignment='left',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.xlabel('Experimental S', fontsize=12)
plt.ylabel('Predicted S', fontsize=12)
plt.title('Experimental vs Predicted S', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
# plt.show()
plt.savefig('plot_no_physical_interpretation.pdf')




