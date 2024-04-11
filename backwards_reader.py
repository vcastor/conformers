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
            smiles  = line[1]
            solvent = line[-6]
            plams_dir = line[-5]
            sp_dir    = line[-4]
            systems.append((smiles, solvent, os.path.join(plams_dir, sp_dir)))

temperature = 298
system_results = {}
# Main loop
for system in systems:
    smiles, solvent, conf = system
    conf_job = ConformersJob.load_external(conf)
    pops = np.array(conf_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    # As in the main filter,
    score_dirs = rkf_paths(os.path.abspath(conf_job.results.rkfpath()))

    # Obtain the molecule from the first conformer
    adf_SP_job = AMSJob.load_external(score_dirs[0])
    mol = adf_SP_job.results.get_main_molecule()
    natoms = len(mol)
    type_atoms = [atom.symbol for atom in mol]

    # Molecule dictionary
    molecule = {'smiles': smiles,
                'solvent': solvent,
                'number_atoms': natoms,
                'atoms': type_atoms,
                'number_conformers': nconfs,
                'average' : {},
                'conformers': {}}

    # Descriptors and average for each conformer
    for j, score in enumerate(score_dirs):
        conformer_data = descriptors(natoms, score, pops[j])
        for key in conformer_data:
            molecule['conformers'].setdefault(key, []).append(conformer_data[key])

    molecule['average'] = average_properties(molecule)

    system_results[(smiles, solvent)] = molecule

#
# Output
output_writer(system_results)

finish()

