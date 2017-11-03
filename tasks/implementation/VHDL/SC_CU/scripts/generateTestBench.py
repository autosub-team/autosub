#!/usr/bin/env python3

#####################################################################################
# generateTestBench.py for VHDL task SC_CU
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2015, 2016 Martin  Mosbeck   <martin.mosbeck@gmx.at>, Gilbert Markum
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
#####################################################################################

import sys
import string
from random import shuffle

from jinja2 import FileSystemLoader, Environment


#################################################################
params={}

sel_Inputs = []
sel_Controls=[]
sel_Strings =[]

taskParameters=sys.argv[1]
In_1, In_2, In_3, In_4 = taskParameters.split('|')

In_1 = int(In_1)
In_2 = int(In_2)
In_3 = int(In_3)
In_4 = int(In_4)

# Inputs= Opcode & Funct & Zero :
Inputs=	["\"0000001000000\"",  # add
		 "\"0000001000100\"",  # sub
		 "\"0000001001000\"",  # and
		 "\"0000001001010\"",  # or
		 "\"0000001001100\"",  # xor
		 "\"0000001001110\"",  # nor
		 "\"0000001010100\"",  # slt
		 "\"100011------0\"",  # lw
		 "\"101011------0\"",  # sw
		 "\"000010------0\"",  # j
		 "\"000100------1\"",  # beq, Zero = 1
		 "\"000100------0\"",  # beq, Zero = 0
		 "\"000101------1\"",  # bne, Zero = 1
		 "\"000101------0\"" ] # bne, Zero = 0

# Controls = RegDst & Branch & Jump & MemRead & MemtoReg & MemWrite & ALUControl & ALUSrc & RegWrite :
Controls=  ["\"10000000001\"",     # add
		"\"10000001001\"",     # sub
		"\"10000010001\"",     # and
		"\"10000010101\"",     # or
		"\"10000011001\"",     # xor
		"\"10000011101\"",     # nor
		"\"10000000101\"",     # slt
		"\"00011000011\"",     # lw
		"\"-000-100010\"",     # sw
		"\"-010-0----0\"",     # j
		"\"-100-001000\"",     # beq, Zero = 1
		"\"-000-001000\"",     # beq, Zero = 0
		"\"-000-001000\"",     # bne, Zero = 1
		"\"-100-001000\""]     # bne, Zero = 0

Strings=   ["\"add\"",
            "\"sub\"",
            "\"and\"",
            "\"or \"",
            "\"xor\"",
            "\"nor\"",
            "\"slt\"",
            "\"lw \"",
            "\"sw \"",
            "\"j  \"",
            "\"beq\"",
            "\"beq\"",
            "\"bne\"",
            "\"bne\""]

# append the selected input, output and a string with the instruction name
if In_1 < 10 :
	sel_Inputs.append(Inputs[In_1])
	sel_Controls.append(Controls[In_1])
	sel_Strings.append(Strings[In_1])
else :
	sel_Inputs.append(Inputs[In_1])
	sel_Inputs.append(Inputs[In_1+1])
	sel_Controls.append(Controls[In_1])
	sel_Controls.append(Controls[In_1+1])
	sel_Strings.append(Strings[In_1])
	sel_Strings.append(Strings[In_1+1])

if In_2 < 10 :
	sel_Inputs.append(Inputs[In_2])
	sel_Controls.append(Controls[In_2])
	sel_Strings.append(Strings[In_2])
else :
	sel_Inputs.append(Inputs[In_2])
	sel_Inputs.append(Inputs[In_2+1])
	sel_Controls.append(Controls[In_2])
	sel_Controls.append(Controls[In_2+1])
	sel_Strings.append(Strings[In_2])
	sel_Strings.append(Strings[In_2+1])

if In_3 < 10 :
	sel_Inputs.append(Inputs[In_3])
	sel_Controls.append(Controls[In_3])
	sel_Strings.append(Strings[In_3])
else :
	sel_Inputs.append(Inputs[In_3])
	sel_Inputs.append(Inputs[In_3+1])
	sel_Controls.append(Controls[In_3])
	sel_Controls.append(Controls[In_3+1])
	sel_Strings.append(Strings[In_3])
	sel_Strings.append(Strings[In_3+1])

if In_4 < 10 :
	sel_Inputs.append(Inputs[In_4])
	sel_Controls.append(Controls[In_4])
	sel_Strings.append(Strings[In_4])
else :
	sel_Inputs.append(Inputs[In_4])
	sel_Inputs.append(Inputs[In_4+1])
	sel_Controls.append(Controls[In_4])
	sel_Controls.append(Controls[In_4+1])
	sel_Strings.append(Strings[In_4])
	sel_Strings.append(Strings[In_4+1])

array_size = len(sel_Inputs)

# make test vector order random:
c = list(zip(sel_Inputs, sel_Controls, sel_Strings))

shuffle(c)

sel_Inputs, sel_Controls, sel_Strings = zip(*c)

sel_Inputs   = list(sel_Inputs);
sel_Controls = list(sel_Controls);
sel_Strings  = list(sel_Strings);

# format and indentation:
for i in range(len(sel_Inputs)-1) :
    sel_Inputs[i]+=","

for i in range(len(sel_Controls)-1) :
    sel_Controls[i]+=","

for i in range(len(sel_Strings)-1) :
    sel_Strings[i]+=","

TestPattern_inputs=("\n"+2*"\t").join(sel_Inputs)
TestPattern_controls=("\n"+2*"\t").join(sel_Controls)
TestPattern_strings=("\n"+2*"\t").join(sel_Strings)

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################
params.update({"TESTPATTERN_INPUTS":TestPattern_inputs, "TESTPATTERN_CONTROLS":TestPattern_controls, "TESTPATTERN_STRINGS":TestPattern_strings, "ARRAY_SIZE":array_size})

###########################
# FILL TESTBENCH TEMPLATE #
###########################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"

template = env.get_template(filename)
template = template.render(params)

print(template)
