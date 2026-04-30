#!/usr/bin/python3
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

csv_data = pd.read_csv('all_data.csv')

# Stadistics for N values
n_stad = csv_data.groupby('Atom')['N'].describe().reset_index()
# Print the statistics for N values
print("Statistics for N values:")
print(n_stad)

# plt.figure(figsize=(10, 6))
# sns.histplot(data=csv_data, x='sN', hue='Atom', bins=40, kde=True, element='step', stat='count')
# plt.title('Distribution of sN values by Atom')
# plt.xlabel('sN value')
# plt.ylabel('Count')
# plt.tight_layout()
# plt.show()
