# -*- coding: UTF-8 -*-
# Boltzmann weighted results in the database: one table for the molecules and
# one (table + 'atoms') for the atomic descriptors
import sqlite3
import numpy as np

KEYS    = {'molecules': ['smiles', 'solvent', 'natoms', 'nconf'],
           'atoms':     ['smiles', 'solvent', 'atom', 'element']}
GLOBAL  = ['mu', 'eta', 'softness', 'gamma', 'omega', 'nucleofuge', 'electrofuge', 'electrodonating', 'electroaccepting']
ENTROPY = ['St', 'Sr', 'Sv', 'dSv']
ATOMIC  = ['fplus', 'fminus', 'fzero', 'f2', 'sfplus', 'sfminus', 'sfzero', 's2',
          'muplusfplus', 'muminusfminus', 'wfplus', 'wf2', 'Sf2', 's2f2', 'electro', 'nucleo',
          'q', 'hirshfeld', 'esp', 'chi', 'N']

def columns(properties):
    """ Columns of the molecules and atoms tables """
    molecular, atomic = [], []
    if 'entropy' in properties:
        molecular = ENTROPY + ['mu', 'eta', 'gamma']
    if 'nucleophilicity' in properties:
        molecular += [col for col in GLOBAL + ['HOMO'] if col not in molecular]
        atomic = list(ATOMIC)
    return molecular, atomic

def create_tables(config):
    """
    Results tables, created or completed with the new columns before any calculation.
    """
    database = config['database']
    molecular, atomic = columns(config['properties'])
    tables = [(database['table'], KEYS['molecules'], molecular)]
    if atomic:
        tables.append((database['table'] + 'atoms', KEYS['atoms'], atomic))

    conn = sqlite3.connect(database['path'])
    for table, keys, cols in tables:
        types = ['TEXT' if key in ['smiles', 'solvent', 'element'] else 'INTEGER' for key in keys]
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(f'{k} {t}' for k, t in zip(keys, types))})")
        existing = [row[1] for row in conn.execute(f'PRAGMA table_info({table})')]
        if not set(keys) <= set(existing):
            raise ValueError(f"Table '{table}' already exists and it is not a results table")
        for col in cols:
            if col not in existing:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN {col} REAL')
    conn.commit()
    conn.close()

def store(molecules, config):
    """
    Boltzmann weighted results of one system, molecules: {property: molecule dictionary}.
    A previous row of the same system is replaced.
    """
    values = {}
    if 'entropy' in molecules:
        average = molecules['entropy']['average']
        values.update(zip(ENTROPY, [average['translational'], average['rotational'],
                                    average['vibrational'], average['correction']]))
        values.update(zip(['mu', 'eta', 'gamma'], average['cdftm']))
    if 'nucleophilicity' in molecules:
        average = molecules['nucleophilicity']['average']
        values.update(zip(GLOBAL, average['cdftm']))
        values['HOMO'] = average['orbitalE'][-1]

    molecule = next(iter(molecules.values()))
    system   = (molecule['smiles'], molecule['solvent'])

    conn  = sqlite3.connect(config['database']['path'])
    table = config['database']['table']
    conn.execute(f'DELETE FROM {table} WHERE smiles = ? AND solvent IS ?', system)
    names = KEYS['molecules'] + list(values)
    conn.execute(f"INSERT INTO {table} ({', '.join(names)}) VALUES ({', '.join('?'*len(names))})",
                 system + (molecule['number_atoms'], molecule['number_conformers']) + tuple(float(v) for v in values.values()))
    # Atoms of a previous run of the same system are deleted too
    table += 'atoms'
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? COLLATE NOCASE", (table,)).fetchone():
        conn.execute(f'DELETE FROM {table} WHERE smiles = ? AND solvent IS ?', system)
    if 'nucleophilicity' in molecules:
        names = KEYS['atoms'] + ATOMIC
        atomic = np.column_stack([average['cdfta'], average['fukui'], average['dual'], average['condensed'],
                                  average['qtaimcharge'], average['hirshfeld'], average['electrostatic'],
                                  average['condensed_linear'], average['population']])
        rows = [system + (i+1, element) + tuple(float(v) for v in atomic[i])
                for i, element in enumerate(molecule['atoms'])]
        conn.executemany(f"INSERT INTO {table} ({', '.join(names)}) VALUES ({', '.join('?'*len(names))})", rows)
    conn.commit()
    conn.close()

