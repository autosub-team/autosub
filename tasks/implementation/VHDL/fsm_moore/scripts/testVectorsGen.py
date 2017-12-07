#!/usr/bin/env python3

########################################################################
# testVectorsGen.py 
# Generates testvectors for the fsm, that covers every edge and node
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################


import sys
import string
from copy import copy
from random import randrange


###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
     delimiter = "%%"

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
        self.predessesor= None

def formatTrans(trans):
    t_reset=0
    t_input=trans.t_input
    t_output=trans.t_output
    t_nextState=trans.t_end.name
    trans.t_taken= True

    return ['(\'{0}\',"{1}","{2}",{3})'.format(t_reset,t_input,t_output,t_nextState)]

def wayToNode (node):
    result=[]
    curNode=node

    while curNode.predessesor!= curNode: #only start has himself as predessesor
        pre=curNode.predessesor
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
numNodes = 5

#########################################
########  PROCESS TASK PARAMETER ########
#########################################
nodes=[]
for i in range(0,numNodes):
    if(i==0):
        ns=Node("START",0)
        ns.predessesor=ns
        nodes.append(ns)
    else:
        nodes.append(Node("S{0}".format(i-1),float('inf')))

transMatrix=eval(taskParameters)


for i in range(0,numNodes):
    for j in range(0,numNodes):
        if(transMatrix[i][j]!=""):
            t_input,t_output=transMatrix[i][j].split("/")
            nodes[i].trans_out.append(Transition(nodes[j],t_input,t_output))

#########################################
########  FIND SHORTEST PATHS ###########
#########################################

Z=[] #processed nodes
N=nodes.copy() #not processed nodes


while(len(N)!=0):
    distances= list(n.distance for n in N) #get all current distances
    curNodeIndex= distances.index(min(distances)) #get index of element with min distance
    curNode=N[curNodeIndex]
    N.remove(curNode)
    Z.append(curNode)


    for i in range(len(curNode.trans_out)):
        neighbor=curNode.trans_out[i].t_end
        if(neighbor.distance > curNode.distance+1): #previious calculated distance bigger
             neighbor.distance=curNode.distance+1
             neighbor.predessesor=curNode        
#print("")
#for n in nodes:
#    print(n.name+": distance= "+str(n.distance)+" pre= "+n.predessesor.name)
#print("")
print("")

toTestNodes =nodes.copy()[1:] #nodes to test, every except start
testedNodes=[]
testVectors=[]
while(len(toTestNodes)!=0):
    #chose a random node to test
    testIndex=randrange(0,len(toTestNodes))
    nodeUnderTest=toTestNodes[testIndex]
    testedNodes.append(nodeUnderTest)
    toTestNodes.remove(nodeUnderTest)

    startToNodeNecessary=True

    startToNode=wayToNode(nodeUnderTest)

    
    #first look if has transition to self    
    for trans in nodeUnderTest.trans_out:
        if(trans.t_taken==True): #this trans was allready covered
            continue
        if(startToNodeNecessary):
            testVectors.extend(startToNode)            
        #self transition? if yes no go to node from start necessary next iteration
        if(trans.t_end==nodeUnderTest):
            testVectors.extend(formatTrans(trans))
            startToNodeNecessary=False
        else:
            testVectors.extend(formatTrans(trans))
            startToNodeNecessary=True

for i in range(0,len(testVectors)):
    print(testVectors[i])
