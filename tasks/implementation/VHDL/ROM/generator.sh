#!/bin/bash

########################################################################
# generator.sh for VHDL task ROM
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
# $5 ... SemesterDB

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

pdflatex -halt-on-error desc_$1_Task$2.tex >/dev/null
RET=$?
zero=0
if [ "$RET" -ne "$zero" ];
then
    echo "ERROR with pdf generation for Task$2 !!! Are all needed LaTeX packages installed??">&2
fi

rm desc_$1_Task$2.aux
rm desc_$1_Task$2.log
rm desc_$1_Task$2.tex
mv $taskPath/tmp/desc_$1_Task$2.pdf $descPath

#move the generated entity file to user's descritption folder
mv $taskPath/tmp/ROM_$1_Task$2.vhdl $descPath/ROM.vhdl

#copy static files to user's description folder
cp $taskPath/static/ROM_beh.vhdl $descPath

#for exam
mv $taskPath/tmp/ROM_tb_exam_$1_Task$2.vhdl $descPath/ROM_tb_exam.vhdl

############### ONLY FOR TESTING #################
mv $taskPath/tmp/solution_$1_Task$2.txt $descPath
##################################################

##########################
##   EMAIL ATTACHMENTS  ##
##########################
taskAttachments=""
taskAttachmentsBase="$descPath/desc_$1_Task$2.pdf $descPath/ROM.vhdl $descPath/ROM_beh.vhdl"

if [ -n "$4" ];
then
    if [ "$4" = "exam" ];
    then
        taskAttachments="$taskAttachmentsBase $descPath/ROM_tb_exam.vhdl"
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
python3 add_to_usertasks.py -u $1 -t $2 -p $task_parameters -a "$taskAttachments" -d $5

cd $autosubPath