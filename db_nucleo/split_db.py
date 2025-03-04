#!/usr/bin/python3
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("nucleo_data.db")
cursor = conn.cursor()

# Create new tables if they do not exist
cursor.executescript("""
CREATE TABLE IF NOT EXISTS peculiar AS SELECT * FROM reactive WHERE 1=0;
CREATE TABLE IF NOT EXISTS peculiar_msc AS SELECT * FROM reactive_msc WHERE 1=0;
""")

# Copy data to peculiar
cursor.execute("""
INSERT INTO peculiar
SELECT * FROM reactive
WHERE nconformers IS NOT NULL
AND (
  comment LIKE "%&%"
  AND comment NOT LIKE "%[&]"
  OR smiles LIKE "%-%"
  OR smiles LIKE "%+%"
);
""")

# Copy system keys to peculiar_msc
cursor.execute("""
INSERT INTO peculiar_msc (smiles, solvent, atom_analysed)
SELECT smiles, solvent, atom_analysed FROM reactive
WHERE nconformers IS NOT NULL
AND (
  comment LIKE "%&%"
  AND comment NOT LIKE "%[&]"
  OR smiles LIKE "%-%"
  OR smiles LIKE "%+%"
);
""")

# Get the columns of peculiar_msc
cursor.execute("PRAGMA table_info(peculiar_msc);")
columns = [row[1] for row in cursor.fetchall() if row[1] not in ["smiles", "solvent", "atom_analysed"]]

# Update peculiar_msc with corresponding data from reactive_msc
for col in columns:
    cursor.execute(f"""
        UPDATE peculiar_msc
        SET {col} = (
            SELECT reactive_msc.{col}
            FROM reactive_msc
            WHERE reactive_msc.smiles = peculiar_msc.smiles
            AND reactive_msc.solvent = peculiar_msc.solvent
            AND reactive_msc.atom_analysed = peculiar_msc.atom_analysed
        )
        WHERE EXISTS (
            SELECT 1 FROM reactive_msc
            WHERE reactive_msc.smiles = peculiar_msc.smiles
            AND reactive_msc.solvent = peculiar_msc.solvent
            AND reactive_msc.atom_analysed = peculiar_msc.atom_analysed
        );
    """)

# Remove moved rows from reactive
cursor.execute("""
DELETE FROM reactive
WHERE nconformers IS NOT NULL
AND (
  comment LIKE "%&%"
  AND comment NOT LIKE "%[&]"
  OR smiles LIKE "%-%"
  OR smiles LIKE "%+%"
);
""")

# Remove moved rows from reactive_msc using peculiar_msc keys
cursor.execute("""
DELETE FROM reactive_msc
WHERE EXISTS (
  SELECT 1 FROM peculiar_msc
  WHERE reactive_msc.smiles = peculiar_msc.smiles
  AND reactive_msc.solvent = peculiar_msc.solvent
  AND reactive_msc.atom_analysed = peculiar_msc.atom_analysed
);
""")

# Copy data from reactive to peculiar [not computed systems]
cursor.execute("""
INSERT INTO peculiar
SELECT * FROM reactive
WHERE comment = "notcomputed";
""")

# Remove moved rows from reactive
cursor.execute("""
DELETE FROM reactive
WHERE comment = "notcomputed";
""")

# Commit the changes and close the connection
conn.commit()
conn.close()

