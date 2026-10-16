#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

with sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/plamsfilter/database_entropies/entropiesCOSMO.db') as conn:
    data = pd.read_sql('SELECT trans_S, rot_S, vib_S, experimental_S FROM PBE0', conn)

data.dropna(inplace=True)

S_sum = data['rot_S'] + data['trans_S'] + data['vib_S']
S_exp = data['experimental_S']

plt.figure(figsize=(8, 6))
plt.scatter(S_exp, S_sum, alpha=0.5)
plt.plot([S_exp.min(), S_exp.max()], [S_exp.min(), S_exp.max()], 'k--', lw=2)
plt.xlabel('Experimental Entropy')
plt.ylabel('$S_r + S_t + S_v$')
plt.title('Sum of Entropy Components vs Experimental')
plt.grid(True)
plt.show()
