#!/usr/bin/python3
import os
import sqlite3

# function to read the atomic information of the system
def atomic_reader(file, smiles, solvent, atomN):
    with open(file) as f:
        data = f.readlines()
    recordsmi, recordsol = False, False
    canonical, fukui, charges, condensed = False, False, False, False
    atomic_descriptors = {}
    for line in data:
        if '===' in line:
            recordsmi = True if smiles == line.split()[1] else False
        elif '***' in line and solvent in line:
            recordsol = True
        elif 'Canonical' in line:
            canonical = True
        elif '|   N ' in line and recordsmi and recordsol and canonical:
            if atomN == int(line.split()[0]):
                nline = line.split()
                atomic_descriptors.update({
                    'fplus': float(nline[4]),
                    'fminus': float(nline[6]),
                    'fzero': float(nline[8]),
                    'f2': float(nline[10]),
                    'sfplus': float(nline[12]),
                    'sfminus': float(nline[14]),
                    'sfzero': float(nline[16]),
                    's2': float(nline[18])
                })
                canonical = False
        elif 'Fukui' in line:
            fukui = True
        elif '|   N ' in line and recordsmi and recordsol and fukui:
            if atomN == int(line.split()[0]):
                nline = line.split()
                atomic_descriptors.update({
                    'muplusfplus': float(nline[4]),
                    'muminusfminus': float(nline[6]),
                    'wfplus': float(nline[8]),
                    'wf2': float(nline[10]),
                    'Sf2': float(nline[12]),
                    's2f2': float(nline[14])
                })
                fukui = False
        elif 'Charges' in line:
            charges = True
        elif '|   N ' in line and recordsmi and recordsol and charges:
            if atomN == int(line.split()[0]):
                nline = line.split()
                atomic_descriptors.update({
                    'qtaimq': float(nline[4]),
                    'hirshfeldq': float(nline[6])
                })
                charges = False
        elif 'Condensed' in line:
            condensed = True
        elif '|   N ' in line and recordsmi and recordsol and condensed:
            if atomN == int(line.split()[0]):
                nline = line.split()
                atomic_descriptors.update({
                    'electrophilicity': float(nline[4]),
                    'nucleophilicity': float(nline[6])
                })
                condensed = False
                break
    return atomic_descriptors

# function to read the global information of the system
def global_reader(file):
    with open(file) as f:
        data = f.readlines()
    smiles, solvents, ncoformers = [], [], []
    for line in data:
        if '===' in line:
            smiles.append(line.split()[1])
        elif '***' in line:
            solvents.append(line.split()[1])
        elif 'number_conformers' in line:
            ncoformers.append(int(line.split()[1]))
    return smiles, solvents, ncoformers

# Main script starts here 🚀

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

outdir = 'outputs'

# loop to read all the files in the directory
for file in os.listdir(outdir):
    if file.endswith('.out'):
        smiles, solvents, ncoformers = global_reader(os.path.join(outdir, file))
        for i in range(len(smiles)):
            if smiles[i].count('N') > 1:
                # get from the database the atom to be analysed
                cur.execute('SELECT atom_analysed FROM main WHERE smiles = ? AND solvent = ?', (smiles[i], solvents[i]))
                atomN = cur.fetchall()
                # some systems have more than one N atom to be analysed
                for atom_N in atomN:
                    if atom_N[0] == 0:
                        continue
                    atomic = atomic_reader(os.path.join(outdir, file), smiles[i], solvents[i], atom_N[0])
                    cur.execute('''UPDATE main SET
                                    fplus = ?, fminus = ?, fzero = ?, f2 = ?,
                                    sfplus = ?, sfminus = ?, sfzero = ?, s2 = ?,
                                    muplusfplus = ?, muminusfminus = ?,
                                    wfplus = ?, wf2 = ?,
                                    Sf2 = ?, s2f2 = ?,
                                    q_qtaim = ?, q_hirshfeld = ?,
                                    electro = ?, nucleo = ?
                                    WHERE smiles = ? AND solvent = ? AND atom_analysed = ?''',
                                (atomic['fplus'], atomic['fminus'], atomic['fzero'], atomic['f2'],
                                 atomic['sfplus'], atomic['sfminus'], atomic['sfzero'], atomic['s2'],
                                 atomic['muplusfplus'], atomic['muminusfminus'],
                                 atomic['wfplus'], atomic['wf2'],
                                 atomic['Sf2'], atomic['s2f2'],
                                 atomic['qtaimq'], atomic['hirshfeldq'],
                                 atomic['electrophilicity'], atomic['nucleophilicity'],
                                 smiles[i], solvents[i], atom_N[0]))

con.commit()
con.close()

