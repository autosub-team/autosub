#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task gates
# Generates random tasks, generates TaskParameters, fill 
# entity and description templates
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import random
import string
import sys

import LogicFormulaCreator

###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

###########################
#### HELPER FUNCTIONS #####
###########################
def toBase3(number,length):
    remainder=0
    dividend=number
    base3Nr=""

    while dividend != 0 :
        remainder = dividend % 3 
        dividend = dividend // 3
        base3Nr+=str(remainder)
    base3Nr=base3Nr.zfill(length)
    return [int(x) for x in base3Nr]

def toBase2(number,length):
    return [int(x) for x in bin(number)[2:].zfill(length)]

#################################################################

userId=sys.argv[1]
taskNr=sys.argv[2]
submissionEmail=sys.argv[3]

paramsDesc={}
params_inputs= {}  
params_gates={}
params_outputs={}

###########################
######## GATES ############
###########################
  
randGates = random.randrange(0,3**5)
gates = toBase3(randGates,5)


gate_types={0:"cand",1:"cor",2:"cxor"}

for i in range(0,5):
    params_gates["G"+str(i)]=gate_types[gates[i]]
	
###########################
### INPUTS ENABLE LVL 1 ###
###########################
randEnableInputsLvl1=0
while True:
    randEnableInputsLvl1 = random.randrange(0,2**16)
    inputsEnableLvl1=toBase2(randEnableInputsLvl1,16)

    #check if no gate with only 1 input
    if( (inputsEnableLvl1[0:4].count(0)  >= 3)  or \
        (inputsEnableLvl1[4:8].count(0)  >= 3)  or \
        (inputsEnableLvl1[8:12].count(0)  >= 3) or \
        (inputsEnableLvl1[12:16].count(0) >= 3)    \
    ):
        continue
    else:
        break

#0 not connected, 1 connected
input_types={0:["false","%"],1:["true"," "]}

for i in range(0,16):
    params_inputs["IE"+str(i)]=input_types[inputsEnableLvl1[i]][0]
    params_inputs["GI"+str(i)]=input_types[inputsEnableLvl1[i]][1]

###########################
### INPUTS NEGATE LVL 1 ###
###########################
randNegateInputsLvl1 = random.randrange(0,2**16)
inputsNegateLvl1=toBase2(randNegateInputsLvl1,16)

input_negation={0:"false",1:"true"}

for i in range(0,16):
    params_inputs["IN"+str(i)]=input_negation[inputsNegateLvl1[i]]

###########################
## INPUTS NEGATE LVL 2 ####
###########################
randNegateInputsLvl2=random.randrange(0,2*4)
inputsNegateLvl2=toBase2(randNegateInputsLvl2,4)

input_negation={0:"false",1:"true"}

for i in range(16,20):
    params_inputs["IN"+str(i)]=input_negation[inputsNegateLvl2[i-16]]


###########################
### OUTPUTS NEGATE ########
###########################
randNegateOutputs=random.randrange(0,2**5)
outputsNegate=toBase2(randNegateOutputs,5)

output_negation={0:"false",1:"true"}

for i in range(0,5):
    params_outputs["ON"+str(i)]=output_negation[outputsNegate[i]]


##############################
## PARAMETER SPECIFYING TASK##
##############################
taskParameters= (randGates<<41) + (randEnableInputsLvl1<<25) + (randNegateInputsLvl1<<9) + (randNegateInputsLvl2<<5) + randNegateOutputs

############### ONLY FOR TESTING #######################
#get logic formula for taskParameters
expression = LogicFormulaCreator.createFromParameters(taskParameters)

filename ="tmp/solution_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + str(taskParameters) + "\n")
    solution.write("logic Formula:\n")
    solution.write(expression)
    solution.write("\nOr preferably use the attached gate entities :)")
#########################################################


###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE # 
###########################################
paramsDesc.update(params_gates)
paramsDesc.update(params_inputs)  
paramsDesc.update(params_outputs)
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
