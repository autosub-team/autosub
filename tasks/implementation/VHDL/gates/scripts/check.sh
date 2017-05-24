cd $user_task_path

##########################
## TASK CONSTRAINT CHECK #
##########################

# check if  the user really uses the provided IEEE 1164 entities
# look for the entity names NAND, AND, OR, NOR, XOR, XNOR
# smallest search is for AND<N> and OR<N>; vhdl is not case sensitive

# user needs 5 gates to build the network
numgates=$(egrep -o "([Aa][Nn][Dd][2-4]|[Oo][Rr][2-4])" gates_beh.vhdl | wc -l)
aimednum=5

if [ "$numgates" -lt "$aimednum" ]
then
   echo "Task ${task_nr} not using the provided gate entities for user ${user_id}!"
   echo "You are not complying to the specified rules in your task discription." > error_msg
   echo "You are not using the provided IEEE 1164 gate entities." >> error_msg
   echo "Use the provided entities to build a gate network with the specified behavior." >> error_msg
   exit $FAILURE
fi

