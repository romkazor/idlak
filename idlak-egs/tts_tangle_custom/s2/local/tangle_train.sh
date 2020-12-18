#!/bin/bash
set -euo pipefail
source cmd.sh
source path.sh

lng=
acc=
spks=
srate=
rawaudiodir=
labeldir=
stage=
endstage=
runnorm=
tpdb=
nodev=
nj=
network_type=
FRAMESHIFT=
TMPDIR=

. parse_options.sh || exit 1;

echo
echo "---- Running Tangle Training ----"
echo "  language:      $lng"
echo "  accent:        $acc"
echo "  speaker(s):    $spks"
echo "  sample rate:   $srate"
echo "  network type:  $network_type"
echo "  audio dir:     $rawaudiodir"
echo "  label dir:     $labeldir"
echo "  tpdb dir:      $tpdb"
echo "---------------------------------"
echo

function incr_stage() {
    stage=$(( $stage + 1 ))
    if [ $stage -gt $endstage ]; then
        echo
        echo "##### Finished after running step $(( $stage - 1 )) #####"
        echo
        exit 0
    fi
}

testdatadir=$tpdb/$lng/testdata

# Working directories
datadir=$HERE/data/$lng/$acc/$spks
f0datadir=$HERE/f0data/$lng/$acc/$spks
expdir=$HERE/exp/$lng/$acc/$spks
lbldatadir=$HERE/lbldata/$lng/$acc/$spks
lblf0datadir=$HERE/lblf0data/$lng/$acc/$spks
lbldurdatadir=$HERE/lbldurdata/$lng/$acc/$spks
durdatadir=$HERE/durdata/$lng/$acc/$spks
exp_dnndir=$HERE/exp-dnn/$lng/$acc/$spks
exp_aligndir=$HERE/exp-align/$lng/$acc/$spks

# Output directories
voicedir=voices/$lng/$acc/${spks}_pmdl
testoutdir=testout/$lng/$acc/$spks

# Temporary directories
export featdir=$TMPDIR/dnn_feats/idlak/$lng/$acc/$spks

############################################
#####     Step -2/-1: Clean options    #####
############################################

# Clean up all working directories
if [ $stage -le -2 ]; then
    echo "##### Step -2: cleaning up ALL voices and working directories #####"
    cd $HERE
    rm -rf data f0data exp lbldata lblf0data lbldurdata durdata exp-dnn exp-align voices testoutdir
    stage=-1 # bit of a hack
    incr_stage
fi

# Clean up voice working directories
if [ $stage -le -1 ]; then
    echo "##### Step -1: cleaning up voice and working directories #####"
    rm -rf $datadir $f0datadir $expdir $lbldatadir $lbldatadir $lblf0datadir $lbldurdatadir
    rm -rf $durdatadir $exp_dnndir $exp_aligndir $voicedir $testoutdir
    incr_stage
fi

############################################
#####     Step 0: Data preparation     #####
############################################

if [ $stage -le 0 ]; then
    echo "##### Step 0: data preparation #####"
    mkdir -p $datadir/{train,dev,full}
    for k in wav.scp utt2spk text.xml; do
        rm -f $datadir/{train,dev,full}/$k
    done

    for spk in $spks; do
        audio_dir=$rawaudiodir/$lng/$acc/$spk/${srate}
        label_dir=$labeldir/$lng/$acc/$spk
        mkdir -p $datadir/{train,dev,full}/$spk

        # Get the audio at the correct sample rate
        if [ ! -e $audio_dir ]; then
            # create a symbolic link for the original audio sample rate
            for f in $rawaudiodir/$lng/$acc/$spk/*_orig/*.wav; do
                org_dir=`dirname $f`
                org_dir=`basename $org_dir`
                cd $rawaudiodir/$lng/$acc/$spk
                org_srate=`sox --info -r $f`
                if [ ! -e "$org_srate" ]; then
                    ln -s  $org_dir $org_srate
                fi
                break
            done
            # if not the same sample rate as original then use sox to resample
            if [ ! -e $audio_dir ]; then
                mkdir -p $audio_dir
                if [ "$srate" -gt "$org_srate" ]; then
                    echo "    Up-sampling data"
                    for i in $rawaudiodir/$lng/$acc/$spk/*_orig/*.wav; do
                        sox $i $audio_dir/`basename $i` remix 1 rate -v -s -a 48000 dither -s
                    done
                else
                    echo "    Down-sampling data"
                    for i in $rawaudiodir/$lng/$acc/$spk/*_orig/*.wav; do
                        sox $i -r $srate $audio_dir/`basename $i`
                    done
                fi
            fi
        fi

        # Create a list of files to process if not done already (can be modified later)
        flist=$datadir/$lng.$acc.$spk.flist
        if [ ! -e $flist ]; then
            cd $audio_dir
            pycmd="import sys,os,random,glob; "
            pycmd+="random.seed(0); "
            pycmd+="files = glob.glob('*.wav'); "
            pycmd+="random.shuffle(files); "
            pycmd+="print ('\n'.join(map(lambda f: os.path.splitext(f)[0], files)))"
            python -c "$pycmd" > $flist
        fi

        # Split train, dev sets
        # linux and mac have to do this in different ways
        head -n-$nodev $flist > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            head -n-$nodev $flist | sed s'|^\(.*\)|\1 '$audio_dir/'\1.wav|' | sort -u > $datadir/train/$spk/wav.scp
        else
            tail -r $flist | tail -n +$nodev | tail -r | sed s'|^\(.*\)|\1 '$audio_dir/'\1.wav|' | sort -u  > $datadir/train/$spk/wav.scp
        fi
        cat $datadir/train/$spk/wav.scp >> $datadir/train/wav.scp

        tail -n$nodev $flist | sed s'|^\(.*\)|\1 '$audio_dir/'\1.wav|' | sort -u  > $datadir/dev/$spk/wav.scp
        cat $datadir/dev/$spk/wav.scp >> $datadir/dev/wav.scp

        cat $datadir/{train,dev}/$spk/wav.scp | sort -u > $datadir/full/$spk/wav.scp

        # Generate utt2spk / spk2utt info
        for step in train dev; do
            cat $datadir/$step/$spk/wav.scp | awk -v spk=$spk '{print $1, spk}' | sort -u  > $datadir/$step/$spk/utt2spk
            cat $datadir/$step/$spk/utt2spk >> $datadir/$step/utt2spk
            utt2spk_to_spk2utt.pl < $datadir/$step/$spk/utt2spk > $datadir/$step/$spk/spk2utt
        done

        # Generate transcriptions
        cd $HERE
        for step in train dev full; do
            python3 local/idlak_extract_utterances.py -i $label_dir/text.xml -s $datadir/$step/$spk/wav.scp -o $datadir/$step/$spk/text.xml
        done

        # Combine transcriptions
        for step in train dev full; do
            if [ ! -e  $datadir/$step/text.xml ]; then
                head -n1 $datadir/$step/$spk/text.xml > $datadir/$step/text.xml
                echo "<all_scripts>" >> $datadir/$step/text.xml
            fi
            grep -v "<?xml" $datadir/$step/$spk/text.xml | sed "s|^|  |" >> $datadir/$step/text.xml
        done
    done

    for step in train dev; do
        for k in wav.scp utt2spk; do
            sort -o $datadir/$step/$k $datadir/$step/$k
        done
        utt2spk_to_spk2utt.pl < $datadir/$step/utt2spk > $datadir/$step/spk2utt
    done

    for k in wav.scp utt2spk; do
        cat $datadir/{train,dev}/$k | sort -u > $datadir/full/$k
    done
    utt2spk_to_spk2utt.pl < $datadir/full/utt2spk > $datadir/full/spk2utt

    for step in train dev full; do
        echo "</all_scripts>" >> $datadir/$step/text.xml
    done

    incr_stage
fi

############################################
##### Step 1: acoustic data generation #####
############################################

if [ $stage -le 1 ]; then
    echo "##### Step 1: acoustic data generation #####"
    mkdir -p $featdir

    if [ "$srate" = "48000" ]; then
        configext="-48k.conf"
    elif [ "$srate" = "16000" ]; then
        configext=".conf"
    else
        echo "Sample rate '$srate' not supported for audio feature extraction"
        exit 1
    fi

    # Use kaldi to generate MFCC features for alignment
    for step in full; do
        steps/make_mfcc.sh --nj $nj --mfcc-config conf/mfcc${configext} $datadir/$step $expdir/make_mfcc/$step $featdir
        steps/compute_cmvn_stats.sh $datadir/$step $expdir/make_mfcc/$step $featdir
    done

    # Use Kaldi + SPTK tools to generate F0 / BNDAP / MCEP
    # NB: respective configs are in conf/pitch.conf, conf/bndap.conf, conf/mcep.conf
    for step in train dev; do
        rm -f $datadir/$step/feats.scp
        # Generate f0 features
        steps/make_pitch.sh --pitch-config conf/pitch${configext}  $datadir/$step $expdir/make_pitch/$step $featdir
        cp $datadir/$step/pitch_feats.scp $datadir/$step/feats.scp
        # Compute CMVN on pitch features, to estimate min_f0 (set as mean_f0 - 2*std_F0)
        steps/compute_cmvn_stats.sh  $datadir/$step  $expdir/compute_cmvn_pitch/$step  $featdir
        # For bndap / mcep extraction to be successful, the frame-length must be adjusted
        # in relation to the "reasonable minimum" pitch frequency.
        # We therefore do something speaker specific using the mean / std deviation from
        # the pitch for each speaker, i.e. min_f0 ~ mean(f0) - 2*std(f0)
        # Note that the CMVN based f0 estimation will not work well if there is a large amount of silence
        # in the recordings, so you may want to override the value in that case.
        for spk in $spks; do
            min_f0=`copy-feats scp:"awk -v spk=$spk '(\\$1 == spk){print}' $datadir/$step/cmvn.scp |" ark,t:- \
                | awk '(NR == 2){n = \$NF; m = \$2 / n}(NR == 3){std = sqrt(\$2/n - m * m)}END{print m - 2*std}'`
            echo "Minimum f0: $min_f0"
            # Rule of thumb recipe; probably try with other window sizes?
            bndapflen=`awk -v f0=$min_f0 'BEGIN{printf "%d", 4.6 * 1000.0 / f0 + 0.5}'`
            mcepflen=`awk -v f0=$min_f0 'BEGIN{printf "%d", 2.3 * 1000.0 / f0 + 0.5}'`
            f0flen=`awk -v f0=$min_f0 'BEGIN{printf "%d", 2.3 * 1000.0 / f0 + 0.5}'`
            echo "using wsizes: $bndapflen $mcepflen"
            echo "$spk" > $datadir/$step/$spk.lst
            subset_data_dir.sh --spk-list $datadir/$step/$spk.lst $datadir/$step $datadir/${step}_$spk

            # Regenerate pitch with more appropriate window
            steps/make_pitch.sh --nj $nj --pitch-config conf/pitch${configext} --frame_length $f0flen    $datadir/${step}_$spk $expdir/make_pitch/${step}_$spk  $featdir
            # Generate Band Aperiodicity feature
            steps/make_bndap.sh --nj $nj --bndap-config conf/bndap${configext} --frame_length $bndapflen $datadir/${step}_$spk $expdir/make_bndap/${step}_$spk  $featdir
            # Generate Mel Cepstral features
            steps/make_mcep.sh  --nj $nj --mcep-config  conf/mcep${configext} --frame_length $mcepflen  $datadir/${step}_$spk $expdir/make_mcep/${step}_$spk   $featdir
        done
        # Merge features
        cat $datadir/${step}_*/bndap_feats.scp > $datadir/$step/bndap_feats.scp
        cat $datadir/${step}_*/mcep_feats.scp > $datadir/$step/mcep_feats.scp
        # Have to set the length tolerance to 1, as mcep files are generated using SPTK
        # which uses different windowing so are a bit longer than the others feature files
        paste-feats --length-tolerance=1 scp:$datadir/$step/mcep_feats.scp scp:$datadir/$step/bndap_feats.scp ark,scp:$featdir/${step}_cmp_feats.ark,$datadir/$step/feats.scp
        # Copy pitch feature in separate folder
        mkdir -p $f0datadir/${step}
        cp $datadir/$step/pitch_feats.scp $f0datadir/${step}/feats.scp
        for k in utt2spk spk2utt; do
            cp $datadir/$step/$k $f0datadir/${step}/$k;
        done
    done

    incr_stage
fi


############################################
#####      Step 2: label creation      #####
############################################
dict=$datadir/local/dict

if [ $stage -le 2 ]; then
    echo "##### Step 2: label creation #####"
    # We are using the idlak front-end for processing the text
    for step in train dev full; do
        # Normalise text and generate phoneme information
        if [ $runnorm = 1 ]; then
            echo "Running normaliser, this is not recommended and takes a long time"
            $KALDI_ROOT/idlak-misc/pyidlaktxp/pyidlaktxp.py --verbose 3 --general-lang=$lng --general-acc=$acc --tpdb=$tpdb $datadir/$step/text.xml $datadir/$step/text_norm.xml
        else
            idlaktxp --pretty --general-lang=$lng --general-acc=$acc --tpdb=$tpdb $datadir/$step/text.xml $datadir/$step/text_norm.xml
        fi
        # Generate full labels
    done

    # Generate language models for alignment
    mkdir -p $dict
    # Create dictionary and text files
    cd $HERE
    python local/idlak_make_lang.py --mode 0 $datadir/full/text_norm.xml $datadir/full $dict
    # Fix data directory, in case some recordings are missing
    utils/fix_data_dir.sh $datadir/full

    incr_stage
fi

#######################################
#####   Step 3: Forced alignment  #####
#######################################
lang=$datadir/lang
expa=$exp_aligndir
train=$datadir/full


if [ $stage -le 3 ]; then
    echo "##### Step 3: forced alignment #####"
    ###############################
    ##  3a: monophone alignment  ##
    ###############################
    echo " #### monophone alignment ####"
    rm -rf $dict/lexiconp.txt $lang
    utils/prepare_lang.sh --num-nonsil-states 5 --share-silence-phones true $dict "<OOV>" $datadir/local/lang_tmp $lang
    #utils/validate_lang.pl $lang

    # Now running the normal kaldi recipe for forced alignment
    #test=$datadir/eval_mfcc

    rm -rf $train/split$nj
    split_data.sh --per-utt $train $nj
    [ -d $train/split$nj ] || mv $train/split${nj}utt $train/split$nj
    steps/train_mono.sh --boost-silence 1.25 --nj $nj --cmd "$train_cmd" \
        $train $lang $expa/mono || exit 1;
    steps/align_si.sh --boost-silence 1.25 --nj $nj --cmd "$train_cmd" \
        $train $lang $expa/mono $expa/mono_ali || exit 1;
    steps/train_deltas.sh --boost-silence 1.25 --cmd "$train_cmd" \
        2000 10000 $train $lang $expa/mono_ali $expa/tri1 || exit 1;
    steps/align_si.sh  --nj $nj --cmd "$train_cmd" \
        $train $lang $expa/tri1 $expa/tri1_ali || exit 1;
    steps/train_deltas.sh --cmd "$train_cmd" \
        5000 50000 $train $lang $expa/tri1_ali $expa/tri2 || exit 1;

    # Create quinphone alignments
    steps/align_si.sh  --nj $nj --cmd "$train_cmd" \
        $train $lang $expa/tri2 $expa/tri2_ali_full || exit 1;

    steps/train_deltas.sh --cmd "$train_cmd" \
        --context-opts "--context-width=5 --central-position=2" \
        5000 50000 $train $lang $expa/tri2_ali_full $expa/quin || exit 1;

    # Create final alignments
    #split_data.sh --per-utt $train 9
    steps/align_si.sh  --nj $nj --cmd "$train_cmd" \
        $train $lang $expa/quin $expa/quin_ali_full || exit 1;

    ################################
    ## 3b. Align with full labels ##
    ################################
    echo " #### full label alignment ####"
    # Convert to phone-state alignement
    for step in full; do
        ali=$expa/quin_ali_$step

        # some versions of gzip do not support { } expansion
        alifiles=""
        for n in $(seq 1 $nj); do
          alifiles="$alifiles $ali/ali.$n.gz"
        done

        # Extract phone alignment
        ali-to-phones --per-frame $ali/final.mdl ark:"gunzip -c $alifiles|" ark,t:- \
            | utils/int2sym.pl -f 2- $lang/phones.txt > $ali/phones.txt

        # Extract state alignment
        ali-to-hmmstate $ali/final.mdl ark:"gunzip -c $alifiles|" ark,t:$ali/states.tra

        # Extract word alignment
        linear-to-nbest ark:"gunzip -c $alifiles|" \
            ark:"utils/sym2int.pl --map-oov 1669 -f 2- $lang/words.txt < $datadir/$step/text |" '' '' ark:- \
            | lattice-align-words $lang/phones/word_boundary.int $ali/final.mdl ark:- ark:- \
            | nbest-to-ctm --frame-shift=$FRAMESHIFT --precision=3 ark:- - \
            | utils/int2sym.pl -f 5 $lang/words.txt > $ali/wrdalign.dat

        # Regenerate text output from alignment
        python3 local/idlak_make_lang.py --mode 1 "2:0.03,3:0.2" "4" $ali/phones.txt $ali/wrdalign.dat $datadir/$step/text_align.xml $ali/states.tra

        # Generate corresponding quinphone full labels
        idlaktxp --pretty --general-lang=$lng --general-acc=$acc --tpdb=$tpdb $datadir/$step/text_align.xml $datadir/$step/text_anorm.xml
        idlakcex --pretty --general-lang=$lng --general-acc=$acc --cex-arch=default --tpdb=$tpdb $datadir/$step/text_anorm.xml $datadir/$step/text_afull.xml
        python3 local/idlak_make_lang.py --mode 2 $datadir/$step/text_afull.xml $datadir/$step/cex.ark > $datadir/$step/cex_output_dump

        # Merge alignment with output from idlak cex front-end => gives you a nice vector
        # NB: for triphone alignment:
        # make-fullctx-ali-dnn  --phone-context=3 --mid-context=1 --max-sil-phone=15 $ali/final.mdl ark:"gunzip -c $ali/ali.{1..$nj}.gz|" ark,t:$datadir/$step/cex.ark ark,t:$datadir/$step/ali
        make-fullctx-ali-dnn --max-sil-phone=15 $ali/final.mdl ark:"gunzip -c $alifiles|" ark,t:$datadir/$step/cex.ark ark,t:$datadir/$step/ali


        # UGLY convert alignment to features
        cat $datadir/$step/ali \
            | awk '{print $1, "["; $1=""; na = split($0, a, ";"); for (i = 1; i < na; i++) print a[i]; print "]"}' \
            | copy-feats ark:- ark,scp:$featdir/in_feats_$step.ark,$featdir/in_feats_$step.scp
    done

# HACKY
# Generate features for duration modelling
# we remove relative position within phone and state
    copy-feats ark:$featdir/in_feats_full.ark ark,t:- \
        | awk -v nstate=5 'BEGIN{oldkey = 0; oldstate = -1; for (s = 0; s < nstate; s++) asd[s] = 0}
function print_phone(vkey, vasd, vpd) {
      for (s = 0; s < nstate; s++) {
         print vkey, s, vasd[s], vpd;
         vasd[s] = 0;
      }
}
(NF == 2){print}
(NF > 2){
   n = NF;
   if ($NF == "]") n = NF - 1;
   state = $(n-4); sd = $(n-3); pd = $(n-1);
   for (i = n-4; i <= NF; i++) $i = "";
   len = length($0);
   if (n != NF) len = len -1;
   key = substr($0, 1, len - 5);
   if ((key != oldkey) && (oldkey != 0)) {
      print_phone(oldkey, asd, opd);
      oldstate = -1;
   }
   if (state != oldstate) {
      asd[state] += sd;
   }
   opd = pd;
   oldkey = key;
   oldstate = state;
   if (NF != n) {
      print_phone(key, asd, opd);
      oldstate = -1;
      oldkey = 0;
      print "]";
   }
}' > $featdir/tmp_durfeats_full.ark

    duration_feats="ark:$featdir/tmp_durfeats_full.ark"
    nfeats=$(feat-to-dim "$duration_feats" -)
    # Input
    select-feats 0-$(( $nfeats - 3 )) "$duration_feats" ark,scp:$featdir/in_durfeats_full.ark,$featdir/in_durfeats_full.scp
    # Output: duration of phone and state are assumed to be the 2 last features
    select-feats $(( $nfeats - 2 ))-$(( $nfeats - 1 )) "$duration_feats" ark,scp:$featdir/out_durfeats_full.ark,$featdir/out_durfeats_full.scp

    # Split in train / dev
    for step in train dev; do
        dir=$lbldatadir/$step
        mkdir -p $dir
        #cp $datadir/$step/{utt2spk,spk2utt} $dir
        utils/filter_scp.pl $datadir/$step/utt2spk $featdir/in_feats_full.scp > $dir/feats.scp
        cat $datadir/$step/utt2spk | awk -v lst=$dir/feats.scp 'BEGIN{ while (getline < lst) n[$1] = 1}{if (n[$1]) print}' > $dir/utt2spk
        utils/utt2spk_to_spk2utt.pl < $dir/utt2spk > $dir/spk2utt
        steps/compute_cmvn_stats.sh $dir $dir $dir
    done

    # Same for duration
    for step in train dev; do
        dir=$lbldurdatadir/$step
        mkdir -p $dir
        #cp data/$step/{utt2spk,spk2utt} $dir
        utils/filter_scp.pl $datadir/$step/utt2spk $featdir/in_durfeats_full.scp > $dir/feats.scp
        cat $datadir/$step/utt2spk | awk -v lst=$dir/feats.scp 'BEGIN{ while (getline < lst) n[$1] = 1}{if (n[$1]) print}' > $dir/utt2spk
        utils/utt2spk_to_spk2utt.pl < $dir/utt2spk > $dir/spk2utt
        steps/compute_cmvn_stats.sh $dir $dir $dir

        dir=$durdatadir/$step
        mkdir -p $dir
        #cp data/$step/{utt2spk,spk2utt} $dir
        utils/filter_scp.pl $datadir/$step/utt2spk $featdir/out_durfeats_full.scp > $dir/feats.scp
        cat $datadir/$step/utt2spk | awk -v lst=$dir/feats.scp 'BEGIN{ while (getline < lst) n[$1] = 1}{if (n[$1]) print}' > $dir/utt2spk
        utils/utt2spk_to_spk2utt.pl < $dir/utt2spk > $dir/spk2utt
        steps/compute_cmvn_stats.sh $dir $dir $dir
    done

    # Compute cmvn for f0data
    for step in train dev; do
        dir=$f0datadir/$step
        steps/compute_cmvn_stats.sh $dir $dir $dir

        dir=$datadir/$step
        steps/compute_cmvn_stats.sh $dir $dir $dir
    done

    # Same for input of DNN3: pitch + frame-level labels
    # Generate DNN 3 input data: pitch + frames labels
    for step in train dev; do
        dir=$lblf0datadir/$step
        indir=$lbldatadir/$step
        mkdir -p $dir
        paste-feats scp:$datadir/$step/pitch_feats.scp scp:$indir/feats.scp ark,scp:$featdir/${step}_f0lbl_feats.ark,$dir/feats.scp
        cp $indir/{utt2spk,spk2utt} $dir
        #utils/filter_scp.pl $datadir/$step/utt2spk $featdir/in_durfeats_full.scp > $dir/feats.scp
    done

    incr_stage
fi


#######################################
#####   Step 4: DNN training      #####
#######################################

acdir=$datadir
lblpitchdir=$lblf0datadir
pitchdir=$f0datadir
lbldir=$lbldatadir
durdir=$durdatadir
lbldurdir=$lbldurdatadir
exp=$exp_dnndir
dnndurdir=$exp/tts_${network_type}_dur_3_delta_quin5
dnnf0dir=$exp/tts_${network_type}_f0_3_delta_quin5
dnndir=$exp/tts_${network_type}_train_3_delta_quin5
dnnffdir=$exp/tts_${network_type}_fake_3_delta_quin5
mkdir -p $exp

if [ $stage -le 4 ]; then
    echo "##### Step 4: training DNNs #####"
    #ensure consistency in lists
    for class in train dev; do
        lst=""
        for dir in $acdir $lbldir $pitchdir $lblpitchdir $durdir $lbldurdir; do
            cp $dir/$class/feats.scp $dir/$class/feats_tmp.scp
            lst=${lst:+$lst,}$dir/$class/feats_tmp.scp
        done
        for dir in $acdir $lbldir $pitchdir $lblpitchdir $durdir $lbldurdir; do
            cat $dir/$class/feats_tmp.scp | awk -v lst=$lst  '
BEGIN{ nv=split(lst, v, ",");
  for (i = 1; i <= nv; i++) while (getline < v[i]) {nt[$1] = 1; nk[i "_" $1] = 1;}
  for (k in nt) {
     add = 1;
     for (i = 1; i <= nv; i++) if (nk[i "_" k] != 1) add=0;
     if (add) n[k]=1
  }
}{
   if (n[$1]) print
}' > $dir/$class/feats.scp
        done
    done

    echo " ### Step 4a: duration model DNN ###"
    # A. Small one for duration modelling
    rm -rf $dnndurdir
    if [ "$network_type" == "lstm" ]; then
        mkdir -p $dnndurdir
        echo "<Splice> <InputDim> 6 <OutputDim> 6 <BuildVector> -5 </BuildVector>" > $dnndurdir/delay5.proto
        $cuda_cmd $dnndurdir/_train_nnet.log steps/train_nnet_basic.sh --config conf/dur-lstm-splice5.conf --feature-transform-proto $dnndurdir/delay5.proto \
            $lbldurdir/train $lbldurdir/dev $durdir/train $durdir/dev $dnndurdir
    else
        $cuda_cmd $dnndurdir/_train_nnet.log steps/train_nnet_basic.sh --config conf/dur-nn-splice5.conf \
            $lbldurdir/train $lbldurdir/dev $durdir/train $durdir/dev $dnndurdir
    fi

    echo " ### Step 4b: pitch prediction DNN ###"
    rm -rf $dnnf0dir
    if [ "$network_type" == "lstm" ]; then
        mkdir -p $dnnf0dir
        echo "<Splice> <InputDim> 6 <OutputDim> 6 <BuildVector> -5 </BuildVector>" >$dnnf0dir/delay5.proto
        $cuda_cmd $dnnf0dir/_train_nnet.log steps/train_nnet_basic.sh --config conf/pitch-lstm-splice5.conf --feature-transform-proto $dnnf0dir/delay5.proto \
            $lbldir/train $lbldir/dev $pitchdir/train $pitchdir/dev $dnnf0dir
    else
        $cuda_cmd $dnnf0dir/_train_nnet.log steps/train_nnet_basic.sh --config conf/pitch-nn-splice5.conf \
            $lbldir/train $lbldir/dev $pitchdir/train $pitchdir/dev $dnnf0dir
    fi

    echo " ### Step 4c: acoustic model DNN ###"
    # C. Larger DNN for filter acoustic features
    rm -rf $dnndir
    if [ "$network_type" == "lstm" ]; then
        mkdir -p $dnndir
        echo "<Splice> <InputDim> 258 <OutputDim> 258 <BuildVector> -5 </BuildVector>" >$dnndir/delay5.proto
        $cuda_cmd $dnndir/_train_nnet.log steps/train_nnet_basic.sh --config conf/full-lstm-splice5.conf --feature-transform-proto $dnndir/delay5.proto \
            $lblpitchdir/train $lblpitchdir/dev $acdir/train $acdir/dev $dnndir
    else
        $cuda_cmd $dnndir/_train_nnet.log steps/train_nnet_basic.sh --config conf/full-nn-splice5.conf \
            $lblpitchdir/train $lblpitchdir/dev $acdir/train $acdir/dev $dnndir
    fi

    echo " ### Step 4d: fake DNN for comparisons ###"
    rm -rf $dnnffdir
    $cuda_cmd $dnnffdir/_train_nnet.log steps/train_nnet_basic.sh --config conf/full-nn-splice5.conf \
        $lbldir/train $lbldir/dev $acdir/train $acdir/dev $dnnffdir

    incr_stage
fi

#######################################
#####   Step 5: Creating voice    #####
#######################################

if [ $stage -le 5 ]; then
    echo "##### Step 5: preparing voice files #####"


    if [ "$srate" = "16000" ]; then
        order=39
        alpha=0.42
        fftlen=1024
        bndap_order=21
    elif [ "$srate" = "48000" ]; then
        order=60
        alpha=0.55
        fftlen=4096
        bndap_order=25
    fi

    # Variant with mlpg: requires mean / variance from coefficients
    copy-feats scp:$datadir/train/feats.scp ark:- \
        | add-deltas --delta-order=2 ark:- ark:- \
        | compute-cmvn-stats --binary=false ark:- - \
        | awk '
    (NR==2){count=$NF; for (i=1; i < NF; i++) mean[i] = $i / count}
    (NR==3){if ($NF == "]") NF -= 1; for (i=1; i < NF; i++) var[i] = $i / count - mean[i] * mean[i]; nv = NF-1}
    END{for (i = 1; i <= nv; i++) print mean[i], var[i]}' \
        > $datadir/train/var_cmp.txt

    # Variant with mlpg: requires mean / variance from coefficients
    copy-feats scp:$datadir/train/pitch_feats.scp ark:- \
        | add-deltas --delta-order=2 ark:- ark:- \
        | compute-cmvn-stats --binary=false ark:- - \
        | awk '
    (NR==2){count=$NF; for (i=1; i < NF; i++) mean[i] = $i / count}
    (NR==3){if ($NF == "]") NF -= 1; for (i=1; i < NF; i++) var[i] = $i / count - mean[i] * mean[i]; nv = NF-1}
    END{for (i = 1; i <= nv; i++) print mean[i], var[i]}' \
        > $datadir/train/var_pitch.txt

    cd $HERE
    local/make_dnn_voice_pitch.sh --spk $spks --lng $lng --acc $acc \
         --srate $srate --mcep_order $order --bndap_order $bndap_order --alpha $alpha --fftlen $fftlen \
         --cex_freq $datadir/full/cex.ark.freq \
         --var_cmp $datadir/train/var_cmp.txt \
         --var_pitch $datadir/train/var_pitch.txt \
         --durdnndir $dnndurdir \
         --f0dnndir $dnnf0dir \
         --acsdnndir $dnndir \
         --outputdir $voicedir

    echo "Voice packaged successfully. Portable models have been stored in '$voicedir'."

    incr_stage
fi


#######################################
#####   Step 6: Synthesizing      #####
#######################################

if [ $stage -le 6 ]; then
    echo "##### Step 6: synthesizing test data #####"

    cd $HERE

    for f in $testdatadir/*.xml ; do
        if [ -e "$f" ]; then
            echo "Synthesizing $f"
            local/synthesis_voice_pitch.sh --input_text $f $voicedir $testoutdir
        else
            echo "Warning : no test data in $testdatadir to synthesize"
        fi
    done

    incr_stage
fi


case $lng in
    en)
        sampletxt='This is a demo of D N N synthesis'
        ;;
    ru)
        sampletxt='Кирпич ни с того ни с сего никому и никогда на голову не свалится.'
        ;;
    ga)
        sampletxt='Níl aon tinteán mar do thinteán féin'
        ;;
    ro)
        sampletxt="Ziua bună de dimineaţă se vede."
        ;;
    *)
        for f in $testdatadir/*.xml ; do
            if [ -e "$f" ]; then
                sampletxt=$(grep -v "<?xml" $f | grep -v "<.*>" | head -n1)
            else
                sampletxt='This is a demo of D N N synthesis'
            fi
            break
        done
        ;;
esac

echo "

*********************
** Congratulations **
*********************

The Tangle TTS DNN has been trained.

Example audio can be found in $testoutdir

Portable voice models have been stored in
    $voicedir

Synthesis can be performed using:
    echo \"$sampletxt\" | local/synthesis_voice_pitch.sh $voicedir <out_dir>

"
