#!/usr/bin/python3
import os
import sqlite3

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

typo_name = 'Tetrahydrofurane'
correct_name = 'Tetrahydrofuran'

# Update the molecule name in the database
cursor.execute('''
UPDATE molecules SET molecule_name = ?
WHERE molecule_name = ?
''', (correct_name, typo_name))

# Commit the changes and close the connection
conn.commit()
conn.close()

