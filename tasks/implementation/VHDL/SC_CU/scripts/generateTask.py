#!/usr/bin/env python3

#####################################################################################
# generateTask.py for VHDL task SC_CU
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) 2015, 2016 Martin  Mosbeck   <martin.mosbeck@gmx.at> , Gilbert Markum
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
#####################################################################################

from random import randrange, shuffle
import string
import sys

from jinja2 import FileSystemLoader, Environment

import json

#################################################################

userId=sys.argv[1]
taskNr=sys.argv[2]
submissionEmail=sys.argv[3]
language=sys.argv[4]

paramsDesc={}
paramsEntity={}

# choose first instruction:
while True:
	In_1 = randrange(0,13)
	if (In_1 != 11):
		break;

# choose second instruction:
while True:
	In_2 = randrange(0,13)
	if (In_2 != 11) and (In_2 != In_1):
		break;

# choose third instruction:
while True:
	In_3 = randrange(0,13)
	if (In_3 != 11) and (In_3 != In_2) and (In_3 != In_1):
		break;

# choose fourth instruction:
while True:
	In_4 = randrange(0,13)
	if (In_4 != 11) and (In_4 != In_3) and (In_4 != In_2) and (In_4 != In_1):
		break;

##############################
## PARAMETER SPECIFYING TASK##
##############################

## just for testing:
#In_1 = 7
#In_2 = 8
#In_3 = 9
#In_4 = 10

taskParameters=str(In_1)+"|"+str(In_2)+"|"+str(In_3)+"|"+str(In_4)

############### ONLY FOR TESTING #######################
filename ="tmp/solution_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + str(taskParameters) + "\n")
#########################################################

###################################
## IMPORT LANGUAGE TEXT SNIPPETS ##
###################################

filename ="templates/task_description/language_support_files/lang_snippets_{0}.json".format(language)
with open(filename) as data_file:
    lang_data = json.load(data_file)

################################################
# GENERATE PARAMETERS FOR DESCRIPTION TEMPLATE #
################################################
sel_Instr = []
sel_Instr_type = []
sel_Instr_Text = []
sel_ALUControls = []
R_type_Instr_counter_processed = 0
R_type_Instr_counter_orig = 0
number_of_Instruction_types = 0


# select Instruction types:
if (In_1 <= 6) or (In_2 <= 6) or(In_3 <= 6) or(In_4 <= 6) :   # R-type
	number_of_Instruction_types = number_of_Instruction_types + 1
	sel_Instr_type.append("\\vspace{-2mm}\n"
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
	sel_Instr_type.append(lang_data["Instr_Typ_cap"][0])

	if not ((In_1 >= 7 and In_1 != 9) or (In_2 >= 7 and In_2 != 9) or (In_3 >= 7 and In_3 != 9) or (In_4 >= 7 and In_4 != 9)) : # no I-type
		sel_Instr_type.append("\\newpage\n")   # insert newpage for formatting when required

if (In_1 >= 7 and In_1 != 9) or (In_2 >= 7 and In_2 != 9) or (In_3 >= 7 and In_3 != 9) or (In_4 >= 7 and In_4 != 9) :   # I-type
	number_of_Instruction_types = number_of_Instruction_types + 1
	sel_Instr_type.append("\\vspace{-2mm}\n"
				    "\\subsection*{I-type:}\n"
				    "\\vspace*{-5mm}\n"
				    "\\begin{table}[h!]\n"
				    "\\centering\n"
				    "    \\begin{bytefield}[boxformatting=\\baselinealign]{32}\n"
				    "        \\bitheader[b]{0,15,16,20,21,25,26,31}\\\\\n"
				    "        \\bitbox{6}{opcode} & \\bitbox{5}{rs} & \\bitbox{5}{rt} & \\bitbox{16}{IMM}\n"
				    "    \\end{bytefield}\n"
				    "\end{table}\n")
	sel_Instr_type.append(lang_data["Instr_Typ_cap"][1])

if (In_1 == 9) or (In_2 == 9) or (In_3 == 9) or (In_4 == 9) :   # J-type
	number_of_Instruction_types = number_of_Instruction_types + 1
	sel_Instr_type.append("\\subsection*{J-type:}\n"
				    "\\vspace*{-5mm}\n"
				    "\\begin{table}[h!]\n"
				    "\\centering\n"
				    "    \\begin{bytefield}[boxformatting=\\baselinealign]{32}\n"
				    "        \\bitheader[b]{0,25,26,31}\\\\\n"
				    "        \\bitbox{6}{opcode} & \\bitbox{26}{address}\n"
				    "    \\end{bytefield}\n"
				    "\\end{table}\n")
	sel_Instr_type.append(lang_data["Instr_Typ_cap"][2])

if (number_of_Instruction_types >= 2) or  (In_1 >= 7 and In_1 != 9) or (In_2 >= 7 and In_2 != 9) or (In_3 >= 7 and In_3 != 9) or (In_4 >= 7 and In_4 != 9):    # if (more than one Instruction) or I-type
	sel_Instr_type.append("\\\\ \n")   # spacing
sel_Instr_type = ("\n").join(sel_Instr_type)


# select Instructions:
sel_Instr.append(lang_data["Instr"][In_1])
sel_Instr.append(lang_data["Instr"][In_2])
sel_Instr.append(lang_data["Instr"][In_3])
sel_Instr.append(lang_data["Instr"][In_4])

sel_Instr=("\n"+2*"\t").join(sel_Instr) # just to make indentation


# count R-type Instructions ( except slt )
if In_1 <= 5 :
	R_type_Instr_counter_processed = R_type_Instr_counter_processed + 1
if In_2 <= 5 :
	R_type_Instr_counter_processed = R_type_Instr_counter_processed + 1
if In_3 <= 5 :
	R_type_Instr_counter_processed = R_type_Instr_counter_processed + 1
if In_4 <= 5 :
	R_type_Instr_counter_processed = R_type_Instr_counter_processed + 1

# select Instruction Text:
if R_type_Instr_counter_processed > 0 :
	sel_Instr_Text.append(lang_data["Instr_Text_helpers"][0]) # "The "
	if In_1 <= 5 :
		sel_Instr_Text.append(lang_data["Instr_Text"][In_1])
		if R_type_Instr_counter_processed > 2 :
			sel_Instr_Text.append(lang_data["Instr_Text_helpers"][1]) # ", "
		elif R_type_Instr_counter_processed == 2 :
			sel_Instr_Text.append(lang_data["Instr_Text_helpers"][2]) # " and "
		R_type_Instr_counter_processed = R_type_Instr_counter_processed - 1

	if In_2 <= 5 :
		sel_Instr_Text.append(lang_data["Instr_Text"][In_2])
		if R_type_Instr_counter_processed > 2 :
			sel_Instr_Text.append(lang_data["Instr_Text_helpers"][1]) # ", "
		elif R_type_Instr_counter_processed == 2 :
			sel_Instr_Text.append(lang_data["Instr_Text_helpers"][2]) # " and "
		R_type_Instr_counter_processed = R_type_Instr_counter_processed - 1

	if In_3 <= 5 :
		sel_Instr_Text.append(lang_data["Instr_Text"][In_3])
		if R_type_Instr_counter_processed == 2 :
			sel_Instr_Text.append(lang_data["Instr_Text_helpers"][2]) # " and "
		R_type_Instr_counter_processed = R_type_Instr_counter_processed - 1

	if In_4 <= 5 :
		sel_Instr_Text.append(lang_data["Instr_Text"][In_4])

	sel_Instr_Text.append(lang_data["Instr_Text_helpers"][3])

if In_1 >= 6 :
	sel_Instr_Text.append(lang_data["Instr_Text"][In_1])

if In_2 >= 6 :
	sel_Instr_Text.append(lang_data["Instr_Text"][In_2])

if In_3 >= 6 :
	sel_Instr_Text.append(lang_data["Instr_Text"][In_3])

if In_4 >= 6 :
	sel_Instr_Text.append(lang_data["Instr_Text"][In_4])#

if (In_1 >= 6) and (In_2 >= 6) and (In_3 >= 6) and (In_4 >= 6) :
	sel_Instr_Text.append(lang_data["Instr_Text_helpers"][4])

sel_Instr_Text = ("").join(sel_Instr_Text)


# select ALUControls:
if In_1 <= 6 :
	sel_ALUControls.append(lang_data["ALUControls"][In_1])
elif In_1 == 7 or In_1 == 8 :
	sel_ALUControls.append(lang_data["ALUControls"][0])
elif In_1 >= 10 :
	sel_ALUControls.append(lang_data["ALUControls"][1])

if In_2 == 0 and In_1 != 7 and In_1 != 8 :
	sel_ALUControls.append(lang_data["ALUControls"][0]);
elif In_2 == 1 and In_1 != 10 and In_1 != 12 :
	sel_ALUControls.append(lang_data["ALUControls"][1]);
elif In_2 <= 6 and In_2 >= 2:
	sel_ALUControls.append(lang_data["ALUControls"][In_2])
elif (In_2 == 7 or In_2 == 8) and (In_1 != 7 and In_1 != 8) and In_1 != 0:
	sel_ALUControls.append(lang_data["ALUControls"][0])
elif In_2 >= 10 and In_1 < 10  and In_1 != 1:
	sel_ALUControls.append(lang_data["ALUControls"][1])

if In_3 == 0 and (In_1 != 7 and In_1 != 8) and (In_2 != 7 and In_2 != 8) :
	sel_ALUControls.append(lang_data["ALUControls"][0]);
elif In_3 == 1 and (In_1 != 10 and In_1 != 12) and (In_2 != 10 and In_2 != 12) :
	sel_ALUControls.append(lang_data["ALUControls"][1]);
elif In_3 <= 6 and In_3 >= 2:
	sel_ALUControls.append(lang_data["ALUControls"][In_3])
elif (In_3 == 7 or In_3 == 8) and (In_1 != 7 and In_1 != 8 and In_1 != 0) and (In_2 != 7 and In_2 != 8 and In_2 != 0):
	sel_ALUControls.append(lang_data["ALUControls"][0])
elif In_3 >= 10 and (In_1 < 10  and In_1 != 1) and (In_2 < 10  and In_2 != 1):
	sel_ALUControls.append(lang_data["ALUControls"][1])

if In_4 == 0 and (In_1 != 7 and In_1 != 8) and (In_2 != 7 and In_2 != 8) and (In_3 != 7 and In_3 != 8):
	sel_ALUControls.append(lang_data["ALUControls"][0]);
elif In_4 == 1 and (In_1 != 10 and In_1 != 12) and (In_2 != 10 and In_2 != 12) and (In_3 != 10 and In_3 != 12) :
	sel_ALUControls.append(lang_data["ALUControls"][1]);
elif In_4 <= 6 and In_4 >= 2:
	sel_ALUControls.append(lang_data["ALUControls"][In_4])
elif (In_4 == 7 or In_4 == 8) and (In_1 != 7 and In_1 != 8 and In_1 != 0) and (In_2 != 7 and In_2 != 8 and In_2 != 0) and (In_3 != 7 and In_3 != 8 and In_3 != 0):
	sel_ALUControls.append(lang_data["ALUControls"][0])
elif In_4 >= 10 and (In_1 < 10  and In_1 != 1) and (In_2 < 10  and In_2 != 1) and (In_3 < 10  and In_3 != 1) :
	sel_ALUControls.append(lang_data["ALUControls"][1])

shuffle(sel_ALUControls) # make selected ALUControls order random

sel_ALUControls=("\n"+2*"\t").join(sel_ALUControls) # just to make indentation

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################
paramsDesc.update({"SELECTED_INSTRUCTIONS_TYPE":str(sel_Instr_type), "SELECTED_INSTRUCTIONS":str(sel_Instr), "SELECTED_INSTRUCTIONS_TEXT":str(sel_Instr_Text), "SELECTED_ALUCONTROLS":str(sel_ALUControls)})
paramsDesc.update({"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="task_description/task_description_template_{0}.tex".format(language)
template = env.get_template(filename)
template = template.render(paramsDesc)

filename ="tmp/desc_{0}_Task{1}.tex".format(userId,taskNr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################
### PRINT TASKPARAMETERS ##
###########################
print(taskParameters)
