#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task blockcode_source
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2017 Martin Mosbeck <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################
import random
from random import randrange

import string
import sys

from bitstring import Bits

import parity_functions

class MyTemplate(string.Template):
    delimiter = "%%"

# for generation of testvectors
class CycleValues(object):
    def __init__ (self, data_len, code_len):
        self.data = data_len * "0"
        self.data_valid = "0"
        self.sink_ready = "0"
        self.code = code_len * "-"
        self.code_valid = "0"
        self.next_action = None
#################################################################

task_parameters=sys.argv[1]

n, k, chosen_parities = task_parameters.split('|')
chosen_parities = eval(chosen_parities)
n = int(n)
k = int(k)

params={}

##########################################
######## GENERATE THE TESTVECTORS ########
##########################################

# set up equations
parity_equations = parity_functions.create_parity_equations(chosen_parities)

# 20 cycles to test + 1 initial + 1 after state
num_cycles = 20 + 2

# first cyle is initial state
cycle_values = [CycleValues(k, n) for i in range(0,num_cycles)]

fifo = []
#print("num_cycles= " + str(num_cycles) + "\n")

fill_max_at = randrange(0,5)
empty_zero_at = randrange(10, 15)

cycle_values[fill_max_at].next_action = "fill_max"
cycle_values[empty_zero_at].next_action = "empty_zero"

#print("fill at cycle " + str(fill_max_at))
#print("empty at cycle " + str(empty_zero_at))
#print("\n")

# only loop from 1 up to last - 1
for i in range(0,len(cycle_values)-1):
    cur_cycle = cycle_values[i]
    next_cycle = cycle_values[i+1]

    if cur_cycle.data_valid == "1":
        fifo.append(cur_cycle.data)

    # resulting from entity
    sending = (cur_cycle.code_valid == "1")
    transmission_success = sending and (cur_cycle.sink_ready == '1');
    code_available = ( len(fifo) > 0 )

    if ((not sending) or transmission_success) and code_available:
        data_string = fifo.pop(0)
        data_bits = list(data_string)
        data = [int(number) for number in list(data_bits)]
        parity = parity_functions.create_parity_check(parity_equations,
                                                      data)
        next_cycle.code = data_string + parity
        next_cycle.code_valid = "1"
        #print("next_new")
    elif sending and not transmission_success:
        next_cycle.code = cur_cycle.code
        next_cycle.code_valid = cur_cycle.code_valid
        #print("next_stay")
    else:
        next_cycle.code = cur_cycle.code
        next_cycle.code_valid = "0"
        #print("next_idle")

    fifo_state = len(fifo)

    if cur_cycle.next_action == "fill_max":
        if fifo_state == 3:
            possible_actions = ["empty", "keep"]
            cur_cycle.next_action = random.choice(possible_actions)
        else:
            cur_cycle.next_action = "fill"
            next_cycle.next_action = "fill_max"

    elif cur_cycle.next_action == "empty_zero":
        if fifo_state == 0:
            cur_cycle.next_action = "empty"
        else:
            cur_cycle.next_action = "empty"
            next_cycle.next_action = "empty_zero"
    else:
        if fifo_state == 3:
            possible_actions = ["empty", "keep"]
            # possible_actions = ["empty"]
        else:
            possible_actions = ["fill", "empty", "keep"]
            # possible_actions = ["fill"]

        cur_cycle.next_action = random.choice(possible_actions)

    # from testbench
    if(cur_cycle.next_action == "fill"):
        next_cycle.data = Bits(uint=randrange(0,2**k),length=k).bin
        next_cycle.data_valid = "1"
        next_cycle.sink_ready = "0"
    elif(cur_cycle.next_action == "empty"):
        next_cycle.data = cur_cycle.data
        next_cycle.data_valid = "0"
        next_cycle.sink_ready = "1"
    elif(cur_cycle.next_action == "keep"):
        next_cycle.data = Bits(uint=randrange(0,2**k),length=k).bin
        next_cycle.data_valid = "1"
        next_cycle.sink_ready = "1"

    #print("fifo_state= " + str(fifo_state))
    #print("fifo= " + str(fifo))
    #print("data= " + cycle_values[i].data)
    #print("data_valid= " + cycle_values[i].data_valid)
    #print("sink_ready= " + cycle_values[i].sink_ready)
    #print("code = " + cycle_values[i].code)
    #print("code_valid = " + cycle_values[i].code_valid)
    #print("next_action= " + cycle_values[i].next_action)
    #print("----------------------------------\n")

# assemble the test_vectors
test_vectors= []

for i in range(1,num_cycles-1):
    test_vectors.append('("{0}","{1}","{2}","{3}","{4}")'\
        .format(cycle_values[i].data_valid, cycle_values[i].data,
                cycle_values[i].sink_ready, cycle_values[i].code_valid,
                cycle_values[i].code))

for i in range(0,len(test_vectors)-1):
    test_vectors[i]+=","

test_pattern=("\n" + 2*"\t").join(test_vectors) #format and join

##########################################
## SET PARAMETERS FOR TESTBENCH TEMPLATE #
##########################################
params.update({"DATALEN":k, "CODELEN":n, "TESTPATTERN": test_pattern})

############################
## FILL TESTBENCH TEMPLATE #
############################
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))
