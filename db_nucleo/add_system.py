#!/usr/bin/python3
import sqlite3
import os

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

directory = './plain_text/new/extra'

for filename in os.listdir(directory):
    if filename.endswith('.dat'):
        family = os.path.splitext(filename)[0].replace("_extra", "")
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(';')# smiles and names can contain spaces and commas
                if len(parts) == 6:
                    smiles, solvent, exp_N, exp_Sn, molecule_name, stars = parts
                elif len(parts) == 7:# comment of the N atom
                    smiles, solvent, exp_N, exp_Sn, molecule_name, stars, _ = parts
                else:
                    continue
                cur.execute('''INSERT INTO main (smiles, molecule_name, solvent, family, experimental_N, experimental_Sn, stars)
                               VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (smiles, molecule_name, solvent.replace(" ", ""), family,
                             float(exp_N), float(exp_Sn), int(stars)))

con.commit()
con.close()

