# -*- coding: UTF-8 -*-
# Sans la première ligne il n'est pas possible d'utiliser des caractères spéciaux (emojis ☺️ )
from scm.plams import *
from scm.conformers import ConformersJob, ConformersResults
from lise_functions import * # local functions
import os
import numpy as np

#
# Main run of the script 🚀

init()

input_file = get_input_file()

systems, user_settings = input_reader(input_file)
user_settings = validate_settings(user_settings)

temperature = user_settings['temperature']

system_results = {}
# Main loop
for system in systems:
    natoms, atoms = get_atoms(system['smiles'])

    # DFTB and DFT calculation
    adf_SP_job = run_jobs(from_smiles(system['smiles']), system['solvent'], user_settings)
    adf_results = adf_SP_job.run()

    pops = np.array(adf_SP_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    # # for now we'll compute dynamics just if we have one conformer
    # if nconfs == 1:
    #     dynamics = adf_SP_job.results.get_dynamics(temperature)

    score_dirs = rkf_paths(os.path.abspath(adf_SP_job.results.rkfpath()))[:nconfs]
    # sp_dirs = pol_jobs(score_dirs, system['solvent'], user_settings)

    # Molecule dictionary
    molecule = {'smiles': system['smiles'],
                'solvent': system['solvent'],
                'number_atoms': natoms,
                'atoms': atoms,
                'number_conformers': nconfs,
                'average' : {},
                'conformers': {}}

    # Conformers loop
    for j, sp in enumerate(score_dirs):
        conformer_data = descriptors(natoms, sp, pops[j])
        for key in conformer_data:
            molecule['conformers'].setdefault(key, []).append(conformer_data[key])

    molecule['average'] = average_properties(molecule)

    system_results[(system['smiles'], system['solvent'])] = molecule

# Output
output_writer(system_results)

finish()

