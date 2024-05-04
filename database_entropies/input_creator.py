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

for smile, name in molecules:
    filename = 'input_files/' + name + '.csv'
    with open(filename, 'w') as f:
        # Smile, solvent
        f.write(smile + ', ' + name + '\n')
        # Paramters
        # Filter
        f.write('Energy threshold Score, 3.0\n')
        f.write('Energy threshold Optimize, 5.0\n')
        f.write('RMSD, 2.5\n')
        # DFT and DFTB
        f.write('Functional, PBE\n')
        f.write('Basis set, TZP\n')
        f.write('dispersion, GRIMME3 BJDAMP\n')
        f.write('model, GFN1-xTB\n')
        #
        f.write('Temperature, 298\n')
        f.write('Number of conformers, 20\n')

print("✨ Input files created successfully! 🚀✨")

