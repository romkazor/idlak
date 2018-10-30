// pyIdlak/vocoder/python-gen-api.h

// Copyright 2018 CereProc Ltd.  (Authors: David Braude)


// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
// THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
// WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
// MERCHANTABLITY OR NON-INFRINGEMENT.
// See the Apache 2 License for the specific language governing permissions and
// limitations under the License.
//


#ifndef KALDI_PYIDLAK_GEN_PYTHON_GEN_API_H_
#define KALDI_PYIDLAK_GEN_PYTHON_GEN_API_H_

#include "pyIdlak/pylib/pyIdlak_types.h"

/* Not all the forward options have not been placed into a struct
   within Kaldi */
typedef struct PyNnetForwardOpts PyNnetForwardOpts;
PyNnetForwardOpts * PyGenNnetNewForwardOpts();
void PyGenNnetRegisterForwardOpts(PySimpleOptions * pyopts, PyNnetForwardOpts * nnet_fwd_opts);
void PyGenNnetDeleteForwardOpts(PyNnetForwardOpts * nnet_fwd_opts);
int PyGenNnetForwardPass(PySimpleOptions * pyopts, PyNnetForwardOpts * nnet_fwd_opts);

#endif // KALDI_PYIDLAK_GEN_PYTHON_GEN_API_H_
