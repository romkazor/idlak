#!/bin/bash
set -euo pipefail
source cmd.sh
source path.sh

# Arctic database usual sampling rate is 16k; although 32k is
# also available for some speakers.
# This recipe uses upsampled 32k data; please adjust to use 16k data instead

srate=48000
FRAMESHIFT=0.005
TMPDIR=/tmp
stage=-1
endstage=7
nj=4 # max 9
# Speaker ID
spks="slt" # can be any of slt, bdl, jmk
network_type=dnn # dnn or lstm
tpdb=$KALDI_ROOT/idlak-data/

nodev=100 # the number of samples used for calculating loss
          # the remaining will be in the training set.
          # 50 utterances in the test set assumes that the number of utterances
          # in the recording script is between 500 and 600

. parse_options.sh || exit 1;

# all Artic voices are in General American English
lng=en
acc=ga

# Check audio and labels have been downloaded and converted to tangle numbering
for spk in $spks; do
    arch=cmu_us_${spk}_arctic-WAVEGG.tar.bz2
    url=http://festvox.org/cmu_arctic/cmu_arctic/orig/$arch
    laburl=http://festvox.org/cmu_arctic/cmuarctic.data
    label_dir=$HERE/labels/$lng/$acc/$spk
    spkrawaudio=$HERE/rawaudio/$lng/$acc/$spk

    #  Audio
    for f in $spkrawaudio/*_orig/*.wav; do
        if [ ! -e "$f" ]; then
            mkdir -p $spkrawaudio
            cd $spkrawaudio
            wget -c -N $url
            tar -xjf $arch
            # get original sample rate
            for i in $spkrawaudio/cmu_us_${spk}_arctic/orig/*.wav; do
                orgsrate=`sox --info -r $i`
                break
            done
            # rename and move data
            mkdir -p $spkrawaudio/${orgsrate}_orig
            for i in $spkrawaudio/cmu_us_${spk}_arctic/orig/*.wav; do
                fid=$(echo $(basename ${i%.*}) | awk -v spk=$spk -F"_" '{print spk"_"substr($2,1,1)"000"substr($2,2,1)+1"_"substr($2,3,3)}')
                cp $i $spkrawaudio/${orgsrate}_orig/${fid}.wav
            done
        fi
        break
    done
    # Script
    if [ ! -e $label_dir/text.xml ]; then
        mkdir -p $label_dir
        cd $label_dir
        wget -c -N $laburl
        fidstr=\"${spk}_\"substr\(\$2,length\(\$2\)-4,1\)\"000\"substr\(\$2,length\(\$2\)-3,1\)+1\"_\"substr\(\$2,length\(\$2\)-2,3\)
        makelab="awk -v spk=$spk '{fid=$fidstr;\$1=\"\";\$2=\"\";\$NF=\"\";print(\"  <fileid id=\\\"\" fid \"\\\">\",substr(\$0,4,length(\$0)-5),\"</fileid>\")}'"
        echo $makelab
        echo "<?xml version='1.0' encoding='utf-8'?>" > $label_dir/text.xml
        echo "<recording_script>" >> $label_dir/text.xml
        cat $label_dir/cmuarctic.data | eval $makelab >> $label_dir/text.xml
        echo "</recording_script>" >> $label_dir/text.xml
    fi
done

trainargs="--lng $lng --acc $acc --spks $spks"
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
