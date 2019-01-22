SHELL := /bin/bash
PYTHONPATH := $(PYTHONPATH):$(CURDIR)/venv/lib64/python3.6/site-packages/


idlak-server-test:
	source setup-server.sh
	python ./testing/integrationtest.py
	rm testing/test.db
	rm -rf venv
