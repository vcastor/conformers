# -*- coding: UTF-8 -*-
import numpy as np
from scm.plams import *

def ponderated(description, atom):
    """
    This function retunrs just the values that i want to ponderate.
    """
    vals_to_pond = {}

    distances = description.get('distances')[atom]

    qtaimcharge = description.get('qtaimcharge')
    condensed_lr = description.get('condensed_linear')
    electro_potential = description.get('electrostatic')
    population = description.get('population')

    sort_idx = sorted(range(len(distances)), key=lambda k: distances[k])

    vals_to_pond['distances']  = np.array([distances[i] for i in sort_idx])
    vals_to_pond['qtaimcharge']  = np.array([qtaimcharge[i] for i in sort_idx])
    vals_to_pond['condensed_linear']  = np.array([condensed_lr[i] for i in sort_idx])
    vals_to_pond['electrostatic_potential']  = np.array([electro_potential[i] for i in sort_idx])
    vals_to_pond['populations']  = np.array([population[i] for i in sort_idx])

    # vals_to_pond['distances'] = [distances[i] for i in sort_idx]
    # vals_to_pond['qtaimcharge'] = [qtaimcharge[i] for i in sort_idx]
    # vals_to_pond['condensed_linear'] = [condensed_lr[i] for i in sort_idx]
    # vals_to_pond['electrostatic_potential'] = [electro_potential[i] for i in sort_idx]
    # vals_to_pond['populations'] = [population[i] for i in sort_idx]

    vals_to_pond['electrofuge'] = description.get('cdftm')[6]
    vals_to_pond['weights'] = description.get('weights')

    return vals_to_pond

def average_pond(vals_to_pond):
    """
    This function averages the ponderated values.
    """
    weights = vals_to_pond['conformers']['weights']
    nconfs = len(weights)

    vals_avg = {
        'distances': np.zeros(vals_to_pond['number_atoms']),
        'qtaimcharge': np.zeros(vals_to_pond['number_atoms']),
        'condensed_linear': np.zeros(vals_to_pond['number_atoms']),
        'electrostatic_potential': np.zeros(vals_to_pond['number_atoms']),
        'populations': np.zeros(vals_to_pond['number_atoms']),
        'electrofuge': 0.0
    }

    for prop in vals_avg.keys():
        for i, weight in enumerate(weights):
            vals_avg[prop] += weight*np.array(vals_to_pond['conformers'][prop][i])

    return vals_avg

