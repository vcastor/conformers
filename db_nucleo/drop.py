#!/usr/bin/python3
import sqlite3

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

# List of tables and columns to remove
tables_columns = {
    "reactive": ["epsilon", "rad"],
    "peculiar": ["epsilon", "rad"],
    "no_reactive": ["epsilon", "rad"],
}

# Function to drop columns
def drop_columns(cursor, table, columns):
    cursor.execute(f"PRAGMA table_info({table})")
    columns_info = cur.fetchall()
    remaining_columns = [col[1] for col in columns_info if col[1] not in columns]

    if remaining_columns:
        columns_str = ", ".join(remaining_columns)
        cur.execute(f"CREATE TABLE {table}_new AS SELECT {columns_str} FROM {table}")
        cur.execute(f"DROP TABLE {table}")
        cur.execute(f"ALTER TABLE {table}_new RENAME TO {table}")

# Execute the column removal for each table
for table, columns in tables_columns.items():
    drop_columns(cur, table, columns)

con.commit()
con.close()

