# -*- coding: UTF-8 -*-
from .gvariables import gconfig

def ponderated_writer(avg_pond):

    lines = f"{avg_pond['number_atoms']}\n"
    lines += f"{avg_pond['expN']} {avg_pond['expSn']}\n"

    lines += " ".join(map(str, avg_pond['average']['distances'].tolist())) + "\n"
    lines += " ".join(map(str, avg_pond['average']['qtaimcharge'].tolist())) + "\n"
    lines += " ".join(map(str, avg_pond['average']['condensed_linear'].tolist())) + "\n"
    lines += " ".join(map(str, avg_pond['average']['electrostatic_potential'].tolist())) + "\n"
    lines += " ".join(map(str, avg_pond['average']['populations'].tolist())) + "\n"

    lines += f"{avg_pond['average']['electrofuge']}\n"

    return lines

def pond_output(system_results):
    out_file = gconfig['input_file_name'].replace(".csv", ".pout")
    with open(out_file, 'w') as f:
        for nsystem in system_results:
            avg_pond = system_results[nsystem]
            f.write(ponderated_writer(avg_pond))

