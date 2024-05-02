#!/usr/bin/python3
import sqlite3
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

cursor.execute('''
SELECT smile, molecule_name FROM molecules
''')

molecules = cursor.fetchall()

# Commit the changes and close the connection
conn.commit()
conn.close()

with open('all_systems.csv', 'w') as f:
    f.write('# Smile, solvent\n')
    for smile, name in molecules:
        f.write(smile + ', ' + name + '\n')
    f.write('#\n')
    f.write('# Paramters\n')
    f.write('# Filter\n')
    f.write('Energy threshold Score, 5.0\n')
    f.write('Energy threshold Optimize, 3.0\n')
    f.write('RMSD, 2.5\n')
    f.write('# DFT and DFTB\n')
    f.write('Functional, B3LYP\n')
    f.write('Basis set, DZP\n')
    f.write('dispersion, GRIMME3 BJDAMP\n')
    f.write('model, GFN1-xTB\n')
    f.write('#\n')
    f.write('Temperature, 298\n')
    f.write('Number of conformers, 50\n')

print("Database created and data inserted successfully ✨")

