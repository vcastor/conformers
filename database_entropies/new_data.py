#!/usr/bin/python3
import sqlite3
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Data written in the csv file
input_file_path = 'EntropiesNIST_COSMO_test.csv'

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

#
# Function to parse each line and insert into the database
def insert_line_into_db(line):
    name, smile, exp_val, eps, rad, _, _ = line.split(';')
    # Insert into the database
    cursor.execute('''
    INSERT INTO test_molecules (
        smile,
        molecule_name,
        experimental_S,
        epsilon,
        rad
    ) VALUES (?, ?, ?, ?, ?)
    ''', (smile, name, float(exp_val.replace(',','.')), float(eps.replace(',','.')), float(rad.replace(',','.'))))

# Read the input file and process each line
with open(input_file_path, 'r', encoding="ISO-8859-1") as file:
    for line in file:
        insert_line_into_db(line)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created and data inserted successfully ✨")

