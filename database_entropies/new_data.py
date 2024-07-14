#!/usr/bin/python3
import sqlite3
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Data written in the csv file
input_file_path = '/Users/vcastor/Downloads/EntropiesNIST_final.txt'

# Database file path
db_file_path = 'entropiesCOSMO.db'
# Solvent SMILES S°liq eps Rad d M

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

#
# Function to parse each line and insert into the database
def insert_line_into_db(line):
    _, name, smile, exp_val, eps, rad, _, _ = line.split()
    q = 'SELECT 1 FROM {} WHERE smile = ? OR molecule_name = ?'
    cursor.execute(q.format('molecules'), (smile, name))
    in_molecules = cursor.fetchone()
    cursor.execute(q.format('test_molecules'), (smile, name))
    in_test_molecules = cursor.fetchone()
    if not in_molecules and not in_test_molecules:
        cursor.execute('''INSERT INTO new_molecules (smile, molecule_name, experimental_S, epsilon, rad)
                          VALUES (?, ?, ?, ?, ?)''', (smile, name, float(exp_val), float(eps), float(rad)))

# Read the input file and process each line
with open(input_file_path, 'r', encoding="ISO-8859-1") as file:
    for line in file:
        insert_line_into_db(line)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created and data inserted successfully ✨")

