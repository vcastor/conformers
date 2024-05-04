# -*- coding: UTF-8 -*-
import numpy as np
from scm.plams import *
from .small_functions import *

def get_atoms(system):
    """ Number of atoms and atom types """
    molecule = from_smiles(system)
    type_atoms = [atom.symbol for atom in molecule]
    return len(molecule), type_atoms

def entropy(natoms, pathdir, pops):
    """
    This function calls for the extraction of descriptors dynamically from
    the output plain text file and from the TAPE21.
    """
    import os
    from scm.plams.tools.units import Units
    plamsdir = os.path.dirname(pathdir)
    outfile = os.path.join(plamsdir, os.path.basename(plamsdir) + '.out')
    cmd = 'grep "Entropy (cal/mol-K)" ' + outfile
    line = os.popen(cmd).read().split()
    # Vibrational, rotational and translational entropies
    temp = float(line[0])
    transS = float(line[3])
    rotS = float(line[4])
    vibS = float(line[5])
    transS = Units.conversion_ratio('kcal/mol', 'kJ/mol')*transS
    rotS = Units.conversion_ratio('kcal/mol', 'kJ/mol')*rotS
    vibS = Units.conversion_ratio('kcal/mol', 'kJ/mol')*vibS

    # should we read everything from the TAPE21?
    return {
        'weights' : pops,
        'translational' : transS,
        'rotational' : rotS,
        'vibrational' : vibS
    }


def orbital_energies(content):
    """
    Orbital Energies (eV) [only the occupied orbitals]
    It should never return an empty list, but just in case, if something
    goes wrong in ADF calculations.
    """
    marker = " Orbital Energies, per Irrep and Spin:" 
    E_ev = []

    try:
        marker_index = content.index(marker) + 5
    except ValueError:
        return E_ev # Return an empty list

    for line in content[marker_index:]:
        parts = line.split()
        if parts[1] == '2.000':
            E_ev.append(parts[3])
        else:
            break

    return np.array(E_ev, dtype=float)

def conceptual_dft_mol(content):
    """
    Extract the chemical potential, hardness, and softness
    """
    marker = " GLOBAL DESCRIPTORS"
    marker_index = content.index(marker) + 3
    global_descriptors = np.zeros(7)
    #Electronic chemical potential
    global_descriptors[0] = float(content[marker_index].split()[5])
    #Hardness
    global_descriptors[1] = float(content[marker_index+4].split()[3])
    #Electrophilicity index
    global_descriptors[2] = float(content[marker_index+7].split()[4])
    #nucleofuge
    global_descriptors[3] = float(content[marker_index+8].split()[4])
    #elctrofuge
    global_descriptors[4] = float(content[marker_index+9].split()[4])
    #Electrodonating
    global_descriptors[5] = float(content[marker_index+10].split()[4])
    #Electroaccepting
    global_descriptors[6] = float(content[marker_index+11].split()[3])

    return global_descriptors

def canonical_grandcanonical(natoms, content):
    """
    Extract the f+, f-, f(2), S*f+, S*f-, s(2)
    """
    marker = " ATOMIC DESCRIPTORS: CANONICAL ENSEMBLE"
    marker_index = content.index(marker) + 5

    atomic_descriptors = np.zeros((natoms, 6))
    for i in range(natoms):
        aux = content[marker_index+i].split()
        atomic_descriptors[i, :3] = aux[3:5] + [aux[6]]
    
    marker = " ATOMIC DESCRIPTORS: GRAND CANONICAL ENSEMBLE"
    marker_index = content.index(marker) + 5
    for i in range(natoms):
        aux = content[marker_index+i].split()
        atomic_descriptors[i, 3:] = aux[3:5] + [aux[6]]

    return atomic_descriptors

def fukui_functions(natoms, content):
    """
    Extract Fukui mu-*f-
    """
    marker = " COMPOSITE FUKUI FUNCTIONS"
    marker_index = content.index(marker) + 5

    fukui_functions = np.zeros(natoms)
    for i in range(natoms):
        fukui_functions[i] = content[marker_index+i].split()[4]

    return fukui_functions

def dual_descriptor(natoms, content):
    """
    Composite Dual Descriptor
    """
    marker = " COMPOSITE DUAL DESCRIPTORS"
    marker_index = content.index(marker) + 5

    dual_descriptor = np.zeros((natoms, 2))
    for i in range(natoms):
        dual_descriptor[i] = content[marker_index+i].split()[3:5]

    return dual_descriptor

def condensed_local(natoms, content):
    """
    Extract condensed local electrophilicity and nucleophilicity
    """
    marker = " CONDENSED LOCAL ELECTROPHILICITY AND NUCLEOPHILICITY"
    marker_index = content.index(marker) + 5

    condensed_local = np.zeros((natoms, 2))
    for i in range(natoms):
        aux = content[marker_index+i].split()
        condensed_local[i] = content[marker_index+i].split()[3:5]

    return condensed_local

def average_properties(molecule):
    weights = molecule['conformers']['weights']
    nconformers = len(weights)

    entrop_avg = {
        'translational': 0,
        'rotational': 0,
        'vibrational': 0
    }

    for entrop in entrop_avg:
        for i, weight in enumerate(weights):
            val = molecule['conformers'][entrop][i]
            entrop_avg[entrop] += weight * val
        
    return entrop_avg

