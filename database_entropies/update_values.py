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
cursor.execute('SELECT molecule_name, natoms FROM molecules')
molecules = cursor.fetchall()

def contribution_S(outfile):
    with open(outfile, 'r', encoding="ISO-8859-1") as file:
        data = file.readlines()
    natoms = data[2].split()[1]
    nconformers = int(data[3].split()[1])
    if nconformers == 1:
        trans_S = data[7].split()[1]
        rot_S = data[8].split()[2]
        vib_S = data[9].split()[2]
        mu = data[10].split()[1]
        eta = data[11].split()[2] #hardness
        # gamma = data[12].split()[2] #Hyperhardness
    else:
        trans_S = data[6].split()[1]
        rot_S = data[7].split()[2]
        vib_S = data[8].split()[2]
        mu = data[9].split()[1]
        eta = data[10].split()[2]
    return natoms, nconformers, trans_S, rot_S, vib_S, mu, eta

for molecule, atoms in molecules:
    outfile = os.path.join('output_files', f'{molecule}.out')
    if os.path.exists(outfile) and atoms is None:
        natoms, nconformers, trans_S, rot_S, vib_S, mu, eta = contribution_S(outfile)
        cursor.execute('''
        UPDATE molecules SET
        natoms = ?,
        nconformers = ?,
        trans_S = ?,
        rot_S = ?,
        vib_S = ?,
        mu = ?,
        eta = ?
        WHERE molecule_name = ?
        ''', (natoms, nconformers, trans_S, rot_S, vib_S, mu, eta, molecule))

# Commit the changes and close the connection
conn.commit()
conn.close()

