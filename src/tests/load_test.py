########################################################################
# test_fetcher.py -- unittests for fetcher.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################
import threading, queue
import unittest
import mock
import fetcher
from fetcher import mailFetcher
import sender
from sender import mailSender
import generator
from generator import taskGenerator
import worker
import sqlite3 as lite
import logger
import time, datetime
import configparser as CP
import imaplib
import common as c
import os

class Test_LoadTest(unittest.TestCase):
   def setUp(self):
      self.semesterdb = "semester.db"
      self.coursedb = "course.db"

      self.numusers = 200
      self.testcase = "b'10'"
      self.lasttestcase = ""
      #self.testcase = ""
      self.testcases = []
   
      self.logger_queue = queue.Queue(2000)
      #Before we do anything else: start the logger thread, so we can log whats going on
      threadID=1
      logger_t = logger.autosubLogger(threadID, "logger", self.logger_queue)
      logger_t.daemon = True # make the logger thread a daemon, this way the main
               # will clean it up before terminating!
      logger_t.start()

   def mock_connect_to_imapserver(self):
      # just use any arbitraray IMAP server -- we are not going to login
      # anyway!
      if (self.testcase == ""):
         print("\ncurrently no testcase available.")
         return 0
      print("\ntestcase available: %s" % self.testcase)
      return imaplib.IMAP4_SSL('imap.gmail.com')

   def mock_fetch_new_emails(self, m):
      self.testcases = []
      for i in range (1, self.numusers +1):
         self.testcases.append(bytes(str(i), "ascii"))
      print("\ntestcases to be generated: %s" % self.testcases)
      self.lasttestcase = self.testcase
      self.testcase = ""
      return self.testcases

   def mock_fetch(self, mailid, encoding):
#      print("\ngenerating: testcase %s" % str(int(mailid)))
      config = CP.ConfigParser()
      config.readfp(open('tests/loadtest_testcases.cfg'))
      resp = eval(str(config.get(self.lasttestcase, 'resp')))
      tmp_data = str(config.get(self.lasttestcase, 'data'))
      tmp_data = tmp_data.replace('REPLACEEMAILADDRESS', "testuser{0}@sometestdomain.abc".format(str(int(mailid))))
      tmp_data = tmp_data.replace('REPLACENAME', "test{0} user{1}".format(str(int(mailid)), str(int(mailid))))
      data = eval(tmp_data)
#      print("\ngenerated: testcase %s" % data)
      return resp, data

   def mock_close(self):
      return 0

   ####
   # mock_send_out_email()
   #
   # mock-up function for send_out_mail() in sender.py that does not send out the e-mail,
   # but instead throws it into a message queu from where it can be retrieved and the
   # content be tested.
   ####
   def mock_send_out_email(self, recipient, message, cur, con):
      self.email_queue.put(dict({"recipient": recipient, "message": message})) 

   def get_userid_by_email(self, email):
      #connect to the semester database, and assure, that the e-mail(user) in the test
      #cases is not yet whitelisted (from some other test).
      con = lite.connect(self.semesterdb)
      cur = con.cursor()
      sqlcmd = "SELECT UserId FROM Users WHERE Email=='" + email + "';"
      cur.execute(sqlcmd)
      res = cur.fetchone()
      if str(res) != 'None':
         userid = str(res[0])
      else:
         userid = "0"
      con.close()
      return userid

   def clean_whitelist(self):
      con = lite.connect(self.semesterdb)
      cur = con.cursor()
      sqlcmd = "DROP TABLE WhiteList;"
      cur.execute(sqlcmd)
      con.commit()
      sqlcmd = "CREATE TABLE Whitelist (UniqueId INTEGER PRIMARY KEY AUTOINCREMENT, Email TEXT);"
      cur.execute(sqlcmd)
      con.commit()
      con.close()

   def clean_users(self):
      con = lite.connect(self.semesterdb)
      cur = con.cursor()
      sqlcmd = "DROP TABLE Users;"
      cur.execute(sqlcmd)
      con.commit()
      sqlcmd = "CREATE TABLE Users (UserId INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Email TEXT, FirstMail DATETIME, LastDone DATETIME, CurrentTask INT);"
      cur.execute(sqlcmd)
      con.commit()
      con.close()

   def clean_usertasks(self):
      con = lite.connect(self.semesterdb)
      cur = con.cursor()
      sqlcmd = "DROP TABLE UserTasks;"
      cur.execute(sqlcmd)
      con.commit()
      sqlcmd = "CREATE TABLE UserTasks (UniqueId INTEGER PRIMARY KEY AUTOINCREMENT, TaskNr INT, UserId INT, TaskParameters TEXT, TaskDescription TEXT, TaskAttachments TEXT, NrSubmissions INTEGER, FirstSuccessful INTEGER);"
      cur.execute(sqlcmd)
      con.commit()
      con.close()

   def clean_taskconfig(self):
      conc = lite.connect(self.coursedb)
      curc = conc.cursor()
      #Drop the task configuration table (start clean)
      sqlcmd = "DROP table TaskConfiguration"
      try:
         curc.execute(sqlcmd)
         conc.commit()
      except:
         logmsg = "No Table TaskConfiguration?"
         c.log_a_msg(self.logger_queue, "Debugger", logmsg, "DEBUG")

      sqlcmd = "CREATE TABLE TaskConfiguration (TaskNr INT PRIMARY KEY, TaskStart DATETIME, TaskDeadline DATETIME, PathToTask TEXT, GeneratorExecutable TEXT, TestExecutable TEXT, Score INT, TaskOperator TEXT, TaskActive BOOLEAN);"
      curc.execute(sqlcmd)
      conc.commit()

      conc.close()

   def insert_email_to_whitelist(self, email):
      con = lite.connect(self.semesterdb)
      cur = con.cursor()
      sqlcmd = "INSERT INTO WhiteList (Email) VALUES('" + email + "');"
      cur.execute(sqlcmd)
      con.commit()
      con.close()

   def add_task(self, cur, con, tasknr, start, deadline, pathtotask, genexe, testexe, score, operator, active):
      sqlcmd = "INSERT INTO TaskConfiguration (TaskNr, TaskStart, TaskDeadline, PathToTask, GeneratorExecutable, TestExecutable, Score, TaskOperator, TaskActive) VALUES({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}');".format(str(tasknr), start, deadline, pathtotask, genexe, testexe, score, operator, active)
      cur.execute(sqlcmd)
      con.commit()


   def test_load_code(self):
      threadID = 2  # LOGGER IS NUMBER 1 !!!
      queueSize = 500
      poll_period = 5
      numThreads = 8
      worker_t = []

      job_queue = queue.Queue(queueSize)
      sender_queue = queue.Queue(queueSize)
      gen_queue = queue.Queue(queueSize)
      arch_queue = queue.Queue(queueSize)

      self.email_queue=queue.Queue(20000) # used by the mock-up sender function instead of smtp

      self.clean_whitelist()
      self.clean_users()
      self.clean_usertasks()
      self.clean_taskconfig()

      curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, "loadtester")

      this_time_yesterday = str(datetime.datetime.now() - datetime.timedelta(1)).split('.')[0]
      this_time_tomorrow = str(datetime.datetime.now() + datetime.timedelta(1)).split('.')[0]

      self.add_task(curc, conc, 1, this_time_yesterday, this_time_tomorrow, '/home/andi/working_git/autosub_internal/tasks/implementation/gates', 'generator.sh', 'tester.sh', '5', 'testoperator@q.q', '1')
      self.add_task(curc, conc, 2, this_time_yesterday, this_time_tomorrow, '/home/andi/working_git/autosub_internal/tasks/implementation/fsm', 'generator.sh', 'tester.sh', '5', 'testoperator@q.q', '1')

      conc.close()

      for i in range(1, self.numusers+1):
         self.insert_email_to_whitelist("testuser{0}@sometestdomain.abc".format(str(i)))
     
      with mock.patch.multiple('fetcher.mailFetcher',
                               connect_to_imapserver=self.mock_connect_to_imapserver,
                               fetch_new_emails=self.mock_fetch_new_emails):
         with mock.patch.multiple("imaplib.IMAP4",
                               fetch=self.mock_fetch,
                               close=self.mock_close):
            with mock.patch("sender.mailSender.send_out_email", self.mock_send_out_email):

               while (threadID <= numThreads + 1):
                  tName = "Worker" + str(threadID-1)
                  t = worker.worker(threadID, tName, job_queue, gen_queue, sender_queue, self.logger_queue, self.coursedb, self.semesterdb)
                  t.daemon = True
                  t.start()
                  worker_t.append(t)
                  threadID += 1

               sender_t = sender.mailSender(threadID, "sender", sender_queue, 'autosubmail@q.q', 'autosub_user', 'autosub_passwd', 'smtpserver', self.logger_queue, arch_queue, self.coursedb, self.semesterdb)
               sender_t.daemon = True # make the sender thread a daemon, this way the main
                          # will clean it up before terminating!
               sender_t.start()
               threadID += 1

               fetcher_t = fetcher.mailFetcher(threadID, "fetcher", job_queue, sender_queue, gen_queue, 'autosub_user', 'autosub_passwd', 'imapserver', self.logger_queue, arch_queue, poll_period, self.coursedb, self.semesterdb)
               fetcher_t.daemon = True # make the fetcher thread a daemon, this way the main
                        # will clean it up before terminating!
               fetcher_t.start()
               threadID += 1

               generator_t = generator.taskGenerator(threadID, "generator", gen_queue, sender_queue, self.logger_queue, self.coursedb,"submission@test.xy")
               generator_t.daemon = True # make the fetcher thread a daemon, this way the main
                                # will clean it up before terminating!
               generator_t.start()
               threadID += 1

               # There first test case is set above in the setup routine: self.testcase = "b'10'"
               time.sleep(int(self.numusers)*2)

               tc = "b'84'"
               config = CP.ConfigParser()
               config.readfp(open('tests/loadtest_testcases.cfg'))
               testparam = eval(str(config.get(tc, 'generatorstring')))

               curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, "testcode")
               sqlcmd = "UPDATE UserTasks SET TaskParameters = '162159553761823' WHERE TaskNr==1;".format(testparam)
               curs.execute(sqlcmd)
               cons.commit()
               cons.close() 

               self.testcase = tc 
               time.sleep(self.numusers*2 + poll_period)



if __name__ == '__main__':
   unittest.main()

