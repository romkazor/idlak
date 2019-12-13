#!/usr/bin/env python3
# -*- encoding utf-8 -*-

import argparse
from lxml import etree
import os
import sys
import re
import unicodedata





def check_trules(trulesxml, lexiconxml):
    good_trules = True
    if not trules_convertillegal(trulesxml, lexiconxml):
        good_trules = False
    return good_trules 


def trules_convertillegal(trulesxml, lexiconxml):
    """ convertillegal """
    convertillegal = trulesxml.find('//lookup[@name="convertillegal"]')
    if convertillegal is None:
        eprint("convertillegal lookup is missing")
        return False
    exp = convertillegal.find("./exp")
    if convertillegal is None:
        eprint("convertillegal lookup is missing 'exp' child")
        return False
    table = to_dictionary(exp.text)
    
    if table is None:
        eprint("convertillegal lookup cannot be converted to a dictionary\n")
        return False
    bad_table = False
    
    suggested_table = {}
    for bad, good in table.items():
        if good == bad:
            eprint(f"convertillegal: {entry_str(bad, good)} good and bad value are the same")
            bad_table = True
            continue

        bad_entry = False
        if good != unicodedata.normalize('NFD', good):
            if bad == unicodedata.normalize('NFC', good):
                eprint(
                    f'convertillegal: unicode: {entry_str(bad, good)}'
                    f' maps decomposed to composed, should be {entry_str(good, bad)}'
                )
                suggested_table[good] = unicodedata.normalize('NFD', bad)
            else:
                eprint(f"convertillegal: {entry_str(bad, good)} good value is not fully decomposed")
                suggested_table[bad] = unicodedata.normalize('NFD', good)
            bad_table = True
            bad_entry = True
        
        if good in table.keys():
            eprint(f"convertillegal: {entry_str(bad, good)} good value is marked as a bad value in"
                   f" {entry_str(good, table[good])}, one must be deleted (suggested table keeps)"
                   f" {entry_str(bad, unicodedata.normalize('NFD', good))}")
            bad_table = True
            bad_entry = True

        if bad == unicodedata.normalize('NFC', good) and good == unicodedata.normalize('NFD', good):
            com = unicodedata.normalize('NFC', good.upper())
            dec = unicodedata.normalize('NFD', good.upper())
            if com not in table:
                eprint(f"convertillegal: {entry_str(com, dec)} uppercase decomposition missing")
                suggested_table[com] = unicodedata.normalize('NFD', dec)
                bad_table = True 
            com = unicodedata.normalize('NFC', good.lower())
            dec = unicodedata.normalize('NFD', good.lower())
            if com not in table:
                eprint(f"convertillegal: {entry_str(com, dec)} lowercase decomposition missing")
                suggested_table[com] = unicodedata.normalize('NFD', dec)
                bad_table = True 
            


        if not bad_entry:
            suggested_table[bad] = unicodedata.normalize('NFD', good) 

    if lexiconxml is not None:
        # checks that all unicode characters in the lexicon have decomposed to composed entries
        charset = set()
        for lex in lexiconxml.xpath('//lex'):
            charset.update( lex.text.strip() )
        charset = ''.join(list(charset))
        charset = set(charset.lower() + charset.upper())
        for c in charset:
            com = unicodedata.normalize('NFC', c)
            dec = unicodedata.normalize('NFD', c)
            if com != dec:
                if (com not in table) and (table.get(dec) != com):
                    eprint(
                        f'convertillegal: unicode: decomposed form does not map to composed form'
                        f' should have {entry_str(com, dec)}'
                    )
                    bad_table = True
                    suggested_table[com] = dec

    if bad_table:
        eprint('suggested convertillegal table:')
        eprint(dist_to_str(suggested_table))
        return False

    return True

def eprint(s = '', end='\n'):
    sys.stderr.write(s + end)


def entry_str(key, val):
    q = "'" if ("\"" in key or  "\"" in val) else "\""
    return f'{q}{key}{q}:{q}{val}{q}'


def dist_to_str(dictionary):
    entries = []
    for key, val in dictionary.items():
        entries.append(entry_str(key, val))
    entries.sort(key=lambda k: unicodedata.normalize('NFD', k[1:]))
    return '{' + ', '.join(entries) + '}'


def to_dictionary(dictstr):
    dstr = dictstr.strip()
    if not dstr:
        eprint("dictionary text is empty")
        return None
    if not dstr.startswith('{'):
        eprint("dictionary text does not start with '{'")
        return None
    if not dstr.endswith('}'):
        eprint("dictionary text does not end with '}'")
        return None
  
    entries = dstr[1:-1].split(',')
    
    dout = {}
    for idx, entry in enumerate(entries):
        entry = entry.strip()
        key_start = entry[0]
        key = ''
        if key_start not in ['"', "'"]: 
            eprint(f"key for entry {idx} does not start with a quote mark")
            return None
        for e in entry[1:]:
            if e == key_start:
                break
            key += e
        if key in dout:
            eprint(f"entry {idx} has duplicate key: {key}")
            return None
        val = entry[len(key)+2:].strip()
        if val[0] != ':':
            eprint(f"entry {idx} key: {key} does not have : after key")
            return None
        val = val[1:].strip()
        if val[0] not in ['"', "'"]: 
            eprint(f"value for entry {idx} key: {key} does not start with a quote mark")
            return None
        if val[0] != val[-1]: 
            eprint(f"value for entry {idx} key: {key} does not start end with matching"
                    " quote mark to start")
            return None
        val = val[1:-1]
        dout[key] = val
    return dout

        



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--trules', required = True, type = argparse.FileType('rb'),
                        help = 'tokensier rules xml to check')
    parser.add_argument("-l", "--lexicon", type=argparse.FileType('rb'),
                        help = "lexicon file")
    args = parser.parse_args()

    trulesxml = etree.parse(args.trules)
    lexiconxml = etree.parse(args.lexicon) if args.lexicon else None

    if not check_trules(trulesxml, lexiconxml):
        eprint('errors in trules file file')
        exit(1)
    exit(0)





if __name__ == "__main__":
    main()
