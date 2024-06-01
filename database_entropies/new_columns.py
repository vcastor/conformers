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

# cursor.execute('''
#     CREATE TABLE pbe0 AS
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

cursor.execute('ALTER TABLE pbe0 ADD COLUMN natoms INTEGER;')
cursor.execute('ALTER TABLE pbe0 ADD COLUMN nconformers INTEGER;')
cursor.execute('ALTER TABLE pbe0 ADD COLUMN trans_S REAL;')
cursor.execute('ALTER TABLE pbe0 ADD COLUMN rot_S REAL;')
cursor.execute('ALTER TABLE pbe0 ADD COLUMN vib_S REAL;')
cursor.execute('ALTER TABLE pbe0 ADD COLUMN correctionS REAL;')
cursor.execute('ALTER TABLE pbe0 ADD COLUMN mu REAL;')
cursor.execute('ALTER TABLE pbe0 ADD COLUMN eta REAL;')
cursor.execute('ALTER TABLE pbe0 ADD COLUMN gamma REAL;')

conn.commit()
conn.close()

