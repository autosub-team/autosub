########################################################################
# generator.py -- Generates the individual tasks when needed
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import sqlite3 as lite
import datetime
import logger, common
import os

class taskGenerator (threading.Thread):
   def __init__(self, threadID, name, gen_queue, sender_queue, logger_queue):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.gen_queue = gen_queue
      self.sender_queue = sender_queue
      self.logger_queue = logger_queue

   ####
   # log_a_msg()
   ####
   def log_a_msg(self, msg, loglevel):
      self.logger_queue.put(dict({"msg": msg, "type": loglevel, "loggername": self.name}))

   def run(self):
      self.log_a_msg("Task Generator thread started", "INFO")

      while True:
         next_gen_msg = self.gen_queue.get(True) #blocking wait on gen_queue

         scriptpath = "tasks/task" + str(next_gen_msg.get('TaskNr')) + "/generator.sh"
#         command = "cd "+ scriptpath + ">> autosub.stdout 2>>autosub.stderr"
#         test_res = os.system(command)
         command = "sh "+ scriptpath + " " + str(next_gen_msg.get('UserId')) + " " + str(next_gen_msg.get('TaskNr')) + "  >> autosub.stdout 2>>autosub.stderr"
         test_res = os.system(command)
         if test_res:
            logmsg = "Failed to call generator script, return value: " + str(test_res)
            self.log_a_msg(logmsg, "DEBUG")
#         command = "cd - >> autosub.stdout 2>>autosub.stderr"
#         test_res = os.system(command)

         logmsg = "Generated individual task for user/tasknr:" + str(next_gen_msg.get('UserId')) + "/" + str(next_gen_msg.get('TaskNr'))
         self.log_a_msg(logmsg, "DEBUG")

         common.send_email(self.sender_queue, str(next_gen_msg.get('UserEmail')), str(next_gen_msg.get('UserId')), "Task", str(next_gen_msg.get('TaskNr')), "Your personal example", str(next_gen_msg.get('MessageId')))



         
