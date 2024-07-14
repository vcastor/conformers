#!/usr/bin/python3
import sqlite3

database = 'entropiesCOSMO.db'

# Connect to the database
conn = sqlite3.connect(database)
cursor = conn.cursor()

#cursor.execute('ALTER TABLE molecules ADD COLUMN epsilon REAL;')
#cursor.execute('ALTER TABLE molecules ADD COLUMN rad REAL;')

# Get the columns from the molecules table
# cursor.execute("PRAGMA table_info(molecules)")
# columns = cursor.fetchall()

# Create a list of column definitions
# column_defs = ", ".join([f"{col[1]} {col[2]}" for col in columns])

# Create the new table test_molecules with the same columns as the molecules table
# cursor.execute(f"CREATE TABLE IF NOT EXISTS test_molecules ({column_defs})")

# New columns for the test_molecules table

# cursor.execute('''
#     CREATE TABLE new_molecules AS
#     SELECT
#         molecules.smile AS smile,
#         molecules.molecule_name AS molecule_name,
#         molecules.epsilon AS epsilon,
#         molecules.rad AS rad,
#         molecules.experimental_S AS experimental_S
#     FROM
#         molecules
#     UNION ALL
#     SELECT
#         test_molecules.smile AS smile,
#         test_molecules.molecule_name AS molecule_name,
#         test_molecules.epsilon AS epsilon,
#         test_molecules.rad AS rad,
#         test_molecules.experimental_S as experimental_S
#     FROM
#         test_molecules
# ''')

# Create a new table

cursor.execute('''
CREATE TABLE IF NOT EXISTS all_molecules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    smile TEXT,
    molecule_name TEXT,
    epsilon REAL,
    rad REAL,
    natoms INTEGER,
    nconformers INTEGER,
    trans_S REAL,
    rot_S REAL,
    vib_S REAL,
    correctionS REAL,
    mu REAL,
    eta REAL,
    gamma REAL,
    experimental_S REAL
)
''')

# Add the new columns to the pbe0 table

# cursor.execute('ALTER TABLE pbe0 ADD COLUMN natoms INTEGER;')
# cursor.execute('ALTER TABLE pbe0 ADD COLUMN nconformers INTEGER;')
# cursor.execute('ALTER TABLE pbe0 ADD COLUMN trans_S REAL;')
# cursor.execute('ALTER TABLE pbe0 ADD COLUMN rot_S REAL;')
# cursor.execute('ALTER TABLE pbe0 ADD COLUMN vib_S REAL;')
# cursor.execute('ALTER TABLE pbe0 ADD COLUMN correctionS REAL;')
# cursor.execute('ALTER TABLE pbe0 ADD COLUMN mu REAL;')
# cursor.execute('ALTER TABLE pbe0 ADD COLUMN eta REAL;')
# cursor.execute('ALTER TABLE pbe0 ADD COLUMN gamma REAL;')

# Merge the molecules in [molecules, test_molecules, new_molecules] into all_molecules

cursor.execute('''
INSERT INTO all_molecules (smile, molecule_name, epsilon, rad, natoms, nconformers, trans_S, rot_S, vib_S, correctionS, mu, eta, gamma, experimental_S)
SELECT smile, molecule_name, epsilon, rad, natoms, nconformers, trans_S, rot_S, vib_S, correctionS, mu, eta, gamma, experimental_S FROM molecules
UNION
SELECT smile, molecule_name, epsilon, rad, natoms, nconformers, trans_S, rot_S, vib_S, correctionS, mu, eta, gamma, experimental_S FROM test_molecules
UNION
SELECT smile, molecule_name, epsilon, rad, natoms, nconformers, trans_S, rot_S, vib_S, correctionS, mu, eta, gamma, experimental_S FROM new_molecules
''')

conn.commit()
conn.close()

