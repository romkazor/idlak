#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett
#                                       David Braude )
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.


import os
import sys

# load pyidlak python library
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
from pyIdlak import txp

USAGE = """
Normalise and save xml input text to .wav file
Usage: ./pyidlaktts.py [options] xml_input wav_output\n"
     e.g.: ./pyidlaktts.py --tpdb=../../idlak-data --general-lang=en --general-acc=ga ../../src/idlaktxp/test_data/mod-test001.xml output.wav
     e.g.: cat  ../../src/idlaktxp/test_data/mod-test001.xml | ./pyidlaktts.py --tpdb=../../idlak-data --general-lang=en --general-acc=ga - - > output.wav
"""


def main():

    # Create an Idlak option parser & parse the command line
    args = txp.TxpArgumentParser(usage = USAGE)

    args.parse_args()

    # Check that the input and output have been specified
    if args.no_args != 2:
        sys.stderr.write("Script requires extactly 2 arguments\n")
        args.print_usage()
        sys.exit(1)

    filein = args.get_arg(1)
    fileout = args.get_arg(2)
    try:
        wavout = open(fileout, 'w')
        wavout.close()
    except:
        sys.stderr.write("Failed to create output file '{0}'.\n".format(fileout))
        sys.exit(1)

    # Initialise all the modules that will be run
    if args.get('verbose'):
        sys.stderr.write('Loading text processing modules\n')
    modules = []
    modules.append(txp.modules.Tokenise(args))
    modules.append(txp.modules.PosTag(args))
    modules.append(txp.modules.Normalise(args))
    modules.append(txp.modules.Pauses(args))
    modules.append(txp.modules.Phrasing(args))
    modules.append(txp.modules.Pronounce(args))
    modules.append(txp.modules.PostLex(args))
    modules.append(txp.modules.Syllabify(args))
    modules.append(txp.modules.ContextExtraction(args))

    # Create an Idlak XML document
    if filein == '-':
        inputxml = sys.stdin.read()
    else:
        if not os.path.isfile(filein):
            sys.stderr.write("Can't open input XML file '{0}'\n".format(filein))
            sys.exit(1)
        else:
            if args.get('verbose'):
                sys.stderr.write("Loading input xml file: '{0}'\n".format(filein))
            try:
                inputxml = open(filein).read()
            except UnicodeDecodeError:
                inputxml = open(filein, encoding = 'utf8').read()

    doc = txp.XMLDoc(inputxml)

    # Run the txp modules over it in order
    for txp_module in modules:
        if args.get('verbose'):
            sys.stderr.write("Running: {0}\n".format(txp_module.name))
        txp_module.process(doc)


    # Synthesise the output
    if args.get('verbose'):
        sys.stderr.write("Synthesising audio\n")


    # Output generated .wav
    if args.get('verbose'):
        sys.stderr.write("Saving audio into '{0}'\n".format(fileout))


if __name__ == "__main__":
    main()
