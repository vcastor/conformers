# -*- coding: UTF-8 -*-
# Sans la première ligne il n'est pas possible d'utiliser des caractères spéciaux (emojis ☺️ )
from scm.plams import *
from scm.conformers import ConformersJob, ConformersResults
import os
import sys
import numpy as np
import sqlite3
from lise_functions import * # local functions

#
# Main run of the script 🚀

init()

# From the plain text of all outputs generated until now
systems = []
system = 'BUTANONE'
conn = sqlite3.connect('database_entropies/entropiesCOSMO.db')
cursor = conn.cursor()
cursor.execute('SELECT smile FROM PBE WHERE molecule_name = ?', (system,))
smiles = cursor.fetchall()
sp_dir = os.path.join('work_dir', system, 'SP_ADF')
systems.append((smiles[0][0], system, sp_dir))

temperature = 298.15
system_results = {}
# Main loop
for system in systems:
    smiles, solvent, conf = system
    conf_job = ConformersJob.load_external(conf)
    plot_conformers(conf_job)
    pops = np.array(conf_job.results.get_boltzmann_distribution(temperature))
    nconfs = len(pops)

    # As in the main filter,
    # score_dirs = rkf_paths(os.path.abspath(conf_job.results.rkfpath()))

    # # Obtain the molecule from the first conformer
    # adf_SP_job = AMSJob.load_external(score_dirs[0])
    # mol = adf_SP_job.results.get_main_molecule()
    # natoms = len(mol)
    # type_atoms = [atom.symbol for atom in mol]

    # # Molecule dictionary
    # molecule = {'smiles': smiles,
    #             'solvent': solvent,
    #             'number_atoms': natoms,
    #             'atoms': type_atoms,
    #             'number_conformers': nconfs,
    #             'average' : {},
    #             'conformers': {}}

    # # Descriptors and average for each conformer
    # for j, score in enumerate(score_dirs):
    #     conformer_data = entropy_cdft(natoms, freq, pops[j])
    #     for key in conformer_data:
    #         molecule['conformers'].setdefault(key, []).append(conformer_data[key])

    # molecule['average'] = average_properties(molecule)

    # system_results[(smiles, solvent)] = molecule

#
# Output
# output_writer(system_results)

finish()

