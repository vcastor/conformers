#!/usr/bin/python3
import sqlite3
import csv
import os

def format_value(value):
    if isinstance(value, float):
        return f"{value:.2f}"
    return value

# Connect to the database
con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()
    
# Export parameters table with reactive yes/no conversion
cur.execute("SELECT * FROM parameters")
        
# Get column names
column_names = [description[0] for description in cur.description]
rows = cur.fetchall()
        
# Find the index of table_name column
table_name_index = column_names.index('table_name') if 'table_name' in column_names else None
        
# Write parameters.csv
with open('parameters.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
            
    # Write header (replace table_name with reactive for clarity)
    header = column_names.copy()
    header[table_name_index] = 'reactive'
    writer.writerow(header)
            
    # Write data rows with reactive yes/no conversion
    for row in rows:
        row_list = list(row)
        # Convert table_name to yes/no based on whether it contains 'reactive'
        if row_list[table_name_index]:
            if 'reactive' in str(row_list[table_name_index]).lower():
                row_list[table_name_index] = 'yes'
            else:
                row_list[table_name_index] = 'no'
        else:
            row_list[table_name_index] = 'no'
        row_list = [format_value(val) for val in row_list]
        writer.writerow(row_list)
        
# Export reactive table
cur.execute("SELECT * FROM reactive")
column_names = [description[0] for description in cur.description]
rows = cur.fetchall()
        
with open('reactive.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(column_names)
    formatted_rows = [[format_value(val) for val in row] for row in rows]
    writer.writerows(formatted_rows)

# Export no_reactive table
cur.execute("SELECT * FROM no_reactive")
column_names = [description[0] for description in cur.description]
rows = cur.fetchall()
        
with open('no_reactive.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(column_names)
    formatted_rows = [[format_value(val) for val in row] for row in rows]
    writer.writerows(formatted_rows)

con.close()

