# -*- coding: UTF-8 -*-
# Just settings for the solvent in ADF
from scm.plams import Settings

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
    if normalized_solvent in solvent_mapping:
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
