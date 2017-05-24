#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task {{ task_name }}
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C)
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]

params_desc={}

###########################################
#              YOUR CODE                  #
###########################################
#...
#...
#...
task_parameters =


###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################
params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email})

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
filename ="templates/task_description_template.tex"
with open (filename, "r") as template_file:
    data=template_file.read()

filename ="tmp/desc_{0}_Task{1}.tex".format(user_id,task_nr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(params_desc))

###########################
### PRINT TASKPARAMETERS ##
###########################
print(task_parameters)
