#!/usr/bin/python3
import os
import shutil
import sqlite3
import subprocess
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'database_entropies/entropiesCOSMO.db'

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
    inputf = os.path.join('database_entropies', 'input_files', f'{name}.csv')
    output = os.path.join('database_entropies', 'output_files', f'{name}.out')
    if not os.path.exists(output):
        command = f'$AMSBIN/plams filter.py -v {inputf}'
        subprocess.run(command, shell=True)
        shutil.move(inputf, output)

