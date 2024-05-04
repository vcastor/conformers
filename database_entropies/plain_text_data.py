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
cursor.execute('SELECT molecule_name, trans_S, rot_S, vib_S, experimental_S FROM molecules')
valdata = cursor.fetchall()

filtered_valdata = [val for val in valdata if None not in val]

# Commit the changes and close the connection
conn.commit()
conn.close()

factor = 1000/298.15
with open('plain_text_data.txt', 'w') as file:
    file.write('molecule_name, trans_S, rot_S, vib_S, experimental_S\n')
    for row in valdata:
        try:
            file.write(f'{row[0]}, {factor*row[1]:.3f}, {factor*row[2]:.3f}, {factor*row[3]:.3f}, {row[4]:.3f}\n')
        except TypeError:
            continue

