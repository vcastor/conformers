#!/usr/bin/python3
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("nucleo_data.db")
cursor = conn.cursor()

# # Set 0 to NULL values in paramters table
# cursor.execute("SELECT smiles, solvent, atom_analysed FROM parameters WHERE comment = 'notcomputed'")
# rows = cursor.fetchall()

# cursor.executemany(
#     "UPDATE parameters SET atom_analysed = 0, nconformers = 0 WHERE smiles = ? AND solvent = ? AND atom_analysed = ?",
#     rows
# )

# # Then [peculiar, reactive_msc] table does not need that systems
# tables = ["peculiar", "reactive_msc"]
# for table in tables:
#     cursor.executemany(
#         f"DELETE FROM {table} WHERE smiles = ? AND solvent = ? AND atom_analysed = ?",
#         rows
#     )

# # Update the parameters table if the system is in peculiar
# # peculiar = 0 means False, 1 means True and 2 means not computed
# cursor.execute("UPDATE parameters SET peculiar = 0 WHERE peculiar IS NULL")
# cursor.execute("UPDATE parameters SET peculiar = 2 WHERE comment = 'notcomputed'")
# cursor.execute("""
#     UPDATE parameters 
#     SET peculiar = 1 
#     WHERE EXISTS (
#         SELECT 1 FROM peculiar 
#         WHERE peculiar.smiles = parameters.smiles 
#         AND peculiar.solvent = parameters.solvent 
#         AND peculiar.atom_analysed = parameters.atom_analysed
#     )
# """)

# 3 means no_reactive
cursor.execute("SELECT smiles, solvent, atom_analysed FROM no_reactive")
for row in cursor.fetchall():
    cursor.execute(
        "UPDATE parameters SET peculiar = 3 WHERE smiles = ? AND solvent = ? AND atom_analysed = ?",
        row
    )

# Commit the changes and close the connection
conn.commit()
conn.close()

