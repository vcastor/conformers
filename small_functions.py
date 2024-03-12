# -*- coding: UTF-8 -*-
import re
import numpy as np

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

def extractor(content, start_marker, end_marker):
    start_marker_pattern = re.compile(start_marker)
    start_index = start_marker_pattern.search(content)
    n = start_index.start()
    #start_index = content.index(start_marker)
    #end_index = content.index(end_marker, start_index + len(start_marker))
    end_index = content.index(end_marker, n)
    table = content[n:end_index].strip()
    return [line.strip() for line in table.split('\n') if line.strip()]

def verification_geom_converged(content):
    return "Geometry optimization converged" in content

def writer(line, file):
    line = str(line)
    print(line)
    file.write(line + '\n')

def to_lower_dict(d):
    """Converts dictionary keys to lowercase."""
    return {key.lower(): value for key, value in d.items()}
