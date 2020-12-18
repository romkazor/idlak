#!/bin/bash
set -euo pipefail
source cmd.sh
source path.sh

# This recipe is used for voices with your own data

spk= # speaker codes
lng= # language code
acc= # accent code
audio_dir= # original audio directory
script_file= # original script file, must match LADs format

srate=48000
FRAMESHIFT=0.005
TMPDIR=/tmp
stage=-1
endstage=7
nj=4 
network_type=dnn # dnn or lstm
tpdb=$KALDI_ROOT/idlak-data/

nodev=100 # the number of samples used for calculating loss
          # the remaining will be in the training set.
          # 50 utterances in the test set assumes that the number of utterances
          # in the recording script is between 500 and 600

. parse_options.sh || exit 1;

# Copy Audio
for f in $HERE/rawaudio/$lng/$acc/$spk/*_orig/*.wav; do
    if [ ! -e "$f" ]; then
        echo "INFO: copying audio from ${audio_dir}"
        # assumes the same sample rate is in all files
        # Check audio and labels have been downloaded and converted to tangle numbering
        # Get the audio at the correct sample rate
        if [ ! -e $audio_dir ]; then
            echo "ERROR: Could not find audio directory: '${audio_dir}'"
            exit 1
        fi
        for wavfn in ${audio_dir}/*.wav; do
            if [ ! -e "$wavfn" ]; then
                echo "ERROR: could not find any wavs in ${audio_dir}"
                exit 1
            fi
            srate=`sox --info -r $wavfn`
            break
        done
        spk_audio_dir=$HERE/rawaudio/$lng/$acc/$spk/${srate}_orig
        mkdir -p $spk_audio_dir
        cp ${audio_dir}/*.wav $spk_audio_dir/.
    fi
    break
done

# Copy script
label_dir=$HERE/labels/$lng/$acc/$spk
if [ ! -e $label_dir/text.xml ]; then
    echo "INFO: copying script from ${script_file}"
    if [ ! -e $script_file ]; then
        echo "ERROR: Could not find script file: '${script_file}'"
        exit 1
    fi
    mkdir -p $label_dir
    cp $script_file $label_dir/text.xml
fi

trainargs="--lng $lng --acc $acc --spks $spk"
trainargs="$trainargs --srate $srate"
trainargs="$trainargs --rawaudiodir $HERE/rawaudio"
trainargs="$trainargs --labeldir $HERE/labels"
trainargs="$trainargs --runnorm 0"
trainargs="$trainargs --stage $stage"
trainargs="$trainargs --endstage $endstage"
trainargs="$trainargs --tpdb $tpdb"
trainargs="$trainargs --nodev $nodev"
trainargs="$trainargs --nj $nj"
trainargs="$trainargs --network_type $network_type"
trainargs="$trainargs --FRAMESHIFT $FRAMESHIFT"
trainargs="$trainargs --TMPDIR $TMPDIR"

cd $HERE
./local/tangle_train.sh  $trainargs
