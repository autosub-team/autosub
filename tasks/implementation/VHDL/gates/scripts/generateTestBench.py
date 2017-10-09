#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task gates
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
import string
from random import shuffle

import LogicFormulaCreator

from jinja2 import FileSystemLoader, Environment 

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

taskParameter=int(sys.argv[1]) 
params={}

#get logic formula for taskParameter
formula = LogicFormulaCreator.createFromParameters(taskParameter)



v=[ "('0', '0', '0', '0')",
    "('0', '0', '0', '1')",      
    "('0', '0', '1', '0')",
    "('0', '0', '1', '1')",
    "('0', '1', '0', '0')",
    "('0', '1', '0', '1')",
    "('0', '1', '1', '0')",
    "('0', '1', '1', '1')",
    "('1', '0', '0', '0')",
    "('1', '0', '0', '1')",
    "('1', '0', '1', '0')",
    "('1', '0', '1', '1')",
    "('1', '1', '0', '0')",
    "('1', '1', '0', '1')",
    "('1', '1', '1', '0')",
    "('1', '1', '1', '1')" ]
         

shuffle(v) # make test vector order random

for i in range(len(v)-1) :
    v[i]+=","

testPattern=("\n"+12*" ").join(v) # just to make indentation 

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE # 
#########################################
params.update({"TESTPATTERN":testPattern, "FORMULA":formula})

###########################
# FILL TESTBENCH TEMPLATE #
###########################

env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"

template = env.get_template(filename)
template = template.render(params)

print(template)


