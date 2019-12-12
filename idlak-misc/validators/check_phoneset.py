#!/usr/bin/env python3
# -*- encoding utf-8 -*-

import argparse
from lxml import etree
import os
import sys
import re
import unicodedata



def check_phoneset(phonsetxml):
    good_phoneset = True
    if not phonsetxml.xpath('//phone'):
        eprint("phoneset does not have phones lookup is missing")
        return False

    for phone in phonsetxml.xpath('//phone'):
        name = phone.get('name')
        if not check_name(phone.get('name')):
            good_phoneset = False
            continue
        dec_nodes = phone.xpath('./description')
        if not dec_nodes:
            eprint(f"phone name '{name}' had no discription node")
            good_phoneset = False
        elif len(dec_nodes) != 1:
            eprint(f"phone name '{name}' had multiple discription node")
            good_phoneset = False
        elif not check_discription(dec_nodes[0]):
            good_phoneset = False

    if good_phoneset:
        if not check_unique_phone(phonsetxml):
            good_phoneset = False
        if not check_unique_ipa(phonsetxml):
            good_phoneset = False


    return good_phoneset 


def check_name(name):
    if name is None:
        eprint("phone is missing name")
        return False 
    if not name:
        eprint("phone name is blank")
        return False
    if len(name) != len(name.strip()):
        eprint(f"phone name '{name}' has blank spaces")
        return False
    if len(name) > 3:
        eprint(f"phone name '{name}' is longer than 3 characters")
        return False
    pat = re.compile('[^a-zA-Z@]+')
    if name != '_' and pat.match(name):
        chars = ','.join(set(pat.match(name).group(0)))
        eprint(f"phone name '{name}' contains illegal characters {chars}")
        return False
    if name.upper() != name  and name.lower() != name:
        eprint(f"phone name '{name}' must either be entirely lower or upper case (uppercase for archiphones)")
        return False
    return True


def check_discription(dnode):
    name = dnode.getparent().get('name')
    word_example = dnode.get('word_example')
    pron_example = dnode.get('pron_example')
    ipa = dnode.get('ipa')
    
    good_desc = True
    if word_example is None:
        eprint(f"'{name}' is missing a word_example")
        good_desc = False
    if pron_example is None:
        eprint(f"'{name}' is missing a pron_example")
        good_desc = False
    if ipa is None:
        eprint(f"'{name}' is missing an ipa symbol")
        good_desc = False

    if re.match('[a-z@]+', name):
        pron_example = [p for p in re.sub('\d', '', pron_example).replace('_', ' ').split() if p]
        if name not in pron_example:
            eprint(f"'{name}' is not in the pronunciation example")
            good_desc = False
    elif name == '_':
        if word_example or pron_example or ipa:
            eprint(f"'{name}' should have blank word_example, pron_example and ipa")
            good_desc = False

    dec_ipa = unicodedata.normalize('NFD', ipa)
    if ipa != dec_ipa:
        eprint(f'"{name}" ipa symbol is not fully decomposed should be "{dec_ipa}"')
        good_desc = False

    return good_desc

def check_unique_phone(phonsetxml):
    good_phoneset = True

    names = [phone.get('name') for phone in phonsetxml.xpath('//phone')]
    dup_names = []
    for n in names:
        if names.count(n) > 1:
            dup_names.append(n)
    if dup_names:
        eprint(f'the following phones are not unique {", ".join(set(dup_names))}')
        good_phoneset = False

    return good_phoneset

def check_unique_ipa(phonsetxml):
    good_phoneset = True

    names = []
    ipas = []
    for phone in phonsetxml.xpath('//phone'):
        name = phone.get('name')
        ipa = phone.find('description').get('ipa')
        if name != '_' and name != name.upper():
            names.append(name)
            ipas.append(ipa)
    dup_ipas = []
    for n, i in zip(names, ipas):
        if ipas.count(i) > 1:
            eprint(f'{n} has non-unique ipa symbol {i}')
            good_phoneset = False

    return good_phoneset

def eprint(s = '', end='\n'):
    sys.stderr.write(s + end)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--phoneset', required = True, type = argparse.FileType('rb'),
                        help = 'phoneset xml to check')
    args = parser.parse_args()

    phonesetxml = etree.parse(args.phoneset)
    
    if not check_phoneset(phonesetxml):
        eprint('errors in phoneset file')
        exit(1)
    exit(0)

if __name__ == "__main__":
    main()
