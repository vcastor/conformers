# -*- coding: UTF-8 -*-
# Sans la première ligne il n'est pas possible d'utiliser des caractères spéciaux (emojis ☺️ )
from scm.plams import *
from scm.conformers import ConformersJob, ConformersResults
import os
import sys
import numpy as np
from lise_functions import * # local functions

#
# Main run of the script 🚀

init()

# From the plain text of all outputs generated until now
systems = []
db_plaintxt = backwards_r('lise_plaintextdata.txt')
with open(db_plaintxt, 'r') as file:
    for line in file:
        if not line.startswith('#'):
            line = line.split()
            if len(line) == 0:
                continue
            smiles  = line[0]
            solvent = line[-6]
            plams_dir = line[-5]
            sp_dir    = line[-4]
            systems.append((smiles, solvent, os.path.join(plams_dir, sp_dir)))

temperature = 298
counter = 0
# Main loop
for system in systems:
    counter += 1
    count_num = str(counter).zfill(3)
    smiles, solvent, conf = system
    conf_job = ConformersJob.load_external(conf)
    pops = np.array(conf_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    # As in the main filter,
    score_dirs = rkf_paths(os.path.abspath(conf_job.results.rkfpath()))

    # Obtain number of atoms
    adf_SP_job = AMSJob.load_external(score_dirs[0])
    mol = adf_SP_job.results.get_main_molecule()
    natoms = len(mol)

    # Get the conformers.xyz file
    xyzfile = os.path.join(conf, 'conformers.xyz')
    with open(xyzfile, 'r') as file:
        xyzraw = file.readlines()

    # Divide the xyzraw into conformers
    nstart, nend = 0, natoms + 2
    for conformer in range(nconfs):
        nlines = xyzraw[nstart:nend]
        # Update start and end indices for the next conformer
        nstart, nend = nstart + natoms + 2, nend + natoms + 2
        # Define the file name for the current conformer
        conf_num = str(conformer+1).zfill(3)
        file_name = f'system_{count_num}_conformer_{conf_num}.xyz'
        # Open the file in write mode and write the selected lines
        with open(file_name, 'w') as f:
            f.write(''.join(nlines))

