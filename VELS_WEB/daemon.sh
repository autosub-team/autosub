#!/bin/bash
#$1 start|stop
#$2 port
#$3 password

port=8000 #default port
password="notSecure" #default password

VELS_WEB_PATH=$HOME/web2py/applications/VELS_WEB
server_ip=$(ip -json -family inet addr show scope global | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['addr_info'][0]['local'])")

if [ -n $2 ]; #port given
then
	port=$2
fi

if [ -n $3 ]; #password given
then
	password=$3
fi

if [ -z $1 ];
then

	echo "Usage: ./daemon.sh [start|stop] [port] [password]"
	echo "After starting attach VELS_WEB to the given url to reach VELS_WEB"
	exit
fi

if [ $1 = "start" ];
then
	python $HOME/web2py/web2py.py --no_gui -i $server_ip -p $port -a $password -d $VELS_WEB_PATH/daemon.pid -c server.crt -k server.key &
elif [ $1 = "stop" ];
then
	PID=$(cat $VELS_WEB_PATH/daemon.pid)
	kill -SIGTERM $PID
else
	echo "Usage: ./daemon.sh [start|stop] [port] [password]"
	echo "After starting attach VELS_WEB to the given url to reach VELS_WEB"
fi
