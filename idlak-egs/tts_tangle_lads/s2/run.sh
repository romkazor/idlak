#!/bin/bash
set -euo pipefail
source cmd.sh
source path.sh

# Living Audio Dataset data is hosted at archive.org,
# while the rest of the resources are available from Github
# The url for the audio is from the Github too

srate=48000
FRAMESHIFT=0.005
TMPDIR=/tmp
stage=-1
endstage=7
nj=4 # max 9
lng="ru"
acc="ru"
# Speaker ID
spks="abr" # Must be a speaker from the Idlak Resources
network_type=dnn # dnn or lstm
nodev=50 # the number of samples used for calculating loss
         # the remaining will be in the training set.
         # 50 utterances in the test set assumes that the number of utterances
         # in the recording script is between 500 and 600
runnorm=0
tpdb=$KALDI_ROOT/idlak-data/

. parse_options.sh || exit 1;



# Check audio and labels have been downloaded
for spk in $spks; do
    # URLs of Living Audio Dataset
    arch=$lng.$acc.$spk.$srate.tar.gz
    url=https://github.com/Idlak/Living-Audio-Dataset/raw/master/$lng/$acc/$spk/audiourl
    laburl=https://github.com/Idlak/Living-Audio-Dataset/raw/master/$lng/$acc/$spk/text.xml
    audio_dir=$HERE/rawaudio/$lng/$acc/$spk/${srate}
    label_dir=$HERE/labels/$lng/$acc/$spk

    # Get the audio at the correct sample rate
    if [ ! -e $audio_dir ]; then
        # Download data
        for f in $HERE/rawaudio/$lng/$acc/$spk/*_orig/*.wav; do
            if [ ! -e "$f" ]; then
                mkdir -p $HERE/rawaudio/$lng/$acc/$spk
                cd $HERE/rawaudio/$lng/$acc/$spk
                wget -c -N $(curl -L $url)
                tar -xzf $arch
            fi
            break
        done
    fi

    # Get the transcription
    if [ ! -e $label_dir/text.xml ]; then
        mkdir -p $label_dir
        cd $label_dir
        wget -c -N $laburl
    fi
done

trainargs="--lng $lng --acc $acc --spks $spks"
trainargs="$trainargs --srate $srate"
trainargs="$trainargs --rawaudiodir $HERE/rawaudio"
trainargs="$trainargs --labeldir $HERE/labels"
trainargs="$trainargs --stage $stage"
trainargs="$trainargs --endstage $endstage"
trainargs="$trainargs --tpdb $tpdb"
trainargs="$trainargs --runnorm $runnorm"
trainargs="$trainargs --nodev $nodev"
trainargs="$trainargs --nj $nj"
trainargs="$trainargs --network_type $network_type"
trainargs="$trainargs --FRAMESHIFT $FRAMESHIFT"
trainargs="$trainargs --TMPDIR $TMPDIR"

cd $HERE
./local/tangle_train.sh  $trainargs
