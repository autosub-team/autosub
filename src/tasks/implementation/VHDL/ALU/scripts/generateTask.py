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
inst =['ADD','SUB','AND','OR','XOR','Comparator','Shift Left','Shift Right','Rotate Left without Carry','Rotate Right without Carry']
flag=['Overflow','Carry','Zero','Sign','Odd Parity']
desc=['add B to A',
      'subtract B from A',
      'operate logical AND between A and B',
      'operate logical OR between A and B',
      'operate logical XOR between A and B',
      'compare A with B. If A\\textgreater=B then the flag bit will be 1, if A \\textless B then the carry flag bit will be 0, A is the output',
      'shift the most significant bit to the carry flag, shift all bits of input A one bit to the left and then write zero to position 0',
      'shift the least significant bit to the carry flag, shift all bits of input A one bit to the right and then write zero to the most significant bit',
      'write the value of the most significant bit to position 0 (and also to carry flag), shift all bits of input A to the left',
      'write the value of position 0 to the most significant position (and also to carry flag), shift all bits of input A to right']
desc_flag=['For unsigned values, overflow happens in add operation when the sum of two number is more than 15 (for 4-bit values). In subtraction, overflow happens when a value is subtracts from a smaller value',
	   'Carry flag is the carry of operation',
	   'Zero flag is 1, when the result is zero',
	   'Sign of the result (even though the operands are considered to be unsigned)',
	   'Odd parity of the result']

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

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE # 
########################################### 
paramsDesc.update({"INS1":inst[x[0]],"INS2":inst[x[1]],"INS3":inst[x[2]],
                   "INS4":inst[x[3]],"DESC1":desc[x[0]],"DESC2":desc[x[1]],"DESC3":desc[x[2]],"DESC4":desc[x[3]],
                   "DESCflag1":desc_flag[x[4]],"DESCflag2":desc_flag[x[5]],
                   "FLAG1":flag[x[4]],"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})

cp_flag=[flag[x[5]],flag[x[5]]]
if y[0]==5: cp_flag[0]='Carry flag is computed during the operation'
if y[1]==5: cp_flag[1]='Carry flag is computed during the operation'

if (x[3]==6 or x[3]==8): DESCflag4='Carry is the most significant bit of A that is shifted out'
elif (x[3]==7 or x[3]==9): DESCflag4='Carry is the least significant bit of A that is shifted out'
paramsDesc.update({"FLAG2":cp_flag[0],"FLAG3":cp_flag[1],"FLAG4":DESCflag4})
   
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
