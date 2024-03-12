# -*- coding: UTF-8 -*-
# Sans la première ligne il n'est pas possible d'utiliser des caractères spéciaux (emojis ☺️ )
from scm.plams import *
from scm.conformers import ConformersJob, ConformersResults
from scm.plams.recipes.adfcosmorscompound import *
import os
import numpy as np
import json
# local imports
from descriptors import *
from functional_settings import *
from input_reader import *
from output_writer import *
from small_functions import *
from solvent_settings import *
from task_settings import *

#
# Funtion to run the calculations ✨
def run_jobs(smile, solvent):
    global temperature
    molecule = from_smiles(smile)
    # RDKit generator
    generate_settings = settings_for_task('Generate', user_settings)
    generate_job = ConformersJob(name='generate', molecule=molecule, settings=generate_settings)
    generate_job.run()
    plot_conformers(generate_job, temperature)
    # ADF reoptimization
    reoptimize_settings = settings_for_task('Optimize', user_settings, solvent)
    reoptimize_settings.input.ams.InputConformersSet = os.path.abspath(generate_job.results.rkfpath())
    reoptimize_ADF_job = ConformersJob(settings=reoptimize_settings, name='reoptimize_ADF')
    reoptimize_ADF_job.run()
    plot_conformers(reoptimize_ADF_job, temperature)
    # ADF Single Point
    adf_SP_settings = settings_for_task('Score', user_settings, solvent)
    adf_SP_settings.input.ams.InputConformersSet = os.path.abspath(reoptimize_ADF_job.results.rkfpath())
    adf_SP_job = ConformersJob(settings=adf_SP_settings, name='SP_ADF')
    return adf_SP_job

#
# Main run of the script 🚀

init()

input_file = get_input_file()
systems, user_settings = input_reader(input_file)
user_settings = validate_settings(user_settings)

# global variables FIXME
temperature = user_settings['temperature']
unit = 'kcal/mol'


for system in systems:
    adf_SP_job = run_jobs(system['smiles'], system['solvent'])
    adf_results = adf_SP_job.run()
    
    path = os.path.abspath(adf_SP_job.results.rkfpath())
    paths = [path[0:len(path)-14] + str(element) for element in adf_results.files if 'Score' in element and element.endswith('.out') and 'CreateAtoms.out' not in element]
    paths = sorted(paths, key=extract_number)

    content = [open(path, 'r', encoding='unicode_escape').read() for path in paths]

    pops = np.array(get_main_results(adf_SP_job, temperature, unit)[2])

    molecule = {'number_atoms': atoms(content[0])[0],
                'atoms': atoms(content[0])[1],
                'number_conformers': len(pops),
                'conformers': {'weights': [],
                                'IDM': [],
                                'Hirshfeld': [],
                                's2': [],
                                'OE': []}}

    for i, conformer in enumerate(content):
        molecule['conformers']['weights'].append(pops[i])
        molecule['conformers']['IDM'].append(distance_matrix(conformer))
        molecule['conformers']['Hirshfeld'].append(hirshfeld(conformer))
        molecule['conformers']['s2'].append(s2(conformer))
        molecule['conformers']['OE'].append(orbital_energies(conformer))
             
    Results_smiles[system['smiles']] = molecule

output_file = input_file.replace('.csv', '.out')
file = open('results.txt', 'w', encoding='utf8')

#FIXME
mol_list = list(Results_smiles.keys())
for smiles in Results_smiles:
    writer(f"================================ {smiles} ================================", file)
    molecule = Results_smiles[smiles]
    for key, value in molecule.items():
        if key != 'conformers':
            writer(f"{key}: {value}", file)
        else:
            for i in range(min(4, len(value['weights']))):
                writer(f"======================== Conformer {i+1} ========================", file)
                for sub_key, sub_value in value.items():
                    if sub_key != 'IDM':
                            writer(f"{sub_key}: {sub_value[i]}", file)
                    else:
                            writer(f"{sub_key}: {'IDM omitted for brevity'}", file)

with open('results.json', 'w',encoding='utf8') as outfile:
    json.dump(conversion(Results_smiles), outfile, ensure_ascii=False, indent=4)

finish()
