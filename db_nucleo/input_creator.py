#!/usr/bin/python3
import os
import sqlite3

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

directory = './plain_text/new/extra'

for filename in os.listdir(directory):
    if filename.endswith('.dat'):
        family = os.path.splitext(filename)[0].replace("_extra", "")
        # cur.execute(f"SELECT smiles, solvent FROM main WHERE family = '{family}'")
        cur.execute(f"SELECT smiles, solvent FROM main WHERE family='{family}' AND atom_analysed IS NULL")
        rows = cur.fetchall()
        with open(f'{family}_extra.csv', 'w') as f:
            f.write(f"# molecule, solvent\n")
            for row in rows:
                f.write(f"{row[0]}, {row[1]}\n")
            f.write("Energy threshold Optimize, 5.0\n")
            f.write("RMSD opt, 3.0\n")
            f.write("Energy threshold Score, 2.5\n")
            f.write("RMSD score, 1.5\n")
            f.write("Functional, PBE\n")
            f.write("Basis set, TZP\n")
            f.write("dispersion, GRIMME3 BJDAMP\n")
            f.write("model, GFN1-xTB\n")
            f.write("Temperature, 298\n")
            f.write("Number of conformers, 20\n\n")

conn.close()

