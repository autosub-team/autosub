#!/usr/bin/env python3

#####################################################################################
# generateTestBench.py for VHDL task register_file
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2015, 2016 Martin  Mosbeck   <martin.mosbeck@gmx.at>, Gilbert Markum
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
#####################################################################################

import sys
import string
from random import randrange
from math import ceil, log

from jinja2 import FileSystemLoader, Environment

###################################################################

# function to generate N unique test vectors for a specified n bit width
def generate_test_vectors(n, N):
	selects = [0] * N
	n_2 = pow(2,n)

	for i in range(N) :
		is_unique = 0
		while is_unique == 0:
			is_unique = 1
			selects[i] = randrange(n_2);
			for j in range(i) :
				if selects[j] == selects[i] :
					is_unique = 0

	selects = [format(x, '0'+str(n)+'b') for x in selects] # convert from integer list to a binary list with zero padding suited for n bit width

	return selects


#################################################################
params={}

taskParameters=sys.argv[1]
n, N_n, special_reg0_size, n_bypass_or_read_priority, reg0_bypass_or_read_priority = taskParameters.split('|')

n = int(n)
N_n = int(N_n)
special_reg0_size = int(special_reg0_size)
n_bypass_or_read_priority = int(n_bypass_or_read_priority)
reg0_bypass_or_read_priority = int(reg0_bypass_or_read_priority)

# calculate values derived of the task parameters:
address_width_n  = int(ceil(log(N_n,2)))
address_width_reg0  = int(ceil(log(special_reg0_size,2)))

address_array_size = max(N_n,special_reg0_size)
address_array_width= max(address_width_n, address_width_reg0)

# generate test data:
data_n_test_array = generate_test_vectors(n, 2 * N_n) # create 2 unique values for each address of the register file

reg0_test_vectors = generate_test_vectors(special_reg0_size, 2) # create 2 unique test vectors for the special register 0
reg0_test_vector_1 = reg0_test_vectors[0]
reg0_test_vector_2 = reg0_test_vectors[1]

# address_test_array generation:
address_test_array = range(0,address_array_size)  # create an array containing all the addresses to be tested
address_test_array = [format(x, '0'+str(int(address_array_width))+'b') for x in address_test_array] # convert from integer list to a binary list with zero padding suited for address_array_width

data_n_test_array =  (', '.join('\n\t\t"' + x + '"' for x in data_n_test_array))
address_test_array = (', '.join('\n\t\t"' + x + '"' for x in address_test_array))

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################
params.update({"n":n, "address_width_n":address_width_n, "N_n":N_n, "address_width_reg0":address_width_reg0, "special_reg0_size":special_reg0_size, "address_array_size":address_array_size, "address_array_width":address_array_width, "address_test_array":address_test_array, "data_n_test_array":data_n_test_array, "reg0_test_vector_1":reg0_test_vector_1, "reg0_test_vector_2":reg0_test_vector_2, "n_bypass_or_read_priority":n_bypass_or_read_priority, "reg0_bypass_or_read_priority":reg0_bypass_or_read_priority })

###########################
# FILL TESTBENCH TEMPLATE #
###########################

env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"

template = env.get_template(filename)
template = template.render(params)

print(template)
