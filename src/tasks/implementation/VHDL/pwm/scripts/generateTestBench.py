#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task pwm
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
import string
import random

###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

taskParameters=int(sys.argv[1]) 
params={}

simCycles = random.randrange(5,30)  
periodClks = taskParameters >> 18
dutyClks = taskParameters & (2**18-1)

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE # 
#########################################
params.update({"PERIODCLKS":periodClks,"DUTYCLKS":dutyClks,"SIMCYCLES":simCycles})

###########################
# FILL TESTBENCH TEMPLATE #
###########################
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))

    
