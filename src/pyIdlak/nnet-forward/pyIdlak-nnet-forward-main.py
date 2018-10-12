import os
import sys
import argparse
import textwrap
from nnet_forward import nnet_forward as nnet_fwd


def tobool(prop):
    if prop and prop.lower() == "true":
        prop = True
    else:
        prop = False
    return prop


def main():
    descrp = '''\
Perform forward pass through Neural Network
Usage: pyIdlak-nnet-forward-main.py [options] <nnet1-in> <feature-rspecifier> \
<feature-wspecifier>
e.g.: pyIdlak-nnet-forward-main.py final.nnet ark:input.ark ark:output.ark
'''
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=descrp,
                                     formatter_class=formatter)
    parser.add_argument('--feature-transform', help='Feature transform in ' +
                        'front of main network (in nnet format)', default='')
    parser.add_argument('--reverse-transform', help='Feature transform ' +
                        'applied in reverse on output')
    parser.add_argument('--no-softmax', help='Removes the last component ' +
                        'with Softmax, if found. The pre-softmax activations' +
                        ' are the output of the network. Decoding them ' +
                        'leads to the same lattices as if we had used ' +
                        "'log-posteriors'. in reverse on output")
    parser.add_argument('--apply-log', help='Transform NN output by log()')
    parser.add_argument('--use-gpu', help='only has effect if compiled with ' +
                        ' CUDA', choices=['no', 'yes', 'optional'],
                        default='no')
    parser.add_argument('nnet1_in', nargs=1)
    parser.add_argument('feature_rspecifier', nargs=1)
    parser.add_argument('feature_wspecifier', nargs=1)
    args = parser.parse_args()

    nnet_fwd(args.nnet1_in[0], args.feature_rspecifier[0],
             args.feature_wspecifier[0], args.feature_transform,
             tobool(args.reverse_transform), tobool(args.no_softmax),
             tobool(args.apply_log), args.use_gpu)


if __name__ == '__main__':
    main()
