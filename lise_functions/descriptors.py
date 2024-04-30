# -*- coding: UTF-8 -*-
import numpy as np
from scm.plams import *
from .small_functions import *

def get_atoms(system):
    """ Number of atoms and atom types """
    molecule = from_smiles(system)
    type_atoms = [atom.symbol for atom in molecule]
    return len(molecule), type_atoms

def descriptors(natoms, pathdir, pops):
    """
    This function calls for the extraction of descriptors dynamically from
    the output plain text file and from the TAPE21.
    """
    import os
    from scm.plams.tools.units import Units
    # Open the TAPE 21
    resultpath = os.path.join(pathdir, 'ams.rkf')
    amsrkf = AMSJob.load_external(resultpath)
    amsresults = amsrkf.results
    # Open the plain text output file
    dirname = os.path.basename(pathdir)
    outfile = os.path.join(pathdir, dirname + '.out')
    with open(outfile, 'r', encoding="ISO-8859-1") as f:
        content = f.read()
    content = content.split('\n')
    # In the TAPE 21 descriptors are written in the internal order
    atom_order = np.array(amsresults.readrkf('Geometry', 'atom order index', file='adf'))
    # internal order -> input order [FORTRAN counting]
    atom_order = atom_order[:natoms] - 1

    # Interactomic distance matrix
    idm = np.array(amsresults.readrkf('Geometry', 'Atomic Distances', file='adf')).reshape(natoms+1, natoms+1)
    idm = Units.conversion_ratio('bohr','angstrom')*idm[1:, 1:]
    idm = idm[atom_order, :][:, atom_order]

    # Hirshfeld & QTAIM charges
    qtaim_charges = np.array(amsresults.readrkf('Properties', 'Bader atomic charges', file='adf'))
    qtaim_charges = qtaim_charges[atom_order]
    hirshfeld = np.array(amsresults.readrkf('Properties', 'FragmentCharge Hirshfeld', file='adf'))
    hirshfeld = hirshfeld[atom_order]

    # should we read everything from the TAPE21?
    description = {
        'weights' : pops,
        'distances': idm,
        'qtaimcharge': qtaim_charges,
        'hirshfeld': hirshfeld,
        'orbitalE': orbital_energies(content),
        'cdftm': conceptual_dft_mol(content),
        'cdfta': canonical_grandcanonical(natoms, content),
        'fukui': fukui_functions(natoms, content),
        'dual': dual_descriptor(natoms, content),
        'condensed': condensed_local(natoms, content)
    }

    return description

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
    oe_len = sum(len(sublist) for sublist in molecule['conformers']['orbitalE']) // nconformers

    properties_avg = {
        'qtaimcharge': np.zeros(molecule['number_atoms']),
        'hirshfeld': np.zeros(molecule['number_atoms']),
        'orbitalE': np.zeros(oe_len),
        'cdftm': np.zeros(7),
        'cdfta': np.zeros((molecule['number_atoms'], 6)),
        'fukui': np.zeros(molecule['number_atoms']),
        'dual': np.zeros((molecule['number_atoms'], 2)),
        'condensed': np.zeros((molecule['number_atoms'], 2))
    }

    # Loop through each conformer property to calculate weighted averages
    for prop in properties_avg.keys():
        for i, weight in enumerate(weights):
            prop_array = np.array(molecule['conformers'][prop][i])
            properties_avg[prop] += weight * prop_array

    properties_avg['orbitalE'] = np.round(properties_avg['orbitalE'], 3)

    return properties_avg

