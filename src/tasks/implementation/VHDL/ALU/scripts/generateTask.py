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
desc=['add B to A',
      'to subtract B from A',
      'to operate logical AND between A and B',
      'to operate logical OR between A and B',
      'to operate logical XOR between A and B',
      'to compare A with B. If A\\textgreater=B then the flag bit will be 1, if A \\textless B then the carry flag bit will be 0, A is the output',
      'to copy and paste the most significant bit of input A to the carry flag, shift all bits of input A one bit to the left and then write zero to position 0',
      'to copy and paste the least significant bit of input A to the carry flag, shift all bits of input A one bit to the right and then write zero to the most significant bit',
      'to write the value of the most significant bit to position 0 (and also to carry flag), shift all bits of input A to the left',
      'to write the value of position 0 to the most significant position (and also to carry flag), shift all bits of input A to right']
desc_flag=['for unsigned values, overflow happens in an add operation when the sum of two numbers is more than 15 (for 4-bit values). In subtraction, overflow happens when a value is subtracted from a smaller value. Flag is set to 1, when overflow happens.',
	   'flag is the carry of operation',
	   'flag is 1, when the result is zero',
	   'if we assume that the result is signed, when the result is negative, flag is 1; otherwise, flag is 0.',
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
                   "DESCflag1":desc_flag[x[4]],
                   "FLAG1":flag[x[4]],"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})

if y[0]==5: 
  DESCflag2='carry flag is computed during the operation'
  tmp_flag2=flag[1]
else: 
  DESCflag2=desc_flag[x[5]]
  tmp_flag2=flag[x[5]]

if y[1]==5: 
  DESCflag3='carry flag is computed during the operation'
  tmp_flag3=flag[1]
else: 
  DESCflag3=desc_flag[x[5]]
  tmp_flag3=flag[x[5]]

if (x[3]==6 or x[3]==8): DESCflag4='carry is the most significant bit of A that is shifted out'
elif (x[3]==7 or x[3]==9): DESCflag4='carry is the least significant bit of A that is shifted out'
paramsDesc.update({"FLAG2":tmp_flag2,"FLAG3":tmp_flag3,"DESCflag2":DESCflag2,"DESCflag3":DESCflag3,"FLAG4":DESCflag4})
   
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
