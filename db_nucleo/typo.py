#!/usr/bin/python3
import sqlite3

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

# List of tables 
tables = ['reactive', 'peculiar', 'no_reactive']
msctables = [c+'_msc' for c in tables]
pondtables = [c+'_ponderated' for c in tables]
tables += msctables + pondtables

old_column = 'condensed_liner_response'
new_column = 'condensed_linear_response'

# Function to drop columns
for table in tables:
    cur.execute(f'ALTER TABLE {table} RENAME COLUMN {old_column} TO {new_column}')

con.commit()
con.close()

