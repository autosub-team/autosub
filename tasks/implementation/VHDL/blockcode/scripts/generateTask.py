#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task blockcode
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) 2017 Martin Mosbeck <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import random
import string
import numpy
import itertools
import sys

import parity_functions

class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]

params_desc = {}
params_entity = {}
params_tb_exam = {}

###########################################
#   GENERATROR MATRIX GENERATION          #
###########################################
# (n,k) code; n= data; k= parity

n = random.randrange(5,8) # 5-7 data bits
k = random.randrange(3, n-n%2)

identity_vectors = [i*'0'+'1'+(n-i-1)*'0' for i in range(0,n)]

parities = ["".join(seq) for seq in itertools.product("01", repeat=n)]

# remove the 0
del parities[0]

# remove all containing only one 1 (xor neads at least 2 operands)
num_remaining = len(parities)
remaining_parities = []

for parity in parities:
    if parity.count('1') == 1:
        num_remaining -= 1;
    else:
        remaining_parities.append(parity)

# chose k of these parity vectors
chosen_parities_indexes = random.sample(range(0, num_remaining-1), k)
chosen_parities = [remaining_parities[index] for index in chosen_parities_indexes]

generator_vectors = identity_vectors + chosen_parities

generator_matrix = ""
generator_rows = []
for i in range(0,n):
    generator_row = ""
    for j in range(0,n+k):
        generator_row += generator_vectors[j][i];
    generator_rows.append(" & ".join(generator_row) + " \\\\ \n")
generator_matrix = "".join(generator_rows)

matrix_header = n*'c' + "|" + k*'c' #for the seperating vertical line

task_parameters = str(n) + '|' + str(k) + '|' + ",".join(chosen_parities)

#print(chosen_parities)

parity_equations = parity_functions.create_parity_equations(chosen_parities)

data_bits = list(Bits(uint=randrange(0,2**n),length=n).bin)
data = [int(number) for number in data_bits]

example_data = data_bits
example_code = parity_functions.create_parity_check(parity_equations, data) + example_data


###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################
params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email})
params_desc.update({"GENERATORMATRIX":generator_matrix,
                    "MATRIXHEADER":matrix_header,
                    "DATALENGTH":str(n), "CODELENGTH":str(n+k),
                    "EXAMPLEDATA":example_data,
                    "EXAMPLECODE":example_code})

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

###########################################
# SET PARAMETERS FOR ENTITY TEMPLATE CRC  #
###########################################
params_entity.update({"DATALEN":str(n), "CODELEN":str(n+k)})

#############################
#   FILL ENTITY TEMPLATE    #
#############################
filename ="templates/blockcode_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()

filename ="tmp/blockcode_{0}_Task{1}.vhdl".format(user_id,task_nr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(params_entity))

###########################
### PRINT TASKPARAMETERS ##
###########################
print(task_parameters)
