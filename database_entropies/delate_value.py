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

cursor.execute("DELETE FROM PBE0 WHERE smile = 'CCCCCBr'")
# cursor.execute("DROP TABLE pbe0")

# # Step 1: Create a temporary table to store unique rows
# cursor.execute('''
# CREATE TEMPORARY TABLE unique_smiles AS
# SELECT * FROM new_molecules
# GROUP BY smile
# ORDER BY id
# ''')

# Step 2: Delete all rows from the original table
# cursor.execute('DELETE FROM new_molecules')

# # Step 3: Insert the unique rows back into the original table
# cursor.execute('''
# INSERT INTO new_molecules
# SELECT * FROM unique_smiles
# ''')


# Commit the changes and close the connection
conn.commit()
conn.close()

