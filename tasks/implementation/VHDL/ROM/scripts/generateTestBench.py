#!/usr/bin/env python3
import sys
import string
import random
from random import shuffle

from jinja2 import FileSystemLoader, Environment

#################################################################

x=str(sys.argv[1])
l = len(x)
tmp=x[l-8:l]
taskParameter=[int(tmp[0]),int(tmp[1])+8,int(tmp[2])+8,int(tmp[3:6])-50,int(tmp[6:8])]
y=bin(int(x[0:l-8]))
z=y[2:]
z=z.zfill(taskParameter[2]*taskParameter[4])
params={}
clk =['falling_edge','rising_edge']

#########################################
######### GENERATE TESTVECTORS ##########
#########################################
instructions=[]
random_num=[]

for i in range(0,len(z)-1,taskParameter[2]):
    instructions.append('"'+z[i:i+taskParameter[2]]+'"')

for i in range(len(instructions)-1):
    instructions[i]+=","

instructions=("\n"+(28)*" ").join(instructions)

random_tmp=random.sample(range(taskParameter[3], taskParameter[3]+taskParameter[4]),taskParameter[4])
for i in range(0,taskParameter[4]):
    random_num.append(str(random_tmp[i]))

for i in range(len(random_num)-1):
    random_num[i]+=","

random_num=("\n"+(28)*" ").join(random_num)

if taskParameter[0]==0:
    main_clk='falling edge'
    opposite_clk ='rising edge'
elif taskParameter[0]==1:
    main_clk='rising edge'
    opposite_clk ='falling edge'
#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################
params.update({"CLK":clk[taskParameter[0]],"mainClk":main_clk,"oppositeClk":opposite_clk,
	       "OPPOSITECLK":clk[abs(taskParameter[0]-1)],"RANDOM":str(random_num),
	       "INSTRUCTIONLENGTH":str(taskParameter[2]-1),"ADDRLENGTH":str(taskParameter[1]-1),
	       "ADDRESSLENGTH":str(taskParameter[1]),"ROMSIZE":str(taskParameter[1]**2-1),"START":str(taskParameter[3]),
	       "DATALENGTH":str(taskParameter[4]-1),"INSTRUCTIONS":instructions})

###########################
# FILL TESTBENCH TEMPLATE #
###########################
filename ="testbench_template.vhdl"
env = Environment()
env.loader = FileSystemLoader('templates/')
template = env.get_template(filename)
template = template.render(params)

print(template)
