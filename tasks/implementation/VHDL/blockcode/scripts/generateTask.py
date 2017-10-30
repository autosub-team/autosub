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
from bitstring import Bits
from random import randrange

import parity_functions

from jinja2 import FileSystemLoader, Environment

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]
language=sys.argv[4]

params_desc = {}
params_entity = {}
params_tb_exam = {}

###########################################
#   GENERATROR MATRIX GENERATION          #
###########################################
# (n,k) code; n= codelength; k= num of data bits, n-k= num of parity bits

# fixing it: n + k ->n ; n -> k ; k -> n - k

k = random.randrange(5,8) # 5-7 data bits
n = k + random.randrange(3, k-k%2)

identity_vectors = [i*'0'+'1'+(k-i-1)*'0' for i in range(0,k)]

parities = ["".join(seq) for seq in itertools.product("01", repeat=k)]

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

# chose n - k of these parity vectors
chosen_parities_indexes = random.sample(range(0, num_remaining-1), (n - k))
chosen_parities = [remaining_parities[index] for index in chosen_parities_indexes]

generator_vectors = identity_vectors + chosen_parities

generator_matrix = ""
generator_rows = []
for i in range(0,k):
    generator_row = ""
    for j in range(0,n):
        generator_row += generator_vectors[j][i];
    generator_rows.append(" & ".join(generator_row) + " \\\\ \n")
generator_matrix = "".join(generator_rows)

matrix_header = k*'c' + "|" + (n-k)*'c' #for the seperating vertical line

chosen_parities_formated = ["'" + parity + "'" for parity in chosen_parities]
task_parameters = str(n) + '|' + str(k) + '|' + "["+",".join(chosen_parities_formated)+"]"

parity_equations = parity_functions.create_parity_equations(chosen_parities)

data_bits = list(Bits(uint=randrange(0,2**k),length=k).bin)
data = [int(number) for number in data_bits]

example_data = ''.join(data_bits)
example_parity = parity_functions.create_parity_check(parity_equations, data)
example_code = example_data + str(example_parity)

###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################
params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email})
params_desc.update({"GENERATORMATRIX":generator_matrix,
                    "MATRIXHEADER":matrix_header,
                    "DATALENGTH":str(k), "CODELENGTH":str(n),
                    "NUMPARITY":str(n-k),
                    "LASTDATAELEM" : str(k-1), "LASTPARITYELEM": str(n-k-1),
                    "EXAMPLEDATA":example_data,
                    "EXAMPLECODE":example_code})

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

###########################################
# SET PARAMETERS FOR ENTITY TEMPLATE CRC  #
###########################################
params_entity.update({"DATALEN":str(k), "CODELEN":str(n)})

#############################
#   FILL ENTITY TEMPLATE    #
#############################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="blockcode_template.vhdl"
template = env.get_template(filename)
template = template.render(params_entity)

filename ="tmp/blockcode_{0}_Task{1}.vhdl".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)


############### ONLY FOR TESTING #######################
filename ="tmp/solution_{0}_Task{1}.txt".format(user_id,task_nr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + str(task_parameters) + "\n\n")
    solution.write(str(n)+ "\n")
    solution.write(str(k)+ "\n")

    for i in range(0,k):
        solution.write("fifo.data(fifo.write_ptr)(" + str(i)+ ") := data(" + str(i) + ");\n")

    for i in range(0,n-k):
        chosen_databits= []
        parity_vector = chosen_parities[i]

        for j in range(0,k):
            if parity_vector[j] == "1":
                chosen_databits.append("data(" + str(j) + ")")

        left_side =  "fifo.data(fifo.write_ptr)(" + str(k+i)+ ") := "
        right_side = " xor ".join(chosen_databits)
        solution.write(left_side + right_side +";\n")
#########################################################

###########################
### PRINT TASKPARAMETERS ##
###########################
print(task_parameters)
