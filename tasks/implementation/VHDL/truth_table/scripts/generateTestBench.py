#!/usr/bin/env python3
import sys
import string
from random import shuffle
from jinja2 import FileSystemLoader, Environment

#################################################################

taskParameter=int(sys.argv[1])
params={}

y=bin(taskParameter)
z=y[2:]
z=z.zfill(16)

#########################################
######### GENERATE TESTVECTORS ##########
#########################################

test_pattern=[  "('0', '0', '0', '0', ",
                "('0', '0', '0', '1', ",
                "('0', '0', '1', '0', ",
                "('0', '0', '1', '1', ",
                "('0', '1', '0', '0', ",
                "('0', '1', '0', '1', ",
                "('0', '1', '1', '0', ",
                "('0', '1', '1', '1', ",
                "('1', '0', '0', '0', ",
                "('1', '0', '0', '1', ",
                "('1', '0', '1', '0', ",
                "('1', '0', '1', '1', ",
                "('1', '1', '0', '0', ",
                "('1', '1', '0', '1', ",
                "('1', '1', '1', '0', ",
                "('1', '1', '1', '1', " ]

v=[]

for i in range(0,16) :
    v.append(test_pattern[i]+"'"+str(z[i])+"')")

shuffle(v)

for i in range(len(v)-1) :
    v[i]+=","

testPattern=("\n"+12*" ").join(v)

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################
params.update({"TESTPATTERN":testPattern})

###########################
# FILL TESTBENCH TEMPLATE #
###########################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"

template = env.get_template(filename)
template = template.render(params)

print(template)
