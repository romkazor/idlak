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

import collections
import copy
import logging
import math
import os
import sys

from lxml import etree

from . import txp
from . import vocoder
from . import gen
from . import pylib

class TangleVoice:

    NumStates = 5 # number of duration states

    # should not ever need to be changed
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
        self._voice_thresh = 0.8

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
        self._load_mlpg()
        self._load_vocoder()


    def speak(self, text, wav_filename = None):
        """ Simple interface for speaking text, returns the waveform

            if wav_filename is a file name, then
        """
        cex = self.process_text(text)
        durfeatures = self.cex_to_dnn_features(cex)
        state_durations = self.generate_state_durations(durfeatures)
        pitchfeatures = self.combine_durations_and_features(
            state_durations, durfeatures)
        pitch = self.generate_pitch(pitchdnnfeatures)
        acousticdnnfeatures = self.combine_pitch_and_features(
            pitch, pitchfeatures)
        acousticfeatures = self.generate_acoustic_features(acousticdnnfeatures)
        waveform = self.vocode_acoustic_features(acousticfeatures, pitch,
                                                 wav_filename)
        return waveform


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
        for spurtid, spurtfeatures in dnnfeatures.items():
            self.log.debug('generating duration for ' + spurtid)
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


    def generate_pitch(self, dnnfeatures, mlpg = True, extract = True,
                             save_pdf_directory = ""):
        """ Predict the pitch features

            if mlpg is True then mlpg is applied
            if save_pdf_directory is set then the means and variances will
                be saved into that directory (used for debugging)
            if extract is True then only the first two columns are returned
                which are the voicing confidence and F0 respectively
        """
        self.log.debug("Generating pitch values")
        pitch = collections.OrderedDict()
        for spurtid, spurtfeatures in dnnfeatures.items():
            self.log.debug('generating pitch for ' + spurtid)
            pitchmatrix = self._pitchmodel.forward(spurtfeatures)
            if mlpg:
                self.log.debug('applying MLPG to pitch')
                if os.path.isdir(save_pdf_directory):
                    pdffile = os.path.join(save_pdf_directory, spurtid + '.pitch.pdf')
                else:
                    pdffile = False
                pitch[spurtid] = self._apply_mlpg(pitchmatrix, 'logf0', pdffile)
            else:
                if extract:
                    for idx, row in enumerate(pitchmatrix):
                        pitchmatrix[idx] = row[:2]
                pitch[spurtid] = pitchmatrix

        return pitch


    def combine_pitch_and_features(self, pitch, dnnfeatures):
        """ Insert the pitch as the first two columns of the DNN features """
        self.log.debug("Combining predicted pitch with DNN features")
        combinedfeatures = collections.OrderedDict()
        for spurtid in pitch.keys():
            combinedfeatures[spurtid] = []
            spurt_pitch = pitch[spurtid]
            spurt_feats = dnnfeatures[spurtid]
            for row_pitch, row_feats in zip(spurt_pitch, spurt_feats):
                combinedfeatures[spurtid].append(row_pitch + row_feats)
        return combinedfeatures


    def generate_acoustic_features(self, dnnfeatures, mlpg = True, extract = True,
                                         save_pdf_directory = ""):
        """ Predict the acoustic features

            if mlpg is True then mlpg is applied
            otherwise if extract is True then split out the MCEPs and Bndaps
            if save_pdf_directory is set then the means and variances will
            be saved into that directory (used for debugging)
        """
        self.log.debug("Generating acoustic features")
        acoustic = collections.OrderedDict()
        for spurtid, spurtfeatures in dnnfeatures.items():
            self.log.debug('generating acoustic features for ' + spurtid)
            acf = self._acousticmodel.forward(spurtfeatures)
            if not (mlpg or extract):
                acoustic[spurtid] = acf
                continue

            # order in the matrix is mcep, bndap, mcep_d, bndap_d, mcep_dd, bndap_dd
            mcep_start = 0
            mcep_end = mcep_start + self.mcep_order + 1
            bndap_start = mcep_end
            bndap_end = bndap_start + self.bndap_order
            mcep_d_start = bndap_end
            mcep_d_end = mcep_d_start + self.mcep_order + 1
            bndap_d_start = mcep_d_end
            bndap_d_end = bndap_d_start + self.bndap_order
            mcep_dd_start = bndap_d_end
            mcep_dd_end = mcep_dd_start + self.mcep_order + 1
            bndap_dd_start = mcep_dd_end
            bndap_dd_end = bndap_dd_start + self.bndap_order

            mceps = []
            bndaps = []
            for row in acf:
                mceps.append(row[mcep_start:mcep_end] + row[mcep_d_start:mcep_d_end] + row[mcep_dd_start:mcep_dd_end])
                bndaps.append(row[bndap_start:bndap_end] + row[bndap_d_start:bndap_d_end] + row[bndap_dd_start:bndap_dd_end])

            if mlpg:
                self.log.debug('applying MLPG')
                if os.path.isdir(save_pdf_directory):
                    mcep_pdf_file = os.path.join(save_pdf_directory,
                                                 spurtid + '.mcep.pdf')
                    bndap_pdf_file = os.path.join(save_pdf_directory,
                                                  spurtid + '.bndap.pdf')
                else:
                    mcep_pdf_file = False
                    bndap_pdf_file = False

                mceps = self._apply_mlpg(mceps, 'mcep', mcep_pdf_file)
                bndaps = self._apply_mlpg(bndaps, 'bndap', bndap_pdf_file)
            else:
                mceps = [mrow[:self.mcep_order+1] for mrow in mceps]
                bndaps = [brow[:self.bndap_order] for brow in bndaps]

            # convert bndaps to decibels to be inline with other tools (predicted as log value)
            for fidx in range(len(bndaps)):
                for bidx, bval in enumerate(bndaps[fidx]):
                    if bval >= -.5:
                        bndaps[fidx][bidx] = 0.
                    else:
                        bndaps[fidx][bidx] = 20. * (bval + .5) / math.log(10)

            acoustic[spurtid] = {'mcep' : mceps, 'bndap': bndaps}
        return acoustic


    def vocode_acoustic_features(self, acoutic_features, pitch,
                                 mixed_excitation = True,
                                 save_residual_directory = False,
                                 wav_filename = None):
        """ Vocode the acoustic features using MLSA

            if mixed_excitation is set to False, then the residual is
            generated without mixed excitation

            if save_residual_directory is set then the by spurt residual will
                be saved into that directory (used for debugging)
        """
        if mixed_excitation:
            exc_type = vocoder.MCEPExcitation.MIXED
        else:
            exc_type = vocoder.MCEPExcitation.SPTK

        waveform = []
        for spurtid in acoutic_features:
            mceps =  acoutic_features[spurtid]['mcep']
            bndaps = copy.copy(acoutic_features[spurtid]['bndap'])
            f0s = []
            for fidx, (confidence, f0) in enumerate(pitch[spurtid]):
                if confidence > self._voice_thresh:
                    f0s.append(f0)
                else:
                    f0s.append(0.0)
                    for bidx in range(self.bndap_order):
                        bndaps[fidx][bidx] = 0.0

            excitation = self._vocoder.gen_excitation(f0s, bndaps, exc_type)
            if os.path.isdir(save_residual_directory):
                residualfile = os.path.join(save_residual_directory, spurtid + '.res')
                with open(residualfile, 'w') as fout:
                    def _tostr(v):
                        return '{0:.5f}'.format(v)
                    fout.write('\n'.join(map(_tostr, excitation)))
                    fout.write('\n')
            spurt_waveform = self._vocoder.apply_mlsa(mceps, excitation)
            waveform.extend(spurt_waveform)

        if wav_filename:
            self.log.debug('saving to ' + wav_filename)
            self._vocoder.to_wav(wav_filename, waveform)

        return waveform


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
    @property
    def voicedir(self):
        return self._voicedir

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
        from os.path import join
        cexfreqtable = join(self._voicedir, 'lang',  'cex.ark.freq')
        if not os.path.isfile(cexfreqtable):
            msg = "Cannot find cex frequency table: '{0}'".format(cexfreqtable)
            self.log.critical(msg)
            raise IOError(msg)
        self._cexfreqtable = gen.load_cexfreqtable(cexfreqtable)
        self._durmodel = self._load_dnn(join(self._voicedir, 'dur'))
        self._pitchmodel = self._load_dnn(join(self._voicedir, 'pitch'))
        self._acousticmodel = self._load_dnn(join(self._voicedir, 'acoustic'))


    def _load_mlpg(self):
        """ Loads the parts of the voice that deal with MLPG """
        from os.path import join, isfile
        var_cmpfn = join(self._voicedir, 'lang', 'var_cmp.txt')
        varfile = open(var_cmpfn).readlines()
        self._variances =  {
            'logf0' : [float(v.split()[1]) for v in varfile[:6]],
            'mcep' :  [],
            'bndap' : [],
        }
        # bit confusing but the order in the file is:
        # f0 : df0 : ddf0 : mcep : bndap : d_mcep : d_bndap: dd_mcep : dd_bndap
        mcep_idx     = 6
        bndap_idx    = mcep_idx    + (1 + self.mcep_order)
        d_mcep_idx   = bndap_idx   + self.bndap_order
        d_bndap_idx  = d_mcep_idx  + (1 + self.mcep_order)
        dd_mcep_idx  = d_bndap_idx + self.bndap_order
        dd_bndap_idx = dd_mcep_idx + (1 + self.mcep_order)
        for idx, line in enumerate(varfile):
            v = float(line.split()[1])
            if   idx >= dd_bndap_idx:
                self._variances['bndap'].append(v)
            elif idx >= dd_mcep_idx:
                self._variances['mcep'].append(v)
            elif idx >= d_bndap_idx:
                self._variances['bndap'].append(v)
            elif idx >= d_mcep_idx:
                self._variances['mcep'].append(v)
            elif idx >= bndap_idx:
                self._variances['bndap'].append(v)
            elif idx >= mcep_idx:
                self._variances['mcep'].append(v)

        self._delta_windows = {
            'logf0' : (
                self._load_float_file(join(self._voicedir, 'win', 'logF0_d1.txt')),
                self._load_float_file(join(self._voicedir, 'win', 'logF0_d2.txt'))
            ),
            'bndap' : (
                self._load_float_file(join(self._voicedir, 'win', 'bndap_d1.txt')),
                self._load_float_file(join(self._voicedir, 'win', 'bndap_d2.txt'))
            ),
            'mcep' : (
                self._load_float_file(join(self._voicedir, 'win', 'mcep_d1.txt')),
                self._load_float_file(join(self._voicedir, 'win', 'mcep_d2.txt'))
            ),
        }


    def _load_vocoder(self):
        """ Loads the vocoding info part of the voice """
        self._vocoder = vocoder.MCEPVocoder(srate  = self.srate,
                                            order  = self.mcep_order,
                                            alpha  = self.alpha,
                                            fftlen = self.fftlen,
                                            fshift = self.fshift)

    def _load_dnn(self, dnndir):
        """ Loads a DNN model from a directory """
        from os.path import join, isdir, isfile

        nnet_model_fn = join(dnndir, 'final.nnet')
        feat_transform_fn = join(dnndir, 'reverse_final.feature_transform')

        kwargs = {}

        # Input deltas
        in_delta_optsfn = join(dnndir, 'indelta_opts')
        if isfile(in_delta_optsfn) and isfile(in_delta_optsfn):
            kwargs['in_delta_opts'] = open(in_delta_optsfn).read()

        # Global input CMVN
        in_cmvn_global_optsfn = join(dnndir, 'incmvn_opts')
        in_cmvn_global_fn = join(dnndir, 'incmvn_glob.ark')
        if isfile(in_cmvn_global_optsfn) and isfile(in_cmvn_global_fn):
            kwargs['in_cmvn_global_opts'] = open(in_cmvn_global_optsfn).read()
            kwargs['in_cmvn_global_mat'] = pylib.PyReadKaldiDoubleMatrix(in_cmvn_global_fn)

        # Input transform
        intransformfn = join(dnndir, 'input_final.feature_transform')
        if isfile(intransformfn):
            kwargs['input_transform'] = intransformfn

        # Applying (reversed) fmllr transformation per-speaker

        # Output by speaker CMVN
        out_cmvn_speaker_optsfn = join(dnndir, 'cmvn_opts')
        out_cmvn_speaker_fn = join(dnndir, 'cmvn.ark')
        if isfile(out_cmvn_speaker_optsfn) and isfile(out_cmvn_speaker_fn):
            kwargs['out_cmvn_speaker_opts'] = open(out_cmvn_speaker_optsfn).read()
            rspecifier = 'ark:' +  out_cmvn_speaker_fn
            kwargs['out_cmvn_speaker_mat'] = pylib.get_matrix_by_key(rspecifier, self.spk)


        # Global CMVN options


        return gen.NNet(nnet_model_fn, feat_transform_fn, **kwargs)


    def _load_float_file(self, fname):
        """ Loads a filename into a flat list of floats """
        ret = []
        with open(fname) as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                line = line.split()
                for v in map(float, line):
                    ret.append(v)
        return ret



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
        real_position = position / duration
        fuzzy_pos =  math.ceil(real_position / fuzzy_factor)
        return fuzzy_pos


    def _apply_mlpg(self, matrix, name, pdffile):
        """ Apply MLPG

            Assume the order is a third of the matrix
        """
        num_frames = len(matrix)
        order = len(matrix[0])//3

        mean = []
        mean_d = []
        mean_dd = []
        for frame in matrix:
            mean.append(list(frame[:order]))
            mean_d.append(list(frame[order:2*order]))
            mean_dd.append(list(frame[2*order:]))

        var = [self._variances[name][:order]] * num_frames
        var_d = [self._variances[name][order:2*order]]  * num_frames
        var_dd = [self._variances[name][2*order:]] * num_frames
        var[0] = [0.]*order
        var_d[0] = [0.]*order
        var_dd[0] = [0.]*order
        var[-1] = [0.]*order
        var_d[-1] = [0.]*order
        var_dd[-1] = [0.]*order

        if pdffile:
            with open(pdffile, 'w') as fout:
                for fidx in range(num_frames):
                    def _tostr(v):
                        return '{0:.5f}'.format(v)
                    fout.write(' '.join(map(_tostr, mean[fidx])))
                    fout.write(' ')
                    fout.write(' '.join(map(_tostr, mean_d[fidx])))
                    fout.write(' ')
                    fout.write(' '.join(map(_tostr, mean_dd[fidx])))
                    fout.write(' ')
                    fout.write(' '.join(map(_tostr, var[fidx])))
                    fout.write(' ')
                    fout.write(' '.join(map(_tostr, var_d[fidx])))
                    fout.write(' ')
                    fout.write(' '.join(map(_tostr, var_dd[fidx])))
                    fout.write('\n')

        d1win, d2win = self._delta_windows[name]
        output = vocoder.mlpg(mean, mean_d, mean_dd,
                              var,  var_d,  var_dd,
                              d1win, d2win,
                              input_type = 0)
        return output
