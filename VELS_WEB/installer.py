#!/usr/bin/env python3

# Usage:
# python3 installer.py [path to autosub] [path to used autosub-config file]

import argparse
import configparser
import os
import sys
import urllib.request
import zipfile


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("autosub_path", help="absoulute path to autosub")
arg_parser.add_argument("configfile", help="absoulute path to used autosub config file")

args = arg_parser.parse_args()

autosub_path = args.autosub_path
configfile = args.configfile

#check if valid path
if(os.path.isdir(autosub_path) == False):
    print("Your autosub_path is not a valid path: " + autosub_path)
    print("Install Failed")
    sys.exit(1)

#check if config file exists
if(os.path.isfile(configfile) == False):
    print("Your config file does not exist: " + configfile)
    print("Install Failed")
    sys.exit(1)

#strip trailing / from autosub_path
autosub_path = autosub_path.rstrip('/')

#get path to the VELS_WEB itself
vels_web_path = os.path.dirname(os.path.realpath(__file__))

#get paths to databases from configfile
config = configparser.ConfigParser()
config.readfp(open(configfile))

try:
    semesterdb_file = config.get('general', 'semesterdb')
except:
    print("Your configfile has no semesterdb specified")
    print("Assuming:" + autosub_path +"/src/semester.db")
    semesterdb = autosub_path + "/" +"src/semester.db"

try:
    coursedb_file = config.get('general', 'coursedb')
except:
    print("Your configfile has no coursedb specified")
    print("Assuming:" + autosub_path +"/src/course.db")
    semesterdb = autosub_path + "/src/course.db"


#download and place web2py

web2py_url="http://www.web2py.com/examples/static/web2py_src.zip"
user_home_path = os.path.expanduser('~')

local_file = user_home_path + "/web2py.zip"

print("Downloading web2py to " + local_file)
urllib.request.urlretrieve(web2py_url, local_file)
print("Download finished")

print("Extracting web2py to " + user_home_path)
zip_ref = zipfile.ZipFile(local_file, 'r')
zip_ref.extractall(user_home_path)
zip_ref.close()
print("Unzip complete")

#Set all the needed symlinks

print("Setting up web2py")
os.symlink(vels_web_path,user_home_path+"/web2py/applications/VELS_WEB")

os.makedirs(vels_web_path+"/databases",exist_ok=True)
os.symlink(semesterdb_file,vels_web_path+"/databases/semester.db")
os.symlink(coursedb_file,vels_web_path+"/databases/course.db")

os.symlink(autosub_path+"/src/nr_mails_received.png",vels_web_path+"/static/images/nr_mails_received.png")
os.symlink(autosub_path+"/src/nr_mails_sent.png",vels_web_path+"/static/images/nr_mails_sent.png")
os.symlink(autosub_path+"/src/nr_questions_received.png",vels_web_path+"/static/images/nr_questions_received.png")
os.symlink(autosub_path+"/src/nr_users.png",vels_web_path+"/static/images/nr_users.png")

print("Setting up completed")
