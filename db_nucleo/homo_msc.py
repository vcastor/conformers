#!/usr/bin/python3
import os
import sqlite3

# function to read the global information of the system
def solvent_reader(file):
    with open(file) as f:
        data = f.readlines()
    smiles, solvents, nconformers = [], [], []
    for line in data:
        if '===' in line:
            smiles.append(line.split()[1])
        elif '***' in line:
            solvents.append(line.split()[1])
        elif 'number_conformers' in line:
            nconformers.append(int(line.split()[1]))
    return smiles, solvents, nconformers

# function to read the global information of the system
def homo_reader(smiles, solvent, file):
    with open(file) as f:
        data = f.readlines()
    record, auxrecord, aux2record = False, False, False
    read = False
    for line in data:
        if '===' in line and smiles in line:
            auxrecord = True
        elif '***' in line and solvent in line:
            aux2record = True
        elif '---' in line and 'Conformer 1' in line:
            record = auxrecord and aux2record
        elif 'Orbital Energies:' in line and record:
            read = True
            homo1 = float(line.split()[-1])
        elif read:
            try:
                value = float(line.split()[-1])
            except ValueError:
                value = homo1
            break
    return value

# Main script starts here 🚀

outdir = 'outputs'
conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

copy_query = '''
UPDATE {}
  SET HOMO = (SELECT HOMO FROM {} WHERE smiles = ? AND solvent = ?)
    WHERE smiles = ? AND solvent = ?
'''

global_update_query = '''
UPDATE {} SET
    HOMO = ?
WHERE smiles = ? AND solvent = ?
'''

# loop to read all the files in the directory
for file in os.listdir(outdir):
    if not file.endswith('.out'):
        continue

    smiles_list, solvents, nconformers = solvent_reader(os.path.join(outdir, file))

    for smiles, solvent, nconf in zip(smiles_list, solvents, nconformers):

        # Get the table where the molecule is/are [it can be in more than one table]
        cur.execute('SELECT table_name, atom_analysed FROM parameters WHERE smiles = ? AND solvent = ?', (smiles, solvent))
        tables_atoms = cur.fetchall()

        if nconf == 1:
            for table, atom in tables_atoms:
                cur.execute(copy_query.format(table+'_msc', table), (smiles, solvent, smiles, solvent))
            continue

        # update the name of the table
        tables_atoms = [(table[0]+'_msc', table[1]) for table in tables_atoms]

        # Global descriptors
        homo_descriptor = homo_reader(smiles, solvent, os.path.join(outdir, file))
        for table in set([table[0] for table in tables_atoms]):
            cur.execute(global_update_query.format(table), (
                homo_descriptor, smiles, solvent
            ))

conn.commit()
conn.close()

