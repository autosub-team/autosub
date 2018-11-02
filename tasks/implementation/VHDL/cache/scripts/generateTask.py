#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task cache
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C): 2018, HAUER Daniel, daniel.hauer@tuwien.ac.at
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

from random import randrange,choice
from math import ceil, log
import string
import hashlib

import string
import sys

from jinja2 import FileSystemLoader, Environment

import json

#################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]
language=sys.argv[4]


#####################
#  TASK GENERATION  #
#####################

# choose size of cache (5-32 entries -> 3-5 bit of address)
# must not be large than 32 to fit the later used random data generation
cache_size = randrange(5,33)

# calculate minimal number of bits, which are necessary to address whole cache (3-5)
block_length = ceil(log(cache_size,2))

# choose bit length of tags in cache (3-6)
# must not be large than 8 to fit the later used random data generation
tag_length = randrange(3,7)

# choose bit length data in cache (4-8)
# must not be large than 8 to fit the later used random data generation
data_length = randrange(4,9)

#total address bit length will therefore be: addr_length = block_length + tag_length (6-11)
addr_length = block_length + tag_length

#choose, if cache should work at falling or rising edge (0=rising, 1=falling)
clock_polarity=randrange(0,2)

# generate random key (string with 6 digits) for generation of random cache content
hash_str = ''.join(choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))


##############################
#  PARAMETER SPECIFYING TASK #
##############################

task_parameters=str(cache_size)+"|"+str(block_length)+"|"+str(tag_length)+"|"+str(data_length)+"|"+str(clock_polarity)+"|"+str(hash_str)


###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE #
###########################################
params_desc={}

tag_values=[]
data_values=[]

####### Generation of random cache content #######

#generate two unique but pseudorandom hash values (each 64 hex-digits) out of task parameters
hash_value1 = hashlib.sha256((hash_str+str(cache_size)+str(block_length)).encode()).hexdigest()
hash_value2 = hashlib.sha256((hash_str+str(data_length)+str(clock_polarity)).encode()).hexdigest()

# use these hash values to generate pseudorandom cache content
# each hash value has 64 hex-digits; each two hex digits are combined and therefore 32 8-Bit binary values can be generated from each hash value
# the 8 bit values are individually reduced depending on tag and data length 
# this allows generating large pseudorandom data out of short task parameters
for cnt in range(cache_size):
    tmp1=bin(int(hash_value1[(2*cnt):(2*cnt+2)],16))[2:].zfill(tag_length)
    tmp2=bin(int(hash_value2[(2*cnt):(2*cnt+2)],16))[2:].zfill(addr_length)
    
    tag_values.append(tmp1[0:tag_length])
    data_values.append(tmp2[0:data_length])

##################################################

params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email})
params_desc.update({"addr_length":str(addr_length), "data_length":data_length})
params_desc.update({"clock_polarity":str(clock_polarity), "cache_size":cache_size})
params_desc.update({"tag_values":tag_values, "data_values":data_values})

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
env = Environment(trim_blocks = True, lstrip_blocks = True)
env.loader = FileSystemLoader('templates/')
filename ="task_description/task_description_template_{0}.tex".format(language)
template = env.get_template(filename)
template = template.render(params_desc)

filename ="tmp/desc_{0}_Task{1}.tex".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)


######################################
# SET PARAMETERS FOR ENTITY TEMPLATE #
######################################
params_entity = {}
params_entity.update({"addr_length":str(block_length + tag_length), "data_length":data_length})

#############################
#   FILL ENTITY TEMPLATE    #
#############################
env = Environment(trim_blocks = True, lstrip_blocks = True)
env.loader = FileSystemLoader('templates/')
filename ="cache_template.vhdl"
template = env.get_template(filename)
template = template.render(params_entity)

filename ="tmp/cache_{0}_Task{1}.vhdl".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)

###########################
#   PRINT TASKPARAMETERS  #
###########################
print(task_parameters)
