#!/usr/bin/python3
import os
import sqlite3
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'nucleo_data.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Retrieve all molecule names from the database
cursor.execute('SELECT smiles, solvent FROM non_reactive_N')
molecules = cursor.fetchall()

basecmd = '/Users/vcastor/amshome/src/lib/core/solvation/CosmoSolvents.f90'
for smile, solvent in molecules:
    if '/' in solvent:
        continue
    solventcommand = solvent
    if solvent == 'DCM':
        solventcommand = 'DICHLOROMETHANE'
    elif solvent == 'THF':
        solventcommand = 'TETRAHYDROFURAN'
    elif solvent.lower() == 'MeCN'.lower():
        solventcommand = 'ACETONITRILE'
    elif solvent == 'DMF':
        solventcommand = 'dmfa'
    elif solvent == 'ET2O':
        solventcommand = 'diethylether'
    cmd = f'grep -i \"\'{solventcommand}\'\" {basecmd}'
    nline = os.popen(cmd).read().split(',')
    nepsilon, nrad = nline[2].strip(), nline[3].strip()
    nepsilon, nrad = nepsilon.replace('_KREAL',''), nrad.replace('_KREAL','')
    if '/' or ')' in nrad:
        nrad = nrad.replace('/','').replace(')','')
    nrad, nepsilon = float(nrad), float(nepsilon)
    cursor.execute('''
    UPDATE non_reactive_N SET
    epsilon = ?,
    rad = ?
    WHERE smiles = ? AND solvent = ?
    ''', (nepsilon, nrad, smile, solvent))

# Commit the changes and close the connection
conn.commit()
conn.close()

