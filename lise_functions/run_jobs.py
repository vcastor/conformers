# -*- coding: UTF-8 -*-
from scm.plams import *
from scm.conformers import ConformersJob, ConformersResults, UniqueConformersAMS, RDKitGenerator
from .settings_task import settings_for_task
import os
import subprocess

#
# Funtion to run the calculations ✨
def run_jobs(molecule, solvent, user_settings):
    # RDKit generator
    generate_settings = settings_for_task('Generate', user_settings)
    generate_job = ConformersJob(name='generate', molecule=molecule, settings=generate_settings)
    generate_job.run()
    # ADF reoptimization
    reoptimize_settings = settings_for_task('Optimize', user_settings, solvent)
    reoptimize_settings.input.ams.InputConformersSet = os.path.abspath(generate_job.results.rkfpath())
    reoptimize_ADF_job = ConformersJob(name='reoptimize_ADF', settings=reoptimize_settings)
    reoptimize_ADF_job.run()
    # ADF Score
    adf_SP_settings = settings_for_task('Score', user_settings, solvent)
    adf_SP_settings.input.ams.InputConformersSet = os.path.abspath(reoptimize_ADF_job.results.rkfpath())
    adf_SP_job = ConformersJob(name='SP_ADF', settings=adf_SP_settings)
    return adf_SP_job

def pol_jobs(pol_dirs, solvent, user_settings):
    # Frequency calculation
    pol_settings = settings_for_task('SinglePoint', user_settings, solvent)
    pol_dirs = []
    # for every score directory
    for pol in pol_dirs:
        amsrkf = AMSJob.load_external(os.path.join(pol, 'ams.rkf'))
        mol = amsrkf.results.get_main_molecule()
        freq_job = AMSJob(name='Freq', molecule=mol, settings=freq_settings)
        freq_job.run()
        freq_dirs.append(os.path.abspath(freq_job.results.rkfpath()))
    return freq_dirs

