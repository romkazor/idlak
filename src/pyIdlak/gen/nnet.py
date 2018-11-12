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
import re
import logging

from .. import pylib
from . import pyIdlak_gen

# Todo type checking

class NNet:
    def __init__(self, nnet_model_fn, feat_transform_fn,
                    in_cmvn_global_mat = False, in_cmvn_global_opts = False,
                    in_delta_opts = False,
                    input_transform = False,
                    out_cmvn_speaker_mat = False, out_cmvn_speaker_opts = False,
                    out_cmvn_global_mat = False, out_cmvn_global_opts = False,
                    loglvl = logging.WARN):
        """ Load a NNet model """
        logging.basicConfig(level = loglvl)
        self.log = logging.getLogger('pynnet')
        self.log.debug('Initialising NNet')

        if not os.path.isfile(nnet_model_fn):
            raise IOError("cannot find model file: " + nnet_model_fn)
        if not os.path.isfile(feat_transform_fn):
            raise IOError("cannot find transform file: " + feat_transform_fn)
        self._nnet_model_fn = nnet_model_fn
        self._feat_transform_fn = feat_transform_fn

        # Network options
        self._fwd_opts = pylib.PyOptions(
            pylib.PdfPriorOptions, pylib.NnetForwardOptions)
        self._fwd_opts.set('model-filename', nnet_model_fn)
        self._fwd_opts.set('reverse-transform', True)
        self._fwd_opts.set('feature-transform', self._feat_transform_fn)

        self.log.debug('Loading options')
        # Pre-processing options
        if in_cmvn_global_mat and in_cmvn_global_opts:
            self._in_cmvn_global_mat = in_cmvn_global_mat
            self._in_cmvn_global_opts = pylib.PyOptions(pylib.ApplyCMVNOptions)
            self._load_cmvn(self._in_cmvn_global_opts, in_cmvn_global_opts)
        elif (in_cmvn_global_mat or in_cmvn_global_opts):
            raise ValueError('in_cmvn_global_mat and in_cmvn_global_opts '
                             'must both be specified or left out')
        else:
            self._in_cmvn_global_mat = False

        if input_transform:
            if not os.path.isfile(input_transform):
                raise IOError("Cannot find input transform file: " + input_transform)
            self._in_transform = input_transform # A file name
            self._in_transform_opts = pylib.PyOptions(
                pylib.PdfPriorOptions, pylib.NnetForwardOptions)
            self._in_transform_opts.set("model-filename", input_transform)
        else:
            self._in_transform = False

        # Post-prosessing options
        if out_cmvn_speaker_mat and out_cmvn_speaker_opts:
            self._out_cmvn_speaker_mat = out_cmvn_speaker_mat
            self._out_cmvn_speaker_opts = pylib.PyOptions(pylib.ApplyCMVNOptions)
            self._out_cmvn_speaker_opts.set('reverse', True)
            self._load_cmvn(self._out_cmvn_speaker_opts, out_cmvn_speaker_opts)
        elif (out_cmvn_speaker_mat or out_cmvn_speaker_opts):
            raise ValueError('out_cmvn_speaker_mat and out_cmvn_speaker_opts '
                             'must both be specified or left out')
        else:
            self._out_cmvn_speaker_mat = False

        if out_cmvn_global_mat and out_cmvn_global_opts:
            self._out_cmvn_global_mat = out_cmvn_global_mat
            self._out_cmvn_global_opts = pylib.PyOptions(pylib.ApplyCMVNOptions)
            self._out_cmvn_global_opts.set('reverse', True)
            self._load_cmvn(self._out_cmvn_global_opts, out_cmvn_global_opts)
        elif (out_cmvn_global_mat or out_cmvn_global_opts):
            raise ValueError('out_cmvn_global_mat and out_cmvn_global_opts '
                             'must both be specified or left out')
        else:
            self._out_cmvn_global_mat = False


    def forward(self, features_in):
        """ Runs a forward pass through the features """
        mat = pylib.PyKaldiMatrixBaseFloat_frmlist(features_in)

        # 'Applying deltas on labels'

        if self._in_cmvn_global_mat:
            self.log.debug('Applying global cmvn on labels')
            mat = pyIdlak_gen.PyApplyCMVN(self._in_cmvn_global_opts.kaldiopts,
                 mat, self._in_cmvn_global_mat)

        if self._in_transform:
            self.log.debug('Applying feature transform on labels')
            mat = pyIdlak_gen.PyGenNnetForwardPass(
                self._in_transform_opts.kaldiopts, mat)

        self.log.debug('Forward DNN pass')
        mat = pyIdlak_gen.PyGenNnetForwardPass(self._fwd_opts.kaldiopts, mat)

        ## "Applying (reversed) fmllr transformation per-speaker"
        if self._out_cmvn_speaker_mat:
            self.log.debug('Applying (reversed) per-speaker cmvn on output features')
            mat = pyIdlak_gen.PyApplyCMVN(self._out_cmvn_speaker_opts.kaldiopts,
                 mat, self._out_cmvn_speaker_mat)

        if self._out_cmvn_global_mat:
            self.log.debug('Applying (reversed) global cmvn on output feature')
            mat = pyIdlak_gen.PyApplyCMVN(self._out_cmvn_global_opts.kaldiopts,
                 mat, self._out_cmvn_global_mat)

        return pylib.PyKaldiMatrixBaseFloat_tolist(mat)

    def _load_cmvn(self, pyopts, cmvn_opts):
        """ Load CMVN options """
        norm_mean = self._get_optval('norm-means', cmvn_opts)
        if not norm_mean is None:
            pyopts.set('norm-means', self._str_to_bool(norm_mean))
        norm_vars = self._get_optval('norm-vars', cmvn_opts)
        if not norm_vars is None:
            pyopts.set('norm-vars', self._str_to_bool(norm_vars))


    def _str_to_bool(self, val):
        """ Convert string to boolean value """
        return val.upper() in ['TRUE', 'ON', '1', 'T']


    def _get_optval(self, optname, optstring):
        """ Grab an option from a file """
        pat = '--' + optname + '\s*=\s*(?P<val>\S+)'
        m = re.search(pat, optstring)
        if m is None:
            return None
        val = m.group('val')
        if val.startswith('--'): # catches flags
            return 'true'
        return val
