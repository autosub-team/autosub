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

###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

params={}

task_parameters=sys.argv[1]
first_instruction, second_instruction = task_parameters.split('|')
first_instruction = int(first_instruction)
second_instruction = int(second_instruction)

ALUControls = ["000",
		   "010",
		   "100",
		   "101",
		   "110",
		   "111",
		   "001" ]

instruction_names = ["add",
	               "sub",
	               "and",
	               "or",
	               "xor",
	               "nor",
	               "slt",
	               "j",
	               "lw",
	               "sw",
	               "addi",
	               "beq",
	               "bne"]

Opcodes = ["000000", # currently not used
	     "000000",
	     "000000",
	     "000000",
	     "000000",
	     "000000",
	     "000000",
	     "000010",
	     "100011",
	     "101011",
	     "001000",
	     "000100",
	     "000101"]

Functs = ["100000",
	    "100010",
	    "100100",
	    "100101",
	    "100110",
	    "100111",
	    "101010"]

tests_for_instuctions = ["""		-- check R-type (%%instruction_name):

		wait until rising_edge(CLK);

		if (std_match(Controls, "00010000011--00")) then
			Opcode <= "000000";
			Funct  <= "%%Funct";
			report "good Fetch";
		else
			report "§{Failure during: Fetch}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "%%beq_bne_required")) then
			report "good Decode";
		else
			report "§{Failure during: Decode}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "-100%%ALUControl--00--00")) then
			report "good Execute R-type (%%instruction_name)";
		else
			report "§{Failure during: Execute R-type (%%instruction_name)}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "---------001010")) then
			report "good ALUWriteback R-type (%%instruction_name)";
		else
			report "§{Failure during: ALUWriteback R-type (%%instruction_name)}§" severity failure;
		end if;""",
		"""		-- check j:

		wait until rising_edge(CLK);

		if (std_match(Controls, "00010000011--00")) then
			Opcode <= "000010";
			report "good Fetch";
		else
			report "§{Failure during: Fetch}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "%%beq_bne_required")) then
			report "good Decode";
		else
			report "§{Failure during: Decode}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "-------1001--00")) then
			report "good Jump";
		else
			report "§{Failure during: Jump}§" severity failure;
		end if;""",
		"""		-- check lw:

		wait until rising_edge(CLK);

		if (std_match(Controls, "00010000011--00")) then
			Opcode <= "100011";
			report "good Fetch";
		else
			report "§{Failure during: Fetch}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "%%beq_bne_required")) then
			report "good Decode";
		else
			report "§{Failure during: Decode}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "-110000--00--00")) then
			report "good MemAddress for lw";
		else
			report "§{Failure during: MemAddress (lw)}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "1--------00--00")) then
			report "good MemRead for lw";
		else
			report "§{Failure during: MemRead (lw)}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "---------000110")) then
			report "good MemWriteback for lw";
		else
			report "§{Failure during: MemWriteback (lw)}§" severity failure;
		end if;""",
		"""		-- check sw:

		wait until rising_edge(CLK);

		if (std_match(Controls, "00010000011--00")) then
			Opcode <= "101011";
			report "good Fetch";
		else
			report "§{Failure during: Fetch}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "%%beq_bne_required")) then
			report "good Decode";
		else
			report "§{Failure during: Decode}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "-110000--00--00")) then
			report "good MemAddress for sw";
		else
			report "§{Failure during: MemAddress (sw)}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "1--------00--01")) then
			report "good MemWrite for sw";
		else
			report "§{Failure during: MemWrite (sw)}§" severity failure;
		end if;""",
		"""		-- check addi:

		wait until rising_edge(CLK);

		if (std_match(Controls, "00010000011--00")) then
			Opcode <= "001000";
			report "good Fetch";
		else
			report "§{Failure during: Fetch}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "%%beq_bne_required")) then
			report "good Decode";
		else
			report "§{Failure during: Decode}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "-110000--00--00")) then
			report "good Addi Execute";
		else
			report "§{Failure during: Addi Execute}§" severity failure;
		end if;

		wait until rising_edge(CLK);

		if (std_match(Controls, "---------000010")) then
			report "good Addi Writeback";
		else
			report "§{Failure during: Addi Writeback}§" severity failure;
		end if;""",
		"""		-- check beq:

		for i in 0 to 1 loop
			wait until rising_edge(CLK);

			zero_out <= std_logic(to_unsigned(i, 1)(0));
			if (std_match(Controls, "00010000011--00")) then
				Opcode <= "000100";
				report "good Fetch";
			else
				report "§{Failure during: Fetch}§" severity failure;
			end if;

			wait until rising_edge(CLK);

			if (std_match(Controls, "%%beq_bne_required")) then
				report "good Decode";
			else
				report "§{Failure during: Decode}§" severity failure;
			end if;

			wait until rising_edge(CLK);

			if (std_match(Controls, "-100010010" & zero_out & "--00")) then
				report "good Branch (beq)";
			else
				report "§{Failure during: Branch (beq)}§" severity failure;
			end if;

		end loop;""",
		"""		-- check bne:

		for i in 0 to 1 loop
			wait until rising_edge(CLK);

			zero_out <= std_logic(to_unsigned(i, 1)(0));
			if (std_match(Controls, "00010000011--00")) then
				Opcode <= "000101";
				report "good Fetch";
			else
				report "§{Failure during: Fetch}§" severity failure;
			end if;

			wait until rising_edge(CLK);

			if (std_match(Controls, "%%beq_bne_required")) then
				report "good Decode";
			else
				report "§{Failure during: Decode}§" severity failure;
			end if;

			wait until rising_edge(CLK);

			if (std_match(Controls, "-100010010" & not zero_out & "--00")) then
				report "good Branch (beq)";
			else
				report "§{Failure during: Branch (bne)}§" severity failure;
			end if;

		end loop;""",


]

# test for first_instruction:
if (first_instruction <= 6):
	first_instruction_test = tests_for_instuctions[0]
	first_instruction_test = first_instruction_test.replace("%%instruction_name", instruction_names[first_instruction])
	first_instruction_test = first_instruction_test.replace("%%Funct", Functs[first_instruction])
	first_instruction_test = first_instruction_test.replace("%%ALUControl", ALUControls[first_instruction])
else:
	first_instruction_test = tests_for_instuctions[first_instruction - 6]

if (first_instruction >= 11) or (second_instruction >= 11) :
	first_instruction_test = first_instruction_test.replace("%%beq_bne_required", "-011000--00--00")
else:
	first_instruction_test = first_instruction_test.replace("%%beq_bne_required", "---------00--00")

# test for second_instruction:
if (second_instruction <= 6):
	second_instruction_test = tests_for_instuctions[0]
	second_instruction_test = second_instruction_test.replace("%%instruction_name", instruction_names[second_instruction])
	second_instruction_test = second_instruction_test.replace("%%Funct", Functs[second_instruction])
	second_instruction_test = second_instruction_test.replace("%%ALUControl", ALUControls[second_instruction])
else:
	second_instruction_test = tests_for_instuctions[second_instruction - 6]

if (first_instruction >= 11) or (second_instruction >= 11) :
	second_instruction_test = second_instruction_test.replace("%%beq_bne_required", "-011000--00--00")
else:
	second_instruction_test = second_instruction_test.replace("%%beq_bne_required", "---------00--00")

first = randrange(2)
if first == 0:
	instruction_test_1 = first_instruction_test
	instruction_test_2 = second_instruction_test
else:
	instruction_test_1 = second_instruction_test
	instruction_test_2 = first_instruction_test

second = randrange(2)
if second == 0:
	instruction_test_3 = first_instruction_test
	instruction_test_4 = second_instruction_test
else:
	instruction_test_3 = second_instruction_test
	instruction_test_4 = first_instruction_test


#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################

params.update({"instruction_test_1":instruction_test_1, "instruction_test_2":instruction_test_2, "instruction_test_3":instruction_test_3, "instruction_test_4":instruction_test_4 })

#####################################
# FILL AND PRINT TESTBENCH TEMPLATE #
#####################################
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))