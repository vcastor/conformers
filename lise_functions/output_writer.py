# -*- coding: UTF-8 -*-
from .small_functions import *
from .writer_helper import table_formatter, entropy_formatter
import numpy as np

def plain_text_output(output_file, system_results, formatter):
    with open(output_file, "w", encoding="utf-8") as file:
        for nsystem in system_results:
            system = system_results[nsystem]
            string_smile = ' {} '.format(system['smiles'])
            string_smile = '{:=^72}'.format(string_smile)
            string_solvent = ' {} '.format(system['solvent'])
            string_solvent = '{:*^72}'.format(string_solvent)
            file.write(f'{string_smile}\n')
            file.write(f'{string_solvent}\n')
            for key, value in system.items():
                if key == 'number_conformers' or key == 'number_atoms':
                    file.write(f'{key}: {value}\n')
                elif key == 'average' and system['number_conformers'] > 1:
                    string_average = '{:-^72}'.format(' Average ')
                    file.write(f'{string_average}\n')
                    formatted_average = formatter(system['atoms'], value)
                    file.write(f'{formatted_average}\n')
                elif key == 'conformers':
                    systems_aux = []
                    for i in range(system['number_conformers']):
                        aux_data = {subkey: subvalue[i] if isinstance(subvalue, list) else subvalue for subkey, subvalue in value.items()}
                        systems_aux.append(aux_data)
                    for j in range(system['number_conformers']):
                        string_conformer = '{:-^72}'.format(f' Conformer {j+1} ')
                        file.write(f'{string_conformer}\n')
                        file.write(f"Weight: {value['weights'][j]}\n")
                        formatted_conformer = formatter(system['atoms'], systems_aux[j])
                        file.write(f'{formatted_conformer}\n')

def json_writer(outfile, system_results):
    import json
    with open(outfile, "w", encoding="utf-8") as file:
        json.dump(conversion(system_results), file, ensure_ascii=False, indent=4)

def output_writer(system_results, name):
    out_file = name + '.out'
    plain_text_output(out_file, system_results, table_formatter)
    # JSON output [It is written for the ML, DO NOT CHANGE]
    json_file = name + '.json'
    jsonresults = {}
    for smileskey, molecule in system_results.items():
        smiles = molecule['smiles']
        s2 = np.concatenate([arr[:, 5] for arr in molecule['conformers']['cdfta']])
        auxmol = {'number_atoms': molecule['number_atoms'],
                  'atoms': molecule['atoms'],
                  'number_conformers': molecule['number_conformers'],
                  'conformers': {'weights': molecule['conformers']['weights'],
                                 'IDM': molecule['conformers']['distances'],
                                 'Hirshfeld': molecule['conformers']['hirshfeld'],
                                 's2': s2,
                                 'OE': molecule['conformers']['orbitalE']}}
        jsonresults[smiles] = auxmol
    json_writer(json_file, jsonresults)

def entropy_writer(system_results, name):
    out_file = name + '.out'
    plain_text_output(out_file, system_results, lambda atoms, data: entropy_formatter(data))
