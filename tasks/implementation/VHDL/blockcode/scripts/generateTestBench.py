#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task blockcode_source
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2017 Martin Mosbeck <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

from random import randrange
import string
import sys

from bitstring import Bits
import parity_functions

class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

task_parameters=sys.argv[1]

n, k, chosen_parities = task_parameters.split('|')

params={}

##########################################
######## GENERATE THE TESTVECTORS ########
##########################################

# number of test_vectors = number of test cycles
num_vectors = randrange(10,20)
testVectors= [None] * num_vectors

# initialize all needed arrays to build the test_vectors
new_data = [None] * num_vectors
data = [None] * num_vectors
data_valid = [None] * num_vectors

code = [None] * num_vectors
code_valid = [None] * num_vectors

sink_ready = [None] * num_vectors

#Possible strategy:
#random sink_ready and data, when approach FIFO limit, empty it with:
#    no new data and sink_ready
#how to cover all corner cases, how to compute right cycle for code and
#code_valid?

# assemble the test_vectors
for i in range(0,num_vectors):
    test_vectors.append('("{0}","{1}","{2}","{3}","{4}")'\
        .format(data_valid[i], data[i], sink_ready[i],
                code_valid[i], code[i]))

for i in range(num_vectors-1):
    test_vectors[i]+=","

test_pattern=("\n" + 2*"\t").join(testVectors) #format and join

##########################################
## SET PARAMETERS FOR TESTBENCH TEMPLATE #
##########################################
params.update({"DATALEN":n, "CODELEN":(n+k), "TESTPATTERN": test_pattern})

############################
## FILL TESTBENCH TEMPLATE #
############################
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))
