# -*- coding: UTF-8 -*-
# Sans la première ligne il n'est pas possible d'utiliser des caractères spéciaux (emojis ☺️ )
import os
import sys
import sqlite3
import numpy as np
from scm.plams import *
from scm.conformers import ConformersJob, ConformersResults
from lise_functions import * # local functions

#
# Main run of the script 🚀

init()

# Direct connection to the database
con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

# Get the order from the input files
input_file = get_input_file()

systems, user_settings = input_reader(input_file)
user_settings = validate_settings(user_settings)
family = os.path.basename(input_file).split('.')[0]

temperature = user_settings['temperature']
system_results = {}

# Main loop
sys_counter = 0
for system in systems:
    sys_counter += 1
    sys_count_num = str(sys_counter).zfill(3)
    sp_dir = 'SP_ADF.' + sys_count_num if sys_counter > 1 else 'SP_ADF'
    sp_dir = os.path.join('inputs', family, sp_dir)
    conf_job = ConformersJob.load_external(sp_dir)
    pops = np.array(conf_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    # As in the main filter,
    score_dirs = rkf_paths(os.path.abspath(conf_job.results.rkfpath()))[:nconfs]

    # Obtain number of atoms
    natoms, atoms = get_atoms(system['smiles'])

    # Get the atom analysed from the DB
    cur.execute(f'''
        SELECT atom_analysed, experimental_N, experimental_Sn
        FROM parameters
        WHERE smiles = "{system['smiles']}" AND solvent = "{system['solvent']}" AND table_name = "reactive"
    ''')
    for atom_analysed, expN, expSn in cur.fetchall():
        # Molecule dictionary
        molecule = {'expN': expN,
                    'expSn': expSn,
                    'atom_analysed': atom_analysed,
                    'number_atoms': natoms,
                    'number_conformers': nconfs,
                    'average' : {},
                    'conformers': {}}
        # Get the descriptors ONLY for the most stable conformer
        msc_data = ponderated(descriptors(natoms, score_dirs[0], pops[0]), atom_analysed)
        molecule['average'] = msc_data
        # for key in msc_data:
        #     molecule['average'].setdefault(key, []).append(msc_data[key])
        
        system_results[(system['smiles'], system['solvent'], atom_analysed)] = molecule

# plain text output
pond_output(system_results)

finish()

