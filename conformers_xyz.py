# -*- coding: UTF-8 -*-
# Sans la première ligne il n'est pas possible d'utiliser des caractères spéciaux (emojis ☺️ )
import os
import sys
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
    adf_SP_job = AMSJob.load_external(score_dirs[0])
    natoms = len(adf_SP_job.results.get_main_molecule())

    # Get the conformers.xyz file
    xyzfile = os.path.join(os.path.abspath(sp_dir), 'conformers.xyz')
    with open(xyzfile, 'r') as file:
        xyzraw = file.readlines()

    # Be sure the directory exists
    os.makedirs(os.path.join('xyz_conf', family), exist_ok=True)

    # Divide the xyzraw into conformers
    nstart, nend = 0, natoms + 2
    for conformer in range(nconfs):
        nlines = xyzraw[nstart:nend]
        # Update start and end indices for the next conformer
        nstart, nend = nstart + natoms + 2, nend + natoms + 2
        # Define the file name for the current conformer
        conf_num = str(conformer+1).zfill(3)
        file_xyz_nconf = f'system_{sys_count_num}_conformer_{conf_num}.xyz'
        file_xyz_nconf = os.path.join('xyz_conf', family, file_xyz_nconf)
        # Change the comment line with the smiles, solvent and weight of the conformer
        nlines[1] = f'{system["smiles"]} {system["solvent"]} {pops[conformer]:.4f}\n'
        # Open the file in write mode and write the selected lines
        with open(file_xyz_nconf, 'w') as f:
            f.write(''.join(nlines))

finish()

