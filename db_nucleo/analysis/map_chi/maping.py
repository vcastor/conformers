#!/usr/bin/python3
import os
import sqlite3
import numpy as np

DIR_OUTS = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/adf_out"
DIR_XYZ  = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/xyz_conformers"
DB       = "/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db"

def get_natoms(xyz_path):
    with open(xyz_path) as f:
        return int(f.readline().strip())

def read_out_file(path, natoms):
    header = 'CONDENSED LINEAR RESPONSE FUNCTION (MATRIX ELEMENTS)'
    grep = 'grep -n "{}" {}'.format(header, path)
    matrix_start = int(os.popen(grep).read().strip().split(':')[0]) + 2
    matrix = np.zeros((natoms, natoms))
    with open(path) as f:
        lines = f.readlines()
    extra = 0
    for atom_idx in range(natoms):
        nvals = atom_idx + 1
        block = atom_idx//10
        row_start = matrix_start + atom_idx + extra
        vals = []
        for iblock in range(block + 1):
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

def fallback_eigen_for_atom(w, P, atom_idx):
    k = np.argmax(P[atom_idx, :])
    return w[k]

def mapping_for_atom(w, P, atom_idx):
    main_idx = np.argmax(P, axis=0)
    candidates = np.where(main_idx == atom_idx)[0]
    if candidates.size == 0:
        return 0, fallback_eigen_for_atom(w, P, atom_idx)
    return candidates.size, np.mean(w[candidates])

def analyse_mat(M, atom_analysed, natoms):
    w, V = np.linalg.eigh(M)
    P = V**2
    eigens = np.zeros(natoms)
    for atom in range(natoms):
        _, e = mapping_for_atom(w, P, atom)
        eigens[atom] = e
    return eigens[atom_analysed]

def get_targets(cur, smiles, solvent):
    cur.execute("SELECT table_name FROM parameters WHERE smiles=? AND solvent=?",
                (smiles, solvent))
    raw_tables = [row[0] for row in cur.fetchall()]
    targets = []
    for t in raw_tables:
        cur.execute("SELECT atom_analysed FROM {} WHERE smiles=? AND solvent=?".format(t),
                    (smiles, solvent))
        for row in cur.fetchall():
            targets.append((t, row[0]))
    return targets

def ensure_eigenchi_column(cur, table):
    cur.execute("PRAGMA table_info({})".format(table))
    cols = [info[1] for info in cur.fetchall()]
    if 'eigenchi' not in cols:
        cur.execute("ALTER TABLE {} ADD COLUMN eigenchi REAL".format(table))

# MAIN

conn = sqlite3.connect(DB)
cur  = conn.cursor()

cur.execute("SELECT DISTINCT smiles, solvent FROM parameters")
pairs = cur.fetchall()

for smiles, solvent in pairs:
    cur.execute("SELECT family, raw_out, nconformers FROM parameters WHERE smiles=? AND solvent=?",
                (smiles, solvent))
    fam, raw, nconf = cur.fetchone()

    fam_path = os.path.join(DIR_OUTS, fam)
    base     = 'system_{}_conformer_'.format(raw)
    xyz_path = os.path.join(DIR_XYZ, fam, base + '001.xyz')

    if not os.path.exists(xyz_path):
        continue

    if nconf > 1:
        files = []
        for i in range(1, nconf + 1):
            f = os.path.join(fam_path, base + str(i).zfill(3) + '.out')
            if os.path.exists(f):
                files.append(f)
    else:
        files = [os.path.join(fam_path, base + '001.out')]

    if not files:
        continue

    natoms = get_natoms(xyz_path)
    nconf  = len(files)

    targets = get_targets(cur, smiles, solvent)
    if not targets:
        continue

    eigen_per_conf = {key: np.zeros(nconf) for key in targets}

    for i, f in enumerate(files):
        M = read_out_file(f, natoms)
        w, V = np.linalg.eigh(M)
        P = V**2
        eigens = np.zeros(natoms)
        for atom in range(natoms):
            _, e = mapping_for_atom(w, P, atom)
            eigens[atom] = e
        for table, atom_db in targets:
            eigen_per_conf[(table, atom_db)][i] = eigens[atom_db - 1]

    for (table, atom_db), arr in eigen_per_conf.items():
        ensure_eigenchi_column(cur, table)
        eigen_avg = float(np.mean(arr))
        cur.execute(
            "UPDATE {} SET eigenchi=? WHERE smiles=? AND solvent=? AND atom_analysed=?".format(table),
            (eigen_avg, smiles, solvent, atom_db)
        )

conn.commit()
conn.close()

