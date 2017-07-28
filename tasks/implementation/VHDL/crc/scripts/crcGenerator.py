#!/usr/bin/env python3

########################################################################
# crcGenerator.py #
# Generates a crc for a given message and generator polynom
# Copyright (C) 2015 Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

def genCRC(msg,gen):
    
    crc_len=len(gen)-1
    msg = msg +crc_len*"0" 

    msg = list(msg)
    gen = list(gen)

    for i in range(len(msg)-crc_len):
        # If top bit 1, perform modulo 2 xor
        if msg[i] == '1':
            for j in range(len(gen)):
                # on each index 
                msg[i+j] = str((int(msg[i+j])+int(gen[j]))%2)

    return ''.join(msg[-crc_len:]) 
