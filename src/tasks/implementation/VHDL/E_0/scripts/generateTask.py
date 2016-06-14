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
temp = 0
y= ['active low','active high']
inst =['ADD','SUB','AND','OR']


while True:
    x.append(random.randrange(0, 2)) # random number to choose between active low and high
    x.append(random.randrange(0, 4)) # first instruction
    temp =(random.randrange(0, 4))   # select the second instruction. it should be different from the first one
    while temp[0]==x[1]:
        temp =(random.randrange(0, 4))
    x.append(temp)

##############################
## PARAMETER SPECIFYING TASK##
##############################
taskParameters=x   

############### ONLY FOR TESTING #######################

#########################################################

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE # 
###########################################
#the 
paramsDesc.update({"CLK":y[x[0]],"INS1":inst[x[1]],"INS2":inst[x[2]],"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})
   
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
