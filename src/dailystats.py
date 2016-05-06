#!/usr/bin/python

import threading
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime, time
import common as c

def get_statcounter_value(curst, countername):
    data = {'Name' : countername}
    sql_cmd = "SELECT Value FROM StatCounters WHERE Name==:Name;"
    curst.execute(sql_cmd, data)
    res = curst.fetchone()
    return int(res[0])

def insert_stat_db(curst, const, table, count):
    data = {'Count': count, 'Now': str(datetime.datetime.now())}
    sql_cmd = "INSERT INTO {0} (TimeStamp, value) VALUES(:Now, :Count);".format(table)
    curst.execute(sql_cmd, data)
    const.commit()

def plot_stat_graph(curst, tablename, filename):
    sql_cmd = "SELECT TimeStamp FROM {0};".format(tablename)
    list_of_datetimes = curst.fetchall()
    curst.execute(sql_cmd)
    dates = []

    for dtime in list_of_datetimes:
        dates.append(datetime.datetime.strptime(dtime[0], \
                                                "%Y-%m-%d %H:%M:%S.%f"))

    sql_cmd = "SELECT value FROM {0};".format(tablename)
    curst.execute(sql_cmd)
    counts = curst.fetchall()

    plt.plot(dates, counts)
    plt.gcf().autofmt_xdate()
    plt.savefig(filename)
    plt.clf()

class DailystatsTask(threading.Thread):
    def __init__(self, name, logger_queue, semesterdb):
        threading.Thread.__init__(self)
        self.logger_queue = logger_queue
        self.name = name
        self.semesterdb = semesterdb

####
# check_and_create_table():
#
# check if table exists and create if it does not exist
####
    def check_and_create_table(self, cur, tablename):
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
            sql_cmd = "CREATE TABLE {0} (TimeStamp STRING PRIMARY KEY, value INT)".format(tablename)
            cur.execute(sql_cmd)

    def run(self):
        while True:
            #connect to sqlite database ...
            curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, \
                                         self.name)

            # get number of users
            sql_cmd = "SELECT COUNT(UserId) FROM Users;"
            curs.execute(sql_cmd)
            res = curs.fetchone()
            count = int(res[0])

            nr_mails_sent = get_statcounter_value(curs, 'nr_mails_sent')
            nr_mails_fetched = get_statcounter_value(curs, 'nr_mails_fetched')
            nr_questions_received = get_statcounter_value(curs, \
                                                    'nr_questions_received')

            #connect to sqlite database ...
            curst, const = c.connect_to_db('semesterstats.db', \
                                           self.logger_queue, self.name)

            self.check_and_create_table(curst, 'NrUserStats')
            self.check_and_create_table(curst, 'NrSendStats')
            self.check_and_create_table(curst, 'NrReceiveStats')
            self.check_and_create_table(curst, 'NrQuestionStats')

            insert_stat_db(curst, const, 'NrUserStats', \
                           count)
            insert_stat_db(curst, const, 'NrSendStats', \
                           nr_mails_sent)
            insert_stat_db(curst, const, 'NrReceiveStats', \
                           nr_mails_fetched)
            insert_stat_db(curst, const, 'NrQuestionStats', \
                           nr_questions_received)

            plot_stat_graph(curst, 'NrUserStats', \
                            'nr_users.png')
            plot_stat_graph(curst, 'NrSendStats', \
                            'nr_mails_sent.png')
            plot_stat_graph(curst, 'NrReceiveStats', \
                            'nr_mails_received.png')
            plot_stat_graph(curst, 'NrQuestionStats', \
                            'nr_questions_received.png')

            cons.close()
            const.close()

            time.sleep(3600*12) #updating the images every 12h is enough
