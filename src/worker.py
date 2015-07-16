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

   ####
   # log_a_msg()
   ####
   def log_a_msg(self, msg, loglevel):
         self.logger_queue.put(dict({"msg": msg, "type": loglevel, "loggername": self.name}))

   ####
   # send_email()
   ####
   def send_email(self, recipient, userid, messagetype, tasknr, body, messageid):
      self.sender_queue.put(dict({"recipient": recipient, "UserId": userid ,"message_type": messagetype, "Task": tasknr, "Body": body, "MessageId": messageid}))

   def run(self):
      logmsg = "Starting " + self.name
      self.log_a_msg(logmsg, "INFO")

      while True:
         nextjob = self.job_queue.get(True)
         if nextjob:
             TaskNr=nextjob.get('taskNr')
             UserId=nextjob.get('UserId')
             user_email=nextjob.get('UserEmail')
             messageid=nextjob.get('MessageId')

             logmsg = self.name + ": got a new job: " + str(TaskNr) + "from the user with id: " + str(UserId)
             self.log_a_msg(logmsg, "INFO")

             scriptpath = "tasks/task" + str(TaskNr) + "/tests.sh"
             command = "sh "+scriptpath+" " + str(UserId) + " " + str(TaskNr) + " >> autosub.stdout 2>>autosub.stderr"
             test_res = os.system(command)

             if test_res:

                logmsg = "Test failed! User: " + str(UserId) + " Task: " + str(TaskNr)
                logmsg = logmsg + "return value:" + str(test_res)
                self.log_a_msg(logmsg, "INFO")

                self.send_email(user_email, UserId, "Failed", str(TaskNr), "", messageid)

                if test_res == 512: # Need to read up on this but os.system() returns 
                                    # 256 when the script returns 1 and 512 when the script returns 2!
                   logmsg = "SecAlert: This test failed due to probable attack by user!"
                   self.log_a_msg(logmsg, "INFO")

                   self.send_email(user_email, str(UserId), "SecAlert", str(TaskNr), "", messageid)

             else:

                logmsg = "Test succeeded! User: " + str(UserId) + " Task: " + str(TaskNr)
                self.log_a_msg(logmsg, "INFO")

                self.send_email(user_email, str(UserId), "Success", str(TaskNr), "", "")
                self.send_email(user_email, str(UserId), "Task", str(int(TaskNr)+1), "", messageid)
