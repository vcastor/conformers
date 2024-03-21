# -*- coding: UTF-8 -*-
import numpy as np
from scm.plams import *
from .small_functions import *

def get_atoms(system):
    """ Number of atoms and atom types """
    molecule = from_smiles(system)
    type_atoms = [atom.symbol for atom in molecule]
    return len(molecule), type_atoms

def distance_matrix(natoms, content):
    """
    Interatomic Distance Matrix
    """
    start_marker = " ATOMS"
    content = content.split('\n')
    marker_index = content.index(start_marker) + 4
    coord_lines = content[marker_index:marker_index+natoms]

    coords = np.zeros((natoms, 3))
    for i in range(natoms):
        coords[i] = coord_lines[i].split()[2:5]

    # Calculate the interatomic distance matrix
    distance_mat = np.zeros((natoms, natoms))
    for i in range(natoms):
        for j in range(i+1, natoms):
            distance_mat[i, j] = np.linalg.norm(coords[i] - coords[j])
            distance_mat[j, i] = distance_mat[i, j]
    
    return distance_mat

def s2(natoms, content):
    """
    Grand Canonical Ensemble
    """
    marker = " ATOMIC DESCRIPTORS: GRAND CANONICAL ENSEMBLE"
    content = content.split('\n')
    marker_index = content.index(marker) + 5

    s2_values = np.zeros(natoms)
    for i in range(natoms):
        s2_values[i] = content[marker_index+i].split()[-1]

    return np.array(s2_values, dtype=float)

def hirshfeld(natoms, content):
    """
    Extract Hirshfeld values.
    """
    marker = " H I R S H F E L D   C H A R G E   A N A L Y S I S"
    content = content.split('\n')
    marker_index = content.index(marker) + 11
    
    hirshfeld_values = np.zeros(natoms)
    for i in range(natoms):
        hirshfeld_values[i] = content[marker_index+i].split()[2]
    
    return hirshfeld_values

def orbital_energies(content):
    """
    Orbital Energies (eV) [only the occupied orbitals]
    """
    marker = " Orbital Energies, per Irrep and Spin:" 
    content = content.split('\n')
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
    content = content.split('\n')
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
    global_descriptors[6] = float(content[marker_index+11].split()[4])

    return global_descriptors

def conceptual_dft_atom(natoms, content):
    """
    Extract the f+, f-, f(2), S*f+, S*f-, S*f(2)
    """
    marker = " ATOMIC DESCRIPTORS: CANONICAL ENSEMBLE"
    content = content.split('\n')
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

def condensed_local(natoms, content):
    """
    Extract CONDENSED LOCAL ELECTROPHILICITY AND NUCLEOPHILICITY
    """
    marker = " CONDENSED LOCAL ELECTROPHILICITY AND NUCLEOPHILICITY"
    content = content.split('\n')
    marker_index = content.index(marker) + 5

    condensed_local = np.zeros((natoms, 2))
    for i in range(natoms):
        aux = content[marker_index+i].split()
        condensed_local[i] = content[marker_index+i].split()[3:5]

    return condensed_local


