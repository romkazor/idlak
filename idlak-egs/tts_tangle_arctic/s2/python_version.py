#!/usr/bin/env python3

import sys
import os
import re
import collections
import logging
import shutil
import subprocess as SP
import numpy as np

from os.path import expanduser, join, abspath, dirname, isfile, isdir

# Import pyIdlak
_srcpath = join(abspath(dirname(__file__)), '..', '..', '..', 'src')
sys.path.insert(0, _srcpath)
import pyIdlak


inputtxt = "This is a demo of D N N synthesis"

"""

voice = pyIdlak.TangleVoice(voicedir)
waveform = voice.speak(inputtxt)

"""

outdir = expanduser('~/tmp/idlak_out_py')
pyoutdir = expanduser('~/tmp/idlak_tmp_py')
voicedir = join(dirname(abspath(__file__)), 'slt_pmdl')
shutil.rmtree(join(outdir), ignore_errors = True)
shutil.rmtree(join(pyoutdir), ignore_errors = True)

vocoderdir = join(pyoutdir, 'vocoder')
os.makedirs(outdir, exist_ok = True)
os.makedirs(pyoutdir, exist_ok = True)
os.makedirs(vocoderdir, exist_ok = True)


# Clean the output directories

lvl = logging.WARN
voice = pyIdlak.TangleVoice(voicedir, lvl)

final_cex = voice.process_text(inputtxt, normalise = False)

durfeatures = voice.cex_to_dnn_features(final_cex)

durpred = voice.generate_state_durations(durfeatures, False)

durations = voice.generate_state_durations(durfeatures)

pitchfeatures = voice.combine_durations_and_features(durations, durfeatures)

rawpitchpred = voice.generate_pitch(pitchfeatures, mlpg = False, extract = False)

pitch = voice.generate_pitch(pitchfeatures,
                             save_pdf_directory = pyoutdir)

acfdnnfeatures = voice.combine_pitch_and_features(pitch, pitchfeatures)

acffeatures = voice.generate_acoustic_features(acfdnnfeatures, mlpg = False, extract = False)

acousticfeatures = voice.generate_acoustic_features(acfdnnfeatures,
                                                    save_pdf_directory = pyoutdir)

waveform = voice.vocode_acoustic_features(acousticfeatures, pitch,
                                          save_residual_directory = vocoderdir,
                                          wav_filename = join(outdir, 'pytest.wav'))

# Save bits and pieces of the results
os.makedirs(pyoutdir, exist_ok = True)

with open(join(pyoutdir, 'text_full.xml'), 'w') as fout:
    fout.write(final_cex.to_string())

pyIdlak.gen.feat_to_ark(join(pyoutdir, 'dur.in.ark'), durfeatures, matrix=False)
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'dur.out.ark'), durpred, matrix=True)
voice.durations_to_mlf(join(pyoutdir, 'pyIdlak_lab.mlf'), durations)
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'pitch.in.ark'), pitchfeatures, matrix = True)
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'pitch.out.ark'), rawpitchpred, matrix = True, fmt='{:.5f}')
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'pitch.mlpg.ark'), pitch, matrix = True, fmt='{:.5f}')
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'acf.in.ark'), acfdnnfeatures, matrix = True, fmt='{:.5f}')
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'acf.out.ark'), acffeatures, matrix = True, fmt='{:.5f}')


for spurtid, spurt_acfs in acousticfeatures.items():
    for acf_type, values in spurt_acfs.items():
        fn = join(vocoderdir, spurtid + '.' + acf_type)
        np.savetxt(fn, values, fmt = "%.6f")


print('Done')
