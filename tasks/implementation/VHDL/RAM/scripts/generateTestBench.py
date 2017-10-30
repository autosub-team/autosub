#!/usr/bin/env python3
import sys
import string
import random
from random import shuffle
from random import randint

from jinja2 import FileSystemLoader, Environment

#################################################################

x=sys.argv[1]
taskParameter=[int(x[0:2])-8,int(x[2:4])-6,int(x[4]),int(x[5]),int(x[6])]

params={}
read_len=0
write_len=0

if taskParameter[3]==0: read_len=taskParameter[0]
elif taskParameter[3]==1: read_len=taskParameter[0]*2
if taskParameter[4]==0: write_len=taskParameter[0]
elif taskParameter[4]==1: write_len=taskParameter[0]*2

########################################
######## GENERATE TESTVECTORS ##########
########################################
random_addr=[]
content_in=[]
content_out=[]
content_test_in=[]
content_test_out=[]

# array of random addresses
a=random.sample(range(0, 2**taskParameter[1]-3), 2**taskParameter[1]-3)
b=[i for i in a if i%2 == 0]
for i in range(0,16):
    random_addr.append('"'+'0'*(taskParameter[1]-len(bin(b[i])[2:]))+bin(b[i])[2:]+'"')
for i in range(len(random_addr)-1):
    random_addr[i]+=","
random_addr=("\n"+(25)*" ").join(random_addr)

# array of random first input data
y = [randint(1,2**write_len)-1 for p in range(0,16)]
for i in y:
    content_in.append('"'+'0'*(write_len-len(bin(i)[2:]))+bin(i)[2:]+'"')

# array of random first output data
for j in y:
    i='0'*(write_len-len(bin(j)[2:]))+bin(j)[2:]
    if taskParameter[3]==0 and taskParameter[4]==0:
        content_out.append('"'+i+'"')
    elif taskParameter[3]==1 and taskParameter[4]==0:
        t='0'*(write_len-len(bin(0)[2:]))+bin(0)[2:]+i
        content_out.append('"'+t+'"')
    elif taskParameter[3]==0 and taskParameter[4]==1:
        content_out.append('"'+i[len(i)-read_len:len(i)]+'"')
    elif taskParameter[3]==1 and taskParameter[4]==1:
        content_out.append('"'+i+'"')

for i in range(len(content_in)-1):
    content_in[i]+=","
content_in=("\n"+(25)*" ").join(content_in)
for i in range(len(content_out)-1):
    content_out[i]+=","
content_out=("\n"+(25)*" ").join(content_out)

# array of random second input data
y = [randint(1,2**write_len-1) for p in range(0,16)]
for i in y:
    content_test_in.append('"'+'0'*(write_len-len(bin(i)[2:]))+bin(i)[2:]+'"')

# array of random second output data
for j in y:
    i='0'*(write_len-len(bin(j)[2:]))+bin(j)[2:]
    if taskParameter[3]==0 and taskParameter[4]==0:
        content_test_out.append('"'+i+'"')
    elif taskParameter[3]==1 and taskParameter[4]==0:
        t='0'*(write_len-len(bin(0)[2:]))+bin(0)[2:]+i
        content_test_out.append('"'+t+'"')
    elif taskParameter[3]==0 and taskParameter[4]==1:
        content_test_out.append('"'+i[len(i)-read_len:len(i)]+'"')
    elif taskParameter[3]==1 and taskParameter[4]==1:
        content_test_out.append('"'+i+'"')

for i in range(len(content_test_in)-1):
    content_test_in[i]+=","
content_test_in=("\n"+(25)*" ").join(content_test_in)
for i in range(len(content_test_out)-1):
    content_test_out[i]+=","
content_test_out=("\n"+(25)*" ").join(content_test_out)

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################
params.update({"READLENGTH":str(read_len-1),"ADDRLENGTH":str(taskParameter[1]-1),"WRITELENGTH":str(write_len-1),
               "DATASIZE":str(taskParameter[0]),"RANDOM_ADDR":random_addr,"CONTENT_IN1":content_in,"CONTENT_OUT1":content_out,
               "CONTENT_IN2":content_test_in,"CONTENT_OUT2":content_test_out})

###########################
# FILL TESTBENCH TEMPLATE #
###########################
if taskParameter[2]==0:
    filename ="testbench_template_1.vhdl"
elif taskParameter[2]==1:
    filename ="testbench_template_2.vhdl"
elif taskParameter[2]==2:
    filename ="testbench_template_3.vhdl"
elif taskParameter[2]==3:
    filename ="testbench_template_4.vhdl"

env = Environment()
env.loader = FileSystemLoader('templates/')
template = env.get_template(filename)
template = template.render(params)

print(template)
