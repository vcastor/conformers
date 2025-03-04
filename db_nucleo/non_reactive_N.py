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
                parts = line.split(';')# smiles and names can contain spaces and commas
                if len(parts) == 7:# comment of the N atom
                    smiles, solvent, exp_N, exp_Sn, molecule_name, stars, comment = parts
                else:
                    continue
                cur.execute('''UPDATE main SET
                                comment = ? WHERE smiles = ? AND experimental_N = ? AND experimental_Sn = ?''',
                            (comment.replace(" ", ""), smiles, float(exp_N), float(exp_Sn)))

con.commit()
con.close()

