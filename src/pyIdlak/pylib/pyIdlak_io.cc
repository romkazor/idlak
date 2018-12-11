// pyIdlak/pylib/pyIdlak_io.cc

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

// TODO: Replace with template Class

#include "util/kaldi-io.h"
#include "pyIdlak_io.h"

kaldi::Matrix<double> PyReadKaldiDoubleMatrix(const std::string &rxfilename) {
  bool binary;
  kaldi::Input ki(rxfilename, &binary);
  kaldi::Matrix<double> output;
  output.Read(ki.Stream(), binary);
  return output;
}

KaldiMatrixBaseFloat_list * PyKaldiMatrixBaseFloat_tolist(kaldi::Matrix<kaldi::BaseFloat> * M) {
  return reinterpret_cast<KaldiMatrixBaseFloat_list *>(M);
}

KaldiMatrixDouble_list * PyKaldiMatrixDouble_tolist(kaldi::Matrix<double> * M) {
  return reinterpret_cast<KaldiMatrixDouble_list *>(M);
}

kaldi::Matrix<kaldi::BaseFloat> * PyKaldiMatrixBaseFloat_frmlist(const double * MATRIX, int m, int n) {
    int i, j;
    kaldi::Matrix<kaldi::BaseFloat> * kaldimat = new kaldi::Matrix<kaldi::BaseFloat>(m, n);
    for (i = 0; i < m; i++) {
        for (j = 0; j < n; j++) {
            kaldimat->operator()(i,j) = MATRIX[i*n + j];
        }
    }
    return kaldimat;
}

kaldi::Matrix<double> * PyKaldiMatrixDouble_frmlist(const double * MATRIX, int m, int n) {
    int i, j;
    kaldi::Matrix<double> * kaldimat = new kaldi::Matrix<double>(m, n);
    for (i = 0; i < m; i++) {
        for (j = 0; j < n; j++) {
            kaldimat->operator()(i,j) = MATRIX[i*n + j];
        }
    }
    return kaldimat;
}
