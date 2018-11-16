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
datadir = expanduser('~/tmp/idlak_tmp_py')
pyoutdir = join(datadir, 'pyout')
voicedir = join(dirname(abspath(__file__)), 'slt_pmdl')

# Clean the output directories
shutil.rmtree(join(outdir), ignore_errors = True)
shutil.rmtree(join(datadir), ignore_errors = True)
os.makedirs(outdir, exist_ok = True)
os.makedirs(datadir, exist_ok = True)

voice = pyIdlak.TangleVoice(voicedir, loglvl = logging.DEBUG)
final_cex = voice.process_text(inputtxt)
durfeatures = voice.cex_to_dnn_features(final_cex)
durpred = voice.generate_state_durations(durfeatures, False)
durations = voice.generate_state_durations(durfeatures)
pitchfeatures = voice.combine_durations_and_features(durations, durfeatures)
rawpitchpred = voice.generate_pitch(pitchfeatures, mlpg = False, extract = False)
pitch_nomlpg = voice.generate_pitch(pitchfeatures, mlpg = False)
pitch = voice.generate_pitch(pitchfeatures)

acfdnnfeatures_nopitchmlpg = voice.combine_pitch_and_features(pitch_nomlpg, pitchfeatures)
acfdnnfeatures = voice.combine_pitch_and_features(pitch, pitchfeatures)

acffeatures_nopitchmlpg = voice.generate_acoustic_features(acfdnnfeatures_nopitchmlpg)
acffeatures = voice.generate_acoustic_features(acfdnnfeatures)

##### Finished



# Save bits and pieces of the results
os.makedirs(pyoutdir, exist_ok = True)
for fid, fdurs in durpred.items():
    with open(join(pyoutdir, fid + '.dur.cmp'), 'w') as fout:
        for d in fdurs:
            fout.write(' '.join(map(lambda f: '{:.6f}'.format(f), d)) + '\n')
voice.durations_to_mlf(join(pyoutdir, 'pyIdlak_lab.mlf'), durations)

pyIdlak.gen.feat_to_ark(join(pyoutdir, 'pitch.in.ark'), pitchfeatures, matrix = True)
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'pitch.out.ark'), rawpitchpred, matrix = True, fmt='{:.5f}')
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'pitch.mlpg.ark'), pitch, matrix = True, fmt='{:.5f}')

pyIdlak.gen.feat_to_ark(join(pyoutdir, 'acfnopitchmlpg.in.ark'), acfdnnfeatures_nopitchmlpg, matrix = True, fmt='{:.5f}')
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'acf.in.ark'), acfdnnfeatures, matrix = True, fmt='{:.5f}')
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'acfnopitchmlpg.out.ark'), acffeatures_nopitchmlpg, matrix = True, fmt='{:.5f}')
pyIdlak.gen.feat_to_ark(join(pyoutdir, 'acf.out.ark'), acffeatures, matrix = True, fmt='{:.5f}')



print ("\n\n'Bash' Version Started\n\n\n")

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
    infeats_tst = 'ark:copy-feats scp:{lbl}/feats.scp ark:-'.format(**dnnopts)
    if 'incmvn_opts' in dnnopts:
        infeats_tst += ' | apply-cmvn {incmvn_opts}'.format(**dnnopts)
        infeats_tst += ' {dnndir}/incmvn_glob.ark ark:- ark:-'.format(**dnnopts)
    if 'infeat_transf' in dnnopts:
        infeats_tst += ' | nnet-forward {infeat_transf}'.format(**dnnopts)
        infeats_tst += ' ark:- ark:-'.format(**dnnopts)
    infeats_tst += ' |'

    postproc = "ark:| cat "
    if 'cmvn_opts' in dnnopts:
        postproc += " | apply-cmvn --reverse {cmvn_opts}".format(**dnnopts)
        postproc += " --utt2spk=ark:{lbl}/utt2spk".format(**dnnopts)
        postproc += " scp:{lbl}/cmvn.scp ark:- ark,t:-".format(**dnnopts)
    postproc += " | copy-feats ark:- ark,t,scp:{out}/feats.ark,{out}/feats.scp".format(**dnnopts)

    durcmd  = "nnet-forward --reverse-transform=true"
    durcmd += " --feature-transform={feat_transf} {nnet}".format(**dnnopts)
    durcmd += " '" + infeats_tst + "' '" + postproc + "'"
    SP.run(durcmd, shell = True)

    ark = parse_arkfile(join(dnnopts['out'], 'feats.ark'))
    for sptid, pred in ark.items():
        cmpfile = join(dnnopts['cmp'], sptid + '.cmp')
        np.savetxt(cmpfile, pred, fmt = "%.6f")


def parse_arkfile(fname):
    ark = collections.OrderedDict()
    arkfile = open(fname).read()
    arkfile = re.sub(';', '\n', arkfile)
    repat = re.compile('(?P<id>[a-zA-Z0-9]+)\s*\[(?P<mat>.*?)\]\s*',
                       flags = re.S)
    for m in re.finditer(repat, arkfile):
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

for name, dnndir in [('dur', durdnndir), ('pitch', pitchdnndir),
                     ('acf_nopitchmlpg', acfdnndir), ('acf', acfdnndir)]:
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
pyIdlak.gen.feat_to_ark(join(datadir, 'cex.ark'), durfeatures)


####### Duration modelling

# Input
to_feat_cmd = 'cat {[datadir]}/cex.ark'.format(opts)
to_feat_cmd += ' ' + """
 | awk -v extras="" '{print $1, "["; $1=""; na = split($0, a, ";"); for (i = 1; i < na; i++) for (state = 0; state < 5; state++) print extras, a[i], state; print "]"}'
""".strip()
to_feat_cmd += " | copy-feats ark:- ark,scp:{datadir}/in_durfeats.ark,{datadir}/in_durfeats.scp".format(**opts)
SP.run(to_feat_cmd, shell = True)

scpfile = join(opts['dur']['lbl'], 'feats.scp')
shutil.copy(join(datadir, "in_durfeats.scp"), scpfile)
shutil.copy(join(durdnndir, "cmvn.scp"), opts['dur']['lbl'])
scp_to_spkutt_files(opts['dur']['lbl'], voice, scpfile)

# Predict
run_prediction(opts['dur'])

# Post process
SP.run('./local/makemlf.sh {dur[cmp]} {datadir}'.format(**opts), shell = True)


######## Pitch modelling

# Input
SP.run('python3 local/make_fullctx_mlf_dnn.py'
        ' {datadir}/synth_lab.mlf {datadir}/cex.ark {datadir}/pitchfeat.ark'.format(**opts),
        shell = True)
SP.run('copy-feats ark:{datadir}/pitchfeat.ark ark,scp:{datadir}/in_pitchfeats.ark,{datadir}/in_pitchfeats.scp'.format(**opts), shell = True)
shutil.copyfile(join(datadir, 'in_pitchfeats.scp'), join(opts['pitch']['lbl'], 'feats.scp'))
scpfile = join(opts['pitch']['lbl'], 'feats.scp')
scp_to_spkutt_files(opts['pitch']['lbl'], voice, scpfile)

# Predict
run_prediction(opts['pitch'])

# Post process (MLPG)
f0_win = "-d win/logF0_d1.win -d win/logF0_d2.win"
varf0 =  ' '.join(map(str, voice._variances['logf0']))

mlpgcmd = """
cat {pitch[out]}/feats.scp | \
while read line; do
    echo ${{line%% *}} "["
    copy-feats scp:"echo $line |" ark,t:- \
        | awk -v var="{varf0}" '{{ if ($NF == "]" || NR == 2) cvar = "0.0 0.0 0.0 0.0 0.0 0.0"; else cvar = var; if ($2 == "[") {{}} else {{if ($NF == "]") {{$0 = substr($0, 1, length($0) - 2);}} print $0, cvar}}}}' \
        | x2x +a +f \
        | mlpg -i 0 -m 1 {f0_win} \
        | x2x +f +a2
    echo "]"
done | sed 's/\t/ /g' > {pitch[out]}/feats_mlpg.ark
""".format(varf0 = varf0, f0_win = f0_win, **opts).strip()
SP.run(mlpgcmd, shell = True)

######## Acoustic feature modelling (no pitch mlpg)

# Input
cmd  = "select-feats 0-1 ark:{pitch[out]}/feats.ark ark:-".format(**opts)
cmd += " | paste-feats ark:- scp:{pitch[lbl]}/feats.scp".format(**opts)
cmd += "    ark,t:{datadir}/acf_nopitchmlpg_feat.ark".format(**opts)
SP.run(cmd, shell = True)

cmd = "copy-feats ark:{datadir}/acf_nopitchmlpg_feat.ark ark,scp:{acf_nopitchmlpg[lbl]}/feats.ark,{acf_nopitchmlpg[lbl]}/feats.scp".format(**opts)
SP.run(cmd, shell = True)
scpfile = join(opts['acf_nopitchmlpg']['lbl'], 'feats.scp')
scp_to_spkutt_files(opts['acf_nopitchmlpg']['lbl'], voice, scpfile)

run_prediction(opts['acf_nopitchmlpg'])


####### Acoustic feature modelling

# Input
cmd  = "select-feats 0-1 ark:{pitch[out]}/feats_mlpg.ark ark:-".format(**opts)
cmd += " | paste-feats ark:{pitch[out]}/feats_mlpg.ark scp:{pitch[lbl]}/feats.scp".format(**opts)
cmd += "    ark,t:{datadir}/acf_feat.ark".format(**opts)
SP.run(cmd, shell = True)

cmd = "copy-feats ark:{datadir}/acf_feat.ark ark,scp:{acf[lbl]}/feats.ark,{acf[lbl]}/feats.scp".format(**opts)
SP.run(cmd, shell = True)
scpfile = join(opts['acf']['lbl'], 'feats.scp')
scp_to_spkutt_files(opts['acf']['lbl'], voice, scpfile)

run_prediction(opts['acf'])


######## Checking

print ("\n\nStarted Checking\n")

def compare_arks(pyfn, bashfn):
    pyark = parse_arkfile(pyfn)
    bashark = parse_arkfile(bashfn)
    for spurtid, pymat in pyark.items():
        bashmat = bashark[spurtid]
        if pymat.shape[0] != bashmat.shape[0]:
            raise ValueError("unequal number of rows "
                             "py: {[0]} bash: {[0]}".format(pymat.shape, bashmat.shape))
        if pymat.shape[1] != bashmat.shape[1]:
            raise ValueError("unequal number of columns "
                             "py: {[1]} bash: {[1]}".format(pymat.shape, bashmat.shape))
        if not np.allclose(pymat, bashmat, atol = 1e-3, rtol=0.):
            raise ValueError("different values")


# check the duration prediction
print("Checking the duration prediction")
# Also checking the cmp files were split correctly only this time
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
pyark = join(pyoutdir, 'pitch.in.ark')
bashark = join(datadir, 'pitchfeat.ark')
compare_arks(pyark, bashark)

print("Checking the pitch prediction")
pyark = join(pyoutdir, 'pitch.out.ark')
bashark = join(opts['pitch']['out'], 'feats.ark')
compare_arks(pyark, bashark)

print("Checking the acf no pitch mlpg input features")
pyark = join(pyoutdir, 'acfnopitchmlpg.in.ark')
bashark = join(datadir, 'acf_nopitchmlpg_feat.ark')
compare_arks(pyark, bashark)

print("Checking the acf no pitch mlpg prediction")
pyark = join(pyoutdir, 'acfnopitchmlpg.out.ark')
bashark = join(opts['acf_nopitchmlpg']['out'], 'feats.ark')
compare_arks(pyark, bashark)

print("Checking the acf input features")
pyark = join(pyoutdir, 'acf.in.ark')
bashark = join(datadir, 'acf_feat.ark')
compare_arks(pyark, bashark)

print("Checking the acf prediction")
pyark = join(pyoutdir, 'acf.out.ark')
bashark = join(opts['acf']['out'], 'feats.ark')
compare_arks(pyark, bashark)




print ("\nAll good\n")
