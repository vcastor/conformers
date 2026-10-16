#!/usr/bin/python3
import os

print("system_name", ";", "max_diff", ";", "weights")
for fname in os.listdir("."):
    if fname.endswith(".out"):
        with open(fname) as f:
            lines = f.readlines()
        #
        vib_lines = [(i, line.split()[2]) for i, line in enumerate(lines) if "vibrational" in line][1:]
        if len(vib_lines) > 1:
            vib_values, weights = [], []
            for i, vib in vib_lines:
                weight = lines[i - 4].split()[1]
                vib_values.append(float(vib))
                weights.append(float(weight))
            max_diff = max(vib_values) - min(vib_values)
            max_diff_indices = (vib_values.index(min(vib_values)), vib_values.index(max(vib_values)))
            system_name = fname.replace(".out", "")
            print(f"{system_name.lower()}; {max_diff:.2f}; {weights[max_diff_indices[0]]:.3f}; {weights[max_diff_indices[1]]:.3f}")

