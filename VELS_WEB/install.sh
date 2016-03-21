#!/bin/bash
#$1 path to autosub/src

if [ -z $1 ];
then
	echo "Usage: ./install.sh [path to root autosub directory]"
	exit 0
fi


VELS_WEB_PATH=$(readlink -f $0|xargs dirname)
AUTOSUB_ROOT_PATH=$(echo $1 | sed 's:/*$::') #strip trailing /

#download and place web2py
cd /home/$USER
wget http://www.web2py.com/examples/static/web2py_src.zip
unzip web2py_src.zip 
rm web2py_src.zip

#set symbiloc links
ln -s $VELS_WEB_PATH /home/$USER/web2py/applications/VELS_WEB 
mkdir $VELS_WEB_PATH/databases
ln -s $AUTOSUB_ROOT_PATH/semester.db $VELS_WEB_PATH/databases/semester.db
ln -s $AUTOSUB_ROOT_PATH/course.db $VELS_WEB_PATH/databases/course.db
ln -s $AUTOSUB_ROOT_PATH/nr_mails_received.png $VELS_WEB_PATH/static/images/nr_mails_received.png
ln -s $AUTOSUB_ROOT_PATH/nr_mails_sent.png $VELS_WEB_PATH/static/images/nr_mails_sent.png
ln -s $AUTOSUB_ROOT_PATH/nr_questions_received.png $VELS_WEB_PATH/static/images/nr_questions_received.png
ln -s $AUTOSUB_ROOT_PATH/nr_users.png $VELS_WEB_PATH/static/images/nr_users.png

cd -
