# -*- coding: UTF-8 -*-
from .small_functions import format_list

def entropy_formatter(data):
    formatted_str = "Entropy contributions\n"
    formatted_str += f"translational: {data['translational']:9.4f}\n"
    formatted_str += f"rotational   : {data['rotational']:9.4f}\n"
    formatted_str += f"vibrational  : {data['vibrational']:9.4f}\n"
    formatted_str += f"correction   : {data['correction']:9.4f}\n"
    # Conceptual DFT properties (whole system)
    formatted_str += "Global descriptors, Conceptual DFT\n"
    formatted_str += f"Electronic chemical potential: {data['cdftm'][0]:9.4f}\n"
    formatted_str += f"Hardness                     : {data['cdftm'][1]:9.4f}\n"
    formatted_str += f"Hyperhardness                : {data['cdftm'][2]:9.4f}\n"
    return formatted_str

