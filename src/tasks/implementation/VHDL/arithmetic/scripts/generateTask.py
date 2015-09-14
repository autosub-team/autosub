#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task arithmetic
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import random
import string
import sys
from bitstring import Bits

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
paramsEntity={}
paramsTbExam={}

width1=0
width2=0

#search for 2 different widths
while True:
   width1=random.randrange(4,17)
   width2=random.randrange(4,17)
   if(width1!=width2):
      break;

#the bit widths of input 1 & 2 and the output
i1_width=max(width1,width2)
i2_width=min(width1,width2)
o_width=max(width1,width2)

#operation 0->ADD, 0->SUB
operation=random.randrange(0,2)

#operand style: 0-> unsigned, 1->1s complement, 2->2s complement
operand_style=random.randrange(0,3)

##############################
## PARAMETER SPECIFYING TASK##
##############################
#|2|1|5|5|5|
taskParameters=(operand_style<<16)+(operation<<15)+(o_width<<10)+(i2_width<<5)+i1_width

############### ONLY FOR TESTING #######################
filename ="tmp/solution_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + str(taskParameters) + "\n")
    solution.write("FOOBAR")
   
#########################################################

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE # 
###########################################
operation_name_dict={0:"Addition",1:"Substraction"}
###########################################
operation_sign_dict={0:"+",1:"-"}
operand_style_dict={0:"unsigned",1:"ones' complement",2:"two's complement"}

paramsDesc.update({"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})
paramsDesc.update({"I1_WIDTH":str(i1_width),"I2_WIDTH":str(i2_width),"O_WIDTH":str(o_width)})
paramsDesc.update({"OPERATION_NAME":operation_name_dict[operation],"OPERATION_SIGN":operation_sign_dict[operation],"OPERAND_STYLE":operand_style_dict[operand_style]})

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

###########################################
#    SET PARAMETERS FOR ENTITY TEMPLATE   # 
###########################################
paramsEntity.update({"I1_WIDTH":i1_width,"I2_WIDTH":i2_width,"O_WIDTH":o_width})

#############################
#   FILL ENTITY TEMPLATE    #
#############################
filename ="templates/arithmetic_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()

filename ="tmp/arithmetic_{0}_Task{1}.vhdl".format(userId,taskNr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(paramsEntity))

##############################################
# SET PARAMETERS FOR EXAM TESTBENCH TEMPLATE # 
##############################################
i1Example=Bits(uint=random.randrange(1,2**i1_width-1),length=i1_width).bin
i2Example=Bits(uint=random.randrange(1,2**i2_width-1),length=i2_width).bin
paramsTbExam.update({"I1_WIDTH":i1_width,"I2_WIDTH":i2_width,"O_WIDTH":o_width,"I1_EXAMPLE":i1Example,"I2_EXAMPLE":i2Example})

#############################
#   FILL ENTITY TEMPLATE    #
#############################
filename ="exam/testbench_exam_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()

filename ="tmp/arithmetic_tb_exam_{0}_Task{1}.vhdl".format(userId,taskNr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(paramsTbExam))

###########################
### PRINT TASKPARAMETERS ##
###########################
print(taskParameters)
