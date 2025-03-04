#!/usr/bin/python3
import os
import sqlite3

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

# # Create the new table
# cur.execute('DROP TABLE IF EXISTS non_reactive_N')
# cur.execute('''
#     CREATE TABLE non_reactive_N (
#         smiles TEXT,
#         molecule_name TEXT,
#         solvent TEXT,
#         family TEXT,
#         stars INTEGER,
#         atom_analysed INTEGER,
#         nconformers INTEGER,
#         mu REAL,
#         eta REAL,
#         softness REAL,
#         hyperhardness REAL,
#         omega REAL,
#         nucleofuge REAL,
#         electrofuge REAL,
#         electrodonating REAL,
#         electroaccepting REAL,
#         fplus REAL,
#         fminus REAL,
#         fzero REAL,
#         f2 REAL,
#         sfplus REAL,
#         sfminus REAL,
#         sfzero REAL,
#         s2 REAL,
#         muplusfplus REAL,
#         muminusfminus REAL,
#         wfplus REAL,
#         wf2 REAL,
#         Sf2 REAL,
#         s2f2 REAL,
#         electro REAL,
#         nucleo REAL,
#         q_qtaim REAL,
#         q_hirshfeld REAL,
#         dipole REAL,
#         polarisability REAL
#     )
# ''')

# Select data from main for processing
cur.execute("SELECT smiles, molecule_name, solvent, family, stars, nconformers, comment FROM main")
rows = cur.fetchall()

# Insert data into the new table
for r in rows:
    smiles, molecule_name, solvent, family, stars, nconformers, comment = r
    nNitrogen = smiles.count('N') + smiles.count('n')

    if comment is None :
        comment = 'notknowncomment'

    if nNitrogen == 1 or comment == 'notcomputed':
        continue

    if comment == 'bothReact' or comment == 'symmetricN' or '&' in comment:
        nNitrogen -= 2
    else:
        nNitrogen -= 1

    if nNitrogen == 1:
        cur.execute("SELECT atom_analysed FROM main WHERE smiles = ? AND solvent = ?", (smiles, solvent))
        atom_analysed = cur.fetchall()
        atom_analysed = [x[0] for x in atom_analysed]
        # Look for the xyz file to know the other atom
        commentline = smiles + ' ' + solvent
        cmd = 'grep -rF "' + commentline + '" ./xyz_conformers'
        # Get the file name
        file = os.popen(cmd).read().split('\n')[0].split(':')[0]
        # Get the other atom
        cmd = 'grep -nF "N" ' + file
        nitlines = os.popen(cmd).read().split('\n')[1:] # line with the smiles
        nitlines = [x.split(':')[0] for x in nitlines if x]
        nitlines = [int(x) - 2 for x in nitlines] # the 2 lines xyz format
        # the one that is not the atom analysed
        nitlines = [x for x in nitlines if x not in atom_analysed]
        # if the list is emtpy continue
        if not nitlines:
            continue
        nonReact = nitlines[0]
        cur.execute("UPDATE non_reactive_N SET atom_analysed = ? WHERE smiles = ? AND solvent = ?",
            (nonReact, smiles, solvent))
    # else:
    #     for _ in range(nNitrogen):
    #         cur.execute("""
    #             UPDATE non_reactive_N SET (smiles, molecule_name, solvent, family, nconformers, stars)
    #             VALUES (?, ?, ?, ?, ?, ?)
    #         """, (smiles, molecule_name, solvent, family, nconformers, stars))

conn.commit()
conn.close()

