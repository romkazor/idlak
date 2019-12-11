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
            errprint("ERROR: '{}': graphemes cannot contain more than one token".format(grapheme))
            valid = False
            continue

        pron = lex.attrib.get('pron')
        if not pron:
            errprint("ERROR: '{}': requires pronuncation".format(grapheme))
            valid = False
            continue
        if not pc.check_pron(pron):
            errprint("ERROR: '{}': pronuncation is invalid".format(grapheme))
            valid = False
            continue

        entry = lex.attrib.get('entry', '').strip()
        if not entry:
            errprint("ERROR: '{}': requires entry".format(grapheme))
            valid = False
            continue

        default = lex.attrib.get('default', '').strip()
        if not default:
            errprint("ERROR: '{}': requires default".format(grapheme))
            valid = False
            continue

        if default.lower() not in ['true', 'false']:
            errprint("ERROR: '{}': default must be 'true' or 'false' not '{}'".format(grapheme, default))
            valid = False
            continue
        default = (default.lower() == 'true')

        for prev in lex_dict[grapheme]:
            p, e, d = prev
            if p == pron and e == entry:
                errprint("ERROR: '{}' : '{}' : duplicate entry".format(grapheme, entry))
                valid = False

        lex_dict[grapheme].append((pron, entry, default))


    for grapheme, (lex) in lex_dict.items():
        if len(lex) > 1 and sum(map(lambda l: l[2], lex)) > 1:
            errprint("ERROR: '{}' : has multiple default entries".format(grapheme))
            valid = False
        if not any(map(lambda l: l[2], lex)):
            errprint("ERROR: '{}' : has no default entry".format(grapheme))
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
                errprint("ERROR: '{}' is not a valid phone".format(p))
                return False
            if m.group('stress'):
                if not m.group('phoneme') in self.nuclei:
                    errprint("ERROR: '{}' should not have stress".format(p))
                    return False
            elif m.group('phoneme') in self.nuclei:
                errprint("ERROR: '{}' missing stress".format(p))
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
