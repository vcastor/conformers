#!/usr/bin/python3
import sqlite3

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

dyn_tables = ['reactive', 'peculiar', 'no_reactive']
msc_tables = ['reactive_msc', 'peculiar_msc', 'no_reactive_msc']

for table in dyn_tables + msc_tables:
    cur.execute(f'ALTER TABLE {table} ADD COLUMN HOMO REAL;')
    # cur.execute(f'ALTER TABLE {table} ADD COLUMN condensed_liner_response REAL;')

# for i in range(len(dyn_tables)):
#     cur.execute(f'SELECT smiles, solvent, atom_analysed FROM {msc_tables[i]};')
#     for r in cur.fetchall():
#         cur.execute('SELECT nconformers FROM parameters WHERE smiles = ? AND solvent = ? AND atom_analysed = ?;', r)
#         nconformers = cur.fetchone()
#         nconformers = nconformers[0]
#         if nconformers > 1:
#             continue
#         cur.execute(f'''SELECT electrostatic_potential, condensed_liner_response FROM {dyn_tables[i]}
#             WHERE smiles = ? AND solvent = ? AND atom_analysed = ?;''', r)
#         values = cur.fetchone()
#         cur.execute(f'''UPDATE {msc_tables[i]}
#             SET electrostatic_potential = ?, condensed_liner_response = ?
#             WHERE smiles = ? AND solvent = ? AND atom_analysed = ?;''', values + r)

con.commit()
con.close()

