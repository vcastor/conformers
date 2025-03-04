#!/usr/bin/python3
import sqlite3

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

# Create the new table
cur.execute('DROP TABLE IF EXISTS parameters')
cur.execute(f'''
    CREATE TABLE parameters (
        smiles TEXT,
        molecule_name TEXT,
        solvent TEXT,
        family TEXT,
        stars INTEGER,
        atom_analysed INTEGER,
        nconformers INTEGER,
        experimental_N REAL DEFAULT 0,
        experimental_Sn REAL DEFAULT 0,
        epsilon REAL,
        rad REAL,
        peculiar INTEGER,
        comment TEXT
    )
''')

tables = ['reactive', 'non_reactive_N']

for table in tables:
    # Get the data from the tables
    cur.execute(f'''
                SELECT smiles, molecule_name, solvent, family, stars,
                atom_analysed, nconformers, epsilon, rad
                FROM {table}''')
    rows = cur.fetchall()

    # Insert data into the new table
    for r in rows:
        cur.execute(f'''INSERT INTO parameters
            (smiles, molecule_name, solvent, family, stars, atom_analysed, nconformers, epsilon, rad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', r)

# particular loop for comments, some rows have no any comment
cur.execute(f'SELECT smiles, solvent, atom_analysed, comment FROM reactive')
rows = cur.fetchall()
for r in rows:
    if r[-1] == None:
        continue
    cur.execute('UPDATE parameters SET comment = ? WHERE smiles = ? AND solvent = ? AND atom_analysed = ?', (r[-1], r[0], r[1], r[2]))

# only reactive table has experimental_N and experimental_Sn
cur.execute('SELECT experimental_N, experimental_Sn, smiles, solvent, atom_analysed FROM reactive')
exp_data = cur.fetchall()
for exp in exp_data:
    cur.execute('UPDATE parameters SET experimental_N = ?, experimental_Sn = ? WHERE smiles = ? AND solvent = ? AND atom_analysed = ?', exp)

# # delate the columns from the old tables
# for table in tables:
#     cur.execute(f'ALTER TABLE {table} DROP COLUMN family')
#     cur.execute(f'ALTER TABLE {table} DROP COLUMN stars')
#     cur.execute(f'ALTER TABLE {table} DROP COLUMN epsilon')
#     cur.execute(f'ALTER TABLE {table} DROP COLUMN rad')
# cur.execute(f'ALTER TABLE reactive DROP COLUMN experimental_N')
# cur.execute(f'ALTER TABLE reactive DROP COLUMN experimental_Sn')

# change the name of non_reactive_N table to no_reactive
cur.execute('ALTER TABLE non_reactive_N RENAME TO no_reactive')

conn.commit()
conn.close()

