# -*- coding: UTF-8 -*-
# Database access of both cases: legacy and pipeline tables as DataFrames with the short column names
import json
import sqlite3
import pandas as pd

NUCLEO  = '../calculations/nucleo/nucleo_data.db'
ENTROPY = '../calculations/entropy/entropiesCOSMO.db'

NAMES = {'smile': 'smiles', 'molecule_name': 'name', 'atom_analysed': 'atom', 'nconformers': 'nconf',
         'experimental_N': 'Nexp', 'experimental_Sn': 'sN', 'experimental_S': 'Sexp', 'table_name': 'source',
         'raw_out': 'system', 'trans_S': 'St', 'rot_S': 'Sr', 'vib_S': 'Sv', 'correctionS': 'dSv',
         'hyperhardness': 'gamma', 'q_qtaim': 'q', 'q_hirshfeld': 'hirshfeld', 'electrostatic_potential': 'esp',
         'condensed_linear_response': 'chi', 'condensed_liner_response': 'chi', 'population': 'N',
         'q_qtaim_w': 'qw', 'condensed_linear_response_w': 'chiw'}

# labels of a site, kept next to any selection of columns
SITE = ['smiles', 'solvent', 'atom', 'name', 'family', 'stars', 'nconf', 'Nexp', 'sN', 'Sexp', 'epsilon', 'rad',
        'comment', 'source', 'system']

def tables(conn):
    """Lower-case names of the tables of a DB."""
    return [row[0].lower() for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]

def fields(conn, table):
    """Column names of a table."""
    return [row[1] for row in conn.execute(f'PRAGMA table_info({table})')]

def legacy(conn, table, source):
    """Sites of one source joined with the descriptors of its legacy table (reactive, no_reactive_msc, ...)."""
    # the plain, _msc or _ponderated copy, as table
    name        = source + next((s for s in ('_msc', '_ponderated') if table.endswith(s)), '')
    labels      = [c for c in fields(conn, 'parameters') if NAMES.get(c, c) in SITE]
    descriptors = [c for c in fields(conn, name) if NAMES.get(c, c) not in SITE]
    cols        = ['p.' + c for c in labels] + ['t.' + c for c in descriptors]
    return pd.read_sql_query(f'''
        SELECT {', '.join(cols)}
        FROM parameters p JOIN {name} t
          ON t.smiles = p.smiles AND t.solvent = p.solvent AND t.atom_analysed = p.atom_analysed
        WHERE p.table_name = ? AND (p.comment IS NULL OR p.comment != 'exclude')
    ''', conn, params=(source,))

def pipeline(conn, table, source):
    """Sites of one source with the molecular columns of table and the atomic columns of table + 'atoms'."""
    molecular = [c for c in fields(conn, table) if c not in ('smiles', 'solvent')]
    atomic    = [c for c in fields(conn, table + 'atoms') if c not in ('smiles', 'solvent', 'atom')]
    # nconf of the run, not of parameters
    labels    = [c for c in fields(conn, 'parameters') if NAMES.get(c, c) in SITE and NAMES.get(c, c) not in molecular]
    cols      = ['p.' + c for c in labels] + ['m.' + c for c in molecular] + ['a.' + c for c in atomic]
    return pd.read_sql_query(f'''
        SELECT {', '.join(cols)}
        FROM parameters p JOIN {table} m
          ON m.smiles = p.smiles AND m.solvent = p.solvent
        JOIN {table}atoms a
          ON a.smiles = p.smiles AND a.solvent = p.solvent AND a.atom = p.atom_analysed
        WHERE p.table_name = ? AND (p.comment IS NULL OR p.comment != 'exclude')
    ''', conn, params=(source,))

def liquids(conn, table):
    """Entropy table: a functional table as stored, or a pipeline table with name, Sexp, epsilon and rad of PBE0."""
    if 'smile' in fields(conn, table):
        return pd.read_sql_query(f'SELECT * FROM {table}', conn).drop(columns='id', errors='ignore')
    return pd.read_sql_query(f'''
        SELECT r.*, e.molecule_name, e.experimental_S, e.epsilon, e.rad
        FROM {table} r LEFT JOIN PBE0 e
          ON e.smile = r.smiles AND e.molecule_name = r.solvent
    ''', conn)

def load(db=NUCLEO, table='reactive', columns=None, sources=('reactive',)):
    """
    One DataFrame with the short names: the sites of sources with the descriptors of table, an entropy table,
    or a whole atoms table. Listed columns keep the labels, add P and Pf2 when absent, and drop rows with NaN.
    """
    conn    = sqlite3.connect(db)
    present = tables(conn)
    if table.endswith('atoms'):
        df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
    elif 'parameters' not in present:
        df = liquids(conn, table)
    elif (table + 'atoms').lower() in present:
        df = pd.concat([pipeline(conn, table, source) for source in sources], ignore_index=True)
    else:
        df = pd.concat([legacy(conn, table, source) for source in sources], ignore_index=True)
    conn.close()
    df = df.rename(columns=NAMES)
    if columns is None:
        return df
    columns = list(columns)
    if 'P' in columns and 'P' not in df:
        df['P'] = 1/df['gamma'].where(df['gamma'] != 0)
    if 'Pf2' in columns and 'Pf2' not in df:
        df['Pf2'] = df['f2']/df['gamma'].where(df['gamma'] != 0)
    labels = [c for c in SITE if c in df and c not in columns]
    return df[labels + columns].dropna(subset=columns).reset_index(drop=True)

def select(df, families=None, solvents=None, drop=()):
    """
    Rows of families and solvents (None keeps all) without the (smiles, Nexp) sites of drop, matched within 0.01.
    Returns a copy with a fresh 0..n-1 index.
    """
    keep = pd.Series(True, index=df.index)
    if families is not None:
        keep &= df['family'].isin(families)
    if solvents is not None:
        keep &= df['solvent'].isin(solvents)
    for smiles, n in drop:
        keep &= ~((df['smiles'] == smiles) & ((df['Nexp'] - n).abs() < 0.01))
    return df[keep].reset_index(drop=True)

def systems(db=NUCLEO, table='results'):
    """Prints the systems entry of a calculations config: the (smiles, solvent) of the DB without a row in table."""
    conn    = sqlite3.connect(db)
    present = tables(conn)
    if 'parameters' in present:
        rows = conn.execute('SELECT DISTINCT smiles, solvent FROM parameters').fetchall()
    else:
        rows = conn.execute('SELECT DISTINCT smile, molecule_name FROM PBE0 WHERE experimental_S IS NOT NULL').fetchall()
    done = set(conn.execute(f'SELECT smiles, solvent FROM {table}').fetchall()) if table.lower() in present else set()
    conn.close()
    lines = [json.dumps({'smiles': smiles, 'solvent': solvent}) for smiles, solvent in rows if (smiles, solvent) not in done]
    print('[' + ','.join('\n    ' + line for line in lines) + '\n]')
