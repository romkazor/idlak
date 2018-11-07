#!/usr/bin/env python3

import sys
import os
import logging
import subprocess

# Import pyIdlak
_srcpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', 'src')
sys.path.insert(0, _srcpath)
import pyIdlak


inputtxt = "This is a sample. With two sentences."
outdir = os.path.expanduser('~/tmp/idlak_out')
voicedir = os.path.join('slt_pmdl')

print('loading voice')
voice = pyIdlak.TangleVoice(voicedir, loglvl = logging.DEBUG)

print('processing text')
final_cex = voice.process_text(inputtxt)


print('converting text to DNN input features')
dnnfeatures = voice.convert_to_dnn_features(final_cex)

print('generating durations')
durations = voice.generate_duration(dnnfeatures)
# generate_f0
# generate_spec
# vocode
# save

# apply-cmvn --norm-means=true --norm-vars=true ./slt_pmdl/dur/incmvn_glob.ark scp:/home/dave/tmp/idlak_tmp/lbldur/feats.scp ark:-


"""
nnet-forward --reverse-transform=true --feature-transform=./slt_pmdl/dur/reverse_final.feature_transform ./slt_pmdl/dur/final.nnet
    'ark:copy-feats scp:/home/dave/tmp/idlak_tmp/lbldur/feats.scp ark:-
        | apply-cmvn --norm-means=true --norm-vars=true ./slt_pmdl/dur/incmvn_glob.ark ark:- ark:-
        | nnet-forward ./slt_pmdl/dur/input_final.feature_transform ark:- ark:- |'
    'ark,t:
        | cat
        | apply-cmvn --reverse --norm-means=false --norm-vars=true --utt2spk=ark:/home/dave/tmp/idlak_tmp/lbldur/utt2spk scp:/home/dave/tmp/idlak_tmp/lbldur/cmvn.scp ark:- ark,t:-
        | tee /home/dave/tmp/idlak_tmp/durout/feats.ark
        | awk -v dir=/home/dave/tmp/idlak_tmp/durout/cmp/ '\''($2 == "["){if (out) close(out); out=dir $1 ".cmp";}($2 != "["){if ($NF == "]") $NF=""; print $0 > out}'\'''
"""