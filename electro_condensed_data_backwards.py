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

# Get the order from the input files
input_file = get_input_file()

systems, user_settings = input_reader(input_file)
user_settings = validate_settings(user_settings)
family = os.path.basename(input_file).split('.')[0]

temperature = user_settings['temperature']

# Database connection
con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

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
    score_dirs = rkf_paths(os.path.abspath(conf_job.results.rkfpath()))

    # Obtain number of atoms
    adf_SP_job = AMSJob.load_external(score_dirs[0])
    natoms = len(adf_SP_job.results.get_main_molecule())

    # Molecule dictionary
    molecule = {'smiles': system['smiles'],
                'solvent': system['solvent'],
                'number_atoms': natoms,
                'number_conformers': nconfs,
                'average' : {},
                'conformers': {}}

    # Call the database
    cur.execute('SELECT atom_analysed FROM main WHERE smiles = ? AND solvent = ?', (system['smiles'], system['solvent']))
    atomN = cur.fetchall()

    # Descriptors and average for each conformer and N atom
    for atom_N in atomN:
        if atom_N[0] == 0:
            continue
        ele = sum(new_descriptors(natoms, s, atom_N[0])['electrostatic']*p for s, p in zip(score_dirs, pops))
        cond = sum(new_descriptors(natoms, s, atom_N[0])['condensed_linear']*p for s, p in zip(score_dirs, pops))
        cur.execute('''UPDATE main SET
                        electrostatic_potential = ?,
                        condensed_liner_response = ?
                        WHERE smiles = ? AND solvent = ? AND atom_analysed = ?''',
                        (ele, cond, system['smiles'], system['solvent'], atom_N[0]))

con.commit()
con.close()

finish()

