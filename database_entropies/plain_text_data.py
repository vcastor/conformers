#!/usr/bin/python3
import os
import sqlite3
from molmass import Formula

def mol_mass(mol_name):
    mol_name = mol_name.replace('\'', '')
    cases = [mol_name, mol_name.capitalize(), mol_name.upper(), mol_name.lower()]
    for name in cases:
        path = os.path.join('..', 'work_dir', name, 'reoptimize_ADF', 'conformers.xyz')
        if os.path.exists(path):
            with open(path) as f:
                lines = f.readlines()
            formula = lines[1].split()[-1]
            return Formula(formula).mass

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Queries for training and testing data
base_query = '''
SELECT molecule_name, smile, epsilon, rad, experimental_S, 
       trans_S, rot_S, vib_S, correctionS, mu, eta, gamma, omega
FROM {table} 
WHERE nconformers {condition}
'''

queries = {
    'pbe_training': ('PBE', base_query.format(table='PBE', condition='= 1'), './pbe/output_files'),
    'pbe_testing': ('PBE', base_query.format(table='PBE', condition='> 1'), './pbe/output_files'),
    'pbe0_training': ('PBE0', base_query.format(table='PBE0', condition='= 1'), './pbe0/output_files'),
    'pbe0_testing': ('PBE0', base_query.format(table='PBE0', condition='> 1'), './pbe0/output_files')
}

def compute_max_diff(file_path):
    with open(os.path.join(file_path)) as f:
        lines = f.readlines()
    vib_lines = [(i, line.split()[2]) for i, line in enumerate(lines) if "vibrational" in line][1:]
    if len(vib_lines) > 1:
        vib_values = [float(vib) for i, vib in vib_lines]
        max_diff = abs(max(vib_values) - min(vib_values))
    return max_diff

for key, (table, query, directory) in queries.items():
    cursor.execute(query)
    valdata = cursor.fetchall()
    valdata = sorted(valdata, key=lambda x: x[4])
    with open(f'{key}.csv', 'w') as file:
        is_testing = 'testing' in key
        if is_testing:
            file.write('molecule_name; SMILES; Mw; eps_r; radius; S_exp; S_t; S_r; S_v; DeltaGrimme; DeltaS_v\n')
            for row in valdata:
                fname = "2,2-Dimethylbiphenyl.out" if row[0] == "2,2'-Dimethylbiphenyl" else f'{row[0]}.out'
                fname = "PENTANOL.out" if row[0] == "Pentanol" else fname
                max_diff = compute_max_diff(os.path.join(directory, fname))
                mweight = mol_mass(row[0])
                file.write(f'{row[0].lower()}; {row[1]}; {mweight:.2f}; {row[2]}; {row[3]:.2f}; {row[4]:.2f}; {row[5]:.2f}; {row[6]:.2f}; {row[7]:.2f}; {row[8]:.2f}; {max_diff:.2f}\n')
        else:
            file.write('molecule_name; SMILES; Mw; eps_r; radius; S_exp; S_t; S_r; S_v; DeltaGrimme\n')
            for row in valdata:
                mweight = mol_mass(row[0])
                file.write(f'{row[0].lower()}; {row[1]}; {mweight:.2f}; {row[2]}; {row[3]:.2f}; {row[4]:.2f}; {row[5]:.2f}; {row[6]:.2f}; {row[7]:.2f}; {row[8]:.2f}\n')

# Commit the changes and close the connection
conn.commit()
conn.close()

