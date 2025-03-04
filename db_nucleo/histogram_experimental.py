#!/usr/bin/python3
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect('nucleo_data.db')
query = "SELECT experimental_N, experimental_Sn FROM main"

# Load data into a DataFrame
df=pd.read_sql_query(query, conn)

# Plot the histogram
sns.histplot(data=df,x='experimental_N',y='experimental_Sn',bins=30)
plt.show()

# Plot for experimental_N
sns.histplot(data=df, x='experimental_N', bins=30)
plt.title('Histogram of experimental_N')
plt.show()

# Plot for experimental_Sn
sns.histplot(data=df, x='experimental_Sn', bins=30)
plt.title('Histogram of experimental_Sn')
plt.show()

