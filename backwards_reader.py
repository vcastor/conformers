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

backwards_dir = sys.argv[3]
#outputname = sys.argv[2]

sp_calculations = []
# Loop through each item in the specified directory
for entry in os.listdir(backwards_dir):
    full_path = os.path.join(backwards_dir, entry)  # Construct the full path
    # Check if the entry is a directory and contains "SP_ADF" in its name
    if os.path.isdir(full_path) and "SP_ADF" in entry:
        # Now check for a subdirectory with "Score" in its name within this directory
        sp_calculations.append(full_path)  # Add the directory path to the list
        #for sub_entry in os.listdir(full_path):
        #    sub_full_path = os.path.join(full_path, sub_entry)  # Construct the full path for the subdirectory
        #    # Check if the sub_entry is a directory and contains "Score" in its name
        #    if os.path.isdir(sub_full_path) and "Score" in sub_entry:
        #        sp_calculations.append(sub_full_path)  # Add the subdirectory path to the list

temperature = 298
system_results = {}
# Main loop
for system in sp_calculations:
    adf_SP_job = ConformersJob.load_external(system)

    path = os.path.abspath(adf_SP_job.results.rkfpath())
    paths = score_paths(path, adf_SP_job.results)

    pops = np.array(adf_SP_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    amsrkf = AMSJob.load_external(os.path.join(system, 'Score_0/ams.rkf'))
    mol = amsrkf.results.get_input_molecule()
    natoms = len(mol)
    atoms = [mol.atoms[i]._getsymbol() for i in range(natoms)]

    molecule = {'number_atoms': natoms,
                'atoms': atoms,
                'number_conformers': nconfs,
                'conformers': {'weights': [],
                               'IDM': [],
                               'Hirshfeld': [],
                               's2': [],
                               'OE': []}}

    for j, path in enumerate(paths):
        with open(path, 'r', encoding='unicode_escape') as file:
            conformer = file.read()
            molecule['conformers']['weights'].append(pops[j])
            molecule['conformers']['IDM'].append(distance_matrix(natoms, conformer))
            molecule['conformers']['Hirshfeld'].append(hirshfeld(natoms, conformer))
            molecule['conformers']['s2'].append(s2(natoms, conformer))
            molecule['conformers']['OE'].append(orbital_energies(conformer))

    system_results[system] = molecule

print(system_results)
quit()
#
# Output
output_writer(system_results)

finish()

