########################################################################
# test_activator.py -- unittests for activator.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################
import threading, queue
import unittest
import mock
import activator
from activator import taskActivator
import sqlite3 as lite
import logger
import time
import configparser as CP
import imaplib
import common
import os
import datetime

class Test_taskActivator(unittest.TestCase):
   def setUp(self):
      self.logger_queue = queue.Queue(10)
      taskActivator.logger_queue = self.logger_queue
      #Before we do anything else: start the logger thread, so we can log whats going on
      threadID=1
      logger_t = logger.autosubLogger(threadID, "logger", taskActivator.logger_queue)
      logger_t.daemon = True # make the logger thread a daemon, this way the main
                      # will clean it up before terminating!
      logger_t.start()

   def add_test(self, cur, con, start, deadline, pathtotask, genexe, testexe, score, operator, active):
      

   def test_loop_code(self):
      sender_queue = queue.Queue(10)
      gen_queue = queue.Queue(10)
      ta = taskActivator(4, "testactivator", gen_queue, sender_queue, self.logger_queue, 'testcourse.db', 'testsemester.db')

      curc, conc = c.connect_to_db('testcourse.db', self.logger_queue, 'testcode')
      this_time_yesterday = str(datetime.datetime.now() - datetime.delta(1)).split('.')[0]
      this_time_tomorrow = str(datetime.datetime.now() + datetime.delta(1)).split('.')[0]
      self.add_test(curc, conc, this_time_yesterday, this_time_tomorrow, '/home/testuser/path/to/task/implementation', 'generator.sh', 'tester.sh', '5', 'testoperator@q.q', '1')



if __name__ == '__main__':
   unittest.main()

