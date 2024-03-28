# -*- coding: UTF-8 -*-
from scm.plams import *
from scm.conformers import ConformersJob
from .small_functions import *
from .writer_helper import table_formatter
from .gvariables import gconfig
import numpy as np
import matplotlib.pyplot as plt

def get_main_results(job:ConformersJob):
    """
    Results from a ConformersJob, optionally including the molecules

    Returns:
    - A tuple with the molecules, energies, and populations
    """
    molecules = job.results.get_conformers()
    energies = job.results.get_relative_energies('kcal/mol')
    populations = job.results.get_boltzmann_distribution(gconfig['temperature'])

    return molecules, energies, populations

def plot_conformers(job:ConformersJob):
    """
    Plot conformers with their relative energies and populations.

    Parameters:
    - job: the ConformersJob object
    - indices: Specific indices of conformers to plot or an integer specifying how many to plot.
    - lowest: If True and indices is an int, plot the lowest N conformers. Otherwise, spread evenly.
    """
    temperature = gconfig['temperature']
    n_system = int_to_str_with_zeros(gconfig['system_nth'])
    plot_name = gconfig['input_file_name'].replace('.csv', '')
    molecules, energies, populations = get_main_results(job)

    indices = np.arange(len(energies))#arange(min(3, len(energies)))

    # Ensure 'axes' is always a list for consistent indexing, even with a single subplot
    fig, axes = plt.subplots(1, len(indices), figsize=(14, 5))
    axes = np.atleast_1d(axes)  # Make sure axes is always an array for consistency

    for ax, idx in zip(axes, indices):
        mol = molecules[idx]
        E = energies[idx]
        population = 100*populations[idx]

        plot_molecule(mol, ax=ax)  # Assuming this is a predefined function
        ax.set_title(f"#{idx + 1}\nΔE = {E:.2f} kcal/mol\nPop.: {population:.3f}% (T = {temperature} K)")

    plt.tight_layout()
    plt.savefig(f'{plot_name}_system_{n_system}.png')
    gconfig['system_nth'] += 1

def plain_text_output(output_file, system_results):
    with open(output_file, "w", encoding="utf-8") as file:
        for nsystem in system_results:
            system = system_results[nsystem]
            string_smile = ' {} '.format(system['smiles'])
            string_smile = '{:=^72}'.format(string_smile)
            string_solvent = ' {} '.format(system['solvent'])
            string_solvent = '{:*^72}'.format(string_solvent)
            file.write(f'{string_smile}\n')
            file.write(f'{string_solvent}\n')
            for key, value in system.items():
                if key == 'number_conformers' or key == 'number_atoms':
                    file.write(f'{key}: {value}\n')
                elif key == 'average' and system['number_conformers'] > 1:
                    string_average = '{:-^72}'.format(' Average ')
                    file.write(f'{string_average}\n')
                    formatted_average = table_formatter(system['atoms'], value)
                    file.write(f'{formatted_average}\n')
                elif key == 'conformers':
                    systems_aux = []
                    for i in range(system['number_conformers']):
                        aux_data = {subkey: subvalue[i] if isinstance(subvalue, list) else subvalue for subkey, subvalue in value.items()}
                        systems_aux.append(aux_data)
                    for j in range(system['number_conformers']):
                        string_conformer = '{:-^72}'.format(f' Conformer {j+1} ')
                        file.write(f'{string_conformer}\n')
                        file.write(f"Weight: {value['weights'][j]}\n")
                        formatted_conformer = table_formatter(system['atoms'], systems_aux[j])
                        file.write(f'{formatted_conformer}\n')

def json_writer(outfile, system_results):
    import json
    with open(outfile, "w", encoding="utf-8") as file:
        json.dump(conversion(system_results), file, ensure_ascii=False, indent=4)

def output_writer(system_results):
    out_file = gconfig['input_file_name'].replace('.csv', '.out')
    plain_text_output(out_file, system_results)
    json_file = gconfig['input_file_name'].replace('.csv', '.json')
    jsonresults = {}
    for smileskey, molecule in system_results.items():
        json_aux = molecule.copy()
        for key in ['smiles', 'solvent', 'average']:
            json_aux.pop(key)
        rmkey = ['cdftm', 'cdfta', 'condensed', 'qtaimcharge', 'fukui']
        for key in rmkey:
            json_aux['conformers'].pop(key)
        jsonresults[smileskey] = json_aux
    json_writer(json_file, jsonresults)

