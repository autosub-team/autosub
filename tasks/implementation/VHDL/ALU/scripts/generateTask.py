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
inst =['ADD','SUB','AND','OR','XOR','Comparator','Shift Left','Shift Right','Rotate Left','Rotate Right']
flag=['Overflow','Carry','Zero','Sign','Odd Parity']
desc=['adds B to A and outputs the result on R.',
      'subtracts B from A and outputs the result on R.',
      'operates logical AND between A and B and outputs the result on R.',
      'operates logical OR between A and B and outputs the result on R.',
      'operates logical XOR between A and B and outputs the result on R.',
      'compares A with B, and outputs A on R.',
      'shifts all bits of A one place to the left (the most significant bit is discarded), sets the least sigificant bit to 0, and outputs the four least significant bits on R.',
      'shifts all bits of A one place to the right, sets the most sigificant bit to 0, and outputs the four bits on R.',
      'shifts all bits of A one place to the left with the most significant bit moved to position 0, outputs the result on R.',
      'shifts all bits of A one place to the right with the least significant bit moved to position 3, outputs the result on R.']
desc_flag=['the flag is the carry of the operation.',
	   'the flag is 1, when the result is zero.',
	   'the flag is the copy of the most significant bit of the result.',
	   'the flag is 1 if the number of ones in the result is even. Otherwise it is 0.']

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
if x[4]==0:
  if x[0]==0:
    DESCflag1='the flag is set to 1, when overflow happens. For unsigned values, overflow happens in an add operation when the sum of the inputs is more than 15 (for 4-bit values).'
  elif x[0]==1: 
    DESCflag1='the flag is set to 1, when overflow happens. For unsigned values, overflow in subtraction happens when a value is subtracted from a smaller value.'
else:
  DESCflag1=desc_flag[x[4]-1]


if y[0]==5: 
  DESCflag2='if A\\textgreater=B then the flag bit will be 1, if A \\textless B then the flag bit will be 0.'
  tmp_flag2=flag[1]
else: 
  DESCflag2=desc_flag[x[5]-1]
  tmp_flag2=flag[x[5]]

if y[1]==5: 
  DESCflag3='if A\\textgreater=B then the flag bit will be 1, if A \\textless B then the flag bit will be 0.'
  tmp_flag3=flag[1]
else: 
  DESCflag3=desc_flag[x[5]-1]
  tmp_flag3=flag[x[5]]

if (x[3]==6 or x[3]==8): DESCflag4='the flag is the most significant bit of A.'
elif (x[3]==7 or x[3]==9): DESCflag4='the flag is the least significant bit of A.'


paramsDesc.update({"INS1":inst[x[0]],"INS2":inst[x[1]],"INS3":inst[x[2]],
                   "INS4":inst[x[3]],"DESC1":desc[x[0]],"DESC2":desc[x[1]],"DESC3":desc[x[2]],"DESC4":desc[x[3]],
                   "DESCflag1":DESCflag1,"FLAG1":flag[x[4]],"FLAG2":tmp_flag2,
                   "FLAG3":tmp_flag3,"DESCflag2":DESCflag2,"DESCflag3":DESCflag3,"DESCflag4":DESCflag4,
                   "TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})   
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
