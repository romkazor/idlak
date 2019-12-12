#!/bin/bash
# Takes a lexicon a generates letter-to-sound rules

set -euo pipefail

# Usage message
usage="\nUsage: "$0" -p <phoneset> -s <sylmax> -l <lexicon>

  Optional flags and parameters:
    -h: show usage and exits
    -o: output file
        default = ./ccart-default.xml
    -T: path to storage directory
        default = ./tmp

  The following Phonetisaurus arguments can be set as environment variables:
    delim: delimiter between lexicon attributes
      default = \" \"
    s2_char_delim: delimiter between phones
      default = \"_\"\n"

# Some default values for parameters
phoneset=
sylmax=
lexicon=
output="$(pwd)/ccart-default.xml"
tmpdir="$(pwd)/tmp"

# Argument handling
while getopts "hp:s:l:o:T:" opt
do
    case $opt in
        p)
            phoneset=$OPTARG
            ;;
        s)
            sylmax=$OPTARG
            ;;
        l)
            lexicon=$OPTARG
            ;;
        o)
            output=$OPTARG
            ;;
        h)
            echo -e "$usage"
            exit 0
            ;;
        T)
            tmpdir="$OPTARG"
            ;;
        \?)
            echo "Invalid option: -"$OPTARG"" >&2
            echo -e "$usage" >&2
            exit 1
            ;;
    esac
done

if [ -z  $lexicon ] ; then
    echo "ERROR: Lexicon must be provided"
    exit 1
fi
if [ -z  $phoneset ] ; then
    echo "ERROR: Phoneset must be provided"
    exit 1
fi
if [ -z  $sylmax ] ; then
    echo "ERROR: Sylmax must be provided"
    exit 1
fi

HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cart2toolspath="$HERE/../../tools"
validatorspath="$HERE/../validators"
phonetisaurus_align="$cart2toolspath/Phonetisaurus/phonetisaurus-align"

# check the lexicon is valid
python3 $validatorspath/check_lexicon.py -l $lexicon -p $phoneset -s $sylmax

bname=$( basename ${lexicon} .xml )
archname=${bname#lexicon-}

# Install phonetisaurus if needed
if [ ! -f $phonetisaurus_align ]; then
    echo "##### installing Phonetisaurus #####"
    cd $cart2toolspath
    git clone https://github.com/AdolfVonKleist/Phonetisaurus.git
    cd Phonetisaurus
    git checkout 64719ca40c17cb70d810fffadac52c97984ca539 . || exit 1
    CXXFLAGS="-I`pwd`/../openfst/include" LDFLAGS="-Wl,-rpath=`pwd`/../openfst/lib/" \
    ./configure --with-openfst-libs=`pwd`/../openfst/lib \
        --with-openfst-includes=`pwd`/../openfst/include  \
        --prefix=`pwd`
    make -j4
    make install
    cd -
fi


mkdir -p $tmpdir
touch $output # checks can create the output

echo "##### converting lexicon #####"
convertedlex=$tmpdir/converted-${archname}.lex
python3 $HERE/lexicon2lex.py $lexicon $convertedlex

echo "##### creating Phonetisaurus alignment file #####"

# Phonetisaurus enviornment variables
: "${delim:=" "}"
: "${s2_char_delim:=_}"

alignment=$tmpdir/converted-${archname}.align

$phonetisaurus_align --input=$convertedlex --ofile=$alignment --delim="$delim" --s2_char_delim="$s2_char_delim"
# Add more Phonetisaurus arguments here if needed
# Run ./phonetisaurus-align -help in idlak/tools/Phonetisaurus for more options

echo "##### generating cart files #####"
python3 $HERE/phonet2cart.py -o $tmpdir $alignment

echo "##### running wagon #####"
wagondir=$tmpdir/cart
for f in $tmpdir/*.cart ; do
    ID=$( basename $f .cart )
    mkdir -p $wagondir/$ID
    wagon -desc $tmpdir/wagon_description.dat -data $f -o $wagondir/$ID/tree.dat
done

echo "##### generating LTS rules #####"

python3 $HERE/carttree2xml.py -d $tmpdir/$( basename $output .xml )_diagnostics.dat $wagondir $output

echo "##### done #####"
