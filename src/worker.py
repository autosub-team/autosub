########################################################################
# worker.py -- runs the actual tests of task results
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import os

class worker (threading.Thread):
   def __init__(self, threadID, name, job_queue, sender_queue, logger_queue):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.job_queue = job_queue
      self.sender_queue = sender_queue
      self.logger_queue = logger_queue

   def run(self):
      logmsg = "Starting " + self.name
      self.logger_queue.put(dict({"msg": logmsg, "type": "INFO", "loggername": self.name}))

      while True:
         nextjob = self.job_queue.get(True)
         if nextjob:
             TaskNr=nextjob.get('taskNr')
             UserId=nextjob.get('UserId')
             user_email=nextjob.get('UserEmail')
             messageid=nextjob.get('MessageId')
             logmsg = self.name + ": got a new job: " + str(TaskNr) + "from the user with id: " + str(UserId)
             self.logger_queue.put(dict({"msg": logmsg, "type": "INFO", "loggername": self.name}))

             scriptpath = "tasks/task" + str(TaskNr) + "/tests.sh"
             command = "sh "+scriptpath+" " + str(UserId) + " " + str(TaskNr) + " >> autosub.stdout 2>>autosub.stderr"
             test_res = os.system(command)

             if test_res:
                logmsg = "Test failed! User: " + str(UserId) + " Task: " + str(TaskNr) + "return value:" + str(test_res)
                self.logger_queue.put(dict({"msg": logmsg, "type": "INFO", "loggername": self.name}))
                self.sender_queue.put(dict({"recipient": user_email, "UserId": str(UserId), "message_type": "Failed", "Task": str(int(TaskNr)), "MessageId": messageid}))
                if test_res == 512: # Need to read up on this but os.system() returns 256 when the script returns 1 and 512 when the script returns 2!
                   logmsg = "SecAlert: This test failed due to probable attack by user!"
                   self.logger_queue.put(dict({"msg": logmsg, "type": "INFO", "loggername": self.name}))
                   self.sender_queue.put(dict({"recipient": user_email, "UserId": str(UserId), "message_type": "SecAlert", "Task": str(int(TaskNr)), "MessageId": messageid}))
             else:
                logmsg = "Test succeeded! User: " + str(UserId) + " Task: " + str(TaskNr)
                self.logger_queue.put(dict({"msg": logmsg, "type": "INFO", "loggername": self.name}))
#                self.sender_queue.put(dict({"recipient": user_email, "UserId": str(UserId), "message_type": "Success", "Task": TaskNr, "MessageId": ""}))
                self.sender_queue.put(dict({"recipient": user_email, "UserId": str(UserId), "message_type": "Task", "Task": str(int(TaskNr)+1), "MessageId": messageid}))
