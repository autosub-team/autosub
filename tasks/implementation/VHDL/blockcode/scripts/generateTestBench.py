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
import itertools

import parity_functions

from jinja2 import FileSystemLoader, Environment

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

fill_max_at = randrange(0,5)
fill_max_at = 0
empty_zero_at = randrange(10, 15)

cycle_values[fill_max_at].next_action = "fill_max"
cycle_values[empty_zero_at].next_action = "empty_zero"

# so we also see this in the testbench
testing_comment = "fill max at cycle " + str(fill_max_at + 1) + \
                  " ; empty to zero at cycle " + str(empty_zero_at + 1)
print("--" + testing_comment +"\n")

# IMPORTANT:
# To get a codeword one cycle after it was input the entity will have to
# use a write then read strategy! This has to be held in thougt for next actions

# we want different datas for each data_valid, makes debuging easier
possible_data = ["".join(seq) for seq in itertools.product("01", repeat=k)]

# only loop from 1 up to last - 1
for i in range(0,len(cycle_values)-1):
    cur_cycle = cycle_values[i]
    next_cycle = cycle_values[i+1]

    #################
    # WRITE TO FIFO #
    #################
    if cur_cycle.data_valid == "1":
        fifo.append(cur_cycle.data)

    ###################################
    # READ FROM FIFO, APPLY NEXT CODE #
    ###################################
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
    elif sending and not transmission_success:
        next_cycle.code = cur_cycle.code
        next_cycle.code_valid = cur_cycle.code_valid
    else:
        next_cycle.code = '-' * n
        next_cycle.code_valid = "0"

    ##################
    # PLAN NEXT STEP #
    ##################
    fifo_state = len(fifo)

    if cur_cycle.next_action == "fill_max":
        if fifo_state == 3:
            possible_actions = ["empty"]
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
            possible_actions = ["empty"]
        else:
            possible_actions = ["fill", "empty", "keep"]

        cur_cycle.next_action = random.choice(possible_actions)

    # from testbench
    if(cur_cycle.next_action == "fill"):
        random_data_index = randrange(0, len(possible_data))
        next_cycle.data = possible_data[random_data_index]
        del possible_data[random_data_index]
        next_cycle.data_valid = "1"
        next_cycle.sink_ready = "0"
    elif(cur_cycle.next_action == "empty"):
        next_cycle.data = cur_cycle.data
        next_cycle.data_valid = "0"
        next_cycle.sink_ready = "1"
    elif(cur_cycle.next_action == "keep"):
        random_data_index = randrange(0, len(possible_data))
        next_cycle.data = possible_data[random_data_index]
        del possible_data[random_data_index]
        next_cycle.data_valid = "1"
        next_cycle.sink_ready = "1"


    print("--" + str(i).zfill(2)+ ": fifo_state= " + str(fifo_state) +  "  next_action= " + cycle_values[i].next_action)
    #print("fifo= " + str(fifo))
    #print("data= " + cycle_values[i].data)
    #print("data_valid= " + cycle_values[i].data_valid)
    #print("sink_ready= " + cycle_values[i].sink_ready)
    #print("code = " + cycle_values[i].code)
    #print("code_valid = " + cycle_values[i].code_valid)
    print("----------------------------------")

# assemble the test_vectors
test_vectors= []

for i in range(1,num_cycles-1):
    test_vectors.append('(\'{0}\',"{1}",\'{2}\',\'{3}\',"{4}")'\
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
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"
template = env.get_template(filename)
template = template.render(params)
print(template)
