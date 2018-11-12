#!/bin/bash
set -euo pipefail


inputtxt="This is a sample. With two sentences"
voice_dir=./slt_pmdl
outdir=$HOME/tmp/idlak_out
mkdir -p $outdir
source $voice_dir/voice.conf

cex_freq=$voice_dir/lang/cex.ark.freq
var_cmp=$voice_dir/lang/var_cmp.txt
durdnndir=$voice_dir/dur
f0dnndir=$voice_dir/pitch
dnndir=$voice_dir/acoustic
cleanup=
datadir=$HOME/tmp/idlak_tmp
tpdb=`readlink -f $voice_dir/lang/`
extra_feats=

mkdir -p $datadir



# Working directories
lbldurdir=$datadir/lbldur
duroutdir=$datadir/durout


# Add the binaries to the path
[ -f path.sh ] && . ./path.sh;


# Create the input
echo "<parent>$inputtxt</parent>" > $datadir/text.xml

# Generate CEX features
idlaktxp --pretty --general-lang=$lng --general-acc=$acc --tpdb=$tpdb $datadir/text.xml - \
    | idlakcex --pretty --general-lang=$lng --general-acc=$acc --cex-arch=default --tpdb=$tpdb - $datadir/text_full.xml

# Some python magic
python3 local/idlak_make_lang.py --mode 2 -r "test" \
    $datadir/text_full.xml $cex_freq $datadir/cex.ark

# Generate input feature for duration modelling
cat $datadir/cex.ark \
    | awk -v extras="$extra_feats" '{print $1, "["; $1=""; na = split($0, a, ";"); for (i = 1; i < na; i++) for (state = 0; state < 5; state++) print extras, a[i], state; print "]"}' \
    | copy-feats ark:- ark,scp:$datadir/in_durfeats.ark,$datadir/in_durfeats.scp


# Duration synthesis
mkdir -p $lbldurdir
cp $datadir/in_durfeats.scp $lbldurdir/feats.scp
cut -d ' ' -f 1 $lbldurdir/feats.scp | awk -v spk=$spk '{print $1, spk}' > $lbldurdir/utt2spk
[ -f $durdnndir/cmvn.scp ] && cp $durdnndir/cmvn.scp $lbldurdir/cmvn.scp
utils/utt2spk_to_spk2utt.pl $lbldurdir/utt2spk > $lbldurdir/spk2utt

# Generate label with DNN-generated duration

#  1. forward pass through duration DNN

rm -rf $duroutdir

cmpdir=$duroutdir/cmp/
wavdir=$duroutdir/wav/
mkdir -p $cmpdir
mkdir -p $wavdir

infeats_tst="ark:copy-feats scp:$lbldurdir/feats.scp ark:- |"

incmvn_opts=`cat < $durdnndir/incmvn_opts`
echo "Applying global cmvn on labels"
infeats_tst="$infeats_tst apply-cmvn $incmvn_opts $durdnndir/incmvn_glob.ark ark:- ark:- |"

echo "Applying feature transform on labels"
infeats_tst="$infeats_tst nnet-forward $durdnndir/input_final.feature_transform ark:- ark:- |"

feat_transf=$durdnndir/reverse_final.feature_transform
postproc="ark:| cat "

echo "Applying (reversed) per-speaker cmvn on output features"
cmvn_opts=`cat < $durdnndir/cmvn_opts`
postproc="$postproc | apply-cmvn --reverse $cmvn_opts --utt2spk=ark:$lbldurdir/utt2spk scp:${lbldurdir/lbldata/data}/cmvn.scp ark:- ark,t:-"

awkcmd="'"'($2 == "["){if (out) close(out); out=dir $1 ".cmp";}($2 != "["){if ($NF == "]") $NF=""; print $0 > out}'"'"
postproc="$postproc | tee $duroutdir/feats.ark | awk -v dir=$cmpdir $awkcmd"

nnet=$durdnndir/final.nnet

# echo "${infeats_tst}"

nnet-forward --reverse-transform=true --feature-transform=$feat_transf $nnet "${infeats_tst}" "${postproc}" > /dev/null
