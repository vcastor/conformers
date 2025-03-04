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
    # adf_SP_job = AMSJob.load_external(score_dirs[0])
    # natoms = len(adf_SP_job.results.get_main_molecule())
    natoms, atoms = get_atoms(system['smiles'])

    # Molecule dictionary
    molecule = {'smiles': system['smiles'],
                'solvent': system['solvent'],
                'number_atoms': natoms,
                'atoms': atoms,
                'number_conformers': nconfs,
                'average' : {},
                'conformers': {}}

    # Descriptor for each conformer
    for j, score in enumerate(score_dirs):
        conformer_data = descriptors(natoms, score, pops[j]) 
        for key in conformer_data:
            molecule['conformers'].setdefault(key, []).append(conformer_data[key])

    molecule['average'] = average_properties(molecule)

    system_results[(system['smiles'], system['solvent'])] = molecule

# plain text output
output_writer(system_results)

finish()

