# -*- coding: UTF-8 -*-
import os
import sys
import pandas as pd

def get_input_file():
    """
    This function takes the input file from the positional arguments.
    """
    for arg in sys.argv[1:]:
        if arg.endswith('.csv'):
            return os.path.abspath(arg)
    print("Run the script like:\n $AMSBIN/plams Workflow.py -v input_file.csv")
    sys.exit("No input file found")

def input_reader(filepath):
    """
    This function reads the list of molecules and settings from a file.

    Parameters:
    - filepath: the path to the file
    Returns:
    - systems: dictionary, each containing the SMILES and solvent
    - settings: a dictionary with the settings (for all systems)
    """
    data = pd.read_csv(filepath, comment='#', header=None, skip_blank_lines=True)

    systems, settings = [], {}

    key_variations = {
        'functional': ['xc', 'exchange-correlation', 'exchange correlation', 'functional', 'xc functional'],
        'basis set' : ['basis', 'basis set'],
        'dispersion': ['dispersion', 'dispersion correction', 'dispersion method'],
        'RMSD': ['root mean square deviation', 'root mean square deviation of atomic positions', 'rmsd'],
        'score E threshold': ['score e', 'score energy', 'delta energy 1', 'score energy threshold',
                                 'score e threshold', 'energy threshold score'],
        'optimize E threshold': ['optimize e', 'optimize energy', 'delta energy 2',
                                 'optimize energy threshold', 'optimize e threshold', 'energy threshold optimize'],
        'temperature' : ['temp', 't', 'temperature'],
        'n conformers': ['n conformers', 'conformers', 'number of conformers'],
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

    # Validate all expected settings are present
    for setting_key in key_variations:
        if setting_key not in settings:
            raise ValueError(f"Missing setting '{setting_key}'")

    return systems, settings

def validate_settings(settings):
    """ 
    Validates the settings.
    Parameters: settings (a dictionary)

    Raises a ValueError if any of the settings are invalid
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
                raise ValueError(f"{key} must be non-negative")
            if key == 'n conformers' and converted_value < 1:
                raise ValueError("Number of conformers must be positive")
            validated_settings[key] = converted_value
        except ValueError:
            raise ValueError(f"Invalid value for setting '{key}'")

    if validated_settings['optimize E threshold'] >= validated_settings['score E threshold']:
        raise ValueError("Score E threshold must be less than optimize E threshold")

    # The rest of the settings are not validated (for now)
    for key, value in settings.items():
        if key not in validated_settings:
            validated_settings[key] = value

    return validated_settings
