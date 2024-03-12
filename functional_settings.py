# -*- coding: UTF-8 -*-
# Just loooooong data (dictionaries) about functionals
from small_functions import *
from scm.plams import *

def functional_settings(functional, settings):
    gga_functionals = {
     "BP86" : "BP86",
     "BLYP" : "BLYP",
     "PW91" : "PW91",
     "mPW" : "mPW",
     "PBE" : "PBE",
     "RPBE" : "RPBE",
     "revPBE" : "revPBE",
     "PBE" : "PBE",
     "PBEsol" : "PBEsol",
     "OLYP" : "OLYP",
     "OPBE" : "OPBE",
     "HTBS" : "HTBS",
     "KT1" : "KT1",
     "KT2" : "KT2",
    }
    gga_dispersion_functionals = {
     "BP86-D" : ('BP86', 'DEFAULT'),
     "BLYP-D" : ('BLYP', 'DEFAULT'),
     "PBE-D" : ('PBE', ' DEFAULT'),
     "PBEsol-D" : ('PBEsol', ' DEFAULT'),
     "SSB-D" : ('SSB-D', None),
     "BP86-D3" : ('BP86', 'Grimme3'),
     "BLYP-D3" : ('BLYP', 'Grimme3'),
     "revPBE-D3" : ('revPBE', 'Grimme3'),
     "PBE-D3" : ('PBE', 'Grimme3'),
     "PBEsol-D3" : ('PBEsol', 'Grimme3'),
     "PBEsol-D3(BJ)" : ('PBEsol', 'Grimme3 BJDAMP'),
     "RPBE-D3" : ('RPBE', 'Grimme3'),
     "S12g-D3" : ('S12g', 'Grimme3'),
     "BLYP-dDsC" : ('BLYP', 'dDsC'),
     "PBE-dDsC" : ('PBE', 'dDsC'),
     "BP86-dDsC" : ('BP86', 'dDsC'),
     "revPBE-dDsC" : ('revPBE', 'dDsC'),
     "BP86-D3(BJ)" : ('BP86', 'GRIMME3 BJDAMP'),
     "BLYP-D3(BJ)" : ('BLYP', 'GRIMME3 BJDAMP'),
     "revPBE-D3(BJ)" : ('revPBE', 'GRIMME3 BJDAMP'),
     "PBE-D3(BJ)" : ('PBE', 'GRIMME3 BJDAMP'),
     "BP86-D4(EEQ)" : ('BP86', 'GRIMME4'),
     "BLYP-D4(EEQ)" : ('BLYP', 'GRIMME4'),
     "revPBE-D4(EEQ)" : ('revPBE', 'GRIMME4'),
     "PBE-D4(EEQ)" : ('PBE', 'GRIMME4'),
     "PBE-MBD@rsSC" : ('PBE', ' MBD'),
     "PW91-dUFF" : ('PW91', 'UFF'),
     "PBE-dUFF" : ('PBE', 'UFF'),
    }
    meta_gga_functionals = {
     "M06L" : ("M06L", None),
     "revTPSS" : ("revTPSS", None),
     "TPSS" : ("TPSS", None),
     "TPSS-D3" : ("TPSS", "Grimme3"),
     "TPSS-D3(BJ)" : ("TPSS", "GRIMME3 BJDAMP"),
     "TPSS-D4" : ("TPSS", "GRIMME4"),
     "SSB-D" : ("SSB-D", None),
     "MVS" : ("MVS", None),
     "r2SCAN-3c" : ("r2SCAN-3c", None),
     "SCAN" : ("SCAN", None),
     "SCAN-D3(BJ)" : ("SCAN", "GRIMME3 BJDAMP"),
     "TASKxc" : ("TASKxc", None),
     "TASKCC" : ("TASKCC", None)
    }
    model_functionals = {
    #if {$xc eq "Model:GRAC"} {set axc "Model GRAC [GIN xc.ip] [GIN xc.ipb] # FIXME
     "LB94" : "LB94",
     "SAOP" : "SAOP",
     "TB-mBJ" : "TB-mBJ",
     "KTB-mBJ" : "KTB-mBJ",
     "JTS-mTB-mBJ" : "JTS-mTB-mBJ",
     "GLLB-SC" : "GLLB-SC",
     "BGLLB-VWN" : "BGLLB-VWN",
     "BGLLB-LYP" : "BGLLB-LYP",
    }
    hybrid_functionals = {
     "B3LYP" : ("B3LYP", None),
     "B3LYP*" : ("B3LYP*", None),
     "B3LYP-D" : ("B3LYP", "DEFAULT"),
     "B3LYP-D3" : ("B3LYP", "Grimme3"),
     "B3LYP-dDsC" : ("B3LYP", "dDsC"),
     "B3LYP-D3(BJ)" : ("B3LYP", "GRIMME3 BJDAMP"),
     "B3LYP-D4(EEQ)" : ("B3LYP", "GRIMME4"),
     "B3LYP-dUFF" : ("B3LYP", "UFF"),
     "B1LYP" : ("B1LYP", None),
     "KMLYP" : ("KMLYP", None),
     "O3LYP" : ("O3LYP", None),
     "X3LYP" : ("X3LYP", None),
     "BHandH" : ("BHandH", None),
     "BHandHLYP" : ("BHandHLYP", None),
     "BHandHLYP-dDsC" : ("BHandHLYP", "dDsC"),
     "B1PW91" : ("B1PW91", None),
     "MPW1PW" : ("MPW1PW", None),
     "MPW1K" : ("MPW1K", None),
     "OPBE0" : ("OPBE0", None),
     "PBE0" : ("PBE0", None),
     "PBE0-dDsC" : ("PBE0", "dDsC"),
     "PBE0-MBD@rsSC" : ("PBE0", "MBD"),
     "S12h-D3" : ("S12h", "Grimme3"),
    }
    metahybrid_functionals = {
     "M06" : "M06",
     "M06-2X" : "M06-2X",
     "M06-HF" : "M06-HF",
     "TPSSH" : "TPSSH"
    }
    # FIXME, add the rest of the functionals $AMSHOME/gui/libtcl/keys.tcl
    lib_xc_functionals = {
     "N12" : ('N12', None),
     "GAM" : ('GAM', None),
     "rSCAN" : ("rSCAN", None),
     "revSCAN" : ("revSCAN", None),
     "r2SCAN" : ("r2SCAN", None),
     "r2SCAN-D4" : ("r2SCAN", "GRIMME4"),
     "MN15-L" : ("MN15-L", None),
     "B97-D4(EEQ)" : ("B97", "GRIMME4"),
     "MN15" : ("MN15", None),
     "M08-HX" : ("M08-HX", None),
     "revSCAN0" : ("revSCAN0", None)
    }

    gga_functionals_lower = to_lower_dict(gga_functionals)
    gga_dispersion_functionals_lower = to_lower_dict(gga_dispersion_functionals)
    meta_gga_functionals_lower = to_lower_dict(meta_gga_functionals)
    model_functionals_lower = to_lower_dict(model_functionals)
    hybrid_functionals_lower = to_lower_dict(hybrid_functionals)
    metahybrid_functionals_lower = to_lower_dict(metahybrid_functionals)
    lib_xc_functionals_lower = to_lower_dict(lib_xc_functionals)

    functional = functional.strip().lower()

    if functional in gga_functionals_lower:
        settings.input.ADF.XC.GGA = gga_funtionals_lower[functional]
    elif functional in gga_dispersion_functionals_lower:
        func, disp = gga_dispersion_functionals_lower[functional]
        settings.input.ADF.XC.GGA = func
        if disp is not None:
            settings.input.ADF.XC.DISPERSION = disp
    elif functional in meta_gga_functionals_lower:
        func, disp = meta_gga_functionals_lower[functional]
        settings.input.ADF.XC.METAGGA = func
        if disp is not None:
            settings.input.ADF.XC.DISPERSION = disp
    elif functional in model_functionals_lower:
        settings.input.ADF.XC.Model = model_functionals_lower[functional]
    elif functional in hybrid_functionals_lower:
        func, disp = hybrid_functionals_lower[functional]
        settings.input.ADF.XC.HYBRID = func
        if disp is not None:
            settings.input.ADF.XC.DISPERSION = disp
    elif functional in metahybrid_functionals_lower:
        func = metahybrid_functionals_lower[functional]
        settings.input.ADF.XC.METAHYBRID = func
    elif functional == 'hartre fock':
        settings.input.ADF.XC = 'HartreeFock'

    return settings
