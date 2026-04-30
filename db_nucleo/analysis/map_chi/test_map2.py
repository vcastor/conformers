#!/usr/bin/python3
import os
import re
import sqlite3
import numpy as np

DB   = 'nucleo_data.db'
BASE = '/home/victoria/Documents/nucleo/plams'
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

def score_path(njob, conf):
    return os.path.join(SCRATCH.format(njob), 'SP_ADF',
                        'Score_{}'.format(conf), 'Score_{}.out'.format(conf))

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

def analyse_mat(M, atom_analysed_0idx, natoms, zero_tol=1e-6):
    w, V = np.linalg.eigh(M)
    P = V**2

    counts   = np.zeros(natoms, dtype=int)
    eigens   = [None]*natoms
    min_abs  = np.full(natoms, np.inf)
    for atom in range(natoms):
        c, e, m = mapping_for_atom(w, P, atom)
        counts[atom] = c
        eigens[atom] = e
        if m is not None:
            min_abs[atom] = m

    # find the atom carrying the zero mode
    unmapped = [a for a in range(natoms) if counts[a] == 0]
    if len(unmapped) == 1:
        not_mapped = unmapped[0]
    elif len(unmapped) == 0:
        # no strict unmapped atom: pick the one whose smallest |eigenvalue|
        # is closest to zero (numerical zero mode)
        candidate = int(np.argmin(min_abs))
        not_mapped = candidate if min_abs[candidate] < zero_tol else None
    else:
        # several unmapped: pick the one with the largest P value on some
        # eigenvector near zero (the "hardest to avoid" zero-mode carrier)
        near_zero = np.where(np.abs(w) < zero_tol)[0]
        if near_zero.size == 0:
            near_zero = np.array([int(np.argmin(np.abs(w)))])
        best_atom, best_P = unmapped[0], -1.0
        for a in unmapped:
            pmax = np.max(P[a, near_zero])
            if pmax > best_P:
                best_P, best_atom = pmax, a
        not_mapped = best_atom

    return eigens[atom_analysed_0idx], not_mapped

def atom_type(nsystem, atom_0idx):
    path = os.path.join(INPUTS, 'input_{}.in'.format(nsystem))
    with open(path) as f:
        lines = f.readlines()
    return lines[atom_0idx+2].split()[0]

# MAIN

labels = np.array(["N1","C2","C3","N4","H5","H6","H7","H8"])
M = np.array([
    [-5.3687, 4.3690, 0.3117, 0.3464, 0.1608, 0.1597, 0.0105, 0.0105],
    [ 4.3690,-5.2985, 0.6279, 0.1882, 0.0547, 0.0556, 0.0015, 0.0014],
    [ 0.3117, 0.6279,-3.6383, 0.8862, 0.8603, 0.8578, 0.0474, 0.0469],
    [ 0.3464, 0.1882, 0.8862,-3.1928, 0.0887, 0.0881, 0.7991, 0.7961],
    [ 0.1608, 0.0547, 0.8603, 0.0887,-1.2593, 0.0506, 0.0042, 0.0401],
    [ 0.1597, 0.0556, 0.8578, 0.0881, 0.0506,-1.2564, 0.0403, 0.0043],
    [ 0.0105, 0.0015, 0.0474, 0.7991, 0.0042, 0.0403,-0.9430, 0.0399],
    [ 0.0105, 0.0014, 0.0469, 0.7961, 0.0401, 0.0043, 0.0399,-0.9392],
], dtype=float)

# conn = sqlite3.connect(DB)
# cur  = conn.cursor()

# completed, skipped = scan_jobs()
# write_skipped(skipped)

# for njob in completed:

natoms = len(labels)
atom_analysed    = 0

not_mapped_list  = []

eig, not_map = analyse_mat(M, atom_analysed, natoms)
# eigen_per_conf[conf] = eig if eig is not None else 0.0
# not_mapped_list.append(not_map)

print(eig)
print(not_map)



