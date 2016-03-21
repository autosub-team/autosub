#!/bin/bash

if [ $1 = "start" ]
then
#   python3 autosub.py > autosub.log & 
   if [ -z "$2" ]
   then
      python3 $PYTHONPATH/autosub/autosub.py & 
      echo $! > /tmp/autosub.pid
   else
      python3 $PYTHONPATH/autosub/autosub.py --config-file $2 & 
      echo $! > /tmp/autosub.pid
   fi
elif [ $1 = "stop" ]
then
   PID=$(cat /tmp/autosub.pid)
   kill -30 $PID
   rm /tmp/autosub.pid
else
   echo "Usage: autosub.sh [start|stop] [CONFIGFILE]"
fi
