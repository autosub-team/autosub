#!/usr/bin/env python3

#################################################################################
# generateTestBench.py for VHDL task demux
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2015, 2016 Martin Mosbeck <martin.mosbeck@gmx.at>, Gilbert Markum
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
#################################################################################

import sys
import string
from random import randrange
from math import ceil, log

from jinja2 import FileSystemLoader, Environment

# only for testing:
#IN1_width = 2  #( from: 2-10 -> 9 ) 
#num_out   = 3  #( from: 3-7  -> 5 )

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

task_parameters=sys.argv[1]
IN1_width, num_out = task_parameters.split('|')
IN1_width = int(IN1_width)
num_out = int(num_out)

# calculate values derived of the task parameters:

SEL_width = ceil(log(num_out,2)) # calculate width of SEL

SEL_max = pow(2,SEL_width) # calculate highest value for SEL

# SEL_test_array generation:
SEL_test_array = range(0, SEL_max)
SEL_test_array = [format(x, '0'+str(int(SEL_width))+'b') for x in SEL_test_array] # convert from integer list to a binary list with zero padding

# generate num_out outputs for the component declaration
outputs_component = ""
for x in range(1,(num_out+1)):
	outputs_component += "OUT" + str(x) + " : out  std_logic_vector((" + str(IN1_width) + " - 1) downto 0)"
	if x < num_out:
		outputs_component += ";\n"
	if x == num_out:
		outputs_component += ");\n"

# generate num_out output signals
output_signals = ""
for x in range(1,(num_out+1)):
	output_signals += "signal OUT"  + str(x) + ": std_logic_vector((" + str(IN1_width) + " - 1) downto 0);\n"

# generate num_out outputs for port map
outputs_port_map = ""
for x in range(1,(num_out+1)):
	outputs_port_map += "OUT" + str(x) + "=> OUT" + str(x)
	if x < num_out:
		outputs_port_map += ",\n"

# generate num_out signal assignments:
outputs_test_array = ""
for x in range(1,(num_out+1)):
	outputs_test_array += "outputs_test_array(" + str(x-1) + ") <= OUT" + str(x) + ";\n"

# generate test data:
input_test_array = generate_test_vectors(IN1_width, 3)

# format for the VHDL syntax:
input_test_array = (', '.join('\n\t\t"' + x + '"' for x in input_test_array))

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE # 
#########################################

params.update({"IN1_width":IN1_width, "num_out":num_out, "SEL_width":SEL_width, "SEL_max":SEL_max, "input_test_array":input_test_array, "outputs_component":outputs_component, "output_signals":output_signals, "outputs_port_map":outputs_port_map, "outputs_test_array":outputs_test_array })

###########################
# FILL TESTBENCH TEMPLATE #
###########################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"

template = env.get_template(filename)
template = template.render(params)

print(template)
