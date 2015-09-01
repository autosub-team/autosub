########################################################################
# test_autosub.py -- unittests for autosub.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################
import threading, queue
import unittest
import mock 
import autosub
import sender
from sender import *
import logger
import time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import email


class Test_sender(unittest.TestCase):

   def setUp(self):
      self.email_queue = queue.Queue(10) # used instead of mailbox!

      self.logger_queue = queue.Queue(10)
      mailSender.logger_queue = self.logger_queue
      autosub.logger_queue = mailSender.logger_queue
      #Before we do anything else: start the logger thread, so we can log whats going on
      threadID=1
      logger_t = logger.autosubLogger(threadID, "logger", mailSender.logger_queue)
      logger_t.daemon = True # make the logger thread a daemon, this way the main
                      # will clean it up before terminating!
      logger_t.start()

   ####
   # mock_send_out_email()
   #
   # mock-up function for send_out_mail() in sender.py that does not send out the e-mail,
   # but instead throws it into a message queu from where it can be retrieved and the
   # content be tested.
   ####
   def mock_send_out_email(self, recipient, message, cur, con):
      self.email_queue.put(dict({"recipient": recipient, "message": message})) 
#      print("MOCK: send out an email")

   def test_send_out_email_welcome(self):
      print("Testing WELCOME message ...")
      sender_queue = queue.Queue(10)
      arch_queue = queue.Queue(10)

      ms = mailSender(2, "sender", sender_queue, "autosub@testdomain.com", "autosub_testuser", "autosub_test_passwd", "smtp.testdomain.com", autosub.logger_queue, arch_queue, 'testcourse.db', 'testsemester.db')

      autosub.init_ressources(3, 1, 'testcourse.db', 'testsemester.db')

      #give the sender thread some work
      ms.sender_queue.put(dict({"recipient": "student@studentmail.com", "UserId": "42" ,"message_type": "Welcome", "Task": "1", "Body": "WElcome Message Body", "MessageId": "4711"}))

      with mock.patch("sender.mailSender.send_out_email", self.mock_send_out_email):
         ms.handle_next_mail()

         #wait for / get the result
         nextmail = self.email_queue.get(True)
         self.assertEqual(nextmail.get('recipient'), "student@studentmail.com")

         mailcontent = nextmail.get('message')
         mail = email.message_from_string(mailcontent)
         self.assertEqual(mail['subject'], "Welcome!")
         self.assertEqual(mail['to'], "student@studentmail.com")
         self.assertEqual(mail['from'], "autosub@testdomain.com")
         self.assertEqual(mail['MIME-version'], "1.0")

   def test_send_out_email_question(self):
      print("Testing QUESTION message ...")
      sender_queue = queue.Queue(10)
      arch_queue = queue.Queue(10)

      ms = mailSender(2, "sender", sender_queue, "autosub@testdomain.com", "autosub_testuser", "autosub_test_passwd", "smtp.testdomain.com", autosub.logger_queue, arch_queue, 'testcourse.db', 'testsemester.db')

      autosub.init_ressources(3, 1, 'testcourse.db', 'testsemester.db' )

      #give the sender thread some work
      ms.sender_queue.put(dict({"recipient": "student@studentmail.com", "UserId": "42" ,"message_type": "Question", "Task": "1", "Body": "", "MessageId": "4711"}))

      with mock.patch("sender.mailSender.send_out_email", self.mock_send_out_email):
         ms.handle_next_mail()

         #wait for / get the result
         nextmail = self.email_queue.get(True)
         self.assertEqual(nextmail.get('recipient'), "student@studentmail.com")

         mailcontent = nextmail.get('message')
         mail = email.message_from_string(mailcontent)
         self.assertEqual(mail['subject'], "Question received")
         self.assertEqual(mail['to'], "student@studentmail.com")
         self.assertEqual(mail['from'], "autosub@testdomain.com")
         self.assertEqual(mail['MIME-version'], "1.0")

if __name__ == '__main__':
   unittest.main()

