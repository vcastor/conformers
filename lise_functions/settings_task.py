# -*- coding: UTF-8 -*-
# Setting task
from scm.plams import Settings
from scm.plams.recipes.adfcosmorscompound import *
from .gvariables import gconfig
from .small_functions import *
from .settings_solvent import *
from .settings_functional import *

def task_settings(task, user_settings):
    s = Settings()
    if task == 'Generate':
        s.input.ams.Task = 'Generate'
        s.input.ams.Generator.Method = 'RDKit'
        s.input.ams.Generator.RDKit.InitialNConformers = user_settings['n conformers']
        s.input.ams.Equivalence.Crest.RMSDThreshold = user_settings['RMSD']
        model_dftb(user_settings['model'], s)
    elif task == 'Optimize':
        s.input.ams.Task = 'Optimize'
        s.input.ams.GeometryOptimization.ConvergenceQuality = 'Normal'
        s.input.ams.InputMaxEnergy = user_settings['optimize E threshold']
    elif task == 'Score':
        s.input.ams.Task = 'Score'
        s.input.ams.InputMaxEnergy = user_settings['score E threshold']
    elif task == 'SinglePoint':
        s.input.ams.Task = 'SinglePoint'
        s.input.ams.Properties.NormalModes = 'Yes'
    return s

def common_settings(user_settings):
    s = Settings()
    s.input.ADF.Basis.Type = user_settings['basis set']
    s.input.ADF.Basis.Core = user_settings['core']
    s.input.ADF.Symmetry = 'NOSYM'
    functional_settings(user_settings['functional'], user_settings['dispersion'], s)
    s.input.ADF.Relativity.Level = user_settings['relativity']
    return s

def settings_for_task(task, user_settings, solvent=None):
    s = task_settings(task, user_settings)
    if task in ['Optimize', 'Score', 'SinglePoint']:
        s.soft_update(common_settings(user_settings))
        if solvent is not None:
            s.soft_update(solvent_settings(solvent))
    return s

