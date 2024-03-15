# -*- coding: UTF-8 -*-
from scm.plams import *
from scm.conformers import ConformersJob
from .small_functions import *
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

def print_results(job:ConformersJob):
    """
    Print formatted results from a ConformersJob

    Parameters:
    - job: the ConformersJob object
    """
    _, energies, populations = get_main_results(job, return_molecules=False)

    temperature = gconfig['temperature']
    print(f"Total # conformers in set: {len(energies)}")
    dE_header = f"ΔE [kcal/mol]"
    pop_header = f"Pop. (T = {temperature} K)"
    print(f'{"#":>4s} {dE_header:>14s} {pop_header:>18s}')

    for i, (E, pop) in enumerate(zip(energies, populations)):
        print(f'{i+1:4d} {E:14.2f} {pop:18.3f}')

def plot_conformers(job:ConformersJob):
    """
    Plot conformers with their relative energies and populations.

    Parameters:
    - job: the ConformersJob object
    - indices: Specific indices of conformers to plot or an integer specifying how many to plot.
    - lowest: If True and indices is an int, plot the lowest N conformers. Otherwise, spread evenly.
    """
    temperature = gconfig['temperature']
    n_system = gconfig['system_nth']
    plot_name = gconfig['input_file_name'].replace('.csv', '')
    molecules, energies, populations = get_main_results(job)

    indices = np.arange(min(3, len(energies)))

    # Ensure 'axes' is always a list for consistent indexing, even with a single subplot
    fig, axes = plt.subplots(1, len(indices), figsize=(12, 3))
    axes = np.atleast_1d(axes)  # Make sure axes is always an array for consistency

    for ax, idx in zip(axes, indices):
        mol = molecules[idx]
        E = energies[idx]
        population = populations[idx]

        plot_molecule(mol, ax=ax)  # Assuming this is a predefined function
        ax.set_title(f"#{idx + 1}\nΔE = {E:.2f} kcal/mol\nPop.: {population:.3f}% (T = {temperature} K)")

    plt.tight_layout()
    plt.savefig(f'{plot_name}_system_{n_system}.png')
    gconfig['system_nth'] += 1

def format_list(values, max_values_per_line=7):
    formatted_output = ""
    values = [values.tolist() if isinstance(values, np.ndarray) else values]
    for i, value in enumerate(values):
        if i % max_values_per_line == 0 and i > 0:
            formatted_output += ",\n      "
        elif i > 0:
            formatted_output += ", "
        formatted_output += repr(value)
    return formatted_output.strip()

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
                if key != 'conformers':
                    if isinstance(value, list):
                        formatted_value = format_list(value)# when key == atoms
                        file.write(f'{key}: {formatted_value}\n')
                    else:
                        file.write(f'{key}: {value}\n')
                else:
                    for j in range(system['number_conformers']):
                        string_conformer = '{:-^72}'.format(f' Conformer {j+1} ')
                        file.write(f'{string_conformer}\n')
                        for subkey, subvalue in value.items():
                            if subkey == 'IDM':
                                file.write(f'{subkey}: ommited for brevity\n')
                            else:
                                formatted_subvalue = format_list(subvalue[j])
                                file.write(f'{subkey:10}: {formatted_subvalue}\n')

def json_writer(outfile, system_results):
    import json
    with open(outfile, "w", encoding="utf-8") as file:
        json.dump(conversion(system_results), file, ensure_ascii=False, indent=4)

def output_writer(system_results):
    out_file = gconfig['input_file_name'].replace('.csv', '.out')
    json_file = gconfig['input_file_name'].replace('.csv', '.json')
    plain_text_output(out_file, system_results)
    json_writer(json_file, system_results)

