#!/usr/bin/python3
import sqlite3

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

cur.execute('''CREATE TABLE main(
    smiles TEXT,
    molecule_name TEXT,
    solvent TEXT,
    family TEXT,
    star INTEGER,
    atom_analysed INTEGER,
    experimental_N REAL,
    experimental_Sn REAL,
    nconformers INTEGER,
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
    dipole REAL,
    polarisability REAL
)''')

con.commit()
con.close()

