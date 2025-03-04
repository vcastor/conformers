# -*- coding: UTF-8 -*-
import sqlite3
import pandas as pd

# ==============================
# Connect to the database
def connect_db(exp, cols, dynamic=True):
    """
    if dynamic Flase just the most stable conformer
    """
    conn = sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db')
    cursor = conn.cursor()

    react_table = 'reactive' if dynamic else 'reactive_msc'
    non_react_table = 'no_reactive' if dynamic else 'no_reactive_msc'

    # New queries
    keys = ['smiles', 'solvent', 'atom_analysed']


    queryParams = f'''
    SELECT {", ".join(keys)}
    FROM parameters
    '''

    queryReact = f'''
    SELECT {", ".join(cols)}
    FROM {react_table}
    '''

    # Queries:
    queryReact = f'''
    SELECT {", ".join(exp)}, {", ".join(cols)} 
    FROM {react_table}
    WHERE nconformers IS NOT NULL
    AND (
      comment NOT LIKE "%&%"
      OR comment LIKE "%[&]"
      OR comment IS NULL
    )
    AND (
      smiles NOT LIKE "%-%"
      AND smiles NOT LIKE "%+%"
    )
    '''

    queryNoReac = f'SELECT {", ".join(cols)} FROM {non_react_table}'

    queryPeculiar = f'''
    SELECT {", ".join(exp)}, {", ".join(cols)} 
    FROM {react_table}
    WHERE nconformers IS NOT NULL
    AND comment LIKE "%&%"
    AND comment NOT LIKE "%[&]"
    OR smiles LIKE "%-%"
    OR smiles LIKE "%+%"
    '''

    cursor.execute(queryReact)
    reactive_data = cursor.fetchall()

    cursor.execute(queryPeculiar)
    peculiar_data = cursor.fetchall()

    cursor.execute(queryNoReac)
    non_reactive_data = cursor.fetchall()

    conn.close()

    # ==============================
    # Organize data into DataFrames
    reactive_df = pd.DataFrame(reactive_data, columns=exp+cols)
    peculiar_df = pd.DataFrame(peculiar_data, columns=exp+cols)
    noreactive_df = pd.DataFrame(non_reactive_data, columns=cols)

    # For non-reactive, define experimental values = 0
    noreactive_df[exp] = 0

    # Tag dataframes by source
    reactive_df['source'] = 'reactive'
    peculiar_df['source'] = 'peculiar'
    noreactive_df['source'] = 'non_reactive'

    # Combine into one DataFrame
    df = pd.concat([reactive_df, peculiar_df, noreactive_df], ignore_index=True)

    return df

