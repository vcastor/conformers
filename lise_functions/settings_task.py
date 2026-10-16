# -*- coding: UTF-8 -*-
# Setting task
from scm.plams import Settings
from .settings_solvent import solvent_settings
from .settings_functional import functional_settings, model_dftb

def freq_branch(config):
    """
    Entropy-only runs keep the settings of the entropy (freq) branch.
    """
    return config['properties'] == ['entropy']

def task_settings(task, config):
    s = Settings()
    if task == 'Generate':
        s.input.ams.Task = 'Generate'
        s.input.ams.Generator.Method = 'RDKit'
        if freq_branch(config):
            s.input.ams.Generator.RDKit.MaxConfs = config['conformers']
        else:
            s.input.ams.Generator.RDKit.InitialNConformers = config['conformers']
        s.input.ams.Equivalence.Method = 'AMS'
        model_dftb(config['model'], s)
    elif task == 'Optimize':
        s.input.ams.Task = 'Optimize'
        s.input.ams.GeometryOptimization.ConvergenceQuality = 'Normal'
        s.input.ams.InputMaxEnergy = config['Eopt']
        s.input.ams.Equivalence.RMSD.RMSDThreshold = config['RMSDopt']
        if freq_branch(config):
            s.input.ams.Equivalence.CREST.RMSDThreshold = '0.05'
    elif task == 'Score':
        s.input.ams.Task = 'Score'
        s.input.ams.InputMaxEnergy = config['Escore']
        s.input.ams.Equivalence.CREST.RMSDThreshold = config['RMSDscore']
        if 'nucleophilicity' in config['properties']:
            s.input.ADF.ConceptualDFT.Enabled = 'Yes'
            s.input.ADF.ConceptualDFT.AnalysisLevel = 'Full'
            s.input.ADF.QTAIM.Enabled = 'Yes'
            s.input.ADF.QTAIM.AnalysisLevel = 'Extended'
    elif task == 'Freq':
        s.input.ams.Task = 'SinglePoint'
        s.input.ams.Properties.NormalModes = 'Yes'
        s.input.ams.Thermo.Temperatures = config['temperature']
        s.input.ADF.ConceptualDFT.Enabled = 'Yes'
        s.input.ADF.ConceptualDFT.AnalysisLevel = 'Full'
    return s

def common_settings(config):
    s = Settings()
    s.input.ADF.Basis.Type = config['basis']
    s.input.ADF.Basis.Core = config['core']
    s.input.ADF.Symmetry = 'NOSYM'
    functional_settings(config['functional'], config['dispersion'], s)
    s.input.ADF.Relativity.Level = config['relativity']
    return s

def settings_for_task(task, config, solvent=None):
    """
    solvent: ADF solvent (see solvent_name), None for gas phase.
    """
    s = task_settings(task, config)
    if task in ['Optimize', 'Score', 'Freq']:
        s.soft_update(common_settings(config))
        if solvent is not None:
            s.soft_update(solvent_settings(solvent, freq_branch(config)))
    return s
