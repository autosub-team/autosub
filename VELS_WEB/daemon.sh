#!/bin/bash
#$1 start|stop
#$2 port
#$3 password

port=8000 #default port
password="notSecure" #default password

VELS_WEB_PATH=$HOME/web2py/applications/VELS_WEB
server_ip=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
if [ -n $2 ]; #port given
then
	port=$2         
fi

if [ -n $3 ]; #password given
then
	password=$3         
fi

if [ $1 = "start" ];
then
	web2py --nogui -i $server_ip -p $port -a $password -d $VELS_WEB_PATH/daemon.pid -c server.crt -k server.key &
elif [ $1 = "stop" ];
then
	PID=$(cat $VELS_WEB_PATH/daemon.pid)
	kill -SIGTERM $PID
else
	echo "Usage: ./daemon.sh [start|stop] [port] [password]"
fi

