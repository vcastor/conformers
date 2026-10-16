#!/usr/bin/python3
import os
import sqlite3
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Retrieve all molecule names from the database
cursor.execute('SELECT molecule_name, natoms FROM PBE0')
molecules = cursor.fetchall()

def contribution_S(outfile):
    with open(outfile, 'r', encoding="ISO-8859-1") as file:
        data = file.readlines()
    natoms = data[2].split()[1]
    nconformers = int(data[3].split()[1])
    # skip the line of weights
    base_index = 7 if nconformers == 1 else 6
    trans_S = data[base_index].split()[1]
    rot_S = data[base_index + 1].split()[2]
    vib_S = data[base_index + 2].split()[2]
    correction = data[base_index + 3].split()[2]
    mu  = data[base_index + 5].split()[3]
    eta = data[base_index + 6].split()[2]
    gamma = data[base_index + 7].split()[2]
    return natoms, nconformers, trans_S, rot_S, vib_S, correction, mu, eta, gamma

for molecule, atoms in molecules:
    if molecule == "2,2'-Dimethylbiphenyl":
        outfile = os.path.join('pbe0', 'output_files', "2,2-Dimethylbiphenyl.out")
    else:
        outfile = os.path.join('pbe0', 'output_files', f'{molecule}.out')
    # outfile = os.path.join('pbe', 'output_files', f'{molecule}.out')
    if os.path.exists(outfile):# and atoms is None:
        natoms, nconformers, trans_S, rot_S, vib_S, correction, mu, eta, gamma = contribution_S(outfile)
        cursor.execute('''
        UPDATE PBE0 SET
        natoms = ?,
        nconformers = ?,
        trans_S = ?,
        rot_S = ?,
        vib_S = ?,
        correctionS = ?,
        mu = ?,
        eta = ?,
        gamma = ?
        WHERE molecule_name = ?
        ''', (natoms, nconformers, trans_S, rot_S, vib_S, correction, mu, eta, gamma, molecule))

# Commit the changes and close the connection
conn.commit()
conn.close()

print('All values updated successfully ✨')

