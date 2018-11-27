#!/usr/bin/env python3

import sys
import os
import re
import collections
import logging
import shutil
import subprocess as SP
import numpy as np
import glob

from os.path import expanduser, join, abspath, dirname, isfile, isdir

# Import pyIdlak
_srcpath = join(abspath(dirname(__file__)), '..', '..', '..', 'src')
sys.path.insert(0, _srcpath)
import pyIdlak
from pyIdlak.pylib import compare_arks

pydir = expanduser('~/tmp/idlak_tmp_py')
bashdir = expanduser('~/tmp/idlak_tmp')
bashoutdir = expanduser('~/tmp/idlak_out')

#####################################
sys.stdout.write('Duration in  ... ')
py_dur_in = join(pydir, "dur.in.ark")
bash_dur_in = join(bashdir, "cex.ark")
compare_arks(py_dur_in, bash_dur_in)
sys.stdout.write('OK\n')

#####################################
sys.stdout.write('Duration out ... ')
py_dur_out = join(pydir, "dur.out.ark")
bash_dur_out = join(bashdir, "durout", "feats.ark")
compare_arks(py_dur_out, bash_dur_out)
sys.stdout.write('OK\n')

#####################################
sys.stdout.write('MLF          ... ')
def _parse_mlf(mlffn):
    mlf = {}
    mlf_file = open(mlffn)
    fid = ''
    for line in mlf_file:
        line = line.strip()
        if line in ['#!MLF!#', '.', '']:
            continue
        m = re.match(r'\"(.*?)\.(lab|rec)\"', line)
        if not m is None:
            fid = m.group(1)
            mlf[fid] = []
        else:
            label = list(map(int, line.split()))
            mlf[fid].append(label)
    return mlf

py_mlf = _parse_mlf(join(pydir, 'pyIdlak_lab.mlf'))
bash_mlf  = _parse_mlf(join(bashdir, "synth_lab.mlf"))
for fid in py_mlf:
    if fid not in bash_mlf:
        raise ValueError('fid {} missing from bash'.format(fid))
    py_lab = py_mlf[fid]
    bash_lab = bash_mlf[fid]
    if len(py_lab) != len(bash_lab):
        raise ValueError('fid {} have different length (py {}; bash {})'.format(fid), len(py_lab), len(bash_lab))
    for idx, (pylabel, bashlabel) in enumerate(zip(py_lab, bash_lab)):
        if pylabel[2] != bashlabel[2]:
            raise ValueError('fid {} phone labels do not match at line {}'.format(fid, idx))
        if pylabel[3] != bashlabel[3]:
            raise ValueError('fid {} state labels do not match at line {}'.format(fid, idx))
        if pylabel[0] != bashlabel[0]:
            raise ValueError('fid {} start times do not match at line {}'.format(fid, idx))
    del bash_mlf[fid]
if bash_mlf:
    raise ValueError('python missing fids: ' + ' '.join(bash_mlf.keys()))
sys.stdout.write('OK\n')

#####################################
sys.stdout.write('Pitch in     ... ')
py_pitch_in = join(pydir, "pitch.in.ark")
bash_pitch_in = join(bashdir, "in_feats.ark")
compare_arks(py_pitch_in, bash_pitch_in)
sys.stdout.write('OK\n')

#####################################
sys.stdout.write('Pitch out    ... ')
py_pitch_out = join(pydir, "pitch.out.ark")
bash_pitch_out = join(bashdir, "pitchout", "feats.ark")
compare_arks(py_pitch_out, bash_pitch_out)
sys.stdout.write('OK\n')


#####################################
sys.stdout.write('Pitch mlpg   ... ')
py_mlpg = join(pydir, "pitch.mlpg.ark")
bash_mlpg = join(bashdir, "pitchout", "feats_mlpg.ark")
compare_arks(py_mlpg, bash_mlpg)
sys.stdout.write('OK\n')


#####################################
sys.stdout.write('ACF in       ... ')
py_acf_in = join(pydir, "acf.in.ark")
bash_acf_in = join(bashdir, "pitchlbl", "feats.ark")
compare_arks(py_acf_in, bash_acf_in)
sys.stdout.write('OK\n')


#####################################
sys.stdout.write('ACF out      ... ')
py_acf_in = join(pydir, "acf.out.ark")
bash_acf_in = join(bashoutdir, "feats.ark")
compare_arks(py_acf_in, bash_acf_in)
sys.stdout.write('OK\n')


#####################################
sys.stdout.write('PDFs         ... ')

from os.path import basename, splitext
spurtids = {splitext(splitext(basename(s))[0])[0] for s in glob.glob(join(pydir, '*.mcep.pdf'))}
atol = 1e-3
rtol=0.

for spurtid in spurtids:
    py_mcep_pdf = np.loadtxt(join(pydir, spurtid + ".mcep.pdf"))
    bash_mcep_pdf = np.loadtxt(join(bashdir, 'vocoder','test001.mcep.pdf.txt'))
    py_bndap_pdf = np.loadtxt(join(pydir, spurtid + ".bndap.pdf"))
    bash_bndap_pdf = np.loadtxt(join(bashdir, 'vocoder','test001.bndap.pdf.txt'))
    if py_mcep_pdf.shape[0] != bash_mcep_pdf.shape[0]:
        raise ValueError("unequal number of rows "
            "A: {[0]} B: {[0]}".format(py_mcep_pdf.shape, bash_mcep_pdf.shape))
    if py_mcep_pdf.shape[1] != bash_mcep_pdf.shape[1]:
        raise ValueError("unequal number of columns "
            "A: {[1]} B: {[1]}".format(py_mcep_pdf.shape, bash_mcep_pdf.shape))
    if not np.allclose(py_mcep_pdf, bash_mcep_pdf, atol = atol, rtol=rtol):
        raise ValueError("different values")

    if py_bndap_pdf.shape[0] != bash_bndap_pdf.shape[0]:
        raise ValueError("unequal number of rows "
            "A: {[0]} B: {[0]}".format(py_bndap_pdf.shape, bash_bndap_pdf.shape))
    if py_bndap_pdf.shape[1] != bash_bndap_pdf.shape[1]:
        raise ValueError("unequal number of columns "
            "A: {[1]} B: {[1]}".format(py_bndap_pdf.shape, bash_bndap_pdf.shape))
    if not np.allclose(py_bndap_pdf, bash_bndap_pdf, atol = atol, rtol=rtol):
        raise ValueError("different values")

sys.stdout.write('OK\n')

#####################################
sys.stdout.write('ACF mlpg     ... ')

for spurtid in spurtids:
    py_mcep_mlpg = np.loadtxt(join(pydir, 'vocoder', spurtid + '.mcep'))
    bash_mcep_mlpg = np.loadtxt(join(bashdir, 'vocoder',spurtid + '.mcep'))

    if py_mcep_mlpg.shape[0] != bash_mcep_mlpg.shape[0]:
        raise ValueError("unequal number of rows "
            "A: {[0]} B: {[0]}".format(py_mcep_mlpg.shape, bash_mcep_mlpg.shape))
    if py_mcep_mlpg.shape[1] != bash_mcep_mlpg.shape[1]:
        raise ValueError("unequal number of columns "
            "A: {[1]} B: {[1]}".format(py_mcep_mlpg.shape, bash_mcep_mlpg.shape))
    if not np.allclose(py_mcep_mlpg, bash_mcep_mlpg, atol = atol, rtol=rtol):
        raise ValueError("different values")

    py_bndap_mlpg = np.loadtxt(join(pydir, 'vocoder', spurtid + '.bndap'))
    bash_bndap_mlpg = np.loadtxt(join(bashdir, 'vocoder', spurtid + '.bndap_raw'))
    if py_bndap_mlpg.shape[0] != bash_bndap_mlpg.shape[0]:
        raise ValueError("unequal number of rows "
            "A: {[0]} B: {[0]}".format(py_bndap_mlpg.shape, bash_bndap_mlpg.shape))
    if py_bndap_mlpg.shape[1] != bash_bndap_mlpg.shape[1]:
        raise ValueError("unequal number of columns "
            "A: {[1]} B: {[1]}".format(py_bndap_mlpg.shape, bash_bndap_mlpg.shape))
    if not np.allclose(py_bndap_mlpg, bash_bndap_mlpg, atol = atol, rtol=rtol):
        raise ValueError("different values")

sys.stdout.write('OK\n')

#####################################
sys.stdout.write('Excitation   ... ')

for spurtid in spurtids:
    py_residiual = np.loadtxt(join(pydir, 'vocoder', spurtid + '.res'))
    bash_residiual = np.loadtxt(join(bashdir, 'vocoder', spurtid + '.resid'))
    if py_residiual.size != bash_residiual.size:
        raise ValueError("unequal number of samples "
            "A: {} B: {}".format(py_residiual.size, bash_residiual.size))
    if not np.allclose(py_residiual, bash_residiual, atol = atol, rtol=rtol):
        raise ValueError("different values")



sys.stdout.write('OK\n')

#####################################
sys.stdout.write('All checks passed\n')

