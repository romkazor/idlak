# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Skaiste Butkute)
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
import pyIdlak_nnet_forward as nnet_fwd


def nnet_forward(nnet1_in, feature_rspecifier, feature_wspecifier,  # main args
                 class_frame_counts="", prior_scale=1.0,            # optn args
                 prior_floor=1e-10, feature_transform="",           # optn args
                 reverse_transform=False, no_softmax=False,         # optn args
                 apply_log=False, use_gpu="no"):                    # optn args
    """ Perform forward pass through Neural Network

    Attributes:
        nnet1_in (str)
        feature_rspecifier (str)
        feature_wspecifier (str)
        class_frame_counts (str):   optional - Vector with frame-counts of pdfs
                                    to compute log-priors. (priors are
                                    typically subtracted from log-posteriors
                                    or pre-softmax activations), default=''
        prior_scale (float):        optional - Scaling factor to be applied on
                                    pdf-log-priors, default=1.0
        prior_floor (float):        optional - Flooring constatnt for prior
                                    probability (i.e. label rel. frequency),
                                    default=1e-10
        feature_transform (str):    optional - Feature transform in front of
                                    main network (in nnet format), default=''
        reverse_transform (bool):   optional - Feature transform applied in
                                    reverse on output, default=False
        no_softmax (bool):          optional - Removes the last component with
                                    Softmax, if found. The pre-softmax
                                    activations are the output of the network.
                                    Decoding them leads to the same lattices as
                                    if we had used 'log-posteriors'.
                                    default=False
        apply_log (bool):           optional - Transform NN output by log(),
                                    default=False
        use_gpu (str):              optional - yes|no|optional, only has effect
                                    if compiled with CUDA, default='no'

    Return:
        int: return code of the forward pass

    """
    # validatation!
    if nnet1_in is None or nnet1_in == "":
        raise ValueError('nnet1_in (model_filename) cannot be empty!')
    if feature_rspecifier is None or feature_rspecifier == "":
        raise ValueError('feature_rspecifier cannot be empty!')
    if feature_rspecifier is None or feature_rspecifier == "":
        raise ValueError('feature_wspecifier cannot be empty!')
    if use_gpu not in ['no', 'yes', 'optional']:
        raise ValueError('use_gpu can only be no|yes|optional, not {}!'
                         .format(use_gpu))
    # create a nnet forward option object
    nnet_forward_opts = nnet_fwd.PyNnetForwardOpts()
    nnet_forward_opts.class_frame_counts = class_frame_counts
    nnet_forward_opts.prior_scale = prior_scale
    nnet_forward_opts.prior_floor = prior_floor
    nnet_forward_opts.feature_transform = feature_transform
    nnet_forward_opts.reverse_transform = reverse_transform
    nnet_forward_opts.no_softmax = no_softmax
    nnet_forward_opts.apply_log = apply_log
    nnet_forward_opts.use_gpu = use_gpu
    nnet_forward_opts.model_filename = nnet1_in
    nnet_forward_opts.feature_rspecifier = feature_rspecifier
    nnet_forward_opts.feature_wspecifier = feature_wspecifier

    return nnet_fwd.ForwardPass(nnet_forward_opts)
