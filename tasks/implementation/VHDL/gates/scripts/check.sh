cd $user_task_path

##########################
## TASK CONSTRAINT CHECK #
##########################

# component declarations are not allowed, as they are not needed, as the package is included!
numcomponentdec=$(egrep -o "[Cc][Oo][Mm][Pp][Oo][Nn][Ee][Nn][Tt]" gates_beh.vhdl | wc -l)

if [ "$numcomponentdec" -ne 0 ]
then
   echo "Task ${task_nr}, user ${user_id} not complying to task constraints!"
   echo "You are declaring components in your behavior file." > error_msg
   echo "The components are already done using the package import. No need to redeclare them!" >> error_msg
   exit $FAILURE
fi

# any binary logic operator (keyword with whitespaces or tabs at begin and end) is not allowed!!
numoperators=$(egrep -o "([\t| ]+[Aa][Nn][Dd][\t| ]+|[\t| ]+[Nn][Aa][Nn][Dd][\t| ]+|[\t| ]+[Oo][Rr][\t| ]+|[\t| ]+[Nn][Oo][Rr][\t| ]+|[\t| ]+[Xx][Oo][Rr][\t| ]+|[\t| ]+[Xx][Nn][Oo][Rr][\t| ]+)" gates_beh.vhdl | wc -l)

if [ "$numoperators" -ne 0 ]
then
   echo "Task ${task_nr}, user ${user_id} not complying to task constraints!"
   echo "You are not complying to the specified rules in your task discription." > error_msg
   echo "You are using binary logic operators. Only use the provided IEEE 1164 gate entities." >> error_msg
   exit $FAILURE
fi

# check if  the user really uses the provided IEEE 1164 entities
# look for the entity names NAND, AND, OR, NOR, XOR, XNOR
# smallest search is for AND<N> and OR<N>; vhdl is not case sensitive

# user needs 5 gates to build the network
numgates=$(egrep -o "([Aa][Nn][Dd][2-4]|[Oo][Rr][2-4])" gates_beh.vhdl | wc -l)
aimednum=5

if [ "$numgates" -lt "$aimednum" ]
then
   echo "Task ${task_nr}, user ${user_id} not complying to task constraints!"
   echo "You are not complying to the specified rules in your task discription." > error_msg
   echo "You are not using the provided IEEE 1164 gate entities." >> error_msg
   echo "Use the provided entities to build a gate network with the specified behavior." >> error_msg
   exit $FAILURE
fi
