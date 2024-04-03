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

backwards_dir = backwards_path()

sp_calculations, conf_calc = [], []
for entry in os.listdir(backwards_dir):
    full_path = os.path.join(backwards_dir, entry)  # Construct the full path
    # Check if the entry is a directory and contains "SP_ADF" in its name
    if os.path.isdir(full_path) and "SP_ADF" in entry:
        conf_calc.append(full_path)
        # Now check for Score subdirectories
        for sub_entry in os.listdir(full_path):
            sub_full_path = os.path.join(full_path, sub_entry)
            if os.path.isdir(sub_full_path) and sub_entry.startswith('Score'):
                sp_calculations.append(sub_full_path)

temperature = 298
counter = 0
system_results = {}
# Main loop
#for system in sp_calculations:
for i in range(len(sp_calculations)):
    adf_SP_job = AMSJob.load_external(sp_calculations[i])
    mol = adf_SP_job.results.get_main_molecule()
    natoms = len(mol)
    type_atoms = [atom.symbol for atom in mol]

    conf_job = ConformersJob.load_external(conf_calc[i])
    pops = np.array(conf_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    # As in the main filter,
    score_dirs = rkf_paths(os.path.abspath(conf_job.results.rkfpath()))

    # Molecule dictionary
    molecule = {'smiles': 'not known smile',
                'solvent': 'not known solvent',
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

    key1, key2 = 'smiles'+str(counter), 'solvent'+str(counter)
    system_results[(key1, key2)] = molecule
    counter += 1

#
# Output
output_writer(system_results)

finish()

