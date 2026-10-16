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

def compute_max_diff(file_path):
    with open(os.path.join(file_path)) as f:
        lines = f.readlines()
    vib_lines = [(i, line.split()[2]) for i, line in enumerate(lines) if "vibrational" in line][1:]
    if len(vib_lines) > 1:
        vib_values = [float(vib) for i, vib in vib_lines]
        max_diff = abs(max(vib_values) - min(vib_values))
    return max_diff

def outreader(fp):
    cmds = [
        "translational", "rotational", "vibrational", 
        "correction", "Electronic chemical potential", 
        "Hardness", "Hyperhardness"
    ]
    results = [os.popen(f'grep "{c}" {fp}').read().split('\n')[1:-1] for c in cmds]
    weights = os.popen(f'grep "Weight" {fp}').read().split('\n')[:-1]
    parsed_results = [list(map(lambda x: round(float(x.split()[-1]), 2), r)) for r in results]
    parsed_weights = list(map(lambda x: round(float(x.split()[-1]), 2), weights))
    return *parsed_results, parsed_weights

def readomega(workdir, molecule_name):
    fdir = 'PENTANOL' if molecule_name == 'Pentanol' else f'{molecule_name}'
    cmd = f'grep "Electrophilicity index" {workdir}/{fdir}/Fre*/Freq*out'
    lines = os.popen(cmd).read().split('\n')[:-1]
    omega = [round(float(line.split()[-1]), 2) for line in lines]
    return omega

# Connect to SQLite database
db_file_path = 'entropiesCOSMO.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Queries for training and testing data
base_query = '''
SELECT molecule_name, smile, epsilon, rad, experimental_S, nconformers
FROM {table} 
WHERE nconformers {condition}
'''

queries = {
    'pbe_testing_conformers': ('PBE', base_query.format(table='PBE', condition='> 1'), './pbe/output_files', '../work_dir'),
    'pbe0_testing_conformers': ('PBE0', base_query.format(table='PBE0', condition='> 1'), './pbe0/output_files', '../pbe0_work_dir')
}

for key, (table, query, directory, workdir) in queries.items():
    cursor.execute(query)
    valdata = cursor.fetchall()
    valdata = sorted(valdata, key=lambda x: x[4])
    with open(f'{key}.csv', 'w') as file:
        for row in valdata:
            fname = "PENTANOL.out" if row[0] == "Pentanol" else f'{row[0]}.out'
            fname = directory + '/' + fname
            max_diff = compute_max_diff(fname)
            st, sr, sv, grimme, mu, eta, gamma, weights = outreader(fname)
            omega = readomega(workdir, row[0])
            header = 'molecule_name; SMILES; Mw; nconformers; eps_r; radius; S_exp; DeltaS_v; '
            header += '; '.join([f'weight{i+1}' for i in range(row[-1])]) + '; '
            header += '; '.join([f'S_t{i+1}' for i in range(row[-1])]) + '; '
            header += '; '.join([f'S_r{i+1}' for i in range(row[-1])]) + '; '
            header += '; '.join([f'S_v{i+1}' for i in range(row[-1])]) + '; '
            header += '; '.join([f'DeltaGrimme{i+1}' for i in range(row[-1])]) + '\n'
            # header += '; '.join([f'mu{i+1}' for i in range(row[-1])]) + '; '
            # header += '; '.join([f'eta{i+1}' for i in range(row[-1])]) + '; '
            # header += '; '.join([f'gamma{i+1}' for i in range(row[-1])]) + '; '
            # header += '; '.join([f'omega{i+1}' for i in range(row[-1])]) + '\n'
            file.write(header)
            mweight = mol_mass(row[0])
            line = f'{row[0].lower()}; {row[1]}; {mweight:.2f}; {row[5]}; {row[2]}; {row[3]:.2f}; {row[4]:.2f}; {max_diff:.2f}; '
            line += '; '.join(map(str, weights)) + '; '
            line += '; '.join(map(str, st)) + '; '
            line += '; '.join(map(str, sr)) + '; '
            line += '; '.join(map(str, sv)) + '; '
            line += '; '.join(map(str, grimme)) + '\n'
            # line += '; '.join(map(str, mu)) + '; '
            # line += '; '.join(map(str, eta)) + '; '
            # line += '; '.join(map(str, gamma)) + '; '
            # line += '; '.join(map(str, omega)) + '\n'
            file.write(line)

# Commit the changes and close the connection
conn.commit()
conn.close()

