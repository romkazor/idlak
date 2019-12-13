#!/usr/bin/env python3
# -*- encoding utf-8 -*-

import argparse
from lxml import etree
import os
import sys
import re

# TODO: Tones
# TODO: Format

def check_cex(cexxml, possetxml, phonexml):
    good_cex = True
    if not cex_has_allpos(cexxml, possetxml):
        sys.stderr.write('cex does not match posset\n')
        good_cex = False

    if not cex_has_allphones(cexxml, phonexml):
        sys.stderr.write('cex does not match posset\n')
        good_cex = False

    return good_cex 

def cex_has_allpos(cexxml, possetxml):
    """ The CEX file must have all the POS tags in the 'pos' set """
    posset_pos = set()
    for tag in possetxml.xpath('//tag'):
        name = tag.get('name', '')
        name = name.strip("'").strip('"')
        if len(name):
            posset_pos.add(name)

    if len(posset_pos):
        cexpos = cexxml.xpath('//set[@name="pos"]')
        if not cexpos:
            sys.stderr.write('cex does not have a set for pos\n')
            return False
        cex_pos = set()
        for item in cexpos[0].xpath('item'):
            cex_pos.add(item.get('name'))

    missing_pos = list(posset_pos - cex_pos)
    missing_pos.sort()
    if missing_pos:
        sys.stderr.write('POS tags are missing in CEX:\n\t'  + '\n\t'.join(missing_pos) + '\n')

    extra_pos = list(cex_pos - posset_pos)
    extra_pos.sort()
    if extra_pos:
        sys.stderr.write('Extra POS tags in CEX:\n\t'  + '\n\t'.join(extra_pos) + '\n')

    if missing_pos or extra_pos:
        return False

    return True

def cex_has_allphones(cexxml, phonexml):

    cex_phones = []
    has_pau = False
    has_sil = False
    has_X = False
    no_bad_names = True
    for phone in cexxml.xpath('//set[@name="phone"]/item'):
        name = phone.get('name')
        if name is None:
            sys.stderr.write('Phone is missing name\n')
            no_bad_names = False
            continue
        if name == 'pau':
            has_pau = True
        elif name == 'sil':
            has_sil = True
        elif name == 'X':
            has_X = True
        elif not name:
            sys.stderr.write('Phone name is blank\n')
            no_bad_names = False
        elif name != name.strip():
            sys.stderr.write('Phone name has spaces\n')
            no_bad_names = False
        else:
            cex_phones.append(name)
    if not has_pau: sys.stderr.write('Missing required phone "pau"\n')
    if not has_sil: sys.stderr.write('Missing required phone "sil"\n')
    if not has_X: sys.stderr.write('Missing required phone "X"\n')

    no_duplicate_phones = True
    if len(cex_phones) != len(set(cex_phones)):
        sys.stderr.write('Missing required phone "X"\n')
        duplicate_phones = False

    cex_phones = set(cex_phones)

    phoneset = set()
    for phone in phonexml.xpath('//phone'):
        name = phone.get('name')
        if name != '_':
            phoneset.add(name)

    missing_phones = list(phoneset - cex_phones)
    missing_phones.sort()
    if missing_phones:
        sys.stderr.write('Phones are missing in CEX:\n\t'  + '\n\t'.join(missing_phones) + '\n')

    extra_phones = list(cex_phones - phoneset)
    extra_phones.sort()
    if extra_phones:
        sys.stderr.write('Extra phones in CEX:\n\t'  + '\n\t'.join(extra_phones) + '\n')
   
    if missing_phones or extra_phones or not all([no_bad_names, has_pau, has_sil, has_X]):
        return False
   
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cex', required = True, type = argparse.FileType('rb'),
                        help = 'cex xml to check')
    parser.add_argument('-p', '--phoneset', type = argparse.FileType('rb'),
                        help = 'phoneset to check against')
    parser.add_argument('-P', '--posset', required = True, type = argparse.FileType('rb'),
                        help = 'posset to check against')

    args = parser.parse_args()

    cexxml = etree.parse(args.cex)
    possetxml = etree.parse(args.posset)
    phonexml = etree.parse(args.phoneset)

    if not check_cex(cexxml, possetxml, phonexml):
        sys.stderr.write('errors in cex file\n')
        exit(1)
    exit(0)





if __name__ == "__main__":
    main()
