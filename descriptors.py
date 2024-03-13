# -*- coding: UTF-8 -*-
import numpy as np
from scm.plams import *
from small_functions import *

def get_atoms(system):
    """ Number of atoms and atom types """
    molecule = from_smiles(system)
    natoms = len(molecule)
    type_atoms = [atom.symbol for atom in molecule]
    return natoms, type_atoms

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
