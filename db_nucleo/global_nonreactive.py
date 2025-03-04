#!/usr/bin/python3
import sqlite3

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

# Copy values from main into non_reactive_N
cur.execute('''
UPDATE non_reactive_N
SET
    mu = (SELECT mu FROM main WHERE main.smiles = non_reactive_N.smiles AND main.solvent = non_reactive_N.solvent),
    eta = (SELECT eta FROM main WHERE main.smiles = non_reactive_N.smiles AND main.solvent = non_reactive_N.solvent),
    softness = (SELECT softness FROM main WHERE main.smiles = non_reactive_N.smiles AND main.solvent = non_reactive_N.solvent),
    hyperhardness = (SELECT hyperhardness FROM main WHERE main.smiles = non_reactive_N.smiles AND main.solvent = non_reactive_N.solvent),
    omega = (SELECT omega FROM main WHERE main.smiles = non_reactive_N.smiles AND main.solvent = non_reactive_N.solvent),
    nucleofuge = (SELECT nucleofuge FROM main WHERE main.smiles = non_reactive_N.smiles AND main.solvent = non_reactive_N.solvent),
    electrofuge = (SELECT electrofuge FROM main WHERE main.smiles = non_reactive_N.smiles AND main.solvent = non_reactive_N.solvent),
    electrodonating = (SELECT electrodonating FROM main WHERE main.smiles = non_reactive_N.smiles AND main.solvent = non_reactive_N.solvent),
    electroaccepting = (SELECT electroaccepting FROM main WHERE main.smiles = non_reactive_N.smiles AND main.solvent = non_reactive_N.solvent);
''')

conn.commit()
conn.close()

