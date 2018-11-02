#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task cache
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C): 2018, HAUER Daniel, daniel.hauer@tuwien.ac.at
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
import hashlib
from jinja2 import FileSystemLoader, Environment
#################################################################

task_parameters=sys.argv[1] 

# get task parameters
cache_size, block_length, tag_length, data_length, clock_polarity, hash_str = task_parameters.split('|')

# convert to integers
cache_size = int(cache_size)
block_length = int(block_length)
data_length = int(data_length)
tag_length = int(tag_length)
addr_length = block_length + tag_length

# define VHDL clock functions depending on task parameter
if(int(clock_polarity)==0):
    wrong_edge = "falling_edge"
    right_edge = "rising_edge"
else:
    wrong_edge = "rising_edge"
    right_edge = "falling_edge"


# generate random cache content (refer to documentation in TaskGenerator)
tag_values=[]
data_values=[]

hash_value1 = hashlib.sha256((hash_str+str(cache_size)+str(block_length)).encode()).hexdigest()
hash_value2 = hashlib.sha256((hash_str+str(data_length)+str(clock_polarity)).encode()).hexdigest()

for cnt in range(cache_size):
    tmp1=bin(int(hash_value1[(2*cnt):(2*cnt+2)],16))[2:].zfill(tag_length)
    tmp2=bin(int(hash_value2[(2*cnt):(2*cnt+2)],16))[2:].zfill(addr_length)
  
    tag_values.append(tmp1[0:tag_length])
    data_values.append(tmp2[0:data_length])

# generate 3 different correct addresses (adress with cache hit) and corresponding data for testbench
tmp = ('0'*(block_length-2))

correct_addr_set = "\"" + tag_values[0] + tmp+"00\", \"" + tag_values[1] + tmp+"01\", \"" + tag_values[2]+tmp+"10\""
correct_data_set = "\"" + data_values[0] + "\", \""  + data_values[1] + "\",\""   + data_values[2]+"\""

###################################
#   GENERATE TESTBENCH/VECTORS    #
###################################
params = {}
params.update({ \
    "addr_length":str(addr_length), "data_length":str(data_length), "tag_length":str(tag_length), \
    "block_length":str(block_length), "cache_size":str(cache_size),"wrong_edge":wrong_edge, \
    "right_edge":right_edge, "tag_values":tag_values,"data_values":data_values, \
    "correct_addr_set":correct_addr_set, "correct_data_set":correct_data_set \
})

######################################
#  FILL AND PRINT TESTBENCH TEMPLATE #
######################################
env = Environment(trim_blocks = True, lstrip_blocks = True)
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"
template = env.get_template(filename)
template = template.render(params)

print(template)
