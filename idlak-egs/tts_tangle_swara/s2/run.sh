#!/bin/bash
set -euo pipefail
source cmd.sh
source path.sh

# Script for the SWARA Corpus

srate=48000
FRAMESHIFT=0.005
TMPDIR=/tmp
stage=-1
endstage=7
nj=4 # max 9
lng="ro"
acc="ro"
# Speaker ID
spks="bas" # Must be a speaker from SWARA list
            # currently: bas, cau, dcs, dmm, eme, dfs, htm, ips,
            # pcs, pmm, pss, rms, sam, sds, sgs, tim, tss
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
    spk_upper=${spk^^}
    url=https://speech.utcluj.ro/swarasc/data/${spk_upper}.zip
    corpusdir=$HERE/corpus/$lng/$acc/$spk
    spkrawaudio=$HERE/rawaudio/$lng/$acc/$spk
    label_dir=$HERE/labels/$lng/$acc/$spk
    arch=$corpusdir/${spk_upper}.zip

    # Download the corpus
    if [ ! -d "$corpusdir/$spk_upper" ] ; then 
        mkdir -p $corpusdir
        cd $corpusdir
        wget -c -N $url
        unzip -n $arch
    fi 

    # Copy the original audio
    for f in $spkrawaudio/*_orig/*.wav; do
        if [ ! -e "$f" ]; then
            # get original sample rate
            for i in ${corpusdir}/${spk_upper}/wav/*/*.wav; do
                orgsrate=`sox --info -r $i`
                break
            done
            echo "INFO: Detected $orgsrate as original sample rate"

            # rename and copy files (renaming rnd1 rnd2 to z0001 z0002)
            mkdir -p $spkrawaudio/${orgsrate}_orig
            for i in ${corpusdir}/${spk_upper}/wav/*/*.wav; do
                fid=$(echo $(basename ${i%.*}) | sed s"|rnd|z000|" )
                cp $i $spkrawaudio/${orgsrate}_orig/${fid}.wav
            done
        fi
    done

    # Script
    scriptfn=$label_dir/text.xml
    if [ ! -e $scriptfn ]; then
        mkdir -p $label_dir
        cd $label_dir
        echo "<?xml version='1.0' encoding='utf-8'?>" > $scriptfn
        echo "<recording_script>" >> $scriptfn
        for t in ${corpusdir}/${spk_upper}/txt/*.txt ; do 
            g=$(basename ${t%.*} | sed s"|${spk}_||" | sed s"|_corr||" | sed s"|rnd|z000|")
            cat $t | awk -v spk="$spk" -v grp="$g" '{print "  <fileid id=\"" spk "_" grp "_" substr($1,0,length($1)-1) "\">"substr($0,6,length($0))"</fileid>"}' >> $scriptfn
        done
        echo "</recording_script>" >> $scriptfn
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
