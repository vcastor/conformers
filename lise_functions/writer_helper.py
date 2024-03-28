# -*- coding: UTF-8 -*-
from .small_functions import format_list

def table_formatter(atoms, properties):
    # Orbital energies in just one line (or more if needed)
    oe_line = format_list('Orbital Energies', properties['OE'])
    oe_line += "\n"

    # Conceptual DFT properties (whole system)
    cdftp_line = "Global descriptors, Conceptual DFT\n"
    cdftp_line += f"Electronic chemical potential: {properties['cdftm'][0]:9.4f}\n"
    cdftp_line += f"Hardness                     : {properties['cdftm'][1]:9.4f}\n"
    cdftp_line += f"Electrophilicity index       : {properties['cdftm'][2]:9.4f}\n"
    cdftp_line += f"Nucleofuge                   : {properties['cdftm'][3]:9.4f}\n"
    cdftp_line += f"Electrofuge                  : {properties['cdftm'][4]:9.4f}\n"
    cdftp_line += f"Electrodonating              : {properties['cdftm'][5]:9.4f}\n"
    cdftp_line += f"Electroaccepting             : {properties['cdftm'][6]:9.4f}\n"

    # Conceptual DFT properties (atomic)
    cdfta_line = "Atomic descriptors, Conceptual DFT\n"
    cdfta_line += "Canonical and Grand Canonical Ensemble\n"
    cdfta_line += " Atom   |     f+     |     f-     |     f(2)    |    S*f+    |    S*f-    |   S*f(2)\n"
    for i, atom in enumerate(atoms):
        cdfta_line += f"   {atom}    | {properties['cdfta'][i][0]:^10.4f} |"
        cdfta_line += f" {properties['cdfta'][i][1]:^10.4f} |  {properties['cdfta'][i][2]:^10.4f} |"
        cdfta_line += f" {properties['cdfta'][i][3]:^10.4f} | {properties['cdfta'][i][4]:^10.4f} |"
        cdfta_line += f" {properties['cdfta'][i][5]:^10.4f}\n"

    # Charges
    charges_line = "Charges\n"
    charges_line = f" Atom   |    QTAIM    |   Hirshfeld\n"
    for i, atom in enumerate(atoms):
        charges_line += f"   {atom}    |  {properties['qtaimcharge'][i]:^10.4f} |  {properties['Hirshfeld'][i]:^10.4f}\n"

    # Condensed Eletrophilicity and Nuclueophilicity
    condensed_line = "Condensed electrophilicity and nucleophilicity\n"
    condensed_line += f" Atom   |   electrophilicity   |   nucleophilicity\n"
    for i, atom in enumerate(atoms):
        condensed_line += f"   {atom}    | {properties['condensed'][i][0]:^20.4f} | {properties['condensed'][i][1]:^19.4f}\n"

    formatted_str = oe_line + cdftp_line + cdfta_line + charges_line + condensed_line
    return formatted_str

