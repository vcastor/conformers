#!/usr/bin/python3
import sqlite3
import os

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

directory = './plain_text/new'

for filename in os.listdir(directory):
    if filename.endswith('.dat'):
        family = os.path.splitext(filename)[0]
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) == 6:
                    smiles, solvent, exp_N, exp_Sn, molecule_name, stars = parts
                elif len(parts) == 7:# comment of the N atom
                    smiles, solvent, exp_N, exp_Sn, molecule_name, stars, _ = parts
                else:
                    continue
                cur.execute('''INSERT INTO main (smiles, molecule_name, solvent, family, experimental_N, experimental_Sn)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (smiles, molecule_name, solvent, family,
                             float(experimental_N), float(experimental_Sn)))

con.commit()
con.close()

