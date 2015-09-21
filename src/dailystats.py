#!/usr/bin/python

import threading
import sqlite3 as lite
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime, time
import common as c

class dailystatsTask(threading.Thread):
   def __init__(self, threadID, name, logger_queue, semesterdb):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.logger_queue = logger_queue
      self.name = name
      self.semesterdb = semesterdb

   ####
   #
   ###
   def get_statcounter_value(self, cur, con, countername):
      sql_cmd = "SELECT Value from StatCounters WHERE Name=='" + countername + "';"
      cur.execute(sql_cmd)
      res = cur.fetchone()
      return int(res[0])

   ####
   # check_and_create_table():
   #
   # check if table exists and create if it does not exist
   ####
   def check_and_create_table(self, cur, con, tablename):
      cur.execute("SELECT name FROM sqlite_master WHERE type == 'table' AND name = '" + tablename + "';")
      res = cur.fetchall()
      if res:
        logmsg = 'table ' + tablename + ' exists'
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
      else:
        logmsg = 'table ' +tablename + ' does not exist ... creating it now.'
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
        con.execute("CREATE TABLE " + tablename +" (TimeStamp STRING PRIMARY KEY, value INT)")

   def insert_stat_db(self, cur, con, table, count):
      sql_cmd = "INSERT INTO " + table + " (TimeStamp, value) VALUES('" + str(datetime.datetime.now()) + "', " + str(count) +");"
      cur.execute(sql_cmd);
      con.commit();

   def plot_stat_graph(self, cur, con, tablename, filename):
      cur.execute("select TimeStamp from " + tablename + ";")
      list_of_datetimes = cur.fetchall()
      dates =[]
      for s in list_of_datetimes:
         dates.append(datetime.datetime.strptime(s[0], "%Y-%m-%d %H:%M:%S.%f"))

      cur.execute("select value from " + tablename)
      counts = cur.fetchall()

      plt.plot(dates,counts)
      plt.gcf().autofmt_xdate()
      plt.savefig(filename)
      plt.clf()


   def run(self):
      while True:
         #connect to sqlite database ...
         cur1, con1 = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)

         # get number of users
         cur1.execute("SELECT COUNT(UserId) from Users;")
         res = cur1.fetchone()
         count = int(res[0])

         nr_mails_sent = self.get_statcounter_value(cur1, con1, 'nr_mails_sent')
         nr_mails_fetched = self.get_statcounter_value(cur1, con1, 'nr_mails_fetched')
         nr_questions_received = self.get_statcounter_value(cur1, con1, 'nr_questions_received')

         #connect to sqlite database ...
         cur2, con2 = c.connect_to_db('semesterstats.db', self.logger_queue, self.name)

         self.check_and_create_table(cur2, con2, 'NrUserStats')
         self.check_and_create_table(cur2, con2, 'NrSendStats')
         self.check_and_create_table(cur2, con2, 'NrReceiveStats')
         self.check_and_create_table(cur2, con2, 'NrQuestionStats')

         self.insert_stat_db(cur2, con2, 'NrUserStats', count)
         self.insert_stat_db(cur2, con2, 'NrSendStats', nr_mails_sent)
         self.insert_stat_db(cur2, con2, 'NrReceiveStats', nr_mails_fetched)
         self.insert_stat_db(cur2, con2, 'NrQuestionStats', nr_questions_received)

         self.plot_stat_graph(cur2, con2, 'NrUserStats', 'nr_users.png')
         self.plot_stat_graph(cur2, con2, 'NrSendStats', 'nr_mails_sent.png')
         self.plot_stat_graph(cur2, con2, 'NrReceiveStats', 'nr_mails_received.png')
         self.plot_stat_graph(cur2, con2, 'NrQuestionStats', 'nr_questions_received.png')

         con1.close()
         con2.close()

         time.sleep(3600*12) #updating the images every 12h is enough

