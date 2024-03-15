# -*- coding: UTF-8 -*-
# Setting task
from scm.plams import Settings
from scm.plams.recipes.adfcosmorscompound import *
from small_functions import *
from solvent_settings import *
from functional_settings import *

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
        s.input.ADF.Basis.Type = user_settings['basis set']
        s.input.ADF.Symmetry = 'NOSYM'
        functional_settings(user_settings['functional'], user_settings['dispersion'], s)
        s.input.ADF.Relativity.Level = 'None'
        s.input.ADF.Solvation.Surf = 'Delley'
    elif task == 'Score':
        s.input.ams.Task = 'Score'
        s.input.ams.InputMaxEnergy = user_settings['score E threshold']
        s.input.ADF.Basis.Type = user_settings['basis set']
        s.input.ADF.Symmetry = 'NOSYM'
        functional_settings(user_settings['functional'], user_settings['dispersion'], s)
        s.input.ADF.Relativity.Level = 'None'
        s.input.ADF.ConceptualDFT.Enabled = 'Yes'
        s.input.ADF.ConceptualDFT.AnalysisLevel = 'Full'
        s.input.ADF.QTAIM.Enabled = 'Yes'
        s.input.ADF.QTAIM.AnalysisLevel = 'Extended'
    return s

def settings_for_task(task, user_settings, solvent=None):
    s = task_settings(task, user_settings)
    if solvent is not None:
        s.soft_update(solvent_settings(solvent))
    return s

