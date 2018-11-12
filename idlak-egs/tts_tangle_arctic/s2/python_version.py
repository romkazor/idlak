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
tmpdir = expanduser('~/tmp/idlak_tmp')
voicedir = join('slt_pmdl')

voice = pyIdlak.TangleVoice(voicedir, loglvl = logging.DEBUG)
final_cex = voice.process_text(inputtxt)
dnnfeatures = voice.convert_to_dnn_features(final_cex)
#durations = voice.generate_state_durations(dnnfeatures)

# Original version
shutil.rmtree(outdir, ignore_errors = True)
os.makedirs(outdir, exist_ok = True)
shutil.rmtree(tmpdir, ignore_errors = True)
os.makedirs(tmpdir, exist_ok = True)

opts = {
    'datadir' : tmpdir,
    'durdnndir' : join(voicedir, 'dur')
}

with open(join(tmpdir, 'text.xml'),'w') as fout:
    fout.write('<doc>')
    fout.write(inputtxt)
    fout.write('</doc>\n')

with open(join(tmpdir, 'text_full.xml'),'w') as fout:
    fout.write(final_cex.to_string())

pyIdlak.gen.feat_to_ark(join(tmpdir, 'cex.ark'), dnnfeatures)


# Duration modelling
opts['exp'] = './slt_pmdl/dur'
opts['duroutdir'] = join(tmpdir, 'durout')
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
            line = line[:-1]
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


"""
SP.call(cmd + ' > bashres.ark', shell=True)
bashres = collections.OrderedDict()
bashark = open('bashres.ark').readlines()
pat = re.compile(r'^(?P<fid>\S+)\s+\[')
curid = False
for line in bashark:
    empty_curid = False
    line = line.strip()
    m = pat.match(line)
    if m is not None:
        curid = m.group('fid')
        bashres[curid] = []
        print ('loading', curid)
        line = re.sub(pat, '', line).strip()
    if not line:
        continue
    if line.endswith(']'):
        empty_curid = True
        line = line[:-1]
    if not curid:
        raise IOError('ark not formated as expected')
    bashres[curid].append(list(map(float, line.split())))
    if empty_curid:
        curid = ''

for curid in bashres:
    b_mat = np.array(bashres[curid])
    p_mat = np.array(durations[curid])
    if b_mat.shape[0] != p_mat.shape[0]:
        raise ValueError(curid + ' number rows do not match')
    if b_mat.shape[1] != p_mat.shape[1]:
        raise ValueError(curid + ' number columns do not match')
    diff = np.allclose(b_mat, p_mat)
    if not diff:
        raise ValueError(curid + ' is not almost equal')
"""

#for spurtid, durmat in durations.items():
    #print (spurtid, ':')
    #for r in durmat[:1]:
        #print (' '.join(map(lambda v: "{0:10.6f}".format(v), r)))


# generate_f0
# generate_spec
# vocode
# save



print ("All good")