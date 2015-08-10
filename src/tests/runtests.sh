#!/bin/bash

TMPPY=$(echo $PYTHONPATH)
MYPATH=$(cd ../; pwd; cd tests)

export PYTHONPATH=$PYTHONPATH:$MYPATH

rm autosub.log

python3 test_autosub.py

rm autosub.log

python3 test_fetcher.py

export PYTHONPATH=$TMPPY
