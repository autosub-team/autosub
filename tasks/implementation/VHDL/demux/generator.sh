#!/bin/bash

########################################################################
# generator.sh for VHDL task demux
# Generates the individual tasks, enters in databases and moves
# description files to user folder
#
# Copyright (C)
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################


##########################
####### PARAMETERS #######
##########################
user_id=$1
task_nr=$2
submission_email=$3
mode=$4
semester_db=$5
language=$6

##########################
########## PATHS #########
##########################
# src path of autosub system
autosub_path=$(pwd)
# root path of the task itself
task_path=$(readlink -f $0|xargs dirname)
# path for all the files that describe the created path
desc_path="${autosub_path}/users/${user_id}/Task${task_nr}/desc"

##########################
##### PATH CREATIONS #####
##########################
if [ ! -d "${task_path}/tmp" ]
then
   mkdir ${task_path}/tmp
fi

if [ ! -d "${desc_path}" ]
then
   mkdir ${desc_path}
fi

##########################
####### GENERATE #########
##########################
cd ${task_path}

task_parameters=$(python3 scripts/generateTask.py "${user_id}" "${task_nr}" "${submission_email}" "${language}")

#generate the description pdf and move it to user's description folder
cd ${task_path}/tmp

pdflatex -halt-on-error desc_${user_id}_Task${task_nr}.tex >/dev/null
RET=$?
zero=0
if [ "$RET" -ne "$zero" ];
then
    echo "ERROR with pdf generation for Task${task_nr} !!! Are all needed LaTeX packages installed??">&2
fi

rm desc_${user_id}_Task${task_nr}.aux
rm desc_${user_id}_Task${task_nr}.log
rm desc_${user_id}_Task${task_nr}.tex
mv ${task_path}/tmp/desc_${user_id}_Task${task_nr}.pdf ${desc_path}

#copy static files to user's description folder
cp ${task_path}/static/demux_beh.vhdl ${desc_path}

#move generated files to user's description folder
mv ${task_path}/tmp/demux_${user_id}_Task${task_nr}.vhdl ${desc_path}/demux.vhdl

##########################
##   EMAIL ATTACHMENTS  ##
##########################
task_attachments="${desc_path}/desc_${user_id}_Task${task_nr}.pdf ${desc_path}/demux.vhdl ${desc_path}/demux_beh.vhdl"

##########################
## ADD TASK TO DATABASE ##
##########################
cd ${autosub_path}/tools
python3 add_to_usertasks.py -u ${user_id} -t ${task_nr} -p "${task_parameters}" -a "${task_attachments}" -d ${semester_db}
