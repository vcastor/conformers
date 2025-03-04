#!/usr/bin/python3
import sqlite3

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

tables = ['reactive', 'no_reactive', 'peculiar']
msctables = [t+'_msc' for t in tables]
ponderated = [t+'_ponderated' for t in tables]
tables += msctables + ponderated

# Create the new tables
for table in tables:
    cur.execute(f'SELECT smiles, solvent, atom_analysed, hyperhardness, f2 FROM {table}')
    for smiles, solvent, atom, gamma, f2 in cur.fetchall():
        p, pf2 = 1/gamma, f2/gamma
        cur.execute(f'''
            UPDATE {table} SET P = ?, Pf2 = ?
            WHERE smiles = ? AND solvent = ? AND atom_analysed = ?
        ''', (p, pf2, smiles, solvent, atom))

conn.commit()
conn.close()

