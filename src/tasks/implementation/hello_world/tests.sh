#!/bin/bash

cd users/$1/Task$2
touch error_msg

zero=0
# Naive scan for security issues:
grep -R --exclude-dir=Task$2_* 'wget' * > /tmp/tmp_Task$2_User$1
RET=$?
if [ "$RET" -eq "$zero" ]
then
   echo "FAILED to pass SecCheck1 for user with ID $1!"
   cd -
   echo "Your code failed your security checks - What ary you trying to do!??\n Sorry, but I really have to report this to my masters..." > users/$1/Task$2/error_msg
   cat /tmp/tmp_Task$2_User$1 >> users/$1/Task$2/error_msg
   exit 2
fi

grep -R --exclude-dir=Task$2_* 'netcat' * > /tmp/tmp_Task$2_User$1
RET=$?
if [ "$RET" -eq "$zero" ]
then
   echo "FAILED to pass SecCheck2 for user with ID $1!"
   cd -
   echo "Your code failed your security checks - What ary you trying to do!??\n Sorry, but I really have to report this to my masters..." > users/$1/Task$2/error_msg
   cat /tmp/tmp_Task$2_User$1 >> users/$1/Task$2/error_msg
   exit 2 
fi

grep -R --exclude-dir=Task$2_* 'exec' * > /tmp/tmp_Task$2_User$1
RET=$?
if [ "$RET" -eq "$zero" ]
then
   echo "FAILED to pass SecCheck3 for user with ID $1!"
   cd -
   echo "Your code failed your security checks - What ary you trying to do!??\n Sorry, but I really have to report this to my masters..." > users/$1/Task$2/error_msg
   cat /tmp/tmp_Task$2_User$1 >> users/$1/Task$2/error_msg
   exit 2
fi

# now take an actuall look at the code:
make -f ../../../tasks/task$2/Makefile 2> /tmp/tmp_Task$2_User$1
RET=$?

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
 
OUTPUT=$(./hello)

echo $OUTPUT

cd -

if echo $OUTPUT | egrep -q "[Hh][Ee][Ll][Ll][Oo][,]* [Ww][Oo][Rr][Ll][Dd][!]*" ;
then
   echo "Functionally correct!"
   exit 0
else
   echo "Your program should print the Message 'Hello World' to the console. The output
         produced by your program is: $OUTPUT" > users/$1/Task$2/error_msg
   exit 1 
fi
