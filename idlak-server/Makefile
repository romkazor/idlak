
all:

SHELL := /bin/bash
PYTHONPATH := $(PYTHONPATH):$(CURDIR)/venv/lib64/python3.6/site-packages/

ADDLIBS = ../src/pyIdlak/_pyIdlak.a

include ../src/makefiles/default_rules.mk

source setup-server.sh
python ./testing/integrationtest.py
rm testing/test.db
rm -rf venv
