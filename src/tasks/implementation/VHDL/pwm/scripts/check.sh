cd $user_task_path

##########################
## TASK CONSTRAINT CHECK #
##########################

#check for the keywords after and wait
if `egrep -oq "(wait|after)" pwm_beh.vhdl`
then
   echo "Task$2 using forbiddden keywords for user with ID $1!"
   echo "You are not complying to the specified rules in your task discription." > error_msg
   echo "You are not using the input clock to generate your signal! You are either using the keyword 'after' or 'wait'." >> error_msg
   echo "Use counting of periods of the input clock to generate the output PWM. Do not use 'after' or 'wait' signal generation." >> error_msg
   exit $FAILURE
fi