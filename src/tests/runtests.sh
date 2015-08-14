#!/bin/bash

TMPPY=$(echo $PYTHONPATH)
MYPATH=$(cd ../; pwd; cd tests)

export PYTHONPATH=$PYTHONPATH:$MYPATH

#rm autosub.log

#python3 test_autosub.py

#rm autosub.log

ln -s ../SpecialMessages

python3 test_sender.py

rm -rf SpecialMessages

export PYTHONPATH=$TMPPY
