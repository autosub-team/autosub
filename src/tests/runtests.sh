#!/bin/bash

TMPPY=$(echo $PYTHONPATH)
MYPATH=$(cd ../; pwd; cd tests)

export PYTHONPATH=$PYTHONPATH:$MYPATH

python3 test_autosub.py

export PYTHONPATH=$TMPPY
