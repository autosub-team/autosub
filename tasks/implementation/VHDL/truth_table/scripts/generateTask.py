#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task truth_table
# Generates random tasks, generates TaskParameters, fill 
# entity and description templates
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import random
import string
import sys

from jinja2 import FileSystemLoader, Environment

import qm

########################################################################

userId=sys.argv[1]
taskNr=sys.argv[2]
submissionEmail=sys.argv[3]
language = sys.argv[4]

########################################################################

paramsDesc={}

x= 0
y= 0

## Create binary values for truth-table and make sure that it can be optimized
while True:
    x=random.randrange(0, 65535) #possible solutions for a 4 bit truth table

    #convert to a array of '1' and '0'
    y=bin(x);
    y=y[2:]
    y=y.zfill(16)
 
    #find all ones and feed it to Quine–McCluskey algorithm
    indices = [i for i, x in enumerate(y) if x == '1'] 
    optimized=qm.qm(ones=indices)
   
    #find out how many optimizations possile
    xes=[]
    for i in optimized:
        xes.append(i.count("X"));
    
    #we want at least one possible optimization
    if(max(xes)==0 or len(optimized)>4):
       continue
    else:
        break

##############################
## PARAMETER SPECIFYING TASK##
##############################
taskParameters=x   

############### ONLY FOR TESTING #######################
filename ="tmp/solution_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + str(taskParameters) + "\n")
    solution.write("KV Diagramm\n")
    solution.write(str(y[0])+str(y[4])+str(y[5])+str(y[1])+ "\n")
    solution.write(str(y[8])+str(y[12])+str(y[13])+str(y[9])+ "\n")
    solution.write(str(y[10])+str(y[14])+str(y[15])+str(y[11])+ "\n")
    solution.write(str(y[2])+str(y[6])+str(y[7])+str(y[3])+ "\n")
    solution.write("\n")
    solution.write("Optimization as DNF, DCBA:\n")
    for maxterm in optimized:
        solution.write(maxterm + "\n")
#########################################################

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE # 
###########################################
#the bits are labled in template as O0 to O15
for i in range(0,16):
    paramsDesc["O"+str(i)]=y[i]
paramsDesc.update({"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
env = Environment()
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
