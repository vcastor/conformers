#!/usr/bin/python3
import sqlite3

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

# Get the column names from the 'main' table
cur.execute("PRAGMA table_info(main)")
columns = [row[1] for row in cur.fetchall()]

# Print the column names
print("Columns in 'main' table:", columns)

# Close the connection
con.close()

