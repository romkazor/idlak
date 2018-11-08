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

#include <cfloat>
#include <string>
#include <stdexcept>

#include "base/kaldi-common.h"
#include "util/common-utils.h"
#include "cudamatrix/cu-matrix.h"
#include "cudamatrix/cu-vector.h"
#include "nnet/nnet-nnet.h"
#include "nnet/nnet-loss.h"
#include "nnet/nnet-pdf-prior.h"

#include "pyIdlak/pylib/pyIdlak_internal.h"
#include "matrix/matrix-lib.h"
#include "python-gen-api.h"


// Maybe would be better to pass the Neural net as a parameter, but there may
// changes made to the NNet in the forward call.

kaldi::Matrix<kaldi::BaseFloat> * PyGenNnetForwardPass(PySimpleOptions * pyopts,
    const kaldi::Matrix<kaldi::BaseFloat> &input) {
  try {
    using namespace kaldi;
    using namespace kaldi::nnet1;
    typedef kaldi::int32 int32;

    auto prior_opts = pyopts->pdf_prior_;
    auto nnet_fwd_opts = pyopts->nnet_fwd_;

    // check if required parameters are provided
    bool option_err = false;
    if (!prior_opts) {
      KALDI_ERR << "PySimpleOptions does not have PdfPriorOptions registered";
      option_err = true;
    }
    if (!nnet_fwd_opts) {
      KALDI_ERR << "PySimpleOptions does not have NnetForwardOptions registered";
      option_err = true;
    }
    if (nnet_fwd_opts->model_filename.empty()) {
      KALDI_ERR << "Argument model_filename is missing or is empty";
      option_err = true;
    }
    if (option_err)
      throw std::invalid_argument("PyGenNnetForwardPass called with invalid options.");

    // Select the GPU
#if HAVE_CUDA == 1
    CuDevice::Instantiate().SelectGpuId(nnet_fwd_opts->use_gpu);
#endif

    Nnet nnet_transf;
    if (nnet_fwd_opts->feature_transform != "") {
      nnet_transf.Read(nnet_fwd_opts->feature_transform);
    }

    Nnet nnet;
    nnet.Read(nnet_fwd_opts->model_filename);
    // optionally remove softmax,
    Component::ComponentType last_comp_type = nnet.GetLastComponent().GetType();
    if (nnet_fwd_opts->no_softmax) {
      if (last_comp_type == Component::kSoftmax ||
        last_comp_type == Component::kBlockSoftmax) {
          KALDI_LOG << "Removing " << Component::TypeToMarker(last_comp_type)
          << " from the nnet " << nnet_fwd_opts->model_filename;
          nnet.RemoveLastComponent();
      } else {
        KALDI_WARN << "Last component 'NOT-REMOVED' by --no-softmax=true, "
          << "the component was " << Component::TypeToMarker(last_comp_type);
      }
    }

    // avoid some bad option combinations,
    if (nnet_fwd_opts->apply_log && nnet_fwd_opts->no_softmax) {
      KALDI_ERR << "Cannot use both --apply-log=true --no-softmax=true, "
        << "use only one of the two!";
      throw std::invalid_argument("PyGenNnetForwardPass called with invalid options.");
    }

    // we will subtract log-priors later,
    PdfPrior pdf_prior(*prior_opts);

    // disable dropout,
    nnet_transf.SetDropoutRate(0.0);
    nnet.SetDropoutRate(0.0);

    CuMatrix<BaseFloat> feats, feats_transf, nnet_out;


    Timer time;

    KALDI_VLOG(2) << "Processing " << input.NumRows() << "frames";


    if (!KALDI_ISFINITE(input.Sum())) {  // check there's no nan/inf,
      KALDI_ERR << "NaN or inf found in features";
    }

    // push it to gpu,
    feats = input;

    // fwd-pass, feature transform,
    if (!nnet_fwd_opts->reverse_transform) {
      nnet_transf.Feedforward(feats, &feats_transf);
      if (!KALDI_ISFINITE(feats_transf.Sum())) {  // check there's no nan/inf,
        KALDI_ERR << "NaN or inf found in transformed-features";
      }

      // fwd-pass, nnet,
      nnet.Feedforward(feats_transf, &nnet_out);
      if (!KALDI_ISFINITE(nnet_out.Sum())) {  // check there's no nan/inf,
        KALDI_ERR << "NaN or inf found in nn-output for";
      }
    } else {
      nnet.Feedforward(feats, &feats_transf);
      if (!KALDI_ISFINITE(feats_transf.Sum())) {  // check there's no nan/inf,
        KALDI_ERR << "NaN or inf found in transformed-features";
      }

      // fwd-pass, nnet,
      nnet_transf.Feedforward(feats_transf, &nnet_out);
      if (!KALDI_ISFINITE(nnet_out.Sum())) {  // check there's no nan/inf,
        KALDI_ERR << "NaN or inf found in nn-output";
      }
    }

    // convert posteriors to log-posteriors,
    if (nnet_fwd_opts->apply_log) {
      if (!(nnet_out.Min() >= 0.0 && nnet_out.Max() <= 1.0)) {
        KALDI_WARN << "Applying 'log()' to data which don't seem to be probabilities.";
      }
      nnet_out.Add(1e-20);  // avoid log(0),
      nnet_out.ApplyLog();
    }

    // subtract log-priors from log-posteriors or pre-softmax,
    if (prior_opts->class_frame_counts != "") {
      pdf_prior.SubtractOnLogpost(&nnet_out);
    }

    // download from GPU,
    auto output = new Matrix<BaseFloat>(nnet_out);

    // write,
    if (!KALDI_ISFINITE(output->Sum())) {  // check there's no nan/inf,
      KALDI_ERR << "NaN or inf found in final output nn-output";
      delete output;
      return nullptr;
    }

    // progress log,
    double time_now = time.Elapsed();
    KALDI_VLOG(1) << "Time elapsed = " << time_now/60 << " min; "
      << input.NumRows()/time_now << " frames per second.";

#if HAVE_CUDA == 1
    if (GetVerboseLevel() >= 1) {
      CuDevice::Instantiate().PrintProfile();
    }
#endif
    return output;
  } catch(const std::exception &e) {
    std::cerr << e.what();
    return nullptr;
  }
}
