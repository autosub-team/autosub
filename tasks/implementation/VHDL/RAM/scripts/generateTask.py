#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task RAM
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) 2016 Hedyeh Agheh Kholerdi   <hedyeh.kholerdi@tuwien.ac.at>
########################################################################

import random
import string
import sys
from random import randint
from random import choice

from jinja2 import FileSystemLoader, Environment

import json

#################################################################

userId=sys.argv[1]
taskNr=sys.argv[2]
submissionEmail=sys.argv[3]
language=sys.argv[4]

x = []

###################################
## IMPORT LANGUAGE TEXT SNIPPETS ##
###################################

filename ="templates/task_description/language_support_files/lang_snippets_{0}.json".format(language)
with open(filename) as data_file:
    lang_data = json.load(data_file)
####################################

x.append(choice(range(8, 20, 2)))    # length of each location in RAM
x.append(random.randint(6, 12))   # length of address
x.append(random.randint(0, 3))   # number of write and read actions. Based on variable 'actions' below
x.append(random.randint(0, 1)) # length of data that is read each time. 0:word, 1:double word
x.append(random.randint(0, 1)) # length of data that is written each time. 0:word, 1:double word

actions=["one read and two writes","two reads and one write","two reads and two writes","one read and one write at the same time"]

###############################
## PARAMETER SPECIFYING TASK ##
###############################
taskParameters = str(x[0]+8)+str(x[1]+6)+str(x[2])+str(x[3])+str(x[4])

###############################################
############### ONLY FOR TESTING ##############
###############################################
filename ="tmp/solution_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + taskParameters + "\n")

###########################################
# SET PARAMETERS FOR ENTITY FILE TEMPLATE #
###########################################
paramsEntity={}
read_len=0
write_len=0
Desc4="%"
Desc5="%"
Desc6="%"
Desc7="%"

if x[3]==0:
    read_len=x[0]
    Desc6=""

elif x[3]==1:
    read_len=x[0]*2
    Desc7=""

if x[4]==0:
    write_len=x[0]
    Desc4=""

elif x[4]==1:
    write_len=x[0]*2
    Desc5=""


entity=[]
if x[2]==0:
    entity.append("en_read : in std_logic;")
    entity.append("en_write1 : in std_logic;")
    entity.append("en_write2 : in std_logic;")
    entity.append("input1 : in std_logic_vector("+str(write_len-1)+" downto 0);")
    entity.append("input2 : in std_logic_vector("+str(write_len-1)+" downto 0);")
    entity.append("output : out std_logic_vector("+str(read_len-1)+" downto 0)")

elif x[2]==1:
    entity.append("en_read1 : in std_logic;")
    entity.append("en_read2 : in std_logic;")
    entity.append("en_write : in std_logic;")
    entity.append("input : in std_logic_vector("+str(write_len-1)+" downto 0);")
    entity.append("output1 : out std_logic_vector("+str(read_len-1)+" downto 0);")
    entity.append("output2 : out std_logic_vector("+str(read_len-1)+" downto 0)")

elif x[2]==2:
    entity.append("en_read1 : in std_logic;")
    entity.append("en_read2 : in std_logic;")
    entity.append("en_write1 : in std_logic;")
    entity.append("en_write2 : in std_logic;")
    entity.append("input1 : in std_logic_vector("+str(write_len-1)+" downto 0);")
    entity.append("input2 : in std_logic_vector("+str(write_len-1)+" downto 0);")
    entity.append("output1 : out std_logic_vector("+str(read_len-1)+" downto 0);")
    entity.append("output2 : out std_logic_vector("+str(read_len-1)+" downto 0)")

elif x[2]==3:
    entity.append("en_read : in std_logic;")
    entity.append("en_write : in std_logic;")
    entity.append("input : in std_logic_vector("+str(write_len-1)+" downto 0);")
    entity.append("output : out std_logic_vector("+str(read_len-1)+" downto 0)")


#for i in range(len(entity)-1):
    #entity[i]+=","

entity=("\n"+(10)*" ").join(entity)

paramsEntity.update({"ADDRLENGTH":str(x[1]-1),"ENTITY":entity})

##########################
### CHANGE ENTITY FILE ###
##########################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="RAM_template.vhdl"
template = env.get_template(filename)
template = template.render(paramsEntity)

filename ="tmp/RAM_{0}_Task{1}.vhdl".format(userId,taskNr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################
paramsDesc={}
enRead=""

RW12=lang_data["RW"][0]
RW21=lang_data["RW"][1]
RW22=lang_data["RW"][2]
WW22=lang_data["WW"][0]
WR12=lang_data["WR"][0]
WR21=lang_data["WR"][1]
WR22=lang_data["WR"][2]

if x[2]==0:
    enRead="%"
    enReadIndex=""
    enWrite=""
    enWriteIndex="1"
    in2=""
    inIndex="1"
    out2="%"
    outIndex=""
    Desc0=""
    Desc1="%"
    Desc2="%"
    Desc3="%"

elif x[2]==1:
    enRead=""
    enReadIndex="1"
    enWrite="%"
    enWriteIndex=""
    in2="%"
    inIndex=""
    out2=""
    outIndex="1"
    Desc0="%"
    Desc1=""
    Desc2="%"
    Desc3="%"

elif x[2]==2:
    enRead=""
    enReadIndex="1"
    enWrite=""
    enWriteIndex="1"
    in2=""
    inIndex="1"
    out2=""
    outIndex="1"
    Desc0="%"
    Desc1="%"
    Desc2=""
    Desc3="%"

elif x[2]==3:
    enRead="%"
    enReadIndex=""
    enWrite="%"
    enWriteIndex=""
    in2="%"
    inIndex=""
    out2="%"
    outIndex=""
    Desc0="%"
    Desc1="%"
    Desc2="%"
    Desc3=""

### single and double
if (x[3]==0 and x[4]==0):
    RW12=""
    RW21=""
    RW22=""
    WW22=""
    WR12=""
    WR21=""
    WR22=""

elif (x[3]==1 and x[4]==0):
    RW21=""
    RW22=""
    WW22=""
    WR21=""
    WR22=""
elif (x[3]==0 and x[4]==1):
    RW12=""
    RW22=""
    WR12=""
    WR22=""

elif (x[3]==1 and x[4]==1):
    RW12=""
    RW21=""
    WR12=""
    WR21=""

paramsDesc.update({"ENREAD":enRead,"enReadIndex":enReadIndex,"ENWRITE":enWrite,
                   "enWriteIndex":enWriteIndex,"IN2":in2,"inIndex":inIndex,"OUT2":out2,"outIndex":outIndex,
                   "ADDRLENGTH":str(x[1]),"WRITELENGTH":str(write_len),"READLENGTH":str(read_len),
                   "Desc0":Desc0,"Desc1":Desc1,"Desc2":Desc2,"Desc3":Desc3,"DATASIZE":str(x[0]),
                   "Desc4":Desc4,"Desc5":Desc5,"Desc6":Desc6,"Desc7":Desc7,
                   "TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})

paramsDesc.update({"RW12":RW12,"RW21":RW21,"RW22":RW22,"WW22":WW22,
		   "WR12":WR12,"WR21":WR21,"WR22":WR22})

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
env.loader = FileSystemLoader('templates/')
filename ="task_description/task_description_template_{0}.tex".format(language)
template = env.get_template(filename)
template = template.render(paramsDesc)

filename ="tmp/desc_{0}_Task{1}.tex".format(userId,taskNr)
with open (filename, "w") as output_file:
    output_file.write(template)

########################################
######## GENERATE TESTVECTORS ##########
########################################
random_addr=[]
content_in=[]
content_out=[]
content_test_in=[]
content_test_out=[]
paramsExam={}

# array of random addresses
a=random.sample(range(0, 2**x[1]-3), 2**x[1]-3)
b=[i for i in a if i%2 == 0]
for i in range(0,16):
    random_addr.append('"'+'0'*(x[1]-len(bin(b[i])[2:]))+bin(b[i])[2:]+'"')
for i in range(len(random_addr)-1):
    random_addr[i]+=","
random_addr=("\n"+(25)*" ").join(random_addr)

# array of random first input data
y = [randint(0,2**write_len)-1 for p in range(0,16)]
for i in y:
    content_in.append('"'+'0'*(write_len-len(bin(i)[2:]))+bin(i)[2:]+'"')

for i in range(len(content_in)-1):
    content_in[i]+=","
content_in=("\n"+(25)*" ").join(content_in)

# array of random second input data
y = [randint(0,2**write_len-1) for p in range(0,16)]
for i in y:
    content_test_in.append('"'+'0'*(write_len-len(bin(i)[2:]))+bin(i)[2:]+'"')

for i in range(len(content_test_in)-1):
    content_test_in[i]+=","
content_test_in=("\n"+(25)*" ").join(content_test_in)

########################################
### SET PARAMETERS FOR EXAM TEMPLATE ###
########################################
paramsExam.update({"READLENGTH":str(read_len-1),"ADDRLENGTH":str(x[1]-1),"WRITELENGTH":str(write_len-1),
               "RANDOM_ADDR":random_addr,"CONTENT_IN1":content_in,
               "CONTENT_IN2":content_test_in})

##########################
### FILL EXAM TEMPLATE ###
##########################
if x[2]==0:
    filename ="testbench_exam_1.vhdl"
elif x[2]==1:
    filename ="testbench_exam_2.vhdl"
elif x[2]==2:
    filename ="testbench_exam_3.vhdl"
elif x[2]==3:
    filename ="testbench_exam_4.vhdl"

env = Environment()
env.loader = FileSystemLoader('templates/')
template = env.get_template(filename)
template = template.render(paramsExam)

filename ="tmp/RAM_tb_exam_{0}_Task{1}.vhdl".format(userId,taskNr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################
### PRINT TASKPARAMETERS ##
###########################
print(taskParameters)
