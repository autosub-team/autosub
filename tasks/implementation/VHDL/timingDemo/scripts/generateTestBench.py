#!/usr/bin/env python3

#####################################################################################
# generateTestBench.py for VHDL task timingDemo
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2015, 2016 Martin  Mosbeck   <martin.mosbeck@gmx.at>, LingYin Huang
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
#####################################################################################

import sys
import string
import ast
from random import shuffle

###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

params={}

taskParameter=ast.literal_eval(sys.argv[1])
#x=sys.argv[1]




#########################################
### GENERATE TESTVECTORS for Checker#####
#########################################


#ONS1=taskParameter[32]
#PNS1=taskParameter[33]

#VALUE_A, VALUE_N, DELAY_O, DELAY_P, DELAY_E, C1, C2, C3, C4, C5, C6, ONS1, PNS1 = #x.split('|')


ONS1=taskParameter[40]
PNS1=taskParameter[41]

#taskParameter=[NV1,OV1,PV1,EV1,NV1,OV2,PV1,EV1,NV1,OV2,PV2,EV1,NV2,OV2,PV2,EV2,NV2,OV3,PV2,EV2,NV2,OV3,PV3,EV2,NV3,OV3,PV3,EV3,NV4,OV4,PV4,EV3,ONS1,PNS1]



v=[]

for i in range(0,40) :
    v.append(str(taskParameter[i]))

testPattern=(", ").join(v)

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################
params.update({"TESTPATTERN":testPattern, "time_o1":(ONS1-1), "time_p1":(PNS1-ONS1-1), "time_e1":(130-PNS1-1)})
#testbench wait for ns



###########################
# FILL TESTBENCH TEMPLATE #
###########################
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))

#filename ="tmp/testbench_template1.vhdl"
#with open (filename, "w") as output_file:
#	s = MyTemplate(data)
#	output_file.write(s.substitute(params))

#########################################

