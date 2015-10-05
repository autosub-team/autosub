#!/bin/bash

nosetests3 --nologcapture -s -v tests/test_sender.py #this creates all needed dbs!
nosetests3 --nologcapture -s -v tests/

#cleanup
rm -r users
rm -r __pycache__
rm autosub.log
rm autosub.stdout
rm autosub.stderr
rm semester.db
rm course.db
rm testsemester.db
rm testcourse.db
