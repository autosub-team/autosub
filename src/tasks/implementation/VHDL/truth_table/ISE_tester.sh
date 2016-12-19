#!/bin/bash

######################################################################################
# tester.sh for VHDL task truth_table
# Tests the task submission, creates the error messages
#
# Copyright (C) 2015, 2016 Martin  Mosbeck   <martin.mosbeck@gmx.at> , Gilbert Markum
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
######################################################################################


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
userfile="truth_table_beh.vhdl"

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
python3 scripts/generateTestBench.py $3 > $userTaskPath/truth_table_tb_$1_Task$2.vhdl

#------ SAVE USED TESTBENCH FOR DEBUGGING ------ #

#  create used_tbs directory
if [ ! -d "$userTaskPath/used_tbs" ]
then
   mkdir $userTaskPath/used_tbs
fi

#find last submission number
submissionNrs=($(ls $userTaskPath | grep -oP '(?<=Submission)[0-9]+' | sort -nr))
submissionNrLast=${submissionNrs[0]}

#copy used testbench
cp $userTaskPath/truth_table_tb_$1_Task$2.vhdl $userTaskPath/used_tbs/truth_table_tb_$1_Task$2_Submission${submissionNrLast}.vhdl

#--------------------------------------------------#

#copy the entity vhdl file for testing to user's folder
cp $descPath/truth_table.vhdl $userTaskPath

# copy the isim tcl file for testing to user's folder
cp $taskPath/scripts/isim.cmd $userTaskPath

#change to userTaskPath, generate space for errors
cd $userTaskPath
touch error_msg

# create tmp directory
if [ ! -d "/tmp/$USER" ]
then
   mkdir /tmp/$USER
fi

#check if the user supplied a file
if [ ! -f $userfile ]
then
    logPrefix && echo "${logPre}Error with Task $2. User $1 did not attach the right file"
    cd $autosubPath
    echo "You did not attach your solution. Please attach the file $userfile" >$userTaskPath/error_msg
    exit 1
fi

#delete all comments from the file
sed -i 's:--.*$::g' $userfile

##########################
######### ANALYZE ########
##########################

# prepare sources for ISE
. /opt/Xilinx/14.7/ISE_DS/ISE/.settings64.sh /opt/Xilinx/14.7/ISE_DS/ISE

#entity, not from user, should have no errors
vhpcomp truth_table.vhdl
RET=$?
if [ "$RET" -ne "$zero" ]
then
   logPrefix && echo "${logPre}Error with Task $2 entity for user with ID $1";
   echo "Something went wrong with the task $2 test generation. This is not your fault. We are working on a solution" > $userTaskPath/error_msg
   exit 3
fi

#testbench, not from user, should have no errors
vhpcomp truth_table_tb_$1_Task$2.vhdl
RET=$?
if [ "$RET" -ne "$zero" ]
then
   logPrefix && echo "${logPre}Error with Task $2 testbench for user with ID $1";
   echo "Something went wrong with the task $2 test generation. This is not your fault. We are working on a solution" > $userTaskPath/error_msg
   exit 3
fi

#this is the file from the user
vhpcomp truth_table_beh.vhdl 2> /tmp/$USER/tmp_Task$2_User$1
RET=$?
if [ "$RET" -eq "$zero" ]
then
   logPrefix && echo "${logPre}Task$2 analyze success for user with ID $1!"
else
   logPrefix && echo "${logPre}Task$2 analyze FAILED for user with ID $1!"
   cd $autosubPath
   echo "Analyzation of your submitted behavior file failed:" >$userTaskPath/error_msg
   cat /tmp/$USER/tmp_Task$2_User$1 | grep ERROR >> $userTaskPath/error_msg
   exit 1
fi

##########################
######## ELABORATE #######
##########################
fuse -top truth_table_tb
RET=$?

if [ "$RET" -eq "$zero" ]
then
   logPrefix && echo "${logPre}Task$2 elaboration success for user with ID $1!"
else
   logPrefix && echo "${logPre}Task$2 elaboration FAILED for user with ID $1!"
   cd $autosubPath
   echo "Elaboration with your submitted behavior file failed:" >$userTaskPath/error_msg
   cat $userTaskPath/fuse.log | grep ERROR >> $userTaskPath/error_msg
   exit 1
fi

##########################
####### SIMULATION #######
##########################

# set location of licence file
# export LM_LICENSE_FILE=

#Simulation reports "Success" or an error message
./x.exe -tclbatch isim.cmd
egrep -oq "Success" isim.log
RET=$?

if [ "$RET" -eq "$zero" ]
then
    logPrefix && echo "${logPre}Functionally correct for Task$2 for user with ID $1!"
    exit 0
else
   cd $autosubPath
   logPrefix && echo "${logPre}Wrong behavior for Task$2 for user with ID $1"
   echo "Your submitted behavior file does not behave like specified in the task description:" >$userTaskPath/error_msg
   cat $userTaskPath/isim.log | grep Error >> $userTaskPath/error_msg
   exit 1
fi
