#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task ALU
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) 2016 Hedyeh Agheh Kholerdi   <hedyeh.kholerdi@tuwien.ac.at>
#
########################################################################

import random
import string
import sys

import json

from jinja2 import FileSystemLoader, Environment

#################################################################

userId=sys.argv[1]
taskNr=sys.argv[2]
submissionEmail=sys.argv[3]
language=sys.argv[4]

params_desc={}

x = []

x.append(random.randint(0, 1))  # ADD or SUB
y=random.sample(range(2, 6),2)  # AND or OR or XOR or comparator
x.append(y[0])
x.append(y[1])
x.append(random.randint(6, 9)) # SHIFT instructions
x.append(random.randint(0, 3))  # flag for ADD or SUB including Overflow,Carry,Zero and Sign
x.append(random.randint(2, 4))  # flag for AND or OR or XOR including Zero, Sign and Parity

##############################
## PARAMETER SPECIFYING TASK##
##############################
taskParameters=str(x[0])+str(x[1])+str(x[2])+str(x[3])+str(x[4])+str(x[5])

############### ONLY FOR TESTING #######################
filename ="tmp/solution_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + taskParameters)

#########################################################

###################################
## IMPORT LANGUAGE TEXT SNIPPETS ##
###################################

filename ="templates/task_description/language_support_files/lang_snippets_{0}.json".format(language)
with open(filename) as data_file:
    lang_data = json.load(data_file)

#########################################################

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################
if x[4]==0:
  if x[0]==0:
    DESCflag1=lang_data["desc_flag2"][0]
  elif x[0]==1:
    DESCflag1=lang_data["desc_flag2"][1]
else:
  DESCflag1=lang_data["desc_flag"][x[4]-1]


if y[0]==5:
  DESCflag2=lang_data["desc_flag2"][2]
  tmp_flag2=lang_data["flag"][1]
else:
  DESCflag2=lang_data["desc_flag"][x[5]-1]
  tmp_flag2=lang_data["flag"][x[5]]

if y[1]==5:
  DESCflag3=lang_data["desc_flag2"][3]
  tmp_flag3=lang_data["flag"][1]
else:
  DESCflag3=lang_data["desc_flag"][x[5]-1]
  tmp_flag3=lang_data["flag"][x[5]]

if (x[3]==6 or x[3]==8): DESCflag4=lang_data["desc_flag2"][4]
elif (x[3]==7 or x[3]==9): DESCflag4=lang_data["desc_flag2"][5]


params_desc.update({	"INS1":lang_data["inst"][x[0]],		"INS2":lang_data["inst"][x[1]],		"INS3":lang_data["inst"][x[2]],		"INS4":lang_data["inst"][x[3]],
			"DESC1":lang_data["desc"][x[0]],	"DESC2":lang_data["desc"][x[1]],	"DESC3":lang_data["desc"][x[2]],	"DESC4":lang_data["desc"][x[3]],
			"DESCflag1":DESCflag1,			"DESCflag2":DESCflag2,			"DESCflag3":DESCflag3,			"DESCflag4":DESCflag4,
			"FLAG1":lang_data["flag"][x[4]],	"FLAG2":tmp_flag2,			"FLAG3":tmp_flag3,
			"TASKNR":str(taskNr),			"SUBMISSIONEMAIL":submissionEmail})

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="task_description/task_description_template_{0}.tex".format(language)
template = env.get_template(filename)
template = template.render(params_desc)

filename ="tmp/desc_{0}_Task{1}.tex".format(userId,taskNr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################
### PRINT TASKPARAMETERS ##
###########################
print(taskParameters)
