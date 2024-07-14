#!/usr/bin/python3
import os
import sqlite3

# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
# cursor = conn.cursor()

# cursor.execute("UPDATE test_molecules SET smile = 'CCSCC' WHERE smile = 'CSC'")

# Function to delete rows where nconformers is NULL
def delete_rows_with_null_nconformers(conn):
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM pbe0 WHERE natoms IS NULL
    ''')
    conn.commit()
    cursor.close()

# Delete rows with NULL nconformers
# delete_rows_with_null_nconformers(conn)

# # Function to rename a table
# def rename_table(conn, old_table_name, new_table_name):
#     cursor = conn.cursor()
#     cursor.execute(f'''
#     ALTER TABLE {old_table_name} RENAME TO {new_table_name}
#     ''')

# new_names = ['PBE', 'PBE0']
# old_names = ['all_molecules', 'pbe0']

# # Rename tables
# for i in range(len(old_names)):
#     rename_table(conn, old_names[i], new_names[i])

cursor = conn.cursor()
cursor.execute(f'ALTER TABLE pbe0 RENAME TO temp')
cursor.execute(f'ALTER TABLE temp RENAME TO PBE0')

# Commit the changes and close the connection
conn.commit()
conn.close()

