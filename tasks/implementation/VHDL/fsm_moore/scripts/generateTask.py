#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task fsm_moore
# Generates random tasks, generates TaskParameters, fill
# entity and description templates
#
# Copyright (C) 2017 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
#
# Implementation node: Internally the finite state machine is treated
#                      like a mealy state machine in order to be able
#                      to reuse code of the mealy task version
########################################################################

from graphviz import Digraph
from random import randrange
from copy import copy
import math
import string
import sys

from jinja2 import FileSystemLoader, Environment

#################################################################

# generate random 2 bit binary
def rand_bin2():
   r=randrange(0,4)
   return "{0:#04b}".format(r).split('b')[1]

########################################################################

# does the random transition matrix generate a state graph
def is_done(nodes, num_nodes):
   # check if all nodes have an outgoing edge:
   for i in range(0, num_nodes):
      for j in range(1, num_nodes): # outgoing edge may only be to n>0!
         if (nodes[i][j] == 1) and (i != j):
            break
         if j == num_nodes-1:
            return False # -> found at least one node that has no outgoing edge.

   # check if all nodes except START have an incoming edge:
   for j in range(1, num_nodes):
       for i in range(1, num_nodes):
         if (nodes[i][j]==1) and (i != j):
            break
         if i == num_nodes-1:
            return False # -> found at least one node that has no incoming edge.

   return True

########################################################################

# number outgoing edges of a node
def num_outgoing(nodedesc, num_nodes):
   num_edges = 0

   for i in range(0, num_nodes, 1):
      if nodedesc[i] > 0:
         num_edges = num_edges + 1

   return num_edges

########################################################################

# assign each transition in transitionmatrix an input value
def num_to_labels(nodematrix, num_nodes):
   nodes = list(list("" for variable in range(0, num_nodes, 1)) for variable in range(0, num_nodes, 1))

   for i in range (0, num_nodes, 1):
      available_inputs=["00","01","10","11"]
      for j in range(0, num_nodes, 1):
         if nodematrix[i][j] > 0:
            inp_nr = randrange(0,len(available_inputs))
            inp= available_inputs[inp_nr]
            available_inputs.remove(inp)
            nodes[i][j]='{0}'.format(inp)
   return nodes

########################################################################

user_id=sys.argv[1]
task_nr=sys.argv[2]
submission_email=sys.argv[3]
language=sys.argv[4]

params_desc={}

#####################
#  TASK GENERATION  #
#####################
num_nodes = 4 #CONFIGURE HERE


###################################################################
#KNOWN BUG: Sometimes the num_trans condition can not be fullfilled
#           -->redo after cycle_max tried cycles
##################################################################
genSuccess= False
nodemartix= None
cycle_max=100

# create a list of lists as a 'matrix' that contains all
# the transitions from node in line to node in column

# first step: matrix with 0 = no transmittion, 1 = transmission, no self transmissions
while not genSuccess:
   redoGen=False

   nodematrix = list(list(0 for variable in range(0,num_nodes,1)) for variable in range(0,num_nodes,1))

   num_cycle= 0
   num_trans=0
   lastnode = 0
   while (not is_done(nodematrix, num_nodes) or num_trans < (num_nodes -1) * 2):
      nextnode=randrange(1,num_nodes)
      if nodematrix[lastnode][nextnode] == 0 and (num_outgoing(nodematrix[lastnode], num_nodes) < (num_nodes-1)) and (lastnode != nextnode):
         nodematrix[lastnode][nextnode] = 1
         lastnode=nextnode
         num_trans=num_trans+1;

      num_cycle=num_cycle+1
      if num_cycle==cycle_max:
         redoGen=True
         break

   if(redoGen==True):
      genSuccess=False
      continue
   else:
      genSuccess=True
      break

labeled_trans = num_to_labels(nodematrix, num_nodes)

filename_statechart = "fsm_{0}_Task{1}".format(user_id,task_nr)
f = Digraph('finite_state_machine', filename='tmp/' + filename_statechart)
f.format='png'
f.attr('graph',overlap='false',size="7,8!")
f.attr('node', shape='circle')
f.attr('edge',overlap='false')

# states and their output
state_outputs = []
node_names= []

for i in range(0,num_nodes):
    output = rand_bin2()
    state_outputs.append(output)

    if(i==0):
        node_names.append("START\n00")
    else:
        node_names.append("S{0}\n{1}".format(i-1,output))

#create edges labled with input values
for i in range (0, num_nodes, 1):
      for j in range(0, num_nodes, 1):
         if nodematrix[i][j] > 0:
            f.edge(node_names[i], node_names[j]," "+ labeled_trans[i][j]+ "  ")

f.render()

##############################
## PARAMETER SPECIFYING TASK##
##############################
# adds /output so each edge is input/output as in a mealy state machine
for outer in range(0,num_nodes):
    for inner in range(0,num_nodes):
        if labeled_trans[outer][inner]:
            labeled_trans[outer][inner] += "/" + state_outputs[inner]

#format for task_parameters

node_trans=[]
for i in range(0, num_nodes):
   node_trans.append("{}".format(str(labeled_trans[i])))


for i in range(0,num_nodes-1):
   node_trans[i]+=","

task_parameters="["+"".join(node_trans)+"]"

############################################
## SET PARAMETERS FOR DESCRIPTION TEMPLATE #
############################################
params_desc.update({"TASKNR":str(task_nr), "SUBMISSIONEMAIL":submission_email, \
                    "STATECHART":"{"+filename_statechart+"}"})

##############################
## FILL DESCRIPTION TEMPLATE #
##############################
env = Environment()
env.loader = FileSystemLoader('templates/')
filename ="task_description/task_description_template_{0}.tex".format(language)
template = env.get_template(filename)
template = template.render(params_desc)

filename ="tmp/desc_{0}_Task{1}.tex".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)

################################################
# SET & FILL PARAMETERS FOR PACKAGE TEMPLATE   #
################################################
params_package={"num_states":num_nodes}

#############################
#   FILL ENTITY TEMPLATE    #
#############################
env = Environment(trim_blocks=True)
env.loader = FileSystemLoader('templates/')
filename ="fsm_pkg_template.vhdl"
template = env.get_template(filename)
template = template.render(params_package)

filename ="tmp/fsm_pkg_{0}_Task{1}.vhdl".format(user_id,task_nr)
with open (filename, "w") as output_file:
    output_file.write(template)

############################
##   PRINT TASKPARAMETERS  #
############################
print(task_parameters)
