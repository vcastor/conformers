# data_loader.py
import sqlite3
import pandas as pd

FEATURES = [
    'mu', 'eta', 'softness', 'hyperhardness', 'omega', 'nucleofuge', 'electrofuge',
    'electrodonating', 'electroaccepting', 'fplus', 'fminus', 'fzero', 'f2',
    'sfplus', 'sfminus', 'sfzero', 's2', 'muplusfplus', 'muminusfminus', 'wfplus',
    'wf2', 'Sf2', 's2f2', 'nucleo', 'q_qtaim', 'electrostatic_potential',
    'condensed_linear_response', 'P', 'Pf2', 'HOMO', 'eigenchi',
    'q_qtaim_w', 'condensed_linear_response_w'
]


def fetch(db_file_path, features):

    key = ['smiles', 'molecule_name', 'solvent', 'atom_analysed', 'experimental_N', 'experimental_Sn']

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    cursor.execute(f'''
        SELECT {', '.join(key)}
        FROM parameters
        WHERE table_name = 'reactive'
          AND (comment IS NULL OR comment != 'exclude')
    ''')
    rows = cursor.fetchall()

    keys, X_data, y1_data, y2_data = [], [], [], []
    for smiles, name, solvent, atom, exp_N, exp_Sn in rows:
        cursor.execute(f'''
            SELECT {', '.join(features)}
            FROM reactive
            WHERE smiles = ? AND solvent = ? AND atom_analysed = ?
        ''', (smiles, solvent, atom))
        data = cursor.fetchone()
        if data is not None and all(value is not None for value in data):
            keys.append((smiles, name, solvent, atom))
            X_data.append(data)
            y1_data.append(exp_N)
            y2_data.append(exp_Sn)

    conn.close()

    return keys, X_data, y1_data, y2_data


def load_data(db_file_path, features=FEATURES):
    _, X_data, y1_data, y2_data = fetch(db_file_path, features)
    return pd.DataFrame(X_data, columns=features), pd.Series(y1_data, name='experimental_N'), pd.Series(y2_data, name='experimental_Sn')


def load_keys(db_file_path, features=FEATURES):
    keys, *_ = fetch(db_file_path, features)
    return pd.DataFrame(keys, columns=['smiles', 'name', 'solvent', 'atom'])


# per-model outliers (final_permodel.py 5 on the 242 sites): for each nine+solvent model tuned on the whole data set,
# sites with an out-of-fold error above 5 (5-fold CV repeated four times), removed and re-evaluated until none remains
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
# RF and GBR share the same eight sites; used by the scripts that evaluate these two models (grouped_check, family_models)
ERR5 = OUTLIERS['GBR']


def exclude(df, classes, ycol='N'):
    """classes: imidazolidinones (the four imidazolidin-4-one organocatalysts), hydrazines (the family),
    onestar (Mayr's one-star systems), err5 (the list above); needs the columns name, family, stars, smiles, ycol"""
    bad = set(classes)-{'imidazolidinones', 'hydrazines', 'onestar', 'err5'}
    if bad:
        raise ValueError(f'unknown exclusion classes {sorted(bad)}')
    if 'imidazolidinones' in classes:
        df = df[~df['name'].str.contains('imidazolidin-4-one')]
    if 'hydrazines' in classes:
        df = df[df['family'] != 'hydrazines_hydroxylamines_etc']
    if 'onestar' in classes:
        df = df[df['stars'] != 1]
    if 'err5' in classes:
        for smiles, n in ERR5:
            df = df[~((df['smiles'] == smiles) & ((df[ycol]-n).abs() < 0.01))]
    return df
