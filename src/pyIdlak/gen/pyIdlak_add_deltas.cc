// pyIdlak/gen/pyIdlak_add_deltas.cc
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

kaldi::Matrix<kaldi::BaseFloat> * PyAddDeltas(PySimpleOptions * pyopts,
    const kaldi::Matrix<kaldi::BaseFloat> &input) {

  if (!pyopts)
    throw std::invalid_argument("PyAddDeltas called without options.");
  auto add_deltas_opts = pyopts->add_deltas_;
  if (!add_deltas_opts) {
    KALDI_ERR << "PySimpleOptions does not have DeltaFeaturesOptions registered";
    throw std::invalid_argument("PyAddDeltas called with invalid options.");
  }

  kaldi::int32 truncate = static_cast<kaldi::int32>(pyopts->extra_int_["truncate"]);

  if (!input.NumRows()) {
    KALDI_WARN << "PyAddDeltas called with empty input matrix";
    auto output = new kaldi::Matrix<kaldi::BaseFloat>(input);
    return output;
  }

  auto output = new kaldi::Matrix<kaldi::BaseFloat>;
  if (truncate != 0) {
    if (truncate > input.NumCols()) {
      KALDI_ERR << "PyAddDeltas cannot truncate features as dimension " << input.NumCols()
                << " is smaller than truncation dimension.";
      delete output;
      return nullptr;
    }
    kaldi::SubMatrix<kaldi::BaseFloat> feats_sub(input, 0, input.NumRows(), 0, truncate);
    kaldi::ComputeDeltas(*add_deltas_opts, feats_sub, output);
  } else {
    kaldi::ComputeDeltas(*add_deltas_opts, input, output);
  }

  return output;
}
