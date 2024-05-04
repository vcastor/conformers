#!/usr/bin/python3
import sqlite3

database = 'entropiesCOSMO.db'

# Connect to the database
conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute('ALTER TABLE molecules ADD COLUMN epsilon REAL;')
cursor.execute('ALTER TABLE molecules ADD COLUMN rad REAL;')

conn.commit()
conn.close()

