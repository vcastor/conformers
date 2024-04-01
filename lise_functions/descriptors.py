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
    atom_order = atom_order[natoms:] - 1

    # Interactomic distance matrix
    idm = np.array(amsresults.readrkf('Geometry', 'Atomic Distances', file='adf')).reshape(natoms+1, natoms+1)
    idm = idm[1:, 1:]

    # Hirshfeld & QTAIM charges
    qtaim_charges = np.array(amsresults.readrkf('Properties', 'Bader atomic charges', file='adf'))
    qtaim_charges = qtaim_charges[atom_order]
    hirshfeld = np.array(amsresults.readrkf('Properties', 'FragmentCharge Hirshfeld', file='adf'))
    hirshfeld = hirshfeld[atom_order]

    # FIXME: should we read everything from the TAPE21?
    description = {
        'weights' : pops,
        'IDM': idm,
        'qtaimcharge': qtaim_charges,
        'Hirshfeld': hirshfeld,
        's2': s2(natoms, content),
        'OE': orbital_energies(content),
        'cdftm': conceptual_dft_mol(content),
        'cdfta': conceptual_dft_atom(natoms, content),
        'fukui': fukui_functions(natoms, content),
        'dual': dual_descriptor(natoms, content),
        'condensed': condensed_local(natoms, content)
    }

    return description


def distance_matrix(natoms, content):
    """
    Interatomic Distance Matrix
    """
    start_marker = " ATOMS"
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
    marker_index = content.index(marker) + 5

    s2_values = np.zeros(natoms)
    for i in range(natoms):
        s2_values[i] = content[marker_index+i].split()[-1]

    return np.array(s2_values, dtype=float)

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

def orbital_energies(content):
    """
    Orbital Energies (eV) [only the occupied orbitals]
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

def canonical_ensamble(natoms, amsresults):
    """
    f+, f-, f(2)
    """
    atom_order = np.array(amsresults.readrkf('Geometry', 'atom order index', file='adf'))
    fplus = np.array(amsresults.readrkf('Properties', 'Fukui Fplus', file='adf'))
    fminus = np.array(amsresults.readrkf('Properties', 'Fukui Fminus', file='adf'))
    f2 = np.array(amsresults.readrkf('Properties', 'Koopmans DD', file='adf'))
    fplus = fplus[atom_order[natoms:]-1]# internal order -> input order
    fminus = fminus[atom_order[natoms:]-1]
    f2 = f2[atom_order[natoms:]-1]
    return fplus, fminus, f2

def grand_canonical(natoms, amsresults):
    """
    S*f+, S*f-, S*f(2)
    """
    atom_order = np.array(amsresults.readrkf('Geometry', 'atom order index', file='adf'))

def conceptual_dft_atom(natoms, content):
    """
    Extract the f+, f-, f(2), S*f+, S*f-, S*f(2)
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

def condensed_local(natoms, content):
    """
    Extract CONDENSED LOCAL ELECTROPHILICITY AND NUCLEOPHILICITY
    """
    marker = " CONDENSED LOCAL ELECTROPHILICITY AND NUCLEOPHILICITY"
    marker_index = content.index(marker) + 5

    condensed_local = np.zeros((natoms, 2))
    for i in range(natoms):
        aux = content[marker_index+i].split()
        condensed_local[i] = content[marker_index+i].split()[3:5]

    return condensed_local

def fukui_functions(natoms, content):
    """
    Extract Fukui mu-*f-
    """
    marker = " COMPOSITE FUKUI FUNCTIONS"
    marker_index = content.index(marker) + 5

    fukui_functions = np.zeros(natoms)
    for i in range(natoms):
        aux = content[marker_index+i].split()
        fukui_functions[i] = aux[4]

    return fukui_functions

def average_properties(molecule):
    weights = molecule['conformers']['weights']
    nconformers = len(weights)
    qtaim_q_avg = np.zeros(molecule['number_atoms'])
    hirshfeld_avg = np.zeros(molecule['number_atoms'])
    s2_avg = np.zeros(molecule['number_atoms'])
    oe_len = sum(len(sublist) for sublist in molecule['conformers']['OE']) // nconformers
    oe_avg = np.zeros(oe_len)
    cdftm_avg = np.zeros(7)
    cdfta_avg = np.zeros((molecule['number_atoms'], 6))
    fukui_avg = np.zeros(molecule['number_atoms'])
    dual_avg = np.zeros((molecule['number_atoms'], 2))
    condensed_avg = np.zeros((molecule['number_atoms'], 2))

    for i, weight in enumerate(weights):
        qtaim_q_avg += weight * np.array(molecule['conformers']['qtaimcharge'][i])
        hirshfeld_avg += weight * np.array(molecule['conformers']['Hirshfeld'][i])
        s2_avg += weight * np.array(molecule['conformers']['s2'][i])
        oe_avg += weight * np.array(molecule['conformers']['OE'][i])
        cdftm_avg += weight * np.array(molecule['conformers']['cdftm'][i])
        cdfta_avg += weight * np.array(molecule['conformers']['cdfta'][i])
        fukui_avg += weight * np.array(molecule['conformers']['fukui'][i])
        dual_avg += weight * np.array(molecule['conformers']['dual'][i])
        condensed_avg += weight * np.array(molecule['conformers']['condensed'][i])

    oe_avg = np.round(oe_avg, 3)
    return {
        'qtaimcharge' : qtaim_q_avg,
        'Hirshfeld': hirshfeld_avg,
        's2': s2_avg,
        'OE': oe_avg,
        'cdftm': cdftm_avg,
        'cdfta': cdfta_avg,
        'fukui': fukui_avg,
        'dual': dual_avg,
        'condensed': condensed_avg
    }

