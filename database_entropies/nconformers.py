#!/usr/bin/python3
import os
import sqlite3

# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Retrieve all molecule names from the database
# cursor.execute('SELECT molecule_name, nconformers FROM PBE0')
cursor.execute('''
SELECT PBE0.molecule_name, PBE0.nconformers AS nconformersPBE0, PBE.nconformers AS nconformersPBE
FROM PBE0
JOIN PBE ON PBE0.molecule_name = PBE.molecule_name
WHERE PBE0.nconformers IS NOT NULL AND PBE.nconformers IS NOT NULL
''')
valdata = cursor.fetchall()

filtered_valdata = [val for val in valdata if None not in val]

cursor.execute('SELECT molecule_name, natoms FROM PBE0 WHERE natoms=(SELECT MAX(natoms) FROM PBE0)')
max_results = cursor.fetchall()
cursor.execute('SELECT molecule_name, natoms FROM PBE0 WHERE natoms=(SELECT MIN(natoms) FROM PBE0)')
min_results = cursor.fetchall()

print('The systems with more atoms:', max_results)
print('The systems with less atoms:', min_results)

# Commit the changes and close the connection
conn.commit()
conn.close()

with open('nconformers.csv', 'w') as file:
    file.write('molecule_name, nconformersPBE0, nconformersPBE\n')
    for row in valdata:
        file.write(f'{row[0]}, {row[1]}, {row[2]}\n')

