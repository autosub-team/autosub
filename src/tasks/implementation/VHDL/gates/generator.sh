#!/bin/bash

########################################################################
# generator.sh for VHDL task gates
# Generates the individual tasks, enters in databases and moves
# description files to user folder
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################


##########################
####### PARAMETERS #######
##########################
# $1 ... UserId
# $2 ... TaskNr
# $3 ... Submission Email
# $4 ... Mode

##########################
########## PATHS #########
##########################
# src path of autosub system
autosubPath=$(pwd) 
# root path of the task itself
taskPath=$(readlink -f $0|xargs dirname)
# path for all the files that describe the created path
descPath="$autosubPath/users/$1/Task$2/desc"

##########################
##### PATH CREATIONS #####
##########################
if [ ! -d "$taskPath/tmp" ]
then
   mkdir $taskPath/tmp
fi

if [ ! -d "$descPath" ]
then
   mkdir $descPath
fi

##########################
####### GENERATE #########
##########################
cd $taskPath

task_parameters=$(python3 scripts/generateTask.py "$1" "$2" "$3")

#generate the description pdf and move it to user's description folder
cd $taskPath/tmp
latex desc_$1_Task$2.tex >/dev/null 2>/dev/null
dvips desc_$1_Task$2.dvi >/dev/null 2>/dev/null
ps2pdf desc_$1_Task$2.ps >/dev/null 2>/dev/null
rm desc_$1_Task$2.dvi
rm desc_$1_Task$2.aux
rm desc_$1_Task$2.ps
rm desc_$1_Task$2.log
rm desc_$1_Task$2.tex
mv $taskPath/tmp/desc_$1_Task$2.pdf $descPath

#copy static files to user's description folder
cp $taskPath/static/gates.vhdl $descPath
cp $taskPath/static/gates_beh.vhdl $descPath
cp $taskPath/static/IEEE_1164_Gates_pkg.vhdl $descPath 
cp $taskPath/static/IEEE_1164_Gates.vhdl $descPath
cp $taskPath/static/IEEE_1164_Gates_beh.vhdl $descPath

#for exam
cp $taskPath/exam/testbench_exam.vhdl $descPath/gates_tb_exam.vhdl


############### ONLY FOR TESTING #################
mv $taskPath/tmp/solution_$1_Task$2.txt $descPath
##################################################

##########################
##   EMAIL ATTACHMENTS  ##
##########################

taskAttachments=""
taskAttachmentsBase="$descPath/desc_$1_Task$2.pdf $descPath/gates.vhdl $descPath/gates_beh.vhdl $descPath/IEEE_1164_Gates_pkg.vhdl $descPath/IEEE_1164_Gates.vhdl $descPath/IEEE_1164_Gates_beh.vhdl"

if [ -n "$4" ];
then
    if [ "$4" = "exam" ];
    then
        taskAttachments="$taskAttachmentsBase $descPath/gates_tb_exam.vhdl"
    fi
fi
if [ -z "$4" ] || [ "$4" = "normal" ]; #default to normal
then
    taskAttachments="$taskAttachmentsBase" 
fi 

##########################
## ADD TASK TO DATABASE ##
##########################
#NOTE: do not attach solution in final version :)
cd $autosubPath/tools
python3 add_to_usertasks.py -u $1 -t $2 -p $task_parameters -a "$taskAttachments"


cd $autosubPath
