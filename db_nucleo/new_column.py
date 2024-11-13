#!/usr/bin/python3
import sqlite3

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

# cur.execute('ALTER TABLE main ADD COLUMN electrostatic_potential REAL;')
# cur.execute('ALTER TABLE main ADD COLUMN condensed_liner_response REAL;')

cur.execute('ALTER TABLE main ADD COLUMN epsilon REAL;')
cur.execute('ALTER TABLE main ADD COLUMN rad REAL;')

con.commit()
con.close()

