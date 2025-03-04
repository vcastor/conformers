#!/usr/bin/python3
import os
import sqlite3

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

old_tables = ['reactive', 'peculiar', 'no_reactive']
new_tables = [c+'_ponderated' for c in old_tables]
columns_to_copy = ['smiles', 'solvent', 'atom_analysed']

# Create new tables
for old, new in zip(old_tables, new_tables):
    cur.execute(f'DROP TABLE IF EXISTS {new}')
    cur.execute(f'CREATE TABLE {new} AS SELECT * FROM {old} WHERE 1=0')

    # Copy columns
    cols = ', '.join(columns_to_copy)
    cur.execute(f'''
        INSERT INTO {new} ({cols})
        SELECT {cols} FROM {old}
    ''')

conn.commit()
conn.close()

