#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task demux
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C)
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
from random import randrange
from math import ceil, log
import string

import json
from jinja2 import FileSystemLoader, Environment

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]
language=sys.argv[4]

params_desc={}
params_entity={}

##############################
## PARAMETER SPECIFYING TASK##
##############################

# choose bit width of inputs / outputs ( from: 2-10 -> 9 )
IN1_width = randrange(2,11)

# choose number of outputs for the demux ( from: 3-7 -> 5 )
num_out = randrange(3,8)

## for testing only:
#num_out = 8
#IN1_width = 10

task_parameters=str(IN1_width)+"|"+str(num_out)

###################################
## IMPORT LANGUAGE TEXT SNIPPETS ##
###################################

filename ="templates/task_description/language_support_files/lang_snippets_{0}.json".format(language)
with open(filename) as data_file:
    lang_data = json.load(data_file)

#########################################################

################################################
# GENERATE PARAMETERS FOR DESCRIPTION TEMPLATE # 
################################################

SEL_width = ceil(log(num_out, 2))
SEL_width = int(SEL_width)

SEL_max = pow(SEL_width,2)

SEL_possible = range(num_out)
SEL_possible = [format(x, '0'+str(int(SEL_width))+'b') for x in SEL_possible] # convert from integer list to a binary list 
SEL_possible = (' & '.join('' + x + '' for x in SEL_possible))

SEL_binary_zero = format(0, '0'+str(int(SEL_width))+'b')
SEL_binary_one  = format(1, '0'+str(int(SEL_width))+'b')


OUT_selected = ""
for x in range(1,num_out+1):
	OUT_selected += "OUT" + str(x)
	if x < num_out:
		OUT_selected += "& "

SEL_max_greater_num_out = ""
if SEL_max > num_out:
	SEL_max_greater_num_out = lang_data["SEL_max_greater_num_out"]
minimum_height = 6 * (1 + num_out) # minimum_height for tikzpicture

outputs_entity = ""
for x in range(1,num_out+1):
	outputs_entity += "\draw[->] ($ (entity.east) + (0mm," + str(((minimum_height / 2) - (x * (minimum_height / (num_out + 1))))) + "mm)$) -- ($ (entity.east) + (10mm," + str(((minimum_height / 2) - (x * (minimum_height / (num_out + 1))))) + "mm)$);\n"
	outputs_entity += "\draw[anchor=west] node at ($ (entity.east) + (9mm," + str(((minimum_height/2) - (x * ( minimum_height / (num_out + 1))))) + "mm)$){ OUT" + str(x) + " };\n\n"

outputs_comma = ""
for x in range(1,num_out+1):
	outputs_comma += "OUT" + str(x)
	if x < num_out:
		outputs_comma += ", "

num_c = ""
for x in range(num_out):
	num_c += "c "


############################################
## SET PARAMETERS FOR DESCRIPTION TEMPLATE # 
############################################
params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email, "IN1_width":IN1_width, "SEL_width":SEL_width, "num_out":num_out, "minimum_height":minimum_height, "outputs_entity":outputs_entity, "outputs_comma":outputs_comma, "SEL_binary_zero":SEL_binary_zero, "SEL_binary_one":SEL_binary_one, "SEL_max_greater_num_out":SEL_max_greater_num_out, "num_c":num_c, "SEL_possible":SEL_possible, "OUT_selected":OUT_selected })

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="task_description/task_description_template_{0}.tex".format(language)
template = env.get_template(filename)
template = template.render(params_desc)

filename ="tmp/desc_{0}_Task{1}.tex".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################################
# GENERATE PARAMETERS FOR ENTITY TEMPLATE # 
###########################################

# generate num_out outputs for the entity declaration
outputs_entity = ""
for x in range(1,(num_out+1)):
	outputs_entity += "           OUT" + str(x) + " : out std_logic_vector((" + str(IN1_width) + " - 1) downto 0)"
	if x < num_out:
		outputs_entity += ";\n"
	if x == num_out:
		outputs_entity += ");\n"

######################################
# SET PARAMETERS FOR ENTITY TEMPLATE #
######################################
params_entity.update({"IN1_width":IN1_width, "SEL_width":SEL_width, "outputs_entity":outputs_entity})

#############################
#   FILL ENTITY TEMPLATE    #
#############################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="demux_template.vhdl"
template = env.get_template(filename)
template = template.render(params_entity)

filename ="tmp/demux_{0}_Task{1}.vhdl".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################
### PRINT TASKPARAMETERS ##
###########################
print(task_parameters)
