// pyidlak/nnet-forward/pyIdlak_nnet_forward.i

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


// Note that this is intended to be internal to py and not exposed.

%module  pyIdlak_nnet_forward

%include "std_string.i"
%include <std_vector.i>
%include <argcargv.i>
%include "typemaps.i"

namespace std {
   %template(IntVector) vector<int>;
   %template(DoubleVector) vector<double>;
   %template(StringVector) vector<string>;
   %template(ConstCharVector) vector<const char*>;
};

%typemap(in) BaseFloat = float;

%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) }

%{
#include "pyIdlak-nnet-forward.h"
%}

%include "pyIdlak-nnet-forward.h"
