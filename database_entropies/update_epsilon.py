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
cursor.execute('SELECT molecule_name, epsilon, rad FROM molecules')
molecules = cursor.fetchall()


basecmd = '/Users/vcastor/amshome/src/lib/core/solvation/CosmoSolvents.f90'
for mol, epsilon, rad in molecules:
    if epsilon is None and rad is None:
        cmd = f'grep -i \"\'{mol}\'\" {basecmd}'
        nline = os.popen(cmd).read().split(',')
        nepsilon, nrad = nline[2].strip(), nline[3].strip()
        nepsilon, nrad = nepsilon.replace('_KREAL',''), nrad.replace('_KREAL','')
        if '/' or ')' in nrad:
            nrad = nrad.replace('/','').replace(')','')
        nrad, nepsilon = float(nrad), float(nepsilon)
        cursor.execute('''
        UPDATE molecules SET
        epsilon = ?,
        rad = ?
        WHERE molecule_name = ?
        ''', (nepsilon, nrad, mol))

# Commit the changes and close the connection
conn.commit()
conn.close()

