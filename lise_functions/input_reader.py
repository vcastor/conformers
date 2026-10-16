# -*- coding: UTF-8 -*-
import os
import sys
import json

PROPERTIES = ('entropy', 'nucleophilicity')

def get_input_file():
    input_file = next((os.path.abspath(arg) for arg in sys.argv[1:] if arg.endswith('.json')), None)
    if input_file:
        return input_file
    else:
        print("Run the script like:\n $AMSBIN/plams filter.py -v config.json")
        sys.exit("No configuration file found")

def input_reader(filepath):
    with open(filepath, 'r') as file:
        config = json.load(file)

    expected_settings = {
        'temperature': float,
        'conformers': int,
        'Eopt': float,
        'Escore': float,
        'RMSDopt': float,
        'RMSDscore': float
    }
    for key in ['properties', 'database', 'systems', 'model', 'functional', 'basis', *expected_settings]:
        if key not in config:
            raise ValueError(f"Missing setting '{key}'")

    for key, expected_type in expected_settings.items():
        try:
            config[key] = expected_type(config[key])
        except (TypeError, ValueError):
            raise ValueError(f"Invalid value for {key} setting")
        if config[key] < 0:
            raise ValueError(f"{key} must be a {expected_type} non-negative")

    if config['Eopt'] < config['Escore']:
        raise ValueError("Score (single point) E threshold must be smaller than the optimize E threshold")

    config['properties'] = sorted(set(config['properties']))
    if not config['properties'] or not set(config['properties']) <= set(PROPERTIES):
        raise ValueError(f"properties must be taken from {PROPERTIES}")

    for key in ['path', 'table']:
        if key not in config['database']:
            raise ValueError(f"Missing database setting '{key}'")
    # Relative to the configuration file
    config['database']['path'] = os.path.join(os.path.dirname(filepath), config['database']['path'])

    # Default settings (no dispersion, frozen core and no relativistic effects)
    config['dispersion'] = config.get('dispersion')
    config['core'] = config.get('core', 'None')
    config['relativity'] = config.get('relativity', 'None')

    config['systems'] = process_systems(config['systems'])

    return config

def process_systems(systems):
    """
    This function deletes the duplicated systems.
    A system without solvent is computed in gas phase.
    """
    seen, unique = set(), []
    for system in systems:
        identifier = (system['smiles'], system.get('solvent'))
        if identifier not in seen:
            seen.add(identifier)
            unique.append({'smiles': identifier[0], 'solvent': identifier[1]})
    return unique

