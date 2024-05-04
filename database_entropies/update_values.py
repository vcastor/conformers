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
cursor.execute('SELECT molecule_name FROM molecules')
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
    else:
        trans_S = data[6].split()[1]
        rot_S = data[7].split()[2]
        vib_S = data[8].split()[2]
    return natoms, nconformers, trans_S, rot_S, vib_S

for molecule in molecules:
    name = molecule[0]  # Assuming fetchall returns a list of tuples
    outfile = os.path.join('output_files', f'{name}.out')
    if os.path.exists(outfile):
        natoms, nconformers, trans_S, rot_S, vib_S = contribution_S(outfile)
        cursor.execute('''
        UPDATE molecules SET
        natoms = ?,
        nconformers = ?,
        trans_S = ?,
        rot_S = ?,
        vib_S = ?
        WHERE molecule_name = ?
        ''', (natoms, nconformers, trans_S, rot_S, vib_S, name))

# Commit the changes and close the connection
conn.commit()
conn.close()

