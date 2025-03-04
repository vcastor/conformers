#!/usr/bin/python3
import os
import sqlite3

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

# Catch all the smiles and solvents in the non_reactive_N table
cur.execute('SELECT smiles, solvent FROM non_reactive_N')
smiles_solvents = cur.fetchall()

# Loop over the smiles and solvents to call the values directly from the main table
for smiles, solvent in smiles_solvents:
    cur.execute('''SELECT mu, eta, softness, hyperhardness, omega, nucleofuge, electrofuge,
                   electrodonating, electroaccepting FROM main WHERE smiles = ? AND solvent = ?''', (smiles, solvent))
    global_values = cur.fetchall()
    # Update the values in the non_reactive_N table
    cur.execute('''UPDATE non_reactive_N SET
                    mu = ?, eta = ?, softness = ?, hyperhardness = ?, omega = ?,
                    nucleofuge = ?, electrofuge = ?, electrodonating = ?, electroaccepting = ?
                    WHERE smiles = ? AND solvent = ?''',
                (global_values[0][0], global_values[0][1], global_values[0][2], global_values[0][3], global_values[0][4],
                 global_values[0][5], global_values[0][6], global_values[0][7], global_values[0][8], smiles, solvent))

con.commit()
con.close()

