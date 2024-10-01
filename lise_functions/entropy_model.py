# -*- coding: UTF-8 -*-
import sqlite3
import numpy as np
from scm.plams import *

def entropy_model(data):
    # S = e^(-λ*ε)[α*S_r + β*S_t + γ*S_v + δ*S_v*S_r/S_gas + ζ*S_v*S_t/S_gas]
    # λ: 0.0034
    # α: 0.3440, β: 0.7091, γ: 1.0000, δ: 1.0000, ζ: 0.3454
    lambd = 0.0034
    alpha, beta, gamma, delta, zeta = 0.3440, 0.7091, 1.0000, 1.0000, 0.3454
    db = '/Users/vcastor/Documents/PhD_Rouen/plamsfilter/database_entropies/entropiesCOSMO.db'
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = 'SELECT epsilon FROM PBE WHERE molecule_name = ?'
    cursor.execute(query, (data['solvent'],))
    result = cursor.fetchone()
    epsilon = result[0]
    S_gas = data['translational'] + data['rotational'] + data['vibrational']
    return (np.exp(-lambd*epsilon)*(alpha*data['rotational'] + beta*data['translational'] 
                                    gamma*data['vibrational'] +
                                    delta*data['vibrational']*data['rotational']/S_gas +
                                    zeta*data['vibrational']*data['translational']/S_gas))

