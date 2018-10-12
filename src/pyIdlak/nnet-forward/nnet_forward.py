import os
import sys
import pyIdlak_nnet_forward as nnet_fwd


def nnet_forward(nnet1_in, feature_rspecifier, feature_wspecifier,  # main args
                 feature_transform="", reverse_transform=False,     # optn args
                 no_softmax=False, apply_log=False, use_gpu="no"):  # optn args
    """ Perform forward pass through Neural Network

    Attributes:
        nnet1_in (str)
        feature_rspecifier (str)
        feature_wspecifier (str)
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
    nnet_forward_opts = nnet_fwd.NnetForwardOpts()
    nnet_forward_opts.feature_transform = feature_transform
    nnet_forward_opts.reverse_transform = reverse_transform
    nnet_forward_opts.no_softmax = no_softmax
    nnet_forward_opts.apply_log = apply_log
    nnet_forward_opts.use_gpu = use_gpu
    nnet_forward_opts.model_filename = nnet1_in
    nnet_forward_opts.feature_rspecifier = feature_rspecifier
    nnet_forward_opts.feature_wspecifier = feature_wspecifier

    return nnet_fwd.ForwardPass(nnet_forward_opts)
