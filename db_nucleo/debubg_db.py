#!/usr/bin/python3
import sqlite3

# Main script starts here 🚀

outdir = 'outputs'
conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

smiles = 'C[Si](OC(C1=CC=CC=C1)(C2=CC=CC=C2)[C@H]3NCCC3)(C)C'

cur.execute("SELECT * FROM reactive WHERE smiles LIKE ?", ('%' + smiles + '%',))
print(cur.fetchall())
cur.execute("SELECT * FROM reactive WHERE smiles = ?", (smiles,))
print(cur.fetchall())

conn.commit()
conn.close()

