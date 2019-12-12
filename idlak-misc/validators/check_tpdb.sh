#!/usr/bin/env bash

set -euo pipefail

tpdbdir="$( realpath $( pwd )/../../idlak-data)"
lng="*"
acc="*"
spk="*"
arch="*"

function usage {
echo -e "\nUsage: "$0"

  Optional flags and parameters
    -t: override tpdb dir ($tpdbdir)
    -l: language '*' for all ($lng)
    -a: accent, '*' for all ($acc)
    -s: speaker, '*' for all ($spk)
    -A: architecture, '*' for all ($arch)
    -h: show this message and exit
\n" >&2
    exit $1
}

help=
while getopts "ht:l:a:s:A:" opt
do
    case $opt in
        t)
            tpdbdir=$OPTARG
            ;;
        l)
            lng=$OPTARG
            ;;
        a)
            acc=$OPTARG
            ;;
        s)
            spk=$OPTARG
            ;;
        A)
            arch=$OPTARG
            ;;
        h)
            usage 0
            ;;
        \?)
            echo "Invalid option: -"$OPTARG"" >&2
            usage 1
            ;;
    esac
done


function filelist {
    local counter=0
    fnames=()
    local root=$1
    for fn in $tpdbdir/$lng/$acc/$spk/${root}-${arch}.xml $tpdbdir/$lng/$acc/${root}-${arch}.xml $tpdbdir/$lng/${root}-${arch}.xml $tpdbdir/${root}-${arch}.xml ; do 
        if [ -f $fn ] ; then
            let counter+=1
            f=$( realpath --relative-to=$tpdbdir $fn )
            fnames+=("$f")
        fi
    done
}

function file_applys {
    local rootfile=$1
    local targetfile=$2
    local rdir=$( dirname $rootfile )
    local tdir=$( dirname $targetfile )
    local rpath=$( realpath --relative-to=$tpdbdir/$tdir $tpdbdir/$rdir  )
    local res=$( echo $rpath | sed s'/\.\.\///' | sed s'/^\.//' | sed s'/^\.//' )
    if [ -z "$res" ] ; then 
        apply=1
    else
        apply=
    fi
}


filelist phone ; phonesets=("${fnames[@]}") 
filelist trules ; trules=("${fnames[@]}") 
filelist lexicon ; lexicons=("${fnames[@]}") 
filelist sylmax ; sylmaxs=("${fnames[@]}") 

echo "checking phonesets:"
for pset in ${phonesets[@]} ; do 
    echo "$pset"
    error=
    python3 ./check_phoneset.py -p $tpdbdir/$pset || error=true
    if [ $error ] ; then 
        echo "error in $tpdbdir/$pset"
    fi
done
echo

echo "checking trules:"
for tr in ${trules[@]} ; do 
    echo "$tr"
    error=
    python3 ./check_trules.py -t $tpdbdir/$tr || error=true
    if [ ! $error ] ; then
        for lex in ${lexicons[@]} ; do 
            file_applys $tr $lex
            if [ $apply ] ; then
                error=
                python3 ./check_trules.py -t $tpdbdir/$tr -l $tpdbdir/$lex || error=true
                if [ $error ] ; then 
                    echo "error in $tpdbdir/$tr"
                fi
            fi
        done
    fi
done
echo

echo "checking lexicons:"
for lex in ${lexicons[@]} ; do 
    echo "$lex"
    for pset in ${phonesets[@]} ; do 
        for sm in ${sylmaxs[@]} ; do 
            file_applys $lex $pset  ; use_pset=$apply
            file_applys $sm $lex  ; use_sm_lex=$apply
            file_applys $pset $sm ; use_sm_pset=$apply
            if [ $use_pset ] && [ $use_sm_pset ] && [ $use_sm_lex ] ; then
                error=
                python3 ./check_lexicon.py -l $tpdbdir/$lex -p $tpdbdir/$pset -s $tpdbdir/$sm || error=true
                if [ $error ] ; then 
                    echo "error in $tpdbdir/$lex"
                fi
            fi
        done
    done;
done


echo


