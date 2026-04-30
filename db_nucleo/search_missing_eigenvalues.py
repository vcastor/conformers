#!/usr/bin/python3
import sqlite3
import csv

# with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
#     writer = csv.writer(f, lineterminator='\n')
#     writer.writerow(['smiles','solvent'])
#     writer.writerows(missing)
#     for key,val in PARAMETERS.items():
#         f.write(f"{key}, {val}\n")

DB      = 'nucleo_data.db'
TABLES  = ['reactive', 'no_reactive', 'peculiar']
OUTFILE = 'missing_eigenvalues2.csv'

settings_rows = [
   ['Energy threshold Score', '2.5'],
   ['Energy threshold Optimize', '5.0'],
   ['RMSDscore', '1.5'],
   ['RMSDOpt', '3.0'],
   ['Functional', 'PBE'],
   ['Basis set', 'TZP'],
   ['dispersion', 'GRIMME3 BJDAMP'],
   ['model', 'GFN1-xTB'],
   ['Temperature', '298'],
   ['Number of conformers', '20'],
]

rows = []

with sqlite3.connect(DB) as con:
   cur = con.cursor()
   for table in TABLES:
      cur.execute(
         f'''
         SELECT smiles, solvent
         FROM {table}
         WHERE eigenchi IS NULL
         '''
      )
      rows.extend(cur.fetchall())

with open(OUTFILE, 'w', newline='', encoding='utf-8') as f:
   writer = csv.writer(f)
   writer.writerows(rows)
   writer.writerows(settings_rows)
