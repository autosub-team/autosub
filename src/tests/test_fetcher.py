########################################################################
# test_fetcher.py -- unittests for fetcher.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################
import threading, queue
import unittest
import fetcher
from fetcher import mailFetcher
import sqlite3 as lite
import logger
import time


class Test_mailFetcher(unittest.TestCase):
   def setUp(self):
      self.name = "testfecher"
      self.logger_queue = queue.Queue(10)
      mailFetcher.logger_queue = self.logger_queue
      #Before we do anything else: start the logger thread, so we can log whats going on
      threadID=1
      logger_t = logger.autosubLogger(threadID, "logger", mailFetcher.logger_queue)
      logger_t.daemon = True # make the logger thread a daemon, this way the main
                      # will clean it up before terminating!
      logger_t.start()

   # two cases: either the user is whitelisted, or not, so both are tested,
   # after that the testuser is removed from the table (for the next run)
   def test_check_if_whitelisted(self):
      con = lite.connect('semester.db')
      cur = con.cursor()
      result = mailFetcher.check_if_whitelisted(self, cur, con, "testuser@test.com")
      self.assertEqual(result, 0)
      # add the user, then check again!
      sqlcmd = "INSERT INTO WhiteList (Email) VALUES('testuser@test.com')"
      cur.execute(sqlcmd)
      result = mailFetcher.check_if_whitelisted(self , cur, con, "testuser@test.com")
      self.assertEqual(result, 1)

      sqlcmd = "DELETE from WhiteList WHERE Email=='testuser@test.com'"
      cur.execute(sqlcmd)


if __name__ == '__main__':
   unittest.main()

