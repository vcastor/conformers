# -*- coding: UTF-8 -*-
import os
import sys
from .gvariables import gconfig
import pandas as pd

def get_input_file():
    """
    This function takes the input file from the positional arguments.
    """
    input_file = next((os.path.abspath(arg) for arg in sys.argv[1:] if arg.endswith('.csv')), None)
    if input_file:
        gconfig['input_file_name'] = input_file
        return input_file
    else:
        print("Run the script like:\n $AMSBIN/plams Workflow.py -v input_file.csv")
        sys.exit("No input file found")

def input_reader(filepath):
    """
    This function reads the list of molecules and settings from a file.

    Parameters:
    - filepath: the file path
    Returns:
    - systems:  dictionary, each containing the SMILES and solvent
    - settings: a dictionary with the settings (for all systems)
    """
    data = pd.read_csv(filepath, comment='#', header=None, skip_blank_lines=True)

    systems, settings = [], {}

    key_variations = {
        'functional': ['xc', 'exchange-correlation', 'exchange correlation', 'functional', 'xc functional'],
        'basis set' : ['basis', 'basis set', 'basisset'],
        'dispersion': ['dispersion', 'dispersion correction', 'dispersion method'],
        'RMSD'  : ['root mean square deviation', 'root mean square deviation of atomic positions', 'rmsd'],
        'model' : ['model', 'dftb', 'dftmodel', 'dftb model', 'dftb method', 'dft-b'],
        'score E threshold': ['score e', 'score energy', 'delta energy 1', 'score energy threshold',
                              'score e threshold', 'energy threshold score'],
        'optimize E threshold': ['optimize e', 'optimize energy', 'delta energy 2',
                                 'optimize energy threshold', 'optimize e threshold', 'energy threshold optimize'],
        'temperature' : ['temp', 't', 'temperature'],
        'n conformers': ['n conformers', 'conformers', 'number of conformers'],
        'relativity'  : ['relativity', 'relativistic', 'relativistic effects'],
        'core' : ['core', 'basis core', 'core basis']
    }

    # On change la direction du dictionnaire, pour pouvoir faire la correspondance entre les variations et les clés
    reverse_map = {variation.lower(): key for key, variations in key_variations.items() for variation in variations}

    # Extract the systems and settings
    for _, row in data.iterrows():
        first_element = row[0].strip()
        if first_element.lower() in reverse_map:
            key = reverse_map[first_element.lower()]
            settings[key] = str(row[1]).strip() if pd.notna(row[1]) else None
        else:
            solvent = row[1].strip() if pd.notna(row[1]) else None
            systems.append({'smiles': first_element, 'solvent': solvent})

    systems = process_systems(systems)

    # Default settings (frozen core and no relativistic effects)
    settings['relativity'] = settings.get('relativity', 'None')
    settings['core'] = settings.get('core', 'None')

    # Validate all expected settings are present
    for setting_key in key_variations:
        if setting_key not in settings and setting_key != 'dispersion':
            raise ValueError(f"Missing setting '{setting_key}'")

    # Default setting, no dispersion if not provided
    settings['dispersion'] = settings.get('dispersion', None)

    return systems, settings

def process_systems(systems):
    """
    This function check for duplicate systems in the input file
    and deletes the duplicates.
    """

    seen = set()
    unique = []
    for system in systems:
        identifier = (system['smiles'], system['solvent'])
        if identifier not in seen:
            seen.add(identifier)
            unique.append(system)
        else:
            print('{:*^72}'.format(' input waring '))
            print(f"Duplicated system detected: {identifier}, will be computed once.")

    gconfig['total_systems'] = len(unique)
    return unique

def validate_settings(settings):
    """ 
    Validates the settings.
    Parameters: settings (a dictionary)

    Raises a ValueError if any of the settings are invalid.
    """
    expected_settings = { 
        'temperature': float,
        'n conformers': int,
        'RMSD': float,
        'score E threshold': float,
        'optimize E threshold': float,
    }   

    validated_settings = {}
    for key, expected_type in expected_settings.items():
        value = settings.get(key)
        try:
            converted_value = expected_type(value)
            if converted_value < 0:
                raise ValueError(f"{key} must be a {expected_type} non-negative")
            validated_settings[key] = converted_value
        except ValueError:
            raise ValueError(f"Invalid value for {key} setting")

    if validated_settings['optimize E threshold'] < validated_settings['score E threshold']:
        raise ValueError("Score (single point) E threshold must be smaller than the optimize E threshold")

    # The rest of the settings are not validated (for now)
    for key, value in settings.items():
        if key not in validated_settings:
            validated_settings[key] = value

    gconfig['temperature'] = validated_settings['temperature']

    return validated_settings

def backwards_path():
    """
    It returns the path of a previous calculation, be careful, it only works.
    """
    backwards = next((os.path.abspath(arg) for arg in sys.argv[1:] if arg.endswith('/')), None)
    if backwards:
        gconfig['input_file_name'] = backwards + 'backwards.csv'
        return backwards
    else:
        sys.exit("No backwards directory found")

