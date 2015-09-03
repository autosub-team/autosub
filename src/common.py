########################################################################
# common.py -- common functions
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sqlite3 as lite
import os
import datetime
   
format_string='%Y-%m-%d %H:%M:%S'

####
# log_a_msg()
####
def log_a_msg(lqueue, lname, msg, loglevel):
   lqueue.put(dict({"msg": msg, "type": loglevel, "loggername": lname}))

####
#   check_dir_mkdir
#
#   returns 0 if the directory already existed, 1 if it had to be created.
####
def check_dir_mkdir(directory, lqueue, lname): 
   if not os.path.exists(directory):
      os.mkdir(directory)
      logmsg = "Created directory: " + directory
      log_a_msg(lqueue, lname, logmsg, "DEBUG")
      return 1
   else:
      logmsg = "Directory already exists: " + directory
      log_a_msg(lqueue, lname, logmsg, "WARNING")
      return 0

####
# send_email()
####
def send_email(queue, recipient, userid, messagetype, tasknr, body, messageid):
   queue.put(dict({"recipient": recipient, "UserId": str(userid), "message_type": messagetype, "Task": str(tasknr), "Body": body, "MessageId": messageid}))

####
#  connect_to_db()
####
def connect_to_db(dbname, lqueue, lname):
   # connect to sqlite database ...
   try:
      con = lite.connect(dbname)
   except:
      logmsg = "Failed to connect to database: " + dbname
      log_a_msg(lqueue, lname, logmsg, "ERROR")
      return -1, -1

   cur = con.cursor()
   return cur, con

####
# increment_db_statcounter()
####
def increment_db_statcounter(cur, con, countername):
   sql_cmd = "UPDATE StatCounters SET Value=(SELECT Value FROM StatCounters WHERE Name=='" + countername + "')+1 WHERE Name=='" + countername + "';"
   cur.execute(sql_cmd)
   con.commit();


def get_task_starttime(tasknr, lqueue, lname):
   curc, conc = connect_to_db('course.db', lqueue, lname)
   sqlcmd = "SELECT TaskStart FROM TaskConfiguration WHERE TaskNr == '"+ str(tasknr) +"'"
   curc.execute(sqlcmd)
   tstart_string = str(curc.fetchone()[0])
   conc.close()

   #format_string='%Y-%m-%d %H:%M:%S'
   return datetime.datetime.strptime(tstart_string, format_string)


def get_task_deadline(tasknr, lqueue, lname):
   curc, conc = connect_to_db('course.db', lqueue, lname)
   sqlcmd = "SELECT TaskDeadline FROM TaskConfiguration WHERE TaskNr == '"+ str(tasknr) +"'"
   curc.execute(sqlcmd)
   deadline_string = str(curc.fetchone()[0])
   conc.close()

   #format_string='%Y-%m-%d %H:%M:%S'
   return datetime.datetime.strptime(deadline_string, format_string)

####
# user_set_currentTask()
#
# Set the currentTask of the user with userid to tasknr.
####
def user_set_currentTask(cur, con, tasknr, userid):
   sql_cmd = "UPDATE Users SET CurrentTask='" + str(tasknr) + "' where UserId=='" + str(userid) + "';"
   cur.execute(sql_cmd)
   con.commit();

####
# user_get_currentTask()
#
# Get the surrentTask of the user with userid.
####
def user_get_currentTask(cur, con, userid):
   sql_cmd = "Select CurrentTask from Users where UserId=='" + str(userid) + "';"
   cur.execute(sql_cmd)
   res = cur.fetchone();
   return str(res[0]);


