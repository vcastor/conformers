#!/usr/bin/python3
import sqlite3
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Data written in the csv file
input_file_path = 'EntropiesNIST_COSMO.csv'

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Create table with the specified columns
cursor.execute('''
CREATE TABLE IF NOT EXISTS molecules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    smile TEXT,
    molecule_name TEXT,
    natoms INTEGER,
    nconformers INTEGER,
    trans_S REAL,
    rot_S REAL,
    vib_S REAL,
    experimental_S REAL
)
''')

#
# Function to parse each line and insert into the database
def insert_line_into_db(line):
    name, smile, exp_val = line.split(';')
    # Insert into the database
    cursor.execute('''
    INSERT INTO molecules (
        smile,
        molecule_name,
        experimental_S
    ) VALUES (?, ?, ?)
    ''', (smile, name, float(exp_val)))

# Read the input file and process each line
with open(input_file_path, 'r', encoding="ISO-8859-1") as file:
    for line in file:
        insert_line_into_db(line)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created and data inserted successfully ✨")

