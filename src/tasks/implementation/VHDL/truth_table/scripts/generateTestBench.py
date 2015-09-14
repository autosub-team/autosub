#!/usr/bin/env python3
import sys
import string
from random import shuffle

###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

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
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))


