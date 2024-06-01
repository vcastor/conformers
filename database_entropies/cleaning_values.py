#!/usr/bin/python3
import os
import sqlite3
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'entropiesCOSMO.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Clean the values previously computed
cursor.execute('UPDATE molecules SET natoms = NULL, nconformers = NULL')
cursor.execute('UPDATE molecules SET trans_S = NULL, rot_S = NULL, vib_S = NULL')

# Commit the changes and close the connection
conn.commit()
conn.close()

