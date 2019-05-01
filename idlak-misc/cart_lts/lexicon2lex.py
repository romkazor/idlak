#!/usr/bin/env python3

import argparse
from lxml import etree

parser = argparse.ArgumentParser()
parser.add_argument("lexicon", type=argparse.FileType('rb'))
parser.add_argument("output", type=argparse.FileType('w', encoding = 'utf-8'))
args = parser.parse_args()

# assumes the lexicon is correctly formatted
for event, lex in etree.iterparse(args.lexicon, events=("end",), tag='lex'):
    grapheme = lex.text.strip()
    pron = lex.attrib.get('pron')
    args.output.write(f"{grapheme} {pron}\n")