#!/usr/bin/env python3

import sys
import os
import subprocess

# Import pyIdlak
_srcpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', 'src')
sys.path.insert(0, _srcpath)
import pyIdlak


inputtxt = "This is a sample. With two sentences."
outdir = os.path.expanduser('~/tmp/idlak_out')
voicedir = os.path.join('slt_pmdl')

print('loading voice')
voice = pyIdlak.Voice(voicedir)

print('processing text')
final_cex = voice.process_text(inputtxt)

print('converting text to DNN input features')
dnnfeatures = voice.convert_to_dnn_features(final_cex)

pyIdlak.gen.feat_to_ark('-', dnnfeatures)