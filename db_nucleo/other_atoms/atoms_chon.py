#!/usr/bin/python3
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

urls = {
    'C': 'https://www.cup.lmu.de/oc/mayr/reaktionsdatenbank2/fe/showclass/10?num=10000&page=1',
    'H': 'https://www.cup.lmu.de/oc/mayr/reaktionsdatenbank2/fe/showclass/34?num=10000&page=1',
    'O': 'https://www.cup.lmu.de/oc/mayr/reaktionsdatenbank2/fe/showclass/50?num=10000&page=1',
    'N': 'https://www.cup.lmu.de/oc/mayr/reaktionsdatenbank2/fe/showclass/40?num=10000&page=1'
}

def get_from_url(url, atom):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize lists to store data
    n_values, sn_values = [], []

    count = 0
    for tag in soup.find_all(string=True):
        text = tag.strip()
        if 'Param.' in text:
            match = text.split(':')[1]
            if count % 2 == 0:
                n_values.append(float(match))
            else:
                sn_values.append(float(match))
            count += 1

    # Create DataFrame and save
    data = pd.DataFrame({
        'N': n_values,
        'sN': sn_values
    })
    data['Atom'] = atom
    return data

# Concatenate all data
all_data = pd.concat([get_from_url(url, atom) for atom, url in urls.items()], ignore_index=True)
all_data.to_csv('all_data.csv', index=False)

# Plot using seaborn
plt.figure(figsize=(10, 6))
sns.histplot(data=all_data, x='N', hue='Atom', bins=50, kde=True, element='step', stat='count')
plt.title(r'Distribution of $N_{Mayr}$ values by Atom', fontsize=18)
plt.xlabel(r'$N_{Mayr}$ value', fontsize=16)
plt.ylabel('Count', fontsize=16)
plt.tick_params(axis='both',labelsize=14)
plt.tight_layout()
plt.show()

# Dividing by charge of the atom
charge = {'C': 6, 'H': 1, 'O': 8, 'N': 7}

all_data['N/charge'] = all_data['N']/all_data['Atom'].map(charge)
plt.figure(figsize=(10, 6))
sns.histplot(data=all_data, x='N/charge', hue='Atom', bins=50, kde=True, element='step', stat='count')
plt.title('Distribution of N values by Atom and Charge')
plt.xlabel('N value/Charge')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()

