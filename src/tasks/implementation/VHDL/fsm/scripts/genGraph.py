#!/bin/python3

########################################################################
# genGraph.py for VHDL task fsm
# Generates a state chart from given task parameters for task fsm
# Use to retrieve a state chart, if something went wrong with generation
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
#                    Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

from graphviz import Digraph
import sys

num_nodes = 5
node_names=[]
for i in range(0,num_nodes):
    if(i==0):
        node_names.append("START")
    else:
        node_names.append("S{0}".format(i-1))


nodematrix=eval(sys.argv[1])


f = Digraph('finite_state_machine', filename='fsm')
f.format='png'
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
         if nodematrix[i][j] != "":
            f.edge(node_names[i], node_names[j]," "+ nodematrix[i][j]+ "  ")

f.render()

