// pyIdlak/pylib/pyIdlak_internal.h

// Copyright 2018 CereProc Ltd.  (Authors: David Braude
//                                         Matthew Aylett)

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


#ifndef KALDI_PYIDLAK_PYLIB_PYIDLAK_INTERNAL_H_
#define KALDI_PYIDLAK_PYLIB_PYIDLAK_INTERNAL_H_

#include <cmath>
#include <string>
#include <vector>
#include <cstdio>

#include "util/simple-options.h"
#include "idlakfeat/feature-aperiodic.h"
#include "nnet/nnet-pdf-prior.h"

#include "pyIdlak_types.h"
#include "python-pylib-api.h"

/* Additional Option Types */
struct PyNnetForwardOptions {
  std::string feature_transform = "";
  bool reverse_transform = false;
  bool no_softmax = false;
  bool apply_log = false;
  std::string use_gpu = "no";
  std::string model_filename;

  void Register(kaldi::OptionsItf *opts) {
    opts->Register("feature-transform", &(feature_transform),
                   "Feature transform in front of main network (in nnet format)");
    opts->Register("reverse-transform", &(reverse_transform),
                   "Feature transform applied in reverse on output");
    opts->Register("no-softmax", &(no_softmax),
                   "Removes the last component with Softmax, if found. The pre-softmax "
                   "activations are the output of the network. Decoding them leads to "
                   "the same lattices as if we had used 'log-posteriors'.");
    opts->Register("apply-log", &(apply_log),
                   "Transform NN output by log()");
    opts->Register("use-gpu", &(use_gpu),
                   "yes|no|optional, only has effect if compiled with CUDA");
    opts->Register("model-filename", &(model_filename),
                   "Model filename");
  }
};
typedef struct PyNnetForwardOptions PyNnetForwardOptions;

struct PyApplyCMVNOptions {
  std::string utt2spk_rspecifier = "";
  bool norm_vars = false;
  bool norm_means = false;
  bool reverse = false;
  std::string skip_dims_str = "";

  void Register(kaldi::OptionsItf *opts) {
    opts->Register("utt2spk", &utt2spk_rspecifier,
                  "rspecifier for utterance to speaker map");
    opts->Register("norm-vars", &norm_vars, "If true, normalize variances.");
    opts->Register("norm-means", &norm_means, "You can set this to false to turn off mean "
                  "normalization.  Note, the same can be achieved by using 'fake' CMVN stats; "
                  "see the --fake option to compute_cmvn_stats.sh");
    opts->Register("skip-dims", &skip_dims_str, "Dimensions for which to skip "
                  "normalization: colon-separated list of integers, e.g. 13:14:15)");
    opts->Register("reverse", &reverse, "If true, apply CMVN in a reverse sense, "
                  "so as to transform zero-mean, unit-variance input into data "
                  "with the given mean and variance.");
  }
};
typedef struct PyApplyCMVNOptions PyApplyCMVNOptions;



struct PySimpleOptions {
  kaldi::SimpleOptions * po_;
  kaldi::AperiodicEnergyOptions * aprd_ = nullptr;
  kaldi::nnet1::PdfPriorOptions * pdf_prior_ = nullptr;
  PyNnetForwardOptions * nnet_fwd_ = nullptr;
  PyApplyCMVNOptions * apply_cmvn_ = nullptr;
};


struct PyIdlakBuffer {
  char * data_;
  int len_;
};

#endif // KALDI_PYIDLAK_PYLIB_PYIDLAK_INTERNAL_H_
