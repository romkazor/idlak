// pyIdlak/pylib/pyIdlak_typemaps.i

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


// Note that this is intended to ensure all compiled moduoles use the same typemaps

%include <std_string.i>
%include <std_vector.i>
%include <argcargv.i>
%include <std_complex.i>
%include <typemaps.i>

namespace std {
   %template(IntVector) vector<int>;
   %template(DoubleVector) vector<double>;
   %template(ComplexDoubleVector) vector<std::complex<double>>;
   %template(StringVector) vector<string>;
   %template(ConstCharVector) vector<const char*>;
   %template(DoubleVectorList) vector<vector<double>>;
};

%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) }

%{
#include "matrix/matrix-lib.h"
#include "pyIdlak/pylib/pyIdlak_io.h"
%}

%include "pyIdlak_io.h"

/* base float matrix from list of list */
%typemap(in) (const double * MATRIX, int m, int n) %{
    PyObject *row;
    int m, n;

    if (!PyList_Check($input)) {
        PyErr_SetString(PyExc_ValueError, "Expecting a list of lists of numbers");
        return NULL;
    }
    row = PyList_GET_ITEM($input, 0);
    if (!PyList_Check(row)) {
        PyErr_SetString(PyExc_ValueError, "Expecting a list of lists of numbers");
        return NULL;
    }

    m = (int)PyList_Size($input);
    n = (int)PyList_Size(row);
    $1 = (double *) malloc(m * n * sizeof(double));
    $2 = m;
    $3 = n;

    for(Py_ssize_t i = 0; i < m; i++) {
        row = PyList_GET_ITEM($input, i);
        if (!PyList_Check(row)) {
            free($1);
            PyErr_SetString(PyExc_ValueError, "Expecting a list of lists of numbers");
            return NULL;
        }
        if ((int) PyList_Size(row) != n) {
            free($1);
            PyErr_SetString(PyExc_ValueError, "Row dimensions inconsistant");
            return NULL;
        }
        for(Py_ssize_t j = 0; j < n; j++) {
            PyObject *v = PyList_GET_ITEM(row, j);
            if (!PyNumber_Check(v)) {
                free($1);
                PyErr_SetString(PyExc_ValueError, "List items must be numbers");
                return NULL;
            }
            $1[i*n + j] = PyFloat_AsDouble(v);
        }
    }
%}

%typemap(freearg) (const double * MATRIX, int m, n) %{
    free($1);
%}

%typemap(out) (KaldiMatrixBaseFloat_list *)
{
  auto M = reinterpret_cast<kaldi::Matrix<kaldi::BaseFloat> *>($1);
  $result = PyList_New(M->NumRows());
  for (int i = 0; i < M->NumRows(); i++) {
    PyList_SetItem($result, i, PyList_New(M->NumCols()));
    PyObject *row = PyList_GET_ITEM($result, i);
    for (int j = 0; j < M->NumCols(); j++) {
      PyList_SetItem(row, j, PyFloat_FromDouble(M->Index(i,j)));
    }
  }
}

%typemap(out) (KaldiMatrixDouble_list *)
{
  auto M = reinterpret_cast<kaldi::Matrix<double> *>($1);
  $result = PyList_New(M->NumRows());
  for (int i = 0; i < M->NumRows(); i++) {
    PyList_SetItem($result, i, PyList_New(M->NumCols()));
    PyObject *row = PyList_GET_ITEM($result, i);
    for (int j = 0; j < M->NumCols(); j++) {
      PyList_SetItem(row, j, PyFloat_FromDouble(M->Index(i,j)));
    }
  }
}
