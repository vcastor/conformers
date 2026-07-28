# -*- coding: UTF-8 -*-
import sqlite3
import pandas as pd

# ==============================
# Update table names
def update_tablename(table, case):
    if case == 'msc':
        table += '_msc'
    elif case == 'ponderated':
        table += '_ponderated'
    return table

# ==============================
# Connect to the database
def connect_db(exp, cols, case='conformers'):
    """
    Connect to the database and retrieve data for each table
    adding a 'source column to indicate its origin.

    Descriptors not present in every table we query are dropped from `cols`
    in place (so callers keep working with a consistent list of features),
    and rows with NaN values in any remaining descriptor are removed.
    """
    if not case in ['msc', 'peculiar', 'ponderated', 'conformers']:
        raise ValueError('Case must be either "msc", "peculiar", "ponderated" or "conformers".')

    conn = sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db')
    cursor = conn.cursor()

    params_select = ['smiles', 'solvent', 'atom_analysed', 'table_name'] + exp
    queryParams = f'''
    SELECT {', '.join(params_select)}
    FROM parameters
    WHERE nconformers > 0 AND (comment IS NULL OR comment != 'exclude')
    '''
    cursor.execute(queryParams)
    params = cursor.fetchall()

    # Drop descriptors that don't exist in every table we'll touch (e.g. eigenchi
    # in *_msc tables). When all tables eventually expose every descriptor this
    # block becomes a no-op.
    needed_tables = {update_tablename(row[3], case) for row in params}
    missing = set()
    for tbl in needed_tables:
        cursor.execute(f"PRAGMA table_info({tbl})")
        existing = {info[1] for info in cursor.fetchall()}
        missing.update(c for c in cols if c not in existing)
    if missing:
        print(f"Skipping descriptors not present in all tables: {sorted(missing)}")
        cols[:] = [c for c in cols if c not in missing]

    all_data = []
    for smiles, solvent, atom, table, expN, expSn in params:
        query = f'''
        SELECT {', '.join(cols)}
        FROM {update_tablename(table, case)}
        WHERE smiles = '{smiles}' AND solvent = '{solvent}' AND atom_analysed = '{atom}'
        '''
        cursor.execute(query)
        data = cursor.fetchone()

        df = pd.DataFrame([data], columns=cols)
        df['smiles'] = smiles
        df['solvent'] = solvent
        df['atom_analysed'] = atom
        df['source'] = table
        df['experimental_N'] = expN
        df['experimental_Sn'] = expSn
        all_data.append(df)

    conn.close()

    df_final = pd.concat(all_data, ignore_index=True)
    before = len(df_final)
    df_final = df_final.dropna(subset=cols).reset_index(drop=True)
    dropped = before - len(df_final)
    if dropped:
        print(f"Dropped {dropped} row(s) with NaN values in the selected descriptors")

    return df_final

