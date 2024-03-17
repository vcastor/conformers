# -*- coding: UTF-8 -*-
import re
import numpy as np
from scm.plams import *

def score_paths(path, adf_results):
    """
    This function just gets full Score job paths and sorts them.
    14 charactes :: conformers.rkf
    """
    paths = [
        path[0:len(path)-14] + str(element)
        for element in adf_results.files
        if 'Score' in element
        and element.endswith('.out')
        and 'CreateAtoms.out' not in element
    ]
    return sorted(paths, key=extract_number)


def conversion(dic):
    """
    Exporting the results as needed by json.dumps
    """
    if isinstance(dic, dict):
        new_dic = {str(key.tolist()) if isinstance(key, np.ndarray) else str(key): conversion(value) for key, value in dic.items()}
        return new_dic
    if isinstance(dic, list):
        return [conversion(item) for item in dic]
    elif isinstance(dic, np.ndarray):
        return dic.tolist()
    else:
        return dic

def extract_number(string):
    number_extractor_re = re.compile(r'Score_(\d+)\.out')
    match = re.search(r'Score_(\d+)\.out', string)
    if match:
        return int(match.group(1))
    else:
        return 0

def to_lower_dict(d):
    """Converts dictionary keys to lowercase."""
    return {key.lower(): value for key, value in d.items()}

def format_list(values, max_values_per_line=7):
    formatted_output = ""
    values = [values.tolist() if isinstance(values, np.ndarray) else values]
    for i, value in enumerate(values):
        if i % max_values_per_line == 0 and i > 0:
            formatted_output += ",\n         "
        elif i > 0:
            formatted_output += ", "
        formatted_output += repr(value)
    return formatted_output.strip()

def int_to_str_with_zeros(number, length=3):
    return str(number).zfill(length)

