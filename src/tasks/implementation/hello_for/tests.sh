#!/bin/bash

cd users/$1/Task$2

if [ ! -f ../../../tasks/task$2/checkpatch.pl ]
then
	echo "Downloading checkpatch, since it does not exist!"
	wget -v http://raw.githubusercontent.com/torvalds/linux/master/scripts/checkpatch.pl
	wget -v https://raw.githubusercontent.com/torvalds/linux/master/scripts/spelling.txt
	mv checkpatch.pl ../../../tasks/task$2/checkpatch.pl
	chmod a+x ../../../tasks/task$2/checkpatch.pl
	mv spelling.txt ../../../tasks/task$2/spelling.txt
fi

zero=0
flip -u * #change all files that might be in DOS format to UNIX format
OUTPUT=$(../../../tasks/task$2/./checkpatch.pl -f --no-tree hello.c > error_msg)
RET=$?

if [ "$RET" -eq "$zero" ]
then
   echo "Test Passed!"
else
   echo "Test Failed!"
   cd -
   exit 1 
fi

make -f ../../../tasks/task$2/Makefile 2> /tmp/tmp_Task$2_User$1
RET=$?

zero=0
if [ "$RET" -eq "$zero" ]
then
   echo "Task$2 compiled for user with ID $1!"
else
   echo "Compiling Task$2 FAILED for user with ID $1!"
   cd -
   echo "Failed to compile your submitted source:\n" > users/$1/Task$2/error_msg
   cat /tmp/tmp_Task$2_User$1 >> users/$1/Task$2/error_msg
   exit 1 
fi
 
./hello -i 42 | egrep -o '[0-9]*' | python ../../../tasks/task$2/./test_iterations.py -i 42 > error_msg
RET=$?

zero=0
if [ "$RET" -eq "$zero" ]
then
   echo "Test Passed!"
else
   echo "Functional test failed with '-i 42'"
   echo "Functional test failed with '-i 42'" >> error_msg
   cd -
   exit 1 
fi

./hello -i 42 -r | egrep -o '[0-9]*' | python ../../../tasks/task$2/./test_iterations.py -i 42 -r > error_msg
RET=$?

zero=0
if [ "$RET" -eq "$zero" ]
then
   echo "Test Passed!"
else
   echo "Functional test failed with '-i 42 -r'"
   echo "Functional test failed with '-i 42 -r'" >> error_msg
   cd -
   exit 1 
fi

./hello -r -i 42 | egrep -o '[0-9]*' | python ../../../tasks/task$2/./test_iterations.py -i 42 -r > error_msg
RET=$?

zero=0
if [ "$RET" -eq "$zero" ]
then
   echo "Test Passed!"
else
   echo "Functional test failed with '-r -i 42'"
   echo "Functional test failed with '-r -i 42'" >> error_msg
   cd -
   exit 1 
fi


./hello -i 258 -r | egrep -o '[0-9]*' | python ../../../tasks/task$2/./test_iterations.py -i 258 -r > error_msg
RET=$?

zero=0
if [ "$RET" -eq "$zero" ]
then
   echo "Test Passed!"
else
   echo "Functional test failed with '-i 258 -r'"
   echo "Functional test failed with '-i 258 -r'" >> error_msg
   cd -
   exit 1 
fi

