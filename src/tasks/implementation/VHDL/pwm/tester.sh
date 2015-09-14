#!/bin/bash

########################################################################
# tester.sh for VHDL task pwm
# Tests the task submission, creates the error messages
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################


##########################
######## RETURNS #########
##########################
# exit 3 something is wrong with test generation
# exit 1 student solution syntax or behavior wrong
# exit 0 student solution right behavior

##########################
####### PARAMETERS #######
##########################
# $1 ... UserId
# $2 ... TaskNr
# $3 ... TaskParameters

##########################
########## PATHS #########
##########################
# src path of autosub system
autosubPath=$(pwd) 
# root path of the task itself
taskPath=$(readlink -f $0|xargs dirname)
# path for all the files that describe the created path
descPath="$autosubPath/users/$1/Task$2/desc"
#path where the testing takes place
userTaskPath="$autosubPath/users/$1/Task$2"

##########################
###### DEFINITIONS #######
##########################
zero=0
userfile="pwm_beh.vhdl"
simulationTimeout="5"

##########################
#### TEST PREPARATION ####
##########################
cd $taskPath

#generate the testbench and move testbench to user's folder
python3 scripts/generateTestBench.py $3 > $userTaskPath/pwm_tb_$1_Task$2.vhdl 

#copy the entity vhdl file for testing to user's folder
cp $descPath/pwm.vhdl $userTaskPath

#change to userTaskPath, generate space for errors
cd $userTaskPath
touch error_msg

#check if the user supplied a file
if [ ! -f $userfile ]
then
    echo "Error with Task $2. User did not attach the right file"
    cd $autosubPath
    echo "You did not attach your solution. Please attach the file $userfile" >$userTaskPath/error_msg
    exit 1 
fi

##########################
######### ANALYZE ########
##########################

#entity, not from user, should have no errors
ghdl -a pwm.vhdl
RET=$? 
if [ "$RET" -ne "$zero" ]
then
   echo "Error with Task $2 entity";
   echo "Something went wrong with the task $2 test generation. This is not your fault. We are working on a solution" > $userTaskPath/error_msg
   exit 3 
fi

#testbench, not from user, should have no errors
ghdl -a pwm_tb_$1_Task$2.vhdl
RET=$? 
if [ "$RET" -ne "$zero" ]
then
   echo "Error with Task $2 testbench";
   echo "Something went wrong with the task $2 test generation. This is not your fault. We are working on a solution" > $userTaskPath/error_msg
   exit 3 
fi

#this is the file from the user

#first strip the file of all comments for constraint check
sed -i '/^--/ d' pwm_beh.vhdl 

ghdl -a pwm_beh.vhdl 2> /tmp/tmp_Task$2_User$1
RET=$?

if [ "$RET" -eq "$zero" ]
then
   echo "Task$2 analyze success for user with ID $1!"
else
   echo "Task$2 analyze FAILED for user with ID $1!"
   cd $autosubPath
   echo "Analyzation of your submitted behavior file failed:" >$userTaskPath/error_msg
   cat /tmp/tmp_Task$2_User$1 >> $userTaskPath/error_msg
   exit 1 
fi

##########################
## TASK CONSTRAINT CHECK #
##########################
#check for the keywords after and wait
if `egrep -oq "(wait|after)" pwm_beh.vhdl`
then
   echo "Task$2 using forbiddden keywords for user with ID $1!"
   cd $autosubPath
   echo "You are not complying to the specified rules in your task discription.">$userTaskPath/error_msg
   echo "You are not using the input clock to generate your signal! You are either using the keyword 'after' or 'wait'." >>$userTaskPath/error_msg
   echo "Use counting of periods of the input clock to generate the output PWM. Do not use 'after' or 'wait' signal generation." >> $userTaskPath/error_msg
   exit 1 
fi

##########################
######## ELABORATE #######
##########################
ghdl -e pwm_tb 2>/tmp/tmp_Task$2_User$1
RET=$?

if [ "$RET" -eq "$zero" ]
then
   echo "Task$2 elaboration success for user with ID $1!"
else
   echo "Task$2 elaboration FAILED for user with ID $1!"
   cd $autosubPath
   echo "Elaboration with your submitted behavior file failed:" >$userTaskPath/error_msg
   cat /tmp/tmp_Task$2_User$1 >> $userTaskPath/error_msg
   exit 1 
fi

##########################
####### SIMULATION #######
##########################
#Simulation reports "Success" or an error message
timeout $simulationTimeout ghdl -r pwm_tb --vcd=signals.vcd 2> /tmp/tmp_Task$2_User$1
RETghdl=$?
egrep -oq "Success" /tmp/tmp_Task$2_User$1
RETegrep=$?

#make sure the error_attachments folder is empty
if [ ! -d "$userTaskPath/error_attachments" ]; 
then
   mkdir $userTaskPath/error_attachments
else
   rm -r $userTaskPath/error_attachments
   mkdir $userTaskPath/error_attachments
fi

filesize=$(stat -c%s "signals.vcd") #in Bytes

#compression factor is approx 10, so we dont wont anything above 20MB 
if [ "$filesize" -gt 20000000 ]; then 
   head --bytes=20000K signals.vcd >signals_tmp.vcd; #first x K Bytes
   rm signals.vcd
   mv signals_tmp.vcd signals.vcd  
fi

#zip the vcd and move it
zip -r wavefile.zip signals.vcd
mv wavefile.zip $userTaskPath/error_attachments

if [ "$RETegrep" -eq "$zero" ]
then
    echo "Functionally correct!"
    exit 0
elif [ "$RETghdl" -eq 124 ] #; timeout returns 124 if it had to kill process
then  
    cd $autosubPath
    echo "Wrong behavior for Task$2 for user with ID $1!"
    echo "Your submitted behavior file does not behave like specified in the task description:" >$userTaskPath/error_msg
    echo "No continuous signal detected. Please look at the attached wave file to see what signal your entity produces." >> $userTaskPath/error_msg
    exit 1  
else
    cd $autosubPath
    echo "Wrong behavior for Task$2 for user with ID $1!"
    echo "Your submitted behavior file does not behave like specified in the task description:" >$userTaskPath/error_msg
    cat /tmp/tmp_Task$2_User$1 >> $userTaskPath/error_msg
    echo "Please look at the attached wave file to see what signal your entity produces." >> $userTaskPath/error_msg
    exit 1 
fi