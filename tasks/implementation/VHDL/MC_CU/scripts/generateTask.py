#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task MC_CU
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) Gilbert Markum
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
from random import randrange, shuffle
import string

class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]

params_desc={}

##############################
## PARAMETER SPECIFYING TASK##
##############################

# choose first instruction (13 choose 1 -> 13)
first_instruction = randrange(0,13)

# choose second unique instruction (13 - 1 choose 1 -> 12 )
second_instruction = randrange(0,13)
while(second_instruction == first_instruction): # do not use the same instruction
	second_instruction = randrange(0,13)

task_parameters=str(first_instruction)+"|"+str(second_instruction)

################################################
# GENERATE PARAMETERS FOR DESCRIPTION TEMPLATE #
################################################

instruction_table_text =	["add         & 000000 & 100000 & R  \\\\",	# 0
					 "sub         & 000000 & 100010 & R  \\\\",	# 1
					 "and         & 000000 & 100100 & R  \\\\",	# 2
					 "or          & 000000 & 100101 & R  \\\\",	# 3
					 "xor         & 000000 & 100110 & R  \\\\",	# 4
					 "nor         & 000000 & 100111 & R  \\\\",	# 5
					 "slt         & 000000 & 101010 & R  \\\\",	# 6
					 "j           & 000010 &    -   & J  \\\\",	# 7
					 "lw          & 100011 &    -   & I  \\\\",	# 8
					 "sw          & 101011 &    -   & I  \\\\",	# 9
					 "addi        & 001000 &    -   & I  \\\\",	# 10
					 "beq         & 000100 &    -   & I  \\\\",	# 11
					 "bne         & 000101 &    -   & I  \\\\"]	# 12

ALUControls = ["000        & add \\\\",
		   "010        & sub \\\\",
		   "100        & and \\\\",
		   "101        & or  \\\\",
		   "110        & xor \\\\",
		   "111        & nor \\\\",
		   "001        & slt \\\\" ]

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

instruction_text = ["\\vspace{-2mm}\n"
			  "\\subsection*{%instruction_name}\n"
			  "This instruction performs an ALU operation with two register values and saves the result to a register. It takes two clock cycles. First the registers specified in rs and rt are loaded into the ALU and the ALU is sent the %instruction_name control signal. %slt_explanation The ALUControl signal for %instruction_name can be found in Table~1. In the next clock cycle the ALU Result is saved into the register specified by rd.",
			  "\\vspace{-2mm}\n"
			  "\\subsection*{j}\n"
			  "This instruction performs an unconditional jump to the address specified in the instruction. It takes one clock cycle. During this clock cycle the bits 25 -- 0 of the instruction are shiftet left by 2 bits. They are then used as the bits 27 -- 0 of the new program counter value (PC') together with bits 31 -- 28 of the current program counter value (PC).",
			  "\\vspace{-2mm}\n"
			  "\\subsection*{lw}\n"
			  "This instruction loads a data word from data memory into the registers. It takes three clock cycles. First the data memory address is being determined by addition in the ALU. The operands for the ALU are the register specified in rs and an immediate value specified in bits 15 -- 0 of the instruction. During the next clock cycle the result of the ALU is used as a read address from the data memory. In the third clock cycle the data read from data memory is written to the register specified by rd.",
			  "\\vspace{-2mm}\n"
			  "\\subsection*{sw}\n"
			  "This instruction stores a data word from the registers into data memory. It takes two clock cycles. First the data memory address is being calculated by addition in the ALU. The operands for the ALU are the register specified in rs and an immediate value specified in bits 15 -- 0 of the instruction. During the next clock cycle the result of the ALU is used as a write address for the data memory. The written data comes from the register specified by rd.",
			  "\\vspace{-2mm}\n"
			  "\\subsection*{addi}\n"
			  "This instruction performs an addition using the ALU with a register value and an immediate value. It takes two clock cycles. First the register value specified in rs and the immediate value are added in the ALU. In the next clock cycle the ALU Result is saved into the register specified by rt.",
			  "\\vspace{-2mm}\n"
			  "\\subsection*{beq}\n"
			  "This instruction compares two registers and on equality branches to an address specified in the immediate value. It takes only one clock cycle, but as mentioned above, the branching address has to be prepared already while decoding. Then in the clock cycle after decoding a beq instruction, registers specified by rs and rd are compared on equality by substraction in the ALU. If the ALU operation result is zero, then it sets its Zero output to `1'. The control unit has asynchronous logic which sets the PCWrite signal to `1' in case the Zero flag is `1' during the beq instruction. This writes a new value to the PC register, and thus performs the branching.",
			  "\\vspace{-2mm}\n"
			  "\\subsection*{bne}\n"
			  "This instruction compares two registers and if they are not equal, branches to an address specified in the immediate value. It takes only one clock cycle, but as mentioned above, the branching address has to be prepared already while decoding. Then in the clock cycle after decoding a bne instruction, registers specified by rs and rd are compared on equality by substraction in the ALU. If the ALU operation result is zero, then it sets its Zero output to `1'. The control unit has asynchronous logic which sets the PCWrite signal to `1' in case the Zero flag is not `1' during the bne instruction. This writes a new value to the PC register, and thus performs the branching."]

slt_explanation = "The slt ALUControl signal compares the two ALU operands, and sets the ALU Result to 1 in case rs $<$ rt. The ALU Result is set to 0 otherwise."

# add description for selected instruction types:
selected_instruction_type_text = ""
if (first_instruction <= 6) or (second_instruction <= 6):
	selected_instruction_type_text += ("\\vspace{-2mm}\n"
							  "\\subsection*{R-type:}\n"
							  "\\vspace*{-5mm}\n"
							  "\\begin{table}[h!]\n"
							  "\\centering\n"
							  "    \\begin{bytefield}[boxformatting=\\baselinealign]{32}\n"
							  "        \\bitheader[b]{0,5,6,10,11,15,16,20,21,25,26,31}\\\\\n"
							  "        \\bitbox{6}{opcode} & \\bitbox{5}{rs} & \\bitbox{5}{rt} & \\bitbox{5}{rd} &\n"
							  "        \\bitbox{5}{\\textcolor{grau}{unused}} & \\bitbox{6}{funct}\n"
							  "    \\end{bytefield}\n"
							  "\\end{table}\n"
							  "With the opcode representing the instruction, rs and rt the source registers and rd the destination register and funct representing an instruction for the ALU. The R-type instruction processes the two source registers in the ALU. The ALU result is saved in the destination register specified by rd.\\\\ \n")

if (first_instruction == 7) or (second_instruction == 7):
	selected_instruction_type_text += ("\\vspace{-2mm}\n"
							  "\\subsection*{J-type:}\n"
							  "\\vspace*{-5mm}\n"
							  "\\begin{table}[h!]\n"
							  "\\centering\n"
							  "    \\begin{bytefield}[boxformatting=\\baselinealign]{32}\n"
							  "        \\bitheader[b]{0,25,26,31}\\\\\n"
							  "        \\bitbox{6}{opcode} & \\bitbox{26}{address}\n"
							  "    \\end{bytefield}\n"
							  "\\end{table}\n"
							  "With the opcode representing the instruction and the address being part of a 32 bit address. The 32 bit address is constructed by using the first four bits of the program counter as most significant bits, concatenating the 16 bit address from the instruction and setting the two least significant bits to 0.\\\\ \n")

if (first_instruction >= 8) or (second_instruction >= 8):
	selected_instruction_type_text += ("\\vspace{-2mm}\n"
							  "\\subsection*{I-type:}\n"
							  "\\vspace*{-5mm}\n"
							  "\\begin{table}[h!]\n"
							  "\\centering\n"
							  "    \\begin{bytefield}[boxformatting=\\baselinealign]{32}\n"
							  "        \\bitheader[b]{0,15,16,20,21,25,26,31}\\\\\n"
							  "        \\bitbox{6}{opcode} & \\bitbox{5}{rs} & \\bitbox{5}{rt} & \\bitbox{16}{IMM}\n"
							  "    \\end{bytefield}\n"
							  "\end{table}\n"
							  "With the opcode representing the instruction, rs a source register and IMM the immediate value. The usage of rt depends on the instruction, see below for details.\\\\ \n")

# add additional text if beq or bne instruction:
beq_bne_decode_addition = ""
if (first_instruction >= 11) or (second_instruction >= 11):
	beq_bne_decode_addition += "Because the instruction might be a "
	if (first_instruction >= 11) and (second_instruction >= 11):
		beq_bne_decode_addition += "beq/bne"
	elif (first_instruction == 11) or (second_instruction == 11):
		beq_bne_decode_addition += "beq"
	elif (first_instruction == 12) or (second_instruction == 12):
		beq_bne_decode_addition += "bne"
	beq_bne_decode_addition += " instruction which might lead to a branch to a new program counter value, this new program counter value has to be calculated during the decode clock cycle. This means during decode the rt value of the potential I-type instruction has to be added to the potential immediate value in the ALU. This makes the branching address available in the register which saves the ALU Result."


selected_instruction_table_text = []
selected_instruction_table_text.append(instruction_table_text[first_instruction])
selected_instruction_table_text.append(instruction_table_text[second_instruction])

selected_instruction_table_text=("\n"+2*"\t").join(selected_instruction_table_text) # just to make indentation

# add description for first_instruction:
first_instruction_text = ""
if (first_instruction <= 6):
	first_instruction_text += instruction_text[0]
	first_instruction_text = first_instruction_text.replace("%instruction_name",instruction_names[first_instruction])
	if (first_instruction == 6):
		first_instruction_text = first_instruction_text.replace("%slt_explanation", slt_explanation)
	else:
		first_instruction_text = first_instruction_text.replace("%slt_explanation", " ")
else:
	 first_instruction_text += instruction_text[first_instruction-6]

# add description for second_instruction:
second_instruction_text = ""
if (second_instruction <= 6):
	second_instruction_text += instruction_text[0]
	second_instruction_text = second_instruction_text.replace("%instruction_name",instruction_names[second_instruction])
	if (second_instruction == 6):
		second_instruction_text = second_instruction_text.replace("%slt_explanation", slt_explanation)
	else:
		second_instruction_text = second_instruction_text.replace("%slt_explanation", " ")
else:
	second_instruction_text += instruction_text[second_instruction-6]

# fill ALUControl table:
ALUControl_table = []
ALUControl_table.append(ALUControls[0]) # we currently always need add
if (first_instruction <= 6) and (first_instruction != 0):
	ALUControl_table.append(ALUControls[first_instruction])
if (second_instruction <= 6) and (second_instruction != 0):
	ALUControl_table.append(ALUControls[second_instruction])
if ((first_instruction >= 11) or (second_instruction >= 11)) and ((first_instruction != 1) and (second_instruction != 1)):
	ALUControl_table.append(ALUControls[1])

shuffle(ALUControl_table) # make selected ALUControls order random

ALUControl_table=("\n"+2*"\t").join(ALUControl_table) # just to make indentation

############################################
## SET PARAMETERS FOR DESCRIPTION TEMPLATE #
############################################
params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email, "selected_instruction_type_text":selected_instruction_type_text, "beq_bne_decode_addition":beq_bne_decode_addition, "selected_instruction_table_text":selected_instruction_table_text, "first_instruction_text":first_instruction_text, "second_instruction_text":second_instruction_text, "ALUControl_table":ALUControl_table })

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
filename ="templates/task_description_template.tex"
with open (filename, "r") as template_file:
    data=template_file.read()

filename ="tmp/desc_{0}_Task{1}.tex".format(user_id,task_nr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(params_desc))

###########################
### PRINT TASKPARAMETERS ##
###########################
print(task_parameters)