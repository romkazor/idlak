#!/usr/bin/env python3

import sys
import os
import re
import collections
import logging
import shutil
import subprocess as SP
import numpy as np

from os.path import expanduser, join, abspath, dirname

# Import pyIdlak
_srcpath = join(abspath(dirname(__file__)), '..', '..', '..', 'src')
sys.path.insert(0, _srcpath)
import pyIdlak



inputtxt = "This is a sample. With two sentences."
outdir = expanduser('~/tmp/idlak_out')
datadir = expanduser('~/tmp/idlak_tmp')
pyoutdir = join(datadir, 'pyout')
voicedir = join(dirname(abspath(__file__)), 'slt_pmdl')

# Clean the output directories
os.makedirs(outdir, exist_ok = True)
os.makedirs(datadir, exist_ok = True)
shutil.rmtree(join(outdir, '*'), ignore_errors = True)
shutil.rmtree(join(datadir, '*'), ignore_errors = True)

voice = pyIdlak.TangleVoice(voicedir, loglvl = logging.DEBUG)
final_cex = voice.process_text(inputtxt)
durdnnfeatures = voice.cex_to_dnn_features(final_cex)
durpred = voice.generate_state_durations(durdnnfeatures, False)
durations = voice.generate_state_durations(durdnnfeatures)
pitchdnnfeatures = voice.combine_durations_and_features(durations, durdnnfeatures)


# Save bits and pieces of the results
os.makedirs(pyoutdir, exist_ok = True)
for fid, fdurs in durpred.items():
    with open(join(pyoutdir, fid + '.dur.cmp'), 'w') as fout:
        for d in fdurs:
            fout.write(' '.join(map(lambda f: '{:.6f}'.format(f), d)) + '\n')
voice.durations_to_mlf(join(pyoutdir, 'pyIdlak_lab.mlf'), durations)

pyIdlak.gen.feat_to_ark(join(pyoutdir, 'feat.pitch.ark'), pitchdnnfeatures, matrix = True)


print ("\n\nBash Version Started\n\n\n")

# Original version

opts = {
    'datadir' : datadir,
    'durdnndir' : join(voicedir, 'dur')
}

with open(join(datadir, 'text.xml'),'w') as fout:
    fout.write('<parent>')
    fout.write(inputtxt)
    fout.write('</parent>\n')

with open(join(datadir, 'text_full.xml'),'w') as fout:
    fout.write(final_cex.to_string())

pyIdlak.gen.feat_to_ark(join(datadir, 'cex.ark'), durdnnfeatures)


# Duration modelling
opts['exp'] = './slt_pmdl/dur'
opts['duroutdir'] = join(datadir, 'durout')
opts['incmvn_opts'] = open('{exp}/incmvn_opts'.format(**opts)).read().strip()
opts['feat_transf'] = "{exp}/reverse_final.feature_transform".format(**opts)
opts['nnet'] =  "{exp}/final.nnet".format(**opts)
opts['cmvn_opts'] = open('{exp}/cmvn_opts'.format(**opts)).read().strip()
opts['durcmp'] = join(opts['duroutdir'], 'cmp')
opts['lbldurdir'] = join(opts['datadir'], 'lbldur')
opts['tst'] = opts['lbldurdir']

# Generate input feature for duration modelling
to_feat_cmd = 'cat {datadir}/cex.ark'.format(**opts)
to_feat_cmd += ' ' + """
 | awk -v extras="" '{{print $1, "["; $1=""; na = split($0, a, ";"); for (i = 1; i < na; i++) for (state = 0; state < 5; state++) print extras, a[i], state; print "]"}}'
""".format(**opts).strip()
to_feat_cmd += " | copy-feats ark:- ark,scp:{datadir}/in_durfeats.ark,{datadir}/in_durfeats.scp".format(**opts)
SP.call(to_feat_cmd, shell = True)

os.makedirs(opts['lbldurdir'], exist_ok = True)
shutil.copyfile("{datadir}/in_durfeats.scp".format(**opts), "{lbldurdir}/feats.scp".format(**opts))
shutil.copyfile("{durdnndir}/cmvn.scp".format(**opts), "{lbldurdir}/cmvn.scp".format(**opts))

with open(join(opts['lbldurdir'], 'feats.scp')) as fin:
    with open(join(opts['lbldurdir'], 'utt2spk'), 'w') as utt2spk:
        with open(join(opts['lbldurdir'], 'spk2utt'), 'w') as spk2utt:
            spk2utt.write("{} ".format(voice.spk))
            for l in fin:
                utt = l.split()[0]
                utt2spk.write("{} {}\n".format(utt, voice.spk))
                spk2utt.write("{} ".format(utt))
            spk2utt.write("\n")


os.makedirs(opts['duroutdir'], exist_ok = True)
os.makedirs(opts['durcmp'], exist_ok = True)
infeats_tst  = 'ark:copy-feats scp:{tst}/feats.scp ark:-'.format(**opts)
infeats_tst += ' | apply-cmvn {incmvn_opts} {exp}/incmvn_glob.ark ark:- ark:-'.format(**opts)
infeats_tst += ' | nnet-forward {exp}/input_final.feature_transform ark:- ark:-'.format(**opts)
infeats_tst += ' |'
opts['infeats_tst'] = infeats_tst

postproc  = "ark:| cat "
postproc += " | apply-cmvn --reverse {cmvn_opts} --utt2spk=ark:{tst}/utt2spk scp:{tst}/cmvn.scp ark:- ark,t:-".format(**opts)
postproc += " | copy-feats ark:- ark,t:{duroutdir}/feats.ark".format(**opts)
opts['postproc'] = postproc

durcmd = "nnet-forward --reverse-transform=true --feature-transform={feat_transf} {nnet} '{infeats_tst}' '{postproc}'".format(**opts)
SP.call(durcmd, shell = True)

# Split up the duration files
pat = re.compile(r'^(?P<fid>\S+)\s+\[')
curid = False
fout = False
with open(join(opts['duroutdir'], 'feats.ark')) as ark:
    for line in ark:
        empty_curid = False
        line = line.strip()
        m = pat.match(line)
        if m is not None:
            if fout:
                fout.close()
                fout = False
            curid = m.group('fid')
            fout = open(join(opts['durcmp'], curid + '.cmp'), 'w')
            line = re.sub(pat, '', line).strip()
        if not line:
            continue
        if line.endswith(']'):
            empty_curid = True
            line = line[:-1].strip()
        if not curid:
            raise IOError('ark not formated as expected')
        fout.write(line + '\n')
        if empty_curid:
            curid = ''
            if fout:
                fout.close()
                fout = False
if fout:
    fout.close()

SP.call('./local/makemlf.sh {duroutdir} {datadir}'.format(**opts), shell = True)

SP.call('python local/make_fullctx_mlf_dnn.py {datadir}/synth_lab.mlf {datadir}/cex.ark {datadir}/feat.ark'.format(**opts),
        shell = True)


print ("\n\nStarted Checking\n\n\n")
# check the duration prediction
print("Checking the duration prediction")
for spurtid in durpred.keys():
    pydurs = np.loadtxt(join(pyoutdir, fid + '.dur.cmp'))
    bashdurs = np.loadtxt(join(opts['durcmp'], fid + '.cmp'))
    if pydurs.shape[0] != bashdurs.shape[0]:
        raise ValueError("Duration: unequal number of rows")
    if pydurs.shape[1] != bashdurs.shape[1]:
        raise ValueError("Duration: unequal number of columns")
    if not np.allclose(pydurs, bashdurs):
        raise ValueError("Duration: different predictions")


print("Checking the MLF")
pymlf = list(map(str.strip, open(join(pyoutdir, 'pyIdlak_lab.mlf')).readlines()))
bashmlf = list(map(str.strip, open(join(opts['datadir'], 'synth_lab.mlf')).readlines()))
pymlf = list(filter(len, pymlf))
bashmlf = list(filter(len, bashmlf))
if len(pymlf) != len(bashmlf):
    raise ValueError("MLF: different number of rows")
for i in range(len(pymlf)):
    p = pymlf[i]
    b = bashmlf[i]
    if p != b:
        raise ValueError("MLF: different values")

print("Checking the pitch input features")
pypitchark = list(map(str.strip, open(join(pyoutdir, 'feat.pitch.ark')).readlines()))
bashpitchark = list(map(str.strip, open(join(opts['datadir'], 'feat.ark')).readlines()))
pypitchark = list(filter(len, pypitchark))
bashpitchark = list(filter(len, bashpitchark))
if len(pypitchark) != len(bashpitchark):
    raise ValueError("PITCH INPUT: different number of rows")
for i in range(len(pypitchark)):
    p = pypitchark[i]
    b = bashpitchark[i]
    if p != b:
        raise ValueError("PITCH INPUT: different values")



# generate_f0
# generate_spec
# vocode
# save



print ("All good")
