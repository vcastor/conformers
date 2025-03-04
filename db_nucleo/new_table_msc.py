#!/usr/bin/python3
import os
import sqlite3

conn = sqlite3.connect('nucleo_data.db')
cur = conn.cursor()

old_tables = ['reactive', 'no_reactive']
new_tables = ['reactive_msc', 'no_reactive_msc']

# Create the new tables
for table in new_tables:
    cur.execute('DROP TABLE IF EXISTS ' + table)
    cur.execute(f'''
        CREATE TABLE {table} (
            smiles TEXT,
            solvent TEXT,
            atom_analysed INTEGER,
            mu REAL,
            eta REAL,
            softness REAL,
            hyperhardness REAL,
            omega REAL,
            nucleofuge REAL,
            electrofuge REAL,
            electrodonating REAL,
            electroaccepting REAL,
            fplus REAL,
            fminus REAL,
            fzero REAL,
            f2 REAL,
            sfplus REAL,
            sfminus REAL,
            sfzero REAL,
            s2 REAL,
            muplusfplus REAL,
            muminusfminus REAL,
            wfplus REAL,
            wf2 REAL,
            Sf2 REAL,
            s2f2 REAL,
            electro REAL,
            nucleo REAL,
            q_qtaim REAL,
            q_hirshfeld REAL,
            P REAL,
            Pf2 REAL
        )
    ''')

for i in range(len(old_tables)):
    # Select data from main for processing
    cur.execute(f'''
                SELECT smiles, solvent, nconformers, atom_analysed
                FROM {old_tables[i]}''')
    rows = cur.fetchall()

    # Insert data into the new table
    for r in rows:
        smiles, solvent, nconformers, atom_analysed = r

        cur.execute(f'''INSERT INTO {new_tables[i]} (smiles, solvent, atom_analysed) 
                      VALUES (?, ?, ?)''', (smiles, solvent, atom_analysed))

        # already the most stable conformer
        if nconformers == 1:
            cur.execute(f'''SELECT
                            mu, eta, softness, hyperhardness, omega, nucleofuge, electrofuge,
                            electrodonating, electroaccepting, fplus, fminus, fzero, f2,
                            sfplus, sfminus, sfzero, s2, muplusfplus, muminusfminus, wfplus,
                            wf2, Sf2, s2f2, electro, nucleo, q_qtaim, q_hirshfeld, P, Pf2
                        FROM {old_tables[i]} WHERE smiles = ? AND solvent = ? AND atom_analysed = ?''', (smiles, solvent, atom_analysed))
            descriptors = cur.fetchall()
            cur.execute(f'''UPDATE {new_tables[i]} SET
                            mu = ?, eta = ?, softness = ?, hyperhardness = ?, omega = ?, nucleofuge = ?, electrofuge = ?,
                            electrodonating = ?, electroaccepting = ?, fplus = ?, fminus = ?, fzero = ?, f2 = ?,
                            sfplus = ?, sfminus = ?, sfzero = ?, s2 = ?, muplusfplus = ?, muminusfminus = ?, wfplus = ?,
                            wf2 = ?, Sf2 = ?, s2f2 = ?, electro = ?, nucleo = ?, q_qtaim = ?, q_hirshfeld = ?,
                            P = ?, Pf2 = ?
                        WHERE smiles = ? AND solvent = ? AND atom_analysed = ?''', descriptors[0] + (smiles, solvent, atom_analysed))

conn.commit()
conn.close()

