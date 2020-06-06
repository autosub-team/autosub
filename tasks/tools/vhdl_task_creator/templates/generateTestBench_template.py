#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task {{ task_name }}
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) ADD HERE: year, author, email
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys

from jinja2 import FileSystemLoader, Environment
#################################################################

task_parameters=sys.argv[1] 
random_tag=sys.argv[2]

###################################
#   GENERATE TESTBENCH/VECTORS    #
###################################
params = {}
params.update({"random_tag":random_tag})
# ADD HERE: generation of testbench parts / parameters

######################################
#  FILL AND PRINT TESTBENCH TEMPLATE #
######################################
env = Environment(trim_blocks = True, lstrip_blocks = True)
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"
template = env.get_template(filename)
template = template.render(params)

print(template)
