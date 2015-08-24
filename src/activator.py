########################################################################
# worker.py -- runs the actual tests of task results
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import os
import common as c
import sqlite3 as lite
import time
import datetime

class taskActivator (threading.Thread):
   def __init__(self, threadID, name, gen_queue, sender_queue, logger_queue):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.sender_queue = sender_queue
      self.logger_queue = logger_queue
      self.gen_queue = gen_queue

   ####
   # thread code for the worker thread.
   ####
   def run(self):
      logmsg = "Starting " + self.name
      c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

      while True:

          curc, conc = c.connect_to_db('course.db', self.logger_queue, self.name)

          # first we need to know, for which tasks, the message has already been sent out ... ouch!
          sqlcmd="SELECT * from TaskConfiguration WHERE TaskActive==0;"
          curc.execute(sqlcmd)
          res = curc.fetchone()
          while res != None:
             logmsg='Task '+str(res[0])+' is still inactive'
             c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")
             # check if a tasks start time has come
             task_starttime = datetime.datetime.strptime(res[1], c.format_string)
             
             # check if any users are waiting for that task

             res = curc.fetchone()

#          time.sleep(3600) # it's more than enough to check every hour!
          time.sleep(6) # for testing purposes only!




