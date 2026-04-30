# data_loader.py
import sqlite3
import pandas as pd

def load_data(
    db_file_path,
    features = [
        'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
        'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
        'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
        'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'q_hirshfeld', 'electrostatic_potential',
        'condensed_linear_response', 'P', 'Pf2', 'HOMO'
    ]):

    key = ['smiles', 'solvent', 'atom_analysed', 'experimental_N', 'experimental_Sn']

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    cursor.execute(f'''
        SELECT {', '.join(key)}
        FROM parameters 
        WHERE table_name = 'reactive'
          AND (comment IS NULL OR comment != 'exclude')
    ''')
    rows = cursor.fetchall()

    X_data, y1_data, y2_data = [], [], []
    for smiles, solvent, atom, exp_N, exp_Sn in rows:
        cursor.execute(f'''
            SELECT {', '.join(features)}
            FROM reactive
            WHERE smiles = ? AND solvent = ? AND atom_analysed = ?
        ''', (smiles, solvent, atom))
        data = cursor.fetchone()
        if data is not None and all(value is not None for value in data):
            X_data.append(data)
            y1_data.append(exp_N)
            y2_data.append(exp_Sn)

    conn.close()

    return pd.DataFrame(X_data, columns=features), pd.Series(y1_data, name='experimental_N'), pd.Series(y2_data, name='experimental_Sn')

