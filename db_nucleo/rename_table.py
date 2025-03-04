#!/usr/bin/python3
import sqlite3

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

# cur.execute('ALTER TABLE parameters ADD COLUMN table_name TEXT;')
cur.execute('SELECT smiles, solvent, atom_analysed, peculiar FROM parameters;')
for r in cur.fetchall():
    smiles, solvent, atom_analysed, peculiar = r
    if peculiar == 0:
        table_name = 'reactive'
    elif peculiar == 1:
        table_name = 'peculiar'
    elif peculiar == 2: # not computed systems
        continue
    elif peculiar == 3:
        table_name = 'no_reactive'
    else:
        continue
    cur.execute('''UPDATE parameters SET table_name = ?
        WHERE smiles = ? AND solvent = ? AND atom_analysed = ?;''',
        (table_name, smiles, solvent, atom_analysed))

con.commit()
con.close()

