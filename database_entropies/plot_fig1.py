#!/usr/bin/python3
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data from the database
conn=sqlite3.connect('entropiesCOSMO.db')
df=pd.read_sql_query('SELECT epsilon,experimental_S FROM PBE',conn)

# Plot
fig,ax = plt.subplots(1,2,figsize=(12,6))
nbin = 80
nsystems = len(df)

# sns.kdeplot(df['epsilon'], ax=ax[0], fill=True, color='blue')
sns.histplot(df['epsilon'], ax=ax[0], color='blue', fill=True,
             stat='count', bins=nbin, alpha=0.5)
# ax[0].hist(df['epsilon'], bins=nbin, color='blue', alpha=0.5, histtype='stepfilled')
ax[0].set_xlabel(r'$\varepsilon_r$',fontsize=18)
ax[0].set_ylabel('Frequency',fontsize=18)
ax[0].tick_params(which='major', labelsize=14)

# sns.kdeplot(df['experimental_S'], ax=ax[1], fill=True, color='green')
sns.histplot(df['experimental_S'], ax=ax[1], color='green', fill=True,
             stat='count', bins=nbin, alpha=0.5)
# ax[1].hist(df['experimental_S'], bins=nbin, color='green', alpha = 0.5, histtype='barstacked')
ax[1].set_xlabel(r'Experimental Entropy [$\mathrm{JK^{-1}mol^{-1}}$]',fontsize=18)
ax[1].set_ylabel('Frequency',fontsize=18)
ax[1].tick_params(axis='both', which='major', labelsize=14)

plt.tight_layout()
plt.savefig('fig1.pdf')

