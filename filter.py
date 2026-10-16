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

config_file = get_input_file()
config = input_reader(config_file)
create_tables(config)

temperature = config['temperature']

system_results = {prop: {} for prop in config['properties']}
# Main loop
for system in config['systems']:
    natoms, atoms = get_atoms(system['smiles'])
    solvent = solvent_name(system['solvent'], config['database']) if system['solvent'] else None

    # DFTB and DFT calculation
    adf_SP_job = run_jobs(system['smiles'], solvent, config)
    adf_results = adf_SP_job.run()

    pops = np.array(adf_SP_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    score_dirs = rkf_paths(os.path.abspath(adf_SP_job.results.rkfpath()))[:nconfs]

    molecules = {}
    for prop in config['properties']:
        if prop == 'entropy':
            conformer_dirs, reader, average = freq_jobs(score_dirs, solvent, config), entropy_cdft, average_entropy
        else:
            conformer_dirs, reader, average = score_dirs, descriptors, average_properties

        # Molecule dictionary
        molecule = {'smiles': system['smiles'],
                    'solvent': system['solvent'],
                    'number_atoms': natoms,
                    'atoms': atoms,
                    'number_conformers': nconfs,
                    'average' : {},
                    'conformers': {}}

        # Conformers loop
        for j, path in enumerate(conformer_dirs):
            conformer_data = reader(natoms, path, pops[j])
            for key in conformer_data:
                molecule['conformers'].setdefault(key, []).append(conformer_data[key])

        molecule['average'] = average(molecule)

        molecules[prop] = molecule
        system_results[prop][(system['smiles'], system['solvent'])] = molecule

    store(molecules, config)

# Output
name = os.path.splitext(config_file)[0]
if 'entropy' in config['properties']:
    entropy_writer(system_results['entropy'], name + '.entropy')
if 'nucleophilicity' in config['properties']:
    output_writer(system_results['nucleophilicity'], name + '.nucleophilicity')

finish()
