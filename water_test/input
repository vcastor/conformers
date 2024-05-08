# -*- coding: UTF-8 -*-
# Sans la première ligne il n'est pas possible d'utiliser des caractères spéciaux (emojis ☺️ )
from scm.plams import *
from scm.conformers import ConformersJob, ConformersResults
from lise_functions import * # local functions
import os
import numpy as np

#
# Main run of the script 🚀

init(path='.', folder='lise_output/')

input_file = get_input_file()

systems, user_settings = input_reader(input_file)
user_settings = validate_settings(user_settings)

temperature = user_settings['temperature']

system_results = {}
# Main loop
for system in systems:
    natoms, atoms = get_atoms(system['smiles'])

    # DFTB and DFT optimization
    adf_SP_job = run_jobs(from_smiles(system['smiles']), system['solvent'], user_settings)
    adf_SP_job.run()

    pops = np.array(adf_SP_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    score_dirs = rkf_paths(os.path.abspath(adf_SP_job.results.rkfpath()))
    freq_dirs = freq_jobs(score_dirs, system['solvent'], user_settings)

    # Molecule dictionary
    molecule = {'smiles': system['smiles'],
                'solvent': system['solvent'],
                'number_atoms': natoms,
                'atoms': atoms,
                'number_conformers': nconfs,
                'average' : {},
                'conformers': {}}

    # Entropy of every conformer
    for j, freq in enumerate(freq_dirs):
        conformer_data = entropy(natoms, freq, pops[j])
        for key in conformer_data:
            molecule['conformers'].setdefault(key, []).append(conformer_data[key])

    molecule['average'] = average_properties(molecule)

    system_results[(system['smiles'], system['solvent'])] = molecule

#
# Output
output_writer(system_results)

finish()

