#!/usr/bin/python3
import os
import sqlite3

# function to read the global information of the system
def global_reader(file):
    with open(file) as f:
        data = f.readlines()
    smiles, solvents, ncoformers, homo = [], [], [], []
    record, read = False, False
    for line in data:
        if '===' in line:
            smiles.append(line.split()[1])
            gd = {}
        elif '***' in line:
            solvents.append(line.split()[1])
        elif 'number_conformers' in line:
            ncoformers.append(int(line.split()[1]))
        elif '---' in line and (line.split()[1] == 'Average' or (ncoformers[-1] == 1 and line.split()[1] == 'Conformer')):
            record = True
        elif 'Orbital Energies' in line and record:
            read = True
            homo1 = float(line.split()[-1])
        elif read:
            try:
                homo.append(float(line.split()[-1]))
            except ValueError:
                homo.append(homo1)
            record, read = False, False
    return smiles, solvents, ncoformers, homo

# Main script starts here 🚀

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

outdir = 'outputs'

# loop to read all the files in the directory
for file in os.listdir(outdir):
    if file.endswith('.out'):
        smiles, solvents, ncoformers, homo = global_reader(os.path.join(outdir, file))

        for i in range(len(smiles)):
            cur.execute('SELECT table_name FROM parameters WHERE smiles = ? AND solvent = ?', (smiles[i], solvents[i]))
            tables = cur.fetchall()
            for (table,) in set(tables):
                cur.execute(f'''UPDATE {table} SET
                                HOMO = ?
                                WHERE smiles = ? AND solvent = ?''', (homo[i], smiles[i], solvents[i]))

con.commit()
con.close()

