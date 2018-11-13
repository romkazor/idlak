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
import collections
import math
from lxml import etree

from . import txp
from . import vocoder
from . import gen
from . import pylib

class TangleVoice:

    NumStates = 5 # number of duration states

    # should not need to be every changed
    _phone_pos_fuzz = 0.1
    _state_pos_fuzz = 0.2

    """ Wrapper for pyIdlak to be used for TTS """
    def __init__(self, voice_dir = None, loglvl = logging.WARN):
        logging.basicConfig(level = loglvl)
        self.log = logging.getLogger('tangle')
        self._voicedir = None
        self._lng = ''
        self._acc = ''
        self._spk = ''
        self._region = ''
        self._fshift = 0.005


        if not voice_dir is None:
            self.load_voice(voice_dir)


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
            self.log.warn("voice configuration missing langage (lng)")
        try:
            self._acc = voice_conf['acc']
            del voice_conf['acc']
        except KeyError:
            self.log.warn("voice configuration missing accent (acc)")
        try:
            self._spk = voice_conf['spk']
            del voice_conf['spk']
        except KeyError:
            self.log.warn("voice configuration missing speaker (spk)")

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
                        self.log.error(
                            "voice configuration cannot convert '{0}' to {1}".format(
                                field, fieldtypename))
                    finally:
                        del voice_conf[field]
        int_fields = ['srate', 'delta_order', 'mcep_order', 'bndap_order', 'fftlen']
        __load_fields(int_fields, int, 'integer')
        float_fields = ['voice_thresh', 'alpha', 'fshift']
        __load_fields(float_fields, float, 'float')

        for k in voice_conf:
            self.log.warn("unknown voice configuration field '{0}'".format(k))

        self._load_txp()
        self._load_gen()
        self._load_vocoder()


    def speak(self, text):
        """ Simple interface for speaking text, returns the waveform """
        cex = self.process_text(text)
        durdnnfeatures = self.cex_to_dnn_features(cex)
        state_durations = self.generate_state_durations(durdnnfeatures)
        pitchdnnfeatures = self.combine_durations_and_features()
        # model pitch
        # apply MLPG
        # vocode
        # return wav


    def process_text(self, text, normalise=True, cex=True):
        """ Process the input text

            If normalise is True then the full normaliser is run.
            If cex is True then context features are also run

            Returns a txp XML document object
        """
        self.log.debug("Processing input text")
        text = str(text)
        xmlparser = etree.XMLParser(encoding = 'utf8')
        try:
            etree.fromstring(text, parser = xmlparser)
        except etree.XMLSyntaxError:
            self.log.debug("Input is not valid xml, adding parent tags")
            text = '<parent>' + text + '</parent>'
            try:
                etree.fromstring(text, parser = xmlparser)
            except etree.XMLSyntaxError as e:
                self.log.critical('Cannot parse input')
                raise(e)

        doc = txp.XMLDoc(text)
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


    def cex_to_dnn_features(self, doc):
        """ Converts a txp XML to dnn features """
        self.log.debug("Converting processed text to DNN input features")
        if not type(doc) == txp.XMLDoc:
            raise ValueError("doc must be a txp XMLDoc")
        features = gen.cex_to_feat(doc, self._cexfreqtable)
        return features


    def generate_state_durations(self, dnnfeatures, apply_postproc = True):
        """ Takes the dnnfeatures and generates state durations in frames

            The state durations are predicted in frames then go through some
            post-processing. The return is an n x m matrix in the form of a
            list of lists of doubles where n is number of phones and m is the
            number of states

            The post processing can be disabled to just produce the results of
            the duration DNN prediction.
        """
        self.log.debug("Generating state durations")
        durations = collections.OrderedDict()
        for spurtid in dnnfeatures:
            self.log.debug('generating duration for {0}'.format(spurtid))
            spurtfeatures = dnnfeatures[spurtid]
            statedfeatures = self._add_state_feature(spurtfeatures)
            durmatrix = self._durmodel.forward(statedfeatures)
            if apply_postproc:
                durations[spurtid] = self._post_duration_processing(durmatrix)
            else:
                durations[spurtid] = durmatrix

        return durations


    def combine_durations_and_features(self, durations, dnnfeatures):
        """ Combines the state durations and full context features
            and to form inputs for the pitch modelling

            Durations are in frames
            A fuzzy factor is introduced to positions
        """
        self.log.debug("Combining predicted state durations with DNN features")
        combinedfeatures = collections.OrderedDict()
        for spurtid, spurtdurs in durations.items():
            combinedfeatures[spurtid] = []
            for phoneidx, statedurs in enumerate(spurtdurs):
                phnfeatures = dnnfeatures[spurtid][phoneidx]
                phndur = sum(statedurs)
                for stateidx, statedur in enumerate(statedurs):
                    for statepos in range(statedur):
                        phnpos = sum(statedurs[:stateidx]) + statepos
                        fuzzy_statepos = self._fuzzy_position(
                            self._state_pos_fuzz, statepos, statedur)
                        fuzzy_phnpos = self._fuzzy_position(
                            self._phone_pos_fuzz, phnpos, phndur)
                        spos = [stateidx, statedur, fuzzy_statepos]
                        ppos = [phndur, fuzzy_phnpos]
                        combinedfeatures[spurtid].append(list(phnfeatures + spos + ppos))
                        phnpos += 1
        return combinedfeatures


    def durations_to_mlf(self, fname, durations):
        """ Saves an HTK compatable MLF file from the durations """
        _HTKtime = 100e-9  # 100ns
        with open(fname, 'w') as fout:
            fout.write('#!MLF!#\n')
            for fid, fdurations in durations.items():
                fout.write('"{0}.lab"\n'.format(fid))
                tstart = 0
                for pidx, statedurs in enumerate(fdurations):
                    for sidx, sdur in enumerate(statedurs):
                        if sdur:
                            tend = tstart + (sdur * self.fshift) / _HTKtime
                            fout.write('{0:.0f} {1:.0f} {2} {3}\n'.format(
                                tstart, tend, pidx+1, sidx))
                            tstart = tend
                fout.write('.\n')
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
    @property
    def fshift(self):
        return self._fshift

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
        self._pitchmodel = self._load_dnn(os.path.join(self._voicedir, 'pitch'))
        # Load synth model


    def _load_vocoder(self):
        """ Loads the vocoding info part of the voice """


    def _load_dnn(self, dnndir):
        """ Loads a DNN model from a directory """
        from os.path import join as pjoin
        from os.path import isdir, isfile

        nnet_model_fn = pjoin(dnndir, 'final.nnet')
        feat_transform_fn = pjoin(dnndir, 'reverse_final.feature_transform')

        kwargs = {}

        in_cmvn_global_optsfn = pjoin(dnndir, 'incmvn_opts')
        in_cmvn_global_fn = pjoin(dnndir, 'incmvn_glob.ark')
        if isfile(in_cmvn_global_optsfn) and isfile(in_cmvn_global_fn):
            kwargs['in_cmvn_global_opts'] = open(in_cmvn_global_optsfn).read()
            kwargs['in_cmvn_global_mat'] = pylib.PyReadKaldiDoubleMatrix(in_cmvn_global_fn)

        intransformfn = pjoin(dnndir, 'input_final.feature_transform')
        if isfile(intransformfn):
            kwargs['input_transform'] = intransformfn

        # Applying (reversed) fmllr transformation per-speaker

        out_cmvn_speaker_optsfn = pjoin(dnndir, 'cmvn_opts')
        out_cmvn_speaker_fn = pjoin(dnndir, 'cmvn.scp')
        if isfile(out_cmvn_speaker_optsfn) and isfile(out_cmvn_speaker_fn):
            kwargs['out_cmvn_speaker_opts'] = open(out_cmvn_speaker_optsfn).read()
            rspecifier = 'scp:' +  out_cmvn_speaker_fn
            kwargs['out_cmvn_speaker_mat'] = pylib.get_matrix_by_key(rspecifier, self.spk)


        # Global CMVN options

        return gen.NNet(nnet_model_fn, feat_transform_fn, **kwargs)


    def _add_state_feature(self, spurtfeatures):
        """ Takes the features from context,
            and generates features with state info """
        statedfeatures = []
        for row in spurtfeatures:
            statedfeatures.extend([row + [s] for s in range(self.NumStates)])
        return statedfeatures


    def _post_duration_processing(self, durmatrix):
        """ Final processing of state durations

            The first column of the predicted values is the state duration in
            miliseconds, and the second is the total phone duration.

            The post processing will average the prediction of the phones,
            avarage that with the total state duration. We then rescale the
            phones to match this avarage duration, and convert to frames.
            Finally the first and last states are modified so that they have at
            least one frame.
        """
        Sidx = 0 # state duration column = 0
        Pidx = 1 # phone duration column = 1
        N = self.NumStates
        state_durations = []
        predict_indices = range(0, len(durmatrix), N)
        for phone_idx, predict_idx in enumerate(predict_indices):
            pred_idx_range = range(predict_idx, predict_idx + N)
            phn_state_durs = [max(durmatrix[p][Sidx],0) for p in pred_idx_range]

            mean_phn = sum([durmatrix[p][Pidx] for p in pred_idx_range]) / N
            mean_phn = max(mean_phn, 0)
            t_state_dur = sum(phn_state_durs)

            # if all the state durations are zero then just set the first
            # and last to 1 and avoid a div by zero
            if t_state_dur > 0. and mean_phn > 0.:
                tgt_phone_dur = math.ceil((mean_phn + t_state_dur) / 2)
                ratio = tgt_phone_dur / t_state_dur
                for sidx in range(N):
                    phn_state_durs[sidx] *= ratio
                    phn_state_durs[sidx] = math.ceil(phn_state_durs[sidx])
            else:
                tgt_phone_dur = 0
                msg = 'In phone: {0}'.format(phone_idx)
                if t_state_dur == 0.:
                    msg += 'All state have 0. duration'
                if mean_phn == 0.:
                    msg += 'Mean phone duration is 0.'
                self.log.warn(msg)

            # Ensuring that the first and last state have at least 1 occupancy
            # as they model the transitions
            phn_state_durs[0] = max(phn_state_durs[0], 1)
            phn_state_durs[N - 1] = max(phn_state_durs[N - 1], 1)

            state_durations.append(phn_state_durs)

        return state_durations


    def _fuzzy_position(self, fuzzy_factor, position, duration):
        real_position = (position + 0.5) / duration
        return int(round(real_position / fuzzy_factor))
