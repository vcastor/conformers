# -*- coding: UTF-8 -*
from scm.plams import *
from .small_functions import *
from .functionals import *
from .model_dftb import *

def model_dftb(model, settings):
    model = model.strip().lower()
    if model in models:
        settings.input.DFTB.Model = models[model]
        return settings
    else:
        raise ValueError('Model not recognized')

def functional_settings(functional, dispersion, settings):
    functional = functional.strip().lower()
    dispersion = None if dispersion is None else dispersion.strip().lower()

    if functional in gga_functionals:
        settings.input.ADF.XC.GGA = gga_functionals[functional]
        if dispersion:
            settings.input.ADF.XC.DISPERSION = dispersion_models[dispersion]
    elif functional in gga_dispersion_functionals:
        func, disp = gga_dispersion_functionals[functional]
        settings.input.ADF.XC.GGA = func
        if disp or dispersion:
            settings.input.ADF.XC.DISPERSION = disp if disp else dispersion_models[dispersion]
    elif functional in meta_gga_functionals:
        func, disp = meta_gga_functionals[functional]
        settings.input.ADF.XC.METAGGA = func
        if disp or dispersion:
            settings.input.ADF.XC.DISPERSION = disp if disp else dispersion_models[dispersion]
    elif functional in model_functionals:
        settings.input.ADF.XC.Model = model_functionals[functional]
    elif functional in hybrid_functionals:
        func, disp = hybrid_functionals[functional]
        settings.input.ADF.XC.HYBRID = func
        if disp or dispersion:
            settings.input.ADF.XC.DISPERSION = disp if disp else dispersion_models[dispersion]
    elif functional in metahybrid_functionals:
        settings.input.ADF.XC.METAHYBRID = metahybrid_functionals[functional]
    elif functional in lib_xc_functionals:
        func, disp = lib_xc_functionals[functional]
        settings.input.ADF.XC.LibXC = func
        if disp or dispersion:
            settings.input.ADF.XC.DISPERSION = disp if disp else dispersion_models[dispersion]
    elif functional in hartree_fock:
        settings.input.ADF.XC = 'HartreeFock'

    return settings

