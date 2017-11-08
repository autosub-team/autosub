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

from jinja2 import FileSystemLoader, Environment

import json

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]
language=sys.argv[4]

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

###################################
## IMPORT LANGUAGE TEXT SNIPPETS ##
###################################

filename ="templates/task_description/language_support_files/lang_snippets_{0}.json".format(language)
with open(filename) as data_file:
    lang_data = json.load(data_file)

################################################
# GENERATE PARAMETERS FOR DESCRIPTION TEMPLATE #
################################################



instruction_text = 	[	"\\vspace{-2mm}\n"
				"\\subsection*{%instruction_name}\n"
				+lang_data["instruction_text"][0],

				"\\vspace{-2mm}\n"
				"\\subsection*{j}\n"
				+lang_data["instruction_text"][1],

				"\\vspace{-2mm}\n"
				"\\subsection*{lw}\n"
				+lang_data["instruction_text"][2],

				"\\vspace{-2mm}\n"
				"\\subsection*{sw}\n"
				+lang_data["instruction_text"][3],

				"\\vspace{-2mm}\n"
				"\\subsection*{addi}\n"
				+lang_data["instruction_text"][4],

				"\\vspace{-2mm}\n"
				"\\subsection*{beq}\n"
				+lang_data["instruction_text"][5],

				"\\vspace{-2mm}\n"
				"\\subsection*{bne}\n"
				+lang_data["instruction_text"][6]
			]

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
							  "\\end{table}\n")
	selected_instruction_type_text += (lang_data["Instr_Typ_cap"][0])

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
							  "\\end{table}\n")
	selected_instruction_type_text += (lang_data["Instr_Typ_cap"][1])

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
							  "\\end{table}\n")
	selected_instruction_type_text += (lang_data["Instr_Typ_cap"][2])

# add additional text if beq or bne instruction:
beq_bne_decode_addition = ""
if (first_instruction >= 11) or (second_instruction >= 11):
	beq_bne_decode_addition += lang_data["Instr_Text_helpers"][1]
	if (first_instruction >= 11) and (second_instruction >= 11):
		beq_bne_decode_addition += lang_data["Instr_Text_helpers"][2]
	elif (first_instruction == 11) or (second_instruction == 11):
		beq_bne_decode_addition += lang_data["Instr_Text_helpers"][3]
	elif (first_instruction == 12) or (second_instruction == 12):
		beq_bne_decode_addition += lang_data["Instr_Text_helpers"][4]
	beq_bne_decode_addition += lang_data["Instr_Text_helpers"][5]


selected_instruction_table_text = []
selected_instruction_table_text.append(lang_data["instruction_table_text"][first_instruction])
selected_instruction_table_text.append(lang_data["instruction_table_text"][second_instruction])

selected_instruction_table_text=("\n"+2*"\t").join(selected_instruction_table_text) # just to make indentation

# add description for first_instruction:
first_instruction_text = ""
if (first_instruction <= 6):
	first_instruction_text += instruction_text[0]
	first_instruction_text = first_instruction_text.replace("%instruction_name",lang_data["instruction_names"][first_instruction])
	if (first_instruction == 6):
		first_instruction_text = first_instruction_text.replace("%slt_explanation", lang_data["Instr_Text_helpers"][0])
	else:
		first_instruction_text = first_instruction_text.replace("%slt_explanation", " ")
else:
	 first_instruction_text += instruction_text[first_instruction-6]

# add description for second_instruction:
second_instruction_text = ""
if (second_instruction <= 6):
	second_instruction_text += instruction_text[0]
	second_instruction_text = second_instruction_text.replace("%instruction_name",lang_data["instruction_names"][second_instruction])
	if (second_instruction == 6):
		second_instruction_text = second_instruction_text.replace("%slt_explanation", lang_data["Instr_Text_helpers"][0])
	else:
		second_instruction_text = second_instruction_text.replace("%slt_explanation", " ")
else:
	second_instruction_text += instruction_text[second_instruction-6]

# fill ALUControl table:
ALUControl_table = []
ALUControl_table.append(lang_data["ALUControls"][0]) # we currently always need add
if (first_instruction <= 6) and (first_instruction != 0):
	ALUControl_table.append(lang_data["ALUControls"][first_instruction])
if (second_instruction <= 6) and (second_instruction != 0):
	ALUControl_table.append(lang_data["ALUControls"][second_instruction])
if ((first_instruction >= 11) or (second_instruction >= 11)) and ((first_instruction != 1) and (second_instruction != 1)):
	ALUControl_table.append(lang_data["ALUControls"][1])

shuffle(ALUControl_table) # make selected ALUControls order random

ALUControl_table=("\n"+2*"\t").join(ALUControl_table) # just to make indentation

############################################
## SET PARAMETERS FOR DESCRIPTION TEMPLATE #
############################################
params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email, "selected_instruction_type_text":selected_instruction_type_text, "beq_bne_decode_addition":beq_bne_decode_addition, "selected_instruction_table_text":selected_instruction_table_text, "first_instruction_text":first_instruction_text, "second_instruction_text":second_instruction_text, "ALUControl_table":ALUControl_table })

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="task_description/task_description_template_{0}.tex".format(language)
template = env.get_template(filename)
template = template.render(params_desc)

filename ="tmp/desc_{0}_Task{1}.tex".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################
### PRINT TASKPARAMETERS ##
###########################
print(task_parameters)
