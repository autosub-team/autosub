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

inst =["+","-","and","or"]
inst_name =["ADD","SUB","AND","OR"]

#########################################
######### GENERATE TESTVECTORS ########## 
#########################################

test_pattern=[  '("00","00",',
                '("00","01",',      
                '("00","10",',
                '("00","11",',
                '("01","00",',
                '("01","01",',
                '("01","10",',
                '("01","11",',
                '("10","00",',
                '("10","01",',
                '("10","10",',
                '("10","11",',
                '("11","00",',
                '("11","01",',
                '("11","10",',
                '("11","11",' ]

x=inst[taskParameter[1]];
if x=="+":for i in range(0,16):z[i]=A+B
elif x=="-":for i in range(0,16):z[i]=A-B
elif x=="and":for i in range(0,16):z[i]=A and B
elif x=="or":for i in range(0,16):z[i]=A or B

x=inst[taskParameter[2]];
if x=="+":for i in range(0,16):w[i]=A+B
elif x=="-":for i in range(0,16):w[i]=A-B
elif x=="and":for i in range(0,16):w[i]=A and B
elif x=="or":for i in range(0,16):w[i]=A or B

v=[]    

for i in range(0,16) :
    v.append(test_pattern[i]+'"'+str("{0:b}".format((z[i] & 3)))+'"'+","+'"'+str("{0:b}".format((w[i] & 3)))+'"'+")")

shuffle(v)

for i in range(len(v)-1) :
    v[i]+=","

testPattern=("\n"+12*" ").join(v)

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE # 
#########################################
params.update({"TESTPATTERN":testPattern,"INST1":inst_name[taskParameter[1]],"INST2":inst_name[taskParameter[2]],"CLK":taskParameter[0]})

###########################
# FILL TESTBENCH TEMPLATE #
###########################
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))


