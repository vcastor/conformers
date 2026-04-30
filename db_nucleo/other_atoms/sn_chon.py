#!/usr/bin/python3
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# # Plot histogram of sN values by atom, using CSV file
# csv_data = pd.read_csv('all_data.csv')
# plt.figure(figsize=(10, 6))
# sns.histplot(data=csv_data, x='sN', hue='Atom', bins=40, kde=True, element='step', stat='count')
# plt.title('Distribution of sN values by Atom')
# plt.xlabel('sN value')
# plt.ylabel('Count')
# plt.tight_layout()
# plt.show()

# Plot histogram of N values by atom, using CSV file
csv_data = pd.read_csv('all_data.csv')
plt.figure(figsize=(10, 6))
sns.histplot(data=csv_data, x='N', hue='Atom', bins=40, kde=True, element='step', stat='count')
plt.title('Distribution of N values by Atom', fontsize=18)
plt.xlabel('N value', fontsize=16)
plt.ylabel('Count', fontsize=16)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.tight_layout()
plt.savefig('atom_N_distribution.pdf')

