# -*- coding: UTF-8 -*-
# Just settings for the solvent in ADF
import sqlite3
from scm.plams import Settings

def solvent_name(solvent, database):
    """
    epsilon and rad from the database when it has them (mixtures, neat liquids),
    otherwise the ADF name (ADF input case insensitive, but the name must be correct).
    """
    if 'solvents' in database:
        conn = sqlite3.connect(database['path'])
        result = conn.execute(database['solvents'], (solvent,)).fetchone()
        conn.close()
        if result and result[0] is not None and result[1] is not None:
            return f'epsilon={result[0]} rad={result[1]}'
    solvent_mapping = {
        'thf' : 'Tetrahydrofuran',
        'mecn': 'Acetonitrile',
        'dimethyl sulfoxide': 'DMSO',
        'dimethylsulfoxide' : 'DMSO',
        'dcm' : 'Dichloromethane',
        'dmf' : 'DMFA',
        'dimethylformamide' : 'DMFA',
        'et2o': 'DiethylEther',
        'diethyl ether': 'DiethylEther'
    }
    normalized_solvent = solvent.lower()
    # Update the solvent name if it is the dictionary
    if normalized_solvent in solvent_mapping:
        solvent = solvent_mapping.get(normalized_solvent)
    return f'name={solvent}'

def solvent_settings(solvent, freq_branch=False):
    """
    ADF input needs some extra information, not only the name of the solvent.
    """
    settings = Settings()
    # Constant, linear terms of Ecd
    # taken from ADF code $AMSHOME/src/lib/dft/solvation/SolventConfig.f90
    # (T. N. Truong, E. V. Stefanovich, Chem. Phys. Lett 240 , 253-260 (1995)
    cav0, cav1 = 0.0, 0.0067639
    settings.input.ADF.Solvation.Solv = f'{solvent} cav0={cav0} cav1={cav1}'
    settings.input.ADF.Solvation.Charged = 'method=CONJ'
    settings.input.ADF.Solvation.SCF = 'VAR ALL'
    if freq_branch:
        settings.input.ADF.Solvation['C-Mat'] = 'POT'
        settings.input.ADF.Solvation['CSMRSP'] = ''
    else:
        settings.input.ADF.Solvation.Surf = 'Delley'
    return settings

