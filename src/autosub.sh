#!/bin/bash

if [ -z $1 ]
then
   echo "Usage: ./autosub.sh [start|stop|restart] [config-file]"
   exit -1
fi

#################
#     START     #
#################
if [ $1 = "start" ]
then
   if [ -z "$2" ]
   then
      python3 autosub.py &
      echo $! > autosub.pid
      echo "No config file specified, using default.cfg!"
      echo "Started autosub with process id $PID"
   else
      python3 autosub.py --config-file $2 &
      echo $! > autosub.pid
      PID=$(cat autosub.pid 2> /dev/null)
      echo "Started autosub with process id $PID"
   fi

#################
#     STOP      #
#################
elif [ $1 = "stop" ]
then
   PID=$(cat autosub.pid 2> /dev/null)
   if [ -z "$PID" ]
   then
       echo "autosub.pid does not exist, try killing autosub with kill and its process id."
       exit -1
   else
       kill -30 $PID
       rm autosub.pid
       echo "Killed autosub"
   fi

############################
# RESTART = STOP + START   #
############################
elif [ $1 = "restart" ]
then
   # stop #
   PID=$(cat autosub.pid 2> /dev/null)
   if [ -z "$PID" ]
   then
       echo "autosub.pid does not exist, try killing autosub with kill and its process id and then start autosub."
       exit -1
   else
       kill -30 $PID
       rm autosub.pid
       echo "Killed autosub"
   fi

   # start #
   if [ -z "$2" ]
   then
      python3 autosub.py &
      echo $! > autosub.pid
      echo "No config file specified, using default.cfg!"
      echo "Started autosub with process id $PID"
   else
      python3 autosub.py --config-file $2 &
      echo $! > autosub.pid
      PID=$(cat autosub.pid 2> /dev/null)
      echo "Started autosub with process id $PID"
   fi

else
   echo "Usage: ./autosub.sh [start|stop|restart] [config-file]"
fi
