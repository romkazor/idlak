#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018 Cereproc Ltd. (author: David Braude)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.


import os
import copy
import sys
import argparse
import re
from lxml import etree


def extracted_needed_transcriptions(in_file, scp_file, out_file):
    xml = etree.parse(in_file, etree.XMLParser(remove_blank_text=True))

    fileids = []
    for line in scp_file.readlines():
        line = line.strip()
        if not len(line) or line.startswith('#'):
            continue
        fileids.append(line.split()[0])

    spkpat = re.compile('[a-z]{3}')
    speakers = set(s.split('_')[0] for s in fileids)
    speakers = [s for s in speakers if spkpat.match(s)]

    outxml = etree.Element("recording_script")

    for uttnode in xml.xpath('//fileid'):
        fid = uttnode.get('id')
        if fid in fileids:
            outxml.append(copy.copy(uttnode))
        elif len(fid.split('_')) == 2:
            for spk in speakers:
                fullid = spk + '_' + fid
                if fullid in fileids:
                    node = copy.copy(uttnode)
                    node.set('id', fullid)
                    outxml.append(node)

    out_file.write(etree.tostring(outxml,
                   xml_declaration=True,
                   encoding='utf-8',
                   pretty_print = True))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required = True,
                         help = 'Input transcription (normally called text.xml)')

    parser.add_argument('-s', '--scp', required = True, type = argparse.FileType('r'),
                         help = 'SCP file to exctract from')

    parser.add_argument('-o', '--output', required = True,
                         help = 'Output transcription (normally called text.xml)')

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        parser.error("cannot find input file: '{0}'".format(args.input))

    inputfile = open(args.input, 'rb')
    outputfile = open(args.output, 'wb')

    extracted_needed_transcriptions(args.input, args.scp, outputfile)


if __name__ == "__main__":
    main()
