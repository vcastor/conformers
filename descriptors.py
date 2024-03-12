# -*- coding: UTF-8 -*-
import numpy as np
from small_functions import *

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
