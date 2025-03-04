#!/usr/bin/python3
import sqlite3

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

tables = ['reactive_msc', 'no_reactive_msc']

# Create the new tables
for table in tables:
    cur.execute(f'PRAGMA table_info({table})')
    cols = [col[1] for col in cur.fetchall()]
    if 'P' not in cols:
        cur.execute(f'ALTER TABLE {table} ADD COLUMN P REAL')
    if 'Pf2' not in cols:
        cur.execute(f'ALTER TABLE {table} ADD COLUMN Pf2 REAL')

    cur.execute(f'SELECT smiles, solvent, atom_analysed, hyperhardness, f2 FROM {table} WHERE P IS NULL AND Pf2 IS NULL')
    for smiles, solvent, atom, gamma, f2 in cur.fetchall():
        if atom < 1:
            continue
        p, pf2 = 1/gamma, f2/gamma
        cur.execute(f'''UPDATE {table} SET P = ?, Pf2 = ? WHERE smiles = ? AND solvent = ? AND atom_analysed = ?''', (p, pf2, smiles, solvent, atom))

conn.commit()
conn.close()

