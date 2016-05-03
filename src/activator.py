##########################################################################
# activator.py -- check periodically, if the starttime of a task has come.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
##########################################################################

import threading
import os
import common as c
import sqlite3 as lite
import time
import datetime

class taskActivator (threading.Thread):
   def __init__(self, threadID, name, gen_queue, sender_queue, logger_queue, coursedb, semesterdb):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.sender_queue = sender_queue
      self.logger_queue = logger_queue
      self.gen_queue = gen_queue
      self.coursedb = coursedb
      self.semesterdb = semesterdb


   def activator_loop(self):
       curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)

       # first we need to know, for which tasks, the message has already been sent out
       sql_cmd = "SELECT * FROM TaskConfiguration WHERE TaskActive==0;"
       curc.execute(sql_cmd)
       res = curc.fetchone()
       while res != None:
          TaskNr = res[0]
          logmsg = "Task {0} is still inactive".format(str(TaskNr))
          c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")
          # check if a tasks start time has come
          task_starttime = datetime.datetime.strptime(res[1], c.format_string)
          if task_starttime < datetime.datetime.now():
             # first, let's set the task active!
             data = {'tasknr': TaskNr}
             sql_cmd = "UPDATE TaskConfiguration SET TaskActive = 1 WHERE TaskNr == :tasknr;"
             curc.execute(sqlcmd, data)
             conc.commit()
 
             # next, check if any users are waiting for that task
             curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)
             data = {'tasknr': TaskNr}
             sqlcmd = "SELECT * FROM Users WHERE CurrentTask == :tasknr;"
             curs.execute(sqlcmd, data)
             nextuser = curs.fetchone()
             while nextuser != None:
                logmsg="The next example is sent to User {0} now.".format(str(TaskNr))
                c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")
                UserId = nextuser[0]
                UserEmail = nextuser[2]

                try:
                   data = {'tasknr': TaskNr}
                   sql_cmd = "SELECT GeneratorExecutable FROM TaskConfiguration WHERE TaskNr == :tasknr;"
                   curc.execute(sql_cmd, data)
                   res = curc.fetchone()
                except:
                   logmsg = "Failed to fetch Generator Script for Tasknr: "+ str(TaskNr) 
                   logmsg = logmsg + "from the Database! Table TaskConfiguration corrupted?"
                   c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")

                if res != None:
                   logmsg="Calling Generator Script: " + str(res[0])
                   c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                   logmsg="UserID " + str(UserId) + ",UserEmail " + str(UserEmail)
                   c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                   self.gen_queue.put(dict({"UserId": str(UserId), "UserEmail": str(UserEmail), "TaskNr": str(TaskNr), "MessageId": ""}))
                else:
                   c.send_email(self.sender_queue, str(UserEmail), str(UserId), "Task", str(TaskNr), "", "")

                nextuser = curs.fetchone() 

          res = curc.fetchone()

       conc.close() 


   ####
   # thread code for the worker thread.
   ####
   def run(self):
      logmsg = "Starting " + self.name
      c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

      while True:
         self.activator_loop()
#        time.sleep(3600) # it's more than enough to check every hour!
         time.sleep(60) # for testing purposes only!


