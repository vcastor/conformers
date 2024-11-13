# -*- coding: UTF-8 -*-
# Just settings for the solvent in ADF
from scm.plams import Settings

def solvent_name(molecule, solvent):
    """
    ADF input case insensitive, but the solvent name must be correct.
    """
    if "/" in list(solvent.split()):
        dbfile = '/home/vcastor/Documents/nucleo/nucleo_data.db'
        conn = sqlite3.connect(dbfile)
        cursor = conn.cursor()
        query = 'SELECT epsilon, rad FROM main WHERE smiles = ? AND solvent = ?'
        cursor.execute(query, (molecule, solvent))
        result = cursor.fetchone()
        conn.close()
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
    return solvent

def solvent_settings(solvent):
    """
    ADF input needs some extra information, not only the name of the solvent.
    """
    settings = Settings()
    # Constant, linear terms of Ecd
    # taken from ADF code $AMSHOME/src/lib/dft/solvation/SolventConfig.f90
    # (T. N. Truong, E. V. Stefanovich, Chem. Phys. Lett 240 , 253-260 (1995)
    cav0, cav1 = 0.0, 0.0067639
    solvent = solvent_name(solvent)
    settings.input.ADF.Solvation.Solv = f'name={solvent} cav0={cav0} cav1={cav1}'
    settings.input.ADF.Solvation.Charged = 'method=CONJ'
    settings.input.ADF.Solvation.SCF = 'VAR ALL'
    settings.input.ADF.Solvation.Surf = 'Delley'
    return settings

