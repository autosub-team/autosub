########################################################################
# logger.py -- log in a common format to a file.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import logging

class autosubLogger (threading.Thread):
   def __init__(self, threadID, name, logger_queue): #, log_level):
      threading.Thread.__init__(self)
      self.name = name
      self.threadID = threadID
      self.logger_queue = logger_queue
      #self.log_level = log_level

   def run(self):

      FORMAT = "%(asctime)-15s [%(loggername)-12s] %(levelname)s: %(logmsg)s"
      logging.basicConfig(format=FORMAT, filename='autosub.log',level=logging.DEBUG, encoding='utf-8')

      while True:
         next_log_msg = self.logger_queue.get(True)
            
         d = dict({"loggername":str(next_log_msg.get('loggername')), "logmsg":str(next_log_msg.get('msg'))})

         if (str(next_log_msg.get('type')) == "DEBUG"):
            logging.debug("%s ", extra=d)
         elif (str(next_log_msg.get('type')) == "INFO"):
            logging.info("%s ", extra=d)
         elif (str(next_log_msg.get('type')) == "WARNING"):
            logging.warning("%s ", extra=d)
         elif (str(next_log_msg.get('type')) == "ERROR"):
            logging.error("%s ", extra=d)
         else: #if we don't know, we assume the worst
            logging.error("%s ", extra=d)

