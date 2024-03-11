# -*- coding: UTF-8 -*-
# Sans la première ligne il n'est pas possible d'utiliser des caractères spéciaux (emojis ✨)
# THE CODE HAS SOME ISSUES, IT IS NOT FINISHED!
# right now it's kind of monolithic, it should be divided into smaller functions
from scm.plams import *
from scm.conformers import ConformersJob, ConformersResults
from scm.plams.recipes.adfcosmorscompound import *
import os
import re
import csv
import sys
import math
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json

#----------------------------------------------------------------------#
#                   Functions for the input / output
#
def input_reader(filepath):
    """
    Reads the list of molecules and settings from a file.

    Parameters:
    - filepath: the path to the file
    Returns:
    - systems: dictionary, each containing the SMILES and solvent
    - settings: a dictionary with the settings (for all systems)
    """
    data = pd.read_csv(filepath, comment='#', header=None, skip_blank_lines=True)

    systems, settings = [], {}

    key_variations = {
        'functional': ['xc', 'exchange-correlation', 'exchange correlation', 'functional', 'xc functional'],
        'basis set': ['basis', 'basis set'],
        'dispersion': ['dispersion', 'dispersion correction', 'dispersion method'],
        'RMSD': ['root mean square deviation', 'root mean square deviation of atomic positions', 'rmsd'],
        'score E threshold': ['score e', 'score energy', 'delta energy 1', 'score energy threshold',
                                 'score e threshold', 'energy threshold score'],
        'optimize E threshold': ['optimize e', 'optimize energy', 'delta energy 2',
                                 'optimize energy threshold', 'optimize e threshold', 'energy threshold optimize'],
        'temperature': ['temp', 't', 'temperature'],
        'n conformers': ['n conformers', 'conformers', 'number of conformers'],
    }

    reverse_map = {variation.lower(): key for key, variations in key_variations.items() for variation in variations}

    # Extract the systems and settings
    for _, row in data.iterrows():
        first_element = row[0].strip()
        if first_element.lower() in reverse_map:
            key = reverse_map[first_element.lower()]
            settings[key] = str(row[1]).strip() if pd.notna(row[1]) else None
        else:
            solvent = row[1].strip() if pd.notna(row[1]) else None
            systems.append({'smiles': first_element, 'solvent': solvent})

    # Validate all expected settings are present
    for setting_key in key_variations:
        if setting_key not in settings:
            raise ValueError(f"Missing setting '{setting_key}'")

    return systems, settings

def validate_settings(settings):
    """
    Validates the settings.
    Parameters: settings (a dictionary)

    Raises a ValueError if any of the settings are invalid
    """

    expected_settings = {
        'temperature': float,
        'n conformers': int,
        'RMSD': float,
        'score E threshold': float,
        'optimize E threshold': float,
    }

    validated_settings = {}
    for key, expected_type in expected_settings.items():
        value = settings.get(key)
        try:
            converted_value = expected_type(value)
            if converted_value < 0:
                raise ValueError(f"{key} must be non-negative")
            if key == 'n conformers' and converted_value < 1:
                raise ValueError("Number of conformers must be positive")
            validated_settings[key] = converted_value
        except ValueError:
            raise ValueError(f"Invalid value for setting '{key}'")

    if validated_settings['score E threshold'] >= validated_settings['optimize E threshold']:
        raise ValueError("Score E threshold must be less than optimize E threshold")

    # The rest of the settings are not validated (for now)
    for key, value in settings.items():
        if key not in validated_settings:
            validated_settings[key] = value

    return validated_settings

def get_main_results(job:ConformersJob, return_molecules:bool=True):
    """
    Results from a ConformersJob, optionally including the molecules
    Relies on global variables temperature and unit

    Returns:
    - A tuple with the molecules, energies, and populations
    """
    global temperature, unit
    molecules = job.results.get_conformers() if return_molecules else None
    energies = job.results.get_relative_energies(unit)
    populations = job.results.get_boltzmann_distribution(temperature)

    return molecules, energies, populations

def print_results(job:ConformersJob):
    """
    Print formatted results from a ConformersJob

    Parameters:
    - job: the ConformersJob object
    """
    global temperature, unit
    _, energies, populations = get_main_results(job, return_molecules=False)

    print(f"Total # conformers in set: {len(energies)}")
    dE_header = f"ΔE [{unit}]"
    pop_header = f"Pop. (T = {temperature} K)"
    print(f'{"#":>4s} {dE_header:>14s} {pop_header:>18s}')

    for i, (E, pop) in enumerate(zip(energies, populations)):
        print(f'{i+1:4d} {E:14.2f} {pop:18.3f}')

def plot_conformers(job:ConformersJob, indices=None, lowest=True):
    """
    Plot conformers with their relative energies and populations.

    Parameters:
    - job: the ConformersJob object
    - indices: Specific indices of conformers to plot or an integer specifying how many to plot.
    - lowest: If True and indices is an int, plot the lowest N conformers. Otherwise, spread evenly.
    """
    global temperature, n_plot
    molecules, energies, populations = get_main_results(job)

    # Determine which conformers to plot based on 'indices' and 'lowest'
    if isinstance(indices, int):
        N_plot = min(indices, len(energies))
        indices = np.arange(N_plot) if lowest else np.linspace(0, len(energies) - 1, N_plot, dtype=int)
    elif indices is None:
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
    n_plot += 1
    plt.savefig(f'conformers_{n_plot}.png')
    #plt.show()

def conversion(dic):
    """
    Exporting the results to a JSON file
    """
    if isinstance(dic, (list, np.ndarray)):
        return [conversion(item) for item in dic]
    elif isinstance(dic, dict):
        return {key: conversion(value) for key, value in dic.items()}
    elif isinstance(dic, np.ndarray):
        return dic.tolist()
    return dic

#
# Small funtions
#
def extract_number(string):
    number_extractor_re = re.compile(r'Score_(\d+)\.out')
    match = re.search(r'Score_(\d+)\.out', string)
    if match:
        return int(match.group(1))
    else:
        return 0
#return int(number_extractor_re.search(string).group(1))
#return int(re.search(r'Score_(\d+)\.out', string).group(1))

def extractor(content, start_marker, end_marker):
    start_marker_pattern = re.compile(start_marker)
    start_index = start_marker_pattern.search(content)
    n = start_index.start()
    #start_index = content.index(start_marker)
    #end_index = content.index(end_marker, start_index + len(start_marker))
    end_index = content.index(end_marker, n)
    table = content[n:end_index].strip()
    return [line.strip() for line in table.split('\n') if line.strip()]
    
def verification_geom_converged(content):
    return "Geometry optimization converged" in content

def writer(line, file):
    line = str(line)
    print(line)
    file.write(line + '\n')

def to_lower_dict(d):
    """Converts dictionary keys to lowercase."""
    return {key.lower(): value for key, value in d.items()}

#
# Descriptors
#
def atoms(content):
    """
    Number of atoms and types of atoms
    """
    #start_marker = "G E O M E T R Y  ***  3D  Molecule  ***"
    start_marker = "G E O M E T R Y  "
    end_marker = "FRAGMENTS"
    lines = extractor(content, start_marker, end_marker)

    # Assuming the actual atom data starts at line 8
    atom_data_lines = lines[8:]

    type_atoms = [line.split()[1] for line in atom_data_lines if line]

    return len(type_atoms), type_atoms

def distance_matrix(content):
    """
    Interatomic Distance Matrix
    """
    #start_marker = "G E O M E T R Y  ***  3D  Molecule  ***"
    start_marker = "G E O M E T R Y  "
    end_marker = "FRAGMENTS"
    lines = extractor(content, start_marker, end_marker)
    
    coord_lines = lines[8:]
    coords = np.array([line.split()[2:5] for line in coord_lines if line], dtype=float)

    # Calculate the interatomic distance matrix
    distance_mat = np.zeros((coords.shape[0], coords.shape[0]))
    for i in range(coords.shape[0]):
        for j in range(i+1, coords.shape[0]):
            distance_mat[i, j] = np.linalg.norm(coords[i] - coords[j])
            distance_mat[j, i] = distance_mat[i, j]
    
    return distance_mat

def s2(content):
    """
    Grand Canonical Ensemble
    """
    start_marker = "ATOMIC DESCRIPTORS: GRAND CANONICAL ENSEMBLE"
    end_marker = "Please note that s(2)=S^2"#*f(2) (approximation)"
    
    lines = extractor(content, start_marker, end_marker)
    s2_values = [line.split()[-1] for line in lines[5:-4]]
    
    return np.array(s2_values, dtype=float)

def hirshfeld(content):
    """
    Extract Hirshfeld values.
    """
    start_marker = "For each fragment: the "#(numerical) integral of rho(scf)"# * rho(fragment)/rho(sum-of-fragments)"
    end_marker = "Sum of these charges (accuracy NumInt/Tails) ="
    
    lines = extractor(content, start_marker, end_marker)
    hirshfeld_values = [float(line.split()[-1]) for line in lines[8:]]
    
    return np.array(hirshfeld_values, dtype=float)

def orbital_energies(content):
    """
    Orbital Energies
    """
    start_marker = "Orbital Energies, per Irrep and Spin:" 
    end_marker = "cosmo_calcen:"
    
    lines = extractor(content, start_marker, end_marker)
    
    Occup, E_ev = [], []
    for line in lines[5:-4]:# Check the values [the first program use to have an issue] FIXME
        parts = line.split()
        if len(parts) > 3:
            occup, energy = parts[1], parts[3]
            Occup.append(occup)
            E_ev.append(energy)
    
    count_2 = Occup.count('2.000')
    E_ev = E_ev[max(0, count_2-5):count_2+5] # Avoild negative index
    
    return np.array(E_ev, dtype=float)

#----------------------------------------------------------------------#
#                     Funtions for the calculations
#
def functional_settings(functional, settings):
    gga_functionals = {
     "BP86" : "BP86",
     "BLYP" : "BLYP",
     "PW91" : "PW91",
     "mPW" : "mPW",
     "PBE" : "PBE",
     "RPBE" : "RPBE",
     "revPBE" : "revPBE",
     "PBE" : "PBE",
     "PBEsol" : "PBEsol",
     "OLYP" : "OLYP",
     "OPBE" : "OPBE",
     "HTBS" : "HTBS",
     "KT1" : "KT1",
     "KT2" : "KT2",
    }
    gga_dispersion_functionals = {
     "BP86-D" : ('BP86', 'DEFAULT'),
     "BLYP-D" : ('BLYP', 'DEFAULT'),
     "PBE-D" : ('PBE', ' DEFAULT'),
     "PBEsol-D" : ('PBEsol', ' DEFAULT'),
     "SSB-D" : ('SSB-D', None),
     "BP86-D3" : ('BP86', 'Grimme3'),
     "BLYP-D3" : ('BLYP', 'Grimme3'),
     "revPBE-D3" : ('revPBE', 'Grimme3'),
     "PBE-D3" : ('PBE', 'Grimme3'),
     "PBEsol-D3" : ('PBEsol', 'Grimme3'),
     "PBEsol-D3(BJ)" : ('PBEsol', 'Grimme3 BJDAMP'),
     "RPBE-D3" : ('RPBE', 'Grimme3'),
     "S12g-D3" : ('S12g', 'Grimme3'),
     "BLYP-dDsC" : ('BLYP', 'dDsC'),
     "PBE-dDsC" : ('PBE', 'dDsC'),
     "BP86-dDsC" : ('BP86', 'dDsC'),
     "revPBE-dDsC" : ('revPBE', 'dDsC'),
     "BP86-D3(BJ)" : ('BP86', 'GRIMME3 BJDAMP'),
     "BLYP-D3(BJ)" : ('BLYP', 'GRIMME3 BJDAMP'),
     "revPBE-D3(BJ)" : ('revPBE', 'GRIMME3 BJDAMP'),
     "PBE-D3(BJ)" : ('PBE', 'GRIMME3 BJDAMP'),
     "BP86-D4(EEQ)" : ('BP86', 'GRIMME4'),
     "BLYP-D4(EEQ)" : ('BLYP', 'GRIMME4'),
     "revPBE-D4(EEQ)" : ('revPBE', 'GRIMME4'),
     "PBE-D4(EEQ)" : ('PBE', 'GRIMME4'),
     "PBE-MBD@rsSC" : ('PBE', ' MBD'),
     "PW91-dUFF" : ('PW91', 'UFF'),
     "PBE-dUFF" : ('PBE', 'UFF'),
    }
    meta_gga_functionals = {
     "M06L" : ("M06L", None),
     "revTPSS" : ("revTPSS", None),
     "TPSS" : ("TPSS", None),
     "TPSS-D3" : ("TPSS", "Grimme3"),
     "TPSS-D3(BJ)" : ("TPSS", "GRIMME3 BJDAMP"),
     "TPSS-D4" : ("TPSS", "GRIMME4"),
     "SSB-D" : ("SSB-D", None),
     "MVS" : ("MVS", None),
     "r2SCAN-3c" : ("r2SCAN-3c", None),
     "SCAN" : ("SCAN", None),
     "SCAN-D3(BJ)" : ("SCAN", "GRIMME3 BJDAMP"),
     "TASKxc" : ("TASKxc", None),
     "TASKCC" : ("TASKCC", None)
    }
    model_functionals = {
    #if {$xc eq "Model:GRAC"} {set axc "Model GRAC [GIN xc.ip] [GIN xc.ipb] # FIXME
     "LB94" : "LB94",
     "SAOP" : "SAOP",
     "TB-mBJ" : "TB-mBJ",
     "KTB-mBJ" : "KTB-mBJ",
     "JTS-mTB-mBJ" : "JTS-mTB-mBJ",
     "GLLB-SC" : "GLLB-SC",
     "BGLLB-VWN" : "BGLLB-VWN",
     "BGLLB-LYP" : "BGLLB-LYP",
    }
    hybrid_functionals = {
     "B3LYP" : ("B3LYP", None),
     "B3LYP*" : ("B3LYP*", None),
     "B3LYP-D" : ("B3LYP", "DEFAULT"),
     "B3LYP-D3" : ("B3LYP", "Grimme3"),
     "B3LYP-dDsC" : ("B3LYP", "dDsC"),
     "B3LYP-D3(BJ)" : ("B3LYP", "GRIMME3 BJDAMP"),
     "B3LYP-D4(EEQ)" : ("B3LYP", "GRIMME4"),
     "B3LYP-dUFF" : ("B3LYP", "UFF"),
     "B1LYP" : ("B1LYP", None),
     "KMLYP" : ("KMLYP", None),
     "O3LYP" : ("O3LYP", None),
     "X3LYP" : ("X3LYP", None),
     "BHandH" : ("BHandH", None),
     "BHandHLYP" : ("BHandHLYP", None),
     "BHandHLYP-dDsC" : ("BHandHLYP", "dDsC"),
     "B1PW91" : ("B1PW91", None),
     "MPW1PW" : ("MPW1PW", None),
     "MPW1K" : ("MPW1K", None),
     "OPBE0" : ("OPBE0", None),
     "PBE0" : ("PBE0", None),
     "PBE0-dDsC" : ("PBE0", "dDsC"),
     "PBE0-MBD@rsSC" : ("PBE0", "MBD"),
     "S12h-D3" : ("S12h", "Grimme3"),
    }
    metahybrid_functionals = {
     "M06" : "M06",
     "M06-2X" : "M06-2X",
     "M06-HF" : "M06-HF",
     "TPSSH" : "TPSSH"
    }
    # FIXME, add the rest of the functionals $AMSHOME/gui/libtcl/keys.tcl
    lib_xc_functionals = {
     "N12" : ('N12', None),
     "GAM" : ('GAM', None),
     "rSCAN" : ("rSCAN", None),
     "revSCAN" : ("revSCAN", None),
     "r2SCAN" : ("r2SCAN", None),
     "r2SCAN-D4" : ("r2SCAN", "GRIMME4"),
     "MN15-L" : ("MN15-L", None),
     "B97-D4(EEQ)" : ("B97", "GRIMME4"),
     "MN15" : ("MN15", None),
     "M08-HX" : ("M08-HX", None),
     "revSCAN0" : ("revSCAN0", None)
    }

    gga_functionals_lower = to_lower_dict(gga_functionals)
    gga_dispersion_functionals_lower = to_lower_dict(gga_dispersion_functionals)
    meta_gga_functionals_lower = to_lower_dict(meta_gga_functionals)
    model_functionals_lower = to_lower_dict(model_functionals)
    hybrid_functionals_lower = to_lower_dict(hybrid_functionals)
    metahybrid_functionals_lower = to_lower_dict(metahybrid_functionals)
    lib_xc_functionals_lower = to_lower_dict(lib_xc_functionals)

    functional = functional.strip().lower()

    if functional in gga_functionals_lower:
        settings.input.ADF.XC.GGA = gga_funtionals_lower[functional]
    elif functional in gga_dispersion_functionals_lower:
        func, disp = gga_dispersion_functionals_lower[functional]
        settings.input.ADF.XC.GGA = func
        if disp is not None:
            settings.input.ADF.XC.DISPERSION = disp
    elif functional in meta_gga_functionals_lower:
        func, disp = meta_gga_functionals_lower[functional]
        settings.input.ADF.XC.METAGGA = func
        if disp is not None:
            settings.input.ADF.XC.DISPERSION = disp
    elif functional in model_functionals_lower:
        settings.input.ADF.XC.Model = model_functionals_lower[functional]
    elif functional in hybrid_functionals_lower:
        func, disp = hybrid_functionals_lower[functional]
        settings.input.ADF.XC.HYBRID = func
        if disp is not None:
            settings.input.ADF.XC.DISPERSION = disp
    elif functional in metahybrid_functionals_lower:
        func = metahybrid_functionals_lower[functional]
        settings.input.ADF.XC.METAHYBRID = func
    elif functional == 'hartre fock':
        settings.input.ADF.XC = 'HartreeFock'

    return settings

def task_settings(task):
    global user_settings
    s = Settings()
    if task == 'Generate':
        s.input.ams.Task = 'Generate'
        s.input.ams.Generator.Method = 'RDKit'
        s.input.ams.Generator.RDKit.InitialNConformers = user_settings['n conformers']
        s.input.ams.Equivalence.Crest.RMSDThreshold = user_settings['RMSD']
        s.input.DFTB.Model = 'GFN1-xTB'#FIXME
    elif task == 'Optimize':
        s.input.ams.Task = 'Optimize'
        s.input.ams.GeometryOptimization.ConvergenceQuality = 'Normal'
        s.input.ams.InputMaxEnergy = user_settings['optimize E threshold']
        s.input.ADF.Basis.Type = user_settings['basis set']
        s.input.ADF.Symmetry = 'NOSYM'
        functional_settings(user_settings['functional'], s)
        s.input.ADF.Relativity.Level = 'None'
        s.input.ADF.Solvation.Surf = 'Delley'
    elif task == 'Score':
        s.input.ams.Task = 'Score'
        s.input.ams.InputMaxEnergy = user_settings['score E threshold']
        s.input.ADF.Basis.Type = user_settings['basis set']
        s.input.ADF.Symmetry = 'NOSYM'
        functional_settings(user_settings['functional'], s)
        s.input.ADF.Relativity.Level = 'None'
        s.input.ADF.ConceptualDFT.Enabled = 'Yes'
        s.input.ADF.ConceptualDFT.AnalysisLevel = 'Full'
        s.input.ADF.QTAIM.Enabled = 'Yes'
        s.input.ADF.QTAIM.AnalysisLevel = 'Extended'
    return s

def solvent_name(solvent):
    """
    ADF input case insensitive, but the solvent name must be correct.
    """
    solvent_mapping = {
        'thf': 'Tetrahydrofuran',
        'mecn': 'Acetonitrile',
        'dimethyl sulfoxide': 'DMSO',
        'dimethylsulfoxide': 'DMSO',
        'dmf': 'DMFA',
        'dimethylformamide': 'DMFA',
        'et2o': 'DiethylEther',
        'diethyl ether': 'DiethylEther'
    }
    normalized_solvent = solvent.lower()
    # Update the solvent name if it is the dictionary
    solvent = solvent_mapping.get(normalized_solvent)
    return solvent

def solvent_settings(solvent):
    """
    ADF input needs some extra information, not only the name of the solvent.
    This function returns a dictionary with the required settings.
    """
    solvent_settings = Settings()
    #solvent_settings = ADFCOSMORSCompoundJob.solvation_settings()
    #radii = ADFCOSMORSCompoundJob._get_radii() # Klamt's radii
    # Constant, linear terms of Ecd
    # taken from ADF code $AMSHOME/src/lib/dft/solvation/SolventConfig.f90
    # (T. N. Truong, E. V. Stefanovich, Chem. Phys. Lett 240 , 253-260 (1995)
    cav0, cav1 = 0.0, 0.0067639
    solvent = solvent_name(solvent)
    solvent_settings.input.ADF.Solvation.Solv = f'name={solvent} cav0={cav0} cav1={cav1}'
    solvent_settings.input.ADF.Solvation.Charged = 'method=CONJ'
    solvent_settings.input.ADF.Solvation.SCF = 'VAR ALL'
    solvent_settings.input.ADF.Solvation.Surf = 'Delley'
    return solvent_settings

def settings_for_task(task, solvent=None):
    s = task_settings(task)
    if solvent is not None:
        s.soft_update(solvent_settings(solvent))
    return s

def run_jobs(smile, solvent):
    molecule = from_smiles(smile)
    # RDKit generator
    generate_settings = settings_for_task('Generate')
    generate_job = ConformersJob(name='generate', molecule=molecule, settings=generate_settings)
    generate_job.run()
    #plot_conformers(generate_job, 4)
    # ADF reoptimization
    reoptimize_settings = settings_for_task('Optimize', solvent)
    reoptimize_settings.input.ams.InputConformersSet = os.path.abspath(generate_job.results.rkfpath())
    reoptimize_ADF_job = ConformersJob(settings=reoptimize_settings, name='reoptimize_ADF')
    reoptimize_ADF_job.run()
    #plot_conformers(reoptimize_ADF_job, 4)
    # ADF Single Point
    adf_SP_settings = settings_for_task('Score', solvent)
    adf_SP_settings.input.ams.InputConformersSet = os.path.abspath(reoptimize_ADF_job.results.rkfpath())
    adf_SP_job = ConformersJob(settings=adf_SP_settings, name='SP_ADF')
    #adf_SP_job.run()
    return adf_SP_job

#
# End of functions;
#----------------------------------------------------------------------#

#----------------------------------------------------------------------#
#                       Main part of the script                        #
#----------------------------------------------------------------------#
init()

input_file = sys.argv[3] # FIXME
systems, user_settings = input_reader(input_file)
user_settings = validate_settings(user_settings)

temperature = user_settings['temperature']
unit = 'kcal/mol' # FIXME
n_plot = 1

Results_smiles = {}

for system in systems:
    adf_SP_job = run_jobs(system['smiles'], system['solvent'])
    adf_results = adf_SP_job.run()
    
    path = os.path.abspath(adf_SP_job.results.rkfpath())
    paths = [path[0:len(path)-14] + str(element) for element in adf_results.files if 'Score' in element and element.endswith('.out') and 'CreateAtoms.out' not in element]
    #paths.sort(key=extract_number(paths))
    paths = sorted(paths, key=extract_number)

    content = [open(path, 'r', encoding='unicode_escape').read() for path in paths]

    pops = np.array(get_main_results(job=adf_SP_job)[2])

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
                    #writer(f"{sub_key}: {sub_value[i] if sub_key != 'IDM' else 'IDM omitted for brevity'}", file)

with open('results.json', 'w',encoding='utf8') as outfile:
    json.dump(conversion(Results_smiles), outfile, ensure_ascii=False, indent=4)

finish()
