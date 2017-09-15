#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task counter
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) Gilbert Markum
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
from random import randrange
from math import ceil, log
import string

class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]

params_desc={}
params_entity={}

##############################
## PARAMETER SPECIFYING TASK##
##############################

# choose bit width of counter (from: 3-8 -> 6)
counter_width = randrange(3,9)

# choose initial value of counter (0b0 or 0b1 -> 2)
init_value = randrange(0,2)

# choose synchronous function (Clear / Load a constant / Load an input -> 3)
synchronous_function = randrange(0,3) # 0 = Clear, 1 = LoadC, 2 = LoadI

# choose asynchronous function (Clear / Load a constant / Load an input, but not identical to synchronous function -> 2)
asynchronous_function = randrange(0,3) # 0 = Clear, 1 = LoadC, 2 = LoadI
while(asynchronous_function == synchronous_function): # do not use the same function for asynchronous and synchronous
	asynchronous_function = randrange(0,3)

# choose if enable signal shall be used (yes / no -> 2)
enable = randrange(0,2) # 0 = no, 1 = yes

# choose if overflow functionality shall be implemented (yes / no, but not identical to enable -> 1)
overflow = randrange(0,2) # 0 = no, 1 = yes
while(overflow == enable): # do not select to implement overflow and enable at the same time
	overflow = randrange(0,2)

constant_value = 0
# choose constant load value if applicable:
if ((synchronous_function == 1) or (asynchronous_function == 1)):
	constant_value = randrange(1,pow(2,counter_width))
	constant_value = format(constant_value, '0'+str(int(counter_width))+'b')

## for testing only:
# insert values for testing here
# ...

task_parameters=str(counter_width)+"|"+str(init_value)+"|"+str(synchronous_function)+"|"+str(asynchronous_function)+"|"
task_parameters+=str(enable)+"|"+str(overflow)+"|"+str(constant_value)


################################################
# GENERATE PARAMETERS FOR DESCRIPTION TEMPLATE #
################################################

enable_property_desc=""
if (enable == 1):
	enable_property_desc+="\item Input: Enable with type std\_logic"

sync_async_variations=["Clear","LoadConstant","LoadInput"]
sync_variation = sync_async_variations[synchronous_function]
async_variation = sync_async_variations[asynchronous_function]

sync_property_desc="\item Input: Sync" + str(sync_variation) +" with type std\_logic"

async_property_desc="\item Input: Async" + str(async_variation) +" with type std\_logic"

overflow_property_desc=""
if (overflow == 1):
	overflow_property_desc+="\item Output: Overflow with type std\_logic"

input_necessary=0
input_property_desc=""
if ((synchronous_function == 2) or (asynchronous_function == 2)):
	input_property_desc+="\item Input: Input with type std\_logic\_vector of length " + str(counter_width)
	input_necessary=1

num_in=(3) + (1*enable) + (1*(input_necessary))

minimum_height = 6 * (1 + num_in) # minimum_height for tikzpicture

inputs_tikz = ""
inputs_tikz+="\draw[->] ($ (entity.west) + (-10mm," + str(((minimum_height / 2) - 6)) + "mm)$) -- ($ (entity.west) + (0mm," + str((minimum_height / 2) - 6) + "mm)$);\n"
inputs_tikz+= "\draw[anchor=east] node at ($ (entity.west) + (-9mm," + str((minimum_height/2) - 6) + "mm)$){ CLK };\n\n"
current_tikz_offset=6

if ( enable == 1):
	inputs_tikz+="\draw[->] ($ (entity.west) + (-10mm," + str(((minimum_height / 2) - 12)) + "mm)$) -- ($ (entity.west) + (0mm," + str((minimum_height / 2) - 12) + "mm)$);\n"
	inputs_tikz+= "\draw[anchor=east] node at ($ (entity.west) + (-9mm," + str((minimum_height/2) - 12) + "mm)$){ Enable };\n\n"
	current_tikz_offset+=6

current_tikz_offset+=6
inputs_tikz+="\draw[->] ($ (entity.west) + (-10mm," + str(((minimum_height / 2) - current_tikz_offset)) + "mm)$) -- ($ (entity.west) + (0mm," + str((minimum_height / 2) - current_tikz_offset) + "mm)$);\n"
inputs_tikz+= "\draw[anchor=east] node at ($ (entity.west) + (-9mm," + str((minimum_height/2) - current_tikz_offset) + "mm)$){ Sync" + str(sync_variation) + " };\n\n"

current_tikz_offset+=6
inputs_tikz+="\draw[->] ($ (entity.west) + (-10mm," + str(((minimum_height / 2) - current_tikz_offset)) + "mm)$) -- ($ (entity.west) + (0mm," + str((minimum_height / 2) - current_tikz_offset) + "mm)$);\n"
inputs_tikz+= "\draw[anchor=east] node at ($ (entity.west) + (-9mm," + str((minimum_height/2) - current_tikz_offset) + "mm)$){ Async" + str(async_variation) + " };\n\n"

if ( input_necessary == 1):
	current_tikz_offset+=6
	inputs_tikz+="\draw[->] ($ (entity.west) + (-10mm," + str(((minimum_height / 2) - current_tikz_offset)) + "mm)$) -- ($ (entity.west) + (0mm," + str((minimum_height / 2) - current_tikz_offset) + "mm)$);\n"
	inputs_tikz+= "\draw[anchor=east] node at ($ (entity.west) + (-9mm," + str((minimum_height/2) - current_tikz_offset) + "mm)$){ Input };\n\n"

num_out=(1) + (1*overflow)

outputs_tikz = ""
outputs_tikz += "\draw[->] ($ (entity.east) + (0mm," + str((minimum_height / 2) - (1 * (minimum_height / (num_out + 1)))) + "mm)$) -- ($ (entity.east) + (10mm," + str(((minimum_height / 2) - (1 * (minimum_height / (num_out + 1))))) + "mm)$);\n"
outputs_tikz += "\draw[anchor=west] node at ($ (entity.east) + (9mm," + str(((minimum_height/2) - (1 * ( minimum_height / (num_out + 1))))) + "mm)$){ Output };\n\n"

if (overflow == 1):
	outputs_tikz += "\draw[->] ($ (entity.east) + (0mm," + str((minimum_height / 2) - (2 * (minimum_height / (num_out + 1)))) + "mm)$) -- ($ (entity.east) + (10mm," + str(((minimum_height / 2) - (2 * (minimum_height / (num_out + 1))))) + "mm)$);\n"
	outputs_tikz += "\draw[anchor=west] node at ($ (entity.east) + (9mm," + str(((minimum_height/2) - (2 * ( minimum_height / (num_out + 1))))) + "mm)$){ Overflow };\n\n"

init_value_padded = format(init_value, '0'+str(counter_width)+'b')

zero_padded = format(0, '0'+str(counter_width)+'b')

if (synchronous_function == 0):
	sync_text = ("``" + zero_padded + "\"")
elif (synchronous_function == 1):
	sync_text = ("the constant ``" + str(constant_value) + "\"")
elif (synchronous_function == 2):
	sync_text =  "the value of the Input vector"

if (asynchronous_function == 0):
	async_text = ("``" + zero_padded + "\"")
elif (asynchronous_function == 1):
	async_text = ("the constant ``" + str(constant_value) + "\"")
elif (asynchronous_function == 2):
	async_text =  "the value of the Input vector"

Enable_Overflow_text=""
every_a = ""
if ( enable == 1):
	Enable_Overflow_text += "When the Enable signal is set to `1' then the ``counter'' entity shall behave as described above. When the Enable signal is set to `0' then the ``counter'' entity shall not react to any input at all and keep the current Output vector unchanged."
	every_a += "a"
elif ( overflow == 1):
	max_counter_value = [1] * counter_width
	max_counter_value = ''.join(str(e) for e in max_counter_value)
	Enable_Overflow_text += ("When the Output vector changes from ``" + max_counter_value  + "\" to ``" + zero_padded +"\", then the Overflow signal shall be set to `1' until the next rising edge of the CLK signal. In all other cases the Overflow signal shall be `0'.")
	every_a += "every"

############################################
## SET PARAMETERS FOR DESCRIPTION TEMPLATE #
############################################
params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email, "counter_width":counter_width, "enable_property_desc":enable_property_desc, "sync_property_desc":sync_property_desc, "async_property_desc":async_property_desc, "input_property_desc":input_property_desc, "overflow_property_desc":overflow_property_desc, "minimum_height":minimum_height, "inputs_tikz":inputs_tikz, "outputs_tikz":outputs_tikz, "init_value_padded":init_value_padded, "sync_variation":sync_variation, "sync_text":sync_text, "async_variation":async_variation, "async_text":async_text, "every_a":every_a, "Enable_Overflow_text":Enable_Overflow_text })

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
# GENERATE PARAMETERS FOR ENTITY TEMPLATE #
###########################################

entity_in_out = ""
if ( enable == 1):
	entity_in_out += "\t\tEnable      : in   std_logic;\n"

entity_in_out += ("\t\tSync" + str(sync_variation) + "   : in   std_logic;\n")
entity_in_out += ("\t\tAsync" + str(async_variation) + "   : in   std_logic;\n")

if ( input_necessary == 1 ):
	entity_in_out += ("\t\tInput       : in   std_logic_vector((" + str(counter_width) + "-1) downto 0);\n")

entity_in_out += ("\t\tOutput      : out  std_logic_vector((" +  str(counter_width) + "-1) downto 0)")

if ( overflow == 1):
	entity_in_out += ";\n"
	entity_in_out += "\t\tOverflow    : out  std_logic"



######################################
# SET PARAMETERS FOR ENTITY TEMPLATE #
######################################
params_entity.update({"entity_in_out":entity_in_out})

#############################
#   FILL ENTITY TEMPLATE    #
#############################
filename ="templates/counter_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()

filename ="tmp/counter_{0}_Task{1}.vhdl".format(user_id,task_nr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(params_entity))

###########################
### PRINT TASKPARAMETERS ##
###########################
print(task_parameters)