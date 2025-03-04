#!/usr/bin/python3
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from castor_functions import *

# Connect to the database
conn = sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db')
cursor = conn.cursor()

query = f'SELECT experimental_N FROM main'

cursor.execute(query)
data = cursor.fetchall()

fig = plt.figure()

# Create a histogram
plt.hist(np.ravel(data), bins=45, edgecolor='blue', range=(np.min(data), np.max(data)))
plt.title('Histogram of experimental_N')
plt.xlabel('experimental_N')
plt.ylabel('Frequency')

plt.show()

