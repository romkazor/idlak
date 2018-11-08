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

import os
import sys
import logging

from . import txp
from . import vocoder
from . import gen
from . import pylib

class TangleVoice:

    NumStates = 5 # number of duration states

    """ Wrapper for pyIdlak to be used for TTS """
    def __init__(self, voice_dir = None, loglvl = logging.WARN):
        logging.basicConfig(level = loglvl)
        self.log = logging.getLogger('tangle')
        self._voicedir = None
        self._lng = ''
        self._acc = ''
        self._spk = ''
        self._region = ''

        if not voice_dir is None:
            self.load_voice(voice_dir)

    @property
    def lng(self):
        return self._lng
    @property
    def acc(self):
        return self._acc
    @property
    def spk(self):
        return self._spk
    @property
    def region(self):
        return self._region
    @property
    def srate(self):
        return self._srate
    @property
    def delta_order(self):
        return self._delta_order
    @property
    def mcep_order(self):
        return self._mcep_order
    @property
    def bndap_order(self):
        return self._bndap_order
    @property
    def fftlen(self):
        return self._fftlen
    @property
    def voice_thresh(self):
        return self._voice_thresh
    @property
    def alpha(self):
        return self._alpha


    def load_voice(self, voice_dir):
        """ Loads a voice from a directory """
        self._voicedir = os.path.abspath(str(voice_dir))
        self.log.info("Loading voice from {0}".format(self._voicedir))
        if not os.path.isdir(self._voicedir):
            raise IOError("Cannot find voice directory")

        voice_conf = {}
        _ignore_fields = ['tpdbvar']
        with open(os.path.join(self._voicedir, 'voice.conf')) as voice_conf_file:
            for line in voice_conf_file:
                line = line.strip()
                if not len(line) or line.startswith('#'):
                    continue
                try:
                    field, val = line.split('=', 1)
                    if field not in _ignore_fields:
                        voice_conf[field] = val
                except ValueError:
                    raise IOError("cannot load voice configuration")
        try:
            self._lng = voice_conf['lng']
            del voice_conf['lng']
        except KeyError:
            print("WARN: voice configuration missing langage (lng)", file = sys.stderr)
        try:
            self._acc = voice_conf['acc']
            del voice_conf['acc']
        except KeyError:
            print("WARN: voice configuration missing accent (acc)", file = sys.stderr)
        try:
            self._spk = voice_conf['spk']
            del voice_conf['spk']
        except KeyError:
            print("WARN: voice configuration missing speaker (spk)", file = sys.stderr)

        if 'region' in voice_conf:
            self._region = voice_conf['region']
            del voice_conf['region']

        # make sure all types are ok as we go
        def __load_fields(fields, fieldtype, fieldtypename):
            for field in fields:
                if field in voice_conf:
                    try:
                        val = fieldtype(voice_conf[field])
                        setattr(self, '_' + field, val)
                    except ValueError:
                        print("ERROR: voice configuration cannot convert '{0}' to {1}".format(field, fieldtypename),
                              file = sys.stderr)
                    finally:
                        del voice_conf[field]
        int_fields = ['srate', 'delta_order', 'mcep_order', 'bndap_order', 'fftlen']
        __load_fields(int_fields, int, 'integer')
        float_fields = ['voice_thresh', 'alpha']
        __load_fields(float_fields, float, 'float')

        for k in voice_conf:
            print("WARN: unknown voice configuration field '{0}'".format(k), file = sys.stderr)

        self._load_txp()
        self._load_gen()


    def _load_txp(self):
        """ Load the text processing components """
        txpargs = [
            '--tpdb', os.path.join(self._voicedir, 'lang'),
            '--general-lang', self.lng,
            '--general-acc', self.acc,
        ]
        if self._region:
            txpargs.extend(['--general-region', self._region])
        self._args = txp.TxpArgumentParser(usage='')
        self._args.parse_args(*txpargs)
        self.Tokeniser = txp.modules.Tokenise(self._args)
        self.PosTag  = txp.modules.PosTag(self._args)
        self.Normalise = txp.modules.Normalise(self._args)
        self.Pauses = txp.modules.Pauses(self._args)
        self.Phrasing = txp.modules.Phrasing(self._args)
        self.Pronounce = txp.modules.Pronounce(self._args)
        self.PostLex = txp.modules.PostLex(self._args)
        self.Syllabify = txp.modules.Syllabify(self._args)
        self.ContextExtraction = txp.modules.ContextExtraction(self._args)


    def _load_gen(self):
        """ Loads the generative modelling parts of the voice """
        cexfreqtablefn = os.path.join(self._voicedir, 'lang',  'cex.ark.freq')
        if not os.path.isfile(cexfreqtablefn):
            raise IOError("Cannot find cex frequency table: '{0}'".format(cexfreqtablefn))
        self._cexfreqtable = gen.load_cexfreqtable(cexfreqtablefn)
        self._durmodel = self._load_dnn(os.path.join(self._voicedir, 'dur'))


    def _load_dnn(self, dnndir):
        """ Loads a DNN model from a directory """
        # using these functions a lot in this function
        from os.path import join as pjoin
        from os.path import isdir, isfile

        nnet_model = pjoin(dnndir, 'final.nnet')
        feat_transform_fn = pjoin(dnndir, 'reverse_final.feature_transform')

        kwargs = {}
        indelta_optsfn = pjoin(dnndir, 'indelta_opts')
        if isfile(indelta_optsfn):
            kwargs['indelta_opts'] = open(indelta_optsfn).read()

        incmvn_optsfn = pjoin(dnndir, 'incmvn_opts')
        incmvn_globfn = pjoin(dnndir, 'incmvn_glob.ark')
        if isfile(incmvn_optsfn) and isfile(incmvn_globfn):
            kwargs['incmvn_global'] = pylib.PyReadKaldiDoubleMatrix(incmvn_globfn)
            kwargs['incmvn_global_opts'] = open(incmvn_optsfn).read()

        intransformfn = pjoin(dnndir, 'input_final.feature_transform')
        if isfile(intransformfn):
            kwargs['input_transform'] = intransformfn

        return gen.NNet(nnet_model, feat_transform_fn, **kwargs)


    def process_text(self, text, normalise=True, cex=True):
        """ Process the input text

            If normalise is True then the full normaliser is run.
            If cex is True then context features are also run

            Returns a txp XML document object
        """
        self.log.debug("Processing input text")
        doc = txp.XMLDoc('<doc>' + str(text) + '</doc>')
        self.Tokeniser.process(doc)
        self.PosTag.process(doc)
        if normalise:
            self.Normalise.process(doc)
        self.Pauses.process(doc)
        self.Phrasing.process(doc)
        self.Pronounce.process(doc)
        self.PostLex.process(doc)
        self.Syllabify.process(doc)
        if cex:
            self.ContextExtraction.process(doc)
        return doc


    def convert_to_dnn_features(self, doc):
        """ Converts a txp XML to dnn features """
        self.log.debug("Converting processed text to DNN input features")
        if not type(doc) == txp.XMLDoc:
            raise ValueError("doc must be a txp XMLDoc")
        features = gen.cex_to_feat(doc, self._cexfreqtable)
        return features


    def generate_duration(self, dnnfeatures):
        """ Takes the dnnfeatures and generates phone durations """
        self.log.debug("Generating state durations")
        for spurtid in dnnfeatures:
            self.log.debug('generating duration for {0}'.format(spurtid))
            spurtfeatures = dnnfeatures[spurtid]
            statedfeatures = self._add_state_feature(spurtfeatures)
            durmatrix = self._durmodel.forward(statedfeatures)


    def _add_state_feature(self, spurtfeatures):
        statedfeatures = []
        for row in spurtfeatures:
            statedfeatures.extend([row + [s] for s in range(self.NumStates)])
        return statedfeatures

    # model pitch
    # model accoustic features

    # vocodes
