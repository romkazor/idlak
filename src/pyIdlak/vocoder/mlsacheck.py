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

from . import pyIdlak_vocoder

def stablise_mceps(mceps, alpha, fftlen, check_type = 2, stable_condition = 0,
              pade_order = 5, threshold = 0.0, quiet = True):
    """ Return stable mceps """
    flattened_mceps = []
    mcep_order = len(mceps[0]) - 1
    for frame in mceps:
        flattened_mceps.extend(frame)

    rawresult = pyIdlak_vocoder.PySPTK_mlsacheck(flattened_mceps, mcep_order,
        alpha, fftlen, check_type, stable_condition, pade_order,
        threshold, quiet)

    result = []
    for idx in range(0, len(rawresult), mcep_order+1):
        result.append(list(rawresult[idx: idx+vector_length]))
    return result
