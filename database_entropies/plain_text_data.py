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

# Retrieve all molecule names from the database
cursor.execute('SELECT molecule_name, trans_S, rot_S, vib_S, experimental_S, correctionS, rad, epsilon FROM molecules')
valdata = cursor.fetchall()

filtered_valdata = [val for val in valdata if None not in val]

# Commit the changes and close the connection
conn.commit()
conn.close()

with open('plain_text_data.csv', 'w') as file:
    file.write('molecule_name, S_t, S_r, S_v, experimental_S, S_corr, rad, epsilon\n')
    for row in valdata:
        try:
            file.write(f'{row[0]}, {row[1]:.3f}, {row[2]:.3f}, {row[3]:.3f}, {row[4]:.3f}, {row[5]:.3f}, {row[6]:.2f}, {row[7]:.2f}\n')
        except TypeError:
            continue

