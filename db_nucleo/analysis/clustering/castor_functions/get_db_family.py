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
def all_families(cols, case='conformers'):
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
      AND (comment != 'exclude' OR comment IS NULL)
    '''
    # AND table_name = 'reactive'
    # AND table_name != 'no_reactive'
    cursor.execute(queryParams)
    params = cursor.fetchall()

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

    return pd.concat(all_data, ignore_index=True)

