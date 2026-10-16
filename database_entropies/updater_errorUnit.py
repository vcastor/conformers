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
cursor.execute('SELECT molecule_name, trans_S, rot_S, vib_S FROM molecules')
valdata = cursor.fetchall()

factor = 1000/298.15
for row in valdata:
    try:
        cursor.execute('''
        UPDATE molecules
        SET trans_S = ?, rot_S = ?, vib_S = ?
        WHERE molecule_name = ?
        ''', (factor*row[1], factor*row[2], factor*row[3], row[0]))
    except TypeError:
        continue

# Commit the changes and close the connection
conn.commit()
conn.close()

