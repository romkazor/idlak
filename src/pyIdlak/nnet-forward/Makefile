include ../../kaldi.mk

ifeq ($(PYIDLAK), true)

OBJFILES = pyIdlak-nnet-forward.o pyIdlak_nnet_forward_wrap.o

LIBNAME = _pyIdlak_nnet_forward

ADDLIBS = ../../nnet/kaldi-nnet.a ../../cudamatrix/kaldi-cudamatrix.a \
		  ../../lat/kaldi-lat.a ../../hmm/kaldi-hmm.a ../../tree/kaldi-tree.a \
          ../../util/kaldi-util.a \
          ../../matrix/kaldi-matrix.a ../../base/kaldi-base.a

EXTRA_CXXFLAGS = -fPIC -I$(PYTHONDEVINC) -I$(PCREROOT)/include -I$(EXPATROOT)/include -I$(PUJIXMLROOT)/src -I../..
EXTRA_LDLIBS = -Wl,-rpath,"$(PCREROOT)/lib" $(PCREROOT)/lib/libpcre.so $(EXPATROOT)/lib/libexpat.so

ifeq ($(PYTHONDEVLIBDIR),)
  PYLIBFLAG = -l$(PYTHONDEVLIB)
else
  PYLIBFLAG = -L$(PYTHONDEVLIBDIR) -l$(PYTHONDEVLIB)
endif
EXTRA_LDLIBS += $(PYLIBFLAG)

include ../../makefiles/default_rules.mk

ifeq ($(KALDI_FLAVOR), dynamic)
  STATICLIB =
else
  STATICLIB = _pyIdlak_nnet_forward.a
endif

.PHONY: wrapper
wrapper:
	$(SWIG) -c++ -python -o pyIdlak_nnet_forward_wrap.cc pyIdlak-nnet-forward.i
pyIdlak_nnet_forward_wrap.o: wrapper

sharedlib: $(STATICLIB)
ifeq ($(KALDI_FLAVOR), dynamic)
  ifeq ($(shell uname), Darwin)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_nnet_forward.dylib _pyIdlak_nnet_forward.dylib
  else ifeq ($(shell uname), Linux)
	ln -fs $(KALDILIBDIR)/lib_pyIdlak_nnet_forward.so _pyIdlak_nnet_forward.so
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
else
  ifeq ($(shell uname), Darwin)
	$(CXX) -dynamiclib -o _pyIdlak_nnet_forward.dylib -install_name @rpath/_pyIdlak_nnet_forward.a $(LDFLAGS) $(LDLIBS)
  else ifeq ($(shell uname), Linux)
	# Building shared library from static (static was compiled with -fPIC)
	$(CXX) -shared -o _pyIdlak_pylib.so -Wl,--no-undefined -Wl,--as-needed \
		-Wl,-soname=_pyIdlak_nnet_forward.so,--whole-archive _pyIdlak_nnet_forward.a $(ADDLIBS) $(PUJIXMLROOT)/scripts/libpugixml.a -Wl,--no-whole-archive $(LDFLAGS) $(LDLIBS)
  else  # Platform not supported
	$(error Dynamic libraries not supported on this platform '$(shell uname)'. Python wrapper cannot be built.)
  endif
endif

clean_wrapper:
	-rm -rf pyIdlak_nnet_forward.py pyIdlak_nnet_forward.pyc pyIdlak_nnet_forward_wrap.cc *.pyc __pycache__
	@echo "REQUIRED FOR MAKE DO NOT DELETE!" > pyIdlak_nnet_forward_wrap.cc

clean: clean_wrapper

all: sharedlib

endif # PYIDLAK
