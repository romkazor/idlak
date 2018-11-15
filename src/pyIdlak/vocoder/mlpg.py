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
from . import pyIdlak_vocoder

def mlpg(mean, mean_d, mean_dd, var, var_d, var_dd,
         d_win_filename, dd_win_filename,
         input_type = 0, influence_range = 30
         ):
    """ Convience wrapper for MLPG

        mean:               list of mean values vectors
        mean_d:             list of mean delta values vectors
        mean_dd:            list of mean double delta values vectors
        var:                list of variance vectors
        var_d:              list of delta variance vectors
        var_dd:             list of double delta variance vectors
        d_win_filename:     file name for window for calculating delta
        dd_win_filename:    file name for window for calculating delta
        input_type          as per SPTK (0)
        influence_range     as per SPTK (30)
    """
    num_frames = len(mean)
    if num_frames == 0:
        raise ValueError("number of frames is 0")
    inconsistant_num_frames = []
    if len(mean_d) != num_frames: inconsistant_num_frames.append('mean_d')
    if len(mean_dd) != num_frames: inconsistant_num_frames.append('mean_dd')
    if len(var) != num_frames: inconsistant_num_frames.append('var')
    if len(var_d) != num_frames: inconsistant_num_frames.append('var_d')
    if len(var_dd) != num_frames: inconsistant_num_frames.append('var_dd')
    if len(inconsistant_num_frames):
        raise ValueError("number of frames is inconsistant with mean in " +
                         '. '.join(inconsistant_num_frames))

    vector_length = len(mean[0])
    if vector_length == 0:
        raise ValueError("vector length is 0")

    # Get the input in the right form and check all rows are the same order
    mlpg_input = []
    for frame_idx in range(num_frames):
        fmean       = mean[frame_idx]
        fmean_d     = mean_d[frame_idx]
        fmean_dd    = mean_dd[frame_idx]
        fvar        = var[frame_idx]
        fvar_d      = var_d[frame_idx]
        fvar_dd     = var_dd[frame_idx]
        if len(fmean) != vector_length:
            raise ValueError('vector length not consistant at idx {} in mean'.format(frame_idx))
        if len(fmean_d) != vector_length:
            raise ValueError('vector length not consistant at idx {} in mean_d'.format(frame_idx))
        if len(fmean_dd) != vector_length:
            raise ValueError('vector length not consistant at idx {} in mean_dd'.format(frame_idx))
        if len(fvar) != vector_length:
            raise ValueError('vector length not consistant at idx {} in var'.format(frame_idx))
        if len(fvar_d) != vector_length:
            raise ValueError('vector length not consistant at idx {} in var_d'.format(frame_idx))
        if len(fvar_dd) != vector_length:
            raise ValueError('vector length not consistant at idx {} in var_dd'.format(frame_idx))

        frame_vec = map(float, fmean + fmean_d + fmean_dd + fvar + fvar_d + fvar_dd)
        mlpg_input.extend(list(frame_vec))

    # Check the window files
    if not os.path.isfile(d_win_filename):
        raise ValueError('cannot find d window file ' + d_win_filename)
    if not os.path.isfile(dd_win_filename):
        raise ValueError('cannot find dd window file ' + dd_win_filename)

    window_filenames = [d_win_filename, dd_win_filename]

    if input_type not in [0,1,2]:
        raise ValueError("input_type must be 0, 1, or 2")

    rawresult = pyIdlak_vocoder.PySPTK_mlpg(mlpg_input,
                                            vector_length,
                                            window_filenames,
                                            input_type,
                                            influence_range)

    result = []
    for idx in range(0, len(rawresult), vector_length):
        result.append(list(rawresult[idx: idx+vector_length]))
    if len(result) != num_frames:
        print('num frames:', num_frames, '  result:', len(result))
        print('num rawresult:', len(rawresult)/vector_length)
        print('num mlpg_input:', len(mlpg_input)/(6*vector_length))

    return result
