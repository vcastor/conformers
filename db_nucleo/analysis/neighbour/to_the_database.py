#!/usr/bin/python3
import sqlite3
import numpy as np

conn = sqlite3.connect('/Users/vcastor/Documents/PhD_Rouen/plamsfilter/db_nucleo/nucleo_data.db')
cur = conn.cursor()

table = 'reactive'

def read_react(filename):

    data = {
        "natoms": [],
        "expN": [],
        "expSn": [],
        "distances": [],
        "q_qtaim": [],
        "clr": [],
        "electrostatic_potential": [],
        "electrofuge": []
    }

    with open(filename, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            data["natoms"].append(int(lines[i].strip()))
            i += 1

            expN, expSn = map(float, lines[i].split())
            data["expN"].append(expN)
            data["expSn"].append(expSn)
            i += 1

            data["distances"].append(list(map(float, lines[i].split())))
            i += 1

            data["q_qtaim"].append(list(map(float, lines[i].split())))
            i += 1

            data["clr"].append(list(map(float, lines[i].split())))
            i += 1

            data["electrostatic_potential"].append(list(map(float, lines[i].split())))
            i += 2

            data["electrofuge"].append(float(lines[i].strip()))
            i += 1

    return data

react_data = read_react('reactive.pout')
# noreact_data = read_noreact('no_reactive.pout')

def compute_weighted_features(data):
    """
    q_weighted   = Σ exp(-α*distance)*q_atom
    clr_weighted = Σ exp(-β*distance)*clr_atom
    """
    alpha = 1.0; beta = 1.0
    n_molecules = len(data["natoms"])
    features = []
    
    for i in range(n_molecules):
        # Get data for this molecule
        distances = np.array(data["distances"][i])
        q_qtaim   = np.array(data["q_qtaim"][i])
        clr       = np.array(data["clr"][i])
        
        # Compute exponential weights
        weights_q   = np.exp(-alpha*distances)
        weights_clr = np.exp(-beta*distances)
        
        # Compute weighted sums
        q_weighted   = np.sum(weights_q*q_qtaim)
        clr_weighted = np.sum(weights_clr*clr)
        
        features.append([
            q_weighted,
            clr_weighted,
            data["expN"][i],
            data["expSn"][i]
        ])
    
    return features

# Main execution
if __name__ == "__main__":
    react_data = read_react('reactive.pout')
    weighted = compute_weighted_features(react_data)

    for q, clr, expN, expSN in weighted:
        cur.execute("SELECT smiles, solvent FROM parameters WHERE experimental_N = ? AND experimental_Sn = ?", (expN, expSN))
        result = cur.fetchone()
        smiles, solvent = result
        cur.execute(
            f"UPDATE {table} SET q_qtaim_w = ?, condensed_linear_response_w = ? WHERE smiles = ? AND solvent = ?",
            (q, clr, smiles, solvent)
        )


conn.commit()
conn.close()


