#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task fsm_mealy
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
import string
from copy import copy
from random import randrange

from jinja2 import FileSystemLoader, Environment

###########################
######## HELPERS ##########
###########################
class Transition:
    def __init__(self,t_end,t_input,t_output):
        self.t_end=t_end
        self.t_input=t_input
        self.t_output=t_output
        self.t_taken= False

class Node:
    def __init__(self,name,distance):
        self.name=name
        self.trans_out=[]
        self.distance= distance
        #predecessor for shortest path from start
        self.predecessor= None

def formatTrans(trans):
    t_reset=0
    t_input=trans.t_input
    t_output=trans.t_output
    t_nextState=trans.t_end.name
    trans.t_taken= True

    return ['(\'{0}\',"{1}","{2}",{3})'.format(t_reset,t_input,t_output,t_nextState)]

#assemble the shortest way from start to node; start from node to START state, reverse the order at end
def wayToNode (node):
    result=[]
    curNode=node

    while curNode.predecessor!= curNode: #only START state has himself as predecessor
        pre=curNode.predecessor
        for trans in pre.trans_out:
            if(trans.t_end==curNode):
                result.extend(formatTrans(trans))
        curNode=pre
    result.append('(\'1\',"00","00",START)') #append a reset

    result.reverse()
    return result

#################################################################

taskParameters=sys.argv[1]
params={}

#########################################
########  PROCESS TASK PARAMETER ########
#########################################
transMatrix=eval(taskParameters)

numNodes = len(transMatrix)

nodes=[]
for i in range(0,numNodes):
    if(i==0):
        ns=Node("START",0)
        ns.predecessor=ns
        nodes.append(ns)
    else:
        nodes.append(Node("S{0}".format(i-1),float('inf')))

for i in range(0,numNodes):
    for j in range(0,numNodes):
        if(transMatrix[i][j]!=""):
            t_input,t_output=transMatrix[i][j].split("/")
            nodes[i].trans_out.append(Transition(nodes[j],t_input,t_output))

#########################################
########  FIND SHORTEST PATHS ###########
#########################################
# with Dijkstra's algorithm
# finds predecessor for each node for shortest path from start

Z=[] #processed nodes
N=nodes[:] #not processed node

while(len(N)!=0):
    distances= list(n.distance for n in N) #get all current distances
    curNodeIndex= distances.index(min(distances)) #get index of element with min distance
    curNode=N[curNodeIndex]
    N.remove(curNode)
    Z.append(curNode)


    for i in range(len(curNode.trans_out)):
        neighbor=curNode.trans_out[i].t_end
        if(neighbor.distance > curNode.distance+1): #previous calculated distance bigger
             neighbor.distance=curNode.distance+1
             neighbor.predecessor=curNode
# FOR DEBUG:
#print("")
#for n in nodes:
#    print(n.name+": distance= "+str(n.distance)+" pre= "+n.predecessor.name)
#print("")

#############################################
## ADD TESTVECTORS FOR DEFINED TRANSITIONS ##
#############################################
toTestNodes =nodes[1:] #nodes to test, every except start
testedNodes=[]
testVectors_def=[]

while(len(toTestNodes)!=0):
    #chose a random node to test
    testIndex=randrange(0,len(toTestNodes))
    nodeUnderTest=toTestNodes[testIndex]
    testedNodes.append(nodeUnderTest)
    toTestNodes.remove(nodeUnderTest)

    startToNodeNecessary=True

    startToNode=wayToNode(nodeUnderTest)

    #test all defined transitions from the nodeUnderTest
    for trans in nodeUnderTest.trans_out:
        #this trans was already covered in a previous test --> skip
        if(trans.t_taken==True):
            continue

        if(startToNodeNecessary):
            testVectors_def.extend(startToNode)

        #self transition -> no 'go to node from start' necessary for the next iteration
        if(trans.t_end==nodeUnderTest):
            testVectors_def.extend(formatTrans(trans))
            startToNodeNecessary=False

        #new transition to test, 'go to node from start' needed
        else:
            testVectors_def.extend(formatTrans(trans))
            startToNodeNecessary=True
#format for testbench, join
for i in range(len(testVectors_def)-1) :
    testVectors_def[i]+=","
testPattern_def=("\n"+12*" ").join(testVectors_def)

###############################################
## ADD TESTVECTORS FOR UNDEFINED TRANSITIONS ##
###############################################
# find for each node the not defined transitions
# which should result in output and state staying the same
undef_per_node = [None for x in range(numNodes)]
available_inputs = ["00", "01", "10", "11"]

for i in range(0, numNodes):
    undef_per_node[i] = available_inputs[:]
    for t in nodes[i].trans_out:
        # delete (tick off) defined transition input from list of all possible
        undef_per_node[i].remove(t.t_input)

# find the last outputs which results from the shortest way to each node
outputs_to_node = [None for x in range(numNodes)]
for i in range(0, numNodes):
    cur_node = nodes[i]

    # start only happens after reset which results in a 00 at output
    if i == 0:
        outputs_to_node[i] = "00"

    else:
        pre = nodes[i].predecessor

        # find the transition that is on the shortest path to the node and the
        # output it causes
        for trans in pre.trans_out:
            if trans.t_end == cur_node:
                outputs_to_node[i] = trans.t_output

testVectors_undef = []

#add tests for the udefined inputs for each state
for i in range(0,numNodes):
    nodeUnderTest = nodes[i]
    startToNode = wayToNode(nodeUnderTest)
    node_name = nodeUnderTest.name

    #add shortest path from start to the node
    testVectors_undef.extend(startToNode)

    # attach test transition for each undefined input
    for undef_inp in undef_per_node[i]:
        # (end, input, output)
        trans = Transition(nodeUnderTest, undef_inp, outputs_to_node[i])
        testVectors_undef.extend(formatTrans(trans))

#format for testbench, join
for i in range(len(testVectors_undef)-1) :
    testVectors_undef[i]+=","
testPattern_undef=("\n"+12*" ").join(testVectors_undef)

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE #
#########################################
params.update({"TESTPATTERN_DEF":testPattern_def, "TESTPATTERN_UNDEF":testPattern_undef, "num_states" : numNodes})

###########################
# FILL TESTBENCH TEMPLATE #
###########################
env = Environment(trim_blocks=True)
env.loader = FileSystemLoader('templates/')
filename ="testbench_template.vhdl"

template = env.get_template(filename)
template = template.render(params)

print(template)
