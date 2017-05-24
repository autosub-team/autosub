#!/usr/bin/env python3

########################################################################
# generateTestBench.py for VHDL task arithmetic
# Generates testvectors and fills a testbench for specified taskParameters
#
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sys
import string
from random import randrange
from random import shuffle
from bitstring import Bits
import math

######################################
#### GENERATION OF RANDOM NUMBERS ####
######################################

# type                real range                   for random.randrange
# n bit unsigned      [0 .. 2^n -1]                 --> [0 ... 2^n )             --> randrange(0,2**n)
# n bit 2s complement [-2^(n-1) ... 2^(n-1)-1]      --> [-2^(n-1) ... 2^(n-1) )  --> randrange(-(2**(n-1)),2**(n-1))
# n bit 1s complement [-(2^(n-1)-1) ... 2^(n-1)-1)] --> take 2s complement and -1 if negative


def to_unsigned(n,v):
   bits=Bits(uint=v,length=n).bin
   return bits

def to_comp2(n,v):
   bits=Bits(int=v,length=n).bin
   return bits

def to_comp1(n,v):
   bits_raw=Bits(uint=abs(v),length=n)
   if(v<0):
      bits= (bits_raw.__invert__()).bin
   else:
      bits= bits_raw.bin
   
   return bits


def rand_unsigned(n):
   randNr=randrange(0,2**n)
   bits=Bits(uint=randNr,length=n).bin
   return [randNr,bits] 

def rand_comp2(n):
   randNr=randrange(-(2**(n-1)),2**(n-1))
   bits=Bits(int=randNr,length=n).bin
   return [randNr,bits] 

def rand_comp1(n):
   randNr=randrange(0,2**(n-1)-1)
   bits_raw=Bits(uint=randNr,length=n)
   
   negate=randrange(0,2) #make it negative?
   if(negate==0):
      bits= bits_raw.bin;
   else:
      bits= (~bits_raw).bin
      randNr=-randNr
   
   return [randNr,bits]

###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################
taskParameters=int(sys.argv[1]) 
params={}

#|2|1|5|5|5| bits from taskParameters

#the bit widths of input 1 & 2 and the output
i1_width= taskParameters & (2**5-1)
i2_width= (taskParameters & (2**10-1))>>5
o_width=  (taskParameters & (2**15-1))>>10

#operation 0->ADD, 0->SUB
operation= (taskParameters & (2**16-1))>>15

#operand style: 0-> unsigned, 1->1s complement, 2->2s complement
operand_style=(taskParameters & (2**18-1))>>16

###################################################################

v=[] #testvectors

########################################
##### GENERATION VALID = 0 TESTS #######
########################################
numTestWrong=randrange(10,20)  

#first create valid=0 szenarios
if(operand_style==0): #unsigned [0 .. 2^n -1] 
   i1_min= 0
   i2_min= 0
   i1_max= 2**i1_width - 1
   i2_max= 2**i2_width - 1  
   i1=0
   i2=0

   if(operation==0):  #add
      for i in range(0,numTestWrong):
         # + + + overflow
         i1= i1_max - randrange(i2_min , math.floor(1/2*i2_max) )
         i2= randrange(math.floor(1/2*i2_max) , i2_max)
          
         i1_bits=to_unsigned(i1_width,i1)
         i2_bits=to_unsigned(i2_width,i2)
         v.append('\n'+12*" "+'-- ({0}) , ({1}) \n'.format(i1,i2)+12*" "+'("{0}","{1}")'.format(i1_bits,i2_bits))

   elif(operation==1):  #sub
      for i in range(0,numTestWrong):
         # + - + underlow
         i1=i1_min + randrange(i2_min , math.floor(1/2*i2_max))
         i2=randrange( math.floor(1/2*i2_max) , i2_max)

         i1_bits=to_unsigned(i1_width,i1)
         i2_bits=to_unsigned(i2_width,i2)
         v.append('\n'+12*" "+'-- ({0}) , ({1}) \n'.format(i1,i2)+12*" "+'("{0}","{1}")'.format(i1_bits,i2_bits))

elif(operand_style==2): #2comp  -2^(n-1) ... 2^(n-1)-1
   #all absolutes
   i1_min= 2**(i1_width-1)
   i2_min= 2**(i2_width-1)
   i1_max= 2**(i1_width-1)-1
   i2_max= 2**(i2_width-1)-1  
   i1=0
   i2=0 

   if(operation==0): #add
      for i in range(0,numTestWrong):
         errorCase=randrange(0,2)
         if(errorCase==0):
            ## - + - underflow
            i1= - i1_min + randrange(0 , math.floor(1/2*i2_min) )
            i2= - randrange( math.floor(1/2*i2_min) , i2_min )
         elif(errorCase==1):
            ## + + + overflow
            i1= i1_max - randrange(0 , math.floor(1/2*i2_max) )
            i2= randrange( math.floor(1/2*i2_max) , i2_max)

         i1_bits=to_comp2(i1_width,i1)
         i2_bits=to_comp2(i2_width,i2) 
         v.append('\n'+12*" "+'-- ({0}) , ({1}) \n'.format(i1,i2)+12*" "+'("{0}","{1}")'.format(i1_bits,i2_bits))     
    
   if(operation==1): #sub
      for i in range(0,numTestWrong):
         errorCase=randrange(0,2)
         if(errorCase==0):
         ## + - - overflow 
            i1= i1_max - randrange(0 , math.floor(1/2*i2_min) )
            i2= - randrange( math.floor(1/2*i2_min) , i2_min)

         elif(errorCase==1):
         ## - - + underflow
            i1= - i1_min + randrange(0 , math.floor(1/2*i2_max) )
            i2= randrange( math.floor(1/2* i2_max) , i2_max)

         i1_bits=to_comp2(i1_width,i1)
         i2_bits=to_comp2(i2_width,i2)
         v.append('\n'+12*" "+'-- ({0}) , ({1}) \n'.format(i1,i2)+12*" "+'("{0}","{1}")'.format(i1_bits,i2_bits)) 

elif(operand_style==1): #2comp [-(2^(n-1)-1) ... 2^(n-1)-1)]
   #all absolutes
   i1_min= 2**(i1_width-1)-1
   i2_min= 2**(i2_width-1)-1
   i1_max= 2**(i1_width-1)-1
   i2_max= 2**(i2_width-1)-1 
   i1=0
   i2=0  


   if(operation==0): #add
      for i in range(0,numTestWrong):
         errorCase=randrange(0,2)
         if(errorCase==0):
            ## - + - underflow
            i1= - i1_min + randrange(0 , math.floor(1/2*i2_min) )
            i2= - randrange( math.floor(1/2*i2_min) , i2_min )
         elif(errorCase==1):
            ## + + + overflow
            i1= i1_max - randrange(0 , math.floor(1/2*i2_max) )
            i2= randrange( math.floor(1/2*i2_max) , i2_max)

         i1_bits=to_comp1(i1_width,i1)
         i2_bits=to_comp1(i2_width,i2)
         v.append('\n'+12*" "+'-- ({0}) , ({1}) \n'.format(i1,i2)+12*" "+'("{0}","{1}")'.format(i1_bits,i2_bits))       
    
   if(operation==1): #sub
      for i in range(0,numTestWrong):
         errorCase=randrange(0,2)
         if(errorCase==0):
         ## + - - overflow 
           i1= i1_max - randrange(0 , math.floor(1/2*i2_min) )
           i2= - randrange( math.floor(1/2*i2_min) , i2_min)

         elif(errorCase==1):
         ## - - + underflow
            i1= - i1_min + randrange(0 , math.floor(1/2*i2_max) )
            i2= randrange( math.floor(1/2* i2_max) , i2_max)

         i1_bits=to_comp1(i1_width,i1)
         i2_bits=to_comp1(i2_width,i2)
         v.append('\n'+12*" "+'-- ({0}) , ({1}) \n'.format(i1,i2)+12*" "+'("{0}","{1}")'.format(i1_bits,i2_bits))  


########################################
##### GENERATION RANDOM TESTS ##########
########################################

rand_style_func= None;
if(operand_style==0):
    rand_style_func=rand_unsigned
elif(operand_style==1):
    rand_style_func=rand_comp1
else:
    rand_style_func=rand_comp2
  
numTestRandom=randrange(10,20) 
 

for i in range(0,numTestRandom):
    i1,i1_bits=rand_style_func(i1_width)
    i2,i2_bits=rand_style_func(i2_width)
    v.append('\n'+12*" "+'-- ({0}) , ({1}) \n'.format(i1,i2)+12*" "+'("{0}","{1}")'.format(i1_bits,i2_bits))

########################################
######### SHUFFLE, JOIN, FORMAT ########
########################################
shuffle(v)

for i in range(len(v)-1) :
    v[i]+=","

testPattern=("").join(v) 


#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE # 
#########################################
operation_dict={0:"ADD",1:"SUB"}
operand_style_dict={0:"unsigned",1:"comp1",2:"comp2"}

params.update({"I1": i1_width, "I2": i2_width, "O": o_width})
params.update({"OPERATION": operation_dict[operation], "OPSTYLE": operand_style_dict[operand_style]})
params.update({"TESTPATTERN": testPattern})
###########################
# FILL TESTBENCH TEMPLATE #
###########################
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))

