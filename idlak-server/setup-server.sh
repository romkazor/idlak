#!/bin/bash
set -v
TOREPLACE="from pip import main"
REPLACETO="from pip._internal import main"

virtualenv -p python3 venv
source venv/bin/activate
replace "$TOREPLACE" "$REPLACETO" -- venv/bin/pip3
venv/bin/python3 -m pip install -r requirements.txt
export FLASK_APP=runserver.py
set +v
