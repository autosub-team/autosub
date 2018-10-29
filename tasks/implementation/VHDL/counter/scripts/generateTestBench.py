#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task counter
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) Gilbert Markum,
#               Martin Mosbeck <martin.mosbeck@tuwien.ac.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

#################################################################

import sys
import string
from random import randrange
from math import ceil, log

from jinja2 import FileSystemLoader, Environment

# only for testing:
#IN1_width = 2  #( from: 2-10 -> 9 )
#num_out   = 3  #( from: 3-7  -> 5 )

###################################################################

# function to generate N unique test vectors, sorted from low to high
def generate_test_vectors(n, N):
	selects = [0] * N
	n_2 = pow(2,n)

	for i in range(N) :
		is_unique = 0
		while is_unique == 0:
			is_unique = 1
			selects[i] = randrange(n_2); #between 0 and (2^n)-1
			for j in range(i) :
				if selects[j] == selects[i] :
					is_unique = 0

	return selects

#################################################################
params={}

task_parameters=sys.argv[1]
counter_width, init_value, synchronous_function, asynchronous_function, enable, overflow, constant_value = task_parameters.split('|')
counter_width = int(counter_width)
synchronous_function = int(synchronous_function)
asynchronous_function = int(asynchronous_function)
enable = int(enable)
overflow = int(overflow)

# calculate values derived of the task parameters:

input_necessary=0
if ((synchronous_function == 2) or (asynchronous_function == 2)):
	input_necessary=1

sync_async_variations=["Clear","LoadConstant","LoadInput"]
sync_variation = sync_async_variations[synchronous_function]
async_variation = sync_async_variations[asynchronous_function]

counter_max = pow(2,counter_width) -1 # calculate highest value for counter

# generate input test data:
input_test_array = generate_test_vectors(counter_width, 3)

# calculate random counter value which is not equal to any member of the input_test_array or constant value:
random_counter_value = randrange(1, counter_max) # [1,(counter_max-1)]
while ((random_counter_value == (int(constant_value))) or \
       (random_counter_value == (input_test_array[0])) or \
       (random_counter_value == (input_test_array[1])) or \
       (random_counter_value == (input_test_array[2]))):
	random_counter_value = randrange(1, counter_max) # [1,(counter_max-1)]

# convert from integer list to a binary list with zero padding suited for the counter_width:
input_test_array = [format(x, '0'+str(counter_width)+'b') for x in input_test_array]

# format for the VHDL syntax:
input_test_array = (', '.join('\n\t"' + x + '"' for x in input_test_array))

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################

params.update({"enable":enable, "sync_variation":sync_variation, \
    "async_variation":async_variation, "counter_width":counter_width, \
    "overflow":overflow, "input_necessary":input_necessary, \
    "random_counter_value":random_counter_value, "init_value":init_value, \
    "counter_width":counter_width, "counter_max":counter_max, \
    "input_test_array":input_test_array, "constant_value":constant_value, \
    "constant_value_bin":str(int(constant_value, 2))})

###########################
# FILL TESTBENCH TEMPLATE #
###########################
env = Environment(trim_blocks = True, lstrip_blocks = True)
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"

template = env.get_template(filename)
template = template.render(params)

print(template)
