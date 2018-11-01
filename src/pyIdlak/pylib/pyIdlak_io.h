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

// TODO: Convert to Python3 generator class
// TODO: Refactor as template class then use swig templates


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
    if (!reader_->Done())
      return reader_->Value();
    else
      throw std::out_of_range("Itrator has finished");
  }

  std::string key() {
    if (!reader_->Done())
      return reader_->Key();
    else
      throw std::out_of_range("Itrator has finished");
  }

  bool done() {
    return reader_->Done();
  }

  void next() {
    return reader_->Next();
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



#endif // KALDI_PYIDLAK_PYLIB_PYIDLAK_IO_H_
