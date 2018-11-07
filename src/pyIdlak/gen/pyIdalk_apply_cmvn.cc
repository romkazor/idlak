// pyIdlak/nnet-forward/pyIdlak-nnet-forward.cc
// Copyright 2018 CereProc Ltd.  (Authors: David Braude
//                                         Matthew Aylett
//                                         Skaiste Butkute)

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

#include <vector>

#include "base/kaldi-common.h"
#include "util/common-utils.h"
#include "matrix/kaldi-matrix.h"
#include "matrix/matrix-lib.h"

#include "transform/cmvn.h"

#include "pyIdlak/pylib/pyIdlak_internal.h"
#include "python-gen-api.h"

kaldi::Matrix<kaldi::BaseFloat> * PyApplyCMVN(PySimpleOptions * pyopts,
    const kaldi::Matrix<kaldi::BaseFloat> &input,
    const kaldi::Matrix<double> &cmvn_stats) {

  auto apply_cmvn_opts = pyopts->apply_cmvn_;
  bool norm_vars = apply_cmvn_opts->norm_vars;
  bool norm_means = apply_cmvn_opts->norm_means;
  bool reverse = apply_cmvn_opts->reverse;

  auto output = new Matrix<BaseFloat>(input);

  if (!norm_means && !norm_vars) {
    // No-opt just return a copy
    return output;
  }

  Matrix<double> tmp_cmvn_stats(cmvn_stats);
  std::vector<int32> skip_dims;
  if (!kaldi::SplitStringToIntegers(apply_cmvn_opts->skip_dims_str, ":", false, &skip_dims)) {
    KALDI_ERR << "Bad --skip-dims option (should be colon-separated list of "
              << "integers)";
    throw std::invalid_argument("PyApplyCMVN called with invalid options.");
  }
  if (!skip_dims.empty())
    FakeStatsForSomeDims(skip_dims, &tmp_cmvn_stats);

  if (reverse) {
      ApplyCmvnReverse(tmp_cmvn_stats, norm_vars, output, norm_means);
  } else {
      ApplyCmvn(tmp_cmvn_stats, norm_vars, output, norm_means);
  }

  return feat;
}
