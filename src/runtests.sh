#!/bin/bash

nosetests3 --with-doctest --doctest-extension=txt --nologcapture -s -v tests/test_sender.py #this creates all needed dbs!
nosetests3 --with-doctest --doctest-extension=txt --nologcapture -s -v tests/

#cleanup
rm -rf users
rm -rf __pycache__
rm -f autosub.log
rm -f autosub.stdout
rm -f autosub.stderr
rm -f semester.db
rm -f course.db
rm -f testsemester.db
rm -f testcourse.db

rm -rf /tmp/test_logfile
