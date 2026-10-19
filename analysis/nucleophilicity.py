# -*- coding: UTF-8 -*-
# Nucleophilicity: paper ML settings, neighbour data, decay search, χ^λ(N) and the Mayr scrape
import io
import os
import itertools
import contextlib
import numpy as np
import pandas as pd
from fits import damped
from svm import scan

NINE     = ['electrofuge', 'q', 'muplusfplus', 'chi', 'HOMO', 'wfplus', 'qw', 'sfplus', 'eigenchi']
SOLVENT  = ['epsilon', 'rad']
FEATURES = ['mu', 'eta', 'softness', 'gamma', 'omega', 'nucleofuge', 'electrofuge',
            'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
            'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
            'wf2', 'Sf2', 's2f2', 'nucleo', 'q', 'esp', 'chi', 'P', 'Pf2', 'HOMO', 'eigenchi', 'qw', 'chiw']

# final_tuned.py 0 30 none: tuned on the whole set of 242 sites
WHOLE = {
    'RF': {'max_depth': 80, 'max_features': 'sqrt', 'criterion': 'absolute_error', 'n_estimators': 162,
           'min_samples_split': 2, 'min_samples_leaf': 1, 'bootstrap': False},
    'GBR': {'n_estimators': 2693, 'learning_rate': 0.02390655641840526, 'max_depth': 9, 'min_samples_split': 13,
            'min_samples_leaf': 1, 'subsample': 0.610964722075092, 'max_features': 'log2', 'loss': 'absolute_error'},
    'SVR': {'kernel': 'rbf', 'C': 8.402036669106579, 'epsilon': 0.23373383539864973, 'gamma': 'scale'},
    'GPR': {'kernel': 'matern52', 'restarts': 15},
}

# final_permodel.py 5: each model retuned on its own 234 sites
FINAL = {
    'RF': {'max_depth': None, 'max_features': 0.3, 'criterion': 'squared_error', 'n_estimators': 175,
           'min_samples_split': 5, 'min_samples_leaf': 1, 'bootstrap': False},
    'GBR': {'n_estimators': 4201, 'learning_rate': 0.011824982093283917, 'max_depth': 11, 'min_samples_split': 11,
            'min_samples_leaf': 3, 'subsample': 0.46435577260052796, 'max_features': 'sqrt', 'loss': 'huber'},
    'SVR': {'kernel': 'rbf', 'C': 7.961519772308445, 'epsilon': 0.1420968483707335, 'gamma': 'scale'},
    'GPR': {'kernel': 'matern32', 'restarts': 15},
}

# final_permodel.py 5: sites removed per model (out-of-fold error above 5, iterated)
OUTLIERS = {
    'RF': [
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@@H](C3=CC=C(C)O3)N1C', 7.39),
        (r'[H]/C([H])=N\N(C)C', 19.31),
        ('CN(C)N', 22.41),
        ('C1(C(C2=CC=CC=C2)(C3=CC=CC=C3)C4=CC=CC=C4)NCCC1', 9.16),
        ('[C@H]1(CN2C=NC=C2)NCCC1', 15.55),
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@H](C(C)(C)C)N1C', 5.44),
        ('O=C1[C@H](CC2=CC=CC=C2)NC(C)(C)N1C', 6.04),
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@H](C3=CC=C(C)O3)N1C', 8.76),
    ],
    'GBR': [
        ('[C@H]1(CN2C=NC=C2)NCCC1', 15.55),
        (r'[H]/C([H])=N\N(C)C', 19.31),
        ('C1(C(C2=CC=CC=C2)(C3=CC=CC=C3)C4=CC=CC=C4)NCCC1', 9.16),
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@@H](C3=CC=C(C)O3)N1C', 7.39),
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@H](C(C)(C)C)N1C', 5.44),
        ('CN(C)N', 22.41),
        ('O=C1[C@H](CC2=CC=CC=C2)NC(C)(C)N1C', 6.04),
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@H](C3=CC=C(C)O3)N1C', 8.76),
    ],
    'SVR': [
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@H](C(C)(C)C)N1C', 5.44),
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@@H](C3=CC=C(C)O3)N1C', 7.39),
        ('O=C1[C@H](CC2=CC=CC=C2)NC(C)(C)N1C', 6.04),
        ('CN(C)N', 11.72),
        (r'[H]/C([H])=N\N(C)C', 19.31),
        ('C1(C(C2=CC=CC=C2)(C3=CC=CC=C3)C4=CC=CC=C4)NCCC1', 9.16),
        ('CN(C)C', 23.05),
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@H](C3=CC=C(C)O3)N1C', 8.76),
    ],
    'GPR': [
        ('CN(C)N', 22.41),
        (r'[H]/C([H])=N\N(C)C', 19.31),
        ('C1(C(C2=CC=CC=C2)(C3=CC=CC=C3)C4=CC=CC=C4)NCCC1', 9.16),
        ('[C@H]1(CN2C=NC=C2)NCCC1', 15.55),
        ('O=C1[C@H](CC2=CC=CC=C2)NC(C)(C)N1C', 6.04),
        ('O=C1[C@H](CC2=CC=CC=C2)N[C@H](C(C)(C)C)N1C', 5.44),
        ('CN1C2=CC=CC=C2N=N1', 7.77),
        ('n1c2ccccc2[nH]n1', 7.69),
    ],
}

MAYR = {'C': 10, 'H': 34, 'O': 50, 'N': 40}

def geometries(xyzdir):
    """{(smiles, solvent): [(path relative to xyzdir, weight, coordinates)]} of the .xyz files under xyzdir."""
    found = {}
    for root, dirs, names in os.walk(xyzdir):
        dirs.sort()
        for name in sorted(names):
            if not name.endswith('.xyz'):
                continue
            path = os.path.join(root, name)
            with open(path) as f:
                lines = f.readlines()
            natoms  = int(lines[0])
            comment = lines[1].split()
            if len(comment) < 3:
                continue
            xyz = np.array([line.split()[1:4] for line in lines[2:2 + natoms]], dtype=float)
            key = (comment[0], ' '.join(comment[1:-1]))
            found.setdefault(key, []).append((os.path.relpath(path, xyzdir), float(comment[-1]), xyz))
    return found

def chimatrix(path, natoms):
    """Symmetric condensed linear response matrix from the lower triangle of an ADF output."""
    header = 'CONDENSED LINEAR RESPONSE FUNCTION (MATRIX ELEMENTS)'
    with open(path, encoding='ISO-8859-1') as f:
        lines = f.readlines()
    matrix_start = next(i for i, line in enumerate(lines) if header in line) + 3
    matrix       = np.zeros((natoms, natoms))
    extra        = 0
    for atom_idx in range(natoms):
        nvals     = atom_idx + 1
        block     = atom_idx//10
        row_start = matrix_start + atom_idx + extra
        vals      = []
        for iblock in range(block + 1):
            line = lines[row_start + iblock]
            if ':' in line:
                line = line.split(':', 1)[1]
            line = line.split()
            vals.extend([float(x) for x in line])
            if len(vals) >= nvals:
                break
        vals                     = vals[:nvals]
        matrix[atom_idx, :nvals] = vals
        matrix[:nvals, atom_idx] = vals
        extra += block
    return matrix

def neighbours(df, atoms, xyzdir):
    """
    Adds nb to the sites with geometry and atoms: Boltzmann weights 'w' (nconf), distances 'd' (nconf × natoms)
    to the analysed atom and the per-atom values of every column of atoms (load(db, 'resultsatoms')).
    """
    found  = geometries(xyzdir)
    values = {key: group.set_index('atom') for key, group in atoms.groupby(['smiles', 'solvent'])}
    keep   = []
    nb     = []
    for i, site in df.iterrows():
        key = (site.smiles, site.solvent)
        if key not in found or key not in values:
            continue
        w     = np.array([weight for _, weight, _ in found[key]])
        xyz   = [coords for *_, coords in found[key]]
        atom  = int(site.atom) - 1
        group = values[key].reindex(range(1, len(xyz[0]) + 1))
        data  = {'w': w/w.sum(), 'd': np.array([np.linalg.norm(c - c[atom], axis=1) for c in xyz])}
        data.update({col: group[col].to_numpy() for col in group.columns if col not in ('smiles', 'solvent')})
        keep.append(i)
        nb.append(data)
    out       = df.loc[keep].copy()
    out['nb'] = pd.Series(nb, index=keep, dtype=object)
    return out

def decay(df, y, columns=('q', 'chi')):
    """
    Decay k (50 points, 0.01 to 4) of every column in nb, damped as Σ exp(-k·d)·x; each grid point is scored
    by the 20-seed test accuracy of an RBF SVC on the two standardised features. Returns {column: k}.
    """
    grid   = np.linspace(0.01, 4, 50)
    nb     = df.nb.iloc[0]
    names  = [c + 'w' if c in nb else c for c in columns]
    series = {c: {k: damped(df, c, k) for k in grid} for c in columns if c in nb}
    frame  = df[[c for c in columns if c not in nb]].copy()
    scores = []
    for ks in itertools.product(*[grid if c in nb else [None] for c in columns]):
        for c, name, k in zip(columns, names, ks):
            if k is not None:
                frame[name] = series[c][k]
        with contextlib.redirect_stdout(io.StringIO()):
            mean, std, insample, _ = scan(frame, [tuple(names)], y)[0]
        scores.append((mean, std, insample, ks))
    scores.sort(key=lambda s: -s[0])
    for mean, std, insample, ks in scores[:5]:
        decays = '  '.join(f'k({c}) {k:.3f}' for c, k in zip(columns, ks) if k is not None)
        print(f'{decays}   test {100*mean:.1f} ± {100*std:.1f} %   in-sample {100*insample:.1f} %')
    return {c: k for c, k in zip(columns, scores[0][3]) if k is not None}

def eigenchi(df, xyzdir='../calculations/nucleo/xyz_conformers', outdir='../calculations/nucleo/adf_out'):
    """
    χ^λ(N) of every site: each eigenvalue of χ_AB goes to the atom with the largest squared component (zero mode
    excluded), conformers Boltzmann-averaged with the xyz weights. Returns a Series.
    """
    found  = geometries(xyzdir)
    cache  = {}
    value  = pd.Series(np.nan, index=df.index)
    counts = {1: 0, 2: 0, 3: 0}
    for i, site in df.iterrows():
        atom    = int(site.atom) - 1
        weights = []
        values  = []
        cases   = []
        for path, weight, xyz in found.get((site.smiles, site.solvent), []):
            out = os.path.join(outdir, os.path.splitext(path)[0] + '.out')
            if not os.path.exists(out):
                continue
            if out not in cache:
                w, V       = np.linalg.eigh(chimatrix(out, len(xyz)))
                cache[out] = (w, V**2)
            w, P = cache[out]
            # the uniform eigenvector (sum rule) has a null eigenvalue
            nonzero = np.abs(w) > 1e-3
            modes   = np.where((np.argmax(P, axis=0) == atom) & nonzero)[0]
            if modes.size:
                cases.append(1 if modes.size == 1 else 2)
                values.append(np.mean(w[modes]))
            else:
                cases.append(3)
                values.append(w[np.argmax(np.where(nonzero, P[atom], -1.0))])
            weights.append(weight)
        if values:
            value[i] = np.dot(weights, values)/np.sum(weights)
            counts[max(set(cases), key=cases.count)] += 1
    n = sum(counts.values())
    print(f'{n} sites: case 1 (one eigenvector dominated by the analysed atom) {counts[1]}, case 2 (several) '
          f'{counts[2]}, case 3 (none, fallback) {counts[3]}; {len(df) - n} without outputs')
    return value

def mayr():
    """Nexp, sN and atom of the C, H, O and N nucleophiles of the Mayr reactivity database."""
    import requests
    from bs4 import BeautifulSoup
    frames = []
    for atom, number in MAYR.items():
        url    = f'https://www.cup.lmu.de/oc/mayr/reaktionsdatenbank2/fe/showclass/{number}?num=10000&page=1'
        soup   = BeautifulSoup(requests.get(url).text, 'html.parser')
        params = [float(tag.strip().split(':')[1]) for tag in soup.find_all(string=True) if 'Param.' in tag.strip()]
        frames.append(pd.DataFrame({'Nexp': params[0::2], 'sN': params[1::2], 'atom': atom}))
    return pd.concat(frames, ignore_index=True)
