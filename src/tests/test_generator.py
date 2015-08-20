########################################################################
# test_autosub.py -- unittests for autosub.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################
import threading, queue
import unittest
import mock 
import logger
import time
import generator
import os

class Test_generator(unittest.TestCase):
   def setUp(self):
      self.name = "testgenerator"

   def test_generator_loop(self):
      genq = queue.Queue(10)
      senderq = queue.Queue(10)
      lqueue = queue.Queue(10)

      testgen = generator.taskGenerator(1, self.name, genq, senderq, lqueue)

      os.mkdir("users/42")
      genq.put(dict({"UserId": "42", "UserEmail": "testuser@testdomain.com", "TaskNr": "1", "MessageId": "47110815"}))

      testgen.generator_loop()
      sendout = senderq.get()
      self.assertEqual(sendout.get('recipient'), "testuser@testdomain.com")
      self.assertEqual(sendout.get('message_type'), "Task")
      self.assertEqual(sendout.get('Task'), "1")

      genq.put(dict({"UserId": "42", "UserEmail": "testuser@testdomain.com", "TaskNr": "11", "MessageId": "47110815"}))

      testgen.generator_loop()
      sendout = senderq.get()
      self.assertEqual(sendout.get('recipient'), "testuser@testdomain.com")
      self.assertEqual(sendout.get('message_type'), "Task")
      self.assertEqual(sendout.get('Task'), "11")

      os.removedirs("users/42")

if __name__ == '__main__':
   unittest.main()
