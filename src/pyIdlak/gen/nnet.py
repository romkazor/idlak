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

import re
import logging

from .. import pylib
from . import pyIdlak_gen

class NNet:
    def __init__(self, nnet_model,
                    incmvn_glob = False,
                    indelta_opts = False,
                    incmvn_opts = False,
                    loglvl = logging.WARN):
        """ Load a NNet model """
        logging.basicConfig(level = loglvl)
        self.log = logging.getLogger('pynnet')
        self.log.debug('Initialising NNet')

        # Options for different parts
        self._incmvn_opts = pylib.PyOptions(pylib.ApplyCMVNOptions)

        self.log.debug('Loading options')
        if indelta_opts:
            self._load_indelta_opts(indelta_opts)
        if incmvn_glob and incmvn_opts:
            self._incmvn_glob = incmvn_glob
            self._load_incmvn(incmvn_opts)
        elif (incmvn_glob_ark or incmvn_opts):
            raise ValueError('incmvn_glob_ark and incmvn_opts '
                             'must both be specified or left out')
        else:
            self._incmvn_glob = False


    def forward(self, features_in):
        """ Runs a forward pass through the features """
        kaldimat = pylib.PyKaldiMatrixBaseFloat_frmlist(features_in)

        self.log.debug('Applying global cmvn on labels')
        if self._incmvn_glob:
            kaldimat_new = pyIdlak_gen.PyApplyCMVN(
                self._incmvn_opts.kaldiopts, kaldimat, self._incmvn_glob)
            del kaldimat # saves memory
            kaldimat = kaldimat_new

        


    def _load_indelta_opts(self, indelta_opts):
        self.log.debug('Loading input delta options')
        raise NotImplementedError("loading indelta_opts")


    def _load_incmvn(self, incmvn_opts):
        """ Load global CMVN options """
        self.log.debug('Loading options for global CMVN')
        norm_mean = self._get_optval('norm-means', incmvn_opts)
        if not norm_mean is None:
            self._incmvn_opts.set('norm-means', self._str_to_bool(norm_mean))
        norm_vars = self._get_optval('norm-vars', incmvn_opts)
        if not norm_vars is None:
            self._incmvn_opts.set('norm-vars', self._str_to_bool(norm_vars))


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
