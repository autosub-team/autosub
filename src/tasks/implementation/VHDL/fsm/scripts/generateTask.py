#!/usr/bin/env python3

########################################################################
# generateTask.py for VHDL task fsm
# Generates random tasks, generates TaskParameters, fill 
# entity and description templates
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
#                    Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

from graphviz import Digraph
from random import randrange
from copy import copy
import math
import string
import sys


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

def num_outgoing(nodedesc, num_nodes):
   num_edges = 0

   for i in range(0, num_nodes, 1):
      if nodedesc[i] > 0:
         num_edges = num_edges + 1

   return num_edges

def gen_rand_output():
   r=randrange(0,4)
   return "{0:#04b}".format(r).split('b')[1]


def num_to_labels(nodematrix, num_nodes):
   nodes = list(list("" for variable in range(0, num_nodes, 1)) for variable in range(0, num_nodes, 1))

   for i in range (0, num_nodes, 1):
      available_inputs=["00","01","10","11"]
      for j in range(0, num_nodes, 1):
         if nodematrix[i][j] > 0:
            outp = gen_rand_output()
            inp_nr = randrange(0,len(available_inputs))
            inp= available_inputs[inp_nr]
            available_inputs.remove(inp)
            nodes[i][j]='{0}/{1}'.format(inp,outp)
   return nodes


###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

userId=sys.argv[1]
taskNr=sys.argv[2]
submissionEmail=sys.argv[3]

paramsDesc={}


num_nodes = 5 #shall be configurabe eventually

###################################################################
#KNOWN BUG: Sometimes the num_trans condition can not be fullfilled
#           -->redo after cycle_max tried cycles
##################################################################
genSuccess= False
nodemartix= None
cycle_max=100

while not genSuccess:
   redoGen=False

   # create a list of lists as a 'matrix' that contains all
   # the transitions from node in line to node in column
   nodematrix = list(list(0 for variable in range(0,num_nodes,1)) for variable in range(0,num_nodes,1))

   num_cycle= 0
   num_trans=0
   lastnode = 0
   while (not is_done(nodematrix, num_nodes) or num_trans<10):
      nextnode=randrange(1,num_nodes)
      if nodematrix[lastnode][nextnode] == 0 and (num_outgoing(nodematrix[lastnode], num_nodes) < 4):
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


f = Digraph('finite_state_machine', filename='tmp/fsm')
f.format='pdf'
f.attr('graph',overlap='false',size="7,8!")
f.attr('node', shape='circle')
f.attr('edge',overlap='false')

node_names=[]
for i in range(0,num_nodes):
    if(i==0):
        node_names.append("START")
    else:
        node_names.append("S{0}".format(i-1))

for i in range (0, num_nodes, 1):
      for j in range(0, num_nodes, 1):
         if nodematrix[i][j] > 0:
            f.edge(node_names[i], node_names[j]," "+ labeled_trans[i][j]+ "  ")

f.render()



##############################
## PARAMETER SPECIFYING TASK##
##############################
node_trans=[]
for i in range(0, num_nodes):
   node_trans.append("{}".format(str(labeled_trans[i])))


for i in range(0,num_nodes-1):
   node_trans[i]+=","

taskParameters="["+"".join(node_trans)+"]"


############### ONLY FOR TESTING #######################
filename ="tmp/solution_{0}_Task{1}.txt".format(userId,taskNr)
with open (filename, "w") as solution:
    solution.write("For TaskParameters: " + str(taskParameters) + "\n")
    solution.write("FOOBAR")
#########################################################


###########################################
# SET PARAMETERS FOR DESCRIPTION TEMPLATE # 
###########################################
paramsDesc.update({"TASKNR":str(taskNr),"SUBMISSIONEMAIL":submissionEmail})

#############################
# FILL DESCRIPTION TEMPLATE #
#############################
filename ="templates/task_description_template.tex"
with open (filename, "r") as template_file:
    data=template_file.read()

filename ="tmp/desc_{0}_Task{1}.tex".format(userId,taskNr)
with open (filename, "w") as output_file:
    s = MyTemplate(data)
    output_file.write(s.substitute(paramsDesc))

###########################
### PRINT TASKPARAMETERS ##
###########################
print(taskParameters)
