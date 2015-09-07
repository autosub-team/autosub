########################################################################
# test_fetcher.py -- unittests for fetcher.py
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

   def test_loop_code(self):
      sender_queue = queue.Queue(10)
      gen_queue = queue.Queue(10)
      ta = taskActivator(4, "testactivator", gen_queue, sender_queue, self.logger_queue, 'testcourse.db', 'testsemester.db')


if __name__ == '__main__':
   unittest.main()

