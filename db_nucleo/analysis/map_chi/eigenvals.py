#!/usr/bin/python3
import os
import re
import sqlite3
import numpy as np

DB   = 'nucleo_data.db'
BASE = '/home/victoria/Documents/nucleo/plams'
BASE = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/analysis/map_chi'
SKIPPED = 'skipped_systems.txt'
NOHUP   = os.path.join(BASE, 'nohup.log')
INPUTS  = os.path.join(BASE, 'inputs')
SCRATCH = os.path.join(BASE, 'scratch_{}')

def scan_jobs():
    with open(NOHUP) as f:
        content = f.read()
    blocks = re.split(r'(?=PLAMS working folder:)', content)
    completed, skipped = [], []
    for b in blocks:
        if not b.startswith('PLAMS working folder:'):
            continue
        first_line, _, rest = b.partition('\n')
        njob = int(first_line.split('_')[-1].strip())
        if ('----------------------------------------------------' in rest
                or '==============Full traceback========================' in rest):
            skipped.append(njob)
        else:
            completed.append(njob)
    return completed, skipped

def read_input_out(nsystem):
    path = os.path.join(INPUTS, 'input_{}.out'.format(nsystem))
    with open(path) as f:
        lines = f.readlines()
    natoms      = int(lines[2].split()[-1])
    nconformers = int(lines[3].split()[-1])
    if nconformers == 1:
        weights = np.array([1.0])
    else:
        ws = []
        for line in lines:
            if 'Weight' in line:
                ws.append(float(line.split()[-1]))
        weights = np.array(ws)
    return natoms, weights

def smiles_solvent(nsystem):
    path = os.path.join(INPUTS, 'input_{}.out'.format(nsystem))
    with open(path) as f:
        lines = f.readlines()
    smiles  = lines[0].split()[1].strip()
    solvent = lines[1].split()[1].strip()
    return smiles, solvent

def read_out_file(path, natoms):
    header = 'CONDENSED LINEAR RESPONSE FUNCTION (MATRIX ELEMENTS)'
    grep   = 'grep -n "{}" {}'.format(header, path)
    matrix_start = int(os.popen(grep).read().strip().split(':')[0]) + 2
    matrix = np.zeros((natoms, natoms))
    with open(path) as f:
        lines = f.readlines()
    extra = 0
    for atom_idx in range(natoms):
        nvals    = atom_idx + 1
        block    = atom_idx//10
        row_start = matrix_start + atom_idx + extra
        vals = []
        for iblock in range(block+1):
            line = lines[row_start + iblock]
            if ':' in line:
                line = line.split(':', 1)[1]
            line = line.split()
            vals.extend([float(x) for x in line])
            if len(vals) >= nvals:
                break
        vals = vals[:nvals]
        matrix[atom_idx, :nvals] = vals
        matrix[:nvals, atom_idx] = vals
        extra += block
    return matrix

def score_path(njob, conf, out=True):
    if out:
        return os.path.join(SCRATCH.format(njob), 'SP_ADF',
                            'Score_{}'.format(conf), 'Score_{}.out'.format(conf))
    return os.path.join(SCRATCH.format(njob), 'SP_ADF',
                        'Score_{}'.format(conf), 'Score_{}.in'.format(conf))

def get_table_and_atom(cur, smiles, solvent):
    cur.execute("SELECT table_name FROM parameters WHERE smiles=? AND solvent=?",
                (smiles, solvent))
    table = cur.fetchone()[0]
    cur.execute("SELECT atom_analysed FROM {} WHERE smiles=? AND solvent=?".format(table),
                (smiles, solvent))
    atom = cur.fetchone()[0]
    return table, atom

def update_eigen(cur, table, smiles, solvent, eigen):
    cur.execute("UPDATE {} SET eigenchi=? WHERE smiles=? AND solvent=?".format(table),
                (eigen, smiles, solvent))

def write_skipped(skipped):
    with open(SKIPPED, 'w') as f:
        for njob in skipped:
            smiles, solvent = smiles_solvent(njob)
            f.write('{}\t{}\t{}\n'.format(njob, smiles, solvent))

def mapping_for_atom(eigenval, P, atom_idx):
    # atom_idx is 0-indexed here
    main_idx = np.argmax(P, axis=0)
    candidates = np.where(main_idx == atom_idx)[0]
    if candidates.size == 0:
        return 0, None, None
    # also return the min |eigenvalue| among the candidates (for the zero-mode check)
    vals = eigenval[candidates]
    min_abs = np.min(np.abs(vals))
    return candidates.size, np.mean(vals), min_abs

def analyse_mat(M, atom_analysed, natoms):
    w, V = np.linalg.eigh(M)
    print(w)
    P = V**2

    counts  = np.zeros(natoms, dtype=int)
    eigens  = [None]*natoms
    min_abs = np.full(natoms, np.inf)
    for atom in range(natoms):
        c, e, m = mapping_for_atom(w, P, atom)
        counts[atom] = c
        eigens[atom] = e
        if m is not None:
            min_abs[atom] = m

    unmapped = [a for a in range(natoms) if counts[a] == 0]
    print(unmapped)
    if len(unmapped) == 1:
        not_mapped = unmapped[0]
    elif len(unmapped) == 0:
        not_mapped = int(np.argmin(min_abs))
    else:
        not_mapped = min(unmapped, key=lambda a: min_abs[a])

    return eigens[atom_analysed], not_mapped

def atom_type(nsystem, atom):
    if atom is None:
        return None
    path = score_path(njob, 0, out=False)
    with open(path) as f:
        lines = f.readlines()
    print(atom)
    return lines[atom+1].split()[0]

# MAIN

# conn = sqlite3.connect(DB)
# cur  = conn.cursor()

# completed, skipped = scan_jobs()
# write_skipped(skipped)
completed = [12]

for njob in completed:
    natoms, weights  = read_input_out(njob)
    nconformers      = len(weights)
    # smiles, solvent  = smiles_solvent(njob)
    # table, atom_db   = get_table_and_atom(cur, smiles, solvent)
    atom_analysed    = 5-1

    eigen_per_conf   = np.zeros(nconformers)
    not_mapped_list  = []

    i = 0
    for conf in range(nconformers):
        M = read_out_file(score_path(njob, conf), natoms)
        eig, not_map = analyse_mat(M, atom_analysed, natoms)
        not_mapped_list.append(not_map)
        eigen_per_conf[i] = eig
        i += 1

    eigen_avg = float(np.sum(weights*eigen_per_conf))
    types = [atom_type(njob, a) for a in not_mapped_list]
    print('{}\teigen={:.6e}\tnot_mapped={}'.format(
        njob, eigen_avg, ','.join(types)))

# conn.commit()
# conn.close()

