#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task ROM
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) 2016 Hedyeh Agheh Kholerdi   <hedyeh.kholerdi@tuwien.ac.at>
########################################################################

import random
import string
import sys
from random import randint

from bitstring import Bits

from jinja2 import FileSystemLoader, Environment

import json

#################################################################

userId=sys.argv[1]
taskNr=sys.argv[2]
submissionEmail=sys.argv[3]
language=sys.argv[4]

paramsDesc={}

###################################
## IMPORT LANGUAGE TEXT SNIPPETS ##
###################################

filename ="templates/task_description/language_support_files/lang_snippets_{0}.json".format(language)
with open(filename) as data_file:
    lang_data = json.load(data_file)
####################################

x = []
data=[]
content = []
tmp_content = '0'


edge = random.randint(0, 1) # edge on which the ROM should be active 0->falling,1->rising
addr_len = random.randint(8, 16)
data_len = random.randint(8, 16)
data_start = random.randint(50, 200) # start location of data inside the ROM
num_data = random.randint(12, 20))  # number of data inside the ROM


content = [Bits(uint =randint(0,2**data_len-1), length = data_len).bin \
             for i in range(0,num_data)]

#y = [randint(0,2**data_len-1) for p in range(0,num_data)]
#for i in y:
#    bits_str = Bits(uint=i,length=data_len).bin
#    content.append('0'*(data_len-len(bin(i)[2:]))+bin(i)[2:])

tmp_data=(" \\newline").join(content)
for i in content:
    tmp_content=tmp_content+i
tmp=int(tmp_content,2)

start = '0'*(addr_len-len(bin(data_start)[2:]))+bin(data_start)[2:]
stop = '0'*(addr_len-len(bin(data_start+num_data-1)[2:]))+bin(data_start+num_data-1)[2:]

###############################
## PARAMETER SPECIFYING TASK ##
###############################
taskParameters = str(tmp)+str(edge)+str(addr_len-8)+str(data_len-8)+str(data_start+50)+str(num_data)

########################################################
############### ONLY FOR TESTING #######################
########################################################
filename ="tmp/solution_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + taskParameters + "\n")

###########################################
# SET PARAMETERS FOR ENTITY FILE TEMPLATE #
###########################################
paramsEntity={}
paramsEntity.update({"ADDRLENGTH":str(addr_len-1),"INSTRUCTIONLENGTH":str(data_len-1)})

##########################
### CHANGE ENTITY FILE ###
##########################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="ROM_template.vhdl"
template = env.get_template(filename)
template = template.render(paramsEntity)

filename ="tmp/ROM_{0}_Task{1}.vhdl".format(userId,taskNr)
with open (filename, "w") as output_file:
    output_file.write(template)
#################################
#### SET PARAMETERS FOR EXAM ####
#################################
random_num=[]
paramsExam={}
random_tmp=random.sample(range(data_start, data_start+num_data),num_data)
for i in range(0,num_data):
    random_num.append(str(random_tmp[i]))

for i in range(len(random_num)-1):
    random_num[i]+=","

random_num=("\n"+(28)*" ").join(random_num)

paramsExam.update({"RANDOM":random_num,"ADDRLENGTH":str(addr_len-1),"INSTRUCTIONLENGTH":str(data_len-1),"START":str(data_start),"DATALENGTH":str(num_data)})

##########################
#### CHANGE EXAM FILE ####
##########################
filename ="testbench_exam.vhdl"
env = Environment()
env.loader = FileSystemLoader('exam/')
template = env.get_template(filename)
template = template.render(paramsExam)

filename ="tmp/ROM_tb_exam_{0}_Task{1}.vhdl".format(userId,taskNr)
with open (filename, "w") as output_file:
    output_file.write(template)
###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################
#the
paramsDesc.update({"CLK":lang_data["clk_edge"][edge],"ADDRLENGTH":str(addr_len),"INSTRUCTIONLENGTH":str(data_len),
                   "START":start,"STOP":stop,"DATA":tmp_data,"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
env.loader = FileSystemLoader('templates/')
filename ="task_description/task_description_template_{0}.tex".format(language)
template = env.get_template(filename)
template = template.render(paramsDesc)

filename ="tmp/desc_{0}_Task{1}.tex".format(userId,taskNr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################
### PRINT TASKPARAMETERS ##
###########################
print(taskParameters)
