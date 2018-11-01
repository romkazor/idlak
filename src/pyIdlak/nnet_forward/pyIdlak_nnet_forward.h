// pyIdlak/nnet_forward/pyIdlak_nnet_forward.h

// Copyright 2018 CereProc Ltd.  (Authors: Skaiste Butkute)

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

#ifndef KALDI_PYIDLAK_NNET_FORWARD_PYTHON_NNET_FORWARD_API_H_
#define KALDI_PYIDLAK_NNET_FORWARD_PYTHON_NNET_FORWARD_API_H_


#include <limits>

#include "nnet/nnet-nnet.h"
#include "nnet/nnet-loss.h"
#include "nnet/nnet-pdf-prior.h"
#include "base/kaldi-common.h"
#include "util/common-utils.h"
#include "base/timer.h"

typedef struct PyNnetForwardOpts PyNnetForwardOpts;

int ForwardPass(PyNnetForwardOpts * opts);

struct PyNnetForwardOpts {
    std::string class_frame_counts = "";
    BaseFloat prior_scale = 1.0;
    BaseFloat prior_floor = 1e-10;
    std::string feature_transform = "";
    bool reverse_transform = false;
    bool no_softmax = false;
    bool apply_log = false;
    std::string use_gpu = "no";
    std::string model_filename;
    std::string feature_rspecifier;
    std::string feature_wspecifier;
};

#endif // KALDI_PYIDLAK_NNET_FORWARD_PYTHON_NNET_FORWARD_API_H_
