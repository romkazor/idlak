#!/usr/bin/env python3

import argparse
from lxml import etree
import unicodedata as ud 


parser = argparse.ArgumentParser()
parser.add_argument('phoneset', type = argparse.FileType('rb'))
args = parser.parse_args()

phonset_xml = etree.parse(args.phoneset)
for phone in phonset_xml.xpath('//phone'):
    name = phone.get('name')
    if name == '_':
        continue
    desc = phone.find('description')
    ipa = ud.normalize('NFD', desc.get('ipa'))
    ipa_num = ''.join([f'{ord(c):04X}' for c in ipa])
    print(f"{name}\t{ipa}\t{ipa_num}")