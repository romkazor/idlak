#!/usr/bin/env python3

import argparse
from lxml import etree
import unicodedata
import re

parser = argparse.ArgumentParser('decomposes graphemes into NFD form')
parser.add_argument('lexicon', type=argparse.FileType('rb'))
parser.add_argument('lex_out', type=argparse.FileType('wb'))
args = parser.parse_args()

lexicon_xml = etree.parse(args.lexicon)


for lex in lexicon_xml.xpath('lex'):
    lex.text = unicodedata.normalize('NFD', lex.text)

try:
    args.lex_out.write(
        etree.tostring(lexicon_xml, encoding='utf8', pretty_print=True, xml_declaration=True)
    )
    args.lex_out.write(b'\n')
except TypeError as e:
    if str(e) == 'write() argument must be str, not bytes':
        args.lex_out.write(
        etree.tostring(lexicon_xml, encoding='utf8', pretty_print=True, xml_declaration=True).decode('utf8')
    )
    args.lex_out.write('\n')







