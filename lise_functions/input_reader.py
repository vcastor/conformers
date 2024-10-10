# -*- coding: UTF-8 -*-
import os
import sys
from .gvariables import gconfig

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
    systems, settings = [], {}

    key_variations = {
        'functional': ['xc', 'exchange-correlation', 'exchange correlation', 'functional', 'xc functional'],
        'basis set' : ['basis', 'basis set', 'basisset'],
        'dispersion': ['dispersion', 'dispersion correction', 'dispersion method'],
        'RMSDopt' : ['root mean square deviation optimization', 'root mean square deviation of atomic positions optimization', 'rmsdopt', 'rmsd opt'],
        'RMSDscore' : ['root mean square deviation score', 'root mean square deviation of atomic positions score', 'rmsdscore', 'rmsd score'],
        'model' : ['model', 'dftb', 'dftmodel', 'dftb model', 'dftb method', 'dft-b'],
        'score E threshold': ['score e', 'score energy', 'delta energy 1', 'score energy threshold',
                              'score e threshold', 'energy threshold score'],
        'optimize E threshold': ['optimize e', 'optimize energy', 'delta energy 2',
                                 'optimize energy threshold', 'optimize e threshold', 'energy threshold optimize'],
        'temperature' : ['temp', 't', 'temperature'],
        'n conformers': ['n conformers', 'conformers', 'number of conformers'],
        'relativity'  : ['relativity', 'relativistic', 'relativistic effects'],
        'core' : ['core', 'basis core', 'core basis']
        # 'nsteps' : ['nsteps', 'number of steps', 'steps'],
        # 'timestep' : ['timestep', 'time step', 'time-step'],
        # 'thermotype' : ['thermotype', 'thermostat type', 'thermostat-type'],
        # 'tau' : ['tau', 'temperature coupling constant', 'thermostat tau']
    }

    # On change la direction du dictionnaire, pour pouvoir faire la correspondance entre les variations et les clés
    reverse_map = {variation.lower(): key for key, variations in key_variations.items() for variation in variations}

    # Read the data from the file
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip().startswith('#'):
                continue
            parts = line.split(',', 1) # Smiles can contain commas
            first_element = parts[0].strip()
            second_element = parts[1].strip() if len(parts) > 1 else None
            if first_element.lower() in reverse_map:
                key = reverse_map[first_element.lower()]
                settings[key] = second_element
            else:
                systems.append({'smiles': first_element, 'solvent': second_element})

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
        if system['smiles'] == '' or system['solvent'] is None:
            continue
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
        'RMSDopt': float,
        'RMSDscore': float,
        'score E threshold': float,
        'optimize E threshold': float
        # 'nsteps' : int,
        # 'timestep' : float,
        # 'thermotype' : str,
        # 'tau' : float
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

def backwards_r(filename):
    """
    It configure the global variable 'input_file_name' to the backwards file.
    """
    csvname = filename.replace('.txt', '_backwards.csv')
    if os.path.exists(filename):
        gconfig['input_file_name'] = csvname
        return filename
    else:
        sys.exit("No backwards directory found")

