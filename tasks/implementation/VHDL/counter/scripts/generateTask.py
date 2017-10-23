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

from jinja2 import FileSystemLoader, Environment

import json

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]
language=sys.argv[4]

params_desc={}
params_entity={}


###################################
## IMPORT LANGUAGE TEXT SNIPPETS ##
###################################

filename ="templates/task_description/language_support_files/lang_snippets_{0}.json".format(language)
with open(filename) as data_file:
    lang_data = json.load(data_file)

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
	enable_property_desc+= lang_data["properties"][0]

sync_async_variations=["Clear","LoadConstant","LoadInput"]
sync_variation = sync_async_variations[synchronous_function]
async_variation = sync_async_variations[asynchronous_function]

sync_property_desc=lang_data["properties"][1] + str(sync_variation) + lang_data["properties"][3]

async_property_desc=lang_data["properties"][2]+ str(async_variation) + lang_data["properties"][3]

overflow_property_desc=""
if (overflow == 1):
	overflow_property_desc+=lang_data["properties"][4]

input_necessary=0
input_property_desc=""
if ((synchronous_function == 2) or (asynchronous_function == 2)):
	input_property_desc+=lang_data["properties"][5] + str(counter_width)
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
	sync_text = (lang_data["sync_text"][0] + str(constant_value) + "\"")
elif (synchronous_function == 2):
	sync_text =  lang_data["sync_text"][1]

if (asynchronous_function == 0):
	async_text = ("``" + zero_padded + "\"")
elif (asynchronous_function == 1):
	async_text = (lang_data["sync_text"][0] + str(constant_value) + "\"")
elif (asynchronous_function == 2):
	async_text =  lang_data["sync_text"][1]

Enable_Overflow_text=""
every_a = ""
if ( enable == 1):
	Enable_Overflow_text += lang_data["Enable_Overflow_text"][0]
	every_a += lang_data["every_a"][0]
elif ( overflow == 1):
	max_counter_value = [1] * counter_width
	max_counter_value = ''.join(str(e) for e in max_counter_value)
	Enable_Overflow_text += (lang_data["Enable_Overflow_text"][1] + max_counter_value  + lang_data["Enable_Overflow_text"][2] + zero_padded + lang_data["Enable_Overflow_text"][3])
	every_a += lang_data["every_a"][1]

############################################
## SET PARAMETERS FOR DESCRIPTION TEMPLATE #
############################################
params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email, "counter_width":counter_width, "enable_property_desc":enable_property_desc, "sync_property_desc":sync_property_desc, "async_property_desc":async_property_desc, "input_property_desc":input_property_desc, "overflow_property_desc":overflow_property_desc, "minimum_height":minimum_height, "inputs_tikz":inputs_tikz, "outputs_tikz":outputs_tikz, "init_value_padded":init_value_padded, "sync_variation":sync_variation, "sync_text":sync_text, "async_variation":async_variation, "async_text":async_text, "every_a":every_a, "Enable_Overflow_text":Enable_Overflow_text })

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
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="counter_template.vhdl"
template = env.get_template(filename)
template = template.render(params_entity)

filename ="tmp/counter_{0}_Task{1}.vhdl".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)
###########################
### PRINT TASKPARAMETERS ##
###########################
print(task_parameters)
