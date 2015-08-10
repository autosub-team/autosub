########################################################################
# commoon.py -- common functions
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import sqlite3 as lite

####
# log_a_msg()
####
def log_a_msg(lqueue, lname, msg, loglevel):
   lqueue.put(dict({"msg": msg, "type": loglevel, "loggername": lname}))

####
# send_email()
####
def send_email(queue, recipient, userid, messagetype, tasknr, body, messageid):
   queue.put(dict({"recipient": recipient, "UserId": userid ,"message_type": messagetype, "Task": tasknr, "Body": body, "MessageId": messageid}))

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

   cur = con.cursor()
   return cur, con

