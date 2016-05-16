########################################################################
# test_activator.py -- unittests for activator.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################
import threading, queue
import unittest
import activator
from activator import TaskActivator
import time
import imaplib
import common as c
import datetime

class Test_TaskActivator(unittest.TestCase):
    def setUp(self):
        self.logger_queue = queue.Queue(10)
        TaskActivator.logger_queue = self.logger_queue
        #Before we do anything else: start the logger thread, so we can log whats going on
#        threadID=1
#        logger_t = logger.autosubLogger(threadID, "logger", TaskActivator.logger_queue)
#        logger_t.daemon = True # make the logger thread a daemon, this way the main
#                        # will clean it up before terminating!
#        logger_t.start()

    def add_task(self, cur, con, tasknr, start, deadline, pathtotask, genexe, \
                 testexe, score, operator, active):
        sqlcmd = ("INSERT INTO TaskConfiguration (TaskNr, TaskStart, ",
                  "TaskDeadline, PathToTask, GeneratorExecutable, ",
                  "TestExecutable, Score, TaskOperator, TaskActive) ",
                  "VALUES({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', ",
                  "'{7}', '{8}');".format(str(tasknr), start, deadline,
                                          pathtotask, genexe, testexe, score,
                                          operator, active))
        cur.execute(sqlcmd)
        con.commit()
      

    def test_loop_code(self):
        sender_queue = queue.Queue(10)
        gen_queue = queue.Queue(10)
        ta = TaskActivator("testactivator", gen_queue, sender_queue, \
                           self.logger_queue, 'testcourse.db', \
                           'testsemester.db')

        curc, conc = c.connect_to_db('testcourse.db', self.logger_queue, 'testcode')
        this_time_yesterday = str(datetime.datetime.now() - datetime.timedelta(1)).split('.')[0]
        this_time_tomorrow = str(datetime.datetime.now() + datetime.timedelta(1)).split('.')[0]
        this_time_nextmonth = str(datetime.datetime.now() + datetime.timedelta(30)).split('.')[0]

        #Drop the task configuration table (start clean)
        sqlcmd = "DROP table TaskConfiguration"
        try: 
            curc.execute(sqlcmd)
            conc.commit()
        except:
            logmsg = "No Table TaskConfiguration?"
            c.log_a_msg(self.logger_queue, "Debugger", logmsg, "DEBUG")

        sqlcmd = ("CREATE TABLE TaskConfiguration (TaskNr INT PRIMARY KEY, ",
                  "TaskStart DATETIME, TaskDeadline DATETIME, ",
                  "PathToTask TEXT, GeneratorExecutable TEXT, ",
                  "TestExecutable TEXT, Score INT, TaskOperator TEXT, ",
                  "TaskActive BOOLEAN);")
        curc.execute(sqlcmd)
        conc.commit()

        # test case 1: no effect -- nothing to do here for the activator thread
        self.add_task(curc, conc, 1, this_time_yesterday, this_time_tomorrow, \
                      '/home/testuser/path/to/task/implementation', \
                      'generator.sh', 'tester.sh', '5', 'testoperator@q.q', '1')

        # test case 2: only a logmsg, there is an inactive task, however its starttime has not
        #    come (yet)
        self.add_task(curc, conc, 2, this_time_tomorrow, this_time_nextmonth, \
                      '/home/testuser/path/to/task/implementation', \
                      'generator.sh', 'tester.sh', '5', \
                      'testoperator@q.q', '0')

        ta.activator_loop()

        # nothing to test for case 1

        # check expected log message for  test case 2
        logmsg = self.logger_queue.get(True)
        self.assertEqual(logmsg.get('loggername'), 'testactivator')
        self.assertEqual(logmsg.get('msg'), 'Task 2 is still inactive')
        self.assertEqual(logmsg.get('type'), 'INFO')

        # test case 3: only a logmsg, there is an inactive task, however its starttime has not
        #    come (yet)
        this_time_plus3s = str(datetime.datetime.now() + datetime.timedelta(0, 3)).split('.')[0]
        self.add_task(curc, conc, 3, this_time_tomorrow, this_time_plus3s, \
                      '/home/testuser/path/to/task/implementation', \
                      'generator.sh', 'tester.sh', '5', \
                      'testoperator@q.q', '0')

        ta.activator_loop()
        # check expected log message for  test case 2
        logmsg = self.logger_queue.get(True)
        self.assertEqual(logmsg.get('loggername'), 'testactivator')
        self.assertEqual(logmsg.get('msg'), 'Task 2 is still inactive')
        self.assertEqual(logmsg.get('type'), 'INFO')
        # check expected log message for  test case 3
        logmsg = self.logger_queue.get(True)
        self.assertEqual(logmsg.get('loggername'), 'testactivator')
        self.assertEqual(logmsg.get('msg'), 'Task 3 is still inactive')
        self.assertEqual(logmsg.get('type'), 'INFO')

        time.sleep(10)
        ta.activator_loop()
        # check expected log message for  test case 2
        logmsg = self.logger_queue.get(True)
        self.assertEqual(logmsg.get('loggername'), 'testactivator')
        self.assertEqual(logmsg.get('msg'), 'Task 2 is still inactive')
        self.assertEqual(logmsg.get('type'), 'INFO')
        # check expected log message for  test case 3
        logmsg = self.logger_queue.get(True)
        self.assertEqual(logmsg.get('loggername'), 'testactivator')
        self.assertEqual(logmsg.get('msg'), 'Task 3 is still inactive')
        self.assertEqual(logmsg.get('type'), 'INFO')

if __name__ == '__main__':
    unittest.main()

