# -*- coding: UTF-8 -*-
import sqlite3
import pandas as pd

def update_tablename(table, case):
    if case == 'msc':
        table += '_msc'
    elif case == 'ponderated':
        table += '_ponderated'
    return table

# ==============================
# Connect to the database
def connect_fam(cols, case='conformers'):
    """
    Connect to the database and retrieve data for each table
    adding a 'source column to indicate its origin.
    """
    if not case in ['msc', 'peculiar', 'ponderated', 'conformers']:
        raise ValueError('Case must be either "msc", "peculiar", "ponderated" or "conformers".')

    conn = sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db')
    cursor = conn.cursor()

    params = ['smiles', 'solvent', 'atom_analysed', 'family', 'table_name']
    queryParams = f'''
    SELECT {', '.join(params)}
    FROM parameters
    WHERE nconformers > 0
      AND table_name = 'reactive'
      AND (comment != 'exclude' OR comment IS NULL)
    '''
    # AND table_name != 'no_reactive'
    cursor.execute(queryParams)
    params = cursor.fetchall()

    # Drop descriptors not present in every table we'll touch (e.g. eigenchi
    # in *_msc tables). Mirrors the safeguard in connect_db.
    needed_tables = {update_tablename(row[4], case) for row in params}
    missing = set()
    for tbl in needed_tables:
        cursor.execute(f"PRAGMA table_info({tbl})")
        existing = {info[1] for info in cursor.fetchall()}
        missing.update(c for c in cols if c not in existing)
    if missing:
        print(f"Skipping descriptors not present in all tables: {sorted(missing)}")
        cols[:] = [c for c in cols if c not in missing]

    all_data = []
    for smiles, solvent, atom, family, table in params:
        query = f'''
        SELECT {', '.join(cols)}
        FROM {update_tablename(table, case)}
        WHERE smiles = '{smiles}' AND solvent = '{solvent}' AND atom_analysed = '{atom}'
        '''
        cursor.execute(query)
        data = cursor.fetchone()

        df = pd.DataFrame([data], columns=cols)
        df['family'] = family
        all_data.append(df)

    conn.close()

    df_final = pd.concat(all_data, ignore_index=True)
    before = len(df_final)
    df_final = df_final.dropna(subset=cols).reset_index(drop=True)
    dropped = before - len(df_final)
    if dropped:
        print(f"Dropped {dropped} row(s) with NaN values in the selected descriptors")

    return df_final

