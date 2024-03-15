from small_functions import *

gga_functionals = { 
    "BP86" : "BP86",
    "BLYP" : "BLYP",
    "PW91" : "PW91",
    "mPW"  : "mPW",
    "PBE"  : "PBE",
    "RPBE" : "RPBE",
    "revPBE" : "revPBE",
    "PBE"  : "PBE",
    "PBEsol" : "PBEsol",
    "OLYP" : "OLYP",
    "OPBE" : "OPBE",
    "HTBS" : "HTBS",
    "KT1"  : "KT1",
    "KT2"  : "KT2"
}
gga_functionals = to_lower_dict(gga_functionals)

gga_dispersion_functionals = { 
    "BP86-D" : ('BP86', 'DEFAULT'),
    "BLYP-D" : ('BLYP', 'DEFAULT'),
    "PBE-D"  : ('PBE', ' DEFAULT'),
    "PBEsol-D" : ('PBEsol', ' DEFAULT'),
    "SSB-D"   : ('SSB-D', None),
    "BP86-D3" : ('BP86', 'Grimme3'),
    "BLYP-D3" : ('BLYP', 'Grimme3'),
    "revPBE-D3" : ('revPBE', 'Grimme3'),
    "PBE-D3" : ('PBE', 'Grimme3'),
    "PBEsol-D3" : ('PBEsol', 'Grimme3'),
    "PBEsol-D3(BJ)" : ('PBEsol', 'Grimme3 BJDAMP'),
    "RPBE-D3" : ('RPBE', 'Grimme3'),
    "S12g-D3" : ('S12g', 'Grimme3'),
    "BLYP-dDsC" : ('BLYP', 'dDsC'),
    "PBE-dDsC"  : ('PBE', 'dDsC'),
    "BP86-dDsC" : ('BP86', 'dDsC'),
    "revPBE-dDsC" : ('revPBE', 'dDsC'),
    "BP86-D3(BJ)" : ('BP86', 'GRIMME3 BJDAMP'),
    "BLYP-D3(BJ)" : ('BLYP', 'GRIMME3 BJDAMP'),
    "revPBE-D3(BJ)" : ('revPBE', 'GRIMME3 BJDAMP'),
    "PBE-D3(BJ)"  : ('PBE', 'GRIMME3 BJDAMP'),
    "BP86-D4(EEQ)" : ('BP86', 'GRIMME4'),
    "BLYP-D4(EEQ)" : ('BLYP', 'GRIMME4'),
    "revPBE-D4(EEQ)" : ('revPBE', 'GRIMME4'),
    "PBE-D4(EEQ)"  : ('PBE', 'GRIMME4'),
    "PBE-MBD@rsSC" : ('PBE', ' MBD'),
    "PW91-dUFF" : ('PW91', 'UFF'),
    "PBE-dUFF"  : ('PBE', 'UFF')
}
gga_dispersion_functionals = to_lower_dict(gga_dispersion_functionals)

meta_gga_functionals = { 
    "M06L"    : ("M06L", None),
    "revTPSS" : ("revTPSS", None),
    "TPSS"    : ("TPSS", None),
    "TPSS-D3" : ("TPSS", "Grimme3"),
    "TPSS-D3(BJ)" : ("TPSS", "GRIMME3 BJDAMP"),
    "TPSS-D4" : ("TPSS", "GRIMME4"),
    "SSB-D"   : ("SSB-D", None),
    "MVS"     : ("MVS", None),
    "r2SCAN-3c" : ("r2SCAN-3c", None),
    "SCAN"   : ("SCAN", None),
    "SCAN-D3(BJ)" : ("SCAN", "GRIMME3 BJDAMP"),
    "TASKxc" : ("TASKxc", None),
    "TASKCC" : ("TASKCC", None)
}
meta_gga_functionals = to_lower_dict(meta_gga_functionals)

model_functionals = {
    "LB94" : "LB94",
    "SAOP" : "SAOP",
    "TB-mBJ"  : "TB-mBJ",
    "KTB-mBJ" : "KTB-mBJ",
    "JTS-mTB-mBJ" : "JTS-mTB-mBJ",
    "GLLB-SC" : "GLLB-SC",
    "BGLLB-VWN" : "BGLLB-VWN",
    "BGLLB-LYP" : "BGLLB-LYP"
}
model_functionals = to_lower_dict(model_functionals)

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
    "MPW1K"  : ("MPW1K", None),
    "OPBE0"  : ("OPBE0", None),
    "PBE0"   : ("PBE0", None),
    "PBE0-dDsC" : ("PBE0", "dDsC"),
    "PBE0-MBD@rsSC" : ("PBE0", "MBD"),
    "S12h-D3" : ("S12h", "Grimme3")
}
model_functionals = to_lower_dict(model_functionals)

metahybrid_functionals = {
    "M06" : "M06",
    "M06-2X" : "M06-2X",
    "M06-HF" : "M06-HF",
    "TPSSH"  : "TPSSH"
}
metahybrid_functionals = to_lower_dict(metahybrid_functionals)

lib_xc_functionals = {
    "N12" : ('N12', None),
    "GAM" : ('GAM', None),
    "rSCAN"   : ("rSCAN", None),
    "revSCAN" : ("revSCAN", None),
    "r2SCAN"  : ("r2SCAN", None),
    "r2SCAN-D4" : ("r2SCAN", "GRIMME4"),
    "MN15-L" : ("MN15-L", None),
    "B97-D4(EEQ)" : ("B97", "GRIMME4"),
    "MN15"   : ("MN15", None),
    "M08-HX" : ("M08-HX", None),
    "revSCAN0" : ("revSCAN0", None)
}
lib_xc_functionals = to_lower_dict(lib_xc_functionals)

hartree_fock = [
    "hf", "hartree-fock", "hartree fock", "hartreefock"
]

dispersion_models = {
    "DEFAULT" : "DEFAULT",
    "Grimme3" : "Grimme3",
    "D3"      : "Grimme3",
    "dDsC"    : "dDsC",
    "Grimme4" : "Grimme4",
    "D4"      : "Grimme4",
    "GRIMME3 BJDAMP" : "GRIMME3 BJDAMP",
    "D3(BJ)"  : "GRIMME3 BJDAMP",
    "MBD"     : "MBD",
    "UFF"     : "UFF"
}
dispersion_models = to_lower_dict(dispersion_models)


