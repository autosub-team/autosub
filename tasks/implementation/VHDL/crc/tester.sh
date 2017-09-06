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

#path to common scripts
common_path=$(readlink -f $task_path/../_common)

# include external config
source $task_path/task.cfg

#include simulator specific common file
source $common_path/$commonfile

#----------------- TEST ----------------
generate_testbench

prepare_test

taskfiles_analyze

userfiles_analyze

if [ -n "$constraintfile" ]
then
	source $task_path/$constraintfile
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
