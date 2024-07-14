#!/usr/bin/python3
import os
import sqlite3
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'entropiesCOSMO.db'

# plain text file path
plaintxt = '/Users/vcastor/Downloads/EntropiesNIST_final.txt'

# Connect to SQLite database 
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Retrieve all molecule names from the database
cursor.execute('SELECT smile, molecule_name FROM pbe0')
rows = cursor.fetchall()
smiles_db = {row[0] for row in rows}
names_db = {row[1] for row in rows}
conn.close()

with open(plaintxt, 'r') as file:
    lines = file.readlines()[1:]

new_molecules = []
for line in lines:
    smile, name = line.split()[2], line.split()[1]
    if smile not in smiles_db:
        new_molecules.append((smile, name))

for smile, name in new_molecules:
    filename = f'pbe0/input_files/{name}.csv'
    with open(filename, 'w') as f:
        # Smile, solvent
        f.write(f'{smile}, {name}\n')
        # Parameters
        # Filter
        f.write('Energy threshold Optimize, 5.0\n')
        f.write('Energy threshold Score, 2.5\n')
        f.write('RMSD opt, 3.0\n')
        f.write('RMSD score, 1.5\n')
        # DFT and DFTB
        f.write('Functional, PBE0\n')
        f.write('Basis set, TZP\n')
        f.write('dispersion, GRIMME3 BJDAMP\n')
        f.write('model, GFN1-xTB\n')
        # Additional parameters
        f.write('Temperature, 298.15\n')
        f.write('Number of conformers, 20\n')

print("✨ Input files created successfully! 🚀✨")

