# -*- coding: UTF-8 -*-
import re
import os
import numpy as np
from scm.plams import *

def rkf_paths(path):
    """
    This function gets rkf paths for all conformers.
    """
    direcotry_path = os.path.dirname(path)
    score_directories = []
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(direcotry_path):
        # Filter directoires. Sanity check [just Score_*/ directories]
        score_dirs = [os.path.join(root, d) for d in dirs if d.startswith('Score')]
        score_directories.extend(score_dirs)
        break
    score_directories.sort(key=lambda d: int(d.split('_')[-1]))
    return score_directories

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

def to_lower_dict(d):
    return {key.lower(): value for key, value in d.items()}

def format_list(key, values, max_values_per_line=5):
    if isinstance(values, (np.float, float, int)):
        values = [values]

    if all(isinstance(v, str) for v in values):
        formatter = "{:2}"
    else:
        formatter = "{:>8}"

    formatted_lines = []
    line = f"{key}: "
    item_in_line = 0
    for i, value in enumerate(values):
        formatted_value = formatter.format(value)
        if item_in_line > 0:
            line += ", "
        line += formatted_value
        item_in_line += 1
        if item_in_line == max_values_per_line or i == len(values) - 1:
            formatted_lines.append(line)
            line = " " * (len(key) + 2)
            item_in_line = 0

    formatted_output = "\n".join(formatted_lines)
    return formatted_output

def int_to_str_with_zeros(number, length=3):
    return str(number).zfill(length)

