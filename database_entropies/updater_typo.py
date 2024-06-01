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

cursor.execute("UPDATE test_molecules SET smile = 'CCSCC' WHERE smile = 'CSC'")

# Commit the changes and close the connection
conn.commit()
conn.close()

