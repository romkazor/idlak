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



inputtxt = "This is a sample. With two sentences."
outdir = expanduser('~/tmp/idlak_out')
datadir = expanduser('~/tmp/idlak_tmp')
pyoutdir = join(datadir, 'pyout')
voicedir = join(dirname(abspath(__file__)), 'slt_pmdl')

# Clean the output directories
shutil.rmtree(join(outdir), ignore_errors = True)
shutil.rmtree(join(datadir), ignore_errors = True)
os.makedirs(outdir, exist_ok = True)
os.makedirs(datadir, exist_ok = True)

voice = pyIdlak.TangleVoice(voicedir, loglvl = logging.DEBUG)
final_cex = voice.process_text(inputtxt)
durdnnfeatures = voice.cex_to_dnn_features(final_cex)
durpred = voice.generate_state_durations(durdnnfeatures, False)
durations = voice.generate_state_durations(durdnnfeatures)
pitchdnnfeatures = voice.combine_durations_and_features(durations, durdnnfeatures)
pitch = voice.generate_pitch(pitchdnnfeatures)




##### Finished



# Save bits and pieces of the results
os.makedirs(pyoutdir, exist_ok = True)
for fid, fdurs in durpred.items():
    with open(join(pyoutdir, fid + '.dur.cmp'), 'w') as fout:
        for d in fdurs:
            fout.write(' '.join(map(lambda f: '{:.6f}'.format(f), d)) + '\n')
voice.durations_to_mlf(join(pyoutdir, 'pyIdlak_lab.mlf'), durations)

pyIdlak.gen.feat_to_ark(join(pyoutdir, 'feat.pitch.ark'), pitchdnnfeatures, matrix = True)
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'pitch.out.ark'), pitch, matrix = True, fmt='{:.5f}')


print ("\n\nBash Version Started\n\n\n")

def scp_to_spkutt_files(outdir, _voice, scpfile):
    with open(scpfile) as fin:
        with open(join(outdir, 'utt2spk'), 'w') as utt2spk:
            with open(join(outdir, 'spk2utt'), 'w') as spk2utt:
                spk2utt.write("{} ".format(voice.spk))
                for l in fin:
                    utt = l.split()[0]
                    utt2spk.write("{} {}\n".format(utt, voice.spk))
                    spk2utt.write("{} ".format(utt))
                spk2utt.write("\n")


def run_prediction(dnnopts):
    infeats_tst  = 'ark:copy-feats scp:{0[lbl]}/feats.scp ark:-'.format(dnnopts)
    if 'incmvn_opts' in dnnopts:
        infeats_tst += ' | apply-cmvn {0[incmvn_opts]} {0[dnndir]}/incmvn_glob.ark ark:- ark:-'.format(dnnopts)
    if 'infeat_transf' in dnnopts:
        infeats_tst += ' | nnet-forward {0[infeat_transf]} ark:- ark:-'.format(dnnopts)
    infeats_tst += ' |'

    postproc  = "ark:| cat "
    if 'cmvn_opts' in dnnopts:
        postproc += " | apply-cmvn --reverse {0[cmvn_opts]} --utt2spk=ark:{0[lbl]}/utt2spk scp:{0[lbl]}/cmvn.scp ark:- ark,t:-".format(dnnopts)
    postproc += " | copy-feats ark:- ark,t:{0[out]}/feats.ark".format(dnnopts)

    durcmd = "nnet-forward --reverse-transform=true --feature-transform={0[feat_transf]} {0[nnet]} '{infeats_tst}' '{postproc}'".format(
        dnnopts, infeats_tst=infeats_tst, postproc=postproc)
    SP.call(durcmd, shell = True)


def parse_arkfile(fname):
    ark = collections.OrderedDict()
    arkfile = open(fname).read()
    arkfile = re.sub(';', '\n', arkfile)
    for m in re.finditer('(?P<id>[a-zA-Z0-9]+)\s*\[(?P<mat>.*?)\]\s*', arkfile, flags = re.S):
        ark[m.group('id')] = np.array(
            [list(map(float, s.split())) for s in m.group('mat').split('\n') if len(s.strip())]
        )
    return ark


# Setting up the outputs
durdnndir = join(voicedir, 'dur')
pitchdnndir = join(voicedir, 'pitch')
acfdnndir = join(voicedir, 'acoustic')

opts = {
    'datadir' : datadir,
}

for name, dnndir in [('dur', durdnndir), ('pitch', pitchdnndir), ('acf', acfdnndir)]:
    dnnopts = {
        'lbl' : join(datadir, name, 'lbl'), # input
        'out' : join(datadir, name, 'out'), # output
        'cmp' : join(datadir, name, 'cmp'), # processed output
        'nnet' : join(dnndir, 'final.nnet'), # nnet model
        'feat_transf' : join(dnndir, 'reverse_final.feature_transform'), # reverse transform
        'dnndir' : dnndir # where the dnn is located
    }
    if isfile(join(dnndir, 'incmvn_opts')):
        dnnopts['incmvn_opts'] = open(join(dnndir, 'incmvn_opts')).read().strip() # input CMVN
    if isfile(join(dnndir, 'cmvn_opts')):
        dnnopts['cmvn_opts'] = open(join(dnndir, 'cmvn_opts')).read().strip() # output CMVN
    if isfile(join(dnndir, 'input_final.feature_transform')):
        dnnopts['infeat_transf'] = join(dnndir, 'input_final.feature_transform')
    opts[name] = dnnopts
    os.makedirs(dnnopts['lbl'], exist_ok = True)
    os.makedirs(dnnopts['out'], exist_ok = True)
    os.makedirs(dnnopts['cmp'], exist_ok = True)


# Saving the input text for debugging
with open(join(datadir, 'text.xml'),'w') as fout:
    fout.write('<parent>')
    fout.write(inputtxt)
    fout.write('</parent>\n')
with open(join(datadir, 'text_full.xml'),'w') as fout:
    fout.write(final_cex.to_string())
pyIdlak.gen.feat_to_ark(join(datadir, 'cex.ark'), durdnnfeatures)


####### Duration modelling

# Input
to_feat_cmd = 'cat {[datadir]}/cex.ark'.format(opts)
to_feat_cmd += ' ' + """
 | awk -v extras="" '{print $1, "["; $1=""; na = split($0, a, ";"); for (i = 1; i < na; i++) for (state = 0; state < 5; state++) print extras, a[i], state; print "]"}'
""".strip()
to_feat_cmd += " | copy-feats ark:- ark,scp:{datadir}/in_durfeats.ark,{datadir}/in_durfeats.scp".format(datadir = datadir)
SP.call(to_feat_cmd, shell = True)

scpfile = join(opts['dur']['lbl'], 'feats.scp')
shutil.copy(join(datadir, "in_durfeats.scp"), scpfile)
shutil.copy(join(durdnndir, "cmvn.scp"), opts['dur']['lbl'])
scp_to_spkutt_files(opts['dur']['lbl'], voice, scpfile)

# Predict
run_prediction(opts['dur'])

# Post process
durark = parse_arkfile(join(opts['dur']['out'], 'feats.ark'))
for sptid, durs in durark.items():
    cmpfile = join(opts['dur']['cmp'], sptid + '.cmp')
    np.savetxt(cmpfile, durs, fmt = "%.6f")
SP.call('./local/makemlf.sh {0[dur][cmp]} {0[datadir]}'.format(opts), shell = True)


######## Pitch modelling

# Input
SP.call('python3 local/make_fullctx_mlf_dnn.py'
        ' {datadir}/synth_lab.mlf {datadir}/cex.ark {datadir}/pitchfeat.ark'.format(**opts),
        shell = True)
SP.call('copy-feats ark:{datadir}/pitchfeat.ark ark,scp:{datadir}/in_pitchfeats.ark,{datadir}/in_pitchfeats.scp'.format(**opts), shell = True)
shutil.copyfile(join(datadir, 'in_pitchfeats.scp'), join(opts['pitch']['lbl'], 'feats.scp'))
scpfile = join(opts['pitch']['lbl'], 'feats.scp')
scp_to_spkutt_files(opts['pitch']['lbl'], voice, scpfile)

# Predict
run_prediction(opts['pitch'])

# Post process


######## Acoustic feature modelling






print ("\n\nStarted Checking\n\n\n")



# check the duration prediction
print("Checking the duration prediction")
for spurtid in durpred.keys():
    pydurs = np.loadtxt(join(pyoutdir, fid + '.dur.cmp'))
    bashdurs = np.loadtxt(join(opts['dur']['cmp'], fid + '.cmp'))
    if pydurs.shape[0] != bashdurs.shape[0]:
        raise ValueError("Duration: unequal number of rows")
    if pydurs.shape[1] != bashdurs.shape[1]:
        raise ValueError("Duration: unequal number of columns")
    if not np.allclose(pydurs, bashdurs):
        raise ValueError("Duration: different predictions")


print("Checking the MLF")
pymlf = list(map(str.strip, open(join(pyoutdir, 'pyIdlak_lab.mlf')).readlines()))
bashmlf = list(map(str.strip, open(join(datadir, 'synth_lab.mlf')).readlines()))
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
pyark = parse_arkfile(join(pyoutdir, 'feat.pitch.ark'))
bashark = parse_arkfile(join(datadir, 'pitchfeat.ark'))
for spurtid, pymat in pyark.items():
    bashmat = bashark[spurtid]
    if pymat.shape[0] != bashmat.shape[0]:
        raise ValueError("Pitch input: unequal number of rows")
    if pymat.shape[1] != bashmat.shape[1]:
        raise ValueError("Pitch input: unequal number of columns ({}) ({})".format(pymat.shape[1], bashmat.shape[1]))
    if not np.allclose(pymat, bashmat, atol = 1e-4, rtol=0.):
        raise ValueError("Pitch input: different predictions")


print("Checking the pitch prediction")
pyark = parse_arkfile(join(pyoutdir, 'pitch.out.ark'))
bashark = parse_arkfile(join(opts['pitch']['out'], 'feats.ark'))
for spurtid, pymat in pyark.items():
    bashmat = bashark[spurtid]
    if pymat.shape[0] != bashmat.shape[0]:
        raise ValueError("Pitch predict: unequal number of rows")
    if pymat.shape[1] != bashmat.shape[1]:
        raise ValueError("Pitch predict: unequal number of columns")
    if not np.allclose(pymat, bashmat, atol = 1e-4, rtol=0.):
        raise ValueError("Pitch predict: different predictions")





### generate_spec
## vocode
## save



print ("All good")
