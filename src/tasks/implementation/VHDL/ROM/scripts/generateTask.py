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


###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

userId=sys.argv[1]
taskNr=sys.argv[2]
submissionEmail=sys.argv[3]

paramsDesc={}

x = []
data=[]
content = []
tmp_content = '0'
clk =['falling edge','rising edge']


x.append(random.randint(0, 1))    # clock cycle
x.append(random.randint(8, 16))   # length of address
x.append(random.randint(8, 16))   # length of data (instruction)
x.append(random.randint(50, 200)) # start location of data inside the ROM
x.append(random.randint(12, 20))  # number of data inside the ROM

y = [randint(0,2**x[2]-1) for p in range(0,x[4])]
for i in y:
    content.append('0'*(x[2]-len(bin(i)[2:]))+bin(i)[2:])

tmp_data=(" \\newline"+(0)*" ").join(content)
for i in content:
    tmp_content=tmp_content+i
tmp=int(tmp_content,2)
    
start = '0'*(x[1]-len(bin(x[3])[2:]))+bin(x[3])[2:]
stop = '0'*(x[1]-len(bin(x[3]+x[4]-1)[2:]))+bin(x[3]+x[4]-1)[2:]

###############################
## PARAMETER SPECIFYING TASK ##
###############################
taskParameters = str(tmp)+str(x[0])+str(x[1]-8)+str(x[2]-8)+str(x[3]+50)+str(x[4])

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
paramsEntity.update({"ADDRLENGTH":str(x[1]-1),"INSTRUCTIONLENGTH":str(x[2]-1)})
  
##########################
### CHANGE ENTITY FILE ###
##########################
filename ="templates/ROM_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    
filename ="tmp/ROM_{0}_Task{1}.vhdl".format(userId,taskNr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(paramsEntity))

#################################
#### SET PARAMETERS FOR EXAM ####
#################################
random_num=[]
paramsExam={}
random_tmp=random.sample(range(x[3], x[3]+x[4]),x[4])    
for i in range(0,x[4]):
    random_num.append(str(random_tmp[i]))    

for i in range(len(random_num)-1):
    random_num[i]+=","
    
random_num=("\n"+(28)*" ").join(random_num)

paramsExam.update({"RANDOM":random_num,"ADDRLENGTH":str(x[1]-1),"INSTRUCTIONLENGTH":str(x[2]-1),"START":str(x[3]),"DATALENGTH":str(x[4])})

##########################
#### CHANGE EXAM FILE ####
##########################
filename ="exam/testbench_exam.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    
filename ="tmp/ROM_tb_exam_{0}_Task{1}.vhdl".format(userId,taskNr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(paramsExam))
    
###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE # 
###########################################
#the 
paramsDesc.update({"CLK":clk[x[0]],"ADDRLENGTH":str(x[1]),"INSTRUCTIONLENGTH":str(x[2]),
                   "START":start,"STOP":stop,"DATA":tmp_data,"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
filename ="templates/task_description_template.tex"
with open (filename, "r") as template_file:
    data=template_file.read()

filename ="tmp/desc_{0}_Task{1}.tex".format(userId,taskNr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(paramsDesc))

###########################
### PRINT TASKPARAMETERS ##
###########################
print(taskParameters)
