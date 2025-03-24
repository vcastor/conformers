#!/usr/bin/python3
import numpy as np

def read_data(filename):

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
            i += 1

            data["electrofuge"].append(float(lines[i].strip()))
            i += 1

    return data

def data_pond(filename, N_list, Sn_list):
    distances, q_qtaim, clr = [], [], []
    elep, pop = [], []

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        data = {}

        i = 0
        while i < len(lines):
            natoms = int(lines[i].strip())
            i += 1
            expN, expSn = map(float, lines[i].split())
            i += 1

            distance_arr = np.array(list(map(float, lines[i].split())))
            i += 1
            q_qtaim_arr = np.array(list(map(float, lines[i].split())))
            i += 1
            clr_arr = np.array(list(map(float, lines[i].split())))
            i += 1
            elep_arr = np.array(list(map(float, lines[i].split())))
            i += 1
            pop_arr = np.array(list(map(float, lines[i].split())))
            i += 2

            data[(expN, expSn)] = (distance_arr, q_qtaim_arr, clr_arr, elep_arr, pop_arr)

    for N, Sn in zip(N_list, Sn_list):
        distances.append(data[(N, Sn)][0])
        q_qtaim.append(data[(N, Sn)][1])
        clr.append(data[(N, Sn)][2])
        elep.append(data[(N, Sn)][3])
        pop.append(data[(N, Sn)][4])

    return distances, q_qtaim, clr, elep, pop

