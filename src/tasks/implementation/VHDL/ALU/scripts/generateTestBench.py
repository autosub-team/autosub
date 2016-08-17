#!/usr/bin/env python3
import sys
import string
from random import shuffle

###########################
##### TEMPLATE CLASS ######
###########################
class MyTemplate(string.Template):
    delimiter = "%%"

#################################################################

x=sys.argv[1]
a,b,c,d,f,g=x
taskParameters=[int(a),int(b),int(c),int(d),int(f),int(g)]


params={}

inst_name =['ADD','SUB','AND','OR','XOR','Comparator','Shift Left','Shift Right','Rotate Left without Carry','Rotate Right without Carry']
flag_name=['Overflow','Carry','Zero','Sign','Odd Parity']
#########################################
######### GENERATE TESTVECTORS ########## 
#########################################

w=['0000']*16
carry=['0']*16
result_add=[]
result_flag=[]
result_shift=[]
result_carry=[]


for i in range(0,4):
    ind=0
    z=['0000']*(16*16)
    flag=['0']*(16*16)
    for A in range(0,16):
        if inst_name[taskParameters[i]]=='Shift Left':
            w[A]='{0:04b}'.format(A)[1:5]+'0'
            carry[A]='{0:04b}'.format(A)[0]

        elif inst_name[taskParameters[i]]=='Shift Right':
            w[A]='0'+'{0:04b}'.format(A)[0:3]
            carry[A]='{0:04b}'.format(A)[3]
                
        elif inst_name[taskParameters[i]]=='Rotate Left without Carry':
            w[A]='{0:04b}'.format(A)[1:5]+'{0:04b}'.format(A)[0]
            carry[A]='{0:04b}'.format(A)[0]

        elif inst_name[taskParameters[i]]=='Rotate Right without Carry':
            w[A]='{0:04b}'.format(A)[3]+'{0:04b}'.format(A)[0:3]
            carry[A]='{0:04b}'.format(A)[3]

        for B in range(0,16):
            
            if inst_name[taskParameters[i]]=='ADD':
                z[ind]='{0:05b}'.format(A+B)[1:5]
                c='{0:05b}'.format(A+B)[0] # carry
            elif inst_name[taskParameters[i]]=='SUB':
                b=int('{0:05b}'.format((B ^ 15)+1)[1:5],2) # two's complement for subtraction
                z[ind]='{0:05b}'.format(A+b)[1:5]
                c='{0:05b}'.format(A+b)[0] # carry            
            elif inst_name[taskParameters[i]]=='AND':
                z[ind]='{0:04b}'.format(A & B)
            elif inst_name[taskParameters[i]]=='OR':
                z[ind]='{0:04b}'.format(A | B)
            elif inst_name[taskParameters[i]]=='XOR':
                z[ind]='{0:04b}'.format(A ^ B)
            elif inst_name[taskParameters[i]]=='Comparator':
                z[ind]='{0:04b}'.format(A)
                if A>=B: flag[ind]='1'
                elif A<B: flag[ind]='0'                        

                
            if  i==0: # for ADD or SUB
                
                if flag_name[taskParameters[4]]=='Overflow':                
                    if inst_name[taskParameters[i]]=='ADD':
                        if (int(z[ind],2)<A or int(z[ind],2)<B): flag[ind]='1'           # overflow
                        else: flag[ind]='0'
                    elif inst_name[taskParameters[i]]=='SUB':
                        if (A<B): flag[ind]='1'           # carry
                        else: flag[ind]='0'
                    
                elif flag_name[taskParameters[4]]=='Carry':                
                    if c=='1': flag[ind]='1'           # carry
                    else: flag[ind]='0'

                elif flag_name[taskParameters[4]]=='Zero':
                    if z[ind]=='0000': flag[ind]='1'     # zero
                    else: flag[ind]='0'

                elif flag_name[taskParameters[4]]=='Sign': 
                    if z[ind][0]=='1': flag[ind]='1'     # sign
                    else: flag[ind]='0'
                    
            elif (i==1 and taskParameters[1]!=5) or (i==2 and taskParameters[2]!=5): # for AND, OR or XOR and comparator
                
                if flag_name[taskParameters[5]]=='Odd Parity':
                    parity = False
                    val=int(z[ind],2)
                    while val:
                        parity = not parity
                        val = val & (val - 1)
                    if (parity): flag[ind]='0'          # parity
                    else: flag[ind]='1'

                elif flag_name[taskParameters[5]]=='Zero':
                    if z[ind]=='0000': flag[ind]='1'      # zero
                    else: flag[ind]='0'

                elif flag_name[taskParameters[5]]=='Sign':     # sign
                    if z[ind][0]=='1': flag[ind]='1'
                    else: flag[ind]='0'

            ind+=1

    if i==0:
        z1=z
        flag1=flag
    elif i==1:
        z2=z
        flag2=flag
    elif i==2:
        z3=z
        flag3=flag
            
for k in range(0,16*16):
    result_add.append('("'+z1[k]+'","'+z2[k]+'","'+z3[k]+'")')
    result_flag.append("('"+flag1[k]+"','"+flag2[k]+"','"+flag3[k]+"')")

for i in range(len(result_add)-1):
    result_add[i]+=","
    result_flag[i]+=","
    
result_add=("\n"+(42)*" ").join(result_add)
result_flag=("\n"+(42)*" ").join(result_flag)

for k in range(0,16):
    result_shift.append('"'+w[k]+'"')
    result_carry.append("'"+carry[k]+"'")

for i in range(len(result_shift)-1):
    result_shift[i]+=","
    result_carry[i]+=","


result_shift=("\n"+(20)*" ").join(result_shift)
result_carry=("\n"+(20)*" ").join(result_carry)                    

#########################################
# SET PARAMETERS FOR TESTBENCH TEMPLATE # 
#########################################
params.update({"RESULT1":result_add,"FLAG":result_flag,"RESULT2":result_shift,"CARRY":result_carry,"INST1":inst_name[taskParameters[0]],"INST2":inst_name[taskParameters[1]],"INST3":inst_name[taskParameters[2]],"INST4":inst_name[taskParameters[3]]})
###########################
# FILL TESTBENCH TEMPLATE #
###########################
filename ="templates/testbench_template.vhdl"
with open (filename, "r") as template_file:
    data=template_file.read()
    s = MyTemplate(data)
    print(s.substitute(params))


