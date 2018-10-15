// pyIdlak/pylib/python-pylib-api.cc

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

#include "pyIdlak-nnet-forward.h"


int ForwardPass(NnetForwardOpts * opts) {
  using namespace kaldi;
  using namespace kaldi::nnet1;
  try {
    using namespace kaldi;
    using namespace kaldi::nnet1;
    typedef kaldi::int32 int32;

    PdfPriorOptions prior_opts;
    prior_opts.class_frame_counts = opts->class_frame_counts;
    prior_opts.prior_scale = opts->prior_scale;
    prior_opts.prior_floor = opts->prior_floor;

    // check if required parameters are provided
    if (opts->model_filename.empty()) {
        KALDI_ERR << "Argument model_filename is missing or is empty";
    }
    if (opts->feature_rspecifier.empty()) {
        KALDI_ERR << "Argument feature_rspecifier is missing or is empty";
    }
    if (opts->feature_wspecifier.empty()) {
        KALDI_ERR << "Argument feature_wspecifier is missing or is empty";
    }
    // Select the GPU
#if HAVE_CUDA == 1
    CuDevice::Instantiate().SelectGpuId(opts->use_gpu);
#endif

    Nnet nnet_transf;
    if (opts->feature_transform != "") {
      nnet_transf.Read(opts->feature_transform);
    }

    Nnet nnet;
    nnet.Read(opts->model_filename);
    // optionally remove softmax,
    Component::ComponentType last_comp_type = nnet.GetLastComponent().GetType();
    if (opts->no_softmax) {
      if (last_comp_type == Component::kSoftmax ||
          last_comp_type == Component::kBlockSoftmax) {
        KALDI_LOG << "Removing " << Component::TypeToMarker(last_comp_type)
                  << " from the nnet " << opts->model_filename;
        nnet.RemoveLastComponent();
      } else {
        KALDI_WARN << "Last component 'NOT-REMOVED' by --no-softmax=true, "
          << "the component was " << Component::TypeToMarker(last_comp_type);
      }
    }

    // avoid some bad option combinations,
    if (opts->apply_log && opts->no_softmax) {
      KALDI_ERR << "Cannot use both --apply-log=true --no-softmax=true, "
                << "use only one of the two!";
    }

    // we will subtract log-priors later,
    PdfPrior pdf_prior(prior_opts);

    // disable dropout,
    nnet_transf.SetDropoutRate(0.0);
    nnet.SetDropoutRate(0.0);

    kaldi::int64 tot_t = 0;

    SequentialBaseFloatMatrixReader feature_reader(opts->feature_rspecifier);
    BaseFloatMatrixWriter feature_writer(opts->feature_wspecifier);

    CuMatrix<BaseFloat> feats, feats_transf, nnet_out;
    Matrix<BaseFloat> nnet_out_host;

    Timer time;
    double time_now = 0;
    int32 num_done = 0;

    // main loop,
    for (; !feature_reader.Done(); feature_reader.Next()) {
      // read
      Matrix<BaseFloat> mat = feature_reader.Value();
      std::string utt = feature_reader.Key();
      KALDI_VLOG(2) << "Processing utterance " << num_done+1
                    << ", " << utt
                    << ", " << mat.NumRows() << "frm";


      if (!KALDI_ISFINITE(mat.Sum())) {  // check there's no nan/inf,
        KALDI_ERR << "NaN or inf found in features for " << utt;
      }

      // push it to gpu,
      feats = mat;

      // fwd-pass, feature transform,
      if (!opts->reverse_transform) {
          nnet_transf.Feedforward(feats, &feats_transf);
          if (!KALDI_ISFINITE(feats_transf.Sum())) {  // check there's no nan/inf,
              KALDI_ERR << "NaN or inf found in transformed-features for " << utt;
          }

          // fwd-pass, nnet,
          nnet.Feedforward(feats_transf, &nnet_out);
          if (!KALDI_ISFINITE(nnet_out.Sum())) {  // check there's no nan/inf,
              KALDI_ERR << "NaN or inf found in nn-output for " << utt;
          }
      }
      else {
          nnet.Feedforward(feats, &feats_transf);
          if (!KALDI_ISFINITE(feats_transf.Sum())) {  // check there's no nan/inf,
              KALDI_ERR << "NaN or inf found in transformed-features for " << utt;
          }

          // fwd-pass, nnet,
          nnet_transf.Feedforward(feats_transf, &nnet_out);
          if (!KALDI_ISFINITE(nnet_out.Sum())) {  // check there's no nan/inf,
              KALDI_ERR << "NaN or inf found in nn-output for " << utt;
          }
      }

      // convert posteriors to log-posteriors,
      if (opts->apply_log) {
        if (!(nnet_out.Min() >= 0.0 && nnet_out.Max() <= 1.0)) {
          KALDI_WARN << "Applying 'log()' to data which don't seem to be "
                     << "probabilities," << utt;
        }
        nnet_out.Add(1e-20);  // avoid log(0),
        nnet_out.ApplyLog();
      }

      // subtract log-priors from log-posteriors or pre-softmax,
      if (prior_opts.class_frame_counts != "") {
        pdf_prior.SubtractOnLogpost(&nnet_out);
      }

      // download from GPU,
      nnet_out_host = Matrix<BaseFloat>(nnet_out);

      // write,
      if (!KALDI_ISFINITE(nnet_out_host.Sum())) {  // check there's no nan/inf,
        KALDI_ERR << "NaN or inf found in final output nn-output for " << utt;
      }
      feature_writer.Write(feature_reader.Key(), nnet_out_host);

      // progress log,
      if (num_done % 100 == 0) {
        time_now = time.Elapsed();
        KALDI_VLOG(1) << "After " << num_done << " utterances: time elapsed = "
                      << time_now/60 << " min; processed " << tot_t/time_now
                      << " frames per second.";
      }
      num_done++;
      tot_t += mat.NumRows();
    }

    // final message,
    KALDI_LOG << "Done " << num_done << " files"
              << " in " << time.Elapsed()/60 << "min,"
              << " (fps " << tot_t/time.Elapsed() << ")";

#if HAVE_CUDA == 1
    if (GetVerboseLevel() >= 1) {
      CuDevice::Instantiate().PrintProfile();
    }
#endif

    if (num_done == 0) return -1;
    return 0;
  } catch(const std::exception &e) {
    std::cerr << e.what();
    return -1;
  }
}
