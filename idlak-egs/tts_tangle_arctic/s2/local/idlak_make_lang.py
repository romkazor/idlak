#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, io, xml.sax, re, time, logging
from lxml import etree
from xml.dom.minidom import parse, parseString, getDOMImplementation

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_NAME = os.path.splitext(os.path.split(__file__)[1])[0]
DESCRIPTION = 'Creates kaldi compatible lang directory'
FRAMESHIFT=0.005
IDLAK_SRCDIR = os.path.join(os.path.join(SCRIPT_DIR, *[os.path.pardir]*4), 'src')

# Add to path
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(IDLAK_SRCDIR,'pyIdlak', 'gen'))
# The CEX parser does not require pyIdlak to be built, so it is imported directly
import cex

# sax handler
class idlak_saxhandler(xml.sax.ContentHandler):
    def __init__(self):
        self.id = ''
        self.data = [[]]
        self.ids = []
        self.lex = {}
        self.oov = {}

    def startElement(self, name, attrs):
        if name == "fileid":
            newid = attrs['id']
            if self.id and newid != self.id:
                self.data.append([])
                self.id = newid
                self.ids.append(self.id)
            if not self.id:
                self.id = newid
                self.ids.append(self.id)
        elif name == "tk":
            try:
                at = 'norm'
                if 'norm' not in attrs:
                    at = 'tknorm'
                word = str(attrs[at].upper())
            except:
                print("Failed parsing '{0}': word {1}, 'norm' missing or not utf8, attrs: {2}".format(
                    self.id, attrs.getValue('wordid'), ', '.join(attrs.getNames())))
                raise
            self.data[-1].append(word)
            if not word in self.lex:
                self.lex[word] = {}
            if attrs.get('lts','false') == 'true':
                self.oov[word] = 1
            if 'altprons' in attrs:
                prons = attrs['altprons'].split(', ')
            else:
                prons = [attrs['pron']]
            for p in prons:
                self.lex[word][p] = 1


# Convert CEX XML to DNN Features
def forward_context(input_fname, input_freqtable_fname, cexoutput_filename, rname = "alice"):
    # Load frequency table
    freqtables = cex.load_cexfreqtable(input_freqtable_fname)
    xmlparser = etree.XMLParser(encoding = 'utf8')
    inputfile = open(input_fname, 'rb')
    xml = etree.parse(inputfile, parser = xmlparser)
    cex_parser = cex.CEXParser(xml)
    cex_parser.default_name = rname
    cex_features = cex_parser.parse(xml)
    cex_parser.set_conversions(freqtables, False)
    dnn_features = cex_parser.convert_to_dnnfeatures(cex_features)
    inputfile.close()
    cex.feat_to_ark(cexoutput_filename, dnn_features)


def make_output_kaldidnn_cex(logger, input_filename, output_filename, cexoutput_filename, rname = "alice"):
    xmlparser = etree.XMLParser(encoding = 'utf8')
    inputfile = open(input_filename, 'r')
    xml = etree.parse(inputfile, parser = xmlparser)
    cex_parser = cex.CEXParser(xml)
    cex_parser.default_name = rname
    cex_features = cex_parser.parse(xml)

    inputfile.close()

    cexfreqtable = cex_parser.calculate_freqtable(cex_features)

    cex_parser.set_conversions(cexfreqtable, False)
    dnn_features = cex_parser.convert_to_dnnfeatures(cex_features)
    cex.feat_to_ark(cexoutput_filename, dnn_features)

    if output_filename == None or output_filename == '-':
        output_file = sys.stdout
    else:
        output_file = open(output_filename, 'w')

    for f, fcex_features in cex_features.items():
        for cexs in fcex_features:
            output_file.write("{0} {1}\n".format(f, ' '.join(map(str,cexs))))

    if output_filename != None and output_filename != '-':
        output_file.close()

    cex.feat_to_ark(cexoutput_filename, dnn_features)

    return cexs, cex_features, cexfreqtable



def idlak_make_lang(textfile, datadir, langdir):
    p = xml.sax.make_parser()
    handler = idlak_saxhandler()
    p.setContentHandler(handler)
    p.parse(open(textfile, "rb"))
    print(textfile)
    fp = open(os.path.join(datadir, "text"), 'wb')
    for i in range(len(handler.ids)):
        #if valid_ids.has_key(handler.ids[i]):
        # If we are forcing beginning and end silences add <SIL>s
        #fp.write(("%s %s\n" % (handler.ids[i], ' '.join(handler.data[i]))).encode("utf8"))
        s = handler.ids[i] + u" "
        s += ' '.join(handler.data[i]) + "\n"
        #s = u"%s %s\n" % (handler.ids[i], u' '.join(handler.data[i]))
        fp.write(s.encode('utf-8'))
    fp.close()

    # lexicon and oov have all words for the corpus
    # whether selected or not by flist
    fpoov = open(os.path.join(langdir, "oov.txt"), 'wb')
    fplex = open(os.path.join(langdir, "lexicon.txt"), 'wb')
    # add oov word and phone (should never be required!
    fplex.write("<OOV> oov\n".encode('utf-8'))
    # If we are forcing beginning and end silences make lexicon
    # entry for <SIL>
    fplex.write("<SIL> sil\n".encode('utf-8'))
    fplex.write("<SIL> sp\n".encode('utf-8'))
    # write transcription lexicon and oov lexicon for info
    words = list(handler.lex.keys())
    words.sort()
    phones = {}
    chars = {}
    for w in words:
        prons = list(handler.lex[w].keys())
        prons.sort()
        # get all the characters as a check on normalisation
        for c in w:
            chars[c] = 1
        # get phone set from transcription lexicon
        for p in prons:
            if len(p):
                pp = p.split()
                for phone in pp:
                    phones[phone] = 1
                fplex.write(("%s %s\n" % (w, p)).encode('utf-8'))
        if w in handler.oov:
            fpoov.write(("%s %s\n" % (w, prons[0])).encode('utf-8'))
    fplex.close()
    fpoov.close()
    # write phone set
    # Should throw if phone set is not conformant
    # ie. includes sp or ^a-z@
    fp = open(os.path.join(langdir, "nonsilence_phones.txt"), 'w')
    phones = list(phones.keys())
    phones.sort()
    fp.write('\n'.join(phones) + '\n')
    fp.close()
    # write character set
    fp = open(os.path.join(langdir, "characters.txt"), 'wb')
    chars = list(chars.keys())
    chars.sort()
    fp.write((' '.join(chars)).encode('utf8'))
    fp.write("\n".encode('utf-8'))
    fp.close()
    # silence models
    fp = open(os.path.join(langdir, "silence_phones.txt"), 'w')
    fp.write("sil\nsp\noov\n")
    fp.close()
    # optional silence models
    fp = open(os.path.join(langdir, "optional_silence.txt"), 'w')
    fp.write("sp\n")
    fp.close()
    # an empty file for the kaldi utils/prepare_lang.sh script
    fp = open(os.path.join(langdir, "extra_questions.txt"), 'w')
    fp.close()

def load_labs(labfile, statefile = None):
    out = {}
    states = None
    if statefile is not None:
        states = open(statefile).readlines()
    for j, l in enumerate(open(labfile)):
        ll = l.strip().split()
        ls = []
        if states is not None:
            ls = states[j].strip().split()
        key = ll[0]
        phones = []
        oldp = ll[1]
        np = 1
        start_time = 0.0
        state = 0
        olds = 0
        for i, p in enumerate(ll[2:]):
            if len(ls):
                state = int(ls[i+2])
            if p != oldp or olds > state or i == len(ll) - 3:
                if p == oldp and olds <= state: np += 1
                end_time = round(start_time + np * FRAMESHIFT, 4)
                phones.append([start_time, end_time, oldp])
                start_time = end_time
                #if p == oldp and olds > state:
                #    print "Duplicate phone encountered"
                if p != oldp or olds > state:
                    np = 1
                    oldp = p
                    olds = 0
                    # Border case where there is a single lonely phone at the end; should not happen
                    if i == len(ll) - 3:
                        end_time = round(start_time + np * FRAMESHIFT, 4)
                        phones.append([start_time, end_time, oldp])
            else:
                np += 1
                olds = state
        out[key] = phones
    return out

def load_words(wordfile):
    out = {}
    cur_times = {}
    for l in open(wordfile).readlines():
        ll = l.strip().split()
        key = ll[0]
        if key not in out:
            out[key] = []
            cur_times[key] = 0.0
        start_time = round(float(ll[2]), 4)
        end_time = round(start_time + float(ll[3]), 4)
        if start_time > cur_times[key]:
            out[key].append([cur_times[key], start_time, "<SIL>"])
        out[key].append((start_time, end_time, ll[4]))
        cur_times[key] = end_time
    # Hack: add a silence at the end of each sentence
    for k in out.keys():
        if out[k][-1][2] not in ['SIL', '!SIL', '<SIL>']:
            out[k].append([cur_times[k], 100000, "<SIL>"])
    return out

# Recreate an idlak compatible xml file from word and phone alignment
def write_xml_textalign(breaktype, breakdef, labfile, wordfile, output, statefile=None):
    impl = getDOMImplementation()

    document = impl.createDocument(None, "document", None)
    doc_element = document.documentElement

    if statefile is None:
        print("WARNING: alignment with phone identity only is not accurate enough. Please use states aligment as final argument.")

    #labs = glob.glob(labdir + '/*.lab')
    #labs.sort()
    all_labs = load_labs(labfile, statefile)
    all_words = load_words(wordfile)
    f = io.open(output, 'w', encoding='utf8')
    f.write(str('<document>\n'))
    for id in sorted(all_labs.keys()):
        lab = all_labs[id]
        #print lab
        #stem = os.path.splitext(os.path.split(l)[1])[0]

        fileid_element = document.createElement("fileid")
        doc_element.appendChild(fileid_element)
        fileid_element.setAttribute('id', id)

        words = all_words[id]# open(os.path.join(wrddir, stem + '.wrd')).readlines()
        phones = all_labs[id]
        pidx = 0
        for widx, ww in enumerate(words):
            #ww = w.split()
            pron = []
            while pidx < len(phones):
                pp = phones[pidx]#.split()
                if pp[1] != ww[1] and float(pp[1]) > float(ww[1]):
                    break
                pron.append(pp[2].split('_')[0])
                pidx += 1
                #if pidx >= len(phones):
                #    break
            # Truncate end time to end time of last phone
            if float(ww[1]) > float(phones[-1][1]):
                ww[1] = float(phones[-1][1])
            #print ww, pron #, pidx, phones[pidx]
            if len(pron) == 0: continue
            if ww[2] not in ['SIL', '!SIL', '<SIL>']:
                lex_element = document.createElement("lex")
                fileid_element.appendChild(lex_element)
                lex_element.setAttribute('pron', ' '.join(pron))

                text_node = document.createTextNode(ww[2])
                lex_element.appendChild(text_node)
            else:
                if not widx or (widx == len(words) - 1):
                    break_element = document.createElement("break")
                    fileid_element.appendChild(break_element)
                    break_element.setAttribute('type', breakdef)
                else:
                    btype = breakdef
                    for b in breaktype.split(','):
                        bb = b.split(':')
                        minval = float(bb[1])
                        if float(ww[1]) - float(ww[0]) < minval:
                            btype = bb[0]
                    break_element = document.createElement("break")
                    fileid_element.appendChild(break_element)
                    break_element.setAttribute('type', btype)
        f.write(str(fileid_element.toxml()) + '\n')

    f.write(str('</document>'))
    f.close()

def main():
    from optparse import OptionParser
    usage="usage: %prog [options] text.xml datadir langdir\n" \
        "Takes the output from idlaktxp tool and create the corresponding\n " \
        "text file and lang directory required for kaldi forced alignment recipes."
    parser = OptionParser(usage=usage)
    parser.add_option('-m','--mode', default = 0,
                      help = 'Execution mode (0 => make_lang, 1 => write_xml_textalign, 2 => make_output_kaldidnn_cex')
    parser.add_option('-r','--root-name', default = "alice",
                      help = 'Root name to use for generating spurtID from anonymous spt')
    opts, args = parser.parse_args()
    if int(opts.mode) == 0 and len(args) == 3:
        idlak_make_lang(*args)
    elif int(opts.mode) == 1 and len(args) in [5, 6]:
        write_xml_textalign(*args)
    elif int(opts.mode) == 2:
        logger = logging.getLogger('kaldicex')
        if len(args) == 2:
            ret = make_output_kaldidnn_cex(logger, args[0], None, args[1], opts.root_name)

            if args[1] != '-' and args[1] != '':
                fname = args[1] + '.freq'
                cex.save_cexfreqtable(fname, ret[2])

        # Forward with existing freqtable
        elif len(args) == 3:
            forward_context(args[0], args[1], args[2], opts.root_name)
    else:
        parser.error('Mandatory arguments missing or excessive number of arguments')

if __name__ == '__main__':
    main()
