#!/usr/bin/env python3

import argparse
from lxml import etree
import os
import sys
import re
import collections


def check_lexicon(lexicon, phoneset, sylmax):
    valid = True

    lex_dict = collections.defaultdict(list)
    phones = parse_phoneset(phoneset)
    nuclei = get_nuclei(sylmax)
    pc = PronCheck(phones, nuclei)

    for event, lex in etree.iterparse(lexicon, events=("end",), tag='lex'):
        grapheme = lex.text.strip()
        if not len(grapheme):
            errprint("ERROR: grapheme is empty")
            valid = False
            continue
        if len(grapheme.split()) > 1:
            # TODO check using tokenisation rules instead
            errprint(f"ERROR: '{grapheme}': graphemes cannot contain more than one token")
            valid = False
            continue

        pron = lex.attrib.get('pron')
        if not pron:
            errprint(f"ERROR: '{grapheme}': requires pronuncation")
            valid = False
            continue
        if not pc.check_pron(pron):
            errprint(f"ERROR: '{grapheme}': pronuncation is invalid")
            valid = False
            continue

        entry = lex.attrib.get('entry', '').strip()
        if not entry:
            errprint(f"ERROR: '{grapheme}': requires entry")
            valid = False
            continue

        default = lex.attrib.get('default', '').strip()
        if not default:
            errprint(f"ERROR: '{grapheme}': requires default")
            valid = False
            continue

        if default.lower() not in ['true', 'false']:
            errprint(f"ERROR: '{grapheme}': default must be 'true' or 'false' not '{default}'")
            valid = False
            continue
        default = (default.lower() == 'true')

        for prev in lex_dict[grapheme]:
            p, e, d = prev
            if p == pron and e == entry:
                errprint(f"ERROR: '{grapheme}' : '{entry}' : duplicate entry")
                valid = False

        lex_dict[grapheme].append((pron, entry, default))


    for grapheme, (lex) in lex_dict.items():
        if len(lex) > 1 and sum(map(lambda l: l[2], lex)) > 1:
            errprint(f"ERROR: '{grapheme}' : has multiple default entries")
            valid = False
        if not any(map(lambda l: l[2], lex)):
            errprint(f"ERROR: '{grapheme}' : has no default entry")
            valid = False

    return valid



class PronCheck:
    def __init__(self, phoneset, nuclei):
        self.phoneset = phoneset
        self.nuclei = nuclei

        self._regex_phone = re.compile("(?P<phoneme>" + '|'.join(phoneset) + ")(?P<stress>\d*)$")

    def check_pron(self, pron):
        """ check the pronuncation is valid """
        pron = pron.split()
        for p in pron:
            m = self._regex_phone.match(p)
            if m is None:
                errprint(f"ERROR: '{p}' is not a valid phone")
                return False
            if m.group('stress'):
                if not m.group('phoneme') in self.nuclei:
                    errprint(f"ERROR: '{p}' should not have stress")
                    return False
            elif m.group('phoneme') in self.nuclei:
                errprint(f"ERROR: '{p}' missing stress")
                return False

        return True


def parse_phoneset(phoneset):
    """ assumes the phoneset is valid """
    phones = []
    try:
        for event, ph in etree.iterparse(phoneset, events=("end",), tag='phone'):
            if ph.attrib['name'] != '_' and ph.attrib['name'] == ph.attrib['name'].lower():
                phones.append(ph.attrib['name'].strip())
    except Exception as e:
        errprint("CRITICAL: cannot parse phoneset file")
        raise (e)
    if not phones:
        errprint("CRITICAL: cannot find any phonemes")
        raise IOError("no phones")
    return phones


def get_nuclei(sylmax):
    """ assumes the sylmax is valid """
    nuclei = []
    try:
        sylmaxxml = etree.parse(sylmax)
        for nuc in sylmaxxml.xpath('//nuclei/n'):
            nuclei.append(nuc.attrib['pat'].strip())
    except Exception as e:
        errprint("CRITICAL: cannot parse sylmax file")
        raise (e)
    if not nuclei:
        errprint("CRITICAL: cannot find any nuclei")
        raise IOError("no nuclei")
    return nuclei


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--phoneset", required = True, type=argparse.FileType('rb'),
                        help = "accent specific phoneset file")
    parser.add_argument("-s", "--sylmax", required = True, type=argparse.FileType('rb'),
                        help = "accent specific syllabic specification file")
    parser.add_argument("-l", "--lexicon", type=argparse.FileType('rb'),
                        help = "lexicon file")
    args = parser.parse_args()


    if check_lexicon(args.lexicon, args.phoneset, args.sylmax):
        exit()
    else:
        errprint("lexicon contains errors")
        exit(1)


def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    main()