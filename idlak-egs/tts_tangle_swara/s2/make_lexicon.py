#!/usr/bin/env python3

# Script for generating a lexicon from the speakers corpus

import argparse
import collections
import glob
from lxml import etree
import os
import re
import sys
import unicodedata

# load the utterances and their text
def utterances(speaker_dir):
    labdir = os.path.join(speaker_dir, 'hts_labels')
    for txtfn in glob.iglob(speaker_dir + '/txt/*.txt'):
        speaker = os.path.basename(txtfn).split('_')[0]
        group = os.path.basename(txtfn).split('_')[1]
        with open(txtfn, encoding='utf8') as txt:
            for line in txt:
                number, utterance_text = line.split(None,1)
                utterance_name = f"{speaker}_{group}_{number.strip().strip('.')}"
                labelfn = os.path.join(labdir, group, utterance_name + '.lab')
                if not os.path.isfile(labelfn):
                    sys.stderr.write(f"WARN: cannot find label file for {utterance_name}\n")
                    continue
                utt = {
                    'name' : utterance_name,
                    'text' : utterance_text.strip(),
                    'labelfn' : labelfn
                }
                yield(utt)
    return

# loads a word indexed file
def load_pronunciations(utt):
    utt['pron'] = {}
    word_to_idx = {}
    phones_pat = re.compile("^(?P<p1>.*?)~(?P<p2>.*?)-(?P<p3>.*?)\+(?P<p4>.*?)=(?P<p5>[^:]*)")
    with open(utt['labelfn'], encoding='utf8') as lab:
        for phonelab in lab:
            phonelab = phonelab.strip()
            _, _, label = phonelab.split(None, 3)
            label = label.split('/')
            label = dict(zip(['P']+label[1::2], label[0::2]))
            phone_mobj = phones_pat.match(label['P'])
            phone = phone_mobj.group('p3')
            vowel = label['B'].split('|')[-1]
            if phone == vowel:
                phone += label['B'][0]
            word_in_phrase = label['E'].split('+',1)[1].split(':',1)[1].split('+')[0]
            phrase_in_utterance = label['H'].split('=',1)[1].split(':')[1].split('=')[0]
            try:
                word_in_phrase = int(word_in_phrase)
                phrase_in_utterance = int(phrase_in_utterance)
            except:
                continue
            wid = (word_in_phrase, phrase_in_utterance)
            widx = len(word_to_idx)
            if wid not in word_to_idx:
                word_to_idx[wid] = widx
            word = word_to_idx[wid]
            if word not in utt['pron']:
                utt['pron'][word] = ''
            else:
                utt['pron'][word] += ' '
            utt['pron'][word] += phone
    return


def align_words_to_pron(utt):
    txt = re.sub(r'[()\[\]{}"\'!?.,;:|]', '', utt['text'])
    words = txt.split()
    if len(words) != len(utt['pron']):
        return False
    utt['lex'] = {}
    for widx, pron in utt['pron'].items():
        utt['lex'][words[widx].lower()] = pron
    return True


def fix_entry(word, pron):
        
    # put 0 on missing stress characters
    def _fix_missing_stress(pron):
        stress_characters = ['@', 'a', 'a@', 'e', 'i', 'o', 'u']
        phones = pron.split()
        pron = []
        for p in phones:
            if p in stress_characters:
                p += '0'
            pron.append(p)
        pron = ' '.join(pron)
        return pron

    if '-' in word:
        return None, None

    word = unicodedata.normalize('NFD', word) # make sure words are fully decomposed
    pron = _fix_missing_stress(pron)

    stress_count = pron.count('1')
    unstress_count = pron.count('0')
    if stress_count == 1:
        return word, pron
    if unstress_count == 1:
        # switched the only unstressed with a stressed vowel
        pron = pron.replace('0','1')
        return  word, pron

    # cant fix the stress
    return None, None


def make_lexicon_xml(lexicon):
    lexicon_xml = etree.Element('lexicon')
    for grapheme in sorted(lexicon.keys()):
        for pron_idx, pron in enumerate(lexicon[grapheme]):
            lex = etree.SubElement(lexicon_xml, 'lex')
            lex.set('pron', pron)
            lex.set('entry', 'full' if (pron_idx == 0) else f"variant_{pron_idx}")
            lex.set('default', 'true' if (pron_idx == 0) else 'false')
            lex.text = grapheme
    return lexicon_xml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action = "count", default = 0)
    parser.add_argument("speaker_dir", help = "base directory of the speaker in the corpus")
    parser.add_argument("output", type = argparse.FileType('wb'), help = "output lexicon")
    args = parser.parse_args()

    lexicon = collections.defaultdict(set)
    
    for utt in utterances(args.speaker_dir):
        if args.verbose:
            print(f"INFO loading: {utt['name']}")
        load_pronunciations(utt)
        if not align_words_to_pron(utt):
            print(f"WARN could not align words to pronunciations for: {utt['name']}")
            continue
        if args.verbose:
            print(f"INFO adding {len(utt['lex'])} words to lexicon")
        for w, p in utt['lex'].items():
            word, pron = fix_entry(w, p)
            if pron is not None:
                lexicon[word].add(pron)

    lexicon_xml = make_lexicon_xml(lexicon)
    args.output.write(
        etree.tostring(lexicon_xml, encoding='utf8', pretty_print=True, xml_declaration=True)
    )
    args.output.write(b'\n')
    



if __name__ == "__main__":
    main()