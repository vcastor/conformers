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
        s.input.ams.Equivalence.Method = 'AMS'
        model_dftb(user_settings['model'], s)
    elif task == 'Optimize':
        s.input.ams.Task = 'Optimize'
        s.input.ams.GeometryOptimization.ConvergenceQuality = 'Normal'
        s.input.ams.InputMaxEnergy = user_settings['optimize E threshold']
        s.input.ams.Equivalence.RMSD.RMSDThreshold = user_settings['RMSDopt']
        # s.input.ADF.Solvation.Surf = 'Delley'
    elif task == 'Score':
        s.input.ams.Task = 'Score'
        s.input.ams.InputMaxEnergy = user_settings['score E threshold']
        s.input.ams.Equivalence.CREST.RMSDThreshold = user_settings['RMSDscore']
        s.input.ADF.ConceptualDFT.Enabled = 'Yes'
        s.input.ADF.ConceptualDFT.AnalysisLevel = 'Full'
        s.input.ADF.QTAIM.Enabled = 'Yes'
        s.input.ADF.QTAIM.AnalysisLevel = 'Extended'
    elif task == 'MolecularDynamics':
        s.input.ams.Task = 'MolecularDynamics'
        s.input.ams.MolecularDynamics.NSteps = user_settings['nsteps']
        s.input.ams.MolecularDynamics.TimeStep = user_settings['timestep']
        s.input.ams.MolecularDynamics.InitialVelocities.Temperature = gconfig['temperature']
        s.input.ams.MolecularDynamics.Thermostat.Type = user_settings['thermotype']
        s.input.ams.MolecularDynamics.Thermostat.Temperature = gconfig['temperature']
        s.input.ams.MolecularDynamics.Thermostat.Tau = user_settings['tau']
        s.input.ADF.Basis.Type = user_settings['basis set']
        s.input.ADF.Basis.Core = user_settings['core']
        functional_settings(user_settings['functional'], user_settings['dispersion'], s)
        s.input.ADF.Relativity.Level = user_settings['relativity']
        s.input.ADF.ConceptualDFT.Enabled = 'Yes'
        s.input.ADF.ConceptualDFT.AnalysisLevel = 'Full'
        s.input.ADF.QTAIM.Enabled = 'Yes'
        s.input.ADF.QTAIM.AnalysisLevel = 'Extended'
    return s

def common_settings(user_settings):
    s = Settings()
    s.input.ADF.Basis.Type = user_settings['basis set']
    s.input.ADF.Basis.Core = user_settings['core']
    s.input.ADF.Symmetry = 'NOSYM'
    functional_settings(user_settings['functional'], user_settings['dispersion'], s)
    s.input.ADF.Relativity.Level = user_settings['relativity']
    return s

def settings_for_task(task, user_settings, molecule=None, solvent=None):
    s = task_settings(task, user_settings)
    if task in ['Optimize', 'Score', 'MolecularDynamics']:
        s.soft_update(common_settings(user_settings))
        if solvent is not None and molecule is not None:
            s.soft_update(solvent_settings(molecule, solvent))
    return s

