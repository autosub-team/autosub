########################################################################
# test_autosub.py -- unittests for autosub.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################
import threading, queue
import unittest
import autosub
from autosub import *
import logger
import time


class Test_autosub(unittest.TestCase):
   def setUp(self):
      autosub.logger_queue = queue.Queue(10)
      #Before we do anything else: start the logger thread, so we can log whats going on
      threadID=1
      logger_t = logger.autosubLogger(threadID, "logger", autosub.logger_queue)
      logger_t.daemon = True # make the logger thread a daemon, this way the main
                      # will clean it up before terminating!
      logger_t.start()

   def check_last_log_entry(self, logmsg, loglvl):
      log_a_msg(logmsg, loglvl)
      time.sleep(.25) # give the logger some time...

      with open('autosub.log', "r") as fd:
         for line in fd.readlines():
            #nothing - only interested in the very last line!
            pass

         self.assertNotEqual(line.find(logmsg), -1)
         self.assertNotEqual(line.find(loglvl), -1)
      fd.close()

   def test_log_a_msg(self):
      print("Testing Function: log_a_msg()")

      self.check_last_log_entry("Test Message Nr. 1", "DEBUG")
      self.check_last_log_entry("Test Message Nr. 2", "INFO")
      self.check_last_log_entry("ABABABABABABABABABBABABABABABABAB", "WARNING")
      self.check_last_log_entry("", "ERROR")
      self.check_last_log_entry("TestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTest", "INFO")

   def test_check_dir_mkdir(self):
      print("Testing Function: check_dir_mkdir()")

      self.assertEqual(check_dir_mkdir('testdir'), 1)
      self.assertEqual(check_dir_mkdir('testdir'), 0)

      with open('autosub.log', "r") as fd:
         content = fd.read()
      fd.close()

      os.rmdir('testdir')

if __name__ == '__main__':
   unittest.main()

