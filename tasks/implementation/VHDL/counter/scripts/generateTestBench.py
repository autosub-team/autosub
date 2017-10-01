#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task counter
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) Gilbert Markum
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

#################################################################

import sys
import string
from random import randrange
from math import ceil, log

###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

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
			selects[i] = randrange(n_2);
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

counter_max = pow(2,counter_width) # calculate highest value for counter

# generate input test data:
input_test_array = generate_test_vectors(counter_width, 3)

# calculate random counter value which is not equal to any member of the input_test_array-1:
random_counter_value = randrange(counter_max)
while ((random_counter_value == (int(constant_value)-1)) or (random_counter_value == (input_test_array[0]-1)) or (random_counter_value == (input_test_array[1]-1)) or (random_counter_value == (input_test_array[2]-1))):
	random_counter_value = randrange(counter_max)

# convert from integer list to a binary list with zero padding suited for the counter_width:
input_test_array = [format(x, '0'+str(counter_width)+'b') for x in input_test_array]

# format for the VHDL syntax:
input_test_array = (', '.join('\n\t"' + x + '"' for x in input_test_array))

# setup inputs and outputs for the component declaration
entity_in_out = ""
if ( enable == 1):
	entity_in_out += "\t\t\tEnable      : in   std_logic;\n"

entity_in_out += ("\t\t\tSync" + str(sync_variation) + "   : in   std_logic;\n")
entity_in_out += ("\t\t\tAsync" + str(async_variation) + "   : in   std_logic;\n")

if ( input_necessary == 1 ):
	entity_in_out += ("\t\t\tInput       : in   std_logic_vector((" + str(counter_width) + "-1) downto 0);\n")

entity_in_out += ("\t\t\tOutput      : out  std_logic_vector((" +  str(counter_width) + "-1) downto 0)")

if ( overflow == 1):
	entity_in_out += ";\n"
	entity_in_out += "\t\t\tOverflow    : out  std_logic"


# setup input and output signals
signal_in_out = ""
if ( enable == 1):
	signal_in_out += "\tsignal Enable : std_logic := '0';\n"

signal_in_out += "\tsignal Sync"+ sync_variation + " : std_logic := '0';\n"
signal_in_out += "\tsignal Async"+ async_variation+ " : std_logic := '0';\n"

if ( input_necessary == 1 ):
	signal_in_out += "\tsignal Input  : std_logic_vector((" +str(counter_width)+"-1) downto 0);\n"

signal_in_out += "\tsignal Output: std_logic_vector((" +str(counter_width)+ "-1) downto 0);\n"

if ( overflow == 1):
	signal_in_out += "\tsignal Overflow : std_logic := '0';\n"

# setup inputs and outputs for port map
port_map_in_out = ""
if ( enable == 1):
	port_map_in_out += "\t\t\tEnable => Enable,\n"

port_map_in_out += "\t\t\tSync" + sync_variation + " => Sync" + sync_variation + ",\n"
port_map_in_out += "\t\t\tAsync" + async_variation + " => Async" + async_variation + ",\n"

if ( input_necessary == 1 ):
	port_map_in_out += "\t\t\tInput => Input,\n"

port_map_in_out += "\t\t\tOutput => Output"

if ( overflow == 1):
	port_map_in_out += ",\n"
	port_map_in_out += "\t\t\tOverflow => Overflow"

enable_check_code = ""
if ( enable == 1):
	enable_check_code += """		-- do the enable check
		Enable <= '0';
		for i in (init_value + 1) to (""" +str(counter_max)+ """-1) loop
			if (Output /= std_logic_vector(to_unsigned(init_value, Output'length))) then
				report "§{Counter value changed while Enable = '0'. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(init_value, Output'length))) & ".}§" severity failure;
			end if;
			wait for CLK_period;
		end loop;
		Enable <= '1';
		wait for CLK_period;"""

overflow_check_code = ""
if ( overflow == 1):
	overflow_check_code += """		-- do the overflow underflow check
		wait for CLK_period;
		for i in 1 to (counter_max-1) loop
			if (Overflow /= '0') then
				report "§{Overflow was '" & std_logic'image(Overflow) & "' when it was expected to be '0'. Current counter value is " & image(Output) & ".}§" severity failure;
			end if;
			wait for CLK_period;
		end loop;

		if (Overflow /= '1') then
			report "§{Overflow was '" & std_logic'image(Overflow) & "' when it was expected to be '1'. Current counter value is " & image(Output) & ".}§" severity failure;
		end if;
		for i in 0 to (counter_max-2) loop
			wait for CLK_period;
			if (Overflow /= '0') then
				report "§{Overflow was '" & std_logic'image(Overflow) & "' when it was expected to be '0'. Current counter value is " & image(Output) & ".}§" severity failure;
			end if;
		end loop;
		wait for CLK_period;
		"""

if ( synchronous_function == 0 ):
	synchronous_value_integer_vector = "std_logic_vector(to_unsigned(0, Output'length))"
	synchronous_value_integer = "0"
elif ( synchronous_function == 1 ):
	synchronous_value_integer_vector = "\"" + constant_value + "\""
	synchronous_value_integer = str(int(constant_value, 2))
elif ( synchronous_function == 2 ):
	synchronous_value_integer_vector = "input_test_array(j)"
	synchronous_value_integer = "to_integer(unsigned(input_test_array(j)))"

synchronous_check_code = ""
synchronous_check_code += "		-- do the synchronous check:\n"
if ( synchronous_function == 2 ):
	synchronous_check_code += """for j in 0 to 2 loop
			Input <= input_test_array(j);\n"""

synchronous_check_code += """		for i in 0 to random_counter_value loop
			wait for CLK_period;
		end loop;

		Sync""" + sync_variation + """ <= '1';
		wait for CLK_period/4;
		if (Output = """ + synchronous_value_integer_vector + """) then
			report "§{Sync""" + sync_variation + """ not synchronous to CLK. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(random_counter_value, Output'length))) & ".}§" severity failure;
		end if;
		wait for CLK_period*3/4;
		if (Output /= """ + synchronous_value_integer_vector + """) then
			report "§{Sync""" + sync_variation + """ not setting the right Output value. Received " & image(Output) & ". Expected " & image(""" + synchronous_value_integer_vector + """) & ".}§" severity failure;
		end if;
		wait for CLK_period/4;
		Sync""" + sync_variation + """ <= '0';
		wait for CLK_period*3/4;

		for i in (""" + synchronous_value_integer + """+1) to (counter_max-1) loop
			if (Output /= std_logic_vector(to_unsigned(i, Output'length))) then
				report "§{Wrong Output value after Sync""" + sync_variation + """. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(i, Output'length))) & ".}§" severity failure;
			end if;
			wait for CLK_period;
		end loop;\n"""

if ( synchronous_function == 2 ):
	synchronous_check_code += "		end loop;"

if ( asynchronous_function == 0 ):
	asynchronous_value_integer_vector = "std_logic_vector(to_unsigned(0, Output'length))"
	asynchronous_value_integer = "0"
elif ( asynchronous_function == 1 ):
	asynchronous_value_integer_vector = "\"" + constant_value + "\""
	asynchronous_value_integer = str(int(constant_value, 2))
elif ( asynchronous_function == 2 ):
	asynchronous_value_integer_vector = "input_test_array(j)"
	asynchronous_value_integer = "to_integer(unsigned(input_test_array(j)))"

asynchronous_check_code = ""
asynchronous_check_code += "		-- do the asynchronous check:\n"
if ( asynchronous_function == 2 ):
	asynchronous_check_code += """		for j in 0 to 2 loop
			Input <= input_test_array(j);\n"""

asynchronous_check_code += """		for i in 0 to random_counter_value loop
			wait for CLK_period;
		end loop;

		Async""" + async_variation + """ <= '1';
		wait for CLK_period/4;
		if (Output /= """ + asynchronous_value_integer_vector + """) then
			report "§{Async""" + async_variation + """ not setting the right Output value. Received " & image(Output) & ". Expected " & image(""" + asynchronous_value_integer_vector + """) & ".}§" severity failure;
		end if;
		wait for CLK_period/4;
		Async""" + async_variation + """ <= '0';
		wait for CLK_period/2;

		for i in (""" + asynchronous_value_integer + """+1) to (counter_max-1) loop
			if (Output /= std_logic_vector(to_unsigned(i, Output'length))) then
				report "§{Wrong Output value after Async""" + async_variation + """. Received " & image(Output) & ". Expected " & image(std_logic_vector(to_unsigned(i, Output'length))) & ".}§" severity failure;
			end if;
			wait for CLK_period;
		end loop;\n"""

if ( asynchronous_function == 2 ):
	asynchronous_check_code += "		end loop;"

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################

params.update({"entity_in_out":entity_in_out, "random_counter_value":random_counter_value, "init_value":init_value, "counter_width":counter_width, "counter_max":counter_max, "input_test_array":input_test_array, "signal_in_out":signal_in_out, "port_map_in_out":port_map_in_out, "enable_check_code":enable_check_code, "overflow_check_code":overflow_check_code, "synchronous_check_code":synchronous_check_code, "asynchronous_check_code":asynchronous_check_code })

###########################
# FILL TESTBENCH TEMPLATE #
###########################
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))