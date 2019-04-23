# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: David Braude)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.

# This should probably be refactored into C++
import sys
import re
import json
import collections
import logging
from lxml import etree


CexFunc = collections.namedtuple('CexFunc', ['name', 'id', 'delim', 'isinteger'])
CexConversion = collections.namedtuple('CexConversion', ['id', 'mapping', 'func', 'args'])

# TODO compare the CEX to the arch

class CEXParser:

    def __init__(self, cexspec, include_phon_val = True, loglvl = logging.WARN):
        logging.basicConfig(level = loglvl)
        self.log = logging.getLogger('cexparse')
        if type(cexspec) == str:
            _cexspec = etree.parse(cexspec)
        elif (type(cexspec) not in [etree._Element, etree._ElementTree]):
            raise ValueError('CEX spec', type(cexspec), 'is not an etree element or string')
        else:
            _cexspec = cexspec
        self.default_name = 'test'
        self._conversions = None
        self._include_phon_val = bool(include_phon_val)
        self._parse_header(_cexspec)
        self._kaldi_phone_pat = re.compile('\^(.*?)\~(.*?)\-(.*?)\+(.*?)\=(.*)')
        self._hts_phone_pat = re.compile('(.*?)\^(.*?)\-(.*?)\+(.*?)\=(.*)')
        # cex000 is always phone identity or missing
        self._cex000func = CexFunc('PhoneVal', 'cex000', None, False)
        self.log.info("CEX parser initialised")


    def parse(self, xml, check_pron_strings = False):
        """ Parse the CEX document using the parser and returns then
            features by fileid / utterances

            if check_pron_strings is set to True, the parser will check
            the the strings in pron tags contain valid phone information
            in either Kaldi or HTS form
        """
        if (type(xml) not in [etree._Element, etree._ElementTree]):
            raise ValueError('CEX spec is not an etree element or string')

        self._parse_err = False
        self._untitled_counter = 1
        cex_features = collections.OrderedDict()
        if xml.find('fileid') is not None:
            self.log.info('iterating over file ids')
            spurt_iterator = xml.iter('fileid')
        else:
            self.log.info('iterating over spurts')
            spurt_iterator = xml.iter('spt')

        for spurt in spurt_iterator:
            spurt_id = spurt.attrib.get('id')
            if spurt_id is None:
                spurt_id = self.default_name +'{0:03d}'.format(self._untitled_counter)
                self._untitled_counter += 1
            self.log.debug('spurt ID is {0}'.format(spurt_id))
            cex_features[spurt_id] = self._parse_spurt(spurt, check_pron_strings)

        return cex_features


    def calculate_freqtable(self, cex_features):
        """ Takes the output from parsing and creates a frequency table """
        cexfreqtable = collections.OrderedDict()
        for cexid in self._cexids:
            cexfreqtable[cexid] = collections.defaultdict(int)
        for fileid, file_cexfeatures in cex_features.items():
            for phone_cex in file_cexfeatures:
                for val, cexid in zip(phone_cex, self._cexids):
                    cexfreqtable[cexid][val] += 1

        # fill in missing values for integers
        for cexid in self._cexids:
            if self._get_cexfunc(cexid).isinteger:
                minval = min(cexfreqtable[cexid].keys())
                maxval = max(cexfreqtable[cexid].keys())
                for i in range(minval, maxval): # no need to include maxval
                    if i not in cexfreqtable[cexid]:
                        cexfreqtable[cexid][i] = 0
        return cexfreqtable


    def set_conversions(self, cexfreqtable, norm_ints = True):
        """ Converts a frequency table to a lookup table """
        self._conversions = {}
        num_features = 0
        for cexid, val_freqs in cexfreqtable.items():
            cexfunc = self._get_cexfunc(cexid)

            cex_values = list(val_freqs.keys())
            if cexfunc.isinteger:
                cex_values = list(map(int, cex_values))
                mapping = False
                if norm_ints:
                    func = self._norm_int
                    args = [min(cex_values), max(cex_values)]
                else:
                    func = False
                    args = None
                num_features += 1
            else:
                cex_values.sort()
                mapping = {}
                idx = 1
                arrlen = len(cex_values)
                for v in cex_values:
                    if v != '0':
                        mapping[v] = idx
                        idx += 1
                    else:
                        mapping['0'] = 0
                        arrlen -= 1
                func = self._to_binary_array
                args = [arrlen]
                num_features += arrlen

            self._conversions[cexid] = CexConversion(cexid, mapping, func, args)
        self.log.debug("Number of dnnfeatures: {0:d}".format(num_features))


    def convert_to_dnnfeatures(self, cex_features):
        """ Takes the extracted CEX features and coverts them to numeric values """
        dnnfeatures = collections.OrderedDict()
        for spurt, spurt_cex_features in cex_features.items():
            dnnfeatures[spurt] = self._cex_to_features(spurt_cex_features)
        return dnnfeatures


    def _parse_header(self, xml):
        """ Processes the CEX header """
        cex_header = xml.find('./txpheader/cex')

        # Get information about the context features
        self._cexfunctions = []
        cexid_counter = 1
        for cexfunc in cex_header.iter('cexfunction'):
            name = cexfunc.attrib.get('name', '')
            cexid  = cexfunc.attrib.get('id',
                        'cex{0:03d}'.format(cexid_counter))
            cexid_counter += 1
            # delimiters appear on the left
            delim = cexfunc.attrib.get('delim', ' ')
            if re.match('^\s+$', delim):
                delim = '\s'
            else:
                delim = re.escape(delim)
            isinteger = bool(int(cexfunc.attrib.get('isinteger', 0)))
            self._cexfunctions.append(CexFunc(name, cexid, delim, isinteger))

        # Build a regex for extracting the context from the phone tag
        pat = ''
        for cexfunc in self._cexfunctions:
            pat += cexfunc.delim + '(?P<' + cexfunc.id + '>'
            if cexfunc.isinteger:
                pat += '\d'
            else:
                pat += '.'
            pat += '*'
            if cexfunc != self._cexfunctions[-1]:
                pat += '?'
            pat += ')'
        self._repat = re.compile(pat)
        self._cexids = []
        if self._include_phon_val:
            self._cexids.append('cex000')
        self._cexids.extend([c.id for c in self._cexfunctions])


    def _parse_spurt(self, spurt, check_pron_strings):
        """ Parse an indiviual spurt / fileid """
        phone_name_pre = ''
        cexfeats = []
        for pron in spurt.iter('phon'):
            phone_name = pron.attrib.get('val', 'pau')

            # Currently ignore utt internal split pauses
            if phone_name_pre == 'pau' and phone_name == 'pau':
                phone_name_pre = phone_name
                continue
            phone_name_pre = phone_name

            cexfeats.append(self._pron_to_feat(pron, check_pron_strings))
        return cexfeats


    def _pron_to_feat(self, pron, check_pron_strings):
        """ Converts a pron tag to context features """
        if check_pron_strings:
            if self._kaldi_phone_pat.match(pron.text) is None \
                and self._hts_phone_pat.match(pron.text) is None:
                    msg = 'phone context string does not match Kaldi or HTS formats'
                    msg += str(pron.text)
                    self.log.critical(msg)
        m = self._repat.match(pron.text)
        if m is None:
            self._parse_err = True
            self.log.error("Bad phone context string: " + str(pron.text))
        phone_name = pron.attrib.get('val', 'pau')
        cexs = []
        if self._include_phon_val:
            cexs.append(phone_name)
        for cexfunc in self._cexfunctions:
            val = m.group(cexfunc.id)
            if cexfunc.isinteger:
                cexs.append(int(val))
            else:
                cexs.append(val.strip())
        return cexs


    def _cex_to_features(self, spurt_cex_features):
        if not self._conversions:
            raise ValueError('Cannot convert to DNN features if coversion has not been set')

        spurt_features = []
        for phone_cex in spurt_cex_features:
            phone_features = []
            for cex, cexid in zip(phone_cex, self._cexids):
                conversion = self._conversions[cexid]
                if conversion.mapping:
                    try:
                        val = conversion.mapping[cex]
                    except KeyError:
                        msg = "Bad unknown value '{0}' for context feature '{1}' in context string: ".format(cex, cexid)
                        msg += ' '.join(map(str, phone_cex))
                        self.log.error(msg)
                        val = 0
                else:
                    val = cex

                if conversion.func:
                    phone_features.extend(conversion.func(val, *conversion.args))
                else:
                    phone_features.append(val)

            spurt_features.append(phone_features)

        return spurt_features


    def _to_binary_array(self, val, arrlen):
        """ Converts a integer value to a one of many feature """
        val = min(max(val, 0), arrlen)
        arr = [0] * arrlen
        if val:
            arr[val-1] = 1 # 1 indexed in the binary array
        return arr


    def _norm_int(self, val, offset, scaling):
        """ Converts integer to float using offset and scaling """
        return [(val - offset) / float(scaling)]


    def _get_cexfunc(self, cexid):
        """ Get the associated CEX function for the ID """
        if cexid == 'cex000':
            return self._cex000func
        for c in self._cexfunctions:
            if c.id == cexid:
                return c
        self.log.error("Cannot find function for CEX id: {0}".format(cexid))
        return None


###############################################################

def load_cexfreqtable(fname):
    """ Loads a Context Feature frequency table """
    with open(fname) as fp:
        cexfreqtable = json.load(fp)
    return cexfreqtable


def save_cexfreqtable(fname, cexfreqtable):
    """ Saves a Context Feature frequency table """
    with open(fname, 'w') as fp:
        json.dump(cexfreqtable, fp, ensure_ascii=False, indent=2)


def cex_to_feat(doc, cexfreqtable):
    """ Converts XML with context features to dnn features """
    from .. import txp
    if not type(doc) == txp.XMLDoc:
        raise ValueError("doc must be a txp XMLDoc")

    xmlparser = etree.XMLParser(encoding = 'utf8')
    xml = etree.fromstring(doc.to_string(), parser = xmlparser)

    cex_parser = CEXParser(xml)
    cex_features = cex_parser.parse(xml)

    cex_parser.set_conversions(cexfreqtable, False)
    dnn_features = cex_parser.convert_to_dnnfeatures(cex_features)
    return dnn_features


def feat_to_ark(fname, dnn_features, matrix = False, fmt = '{}'):
    """ Saves DNN features as a vector of vectors ascii ark file """
    spurtids = sorted(dnn_features.keys())
    if fname == '-':
        fout = sys.stdout
    else:
        fout = open(fname, 'w')

    for sptid in spurtids:
        fout.write(sptid)
        if matrix:
            fout.write(' [\n')

        for i, sptfeats in enumerate(dnn_features[sptid]):
            fout.write(' ')
            fout.write(' '.join(map(lambda s: fmt.format(s), sptfeats)))
            if matrix:
                fout.write('\n')
            else:
                fout.write(' ;')

        if matrix:
            fout.write(']')
        fout.write('\n')

    if fname == '-':
        fout.flush()
    else:
        fout.close()
