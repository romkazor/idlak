# -*- coding: utf-8 -*-
# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett
#                                       David Braude)
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

# Note that this is intended to be internal to pyIdlak and not exposed.

# Utilities that do not require pyIdlak to be compiled

import collections
import re

def no_pyIdlak_parse_arkfile(fname):
    """ parses a text ark file withot the pyIdlak library
        compiled """
    ark = collections.OrderedDict()
    arkfile = open(fname).read()

    if arkfile.find('[') == -1:
        # Vector of vectors version
        try:
            vector_id = False
            for vector in arkfile.split(';'):
                values = vector.strip().split()
                if not values:
                    continue
                try:
                    float(values[0])
                except ValueError:
                    # switching to new ID
                    vector_id = values[0]
                    ark[vector_id] = [[]]
                else:
                    # switching to next vector
                    ark[vector_id].append([float(values[0])])

                if len(values) > 1:
                    for v in values[1:]:
                        try:
                            float(v)
                        except ValueError:
                            vector_id = values[0]
                            ark[vector_id] = [[]]
                        else:
                            ark[vector_id][-1].append(float(v))
        except KeyError:
            raise IOError('Ark is not correctly formated')

    else:
        # Matrix version
        repat = re.compile('(?P<id>[a-zA-Z0-9]+)\s*\[(?P<mat>.*?)\]\s*', re.S)
        for m in re.finditer(repat, arkfile):
            ark[m.group('id')] = [
                list(map(float, s.split())) for s in m.group('mat').split('\n') if len(s.strip())
            ]
    if not ark:
        raise IOError('Ark file is empty')
    return ark


def compare_arks(A_arkfn, B_arkfn, atol = 1e-3, rtol=0.):
    """ Compares two ark files, the ark files must be in text format, and
        numpy must be installed """
    try:
        import numpy as np
        A_ark = no_pyIdlak_parse_arkfile(A_arkfn)
        B_ark = no_pyIdlak_parse_arkfile(B_arkfn)

        for matid in A_ark:
            if matid not in B_ark:
                raise ValueError("Matrix ID {0} missing from B".format(matid))
            A = np.atleast_2d(np.array(A_ark[matid]))
            B = np.atleast_2d(np.array(B_ark[matid]))
            if A.shape[0] != B.shape[0]:
                raise ValueError("unequal number of rows "
                     "A: {[0]} B: {[0]}".format(A.shape, B.shape))
            if A.shape[1] != B.shape[1]:
                raise ValueError("unequal number of columns "
                     "A: {[1]} B: {[1]}".format(A.shape, B.shape))
            if not np.allclose(A, B, atol = atol, rtol=rtol):
                raise ValueError("different values")

            del B_ark[matid]
        if B_ark:
            raise ValueError("Matrix ID {0} missing from B".format(' '.join(B.keys())))
        return True

    except ImportError:
        import sys
        print("Cannot import numpy, cannot compart ark files", file = sys.stderr)


# SWIG wrapped API
try:
    from . import pyIdlak_pylib

    def get_rspecifier_keys(rspecifier):
        """ Opens an rspecifier with a PyIdlakSequentialBaseFloatMatrixReader
            and retrieves all the keys in it """
        reader = pyIdlak_pylib.PyIdlakSequentialBaseFloatMatrixReader(rspecifier)
        keys = []
        while not reader.done():
            keys.append(reader.key())
            reader.next()
        return keys

    def get_matrix_by_key(rspecifier, key):
        """ Opens an rspecifier with a PyIdlakRandomAccessDoubleMatrixReader
            and retrieves the matrix with the given key """
        reader = pyIdlak_pylib.PyIdlakRandomAccessDoubleMatrixReader(rspecifier)
        return reader.value(key)

except ImportError:
    import sys
    print("Cannot import pyIdlak_pylib, not all utilities are available", file = sys.stderr)
