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
   def get_statcounter_value(self, curst, const, countername):
      data = {'Name' : countername}
      sql_cmd = "SELECT Value FROM StatCounters WHERE Name==:Name;"
      curst.execute(sql_cmd, data)
      res = curst.fetchone()
      return int(res[0])

   ####
   # check_and_create_table():
   #
   # check if table exists and create if it does not exist
   ####
   def check_and_create_table(self, cur, con, tablename):
      data = {'Table': tablename}
      sql_cmd = "SELECT name FROM sqlite_master WHERE type == 'table' AND name == :Table;"
      cur.execute(sql_cmd, data)
      res = cur.fetchall()
      if res:
        logmsg = "table {0} exists".format(tablename)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
      else:
        logmsg = "table {0} does not exist ... creating it now".format(tablename)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
        data = {'Table': tablename}
        sql_cmd = "CREATE TABLE :Table (TimeStamp STRING PRIMARY KEY, value INT)"
        cur.execute(sql_cmd, data)

   def insert_stat_db(self, curst, const, table, count):
      data = {'Count': count, 'Now': str(datetime.datetime.now())}
      sql_cmd = "INSERT INTO {0} (TimeStamp, value) VALUES(:Now, :Count);".format(table)
      curst.execute(sql_cmd, data)
      const.commit()

   def plot_stat_graph(self, curst, const, tablename, filename):
      sql_cmd = "SELECT TimeStamp FROM {0};".format(tablename)
      list_of_datetimes = curst.fetchall()
      curst.execute(sql_cmd);
      dates =[]
      for s in list_of_datetimes:
         dates.append(datetime.datetime.strptime(s[0], "%Y-%m-%d %H:%M:%S.%f"))

      sql_cmd = "SELECT value FROM {0};".format(tablename)
      curst.execute(sql_cmd)
      counts = curst.fetchall()

      plt.plot(dates,counts)
      plt.gcf().autofmt_xdate()
      plt.savefig(filename)
      plt.clf()


   def run(self):
      while True:
         #connect to sqlite database ...
         curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)

         # get number of users
         sql_cmd = "SELECT COUNT(UserId) FROM Users;"
         curs.execute(sql_cmd)
         res = curs.fetchone()
         count = int(res[0])

         nr_mails_sent = self.get_statcounter_value(curs, cons, 'nr_mails_sent')
         nr_mails_fetched = self.get_statcounter_value(curs, cons, 'nr_mails_fetched')
         nr_questions_received = self.get_statcounter_value(curs, cons, 'nr_questions_received')

         #connect to sqlite database ...
         curst, const = c.connect_to_db('semesterstats.db', self.logger_queue, self.name)

         self.check_and_create_table(curst, const, 'NrUserStats')
         self.check_and_create_table(curst, const, 'NrSendStats')
         self.check_and_create_table(curst, const, 'NrReceiveStats')
         self.check_and_create_table(curst, const, 'NrQuestionStats')

         self.insert_stat_db(curst, const, 'NrUserStats', count)
         self.insert_stat_db(curst, const, 'NrSendStats', nr_mails_sent)
         self.insert_stat_db(curst, const, 'NrReceiveStats', nr_mails_fetched)
         self.insert_stat_db(curst, const, 'NrQuestionStats', nr_questions_received)

         self.plot_stat_graph(curst, const, 'NrUserStats', 'nr_users.png')
         self.plot_stat_graph(curst, const, 'NrSendStats', 'nr_mails_sent.png')
         self.plot_stat_graph(curst, const, 'NrReceiveStats', 'nr_mails_received.png')
         self.plot_stat_graph(curst, const, 'NrQuestionStats', 'nr_questions_received.png')

         cons.close()
         const.close()

#         time.sleep(3600*12) #updating the images every 12h is enough
         time.sleep(12) #updating the images every 12h is enough

