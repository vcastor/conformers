#!/usr/bin/python3
import os
import sqlite3

# function to read the atomic information of the system
def atomic_reader(file, smiles, solvent, atomN):
    with open(file) as f:
        data = f.readlines()
    recordsmi, recordsol = False, False
    canonical, fukui, charges, condensed = False, False, False, False
    elepot_conlr, popq = False, False
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
            else:
                continue
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
            else:
                continue
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
            else:
                continue
        elif 'Condensed electrophilicity' in line:
            condensed = True
        elif '|   N ' in line and recordsmi and recordsol and condensed:
            if atomN == int(line.split()[0]):
                nline = line.split()
                atomic_descriptors.update({
                    'electrophilicity': float(nline[4]),
                    'nucleophilicity': float(nline[6])
                })
                condensed = False
            else:
                continue
        elif 'Electrostatic potential at the nuclei and Condensed linear' in line:
            elepot_conlr = True
        elif '|   N ' in line and recordsmi and recordsol and elepot_conlr:
            if atomN == int(line.split()[0]):
                nline = line.split()
                atomic_descriptors.update({
                    'electrostatic': float(nline[4]),
                    'condensed_lresponse': float(nline[6])
                })
                elepot_conlr = False
            else:
                continue
        elif 'QTAIM Population' in line:
            popq = True
        elif '|   N ' in line and recordsmi and recordsol and popq:
            if atomN == int(line.split()[0]):
                nline = line.split()
                atomic_descriptors.update({
                    'population': float(nline[4]),
                })
                popq = False
                break
            else:
                continue
    return atomic_descriptors

# function to read smiles and solvents
def solvent_reader(file):
    with open(file) as f:
        data = f.readlines()
    smiles, solvents, nconformers = [], [], []
    for line in data:
        if '===' in line:
            smiles.append(line.split()[1])
        elif '***' in line:
            solvents.append(line.split()[1])
        elif 'number_conformers' in line:
            nconformers.append(int(line.split()[1]))
    return smiles, solvents, nconformers

# function to read the global information of the system
def global_reader(smiles, solvent, nconf, file):
    with open(file) as f:
        data = f.readlines()
    gd = {}
    record, auxrecord, aux2record = False, False, False
    for line in data:
        if '===' in line and smiles in line:
            auxrecord = True
        elif '***' in line and solvent in line:
            aux2record = True
        elif '---' in line and (line.split()[1] == 'Average' or (nconf == 1 and line.split()[1] == 'Conformer')):
            record = auxrecord and aux2record
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
            break
    return gd

# Main script starts here 🚀

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

outdir = 'outputs'
global_query = '''
UPDATE {} SET
    mu = ?, eta = ?, softness = ?, hyperhardness = ?, omega = ?,
    nucleofuge = ?, electrofuge = ?, electrodonating = ?, electroaccepting = ?
WHERE smiles = ? AND solvent = ?
'''
atomic_query = '''
UPDATE {} SET
    fplus = ?, fminus = ?, fzero = ?, f2 = ?,
    sfplus = ?, sfminus = ?, sfzero = ?, s2 = ?,
    muplusfplus = ?, muminusfminus = ?,
    wfplus = ?, wf2 = ?,
    Sf2 = ?, s2f2 = ?,
    q_qtaim = ?, q_hirshfeld = ?,
    electro = ?, nucleo = ?,
    electrostatic_potential = ?, condensed_linear_response = ?,
    population = ?
WHERE smiles = ? AND solvent = ? AND atom_analysed = ?
'''

# Loop over the files in the directory [evrey file has a family]
for file in os.listdir(outdir):
    if not file.endswith('.out'):
        continue

    smiles_list, solvents, nconformers = solvent_reader(os.path.join(outdir, file))

    # Loop over the the smiles
    for smiles, solvent, nconf in zip(smiles_list, solvents, nconformers):

        # Get the table where the molecule is/are [it can be more than one]
        cur.execute('SELECT table_name, atom_analysed FROM parameters WHERE smiles = ? AND solvent = ?',
            (smiles, solvent))
        tables_atoms = cur.fetchall()

        # Global descriptors
        gd = global_reader(smiles, solvent, nconf, os.path.join(outdir, file))
        for table in set([table_name[0] for table_name in tables_atoms]):
            cur.execute(global_query.format(table), (
                gd['Electronic chemical potential'], gd['Hardness'], gd['Softness'], gd['Hyperhardness'],
                gd['Electrophilicity index'],
                gd['Nucleofuge'], gd['Electrofuge'], gd['Electrodonating'], gd['Electroaccepting'],
                smiles, solvent
            ))

        # Atomic descriptors
        for table, atom in tables_atoms:
            if atom == 0 or atom is None:
                continue
            atomic = atomic_reader(os.path.join(outdir, file), smiles, solvent, atom)
            cur.execute(atomic_query.format(table), (
                atomic['fplus'], atomic['fminus'], atomic['fzero'], atomic['f2'],
                atomic['sfplus'], atomic['sfminus'], atomic['sfzero'], atomic['s2'],
                atomic['muplusfplus'], atomic['muminusfminus'],
                atomic['wfplus'], atomic['wf2'],
                atomic['Sf2'], atomic['s2f2'],
                atomic['qtaimq'], atomic['hirshfeldq'],
                atomic['electrophilicity'], atomic['nucleophilicity'],
                atomic['electrostatic'], atomic['condensed_lresponse'],
                atomic['population'],
                smiles, solvent, atom
            ))

con.commit()
con.close()

