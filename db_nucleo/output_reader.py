#!/usr/bin/python3
import os
import sqlite3

# function to read the atomic information of the system
def atomic_reader(file, smiles, solvent):
    with open(file) as f:
        data = f.readlines()
    record, recordsmi, recordsol = False, False, False
    canonical, fukui, charges, condensed = False, False, False, False
    atomic_descriptors = {}
    for line in data:
        if '===' in line:
            recordsmi = True if smiles == line.split()[1] else False
        if '***' in line and solvent in line:
            recordsol = True
        if 'Canonical' in line:
            canonical = True
        if '|   N ' in line and recordsmi and recordsol and canonical:
            nline = line.split()
            nitrogen_analysed = int(nline[0])
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
        if 'Fukui' in line:
            fukui = True
        if '|   N ' in line and recordsmi and recordsol and fukui:
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
        if 'Charges' in line:
            charges = True
        if '|   N ' in line and recordsmi and recordsol and charges:
            nline = line.split()
            atomic_descriptors.update({
                'qtaimq': float(nline[4]),
                'hirshfeldq': float(nline[6])
            })
            charges = False
        if 'Condensed' in line:
            condensed = True
        if '|   N ' in line and recordsmi and recordsol and condensed:
            nline = line.split()
            atomic_descriptors.update({
                'electrophilicity': float(nline[4]),
                'nucleophilicity': float(nline[6])
            })
            condensed = False
            break
    return nitrogen_analysed, atomic_descriptors

# function to read the global information of the system
def global_reader(file):
    with open(file) as f:
        data = f.readlines()
    smiles, solvents, nNitrogen, ncoformers, global_descriptors = [], [], [], [], []
    record, gd = False, {}
    for line in data:
        if '===' in line:
            smiles.append(line.split()[1])
            gd = {}
        elif '***' in line:
            solvents.append(line.split()[1])
        elif 'number_conformers' in line:
            ncoformers.append(int(line.split()[1]))
        elif '---' in line and (line.split()[1] == 'Average' or (ncoformers[-1] == 1 and line.split()[1] == 'Conformer')):
            record = True
        elif 'Electronic chemical potential' in line and record:
            key, value = line.split(':')
            gd[key.strip()] = float(value)
        elif 'Hardness' in line and record:
            key, value = line.split(':')
            gd[key.strip()] = float(value)
        elif 'Softness' in line and record:
            key, value = line.split(':')
            gd[key.strip()] = float(value)
        elif 'Hyperhardness' in line and record:
            key, value = line.split(':')
            gd[key.strip()] = float(value)
        elif 'Electrophilicity index' in line and record:
            key, value = line.split(':')
            gd[key.strip()] = float(value)
        elif 'Nucleofuge' in line and record:
            key, value = line.split(':')
            gd[key.strip()] = float(value)
        elif 'Electrofuge' in line and record:
            key, value = line.split(':')
            gd[key.strip()] = float(value)
        elif 'Electrodonating' in line and record:
            key, value = line.split(':')
            gd[key.strip()] = float(value)
        elif 'Electroaccepting' in line and record:
            key, value = line.split(':')
            gd[key.strip()] = float(value)
            global_descriptors.append(gd)
            record = False
    return smiles, solvents, ncoformers, global_descriptors

# Main script starts here 🚀

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

outdir = 'outputs'

# loop to read all the files in the directory
for file in os.listdir(outdir):
    if file.endswith('.out'):
        smiles, solvents, ncoformers, global_descriptors = global_reader(os.path.join(outdir, file))

        for i in range(len(smiles)):
            cur.execute('''UPDATE main SET
                            nconformers = ?,
                            mu = ?, eta = ?, softness = ?, hyperhardness = ?,
                            omega = ?,
                            nucleofuge = ?, electrofuge = ?,
                            electrodonating = ?, electroaccepting = ?
                            WHERE smiles = ? AND solvent = ?''',
                        (ncoformers[i],
                         global_descriptors[i]['Electronic chemical potential'],
                         global_descriptors[i]['Hardness'],
                         global_descriptors[i]['Softness'],
                         global_descriptors[i]['Hyperhardness'],
                         global_descriptors[i]['Electrophilicity index'],
                         global_descriptors[i]['Nucleofuge'],
                         global_descriptors[i]['Electrofuge'],
                         global_descriptors[i]['Electrodonating'],
                         global_descriptors[i]['Electroaccepting'],
                         smiles[i], solvents[i]))

            if smiles[i].count('N') == 1:
                atom_N, atomic = atomic_reader(os.path.join(outdir, file), smiles[i], solvents[i])
                cur.execute('''UPDATE main SET
                                atom_analysed = ?,
                                fplus = ?, fminus = ?, fzero = ?, f2 = ?,
                                sfplus = ?, sfminus = ?, sfzero = ?, s2 = ?,
                                muplusfplus = ?, muminusfminus = ?,
                                wfplus = ?, wf2 = ?,
                                Sf2 = ?, s2f2 = ?,
                                q_qtaim = ?, q_hirshfeld = ?,
                                electro = ?, nucleo = ?
                                WHERE smiles = ? AND solvent = ?''',
                            (atom_N,
                             atomic['fplus'], atomic['fminus'], atomic['fzero'], atomic['f2'],
                             atomic['sfplus'], atomic['sfminus'], atomic['sfzero'], atomic['s2'],
                             atomic['muplusfplus'], atomic['muminusfminus'],
                             atomic['wfplus'], atomic['wf2'],
                             atomic['Sf2'], atomic['s2f2'],
                             atomic['qtaimq'], atomic['hirshfeldq'],
                             atomic['electrophilicity'], atomic['nucleophilicity'],
                             smiles[i], solvents[i]))

con.commit()
con.close()

