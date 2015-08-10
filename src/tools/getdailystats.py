#!/usr/bin/python

import sqlite3 as lite
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime, time

def connect_to_db(dbname):
   con = lite.connect(dbname)
   cur = con.cursor()
   return cur, con

####
#
###
def get_statcounter_value(cur, con, countername):
   sql_cmd = "SELECT Value from StatCounters WHERE Name=='" + countername + "';"
   cur.execute(sql_cmd)
   res = cur.fetchone()
   return int(res[0])

####
# check_and_create_table():
#
# check if table exists and create if it does not exist
####
def check_and_create_table(cur, con, tablename, field):
   cur.execute("SELECT " + field + " FROM sqlite_master WHERE type == 'table' AND name = '" + tablename + "';")
   res = cur.fetchall()
   if res:
     print('table ' + tablename + ' exists')
   else:
     print('table ' +tablename + ' does not exist ... creating it now.')
     con.execute("CREATE TABLE " + tablename +" (TimeStamp STRING PRIMARY KEY, value INT)")

def insert_stat_db(cur, con, table, count):
   sql_cmd = "INSERT INTO " + table + " (TimeStamp, value) VALUES('" + str(datetime.datetime.now()) + "', " + str(count) +");"
   cur.execute(sql_cmd);
   con.commit();

def plot_stat_graph(cur, con, tablename, filename):
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


def main():
   #connect to sqlite database ...
   cur1, con1 = connect_to_db('../semester.db')

   # get number of users
   cur1.execute("SELECT COUNT(UserId) from Users;")
   res = cur1.fetchone()
   count = int(res[0])

   nr_mails_sent = get_statcounter_value(cur1, con1, 'nr_mails_sent')
   nr_mails_fetched = get_statcounter_value(cur1, con1, 'nr_mails_fetched')
   nr_questions_received = get_statcounter_value(cur1, con1, 'nr_questions_received')

   #connect to sqlite database ...
   cur2, con2 = connect_to_db('semesterstats.db')

   check_and_create_table(cur2, con2, 'NrUserStats', 'name')
   check_and_create_table(cur2, con2, 'NrSendStats', 'name')
   check_and_create_table(cur2, con2, 'NrReceiveStats', 'name')
   check_and_create_table(cur2, con2, 'NrQuestionStats', 'name')

   insert_stat_db(cur2, con2, 'NrUserStats', count)
   insert_stat_db(cur2, con2, 'NrSendStats', nr_mails_sent)
   insert_stat_db(cur2, con2, 'NrReceiveStats', nr_mails_fetched)
   insert_stat_db(cur2, con2, 'NrQuestionStats', nr_questions_received)

   plot_stat_graph(cur2, con2, 'NrUserStats', 'nr_users.png')
   plot_stat_graph(cur2, con2, 'NrSendStats', 'nr_mails_sent.png')
   plot_stat_graph(cur2, con2, 'NrReceiveStats', 'nr_mails_received.png')
   plot_stat_graph(cur2, con2, 'NrQuestionStats', 'nr_questions_received.png')

   con1.close()
   con2.close()

if __name__ == '__main__':
   main()
