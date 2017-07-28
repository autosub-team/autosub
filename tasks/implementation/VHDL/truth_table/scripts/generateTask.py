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

import qm

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

x= 0
y= 0


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
