#!/usr/bin/python3
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("nucleo_data.db")
cursor = conn.cursor()

msc = ['', '_msc'] # most stable conformer

# get the systems where there are more than one conformer
cursor.execute("SELECT smiles, solvent, atom_analysed, table_name FROM parameters WHERE nconformers > 1")
for smiles, solvent, atom, table in cursor.fetchall():
    for m in msc:
        table_name = table + m
        # we reset all values to 0 except (smiles, solvent, atom_analysed)
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        remaining_columns = [c[1] for c in columns if c[1] not in ["smiles", "solvent", "atom_analysed"]]

        update_query = f"UPDATE {table_name} SET " + ", ".join(f"{col} = ?" for col in remaining_columns)
        update_query += " WHERE smiles = ? AND solvent = ? AND atom_analysed = ?"
        cursor.execute(update_query, [0]*len(remaining_columns) + [smiles, solvent, atom])

# Commit the changes and close the connection
conn.commit()
conn.close()

