#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task gates
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>, LingYin Huang <lynn9c0021@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import random
import string
import sys
import fileinput

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

###########################
######## Function #########
###########################

def first_timing_tex(DELAY):
	value = 0.05*DELAY+1.5
	return value

def next_timing_tex(value):
	value = value+130*0.05
	return value


def first_center_tex(value):
	value = (value+1.5)/2
	return value

def next_center_tex(value2,value1):
	value = (value2+value1)/2
	return value


###########################
######## Timing ###########
###########################

RANDOM_RANGE_LOW = 2
RANDOM_RANGE_HIGH = 11
#initialize the value and coefficients
VALUE_A = VALUE_N = DELAY_O = DELAY_P = DELAY_E = 0
C1=C2=C3=C4=C5=C6=0

#generate random number for the signal value and delays
while(VALUE_A <= VALUE_N or DELAY_O >= DELAY_P or DELAY_O >= DELAY_E or DELAY_P >= DELAY_E or DELAY_P + DELAY_E !=130):
    VALUE_A = random.randint(RANDOM_RANGE_LOW, RANDOM_RANGE_HIGH) * 10
    VALUE_N = random.randint(RANDOM_RANGE_LOW, RANDOM_RANGE_HIGH) * 10
    DELAY_O = random.randint(RANDOM_RANGE_LOW, RANDOM_RANGE_HIGH) * 10
    DELAY_P = random.randint(RANDOM_RANGE_LOW, RANDOM_RANGE_HIGH) * 10
    DELAY_E = random.randint(RANDOM_RANGE_LOW, RANDOM_RANGE_HIGH) * 10


#generate coefficient
while( C1==0 or C3*VALUE_A < C4*VALUE_N ):
	C1 = random.randint(1, 3)
	C2 = random.randint(1, 3)
	C3 = random.randint(1, 3)
	C4 = random.randint(1, 3)
	C5 = random.randint(1, 3)
	C6 = random.randint(1, 3)

###########################
######## Timing Result#####
###########################

#Signal_Value_Number
NV1=NV2=NV3=0
OV1=OV2=OV3=0
PV1=PV2=PV3=0
EV1=EV2=EV3=0

NV1=VALUE_N
NV2=2*VALUE_N
NV3=3*VALUE_N
NV3=3*VALUE_N
NV4=4*VALUE_N

OV1=0
OV2=C1*VALUE_A
OV3=C1*VALUE_A*2+C2*VALUE_N
OV4=C1*VALUE_A*3+C2*VALUE_N*2

PV1=0
PV2=C3*VALUE_A
PV3=C3*VALUE_A*2-C4*VALUE_N
PV4=C3*VALUE_A*3-C4*VALUE_N*2

EV1=0
EV2=C5*OV2+C6*PV2
EV3=C5*OV3+C6*PV3
EV4=C5*OV4+C6*PV4

#Signal_Naro_Second
ONS1=DELAY_O
ONS2=DELAY_O+130
PNS1=DELAY_P
PNS2=DELAY_P+130

#Singal_Xcoordinate_in_Latex
OX1=first_timing_tex(DELAY_O)
OX2=next_timing_tex(OX1)
OX3=next_timing_tex(OX2)


PX1=first_timing_tex(DELAY_P)
PX2=next_timing_tex(PX1)
PX3=next_timing_tex(PX2)




##############################
## PARAMETER SPECIFYING TASK##
##############################
taskParameters=[NV1,OV1,PV1,EV1,NV1,OV2,PV1,EV1,NV1,OV2,PV2,EV1,NV2,OV2,PV2,EV2,NV2,OV3,PV2,EV2,NV2,OV3,PV3,EV2,NV3,OV3,PV3,EV3,NV3,OV4,PV3,EV3,NV3,OV4,PV4,EV3,NV4,OV4,PV4,EV4,ONS1,PNS1]

#taskParameters=str(VALUE_A)+"|"+str(VALUE_N)+"|"+str(DELAY_O)+"|"+str(DELAY_P)+"|"+str(DELAY_E)+"|"+str(C1)+"|"+str(C2)+"|"+str(C3)+"|"+str(C4)+"|"+str(C5)+"|"+str(C6)+"|"+str(ONS1)+"|"+str(PNS1)

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################

#for testing and variable A
paramsDesc["value_a"]=VALUE_A
paramsDesc["value_n"]=VALUE_N
paramsDesc["delay_o"]=DELAY_O
paramsDesc["delay_p"]=DELAY_P
paramsDesc["delay_e"]=DELAY_E

#Coefficient
paramsDesc["c1"]=C1
paramsDesc["c2"]=C2
paramsDesc["c3"]=C3
paramsDesc["c4"]=C4
paramsDesc["c5"]=C5
paramsDesc["c6"]=C6

#Signal_Value_Number
paramsDesc["nv1"]=NV1
paramsDesc["nv2"]=NV2
paramsDesc["nv3"]=NV3
paramsDesc["ov1"]=OV1
paramsDesc["ov2"]=OV2
paramsDesc["ov3"]=OV3
paramsDesc["pv1"]=PV1
paramsDesc["pv2"]=PV2
paramsDesc["pv3"]=PV3
paramsDesc["ev1"]=EV1
paramsDesc["ev2"]=EV2
paramsDesc["ev3"]=EV3

#Singal_Timing_Xcoordinate_in_Latex
paramsDesc["ox1"]=OX1
paramsDesc["ox11"]=OX1-0.25
paramsDesc["ox12"]=OX1+0.25
paramsDesc["ox1_center"]=first_center_tex(OX1)
paramsDesc["ox2"]=OX2
paramsDesc["ox21"]=OX2-0.25
paramsDesc["ox22"]=OX2+0.25
paramsDesc["ox2_center"]=next_center_tex(OX1,OX2)
if DELAY_O < 40 :
	paramsDesc["ox3_center"]=next_center_tex(OX2,OX3)
	paramsDesc["ox31"]=next_timing_tex(OX2)-0.25
	paramsDesc["ox32"]=next_timing_tex(OX2)+0.25

else:
	paramsDesc["ox3_center"]=next_center_tex(OX2,16.5)
	paramsDesc["ox31"]=OX2-0.25
	paramsDesc["ox32"]=OX2+0.25
paramsDesc["px1"]=PX1
paramsDesc["px11"]=PX1-0.25
paramsDesc["px12"]=PX1+0.25
paramsDesc["px1_center"]=first_center_tex(PX1)
paramsDesc["px2"]=PX2
paramsDesc["px21"]=PX2-0.25
paramsDesc["px22"]=PX2+0.25
paramsDesc["px2_center"]=next_center_tex(PX1,PX2)
if DELAY_P == 30 :
	paramsDesc["px3_center"]=next_center_tex(PX2,PX3)
	paramsDesc["px31"]=next_timing_tex(PX2)-0.25
	paramsDesc["px32"]=next_timing_tex(PX2)+0.25

else:
	paramsDesc["px3_center"]=next_center_tex(PX2,16.5)
	paramsDesc["px31"]=PX2-0.25
	paramsDesc["px32"]=PX2+0.25

#Signal_Naro_Second
paramsDesc["ons1"]=ONS1
paramsDesc["ons2"]=ONS2
paramsDesc["pns1"]=PNS1
paramsDesc["pns2"]=PNS2

#Email and Task number
paramsDesc.update({"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})

############### ONLY FOR TESTING #######################

#task results for checker
filename ="tmp/result_check_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + str(taskParameters) + "\n")

#task solution
filename ="templates/solution_template.txt"
with open (filename, "r") as template_file:
	data=template_file.read()
filename ="tmp/solution_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as output_file:
	s = MyTemplate(data)
	output_file.write(s.substitute(paramsDesc))

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
