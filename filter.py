# -*- coding: UTF-8 -*-
# Sans la première ligne il n'est pas possible d'utiliser des caractères spéciaux (emojis ☺️ )
from scm.plams import *
from scm.conformers import ConformersJob, ConformersResults
import os
import numpy as np
from lise_functions import * # local functions

#
# Funtion to run the calculations ✨
def run_jobs(molecule, solvent):
    # RDKit generator
    generate_settings = settings_for_task('Generate', user_settings)
    generate_job = ConformersJob(name='generate', molecule=molecule, settings=generate_settings)
    generate_job.run()
    # ADF reoptimization
    reoptimize_settings = settings_for_task('Optimize', user_settings, solvent)
    reoptimize_settings.input.ams.InputConformersSet = os.path.abspath(generate_job.results.rkfpath())
    reoptimize_ADF_job = ConformersJob(name='reoptimize_ADF', settings=reoptimize_settings)
    reoptimize_ADF_job.run()
    # ADF Single Point
    adf_SP_settings = settings_for_task('Score', user_settings, solvent)
    adf_SP_settings.input.ams.InputConformersSet = os.path.abspath(reoptimize_ADF_job.results.rkfpath())
    adf_SP_job = ConformersJob(name='SP_ADF', settings=adf_SP_settings)
    return adf_SP_job

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

    adf_SP_job = run_jobs(from_smiles(system['smiles']), system['solvent'])
    adf_results = adf_SP_job.run()
    plot_conformers(adf_SP_job)

    pops = np.array(adf_SP_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    # for now we'll compute dynamics just if we have one conformer
    if nconfs == 1:
        dynamics = adf_SP_job.results.get_dynamics(temperature)

    # directories with the plain text output and the TAPE21
    score_dirs = rkf_paths(os.path.abspath(adf_SP_job.results.rkfpath()))

    # Molecule dictionary
    molecule = {'smiles': system['smiles'],
                'solvent': system['solvent'],
                'number_atoms': natoms,
                'atoms': atoms,
                'number_conformers': nconfs,
                'average' : {},
                'conformers': {}}

    # Descriptors and average for each conformer
    for j, score in enumerate(score_dirs):
        conformer_data = descriptors(natoms, score, pops[j])
        for key in conformer_data:
            molecule['conformers'].setdefault(key, []).append(conformer_data[key])

    molecule['average'] = average_properties(molecule)

    system_results[(system['smiles'], system['solvent'])] = molecule

#
# Output
output_writer(system_results)

finish()

