# -*- coding: UTF-8 -*-
import numpy as np
from scm.plams import *


def ponderated(description):
    """
    This function ponderates the descriptors.
    """
    exp_idm = np.exp(-description['distances'])

    # Ponderation
    for key, values in description.items():
        if key in {'weights', 'distances', 'orbitalE', 'cdftm'}:
            continue

        elif key in {'qtaimcharge', 'hirshfeld', 'electrostatic', 'condensed_linear'}:
            description[key] = np.dot(exp_idm, values)

        elif key in ['cdfta', 'fukui', 'dual', 'condensed']:
            ndes = description[key].shape[1]
            description[key] = np.einsum('ij,ki->kj', description[key], exp_idm)

    return description

