#!/usr/bin/env python3

########################################################################
# LogicFormulaCreator.py 
# Generates a logic formula for given TaskParameters
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
import re

def toBase3(number,length):
    remainder=0
    dividend=number
    base3Nr=""

    while dividend != 0 :
        remainder = dividend % 3 
        dividend = dividend // 3
        base3Nr+=str(remainder)
    base3Nr=base3Nr.zfill(length)
    return [int(x) for x in base3Nr]

def toBase2(number,length):
    return [int(x) for x in bin(number)[2:].zfill(length)]

def createFromParameters(taskParameter):
    taskParameter=int(taskParameter)
    gates= toBase3(taskParameter>>41,5)
    inputsEnableLvl1= toBase2((taskParameter & (2**41-1))>>25,16)
    inputsNegateLvl1= toBase2((taskParameter & (2**25-1))>>9,16)
    inputsNegateLvl2= toBase2((taskParameter & (2**9-1))>>5,4)
    outputsNegate= toBase2(taskParameter & (2**5-1),5)

    #print(gates,inputsEnableLvl1,inputsNegateLvl1,inputsNegateLvl2,outputsNegate)

    gate_type={0:" and ",1:" or ",2:" xor "}
    negation_type={0:"",1:"not "}


    for i in range(len(gates)):
        gates[i]=gate_type[gates[i]]

    for i in range(len(inputsNegateLvl1)):
        inputsNegateLvl1[i]=negation_type[inputsNegateLvl1[i]]

    for i in range(len(inputsNegateLvl2)):
        inputsNegateLvl2[i]=negation_type[inputsNegateLvl2[i]]

    for i in range(len(outputsNegate)):
        outputsNegate[i]=negation_type[outputsNegate[i]]

    #print(gates,inputsEnableLvl1,inputsNegateLvl1,inputsNegateLvl2,outputsNegate)


    inputsLvl1_lables={}
    for key in [0, 4,8,12]:
        inputsLvl1_lables[key] = 'A'
    for key in [1, 5, 9,13]:
        inputsLvl1_lables[key] = 'B'
    for key in [2, 6, 10,14]:
        inputsLvl1_lables[key] = 'C'
    for key in [3, 7, 11,15]:
        inputsLvl1_lables[key] = 'D'

    expression=outputsNegate[4]+"( "+                                         \
               outputsNegate[0]+inputsNegateLvl2[0]+"( cond0 )"+gates[4]+     \
               outputsNegate[1]+inputsNegateLvl2[1]+"( cond1 )"+gates[4] +    \
               outputsNegate[2]+inputsNegateLvl2[2]+"( cond2 )"+gates[4]+     \
               outputsNegate[3]+inputsNegateLvl2[3]+"( cond3 )"+              \
               " )"

    conditions_type={2: "x0gx1", 3: "x0gx1gx2", 4: "x0gx1gx2gx3"} # type of conditions possible, x inputs, g gate
    conditions=[inputsEnableLvl1[0:4].count(1),inputsEnableLvl1[4:8].count(1),inputsEnableLvl1[8:12].count(1),inputsEnableLvl1[12:].count(1)]


    for i in range(len(conditions)):
        conditions[i]=conditions_type[conditions[i]]


    for i in range(0,4):
        x_num=0
        conditions[i]=re.sub("g",gates[i],conditions[i])
        for input_num in range(i*4,(i+1)*4):
            if(inputsEnableLvl1[input_num]==1):
                conditions[i]=re.sub("x"+str(x_num),inputsNegateLvl1[input_num]+inputsLvl1_lables[input_num],conditions[i])
                x_num+=1
        expression=re.sub("cond"+str(i),conditions[i],expression)
    
    expression=re.sub("not not ","",expression)#strip double negations 

    return expression
