# -*- coding: UTF-8 -*-
import numpy as np
from scm.plams import *
from .small_functions import *

def entropy_cdft(natoms, pathdir, pops):
    """
    This function calls for the extraction of descriptors dynamically from
    the output plain text file and from the TAPE21.
    """
    import os
    from scm.plams.tools.units import Units
    plamsdir = os.path.dirname(pathdir)
    outfile  = os.path.join(plamsdir, os.path.basename(plamsdir) + '.out')
    # Entropy
    cmd  = 'grep "Entropy (cal/mol-K)" ' + outfile
    line = os.popen(cmd).read().split()
    # Vibrational, rotational and translational entropies [without correction]
    temp, transS, rotS, vibS, totS = map(float, [line[0], line[3], line[4], line[5], line[6]])
    transS, rotS, vibS, totS = [Units.conversion_ratio('kcal/mol', 'kJ/mol')*s for s in (transS, rotS, vibS, totS)]
    # -T*S correction [low frequency modes]
    cmd = 'grep "\-T\*S" ' + outfile
    lines = os.popen(cmd).read().split('\n')
    ts  = float(lines[0].split()[1])
    cts = float(lines[1].split()[2])
    correction = -(cts - ts)*Units.conversion_ratio('hartree', 'kJ/mol')*1000/temp
    # Check if all Frequencies are positive
    cmd   = 'grep -A 4 "Normal Mode Frequencies" ' + outfile
    lines = os.popen(cmd).read().split('\n')
    if float(lines[-2].split()[1]) < 0:
        print('At least one frequency is negative')
        print('Check the output file:', outfile)
    # Conceptual DFT
    with open(outfile, 'r', encoding="ISO-8859-1") as f:
        content = f.read()
    content = content.split('\n')
    # should we read everything from the TAPE21?
    return {
        'weights' : pops,
        'translational' : transS,
        'rotational' : rotS,
        'vibrational' : vibS,
        'correction' : correction,
        'cdftm': conceptual_dft_mol(content)
    }


def conceptual_dft_mol(content):
    """
    Extract the chemical potential, hardness, and softness
    """
    marker = " GLOBAL DESCRIPTORS"
    marker_index = content.index(marker) + 3
    global_descriptors = np.zeros(3)
    #Electronic chemical potential
    global_descriptors[0] = float(content[marker_index].split()[5])
    #Hardness
    global_descriptors[1] = float(content[marker_index+4].split()[3])
    #Hyperhardness
    global_descriptors[2] = float(content[marker_index+6].split()[3])
    return global_descriptors

def average_properties(molecule):
    weights = molecule['conformers']['weights']
    avg = {
        'translational': 0,
        'rotational': 0,
        'vibrational': 0,
        'correction': 0,
        'cdftm': np.zeros(3)
    }
    for prop in avg.keys():
        for i, weight in enumerate(weights):
            val = np.array(molecule['conformers'][prop][i])
            avg[prop] += weight*val
    return avg

