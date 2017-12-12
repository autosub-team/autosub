#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task arithmetic
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import random
import string
import sys
from bitstring import Bits

from jinja2 import FileSystemLoader, Environment

import json

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]
language=sys.argv[4]

params_desc={}
params_entity={}
params_TbExam={}

width1=0
width2=0

#search for 2 different widths
while True:
   width1=random.randrange(4,17)
   width2=random.randrange(4,17)
   if(width1!=width2):
      break;

#the bit widths of input 1 & 2 and the output
i1_width=max(width1,width2)
i2_width=min(width1,width2)
o_width=max(width1,width2)

#operation 0->ADD, 0->SUB
operation=random.randrange(0,2)

#operand style: 0-> unsigned, 1->1s complement, 2->2s complement
operand_style=random.randrange(0,3)

###################################
## IMPORT LANGUAGE TEXT SNIPPETS ##
###################################
filename ="templates/task_description/language_support_files/lang_snippets_{0}.json".format(language)
with open(filename) as data_file:
    lang_data = json.load(data_file)

##############################
## PARAMETER SPECIFYING TASK##
##############################
#|2|1|5|5|5|
task_parameters=(operand_style<<16)+(operation<<15)+(o_width<<10)+(i2_width<<5)+i1_width

############### ONLY FOR TESTING #######################
filename ="tmp/solution_{0}_Task{1}.txt".format(user_id,task_nr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + str(task_parameters) + "\n")
    solution.write("FOOBAR")

#########################################################

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################
operation_sign_dict={0:"+",1:"-"}

params_desc.update({"TASKNR":str(task_nr),"SUBMISSIONEMAIL":submission_email})
params_desc.update({"I1_WIDTH":str(i1_width),"I2_WIDTH":str(i2_width),"O_WIDTH":str(o_width)})
params_desc.update({"OPERATION_NAME":lang_data["operation_name_dict"][operation],"OPERATION_SIGN":operation_sign_dict[operation],"OPERAND_STYLE":lang_data["operand_style_dict"][operand_style]})

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
#    SET PARAMETERS FOR ENTITY TEMPLATE   #
###########################################
params_entity.update({"I1_WIDTH":i1_width,"I2_WIDTH":i2_width,"O_WIDTH":o_width})

#############################
#   FILL ENTITY TEMPLATE    #
#############################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="arithmetic_template.vhdl"
template = env.get_template(filename)
template = template.render(params_entity)

filename ="tmp/arithmetic_{0}_Task{1}.vhdl".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)

##############################################
# SET PARAMETERS FOR EXAM TESTBENCH TEMPLATE #
##############################################
i1Example=Bits(uint=random.randrange(1,2**i1_width-1),length=i1_width).bin
i2Example=Bits(uint=random.randrange(1,2**i2_width-1),length=i2_width).bin
params_TbExam.update({"I1_WIDTH":i1_width,"I2_WIDTH":i2_width,"O_WIDTH":o_width,"I1_EXAMPLE":i1Example,"I2_EXAMPLE":i2Example})

################################
#   FILL TESTBENCH TEMPLATE    #
################################
env = Environment()
env.loader = FileSystemLoader('exam/')
filename ="testbench_exam_template.vhdl"
template = env.get_template(filename)
template = template.render(params_TbExam)

filename ="tmp/arithmetic_tb_exam_{0}_Task{1}.vhdl".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################
### PRINT TASKPARAMETERS ##
###########################
print(task_parameters)
