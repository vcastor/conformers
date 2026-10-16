# -*- coding: UTF-8 -*-
# PLAMS functions, run them with $AMSBIN/amspython (or plams) from the repo root
import os
import numpy as np
import matplotlib.pyplot as plt
from scm.plams import *
from scm.conformers import ConformersJob
from lise_functions.small_functions import rkf_paths

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

def plot_conformers(job:ConformersJob, temperature, plot_name):
    """
    Plot conformers with their relative energies and populations.

    Parameters:
    - job: the ConformersJob object
    - temperature: Boltzmann temperature
    - plot_name: the figure is saved as plot_name.png
    """
    molecules, energies, populations = get_main_results(job, temperature)

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
    plt.savefig(f'{plot_name}.png')

def conformers_xyz(systems, temperature, family):
    """
    One xyz file per conformer, xyz_conf/<family>/system_NNN_conformer_KKK.xyz,
    from inputs/<family>/SP_ADF[.NNN] (systems in the order of the configuration)
    """
    # Main loop
    sys_counter = 0
    for system in systems:
        sys_counter += 1
        sys_count_num = str(sys_counter).zfill(3)
        sp_dir = 'SP_ADF.' + sys_count_num if sys_counter > 1 else 'SP_ADF'
        sp_dir = os.path.join('inputs', family, sp_dir)
        conf_job = ConformersJob.load_external(sp_dir)
        pops = np.array(conf_job.results.get_boltzmann_distribution(temperature))
        nconfs = len(pops)

        # As in the main filter,
        score_dirs = rkf_paths(os.path.abspath(conf_job.results.rkfpath()))[:nconfs]

        # Obtain number of atoms
        adf_SP_job = AMSJob.load_external(score_dirs[0])
        natoms = len(adf_SP_job.results.get_main_molecule())

        # Get the conformers.xyz file
        xyzfile = os.path.join(os.path.abspath(sp_dir), 'conformers.xyz')
        with open(xyzfile, 'r') as file:
            xyzraw = file.readlines()

        # Be sure the directory exists
        os.makedirs(os.path.join('xyz_conf', family), exist_ok=True)

        # Divide the xyzraw into conformers
        nstart, nend = 0, natoms + 2
        for conformer in range(nconfs):
            nlines = xyzraw[nstart:nend]
            # Update start and end indices for the next conformer
            nstart, nend = nstart + natoms + 2, nend + natoms + 2
            # Define the file name for the current conformer
            conf_num = str(conformer+1).zfill(3)
            file_xyz_nconf = f'system_{sys_count_num}_conformer_{conf_num}.xyz'
            file_xyz_nconf = os.path.join('xyz_conf', family, file_xyz_nconf)
            # Change the comment line with the smiles, solvent and weight of the conformer
            nlines[1] = f'{system["smiles"]} {system["solvent"]} {pops[conformer]:.4f}\n'
            # Open the file in write mode and write the selected lines
            with open(file_xyz_nconf, 'w') as f:
                f.write(''.join(nlines))
