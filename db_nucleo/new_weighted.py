#!/usr/bin/python3
import sqlite3

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

tables = ['reactive_msc', 'no_reactive_msc', 'reactive', 'no_reactive']

# Create the new tables
for table in tables:
    cur.execute(f'PRAGMA table_info({table})')
    cols = [col[1] for col in cur.fetchall()]
    if 'q_qtaim_w' not in cols:
        cur.execute(f'ALTER TABLE {table} ADD COLUMN q_qtaim_w REAL')
    if 'condensed_linear_response_w' not in cols:
        cur.execute(f'ALTER TABLE {table} ADD COLUMN condensed_linear_response_w REAL')

conn.commit()
conn.close()

