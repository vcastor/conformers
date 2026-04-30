#!/usr/bin/python3
import os
import sqlite3
import subprocess

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

# Add the column
table = 'parameters'
cur.execute(f"PRAGMA table_info({table})")
columns = [row[1] for row in cur.fetchall()]
if 'raw_out' not in columns:
    cur.execute(f"ALTER TABLE {table} ADD COLUMN raw_out TEXT")

# get the smiles, solvent
cur.execute("SELECT smiles, solvent, family FROM parameters")
combinations = cur.fetchall()

xyzdir = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/xyz_conformers'

for smiles, solvent, family in combinations:
    # Find the file
    familydir = os.path.join(xyzdir, family)
    grep_cmd = f"grep -rF '{smiles}' {familydir} | grep '{solvent}'"
    result = subprocess.run(grep_cmd, shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        file_path = result.stdout.split('\n')[0].split(':')[0]
        file = file_path.split("/")[-1].replace('.xyz', '').split('_')[1]
        cur.execute("UPDATE parameters SET raw_out = ? WHERE smiles = ? AND solvent = ?",
                    (file, smiles, solvent))

conn.commit()
conn.close()

