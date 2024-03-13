# -*- coding: UTF-8 -*-
import re
import numpy as np
from scm.plams import *

def score_paths(path, adf_results):
    """
    This function just gets full Score job paths and sorts them.
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
    Exporting the results to a JSON file
    """
    if isinstance(dic, (list, np.ndarray)):
        return [conversion(item) for item in dic]
    elif isinstance(dic, dict):
        return {key: conversion(value) for key, value in dic.items()}
    elif isinstance(dic, np.ndarray):
        return dic.tolist()
    return dic

def extract_number(string):
    number_extractor_re = re.compile(r'Score_(\d+)\.out')
    match = re.search(r'Score_(\d+)\.out', string)
    if match:
        return int(match.group(1))
    else:
        return 0

def verification_geom_converged(content):
    return "Geometry optimization converged" in content

def writer(line, file):
    line = str(line)
    print(line)
    file.write(line + '\n')

def to_lower_dict(d):
    """Converts dictionary keys to lowercase."""
    return {key.lower(): value for key, value in d.items()}
