# -*- coding: UTF-8 -*-
from scm.plams import *
from scm.conformers import ConformersJob
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

def get_main_results(job:ConformersJob, temperature):
    """
    Results from a ConformersJob, optionally including the molecules

    Returns:
    - A tuple with the molecules, energies, and populations
    """
    molecules = job.results.get_conformers()
    energies = job.results.get_relative_energies('kcal/mol')
    populations = job.results.get_boltzmann_distribution(temperature)

    return molecules, energies, populations

def print_results(job:ConformersJob, temperature):
    """
    Print formatted results from a ConformersJob

    Parameters:
    - job: the ConformersJob object
    """
    _, energies, populations = get_main_results(job, return_molecules=False)

    print(f"Total # conformers in set: {len(energies)}")
    dE_header = f"ΔE [kcal/mol]"
    pop_header = f"Pop. (T = {temperature} K)"
    print(f'{"#":>4s} {dE_header:>14s} {pop_header:>18s}')

    for i, (E, pop) in enumerate(zip(energies, populations)):
        print(f'{i+1:4d} {E:14.2f} {pop:18.3f}')

def plot_conformers(job:ConformersJob, temperature):
    """
    Plot conformers with their relative energies and populations.

    Parameters:
    - job: the ConformersJob object
    - indices: Specific indices of conformers to plot or an integer specifying how many to plot.
    - lowest: If True and indices is an int, plot the lowest N conformers. Otherwise, spread evenly.
    """
    molecules, energies, populations = get_main_results(job, temperature)

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

    n_plot = datetime.now().strftime('%Y%m%d%H%M%S')
    plt.tight_layout()
    plt.savefig(f'conformers_{n_plot}.png')

