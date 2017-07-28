#!/bin/bash

######################################################################################
# Generalized tester for VHDL tasks
#
# Copyright (C) 2017 Martin  Mosbeck   <martin.mosbeck@gmx.at>
#                    Gilbert Markum    < >
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
######################################################################################

#--------------- SET UP ---------------
# parameters the tester gets from autosub
user_id=$1
task_nr=$2
task_params=$3
commonfile=$4

# return values of a tester
SUCCESS=0
TASKERROR=3
FAILURE=1

# root path of the task itself
task_path=$(readlink -f $0|xargs dirname)

#path to autosub
autosub_path=$(pwd)

# path for all the files that describe the created task
desc_path="$autosub_path/users/$1/Task$2/desc"

#path where the testing takes place
user_task_path="$autosub_path/users/$1/Task$2"

# change to the taskpath
cd $task_path

# include external config
source task.cfg

# name for the testbench
testbench=${task_name}_tb_${user_id}_Task${task_nr}.vhdl

#include simulator specific common file
source ../_common/$commonfile

#----------------- TEST ----------------
generate_testbench

prepare_test

taskfiles_analyze

userfiles_analyze

if [ -n "$constraintfile" ]
then
	source $constraintfile
fi

elaborate

simulate

# catch unhandled cases:
cd $user_task_path
touch error_msg
echo "Error: Unhandled tester case for task ${task_name} for user ${user_id}!"
echo "Something went wrong with task ${task_nr}. This is not your " \
"fault. We are working on a solution" > error_msg
exit $TASKERROR
