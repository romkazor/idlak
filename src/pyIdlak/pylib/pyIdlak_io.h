// pyIdlak/pylib/pyIdlak_io.h

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

#ifndef KALDI_PYIDLAK_PYLIB_PYIDLAK_IO_H_
#define KALDI_PYIDLAK_PYLIB_PYIDLAK_IO_H_

#include <string>
#include <stdexcept>
#include "util/common-utils.h"
#include "pyIdlak_types.h"

// TODO: Refactor as templates then use swig templates
// TODO: Convert to Python3 generator class
typedef kaldi::Matrix<kaldi::BaseFloat> KaldiMatrixWrap_BaseFloat;
typedef kaldi::Matrix<double> KaldiMatrixWrap_Double;
typedef KaldiMatrixWrap_BaseFloat KaldiMatrixBaseFloat_list;
typedef KaldiMatrixWrap_Double    KaldiMatrixDouble_list;

class PyIdlakSequentialBaseFloatMatrixReader {
private:
  kaldi::SequentialBaseFloatMatrixReader *reader_;
public:
  PyIdlakSequentialBaseFloatMatrixReader(const std::string &rspecifier) {
    reader_ = new kaldi::SequentialBaseFloatMatrixReader(rspecifier);
  }
  ~PyIdlakSequentialBaseFloatMatrixReader() {
    delete reader_;
  }

  kaldi::Matrix<kaldi::BaseFloat> &value() {
    if (reader_->Done())
      throw std::out_of_range("Iterator has finished");
    return reader_->Value();
  }

  std::string key() {
    if (reader_->Done())
      throw std::out_of_range("Iterator has finished");
    return reader_->Key();
  }

  bool done() {
    return reader_->Done();
  }

  void next() {
    return reader_->Next();
  }
};


// TODO: Refactor as template class then use swig templates
class PyIdlakRandomAccessDoubleMatrixReader {
private:
  kaldi::RandomAccessDoubleMatrixReader *reader_;

public:
  PyIdlakRandomAccessDoubleMatrixReader(const std::string &rspecifier) {
    reader_ = new kaldi::RandomAccessDoubleMatrixReader (rspecifier);
  }

  ~PyIdlakRandomAccessDoubleMatrixReader() {
    delete reader_;
  }

  bool haskey(const std::string &key) {
    return reader_->HasKey(key);
  }

  kaldi::Matrix<double> value(const std::string &key) {
    if (!reader_->HasKey(key))
      throw std::out_of_range("key not in reader");
    return reader_->Value(key);
  }
};


// TODO: Refactor as template class then use swig templates
class PyIdlakRandomAccessDoubleMatrixReaderMapped {
private:
  kaldi::RandomAccessDoubleMatrixReaderMapped *reader_;

public:
  PyIdlakRandomAccessDoubleMatrixReaderMapped(
      const std::string &maxtrix_rspecifier, const std::string &utt2spk_rspecifier) {
    reader_ = new kaldi::RandomAccessDoubleMatrixReaderMapped (
      maxtrix_rspecifier, utt2spk_rspecifier
    );
  }
  ~PyIdlakRandomAccessDoubleMatrixReaderMapped() {
    delete reader_;
  }

  bool haskey(const std::string &key) {
    return reader_->HasKey(key);
  }

  kaldi::Matrix<double> value(const std::string &key) {
    if (!reader_->HasKey(key))
      throw std::out_of_range("key not in reader");
    return reader_->Value(key);
  }
};




class PyIdlakBaseFloatMatrixWriter {
private:
  kaldi::BaseFloatMatrixWriter *writer_;

public:
  PyIdlakBaseFloatMatrixWriter(const std::string &wspecifier) {
    writer_ = new kaldi::BaseFloatMatrixWriter(wspecifier);
  }

  ~PyIdlakBaseFloatMatrixWriter() {
    delete writer_;
  }

  void write(const std::string &key, const kaldi::Matrix<kaldi::BaseFloat> &value) {
    writer_->Write(key, value);
  }
};

kaldi::Matrix<double> PyReadKaldiDoubleMatrix(const std::string &rxfilename);


KaldiMatrixBaseFloat_list * PyKaldiMatrixBaseFloat_tolist(kaldi::Matrix<kaldi::BaseFloat> * M);
KaldiMatrixDouble_list * PyKaldiMatrixDouble_tolist(kaldi::Matrix<double> * M);
kaldi::Matrix<kaldi::BaseFloat> * PyKaldiMatrixBaseFloat_frmlist(const double * MATRIX, int m, int n);
kaldi::Matrix<double> * PyKaldiMatrixDouble_frmlist(const double * MATRIX, int m, int n);


#endif // KALDI_PYIDLAK_PYLIB_PYIDLAK_IO_H_
