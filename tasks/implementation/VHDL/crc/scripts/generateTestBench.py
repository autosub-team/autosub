#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task crc
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
import string
from random import randrange
from crcGenerator import genCRC
from bitstring import Bits

from jinja2 import FileSystemLoader, Environment
#################################################################

taskParameters=sys.argv[1]
params={}


msgLen, genDegree, generator = taskParameters.split('|')
crcWidth=len(generator)-1
msgLen=int(msgLen)

#print(str(msgLen)+" "+str(genDegree)+" " +str(generator)+" "+genString)


##########################################
######## GENERATE THE TESTVECTORS ########
##########################################
numVectors = randrange(10,20);
testVectors=[]

for i in range(0,numVectors):
    msg= Bits(uint=randrange(0,2**msgLen),length=msgLen).bin;
    crc= genCRC(msg,generator)

    testVectors.append('("{0}","{1}")'.format(msg,crc))

for i in range(numVectors-1):
    testVectors[i]+=","

testPattern=("\n"+12*" ").join(testVectors) #format and join

##########################################
## SET PARAMETERS FOR TESTBENCH TEMPLATE #
##########################################
params.update({"CRCWIDTH":crcWidth,"MSGLEN":msgLen,"TESTPATTERN":testPattern})

############################
## FILL TESTBENCH TEMPLATE #
############################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"
template = env.get_template(filename)
template = template.render(params)

print(template)

