#!/bin/bash

########################################################################
# tester.sh for VHDL task gates
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
TaskNr=$2
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
userfile="gates_beh.vhdl"

TaskNr=$2
logPrefix()
{
   logPre=$(date +"%Y-%m-%d %H:%M:%S,%3N ")"[tester.sh Task$TaskNr]   "
}

##########################
#### TEST PREPARATION ####
##########################
cd $taskPath

#generate the testbench and move testbench to user's folder
python3 scripts/generateTestBench.py $3 > $userTaskPath/gates_tb_$1_Task$2.vhdl

#copy the entity vhdl file for testing to user's folder
cp $descPath/gates.vhdl $userTaskPath

#copy needed files for IEEE 1164 gates to user's folder
cp $descPath/IEEE_1164_Gates_pkg.vhdl $userTaskPath
cp $descPath/IEEE_1164_Gates_beh.vhdl $userTaskPath
cp $descPath/IEEE_1164_Gates.vhdl $userTaskPath

#change to userTaskPath, generate space for errors
cd $userTaskPath
touch error_msg

#check if the user supplied a file
if [ ! -f $userfile ]
then
    logPrefix && echo "${logPre}Error with Task $2. User $1 did not attach the right file"
    cd $autosubPath
    echo "You did not attach your solution. Please attach the file $userfile" >$userTaskPath/error_msg
    exit 1 
fi

#############################################
################### ANALYZE #################
#############################################

#entity, not from user, should have no errors
ghdl -a gates.vhdl
RET=$? 
if [ "$RET" -ne "$zero" ]
then
   logPrefix && echo "${logPre}Error with Task $2 entity for user with ID $1";
   echo "Something went wrong with the task $2 test generation. This is not your fault. We are working on a solution" > $userTaskPath/error_msg
   exit 3 
fi

#testbench, not from user, should have no errors
ghdl -a gates_tb_$1_Task$2.vhdl
RET=$? 
if [ "$RET" -ne "$zero" ]
then
   logPrefix && echo "${logPre}Error with Task$2 testbench for user with ID $1";
   echo "Something went wrong with the task $2 test generation. This is not your fault. We are working on a solution" > $userTaskPath/error_msg
   exit 3 
fi

#IEEE 1164 Gates package, not from user, should have no errors
ghdl -a IEEE_1164_Gates_pkg.vhdl
RET=$? 
if [ "$RET" -ne "$zero" ]
then
   logPrefix && echo "${logPre}Error with Task$2 IEEE_1164_Gates pkg for user with ID $1";
   echo "Something went wrong with the task $2 test generation. This is not your fault. We are working on a solution" > $userTaskPath/error_msg
   exit 3 
fi

#IEEE 1164 Gates entities, not from user, should have no errors
ghdl -a IEEE_1164_Gates.vhdl
RET=$? 
if [ "$RET" -ne "$zero" ]
then
   logPrefix && echo "${logPre}Error with Task$2 IEEE_1164_Gates entities for user with ID $1";
   echo "Something went wrong with the task $2 test generation. This is not your fault. We are working on a solution" > $userTaskPath/error_msg
   exit 3 
fi

#IEEE 1164 Gates behaviors, not from user, should have no errors
ghdl -a IEEE_1164_Gates_beh.vhdl
RET=$? 
if [ "$RET" -ne "$zero" ]
then
   logPrefix && echo "${logPre}Error with Task$2 IEEE_1164_Gates behavior for user with ID $1";
   echo "Something went wrong with the task $2 test generation. This is not your fault. We are working on a solution" > $userTaskPath/error_msg
   exit 3 
fi


#this is the file from the user

#first strip the file of all comments for constraint check
sed -i '/^--/ d' gates_beh.vhdl 

ghdl -a gates_beh.vhdl 2> /tmp/tmp_Task$2_User$1
RET=$?

if [ "$RET" -eq "$zero" ]
then
   logPrefix && echo "${logPre}Task$2 analyze success for Task$2 for user with ID $1!"
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
#check if  the user really uses the provided IEEE 1164 entities
#look for the entity names NAND, AND, OR, NOR, XOR, XNOR; smallest search is for AND<N> and OR<N>; vhdl is not case sensitive
#user needs 5 gates to build the network

numgates=$(egrep -o "([Aa][Nn][Dd][2-4]|[Oo][Rr][2-4])" gates_beh.vhdl | wc -l)
aimednum=5

if [ "$numgates" -ne "$aimednum" ]
then
   logPrefix && echo "${logPre}Task$2 not using the provided gate entities for user with ID $1!"
   cd $autosubPath
   echo "You are not complying to the specified rules in your task discription.">$userTaskPath/error_msg
   echo "You are not using the provided IEEE 1164 gate entities." >>$userTaskPath/error_msg
   echo "Use the provided entities to build a gate network with the specified behavior." >> $userTaskPath/error_msg
   exit 1 
fi

##########################
######## ELABORATE #######
##########################
ghdl -e gates_tb 2>/tmp/tmp_Task$2_User$1
RET=$?

if [ "$RET" -eq "$zero" ]
then
   logPrefix && echo "${logPre}Task$2 elaboration success for user with ID $1!"
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
ghdl -r gates_tb 2> /tmp/tmp_Task$2_User$1

egrep -oq "Success" /tmp/tmp_Task$2_User$1
RET=$?

if [ "$RET" -eq "$zero" ]
then
    logPrefix && echo "${logPre}Functionally correct for Task$2 for user with ID $1!"
    exit 0
else
   cd $autosubPath
   logPrefix && echo "${logPre}Wrong behavior for Task$2 for user with ID $1"
   echo "Your submitted behavior file does not behave like specified in the task description:" >$userTaskPath/error_msg
   cat /tmp/tmp_Task$2_User$1 >> $userTaskPath/error_msg
   exit 1 
fi

